import httpx
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from app.models.provider import Region
from app.models.pricing import ComputePricing, StoragePricing
from app.models.reserved_pricing import ReservedPricing
from app.services.ingestion.fallback_data import get_azure_compute_data, get_azure_storage_data, get_azure_reserved_data
from app.config import settings

logger = logging.getLogger(__name__)


async def ingest_azure_pricing(db: AsyncSession):
    """
    Ingest Azure pricing from live API or fallback.
    Primary: Azure Retail Pricing API (public, no auth)
    URL: https://prices.azure.com/api/retail/prices
    Fallback: fallback_data.py
    """
    # Check pricing mode
    if settings.PRICING_API_MODE == "fallback":
        logger.info("PRICING_API_MODE=fallback, skipping live Azure API")
        await _ingest_azure_fallback(db)
        return

    try:
        logger.info("Attempting to fetch Azure pricing from live API...")
        await _ingest_azure_live(db)
    except Exception as e:
        logger.warning(f"Azure live API failed: {e}. Using fallback data.")
        await _ingest_azure_fallback(db)


async def _ingest_azure_live(db: AsyncSession):
    """
    Ingest Azure pricing from live Azure Retail Pricing API.
    Uses public REST API with no authentication required.
    """
    # Get Azure regions from database
    result = await db.execute(
        select(Region).join(Region.provider).where(Region.provider.has(name="Azure"))
    )
    azure_regions = {r.region_code: r for r in result.scalars().all()}
    region_codes = list(azure_regions.keys())

    logger.info(f"Fetching Azure pricing for regions: {region_codes}")

    base_url = "https://prices.azure.com/api/retail/prices"
    compute_count = 0

    async with httpx.AsyncClient(timeout=30.0) as client:
        for region_code in region_codes:
            skip = 0
            page_size = 100

            while True:
                try:
                    # Build filter for Virtual Machines in specific region
                    filter_query = f"serviceName eq 'Virtual Machines' and priceType eq 'Consumption' and armRegionName eq '{region_code}'"

                    params = {
                        '$filter': filter_query,
                        '$skip': skip
                    }

                    response = await client.get(base_url, params=params)
                    response.raise_for_status()

                    data = response.json()
                    items = data.get('Items', [])

                    if not items:
                        break  # No more data for this region

                    for item in items:
                        try:
                            compute_count += await _process_azure_compute_price(item, azure_regions, region_code, db)
                        except Exception as e:
                            logger.debug(f"Error processing Azure price: {e}")
                            continue

                    # Check if there's more data
                    next_link = data.get('NextPageLink')
                    if not next_link:
                        break

                    skip += page_size

                    # Safety limit to avoid excessive API calls during dev
                    if compute_count > 500:
                        logger.info(f"Reached limit of 500 instances for {region_code}, stopping")
                        break

                except httpx.HTTPError as e:
                    logger.error(f"Azure API HTTP error for region {region_code}: {e}")
                    break
                except Exception as e:
                    logger.error(f"Azure API error for region {region_code}: {e}")
                    break

    logger.info(f"Ingested {compute_count} Azure compute pricing records from live API")

    # Use fallback for storage and reserved pricing
    logger.info("Using fallback data for Azure storage and reserved pricing")
    await _ingest_azure_storage_fallback(db, azure_regions)
    await _ingest_azure_reserved_fallback(db, azure_regions)

    await db.commit()
    logger.info("Azure live pricing ingestion completed.")


