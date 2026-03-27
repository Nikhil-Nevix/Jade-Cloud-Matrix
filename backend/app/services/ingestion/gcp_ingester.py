import httpx
import logging
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from app.models.provider import Region
from app.models.pricing import ComputePricing, StoragePricing
from app.models.reserved_pricing import ReservedPricing
from app.services.ingestion.fallback_data import get_gcp_compute_data, get_gcp_storage_data, get_gcp_reserved_data
from app.config import settings

logger = logging.getLogger(__name__)


async def ingest_gcp_pricing(db: AsyncSession):
    """
    Ingest GCP pricing from live API or fallback.
    Primary: GCP Cloud Billing Catalog API
    URL: https://cloudbilling.googleapis.com/v1/services/{service_id}/skus
    Fallback: fallback_data.py
    """
    # Check pricing mode
    if settings.PRICING_API_MODE == "fallback":
        logger.info("PRICING_API_MODE=fallback, skipping live GCP API")
        await _ingest_gcp_fallback(db)
        return

    try:
        logger.info("Attempting to fetch GCP pricing from live API...")
        await _ingest_gcp_live(db)
    except Exception as e:
        logger.warning(f"GCP live API failed: {e}. Using fallback data.")
        await _ingest_gcp_fallback(db)


async def _ingest_gcp_live(db: AsyncSession):
    """
    Ingest GCP pricing from live Cloud Billing Catalog API.
    Supports both public (unauthenticated) and authenticated modes.
    """
    # Get GCP regions from database
    result = await db.execute(
        select(Region).join(Region.provider).where(Region.provider.has(name="GCP"))
    )
    gcp_regions = {r.region_code: r for r in result.scalars().all()}
    region_codes = list(gcp_regions.keys())

    logger.info(f"Fetching GCP pricing for regions: {region_codes}")

    # Try authenticated mode first if credentials are provided
    access_token = None
    if settings.GOOGLE_APPLICATION_CREDENTIALS and os.path.exists(settings.GOOGLE_APPLICATION_CREDENTIALS):
        try:
            access_token = await _get_gcp_access_token()
            logger.info("Using authenticated GCP API access")
        except Exception as e:
            logger.warning(f"GCP authentication failed: {e}. Falling back to public API")

    # GCP Compute Engine service ID
    service_id = "6F81-5844-456A"
    base_url = f"https://cloudbilling.googleapis.com/v1/services/{service_id}/skus"
    compute_count = 0

    # Build headers
    headers = {}
    if access_token:
        headers['Authorization'] = f'Bearer {access_token}'

    async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
        page_token = None

        while True:
            try:
                params = {'pageSize': 100}
                if page_token:
                    params['pageToken'] = page_token

                response = await client.get(base_url, params=params)
                response.raise_for_status()

                data = response.json()
                skus = data.get('skus', [])

                if not skus:
                    break

                for sku in skus:
                    try:
                        compute_count += await _process_gcp_compute_sku(sku, gcp_regions, db)
                    except Exception as e:
                        logger.debug(f"Error processing GCP SKU: {e}")
                        continue

                # Check for next page
                page_token = data.get('nextPageToken')
                if not page_token:
                    break

            except httpx.HTTPError as e:
                logger.error(f"GCP API HTTP error: {e}")
                break
            except Exception as e:
                logger.error(f"GCP API error: {e}")
                break

    logger.info(f"Ingested {compute_count} GCP compute pricing records from live API")

    # Use fallback for storage and reserved pricing
    logger.info("Using fallback data for GCP storage and reserved pricing")
    await _ingest_gcp_storage_fallback(db, gcp_regions)
    await _ingest_gcp_reserved_fallback(db, gcp_regions)

    await db.commit()
    logger.info("GCP live pricing ingestion completed.")


async def _get_gcp_access_token() -> str:
    """
    Get GCP access token using service account credentials.
    Returns access token string.
    """
    try:
        from google.oauth2 import service_account
        from google.auth.transport import requests
    except ImportError:
        logger.error("google-auth not installed. Run: pip install google-auth")
        raise Exception("google-auth not installed")

    credentials = service_account.Credentials.from_service_account_file(
        settings.GOOGLE_APPLICATION_CREDENTIALS,
        scopes=['https://www.googleapis.com/auth/cloud-billing.readonly']
    )

    # Refresh token
    auth_request = requests.Request()
    credentials.refresh(auth_request)

    return credentials.token


