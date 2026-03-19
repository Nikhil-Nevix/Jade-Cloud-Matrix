from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db
from app.models.budget import Budget, BudgetAlert
from app.models.user import User
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse, BudgetAlertResponse, BudgetAlertUpdate
from app.core.security import get_current_user
from app.core.audit import log_audit
from app.services.budget_service import compute_budget_status

router = APIRouter()


@router.get("", response_model=List[BudgetResponse])
async def get_budgets(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all budgets for current user with computed status."""
    result = await db.execute(
        select(Budget)
        .where(Budget.user_id == current_user.id)
        .order_by(Budget.created_at.desc())
    )
    budgets = result.scalars().all()
    
    # Compute status for each budget
    responses = []
    for budget in budgets:
        status_data = await compute_budget_status(budget, db)
        responses.append(BudgetResponse(
            id=budget.id,
            user_id=budget.user_id,
            name=budget.name,
            provider=budget.provider,
            budget_amount=float(budget.budget_amount),
            period=budget.period.value,
            alert_threshold=float(budget.alert_threshold),
            is_active=budget.is_active,
            current_spend=status_data["current_spend"],
            pct_used=status_data["pct_used"],
            status=status_data["status"],
            created_at=budget.created_at,
            updated_at=budget.updated_at,
        ))
    
    return responses


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    request: Request,
    budget_data: BudgetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new budget."""
    budget = Budget(
        user_id=current_user.id,
        name=budget_data.name,
        provider=budget_data.provider,
        budget_amount=budget_data.budget_amount,
        period=budget_data.period,
        alert_threshold=budget_data.alert_threshold,
    )
    db.add(budget)
    await db.commit()
    await db.refresh(budget)
    
    await log_audit(
        db,
        action="create_budget",
        status="success",
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        input_data=budget_data.model_dump()
    )
    
    status_data = await compute_budget_status(budget, db)
    
    return BudgetResponse(
        id=budget.id,
        user_id=budget.user_id,
        name=budget.name,
        provider=budget.provider,
        budget_amount=float(budget.budget_amount),
        period=budget.period.value,
        alert_threshold=float(budget.alert_threshold),
        is_active=budget.is_active,
        current_spend=status_data["current_spend"],
        pct_used=status_data["pct_used"],
        status=status_data["status"],
        created_at=budget.created_at,
        updated_at=budget.updated_at,
    )


@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: int,
    request: Request,
    budget_data: BudgetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a budget."""
    result = await db.execute(select(Budget).where(Budget.id == budget_id))
    budget = result.scalar_one_or_none()
    
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    
    # Check access
    if current_user.role != "admin" and budget.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    # Update fields
    if budget_data.name is not None:
        budget.name = budget_data.name
    if budget_data.provider is not None:
        budget.provider = budget_data.provider
    if budget_data.budget_amount is not None:
        budget.budget_amount = budget_data.budget_amount
    if budget_data.period is not None:
        budget.period = budget_data.period
    if budget_data.alert_threshold is not None:
        budget.alert_threshold = budget_data.alert_threshold
    if budget_data.is_active is not None:
        budget.is_active = budget_data.is_active
    
    await db.commit()
    await db.refresh(budget)
    
    await log_audit(
        db,
        action="update_budget",
        status="success",
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        input_data={"budget_id": budget_id, **budget_data.model_dump(exclude_unset=True)}
    )
    
    status_data = await compute_budget_status(budget, db)
    
    return BudgetResponse(
        id=budget.id,
        user_id=budget.user_id,
        name=budget.name,
        provider=budget.provider,
        budget_amount=float(budget.budget_amount),
        period=budget.period.value,
        alert_threshold=float(budget.alert_threshold),
        is_active=budget.is_active,
        current_spend=status_data["current_spend"],
        pct_used=status_data["pct_used"],
        status=status_data["status"],
        created_at=budget.created_at,
        updated_at=budget.updated_at,
    )


@router.delete("/{budget_id}")
async def delete_budget(
    budget_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a budget."""
    result = await db.execute(select(Budget).where(Budget.id == budget_id))
    budget = result.scalar_one_or_none()
    
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    
    # Check access
    if current_user.role != "admin" and budget.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    await db.delete(budget)
    await db.commit()
    
    await log_audit(
        db,
        action="delete_budget",
        status="success",
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        input_data={"budget_id": budget_id}
    )
    
    return {"message": "Budget deleted successfully"}


@router.get("/{budget_id}/alerts", response_model=List[BudgetAlertResponse])
async def get_budget_alerts(
    budget_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get alerts for a budget."""
    # Check budget access
    result = await db.execute(select(Budget).where(Budget.id == budget_id))
    budget = result.scalar_one_or_none()
    
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    
    if current_user.role != "admin" and budget.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    # Get alerts
    result = await db.execute(
        select(BudgetAlert)
        .where(BudgetAlert.budget_id == budget_id)
        .order_by(BudgetAlert.triggered_at.desc())
    )
    alerts = result.scalars().all()
    
    return [BudgetAlertResponse.model_validate(a) for a in alerts]


@router.put("/alerts/{alert_id}", response_model=BudgetAlertResponse)
async def update_budget_alert(
    alert_id: int,
    alert_data: BudgetAlertUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a budget alert (acknowledge or resolve)."""
    result = await db.execute(select(BudgetAlert).where(BudgetAlert.id == alert_id))
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    
    # Check budget access
    result = await db.execute(select(Budget).where(Budget.id == alert.budget_id))
    budget = result.scalar_one_or_none()
    
    if not budget or (current_user.role != "admin" and budget.user_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    alert.status = alert_data.status
    await db.commit()
    await db.refresh(alert)
    
    return BudgetAlertResponse.model_validate(alert)
