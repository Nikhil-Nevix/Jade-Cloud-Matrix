from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ProviderResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RegionResponse(BaseModel):
    id: int
    provider_id: int
    region_code: str
    region_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
