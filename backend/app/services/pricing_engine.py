from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.pricing import ComputePricing, StoragePricing
from app.models.provider import Provider
from app.schemas.calculation import ComputeSelection, StorageSelection, ProviderBreakdown


async def calculate_standard_pricing(
    db: AsyncSession,
    compute_selections: List[ComputeSelection],
    storage_selections: List[StorageSelection],
    duration_months: int,
) -> Dict:
    """
    Calculate standard compute + storage pricing.
    Returns dict with provider_breakdowns and totals.
    """
    provider_costs = {}
    
    # Compute costs
    for sel in compute_selections:
        result = await db.execute(
            select(ComputePricing, Provider.name)
            .join(Provider, ComputePricing.provider_id == Provider.id)
            .where(ComputePricing.id == sel.compute_pricing_id)
        )
        row = result.first()
        if not row:
            continue
        
        pricing, provider_name = row
        monthly_cost = float(pricing.price_per_month) * sel.quantity
        
        if provider_name not in provider_costs:
            provider_costs[provider_name] = {"compute": 0.0, "storage": 0.0}
        provider_costs[provider_name]["compute"] += monthly_cost
    
    # Storage costs
    for sel in storage_selections:
        result = await db.execute(
            select(StoragePricing, Provider.name)
            .join(Provider, StoragePricing.provider_id == Provider.id)
            .where(StoragePricing.id == sel.storage_pricing_id)
        )
        row = result.first()
        if not row:
            continue
        
        pricing, provider_name = row
        monthly_cost = float(pricing.price_per_gb_month) * sel.size_gb
        
        if provider_name not in provider_costs:
            provider_costs[provider_name] = {"compute": 0.0, "storage": 0.0}
        provider_costs[provider_name]["storage"] += monthly_cost
    
    # Build breakdowns
    breakdowns = []
    for provider_name, costs in provider_costs.items():
        total_monthly = costs["compute"] + costs["storage"]
        breakdowns.append({
            "provider_name": provider_name,
            "compute_cost_monthly": round(costs["compute"], 2),
            "storage_cost_monthly": round(costs["storage"], 2),
            "total_cost_monthly": round(total_monthly, 2),
            "total_cost_annual": round(total_monthly * 12, 2),
            "is_cheapest": False,
        })
    
    # Mark cheapest
    if breakdowns:
        cheapest = min(breakdowns, key=lambda x: x["total_cost_monthly"])
        cheapest["is_cheapest"] = True
        cheapest_provider = cheapest["provider_name"]
    else:
        cheapest_provider = None
    
    # Compute per-provider totals for DB columns
    aws_total = next((b["total_cost_monthly"] for b in breakdowns if b["provider_name"] == "AWS"), None)
    azure_total = next((b["total_cost_monthly"] for b in breakdowns if b["provider_name"] == "Azure"), None)
    gcp_total = next((b["total_cost_monthly"] for b in breakdowns if b["provider_name"] == "GCP"), None)
    
    return {
        "provider_breakdowns": breakdowns,
        "cheapest_provider": cheapest_provider,
        "aws_total_monthly": aws_total,
        "azure_total_monthly": azure_total,
        "gcp_total_monthly": gcp_total,
    }
