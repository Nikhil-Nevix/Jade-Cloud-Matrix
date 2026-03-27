import enum
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from app.database import Base


class StorageType(str, enum.Enum):
    block = "block"
    object = "object"


class ComputePricing(Base):
    __tablename__ = "compute_pricing"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id", ondelete="CASCADE"), nullable=False, index=True)
    instance_type = Column(String(100), nullable=False, index=True)
    os_type = Column(String(50), nullable=False)
    price_per_hour = Column(Numeric(10, 6), nullable=False)
    price_per_month = Column(Numeric(10, 2), nullable=False)
    price_per_year = Column(Numeric(10, 2), nullable=False)
    vcpu = Column(Integer, nullable=False)
    memory_gb = Column(Numeric(8, 2), nullable=False)  # Supports up to 999999.99 GB
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class StoragePricing(Base):
    __tablename__ = "storage_pricing"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id", ondelete="CASCADE"), nullable=False, index=True)
    storage_type = Column(Enum(StorageType, name="storage_type"), nullable=False)
    storage_name = Column(String(100), nullable=False)
    price_per_gb = Column(Numeric(10, 6), nullable=False)
    price_per_gb_month = Column(Numeric(10, 6), nullable=False)
    unit_type = Column(String(50), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
