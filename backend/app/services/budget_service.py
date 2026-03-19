from datetime import datetime, timedelta
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.budget import Budget, BudgetAlert, BudgetPeriod, AlertStatus
from app.models.calculation import Calculation


async def get_period_start_date(period: BudgetPeriod) -> datetime:
    """Calculate the start date for the current budget period."""
    now = datetime.utcnow()
    
    if period == BudgetPeriod.monthly:
        return datetime(now.year, now.month, 1)
    elif period == BudgetPeriod.quarterly:
        quarter_month = ((now.month - 1) // 3) * 3 + 1
        return datetime(now.year, quarter_month, 1)
    elif period == BudgetPeriod.annual:
        return datetime(now.year, 1, 1)
    
    return now


async def compute_budget_status(budget: Budget, db: AsyncSession) -> Dict:
    """
    Compute current spend for a budget by summing calculations in current period.
    Returns: {current_spend, pct_used, status}
    """
    period_start = await get_period_start_date(budget.period)
    
    # Build query for calculations in the period
    query = select(func.coalesce(func.sum(Calculation.aws_total_monthly), 0) +
                   func.coalesce(func.sum(Calculation.azure_total_monthly), 0) +
                   func.coalesce(func.sum(Calculation.gcp_total_monthly), 0)
    ).where(
        Calculation.user_id == budget.user_id,
        Calculation.created_at >= period_start,
    )
    
    # Filter by provider if budget is provider-specific
    if budget.provider:
        provider_col = getattr(Calculation, f"{budget.provider.lower()}_total_monthly", None)
        if provider_col is not None:
            query = select(func.coalesce(func.sum(provider_col), 0)).where(
                Calculation.user_id == budget.user_id,
                Calculation.created_at >= period_start,
            )
    
    result = await db.execute(query)
    current_spend = float(result.scalar() or 0.0)
    
    # Calculate percentage
    pct_used = (current_spend / float(budget.budget_amount)) * 100 if budget.budget_amount > 0 else 0.0
    
    # Determine status
    if pct_used >= 100:
        status = "exceeded"
    elif pct_used >= float(budget.alert_threshold):
        status = "warning"
    else:
        status = "ok"
    
    # Check if we need to create an alert
    if status in ["warning", "exceeded"]:
        # Check if there's already an active alert for this threshold
        result = await db.execute(
            select(BudgetAlert).where(
                BudgetAlert.budget_id == budget.id,
                BudgetAlert.status == AlertStatus.active,
            )
        )
        existing_alert = result.scalar_one_or_none()
        
        if not existing_alert:
            # Create new alert
            alert = BudgetAlert(
                budget_id=budget.id,
                current_spend=current_spend,
                threshold_pct=pct_used,
                status=AlertStatus.active,
                message=f"Budget '{budget.name}' has reached {pct_used:.1f}% of limit (${current_spend:.2f} / ${budget.budget_amount:.2f})"
            )
            db.add(alert)
            await db.commit()
    
    return {
        "current_spend": round(current_spend, 2),
        "pct_used": round(pct_used, 2),
        "status": status,
    }
