from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db
from app.models.reserved_pricing import ReservedPricing
from app.models.provider import Provider, Region
from app.models.user import User
from app.models.calculation import Calculation
from app.schemas.reserved_pricing import ReservedPricingResponse, ReservedCalculateRequest
from app.schemas.calculation import CalculationResult
from app.core.security import get_current_user
from app.core.audit import log_audit
from app.services.reserved_engine import calculate_reserved_pricing

router = APIRouter()


@router.get("/pricing", response_model=List[ReservedPricingResponse])
async def get_reserved_pricing(
    provider_id: Optional[int] = Query(None),
    region_id: Optional[int] = Query(None),
    instance_type: Optional[str] = Query(None),
    term: Optional[str] = Query(None),
    payment_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get reserved instance pricing with optional filters."""
    query = select(
        ReservedPricing,
        Provider.name.label("provider_name"),
        Region.region_code,
        Region.region_name
    ).join(Provider, ReservedPricing.provider_id == Provider.id
    ).join(Region, ReservedPricing.region_id == Region.id)
    
    if provider_id:
        query = query.where(ReservedPricing.provider_id == provider_id)
    if region_id:
        query = query.where(ReservedPricing.region_id == region_id)
    if instance_type:
        query = query.where(ReservedPricing.instance_type == instance_type)
    if term:
        query = query.where(ReservedPricing.term == term)
    if payment_type:
        query = query.where(ReservedPricing.payment_type == payment_type)
    
    result = await db.execute(query.order_by(Provider.name, Region.region_name))
    rows = result.all()
    
    return [
        ReservedPricingResponse(
            id=row.ReservedPricing.id,
            region_id=row.ReservedPricing.region_id,
            provider_id=row.ReservedPricing.provider_id,
            provider_name=row.provider_name,
            region_code=row.region_code,
            region_name=row.region_name,
            instance_type=row.ReservedPricing.instance_type,
            os_type=row.ReservedPricing.os_type,
            term=row.ReservedPricing.term.value,
            payment_type=row.ReservedPricing.payment_type.value,
            upfront_cost=float(row.ReservedPricing.upfront_cost),
            monthly_cost=float(row.ReservedPricing.monthly_cost),
            effective_hourly=float(row.ReservedPricing.effective_hourly),
            savings_vs_ondemand=float(row.ReservedPricing.savings_vs_ondemand),
            updated_at=row.ReservedPricing.updated_at,
        )
        for row in rows
    ]


@router.post("/calculate", response_model=CalculationResult, status_code=status.HTTP_201_CREATED)
async def calculate_reserved(
    request: Request,
    calc_request: ReservedCalculateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate reserved instance costs."""
    result = await calculate_reserved_pricing(
        db,
        calc_request.selections,
        calc_request.duration_months,
    )
    
    # Save calculation
    calc = Calculation(
        user_id=current_user.id,
        calc_type="reserved",
        input_json=calc_request.model_dump(),
        result_json=result,
        cheapest_provider=result.get("cheapest_provider"),
        aws_total_monthly=result.get("aws_total_monthly"),
        azure_total_monthly=result.get("azure_total_monthly"),
        gcp_total_monthly=result.get("gcp_total_monthly"),
        duration_months=calc_request.duration_months,
    )
    db.add(calc)
    await db.commit()
    await db.refresh(calc)
    
    await log_audit(
        db,
        action="calculate_reserved",
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
