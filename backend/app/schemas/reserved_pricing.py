from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ReservedPricingResponse(BaseModel):
    id: int
    region_id: int
    provider_id: int
    provider_name: Optional[str] = None
    region_code: Optional[str] = None
    region_name: Optional[str] = None
    instance_type: str
    os_type: str
    term: str
    payment_type: str
    upfront_cost: float
    monthly_cost: float
    effective_hourly: float
    savings_vs_ondemand: float
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReservedSelection(BaseModel):
    reserved_pricing_id: int
    quantity: int


class ReservedCalculateRequest(BaseModel):
    selections: list[ReservedSelection]
    duration_months: int