async def _process_gcp_compute_sku(sku: dict, gcp_regions: dict, db: AsyncSession) -> int:
    """
    Process a single GCP SKU from Cloud Billing API.
    Returns 1 if processed successfully, 0 otherwise.
    """
    try:
        # Check if this is a compute engine instance SKU
        description = sku.get('description', '')
        category = sku.get('category', {})
        resource_family = category.get('resourceFamily', '')

        if resource_family != 'Compute':
            return 0

        # Parse instance type from description
        # Example: "N1 Standard Instance Core running in Americas"
        # Example: "E2 Instance Core running in Americas"
        if 'Instance Core' not in description:
            return 0

        # Extract machine type
        instance_type = _parse_gcp_instance_type(description)
        if not instance_type:
            return 0

        # Get pricing info
        pricing_info = sku.get('pricingInfo', [])
        if not pricing_info:
            return 0

        # Get first pricing tier
        pricing_expression = pricing_info[0].get('pricingExpression', {})
        tiered_rates = pricing_expression.get('tieredRates', [])
        if not tiered_rates:
            return 0

        # Get unit price (in nanos, need to divide by 1e9)
        unit_price_nanos = tiered_rates[0].get('unitPrice', {}).get('nanos', 0)
        hourly_price_per_core = unit_price_nanos / 1_000_000_000  # Convert from nanos to dollars

        # Get vCPU and memory specs
        vcpu, memory_gb = _get_gcp_instance_specs(instance_type)
        if vcpu == 0:
            return 0

        # Calculate hourly price for full instance
        hourly_price = hourly_price_per_core * vcpu

        if hourly_price == 0:
            return 0

        # GCP pricing is regional, try to map to our regions
        service_regions = sku.get('serviceRegions', [])
        processed_any = False

        for service_region in service_regions:
            # Map GCP service region to our region codes
            matching_regions = _map_gcp_service_region(service_region, gcp_regions)

            for region in matching_regions:
                stmt = insert(ComputePricing).values(
                    region_id=region.id,
                    provider_id=region.provider_id,
                    instance_type=instance_type,
                    os_type="Linux",
                    price_per_hour=hourly_price,
                    price_per_month=hourly_price * 730,
                    price_per_year=hourly_price * 8760,
                    vcpu=vcpu,
                    memory_gb=memory_gb,
                ).on_conflict_do_update(
                    index_elements=["provider_id", "region_id", "instance_type", "os_type"],
                    set_={
                        "price_per_hour": hourly_price,
                        "price_per_month": hourly_price * 730,
                        "price_per_year": hourly_price * 8760,
                        "vcpu": vcpu,
                        "memory_gb": memory_gb,
                    }
                )
                await db.execute(stmt)
                processed_any = True

        return 1 if processed_any else 0

    except Exception as e:
        logger.debug(f"Error parsing GCP SKU: {e}")
        return 0


def _parse_gcp_instance_type(description: str) -> str:
    """
    Parse GCP instance type from SKU description.
    Example: "N1 Standard Instance Core" -> "n1-standard"
    Example: "E2 Instance Core" -> "e2-standard"
    """
    description_lower = description.lower()

    if 'n1 standard' in description_lower:
        return 'n1-standard'
    elif 'n1 highmem' in description_lower:
        return 'n1-highmem'
    elif 'n1 highcpu' in description_lower:
        return 'n1-highcpu'
    elif 'n2 standard' in description_lower:
        return 'n2-standard'
    elif 'n2 highmem' in description_lower:
        return 'n2-highmem'
    elif 'n2 highcpu' in description_lower:
        return 'n2-highcpu'
    elif 'n2d standard' in description_lower:
        return 'n2d-standard'
    elif 'e2 standard' in description_lower or 'e2 instance' in description_lower:
        return 'e2-standard'
    elif 'e2 medium' in description_lower:
        return 'e2-medium'
    elif 'e2 small' in description_lower:
        return 'e2-small'
    elif 'e2 micro' in description_lower:
        return 'e2-micro'
    elif 'c2 standard' in description_lower:
        return 'c2-standard'
    elif 'c2d standard' in description_lower:
        return 'c2d-standard'
    elif 'm1 ultramem' in description_lower:
        return 'm1-ultramem'
    elif 'm2 ultramem' in description_lower:
        return 'm2-ultramem'

    return ''


def _get_gcp_instance_specs(instance_family: str) -> tuple:
    """
    Get typical vCPU and memory specs for GCP instance families.
    Note: GCP machines are customizable, so this returns base configuration.
    """
    specs_map = {
        # E2 (shared-core and standard)
        'e2-micro': (2, 1), 'e2-small': (2, 2), 'e2-medium': (2, 4),
        'e2-standard': (2, 8),  # Base config, multiply by vCPU count
        # N1 Standard
        'n1-standard': (2, 7.5),  # Base
        # N1 High-Memory
        'n1-highmem': (2, 13),
        # N1 High-CPU
        'n1-highcpu': (2, 1.8),
        # N2 Standard
        'n2-standard': (2, 8),
        # N2 High-Memory
        'n2-highmem': (2, 16),
        # N2 High-CPU
        'n2-highcpu': (2, 2),
        # N2D (AMD)
        'n2d-standard': (2, 8),
        # C2 (Compute-optimized)
        'c2-standard': (4, 16),
        # C2D (Compute-optimized AMD)
        'c2d-standard': (2, 4),
    }

    return specs_map.get(instance_family, (2, 8))  # Default to 2 vCPU, 8GB


