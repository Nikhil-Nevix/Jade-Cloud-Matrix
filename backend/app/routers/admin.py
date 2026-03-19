from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.dependencies import get_db
from app.models.user import User
from app.models.calculation import Calculation
from app.models.budget import Budget
from app.models.audit_log import AuditLog
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.audit_log import AuditLogResponse, AuditLogListResponse
from app.core.security import require_admin, hash_password
from app.core.audit import log_audit
from app.services.ingestion.runner import run_full_ingestion

router = APIRouter()


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all users — admin only."""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return [UserResponse.model_validate(u) for u in users]


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: Request,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new user — admin only."""
    # Check if email exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Bad Request", "message": "Email already exists"}
        )
    
    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    await log_audit(
        db,
        action="create_user",
        status="success",
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        input_data={"email": user.email, "role": user.role.value}
    )
    
    return UserResponse.model_validate(user)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    request: Request,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update a user — admin only."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Update fields
    if user_data.email is not None:
        # Check email uniqueness
        result = await db.execute(select(User).where(User.email == user_data.email, User.id != user_id))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Bad Request", "message": "Email already exists"}
            )
        user.email = user_data.email
    
    if user_data.role is not None:
        user.role = user_data.role
    
    if user_data.password is not None:
        user.password_hash = hash_password(user_data.password)
    
    await db.commit()
    await db.refresh(user)
    
    await log_audit(
        db,
        action="update_user",
        status="success",
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        input_data={"user_id": user_id, **user_data.model_dump(exclude_unset=True)}
    )
    
    return UserResponse.model_validate(user)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a user — admin only. Cannot delete own account."""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Bad Request", "message": "Cannot delete your own account"}
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    await db.delete(user)
    await db.commit()
    
    await log_audit(
        db,
        action="delete_user",
        status="success",
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        input_data={"user_id": user_id, "email": user.email}
    )
    
    return {"message": "User deleted successfully"}


@router.get("/audit-logs", response_model=AuditLogListResponse)
async def get_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get audit logs with filters — admin only."""
    query = select(AuditLog, User.email).outerjoin(User, AuditLog.user_id == User.id)
    
    conditions = []
    if user_id:
        conditions.append(AuditLog.user_id == user_id)
    if action:
        conditions.append(AuditLog.action == action)
    if from_date:
        conditions.append(AuditLog.timestamp >= from_date)
    if to_date:
        conditions.append(AuditLog.timestamp <= to_date)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Get total count
    count_query = select(func.count()).select_from(AuditLog)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Paginate
    query = query.order_by(AuditLog.timestamp.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    rows = result.all()
    
    logs = [
        AuditLogResponse(
            id=row.AuditLog.id,
            user_id=row.AuditLog.user_id,
            user_email=row.email,
            action=row.AuditLog.action,
            input_data=row.AuditLog.input_data,
            status=row.AuditLog.status,
            error_message=row.AuditLog.error_message,
            ip_address=row.AuditLog.ip_address,
            timestamp=row.AuditLog.timestamp,
        )
        for row in rows
    ]
    
    return AuditLogListResponse(logs=logs, total=total, page=page, limit=limit)


@router.get("/stats")
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get admin dashboard statistics."""
    # Total users
    result = await db.execute(select(func.count()).select_from(User))
    total_users = result.scalar()
    
    # Total calculations
    result = await db.execute(select(func.count()).select_from(Calculation))
    total_calculations = result.scalar()
    
    # Total budgets
    result = await db.execute(select(func.count()).select_from(Budget))
    total_budgets = result.scalar()
    
    # Total audit logs
    result = await db.execute(select(func.count()).select_from(AuditLog))
    total_audit_logs = result.scalar()
    
    # Pricing data count
    from app.models.pricing import ComputePricing, StoragePricing
    result = await db.execute(select(func.count()).select_from(ComputePricing))
    compute_count = result.scalar()
    result = await db.execute(select(func.count()).select_from(StoragePricing))
    storage_count = result.scalar()
    pricing_data_count = compute_count + storage_count
    
    # Active users last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    result = await db.execute(
        select(func.count(func.distinct(User.id)))
        .where(User.last_login >= thirty_days_ago)
    )
    active_users = result.scalar()
    
    # Last ingestion time
    result = await db.execute(
        select(AuditLog.timestamp)
        .where(AuditLog.action.in_(["trigger_ingestion", "scheduled_ingestion"]))
        .order_by(AuditLog.timestamp.desc())
        .limit(1)
    )
    last_ingestion = result.scalar_one_or_none()
    
    # Recommendations generated (from audit logs)
    result = await db.execute(
        select(func.count())
        .select_from(AuditLog)
        .where(AuditLog.action == "generate_recommendations", AuditLog.status == "success")
    )
    total_recommendations = result.scalar()
    
    return {
        "total_users": total_users,
        "total_calculations": total_calculations,
        "total_budgets": total_budgets,
        "total_audit_logs": total_audit_logs,
        "pricing_data_count": pricing_data_count,
        "active_users_last_30_days": active_users,
        "last_ingestion": last_ingestion.isoformat() if last_ingestion else None,
        "total_recommendations_generated": total_recommendations,
    }


@router.post("/ingest")
async def trigger_ingestion(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Manually trigger pricing data ingestion — admin only."""
    
    async def ingest_task():
        async with AsyncSessionLocal() as session:
            try:
                await run_full_ingestion(session)
                await log_audit(
                    session,
                    action="trigger_ingestion",
                    status="success",
                    user_id=current_user.id,
                    ip_address=request.client.host if request.client else None
                )
            except Exception as e:
                await log_audit(
                    session,
                    action="trigger_ingestion",
                    status="error",
                    user_id=current_user.id,
                    ip_address=request.client.host if request.client else None,
                    error_message=str(e)
                )
    
    from app.database import AsyncSessionLocal
    background_tasks.add_task(ingest_task)
    
    return {"message": "Pricing ingestion triggered. Data will be updated shortly."}
