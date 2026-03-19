from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.reserved_pricing import ReservedPricing
from app.models.provider import Provider, Region
from app.schemas.reserved_pricing import ReservedSelection


async def calculate_reserved_pricing(
    db: AsyncSession,
    selections: List[ReservedSelection],
    duration_months: int,
) -> Dict:
    """
    Calculate reserved instance costs.
    total_cost = (upfront_cost * quantity) + (monthly_cost * quantity * duration_months)
    """
    total_upfront = 0.0
    total_monthly = 0.0
    items = []
    provider_totals = {}
    
    for sel in selections:
        result = await db.execute(
            select(ReservedPricing, Provider.name, Region.region_code)
            .join(Provider, ReservedPricing.provider_id == Provider.id)
            .join(Region, ReservedPricing.region_id == Region.id)
            .where(ReservedPricing.id == sel.reserved_pricing_id)
        )
        row = result.first()
        if not row:
            continue
        
        pricing, provider_name, region_code = row
        
        upfront = float(pricing.upfront_cost) * sel.quantity
        monthly = float(pricing.monthly_cost) * sel.quantity
        total_for_duration = upfront + (monthly * duration_months)
        
        items.append({
            "provider_name": provider_name,
            "region_code": region_code,
            "instance_type": pricing.instance_type,
            "os_type": pricing.os_type,
            "term": pricing.term,
            "payment_type": pricing.payment_type,
            "quantity": sel.quantity,
            "upfront_cost": round(upfront, 2),
            "monthly_cost": round(monthly, 2),
            "total_cost": round(total_for_duration, 2),
            "effective_hourly": float(pricing.effective_hourly),
            "savings_vs_ondemand": float(pricing.savings_vs_ondemand),
        })
        
        total_upfront += upfront
        total_monthly += monthly
        
        if provider_name not in provider_totals:
            provider_totals[provider_name] = 0.0
        provider_totals[provider_name] += monthly
    
    total_for_duration = total_upfront + (total_monthly * duration_months)
    
    # Find cheapest provider
    cheapest_provider = min(provider_totals, key=provider_totals.get) if provider_totals else None
    
    return {
        "items": items,
        "total_upfront": round(total_upfront, 2),
        "total_monthly": round(total_monthly, 2),
        "total_for_duration": round(total_for_duration, 2),
        "duration_months": duration_months,
        "cheapest_provider": cheapest_provider,
        "aws_total_monthly": provider_totals.get("AWS"),
        "azure_total_monthly": provider_totals.get("Azure"),
        "gcp_total_monthly": provider_totals.get("GCP"),
    }
