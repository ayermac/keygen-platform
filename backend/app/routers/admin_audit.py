from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.jwt_auth import get_current_admin
from app.models.admin_user import AdminUser
from app.models.audit_log import AuditLog
from app.schemas.admin import AuditLogItem, AuditLogListResponse
from app.utils.response import success

router = APIRouter(prefix="/api/v1/admin/audit-logs", tags=["管理后台-审计日志"])


@router.get("")
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(AuditLog, AdminUser.username.label("admin_username"))
        .join(AdminUser, AuditLog.admin_id == AdminUser.id)
    )

    count_query = select(func.count()).select_from(AuditLog.__table__)
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * page_size
    query = query.order_by(AuditLog.id.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    rows = result.all()

    items = [
        AuditLogItem(
            id=row.AuditLog.id,
            admin_username=row.admin_username,
            action=row.AuditLog.action,
            target_type=row.AuditLog.target_type,
            target_id=row.AuditLog.target_id,
            detail=row.AuditLog.detail,
            created_at=row.AuditLog.created_at.isoformat(),
        )
        for row in rows
    ]

    return success({"total": total, "page": page, "page_size": page_size, "items": items})
