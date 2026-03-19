from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db
from app.models.calculation import Calculation
from app.models.user import User
from app.core.security import get_current_user
from app.core.audit import log_audit
from app.services.export.pdf_exporter import generate_pdf
from app.services.export.excel_exporter import generate_excel

router = APIRouter()


@router.get("/calculations/{calculation_id}/pdf")
async def export_pdf(
    calculation_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export calculation as PDF."""
    result = await db.execute(select(Calculation).where(Calculation.id == calculation_id))
    calc = result.scalar_one_or_none()
    
    if not calc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calculation not found")
    
    # Check access
    if current_user.role != "admin" and calc.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    # Generate PDF
    calc_dict = {
        "id": calc.id,
        "calc_type": calc.calc_type,
        "input_json": calc.input_json,
        "result_json": calc.result_json,
        "cheapest_provider": calc.cheapest_provider,
        "duration_months": calc.duration_months,
        "created_at": calc.created_at.isoformat(),
    }
    
    pdf_bytes = await generate_pdf(calc_dict, current_user.email)
    
    await log_audit(
        db,
        action="export_pdf",
        status="success",
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        input_data={"calculation_id": calculation_id}
    )
    
    filename = f"jade_report_{calculation_id}_{datetime.utcnow().strftime('%Y%m%d')}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/calculations/{calculation_id}/excel")
async def export_excel(
    calculation_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export calculation as Excel."""
    result = await db.execute(select(Calculation).where(Calculation.id == calculation_id))
    calc = result.scalar_one_or_none()
    
    if not calc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calculation not found")
    
    # Check access
    if current_user.role != "admin" and calc.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    # Generate Excel
    calc_dict = {
        "id": calc.id,
        "calc_type": calc.calc_type,
        "input_json": calc.input_json,
        "result_json": calc.result_json,
        "cheapest_provider": calc.cheapest_provider,
        "duration_months": calc.duration_months,
        "created_at": calc.created_at.isoformat(),
    }
    
    excel_bytes = await generate_excel(calc_dict, current_user.email)
    
    await log_audit(
        db,
        action="export_excel",
        status="success",
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        input_data={"calculation_id": calculation_id}
    )
    
    filename = f"jade_report_{calculation_id}_{datetime.utcnow().strftime('%Y%m%d')}.xlsx"
    
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
