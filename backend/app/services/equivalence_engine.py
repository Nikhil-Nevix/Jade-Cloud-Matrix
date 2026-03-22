"""
Instance Equivalence Matching Engine

This module provides functionality to find equivalent instance types across
AWS, Azure, and GCP based on vCPU and memory specifications.
"""
import logging
from typing import Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from app.models.pricing import ComputePricing
from app.models.provider import Provider

logger = logging.getLogger(__name__)


async def find_equivalent_instances(
    vcpu: int,
    memory_gb: float,
    provider_ids: List[int],
    region_ids: Dict[int, int],  # provider_id -> region_id mapping
    db: AsyncSession
) -> Dict[str, Optional[ComputePricing]]:
    """
    Find equivalent instances across providers based on vCPU and memory specs.

    Algorithm:
    1. Query ComputePricing for exact vCPU match
    2. Within vCPU matches, find closest memory match (±10% tolerance)
    3. Prefer exact memory match, fallback to next tier up
    4. Return dict: {"AWS": pricing_obj, "Azure": pricing_obj, "GCP": pricing_obj}

    Args:
        vcpu: Number of vCPUs to match
        memory_gb: Memory in GB to match
        provider_ids: List of provider IDs to search (1=AWS, 2=Azure, 3=GCP)
        region_ids: Dict mapping provider_id to region_id for each provider
        db: Database session

    Returns:
        Dict mapping provider name to ComputePricing object (or None if no match)
    """
    results = {}

    # Calculate memory tolerance (±10%)
    memory_min = memory_gb * 0.9
    memory_max = memory_gb * 1.1

    # Get provider names for result dict keys
    providers_result = await db.execute(
        select(Provider).where(Provider.id.in_(provider_ids))
    )
    providers = {p.id: p.name for p in providers_result.scalars().all()}

    for provider_id in provider_ids:
        region_id = region_ids.get(provider_id)
        if not region_id:
            logger.warning(f"No region specified for provider {provider_id}, skipping")
            results[providers.get(provider_id, f"Provider{provider_id}")] = None
            continue

        # Try exact match first
        exact_match = await _find_exact_match(vcpu, memory_gb, provider_id, region_id, db)
        if exact_match:
            results[providers[provider_id]] = exact_match
            continue

        # Try tolerance match (±10% memory)
        tolerance_match = await _find_tolerance_match(vcpu, memory_min, memory_max, provider_id, region_id, db)
        if tolerance_match:
            results[providers[provider_id]] = tolerance_match
            continue

        # Fallback: next tier up (same vCPU, higher memory)
        next_tier_match = await _find_next_tier(vcpu, memory_gb, provider_id, region_id, db)
        if next_tier_match:
            results[providers[provider_id]] = next_tier_match
            logger.info(f"Using next tier up for provider {provider_id}: {next_tier_match.instance_type}")
            continue

        # No match found
        logger.warning(f"No equivalent found for {vcpu} vCPU, {memory_gb} GB RAM on provider {provider_id}")
        results[providers[provider_id]] = None

    return results


