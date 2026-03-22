import httpx
import logging
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from app.models.provider import Region
from app.models.pricing import ComputePricing, StoragePricing
from app.models.reserved_pricing import ReservedPricing
from app.services.ingestion.fallback_data import get_aws_compute_data, get_aws_storage_data, get_aws_reserved_data
from app.config import settings

logger = logging.getLogger(__name__)


async def ingest_aws_pricing(db: AsyncSession):
    """
    Ingest AWS pricing from live API or fallback to hardcoded data.
    Primary: AWS Pricing API (public, no auth required)
    Fallback: fallback_data.py
    """
    # Check pricing mode
    if settings.PRICING_API_MODE == "fallback":
        logger.info("PRICING_API_MODE=fallback, skipping live AWS API")
        await _ingest_aws_fallback(db)
        return

    try:
        logger.info("Attempting to fetch AWS pricing from live API...")
        await _ingest_aws_live(db)
    except Exception as e:
        logger.warning(f"AWS live API failed: {e}. Using fallback data.")
        await _ingest_aws_fallback(db)


async def _ingest_aws_live(db: AsyncSession):
    """
    Ingest AWS pricing from live AWS Pricing API using boto3.
    Note: AWS Pricing API response can be very large (~1GB for all EC2 instances).
    We filter for specific regions and instance types to reduce payload.
    """
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
    except ImportError:
        logger.error("boto3 not installed. Run: pip install boto3")
        raise Exception("boto3 not installed")

    # Create AWS Pricing client (us-east-1 is required for Pricing API)
    try:
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            pricing_client = boto3.client(
                'pricing',
                region_name='us-east-1',  # Pricing API only available in us-east-1
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
        else:
            # Try default credentials (environment, IAM role, etc.)
            pricing_client = boto3.client('pricing', region_name='us-east-1')
    except NoCredentialsError:
        logger.warning("No AWS credentials found, will use fallback data")
        raise Exception("No AWS credentials")

    # Get AWS regions from database
    result = await db.execute(
        select(Region).join(Region.provider).where(Region.provider.has(name="AWS"))
    )
    aws_regions = {r.region_code: r for r in result.scalars().all()}
    region_codes = list(aws_regions.keys())

    logger.info(f"Fetching AWS pricing for regions: {region_codes}")

    # Fetch compute pricing for each region
    compute_count = 0
    for region_code in region_codes:
        try:
            # Use paginator to handle large responses
            paginator = pricing_client.get_paginator('get_products')

            filters = [
                {'Type': 'TERM_MATCH', 'Field': 'ServiceCode', 'Value': 'AmazonEC2'},
                {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'Compute Instance'},
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': _aws_region_to_location(region_code)},
                {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
                {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
                {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'},
                {'Type': 'TERM_MATCH', 'Field': 'capacityStatus', 'Value': 'Used'},
            ]

            page_iterator = paginator.paginate(
                ServiceCode='AmazonEC2',
                Filters=filters,
                PaginationConfig={'PageSize': 100}
            )

            for page in page_iterator:
                for price_item in page.get('PriceList', []):
                    try:
                        compute_count += await _process_aws_compute_price(price_item, aws_regions, region_code, db)
                    except Exception as e:
                        logger.warning(f"Error processing AWS compute price: {e}")
                        continue

                # Limit pages to avoid excessive API calls during dev
                if compute_count > 500:  # Adjust as needed
                    logger.info(f"Reached limit of 500 instances for {region_code}, stopping pagination")
                    break

        except ClientError as e:
            logger.error(f"AWS API error for region {region_code}: {e}")
            continue

    logger.info(f"Ingested {compute_count} AWS compute pricing records from live API")

    # For storage and reserved pricing, use fallback for now
    # (Implementing full AWS storage/reserved API is complex and can be added later)
    logger.info("Using fallback data for AWS storage and reserved pricing")
    await _ingest_aws_storage_fallback(db, aws_regions)
    await _ingest_aws_reserved_fallback(db, aws_regions)

    await db.commit()
    logger.info("AWS live pricing ingestion completed.")


async def _process_aws_compute_price(price_item_str: str, aws_regions: dict, region_code: str, db: AsyncSession) -> int:
    """
    Process a single AWS compute price item from the Pricing API.
    Returns 1 if processed successfully, 0 otherwise.
    """
    try:
        price_item = json.loads(price_item_str)
        product = price_item.get('product', {})
        attributes = product.get('attributes', {})

        instance_type = attributes.get('instanceType')
        if not instance_type:
            return 0

        vcpu = int(attributes.get('vcpu', 0))
        memory = attributes.get('memory', '0 GiB').replace(' GiB', '').replace(',', '')
        memory_gb = float(memory) if memory else 0.0

        # Extract pricing (on-demand)
        terms = price_item.get('terms', {})
        on_demand = terms.get('OnDemand', {})
        if not on_demand:
            return 0

        # Get first price dimension
        price_dimensions = None
        for term_key, term_value in on_demand.items():
            price_dimensions = term_value.get('priceDimensions', {})
            break

        if not price_dimensions:
            return 0

        # Get hourly price
        hourly_price = None
        for dim_key, dim_value in price_dimensions.items():
            price_per_unit = dim_value.get('pricePerUnit', {})
            hourly_price = float(price_per_unit.get('USD', 0))
            break

        if hourly_price is None or hourly_price == 0:
            return 0

        # Insert into database
        region = aws_regions.get(region_code)
        if not region:
            return 0

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
        return 1

    except Exception as e:
        logger.debug(f"Error parsing AWS price item: {e}")
        return 0


def _aws_region_to_location(region_code: str) -> str:
    """Map AWS region code to location name used in Pricing API."""
    region_map = {
        'us-east-1': 'US East (N. Virginia)',
        'us-west-2': 'US West (Oregon)',
        'eu-west-1': 'EU (Ireland)',
        'ap-south-1': 'Asia Pacific (Mumbai)',
        'ap-southeast-1': 'Asia Pacific (Singapore)',
        'us-west-1': 'US West (N. California)',
        'eu-central-1': 'EU (Frankfurt)',
        'ap-northeast-1': 'Asia Pacific (Tokyo)',
        'ap-southeast-2': 'Asia Pacific (Sydney)',
    }
    return region_map.get(region_code, region_code)


async def _ingest_aws_fallback(db: AsyncSession):
    """Ingest AWS fallback data into database."""
    # Get AWS provider
    result = await db.execute(select(Region).join(Region.provider).where(Region.provider.has(name="AWS")))
    aws_regions = {r.region_code: r for r in result.scalars().all()}

    await _ingest_aws_compute_fallback(db, aws_regions)
    await _ingest_aws_storage_fallback(db, aws_regions)
    await _ingest_aws_reserved_fallback(db, aws_regions)

    await db.commit()
    logger.info("AWS fallback pricing ingestion completed.")


async def _ingest_aws_compute_fallback(db: AsyncSession, aws_regions: dict):
    """Ingest AWS compute fallback data."""
    compute_data = get_aws_compute_data()
    for item in compute_data:
        region = aws_regions.get(item["region"])
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


async def _ingest_aws_storage_fallback(db: AsyncSession, aws_regions: dict):
    """Ingest AWS storage fallback data."""
    storage_data = get_aws_storage_data()
    for item in storage_data:
        region = aws_regions.get(item["region"])
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
            set_={
                "price_per_gb": item["price_gb_month"],
                "price_per_gb_month": item["price_gb_month"],
            }
        )
        await db.execute(stmt)


async def _ingest_aws_reserved_fallback(db: AsyncSession, aws_regions: dict):
    """Ingest AWS reserved pricing fallback data."""
    from app.models.reserved_pricing import ReservedTerm, ReservedPaymentType
    
    reserved_data = get_aws_reserved_data()
    for item in reserved_data:
        region = aws_regions.get(item["region"])
        if not region:
            continue

        # Convert string to enum member by looking up via value
        term_enum = ReservedTerm(item["term"])  # Lookup enum by value
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