async def _process_azure_compute_price(item: dict, azure_regions: dict, region_code: str, db: AsyncSession) -> int:
    """
    Process a single Azure compute price item from the Retail Pricing API.
    Returns 1 if processed successfully, 0 otherwise.
    """
    try:
        # Extract instance details
        sku_name = item.get('armSkuName')  # e.g., "Standard_D2s_v3"
        if not sku_name:
            return 0

        # Skip non-Linux OS
        product_name = item.get('productName', '').lower()
        if 'windows' in product_name:
            return 0

        # Parse specs from meterName (e.g., "D2s v3" from meterName)
        # For simplicity, we'll extract vCPU and memory from known patterns
        # In production, you might use Azure's Compute API for detailed specs
        vcpu, memory_gb = _parse_azure_instance_specs(sku_name)

        if vcpu == 0:
            return 0  # Skip if we can't determine specs

        # Get hourly price
        retail_price = item.get('retailPrice', 0)
        hourly_price = float(retail_price)

        if hourly_price == 0:
            return 0

        # Insert into database
        region = azure_regions.get(region_code)
        if not region:
            return 0

        stmt = insert(ComputePricing).values(
            region_id=region.id,
            provider_id=region.provider_id,
            instance_type=sku_name.replace('Standard_', ''),  # D2s_v3
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
        return 1

    except Exception as e:
        logger.debug(f"Error parsing Azure price item: {e}")
        return 0


def _parse_azure_instance_specs(sku_name: str) -> tuple:
    """
    Parse Azure instance SKU name to extract vCPU and memory.
    This is a simplified parser. In production, use Azure Compute API for accurate specs.
    """
    # Known Azure instance families and their specs
    # Format: sku_prefix -> (vcpu, memory_gb)
    specs_map = {
        # B-series (Burstable)
        'B1ls': (1, 0.5), 'B1s': (1, 1), 'B1ms': (1, 2), 'B2s': (2, 4), 'B2ms': (2, 8),
        'B4ms': (4, 16), 'B8ms': (8, 32), 'B12ms': (12, 48), 'B16ms': (16, 64), 'B20ms': (20, 80),
        # D-series v3 (General Purpose)
        'D2s_v3': (2, 8), 'D4s_v3': (4, 16), 'D8s_v3': (8, 32), 'D16s_v3': (16, 64),
        'D32s_v3': (32, 128), 'D48s_v3': (48, 192), 'D64s_v3': (64, 256), 'D96s_v3': (96, 384),
        # D-series v4
        'D2s_v4': (2, 8), 'D4s_v4': (4, 16), 'D8s_v4': (8, 32), 'D16s_v4': (16, 64),
        'D32s_v4': (32, 128), 'D48s_v4': (48, 192), 'D64s_v4': (64, 256),
        # D-series v5 (AMD)
        'D2as_v4': (2, 8), 'D4as_v4': (4, 16), 'D8as_v4': (8, 32), 'D16as_v4': (16, 64),
        'D32as_v4': (32, 128), 'D48as_v4': (48, 192), 'D64as_v4': (64, 256), 'D96as_v4': (96, 384),
        # E-series (Memory Optimized)
        'E2s_v3': (2, 16), 'E4s_v3': (4, 32), 'E8s_v3': (8, 64), 'E16s_v3': (16, 128),
        'E32s_v3': (32, 256), 'E48s_v3': (48, 384), 'E64s_v3': (64, 432), 'E96s_v3': (96, 672),
        'E2as_v4': (2, 16), 'E4as_v4': (4, 32), 'E8as_v4': (8, 64), 'E16as_v4': (16, 128),
        'E32as_v4': (32, 256), 'E48as_v4': (48, 384), 'E64as_v4': (64, 512), 'E96as_v4': (96, 672),
        # F-series (Compute Optimized)
        'F2s_v2': (2, 4), 'F4s_v2': (4, 8), 'F8s_v2': (8, 16), 'F16s_v2': (16, 32),
        'F32s_v2': (32, 64), 'F48s_v2': (48, 96), 'F64s_v2': (64, 128), 'F72s_v2': (72, 144),
    }

    # Remove 'Standard_' prefix if present
    clean_sku = sku_name.replace('Standard_', '')

    return specs_map.get(clean_sku, (0, 0))


async def _ingest_azure_fallback(db: AsyncSession):
    """Ingest Azure fallback data."""
    result = await db.execute(select(Region).join(Region.provider).where(Region.provider.has(name="Azure")))
    azure_regions = {r.region_code: r for r in result.scalars().all()}

    await _ingest_azure_compute_fallback(db, azure_regions)
    await _ingest_azure_storage_fallback(db, azure_regions)
    await _ingest_azure_reserved_fallback(db, azure_regions)

    await db.commit()
    logger.info("Azure fallback pricing ingestion completed.")


async def _ingest_azure_compute_fallback(db: AsyncSession, azure_regions: dict):
    """Ingest Azure compute fallback data."""
    compute_data = get_azure_compute_data()
    for item in compute_data:
        region = azure_regions.get(item["region"])
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


async def _ingest_azure_storage_fallback(db: AsyncSession, azure_regions: dict):
    """Ingest Azure storage fallback data."""
    storage_data = get_azure_storage_data()
    for item in storage_data:
        region = azure_regions.get(item["region"])
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


async def _ingest_azure_reserved_fallback(db: AsyncSession, azure_regions: dict):
    """Ingest Azure reserved pricing fallback data."""
    from app.models.reserved_pricing import ReservedTerm, ReservedPaymentType
    
    reserved_data = get_azure_reserved_data()
    for item in reserved_data:
        region = azure_regions.get(item["region"])
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
