from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, AuthResponse, ErrorResponse
from app.schemas.user import UserResponse
from app.core.security import verify_password, hash_password, create_access_token, get_current_user, require_admin
from app.core.audit import log_audit

router = APIRouter()


@router.post("/login", response_model=AuthResponse, responses={401: {"model": ErrorResponse}})
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """User login — returns JWT token."""
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        await log_audit(
            db,
            action="login_failed",
            status="error",
            ip_address=request.client.host if request.client else None,
            input_data={"email": login_data.email}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Unauthorized", "message": "Invalid email or password"}
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Create JWT token — use camelCase keys
    token, expires_at = create_access_token({
        "userId": user.id,
        "email": user.email,
        "role": user.role.value,
    })
    
    await log_audit(
        db,
        action="login",
        status="success",
        user_id=user.id,
        ip_address=request.client.host if request.client else None
    )
    
    return AuthResponse(
        user_id=user.id,
        email=user.email,
        role=user.role.value,
        token=token,
        expires_at=expires_at,
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    register_data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Register new user — admin only."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == register_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Bad Request", "message": "Email already registered"}
        )
    
    # Create new user
    user = User(
        email=register_data.email,
        password_hash=hash_password(register_data.password),
        role=register_data.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Create token
    token, expires_at = create_access_token({
        "userId": user.id,
        "email": user.email,
        "role": user.role.value,
    })
    
    await log_audit(
        db,
        action="register",
        status="success",
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        input_data={"email": user.email, "role": user.role.value}
    )
    
    return AuthResponse(
        user_id=user.id,
        email=user.email,
        role=user.role.value,
        token=token,
        expires_at=expires_at,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse.model_validate(current_user)
