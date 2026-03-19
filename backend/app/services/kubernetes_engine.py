from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.kubernetes_pricing import KubernetesPricing
from app.models.provider import Provider, Region


async def calculate_kubernetes_cost(
    db: AsyncSession,
    provider_id: int,
    region_id: int,
    node_type_id: int,
    node_count: int,
    duration_months: int,
    include_cluster_fee: bool,
) -> Dict:
    """
    Calculate Kubernetes cluster cost.
    total_monthly = (node_cost * node_count) + (cluster_fee if include_cluster_fee)
    """
    result = await db.execute(
        select(KubernetesPricing, Provider.name, Region.region_code)
        .join(Provider, KubernetesPricing.provider_id == Provider.id)
        .join(Region, KubernetesPricing.region_id == Region.id)
        .where(KubernetesPricing.id == node_type_id)
    )
    row = result.first()
    if not row:
        raise ValueError("Kubernetes node type not found")
    
    pricing, provider_name, region_code = row
    
    node_cost_monthly = float(pricing.price_per_month) * node_count
    cluster_fee_monthly = float(pricing.cluster_fee_monthly) if include_cluster_fee else 0.0
    total_monthly = node_cost_monthly + cluster_fee_monthly
    total_for_duration = total_monthly * duration_months
    
    return {
        "provider_name": provider_name,
        "region_code": region_code,
        "node_type": pricing.node_type,
        "vcpu": pricing.vcpu,
        "memory_gb": float(pricing.memory_gb),
        "node_count": node_count,
        "node_cost_per_month": round(float(pricing.price_per_month), 2),
        "node_cost_monthly": round(node_cost_monthly, 2),
        "cluster_fee_monthly": round(cluster_fee_monthly, 2),
        "total_monthly": round(total_monthly, 2),
        "total_for_duration": round(total_for_duration, 2),
        "duration_months": duration_months,
        "cheapest_provider": provider_name,
        f"{provider_name.lower()}_total_monthly": total_monthly,
    }
