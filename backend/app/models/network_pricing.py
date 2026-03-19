from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class NetworkPricing(Base):
    __tablename__ = "network_pricing"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id", ondelete="CASCADE"), nullable=False, index=True)
    source_region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    destination_type = Column(String(100), nullable=False)
    price_per_gb = Column(Numeric(10, 6), nullable=False)
    free_tier_gb = Column(Numeric(10, 2), nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
