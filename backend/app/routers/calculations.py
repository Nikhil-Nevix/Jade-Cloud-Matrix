from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from app.dependencies import get_db
from app.models.calculation import Calculation
from app.models.user import User
from app.schemas.calculation import CalculateRequest, CalculationResult, CalculationListResponse, ProviderBreakdown
from app.core.security import get_current_user
from app.core.audit import log_audit
from app.services.pricing_engine import calculate_standard_pricing

router = APIRouter()


@router.post("", response_model=CalculationResult, status_code=status.HTTP_201_CREATED)
async def create_calculation(
    request: Request,
    calc_request: CalculateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new standard pricing calculation (compute + storage)."""
    result = await calculate_standard_pricing(
        db,
        calc_request.compute_selections,
        calc_request.storage_selections,
        calc_request.duration_months,
    )
    
    # Save to database
    calc = Calculation(
        user_id=current_user.id,
        calc_type="standard",
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
        action="calculate_pricing",
        status="success",
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        input_data=calc_request.model_dump()
    )
    
    # Build response
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
        provider_breakdowns=[ProviderBreakdown(**bd) for bd in result.get("provider_breakdowns", [])]
    )


@router.get("", response_model=CalculationListResponse)
async def get_calculations(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    calc_type: Optional[str] = Query(None),
    min_cost: Optional[float] = Query(None),
    max_cost: Optional[float] = Query(None),
    provider: Optional[str] = Query(None),
    cheapest_provider: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get paginated calculations with advanced filtering.
    Users see their own; admins see all.
    """
    # Base query
    query = select(Calculation)
    
    # Users see only their own
    if current_user.role != "admin":
        query = query.where(Calculation.user_id == current_user.id)
    
    # Apply filters
    if from_date:
        query = query.where(Calculation.created_at >= from_date)
    if to_date:
        query = query.where(Calculation.created_at <= to_date)
    if calc_type and calc_type != "all":
        query = query.where(Calculation.calc_type == calc_type)
    if cheapest_provider:
        query = query.where(Calculation.cheapest_provider == cheapest_provider)
    
    # Cost filters
    if min_cost is not None or max_cost is not None:
        cost_conditions = []
        if min_cost is not None:
            cost_conditions.append(
                or_(
                    Calculation.aws_total_monthly >= min_cost,
                    Calculation.azure_total_monthly >= min_cost,
                    Calculation.gcp_total_monthly >= min_cost,
                )
            )
        if max_cost is not None:
            cost_conditions.append(
                and_(
                    or_(Calculation.aws_total_monthly == None, Calculation.aws_total_monthly <= max_cost),
                    or_(Calculation.azure_total_monthly == None, Calculation.azure_total_monthly <= max_cost),
                    or_(Calculation.gcp_total_monthly == None, Calculation.gcp_total_monthly <= max_cost),
                )
            )
        if cost_conditions:
            query = query.where(and_(*cost_conditions))
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Paginate
    query = query.order_by(Calculation.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    calculations = result.scalars().all()
    
    return CalculationListResponse(
        calculations=[
            CalculationResult(
                id=c.id,
                user_id=c.user_id,
                calc_type=c.calc_type,
                input_json=c.input_json,
                result_json=c.result_json,
                cheapest_provider=c.cheapest_provider,
                aws_total_monthly=float(c.aws_total_monthly) if c.aws_total_monthly else None,
                azure_total_monthly=float(c.azure_total_monthly) if c.azure_total_monthly else None,
                gcp_total_monthly=float(c.gcp_total_monthly) if c.gcp_total_monthly else None,
                aws_total_annual=float(c.aws_total_monthly) * 12 if c.aws_total_monthly else None,
                azure_total_annual=float(c.azure_total_monthly) * 12 if c.azure_total_monthly else None,
                gcp_total_annual=float(c.gcp_total_monthly) * 12 if c.gcp_total_monthly else None,
                duration_months=c.duration_months,
                created_at=c.created_at,
                provider_breakdowns=[ProviderBreakdown(**bd) for bd in c.result_json.get("provider_breakdowns", [])]
            )
            for c in calculations
        ],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/{calculation_id}", response_model=CalculationResult)
async def get_calculation(
    calculation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single calculation by ID."""
    result = await db.execute(select(Calculation).where(Calculation.id == calculation_id))
    calc = result.scalar_one_or_none()
    
    if not calc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calculation not found")
    
    # Check access
    if current_user.role != "admin" and calc.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
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
        provider_breakdowns=[ProviderBreakdown(**bd) for bd in calc.result_json.get("provider_breakdowns", [])]
    )


@router.delete("/{calculation_id}")
async def delete_calculation(
    calculation_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a calculation."""
    result = await db.execute(select(Calculation).where(Calculation.id == calculation_id))
    calc = result.scalar_one_or_none()
    
    if not calc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calculation not found")
    
    # Check access
    if current_user.role != "admin" and calc.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    await db.delete(calc)
    await db.commit()
    
    await log_audit(
        db,
        action="delete_calculation",
        status="success",
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        input_data={"calculation_id": calculation_id}
    )
    
    return {"message": "Calculation deleted successfully"}
