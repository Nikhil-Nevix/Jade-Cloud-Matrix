from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class BudgetCreate(BaseModel):
    name: str
    provider: Optional[str] = None
    budget_amount: float
    period: str = "monthly"
    alert_threshold: float = 80.0


class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    budget_amount: Optional[float] = None
    period: Optional[str] = None
    alert_threshold: Optional[float] = None
    is_active: Optional[bool] = None


class BudgetResponse(BaseModel):
    id: int
    user_id: int
    name: str
    provider: Optional[str] = None
    budget_amount: float
    period: str
    alert_threshold: float
    is_active: bool
    current_spend: float = 0.0
    pct_used: float = 0.0
    status: str = "ok"
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BudgetAlertResponse(BaseModel):
    id: int
    budget_id: int
    triggered_at: datetime
    current_spend: float
    threshold_pct: float
    status: str
    message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class BudgetAlertUpdate(BaseModel):
    status: str
