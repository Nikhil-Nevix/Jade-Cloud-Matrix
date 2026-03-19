from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class KubernetesPricingResponse(BaseModel):
    id: int
    region_id: int
    provider_id: int
    provider_name: Optional[str] = None
    region_code: Optional[str] = None
    region_name: Optional[str] = None
    node_type: str
    vcpu: int
    memory_gb: float
    price_per_hour: float
    price_per_month: float
    cluster_fee_monthly: float
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class KubernetesCalculateRequest(BaseModel):
    provider_id: int
    region_id: int
    node_count: int
    node_type_id: int
    duration_months: int
    include_cluster_fee: bool = True
