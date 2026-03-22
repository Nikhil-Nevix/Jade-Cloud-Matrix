from datetime import datetime
from sqlalchemy import Column, Integer, DECIMAL, String, DateTime, Index
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class InstanceEquivalence(Base):
    """
    Instance equivalence mapping table for multi-cloud comparisons.
    Maps instance configurations (vCPU + memory) to equivalent instance types
    across AWS, Azure, and GCP.
    """
    __tablename__ = "instance_equivalence"

    id = Column(Integer, primary_key=True, index=True)
    vcpu_count = Column(Integer, nullable=False, index=True)
    memory_gb = Column(DECIMAL(10, 2), nullable=False, index=True)

    # JSONB arrays storing equivalent instance types per provider
    aws_instances = Column(JSONB, nullable=False, default=list)
    azure_instances = Column(JSONB, nullable=False, default=list)
    gcp_instances = Column(JSONB, nullable=False, default=list)

    # Instance category: general_purpose, compute_optimized, memory_optimized, etc.
    category = Column(String(50), nullable=False, default="general_purpose")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Composite index for efficient lookups
    __table_args__ = (
        Index('idx_vcpu_memory', 'vcpu_count', 'memory_gb'),
    )
