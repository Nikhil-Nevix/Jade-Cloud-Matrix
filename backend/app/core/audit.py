from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog


async def log_audit(
    db: AsyncSession,
    action: str,
    status: str = "success",
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    input_data: Optional[dict] = None,
    error_message: Optional[str] = None,
):
    """
    Create an audit log entry.
    Call this after every significant operation.
    """
    log = AuditLog(
        user_id=user_id,
        action=action,
        status=status,
        input_data=input_data,
        error_message=error_message,
        ip_address=ip_address,
    )
    db.add(log)
    await db.commit()
