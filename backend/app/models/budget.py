import enum
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Boolean, Enum, Text
from sqlalchemy.sql import func
from app.database import Base


class BudgetPeriod(str, enum.Enum):
    monthly = "monthly"
    quarterly = "quarterly"
    annual = "annual"


class AlertStatus(str, enum.Enum):
    active = "active"
    acknowledged = "acknowledged"
    resolved = "resolved"


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    provider = Column(String(50), nullable=True)
    budget_amount = Column(Numeric(12, 2), nullable=False)
    period = Column(Enum(BudgetPeriod, name="budget_period"), nullable=False, default=BudgetPeriod.monthly)
    alert_threshold = Column(Numeric(5, 2), nullable=False, default=80.0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class BudgetAlert(Base):
    __tablename__ = "budget_alerts"

    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False, index=True)
    triggered_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    current_spend = Column(Numeric(12, 2), nullable=False)
    threshold_pct = Column(Numeric(5, 2), nullable=False)
    status = Column(Enum(AlertStatus, name="alert_status"), nullable=False, default=AlertStatus.active)
    message = Column(Text, nullable=True)
