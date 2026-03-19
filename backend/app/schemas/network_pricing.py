from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class NetworkPricingResponse(BaseModel):
    id: int
    provider_id: int
    provider_name: Optional[str] = None
    source_region_id: int
    region_code: Optional[str] = None
    destination_type: str
    price_per_gb: float
    free_tier_gb: float
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NetworkTransfer(BaseModel):
    network_pricing_id: int
    transfer_gb: float


class NetworkCalculateRequest(BaseModel):
    transfers: list[NetworkTransfer]
    duration_months: int
