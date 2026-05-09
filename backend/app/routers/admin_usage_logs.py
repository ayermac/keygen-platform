from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.jwt_auth import get_current_admin
from app.models.activation_key import ActivationKey
from app.models.activation_log import ActivationLog
from app.models.admin_user import AdminUser
from app.models.category import Category
from app.schemas.key import UsageLogItem, UsageLogSearchRequest, UsageLogSearchResponse
from app.utils.response import success

router = APIRouter(prefix="/api/v1/admin/usage-logs", tags=["管理后台-使用日志"])


@router.post("/search")
async def search_usage_logs(
    req: UsageLogSearchRequest,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(
            ActivationLog.id,
            ActivationKey.key_code,
            Category.name.label("category_name"),
            ActivationLog.action,
            ActivationLog.amount,
            ActivationLog.remaining_after,
            ActivationLog.metadata_.label("metadata"),
            ActivationLog.client_ip,
            ActivationLog.created_at,
        )
        .join(ActivationKey, ActivationLog.key_id == ActivationKey.id)
        .join(Category, ActivationLog.category_id == Category.id)
    )

    if req.key_code:
        query = query.where(ActivationKey.key_code.contains(req.key_code))
    if req.category_id:
        query = query.where(ActivationLog.category_id == req.category_id)
    if req.action:
        query = query.where(ActivationLog.action == req.action)
    if req.start_time:
        query = query.where(ActivationLog.created_at >= req.start_time)
    if req.end_time:
        query = query.where(ActivationLog.created_at <= req.end_time)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (req.page - 1) * req.page_size
    query = query.order_by(ActivationLog.id.desc()).offset(offset).limit(req.page_size)
    result = await db.execute(query)
    rows = result.all()

    items = [
        UsageLogItem(
            id=row.id,
            key_code=row.key_code,
            category_name=row.category_name,
            action=row.action,
            amount=row.amount,
            remaining_after=row.remaining_after,
            metadata=row.metadata,
            client_ip=row.client_ip,
            created_at=row.created_at,
        )
        for row in rows
    ]

    return success({"total": total, "page": req.page, "page_size": req.page_size, "items": items})
