import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from app.models.provider import Provider, Region
from app.models.kubernetes_pricing import KubernetesPricing
from app.models.network_pricing import NetworkPricing
from app.services.ingestion.aws_ingester import ingest_aws_pricing
from app.services.ingestion.azure_ingester import ingest_azure_pricing
from app.services.ingestion.gcp_ingester import ingest_gcp_pricing
from app.services.ingestion.fallback_data import get_kubernetes_data, get_network_data

logger = logging.getLogger(__name__)


async def run_full_ingestion(db: AsyncSession):
    """
    Run full pricing ingestion for all providers.
    Called by scheduler daily and manually via admin endpoint.
    """
    logger.info("Starting full pricing ingestion...")
    
    try:
        # Ingest provider pricing
        await ingest_aws_pricing(db)
        await ingest_azure_pricing(db)
        await ingest_gcp_pricing(db)
        
        # Ingest Kubernetes and Network pricing (always use fallback for now)
        await _ingest_kubernetes_fallback(db)
        await _ingest_network_fallback(db)
        
        logger.info("Full pricing ingestion completed successfully.")
    except Exception as e:
        logger.error(f"Pricing ingestion failed: {e}")
        raise


async def _ingest_kubernetes_fallback(db: AsyncSession):
    """Ingest Kubernetes pricing fallback."""
    # Map provider name to region
    providers_map = {}
    result = await db.execute(select(Provider))
    for provider in result.scalars().all():
        providers_map[provider.name] = provider.id
    
    result = await db.execute(select(Region))
    all_regions = {(r.provider_id, r.region_code): r for r in result.scalars().all()}
    
    k8s_data = get_kubernetes_data()
    for item in k8s_data:
        provider_id = providers_map.get(item["provider"])
        if not provider_id:
            continue
        
        region = all_regions.get((provider_id, item["region"]))
        if not region:
            continue
        
        stmt = insert(KubernetesPricing).values(
            region_id=region.id,
            provider_id=provider_id,
            node_type=item["node_type"],
            vcpu=item["vcpu"],
            memory_gb=item["mem"],
            price_per_hour=item["hourly"],
            price_per_month=item["monthly"],
            cluster_fee_monthly=item["cluster_fee"],
        ).on_conflict_do_update(
            index_elements=["provider_id", "region_id", "node_type"],
            set_={
                "price_per_hour": item["hourly"],
                "price_per_month": item["monthly"],
                "cluster_fee_monthly": item["cluster_fee"],
            }
        )
        await db.execute(stmt)
    
    await db.commit()
    logger.info("Kubernetes pricing ingestion completed.")


async def _ingest_network_fallback(db: AsyncSession):
    """Ingest network pricing fallback."""
    providers_map = {}
    result = await db.execute(select(Provider))
    for provider in result.scalars().all():
        providers_map[provider.name] = provider.id
    
    result = await db.execute(select(Region))
    all_regions = {(r.provider_id, r.region_code): r for r in result.scalars().all()}
    
    network_data = get_network_data()
    for item in network_data:
        provider_id = providers_map.get(item["provider"])
        if not provider_id:
            continue
        
        region = all_regions.get((provider_id, item["region"]))
        if not region:
            continue
        
        stmt = insert(NetworkPricing).values(
            provider_id=provider_id,
            source_region_id=region.id,
            destination_type=item["dest"],
            price_per_gb=item["price_gb"],
            free_tier_gb=item["free_tier"],
        ).on_conflict_do_update(
            index_elements=["provider_id", "source_region_id", "destination_type"],
            set_={
                "price_per_gb": item["price_gb"],
                "free_tier_gb": item["free_tier"],
            }
        )
        await db.execute(stmt)
    
    await db.commit()
    logger.info("Network pricing ingestion completed.")
