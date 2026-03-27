"""
Multi-Cloud Cost Comparison Engine

This module calculates costs across AWS, Azure, and GCP by automatically mapping
equivalent instances and comparing total costs.
"""
import logging
from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.pricing import ComputePricing, StoragePricing
from app.models.provider import Provider
from app.services.equivalence_engine import find_all_equivalents_for_workload, get_instance_specs

logger = logging.getLogger(__name__)


async def calculate_multicloud_comparison(
    db: AsyncSession,
    base_compute_selections: List[Dict],
    base_storage_selections: List[Dict],
    duration_months: int,
) -> Dict:
    """
    Calculate multi-cloud cost comparison with automatic instance mapping.

    Main calculation logic:
    1. Extract vCPU/memory from base selections
    2. For each unique spec, find equivalents across all 3 providers
    3. Build complete workload for AWS, Azure, GCP
    4. Calculate costs: (compute + storage) * duration_months
    5. Identify cheapest provider
    6. Return detailed breakdown with instance mappings

    Args:
        db: Database session
        base_compute_selections: List of base compute selections (any provider)
        base_storage_selections: List of storage selections
        duration_months: Cost calculation duration

    Returns:
        Dict with provider_breakdowns, instance_mappings, cheapest_provider, etc.
    """
    # Get all provider IDs (AWS=1, Azure=2, GCP=3)
    providers_result = await db.execute(select(Provider))
    providers = {p.id: p.name for p in providers_result.scalars().all()}
    provider_ids = list(providers.keys())

    # Find equivalent instances across all providers
    logger.info(f"Finding equivalents for {len(base_compute_selections)} compute selections")
    workload_by_provider = await find_all_equivalents_for_workload(
        compute_selections=base_compute_selections,
        target_provider_ids=provider_ids,
        db=db
    )

    # Calculate costs for each provider
    provider_costs = {}
    instance_mappings = []   # Track what instances were mapped

    for provider_name, compute_workload in workload_by_provider.items():
        if not compute_workload:  # Skip if no equivalents found
            logger.warning(f"No compute equivalents found for {provider_name}, skipping")
            continue

        # Compute costs
        compute_cost_monthly = 0.0
        for item in compute_workload:
            monthly_cost = float(item["price_per_month"]) * float(item["quantity"])
            compute_cost_monthly += monthly_cost

        # Storage costs (use base storage selections as-is for now)
        # TODO: In future, could also map storage types across providers
        storage_cost_monthly = await _calculate_storage_costs(
            db, base_storage_selections, provider_name
        )

        total_monthly = compute_cost_monthly + storage_cost_monthly
        total_annual = float(total_monthly) * 12
        total_for_duration = float(total_monthly) * float(duration_months)

        provider_costs[provider_name] = {
            "compute_cost_monthly": compute_cost_monthly,
            "storage_cost_monthly": storage_cost_monthly,
            "total_cost_monthly": total_monthly,
            "total_cost_annual": total_annual,
            "total_for_duration": total_for_duration,
            "compute_workload": compute_workload,
        }

    # Identify cheapest provider
    cheapest_provider = min(
        provider_costs.keys(),
        key=lambda p: provider_costs[p]["total_cost_monthly"]
    ) if provider_costs else None

    # Build instance mappings for transparency
    for idx, base_selection in enumerate(base_compute_selections):
        vcpu, memory_gb = await get_instance_specs(base_selection["compute_pricing_id"], db)

        # Get base instance details
        base_result = await db.execute(
            select(ComputePricing, Provider.name)
            .join(Provider, ComputePricing.provider_id == Provider.id)
            .where(ComputePricing.id == base_selection["compute_pricing_id"])
        )
        base_pricing, base_provider_name = base_result.first()

        mapping = {
            "base_instance": base_pricing.instance_type,
            "base_provider": base_provider_name,
            "vcpu": vcpu,
            "memory_gb": float(memory_gb),
            "quantity": base_selection["quantity"],
            "equivalents": {}
        }

        # Add equivalent instances for each provider
        for provider_name, workload in workload_by_provider.items():
            if idx < len(workload) and workload:
                equivalent = workload[idx]
                mapping["equivalents"][provider_name] = {
                    "instance_type": equivalent["instance_type"],
                    "vcpu": equivalent["vcpu"],
                    "memory_gb": equivalent["memory_gb"],
                    "price_per_month": equivalent["price_per_month"],
                }
            else:
                mapping["equivalents"][provider_name] = None

        instance_mappings.append(mapping)

    # Build provider breakdowns
    provider_breakdowns = []
    for provider_name, costs in provider_costs.items():
        breakdown = {
            "provider_name": provider_name,
            "compute_cost_monthly": costs["compute_cost_monthly"],
            "storage_cost_monthly": costs["storage_cost_monthly"],
            "total_cost_monthly": costs["total_cost_monthly"],
            "total_cost_annual": costs["total_cost_annual"],
            "total_for_duration": costs["total_for_duration"],
            "is_cheapest": provider_name == cheapest_provider,
        }
        provider_breakdowns.append(breakdown)

    # Sort by cost (cheapest first)
    provider_breakdowns.sort(key=lambda x: x["total_cost_monthly"])

    # Prepare final result
    result = {
        "provider_breakdowns": provider_breakdowns,
        "instance_mappings": instance_mappings,
        "cheapest_provider": cheapest_provider,
        "duration_months": duration_months,
        "total_instances": len(base_compute_selections),
        "total_storage_volumes": len(base_storage_selections),
    }

    # Add individual provider totals for easy access
    for provider_name, costs in provider_costs.items():
        key_prefix = provider_name.lower().replace(" ", "_")
        result[f"{key_prefix}_total_monthly"] = costs["total_cost_monthly"]
        result[f"{key_prefix}_total_annual"] = costs["total_cost_annual"]

    return result


async def _calculate_storage_costs(
    db: AsyncSession,
    storage_selections: List[Dict],
    target_provider_name: str
) -> float:
    """
    Calculate storage costs for a specific provider.
    Filters storage selections to only those matching the target provider.

    Args:
        db: Database session
        storage_selections: List of storage selections
        target_provider_name: Provider name to filter for

    Returns:
        Total monthly storage cost for the provider
    """
    total_storage_cost = 0.0

    for sel in storage_selections:
        result = await db.execute(
            select(StoragePricing, Provider.name)
            .join(Provider, StoragePricing.provider_id == Provider.id)
            .where(StoragePricing.id == sel["storage_pricing_id"])
        )
        row = result.first()
        if not row:
            continue

        pricing, provider_name = row

        # Only include storage for the target provider
        if provider_name != target_provider_name:
            continue

        monthly_cost = float(pricing.price_per_gb_month) * float(sel["size_gb"])
        total_storage_cost += monthly_cost

    return total_storage_cost
