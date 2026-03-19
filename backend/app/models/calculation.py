from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base


class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    calc_type = Column(String(50), nullable=False, default="standard", index=True)
    input_json = Column(JSON, nullable=False)
    result_json = Column(JSON, nullable=False)
    cheapest_provider = Column(String(50), nullable=True)
    aws_total_monthly = Column(Numeric(12, 2), nullable=True)
    azure_total_monthly = Column(Numeric(12, 2), nullable=True)
    gcp_total_monthly = Column(Numeric(12, 2), nullable=True)
    duration_months = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
