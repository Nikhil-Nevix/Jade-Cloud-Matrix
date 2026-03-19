from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db
from app.models.network_pricing import NetworkPricing
from app.models.provider import Provider, Region
from app.models.user import User
from app.models.calculation import Calculation
from app.schemas.network_pricing import NetworkPricingResponse, NetworkCalculateRequest, NetworkTransfer
from app.schemas.calculation import CalculationResult
from app.core.security import get_current_user
from app.core.audit import log_audit
from app.services.network_engine import calculate_network_cost, NetworkTransferInput

router = APIRouter()


@router.get("/pricing", response_model=List[NetworkPricingResponse])
async def get_network_pricing(
    provider_id: Optional[int] = Query(None),
    source_region_id: Optional[int] = Query(None),
    destination_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get network/data transfer pricing with optional filters."""
    query = select(
        NetworkPricing,
        Provider.name.label("provider_name"),
        Region.region_code
    ).join(Provider, NetworkPricing.provider_id == Provider.id
    ).join(Region, NetworkPricing.source_region_id == Region.id)
    
    if provider_id:
        query = query.where(NetworkPricing.provider_id == provider_id)
    if source_region_id:
        query = query.where(NetworkPricing.source_region_id == source_region_id)
    if destination_type:
        query = query.where(NetworkPricing.destination_type == destination_type)
    
    result = await db.execute(query.order_by(Provider.name, Region.region_code))
    rows = result.all()
    
    return [
        NetworkPricingResponse(
            id=row.NetworkPricing.id,
            provider_id=row.NetworkPricing.provider_id,
            provider_name=row.provider_name,
            source_region_id=row.NetworkPricing.source_region_id,
            region_code=row.region_code,
            destination_type=row.NetworkPricing.destination_type,
            price_per_gb=float(row.NetworkPricing.price_per_gb),
            free_tier_gb=float(row.NetworkPricing.free_tier_gb),
            updated_at=row.NetworkPricing.updated_at,
        )
        for row in rows
    ]


@router.post("/calculate", status_code=status.HTTP_201_CREATED)
async def calculate_network(
    request: Request,
    calc_request: NetworkCalculateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate network data transfer costs."""
    transfers = [NetworkTransferInput(t.network_pricing_id, t.transfer_gb) for t in calc_request.transfers]
    
    result = await calculate_network_cost(
        db,
        transfers,
        calc_request.duration_months,
    )
    
    # Save calculation
    calc = Calculation(
        user_id=current_user.id,
        calc_type="network",
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
        action="calculate_network",
        status="success",
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        input_data=calc_request.model_dump()
    )
    
    return {
        "id": calc.id,
        "user_id": calc.user_id,
        "calc_type": calc.calc_type,
        **result
    }
