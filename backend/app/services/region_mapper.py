"""
Region Mapping Service

Maps equivalent regions across AWS, Azure, and GCP based on geographic proximity.
"""
import logging
from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.provider import Region, Provider

logger = logging.getLogger(__name__)

# Geographic region equivalence mapping
# Maps regions across providers based on geographic location
REGION_EQUIVALENCE_MAP = {
    # US East regions
    "us-east": {
        "AWS": ["us-east-1", "us-east-2"],
        "Azure": ["eastus", "eastus2"],
        "GCP": ["us-east1", "us-east4"],
    },
    # US West regions
    "us-west": {
        "AWS": ["us-west-1", "us-west-2"],
        "Azure": ["westus", "westus2", "westus3"],
        "GCP": ["us-west1", "us-west2", "us-west3", "us-west4"],
    },
    # Europe regions
    "europe": {
        "AWS": ["eu-west-1", "eu-west-2", "eu-central-1"],
        "Azure": ["westeurope", "northeurope", "germanywestcentral"],
        "GCP": ["europe-west1", "europe-west2", "europe-west3"],
    },
    # Asia Pacific - India
    "asia-india": {
        "AWS": ["ap-south-1"],
        "Azure": ["centralindia", "southindia"],
        "GCP": ["asia-south1"],
    },
    # Asia Pacific - Singapore/Southeast Asia
    "asia-southeast": {
        "AWS": ["ap-southeast-1", "ap-southeast-2"],
        "Azure": ["southeastasia", "eastasia"],
        "GCP": ["asia-southeast1", "asia-southeast2"],
    },
}


async def find_equivalent_region_id(
    source_region_id: int,
    target_provider_id: int,
    db: AsyncSession
) -> Optional[int]:
    """
    Find an equivalent region ID in the target provider.

    Args:
        source_region_id: Region ID from the source provider
        target_provider_id: Target provider ID to find equivalent region for
        db: Database session

    Returns:
        Region ID in the target provider, or None if no mapping found
    """
    # Get source region details
    source_result = await db.execute(
        select(Region, Provider.name)
        .join(Provider, Region.provider_id == Provider.id)
        .where(Region.id == source_region_id)
    )
    source_row = source_result.first()
    if not source_row:
        logger.warning(f"Source region {source_region_id} not found")
        return None

    source_region, source_provider_name = source_row
    source_region_code = source_region.region_code

    logger.info(f"Finding equivalent for {source_provider_name} {source_region_code}")

    # If target provider is same as source, return same region
    if target_provider_id == source_region.provider_id:
        return source_region_id

    # Get target provider name
    target_result = await db.execute(
        select(Provider.name).where(Provider.id == target_provider_id)
    )
    target_provider_name = target_result.scalar_one_or_none()
    if not target_provider_name:
        logger.warning(f"Target provider {target_provider_id} not found")
        return None

    # Find the geographic group containing the source region
    geographic_group = None
    for group_name, group_map in REGION_EQUIVALENCE_MAP.items():
        if source_provider_name in group_map:
            if source_region_code in group_map[source_provider_name]:
                geographic_group = group_name
                break

    if not geographic_group:
        logger.warning(f"No geographic mapping found for {source_provider_name} {source_region_code}")
        return await _find_default_region(target_provider_id, db)

    # Get equivalent region codes for target provider
    target_region_codes = REGION_EQUIVALENCE_MAP[geographic_group].get(target_provider_name, [])
    if not target_region_codes:
        logger.warning(f"No equivalent regions for {target_provider_name} in group {geographic_group}")
        return await _find_default_region(target_provider_id, db)

    # Find first available region in target provider
    for region_code in target_region_codes:
        result = await db.execute(
            select(Region.id)
            .where(Region.provider_id == target_provider_id)
            .where(Region.region_code == region_code)
        )
        region_id = result.scalar_one_or_none()
        if region_id:
            logger.info(f"Mapped {source_provider_name} {source_region_code} -> {target_provider_name} {region_code}")
            return region_id

    # Fallback to default region
    logger.warning(f"No matching region found, using default for {target_provider_name}")
    return await _find_default_region(target_provider_id, db)


async def _find_default_region(provider_id: int, db: AsyncSession) -> Optional[int]:
    """
    Get the default region for a provider (typically first us-east/eastus/us-east1).

    Args:
        provider_id: Provider ID
        db: Database session

    Returns:
        Default region ID, or None if provider has no regions
    """
    result = await db.execute(
        select(Region.id)
        .where(Region.provider_id == provider_id)
        .order_by(Region.id.asc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def build_region_mapping_for_providers(
    source_region_id: int,
    target_provider_ids: list[int],
    db: AsyncSession
) -> Dict[int, int]:
    """
    Build a complete region mapping for all target providers.

    Args:
        source_region_id: Source region ID
        target_provider_ids: List of target provider IDs
        db: Database session

    Returns:
        Dict mapping provider_id to equivalent region_id
    """
    region_mapping = {}

    for provider_id in target_provider_ids:
        equivalent_region_id = await find_equivalent_region_id(
            source_region_id,
            provider_id,
            db
        )
        if equivalent_region_id:
            region_mapping[provider_id] = equivalent_region_id

    logger.info(f"Built region mapping: {region_mapping}")
    return region_mapping
