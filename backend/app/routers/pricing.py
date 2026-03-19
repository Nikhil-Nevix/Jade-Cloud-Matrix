from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db
from app.models.pricing import ComputePricing, StoragePricing
from app.models.provider import Provider, Region
from app.models.user import User
from app.schemas.pricing import ComputePricingResponse, StoragePricingResponse
from app.core.security import get_current_user

router = APIRouter()


@router.get("/compute", response_model=List[ComputePricingResponse])
async def get_compute_pricing(
    provider_id: Optional[int] = Query(None),
    region_id: Optional[int] = Query(None),
    os_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get compute pricing with optional filters."""
    query = select(
        ComputePricing,
        Provider.name.label("provider_name"),
        Region.region_code,
        Region.region_name
    ).join(Provider, ComputePricing.provider_id == Provider.id
    ).join(Region, ComputePricing.region_id == Region.id)
    
    if provider_id:
        query = query.where(ComputePricing.provider_id == provider_id)
    if region_id:
        query = query.where(ComputePricing.region_id == region_id)
    if os_type:
        query = query.where(ComputePricing.os_type == os_type)
    
    result = await db.execute(query.order_by(Provider.name, Region.region_name, ComputePricing.instance_type))
    rows = result.all()
    
    return [
        ComputePricingResponse(
            id=row.ComputePricing.id,
            region_id=row.ComputePricing.region_id,
            provider_id=row.ComputePricing.provider_id,
            provider_name=row.provider_name,
            region_code=row.region_code,
            region_name=row.region_name,
            instance_type=row.ComputePricing.instance_type,
            os_type=row.ComputePricing.os_type,
            price_per_hour=float(row.ComputePricing.price_per_hour),
            price_per_month=float(row.ComputePricing.price_per_month),
            price_per_year=float(row.ComputePricing.price_per_year),
            vcpu=row.ComputePricing.vcpu,
            memory_gb=float(row.ComputePricing.memory_gb),
            updated_at=row.ComputePricing.updated_at,
        )
        for row in rows
    ]


@router.get("/storage", response_model=List[StoragePricingResponse])
async def get_storage_pricing(
    provider_id: Optional[int] = Query(None),
    region_id: Optional[int] = Query(None),
    storage_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get storage pricing with optional filters."""
    query = select(
        StoragePricing,
        Provider.name.label("provider_name"),
        Region.region_code,
        Region.region_name
    ).join(Provider, StoragePricing.provider_id == Provider.id
    ).join(Region, StoragePricing.region_id == Region.id)
    
    if provider_id:
        query = query.where(StoragePricing.provider_id == provider_id)
    if region_id:
        query = query.where(StoragePricing.region_id == region_id)
    if storage_type:
        query = query.where(StoragePricing.storage_type == storage_type)
    
    result = await db.execute(query.order_by(Provider.name, Region.region_name))
    rows = result.all()
    
    return [
        StoragePricingResponse(
            id=row.StoragePricing.id,
            region_id=row.StoragePricing.region_id,
            provider_id=row.StoragePricing.provider_id,
            provider_name=row.provider_name,
            region_code=row.region_code,
            region_name=row.region_name,
            storage_type=row.StoragePricing.storage_type.value,
            storage_name=row.StoragePricing.storage_name,
            price_per_gb=float(row.StoragePricing.price_per_gb),
            price_per_gb_month=float(row.StoragePricing.price_per_gb_month),
            unit_type=row.StoragePricing.unit_type,
            updated_at=row.StoragePricing.updated_at,
        )
        for row in rows
    ]
