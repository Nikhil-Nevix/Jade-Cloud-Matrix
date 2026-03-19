from typing import Optional
from pydantic import BaseModel


class Recommendation(BaseModel):
    title: str
    category: str
    priority: str
    estimated_monthly_savings: float
    estimated_annual_savings: float
    description: str
    action_steps: list[str]
    affected_providers: list[str]


class RecommendationResponse(BaseModel):
    id: str
    generated_at: str
    calculations_analysed: int
    recommendations: list[Recommendation]
    total_estimated_monthly_savings: float
    total_estimated_annual_savings: float
    summary: str


class GenerateRecommendationRequest(BaseModel):
    calculation_ids: list[int]
    focus_areas: Optional[list[str]] = None
