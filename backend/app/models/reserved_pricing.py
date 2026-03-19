import enum
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from app.database import Base


class ReservedTerm(str, enum.Enum):
    one_yr = "1yr"
    three_yr = "3yr"


class ReservedPaymentType(str, enum.Enum):
    no_upfront = "no_upfront"
    partial_upfront = "partial_upfront"
    all_upfront = "all_upfront"


class ReservedPricing(Base):
    __tablename__ = "reserved_pricing"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id", ondelete="CASCADE"), nullable=False, index=True)
    instance_type = Column(String(100), nullable=False, index=True)
    os_type = Column(String(50), nullable=False)
    term = Column(Enum(ReservedTerm), nullable=False)
    payment_type = Column(Enum(ReservedPaymentType), nullable=False)
    upfront_cost = Column(Numeric(10, 2), nullable=False, default=0)
    monthly_cost = Column(Numeric(10, 2), nullable=False)
    effective_hourly = Column(Numeric(10, 6), nullable=False)
    savings_vs_ondemand = Column(Numeric(5, 2), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
