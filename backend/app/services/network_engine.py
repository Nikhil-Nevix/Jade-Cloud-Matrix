from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.network_pricing import NetworkPricing
from app.models.provider import Provider, Region


class NetworkTransferInput:
    def __init__(self, network_pricing_id: int, transfer_gb: float):
        self.network_pricing_id = network_pricing_id
        self.transfer_gb = transfer_gb


async def calculate_network_cost(
    db: AsyncSession,
    transfers: List[NetworkTransferInput],
    duration_months: int,
) -> Dict:
    """
    Calculate network data transfer costs.
    billable_gb = max(0, transfer_gb - free_tier_gb)
    cost_monthly = billable_gb * price_per_gb
    """
    provider_breakdowns = []
    provider_totals = {}
    
    for transfer in transfers:
        result = await db.execute(
            select(NetworkPricing, Provider.name, Region.region_code)
            .join(Provider, NetworkPricing.provider_id == Provider.id)
            .join(Region, NetworkPricing.source_region_id == Region.id)
            .where(NetworkPricing.id == transfer.network_pricing_id)
        )
        row = result.first()
        if not row:
            continue
        
        pricing, provider_name, region_code = row
        
        free_tier = float(pricing.free_tier_gb)
        billable_gb = max(0, float(transfer.transfer_gb) - free_tier)
        cost_monthly = billable_gb * float(pricing.price_per_gb)
        cost_for_duration = cost_monthly * float(duration_months)
        
        provider_breakdowns.append({
            "provider_name": provider_name,
            "region_code": region_code,
            "destination_type": pricing.destination_type,
            "transfer_gb": round(transfer.transfer_gb, 2),
            "free_tier_gb": round(free_tier, 2),
            "billable_gb": round(billable_gb, 2),
            "price_per_gb": float(pricing.price_per_gb),
            "cost_monthly": round(cost_monthly, 2),
            "cost_for_duration": round(cost_for_duration, 2),
        })
        
        if provider_name not in provider_totals:
            provider_totals[provider_name] = 0.0
        provider_totals[provider_name] += cost_monthly
    
    total_monthly = sum(provider_totals.values())
    cheapest_provider = min(provider_totals, key=provider_totals.get) if provider_totals else None
    
    return {
        "provider_breakdowns": provider_breakdowns,
        "total_monthly": round(total_monthly, 2),
        "total_for_duration": round(total_monthly * duration_months, 2),
        "duration_months": duration_months,
        "cheapest_provider": cheapest_provider,
        "aws_total_monthly": provider_totals.get("AWS"),
        "azure_total_monthly": provider_totals.get("Azure"),
        "gcp_total_monthly": provider_totals.get("GCP"),
    }
