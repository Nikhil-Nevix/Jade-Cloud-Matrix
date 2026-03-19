from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db
from app.models.kubernetes_pricing import KubernetesPricing
from app.models.provider import Provider, Region
from app.models.user import User
from app.models.calculation import Calculation
from app.schemas.kubernetes_pricing import KubernetesPricingResponse, KubernetesCalculateRequest
from app.schemas.calculation import CalculationResult
from app.core.security import get_current_user
from app.core.audit import log_audit
from app.services.kubernetes_engine import calculate_kubernetes_cost

router = APIRouter()


@router.get("/pricing", response_model=List[KubernetesPricingResponse])
async def get_kubernetes_pricing(
    provider_id: Optional[int] = Query(None),
    region_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get Kubernetes node pricing with optional filters."""
    query = select(
        KubernetesPricing,
        Provider.name.label("provider_name"),
        Region.region_code,
        Region.region_name
    ).join(Provider, KubernetesPricing.provider_id == Provider.id
    ).join(Region, KubernetesPricing.region_id == Region.id)
    
    if provider_id:
        query = query.where(KubernetesPricing.provider_id == provider_id)
    if region_id:
        query = query.where(KubernetesPricing.region_id == region_id)
    
    result = await db.execute(query.order_by(Provider.name, Region.region_name))
    rows = result.all()
    
    return [
        KubernetesPricingResponse(
            id=row.KubernetesPricing.id,
            region_id=row.KubernetesPricing.region_id,
            provider_id=row.KubernetesPricing.provider_id,
            provider_name=row.provider_name,
            region_code=row.region_code,
            region_name=row.region_name,
            node_type=row.KubernetesPricing.node_type,
            vcpu=row.KubernetesPricing.vcpu,
            memory_gb=float(row.KubernetesPricing.memory_gb),
            price_per_hour=float(row.KubernetesPricing.price_per_hour),
            price_per_month=float(row.KubernetesPricing.price_per_month),
            cluster_fee_monthly=float(row.KubernetesPricing.cluster_fee_monthly),
            updated_at=row.KubernetesPricing.updated_at,
        )
        for row in rows
    ]


@router.post("/calculate", response_model=CalculationResult, status_code=status.HTTP_201_CREATED)
async def calculate_kubernetes(
    request: Request,
    calc_request: KubernetesCalculateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate Kubernetes cluster costs."""
    result = await calculate_kubernetes_cost(
        db,
        calc_request.provider_id,
        calc_request.region_id,
        calc_request.node_type_id,
        calc_request.node_count,
        calc_request.duration_months,
        calc_request.include_cluster_fee,
    )
    
    # Determine per-provider totals
    provider_name = result["provider_name"]
    total_monthly = result["total_monthly"]
    
    aws_total = total_monthly if provider_name == "AWS" else None
    azure_total = total_monthly if provider_name == "Azure" else None
    gcp_total = total_monthly if provider_name == "GCP" else None
    
    # Save calculation
    calc = Calculation(
        user_id=current_user.id,
        calc_type="kubernetes",
        input_json=calc_request.model_dump(),
        result_json=result,
        cheapest_provider=provider_name,
        aws_total_monthly=aws_total,
        azure_total_monthly=azure_total,
        gcp_total_monthly=gcp_total,
        duration_months=calc_request.duration_months,
    )
    db.add(calc)
    await db.commit()
    await db.refresh(calc)
    
    await log_audit(
        db,
        action="calculate_kubernetes",
        status="success",
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        input_data=calc_request.model_dump()
    )
    
    return CalculationResult(
        id=calc.id,
        user_id=calc.user_id,
        calc_type=calc.calc_type,
        input_json=calc.input_json,
        result_json=calc.result_json,
        cheapest_provider=calc.cheapest_provider,
        aws_total_monthly=float(calc.aws_total_monthly) if calc.aws_total_monthly else None,
        azure_total_monthly=float(calc.azure_total_monthly) if calc.azure_total_monthly else None,
        gcp_total_monthly=float(calc.gcp_total_monthly) if calc.gcp_total_monthly else None,
        aws_total_annual=float(calc.aws_total_monthly) * 12 if calc.aws_total_monthly else None,
        azure_total_annual=float(calc.azure_total_monthly) * 12 if calc.azure_total_monthly else None,
        gcp_total_annual=float(calc.gcp_total_monthly) * 12 if calc.gcp_total_monthly else None,
        duration_months=calc.duration_months,
        created_at=calc.created_at,
        provider_breakdowns=[]
    )
