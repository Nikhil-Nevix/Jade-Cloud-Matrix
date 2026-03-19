from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ComputePricingResponse(BaseModel):
    id: int
    region_id: int
    provider_id: int
    provider_name: Optional[str] = None
    region_code: Optional[str] = None
    region_name: Optional[str] = None
    instance_type: str
    os_type: str
    price_per_hour: float
    price_per_month: float
    price_per_year: float
    vcpu: int
    memory_gb: float
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StoragePricingResponse(BaseModel):
    id: int
    region_id: int
    provider_id: int
    provider_name: Optional[str] = None
    region_code: Optional[str] = None
    region_name: Optional[str] = None
    storage_type: str
    storage_name: str
    price_per_gb: float
    price_per_gb_month: float
    unit_type: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
