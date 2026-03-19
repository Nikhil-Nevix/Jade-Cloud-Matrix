import httpx
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from app.models.provider import Region
from app.models.pricing import ComputePricing, StoragePricing
from app.models.reserved_pricing import ReservedPricing
from app.services.ingestion.fallback_data import get_gcp_compute_data, get_gcp_storage_data, get_gcp_reserved_data

logger = logging.getLogger(__name__)


async def ingest_gcp_pricing(db: AsyncSession):
    """
    Ingest GCP pricing from live API or fallback.
    Primary: GCP Cloud Billing Catalog API
    URL: https://cloudbilling.googleapis.com/v1/services/{service_id}/skus
    Fallback: fallback_data.py
    """
    try:
        logger.info("Attempting to fetch GCP pricing from live API...")
        # Live API would require GCP auth or use public endpoint
        raise Exception("Live GCP API not implemented — using fallback")
    except Exception as e:
        logger.warning(f"GCP API failed: {e}. Using fallback data.")
        await _ingest_gcp_fallback(db)


async def _ingest_gcp_fallback(db: AsyncSession):
    """Ingest GCP fallback data."""
    result = await db.execute(select(Region).join(Region.provider).where(Region.provider.has(name="GCP")))
    gcp_regions = {r.region_code: r for r in result.scalars().all()}
    
    # Compute
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
            }
        )
        await db.execute(stmt)
    
    # Storage
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
    
    # Reserved (CUDs)
    reserved_data = get_gcp_reserved_data()
    for item in reserved_data:
        region = gcp_regions.get(item["region"])
        if not region:
            continue
        
        stmt = insert(ReservedPricing).values(
            region_id=region.id,
            provider_id=region.provider_id,
            instance_type=item["instance"],
            os_type=item["os"],
            term=item["term"],
            payment_type=item["payment"],
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
    
    await db.commit()
    logger.info("GCP fallback pricing ingestion completed.")
