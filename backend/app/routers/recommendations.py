from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db
from app.models.calculation import Calculation
from app.models.user import User
from app.schemas.recommendation import GenerateRecommendationRequest, RecommendationResponse
from app.core.security import get_current_user
from app.core.audit import log_audit
from app.services.ai_recommendations import generate_recommendations

router = APIRouter()


@router.post("/generate", response_model=RecommendationResponse)
async def generate_ai_recommendations(
    request: Request,
    rec_request: GenerateRecommendationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate AI-powered cost optimization recommendations using Claude.
    Analyzes 1-10 calculations and returns actionable insights.
    """
    if not rec_request.calculation_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Bad Request", "message": "At least one calculation_id is required"}
        )
    
    if len(rec_request.calculation_ids) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Bad Request", "message": "Maximum 10 calculations can be analyzed at once"}
        )
    
    # Fetch calculations
    result = await db.execute(
        select(Calculation).where(Calculation.id.in_(rec_request.calculation_ids))
    )
    calculations = result.scalars().all()
    
    # Verify access
    for calc in calculations:
        if current_user.role != "admin" and calc.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": "Forbidden", "message": "Not authorized to access one or more calculations"}
            )
    
    if not calculations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not Found", "message": "No calculations found with provided IDs"}
        )
    
    # Convert to dict for AI service
    calc_dicts = [
        {
            "id": c.id,
            "calc_type": c.calc_type,
            "input_json": c.input_json,
            "result_json": c.result_json,
            "cheapest_provider": c.cheapest_provider,
            "aws_total_monthly": float(c.aws_total_monthly) if c.aws_total_monthly else None,
            "azure_total_monthly": float(c.azure_total_monthly) if c.azure_total_monthly else None,
            "gcp_total_monthly": float(c.gcp_total_monthly) if c.gcp_total_monthly else None,
            "duration_months": c.duration_months,
        }
        for c in calculations
    ]
    
    try:
        recommendations = await generate_recommendations(
            calc_dicts,
            rec_request.focus_areas,
        )
    except Exception as e:
        await log_audit(
            db,
            action="generate_recommendations",
            status="error",
            user_id=current_user.id,
            ip_address=request.client.host if request.client else None,
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal Server Error", "message": str(e)}
        )
    
    await log_audit(
        db,
        action="generate_recommendations",
        status="success",
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        input_data={"calculation_ids": rec_request.calculation_ids, "focus_areas": rec_request.focus_areas}
    )
    
    return recommendations
