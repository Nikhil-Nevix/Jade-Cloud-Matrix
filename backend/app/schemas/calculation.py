from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ComputeSelection(BaseModel):
    provider_id: int
    region_id: int
    compute_pricing_id: int
    quantity: int


class StorageSelection(BaseModel):
    provider_id: int
    region_id: int
    storage_pricing_id: int
    size_gb: float


class CalculateRequest(BaseModel):
    compute_selections: list[ComputeSelection] = []
    storage_selections: list[StorageSelection] = []
    duration_months: int


class ProviderBreakdown(BaseModel):
    provider_name: str
    compute_cost_monthly: float
    storage_cost_monthly: float
    total_cost_monthly: float
    total_cost_annual: float
    is_cheapest: bool


class CalculationResult(BaseModel):
    id: int
    user_id: int
    calc_type: str
    input_json: dict
    result_json: dict
    cheapest_provider: Optional[str] = None
    aws_total_monthly: Optional[float] = None
    azure_total_monthly: Optional[float] = None
    gcp_total_monthly: Optional[float] = None
    aws_total_annual: Optional[float] = None
    azure_total_annual: Optional[float] = None
    gcp_total_annual: Optional[float] = None
    duration_months: int
    created_at: datetime
    provider_breakdowns: list[ProviderBreakdown] = []

    model_config = ConfigDict(from_attributes=True)


class CalculationListResponse(BaseModel):
    calculations: list[CalculationResult]
    total: int
    page: int
    limit: int