async def _find_exact_match(
    vcpu: int,
    memory_gb: float,
    provider_id: int,
    region_id: int,
    db: AsyncSession
) -> Optional[ComputePricing]:
    """Find instance with exact vCPU and memory match."""
    result = await db.execute(
        select(ComputePricing)
        .where(
            and_(
                ComputePricing.provider_id == provider_id,
                ComputePricing.region_id == region_id,
                ComputePricing.vcpu == vcpu,
                ComputePricing.memory_gb == memory_gb
            )
        )
        .order_by(ComputePricing.price_per_hour.asc())  # Prefer cheapest if multiple matches
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _find_tolerance_match(
    vcpu: int,
    memory_min: float,
    memory_max: float,
    provider_id: int,
    region_id: int,
    db: AsyncSession
) -> Optional[ComputePricing]:
    """Find instance within ±10% memory tolerance."""
    result = await db.execute(
        select(ComputePricing)
        .where(
            and_(
                ComputePricing.provider_id == provider_id,
                ComputePricing.region_id == region_id,
                ComputePricing.vcpu == vcpu,
                ComputePricing.memory_gb >= memory_min,
                ComputePricing.memory_gb <= memory_max
            )
        )
        .order_by(
            # Prefer closest to target memory, then cheapest
            ComputePricing.memory_gb.asc(),
            ComputePricing.price_per_hour.asc()
        )
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _find_next_tier(
    vcpu: int,
    memory_gb: float,
    provider_id: int,
    region_id: int,
    db: AsyncSession
) -> Optional[ComputePricing]:
    """Find next tier up (same vCPU, higher memory)."""
    result = await db.execute(
        select(ComputePricing)
        .where(
            and_(
                ComputePricing.provider_id == provider_id,
                ComputePricing.region_id == region_id,
                ComputePricing.vcpu == vcpu,
                ComputePricing.memory_gb > memory_gb
            )
        )
        .order_by(
            # Get smallest memory tier above target, then cheapest
            ComputePricing.memory_gb.asc(),
            ComputePricing.price_per_hour.asc()
        )
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_instance_specs(
    compute_pricing_id: int,
    db: AsyncSession
) -> Tuple[int, float]:
    """
    Get vCPU and memory_gb for a given compute pricing ID.

    Args:
        compute_pricing_id: ID of the compute pricing entry
        db: Database session

    Returns:
        Tuple of (vcpu, memory_gb)
    """
    result = await db.execute(
        select(ComputePricing.vcpu, ComputePricing.memory_gb)
        .where(ComputePricing.id == compute_pricing_id)
    )
    specs = result.first()
    if not specs:
        raise ValueError(f"Compute pricing ID {compute_pricing_id} not found")
    return specs[0], specs[1]


async def find_all_equivalents_for_workload(
    compute_selections: List[Dict],
    target_provider_ids: List[int],
    db: AsyncSession
) -> Dict[str, List[Dict]]:
    """
    Find equivalent instances for an entire workload across multiple providers.

    Args:
        compute_selections: List of dicts with {compute_pricing_id, provider_id, region_id, quantity}
        target_provider_ids: Provider IDs to find equivalents for (typically [1, 2, 3] for AWS, Azure, GCP)
        db: Database session

    Returns:
        Dict mapping provider name to list of equivalent selections
        Example: {"AWS": [{instance, region, quantity}, ...], "Azure": [...], "GCP": [...]}
    """
    # Get provider names
    providers_result = await db.execute(
        select(Provider).where(Provider.id.in_(target_provider_ids))
    )
    providers = {p.id: p.name for p in providers_result.scalars().all()}

    # Initialize result structure
    workload_by_provider = {name: [] for name in providers.values()}

    # For each compute selection, find equivalents
    for selection in compute_selections:
        vcpu,memory_gb = await get_instance_specs(selection["compute_pricing_id"], db)

        # Build region mapping for this instance (use same regions if possible)
        region_mapping = {pid: selection["region_id"] for pid in target_provider_ids}

        # Find equivalents across all providers
        equivalents = await find_equivalent_instances(
            vcpu=vcpu,
            memory_gb=memory_gb,
            provider_ids=target_provider_ids,
            region_ids=region_mapping,
            db=db
        )

        # Add equivalent instances to each provider's workload
        for provider_name, pricing in equivalents.items():
            if pricing:  # Only add if match was found
                workload_by_provider[provider_name].append({
                    "compute_pricing_id": pricing.id,
                    "provider_id": pricing.provider_id,
                    "region_id": pricing.region_id,
                    "quantity": selection["quantity"],
                    "instance_type": pricing.instance_type,
                    "vcpu": pricing.vcpu,
                    "memory_gb": float(pricing.memory_gb),
                    "price_per_month": float(pricing.price_per_month)
                })

    return workload_by_provider