def _map_gcp_service_region(service_region: str, gcp_regions: dict) -> list:
    """
    Map GCP service region (e.g., 'us-east1', 'europe-west1') to our region codes.
    Returns list of matching Region objects.
    """
    # Service regions can be broad (e.g., 'us', 'europe') or specific (e.g., 'us-east1')
    matching = []

    for region_code, region_obj in gcp_regions.items():
        if service_region == region_code:
            matching.append(region_obj)
        elif service_region in ['us', 'americas'] and region_code.startswith('us-'):
            matching.append(region_obj)
        elif service_region in ['europe', 'europe-west'] and region_code.startswith('europe-'):
            matching.append(region_obj)
        elif service_region in ['asia', 'asia-pacific'] and region_code.startswith('asia-'):
            matching.append(region_obj)

    return matching


async def _ingest_gcp_fallback(db: AsyncSession):
    """Ingest GCP fallback data."""
    result = await db.execute(select(Region).join(Region.provider).where(Region.provider.has(name="GCP")))
    gcp_regions = {r.region_code: r for r in result.scalars().all()}

    await _ingest_gcp_compute_fallback(db, gcp_regions)
    await _ingest_gcp_storage_fallback(db, gcp_regions)
    await _ingest_gcp_reserved_fallback(db, gcp_regions)

    await db.commit()
    logger.info("GCP fallback pricing ingestion completed.")


async def _ingest_gcp_compute_fallback(db: AsyncSession, gcp_regions: dict):
    """Ingest GCP compute fallback data."""
    compute_data = get_gcp_compute_data()
    for item in compute_data:
        region = gcp_regions.get(item["region"])
        if not region:
            continue

        stmt = insert(ComputePricing).values(
            region_id=region.id,
            provider_id=region.provider_id,
            instance_type=item["instance_type"],
            os_type=item["os"],
            price_per_hour=item["hourly"],
            price_per_month=item["hourly"] * 730,
            price_per_year=item["hourly"] * 8760,
            vcpu=item["vcpu"],
            memory_gb=item["mem"],
        ).on_conflict_do_update(
            index_elements=["provider_id", "region_id", "instance_type", "os_type"],
            set_={
                "price_per_hour": item["hourly"],
                "price_per_month": item["hourly"] * 730,
                "price_per_year": item["hourly"] * 8760,
                "vcpu": item["vcpu"],
                "memory_gb": item["mem"],
            }
        )
        await db.execute(stmt)


async def _ingest_gcp_storage_fallback(db: AsyncSession, gcp_regions: dict):
    """Ingest GCP storage fallback data."""
    storage_data = get_gcp_storage_data()
    for item in storage_data:
        region = gcp_regions.get(item["region"])
        if not region:
            continue

        stmt = insert(StoragePricing).values(
            region_id=region.id,
            provider_id=region.provider_id,
            storage_type=item["type"],
            storage_name=item["name"],
            price_per_gb=item["price_gb_month"],
            price_per_gb_month=item["price_gb_month"],
            unit_type="GB/month",
        ).on_conflict_do_update(
            index_elements=["provider_id", "region_id", "storage_type", "storage_name"],
            set_={"price_per_gb_month": item["price_gb_month"]}
        )
        await db.execute(stmt)


async def _ingest_gcp_reserved_fallback(db: AsyncSession, gcp_regions: dict):
    """Ingest GCP reserved pricing (CUDs) fallback data."""
    from app.models.reserved_pricing import ReservedTerm, ReservedPaymentType
    
    reserved_data = get_gcp_reserved_data()
    for item in reserved_data:
        region = gcp_regions.get(item["region"])
        if not region:
            continue

        # Convert string to enum member by looking up via value
        term_enum = ReservedTerm(item["term"])
        payment_enum = ReservedPaymentType(item["payment"])
        
        stmt = insert(ReservedPricing).values(
            region_id=region.id,
            provider_id=region.provider_id,
            instance_type=item["instance"],
            os_type=item["os"],
            term=term_enum,
            payment_type=payment_enum,
            upfront_cost=item["upfront"],
            monthly_cost=item["monthly"],
            effective_hourly=item["eff_hourly"],
            savings_vs_ondemand=item["savings"],
        ).on_conflict_do_update(
            index_elements=["provider_id", "region_id", "instance_type", "os_type", "term", "payment_type"],
            set_={
                "upfront_cost": item["upfront"],
                "monthly_cost": item["monthly"],
                "effective_hourly": item["eff_hourly"],
                "savings_vs_ondemand": item["savings"],
            }
        )
        await db.execute(stmt)
