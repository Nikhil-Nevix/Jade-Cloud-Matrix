from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db
from app.models.provider import Provider, Region
from app.models.user import User
from app.schemas.provider import ProviderResponse, RegionResponse
from app.core.security import get_current_user

router = APIRouter()


@router.get("", response_model=List[ProviderResponse])
async def get_providers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all cloud providers."""
    result = await db.execute(select(Provider).order_by(Provider.name))
    providers = result.scalars().all()
    return [ProviderResponse.model_validate(p) for p in providers]


@router.get("/{provider_id}/regions", response_model=List[RegionResponse])
async def get_provider_regions(
    provider_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all regions for a provider."""
    result = await db.execute(
        select(Region)
        .where(Region.provider_id == provider_id)
        .order_by(Region.region_name)
    )
    regions = result.scalars().all()
    return [RegionResponse.model_validate(r) for r in regions]
