from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class KubernetesPricing(Base):
    __tablename__ = "kubernetes_pricing"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id", ondelete="CASCADE"), nullable=False, index=True)
    node_type = Column(String(100), nullable=False)
    vcpu = Column(Integer, nullable=False)
    memory_gb = Column(Numeric(5, 2), nullable=False)
    price_per_hour = Column(Numeric(10, 6), nullable=False)
    price_per_month = Column(Numeric(10, 2), nullable=False)
    cluster_fee_monthly = Column(Numeric(10, 2), nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
