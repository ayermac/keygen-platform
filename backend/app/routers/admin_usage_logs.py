from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.jwt_auth import get_current_admin
from app.models.redemption_code import RedemptionCode
from app.models.usage_log import UsageLog
from app.models.admin_user import AdminUser
from app.models.product import Product
from app.schemas.code import UsageLogItem, UsageLogSearchRequest, UsageLogSearchResponse
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
            UsageLog.id,
            RedemptionCode.key_code,
            Product.name.label("product_name"),
            UsageLog.action,
            UsageLog.amount,
            UsageLog.remaining_after,
            UsageLog.metadata_.label("metadata"),
            UsageLog.client_ip,
            UsageLog.created_at,
        )
        .join(RedemptionCode, UsageLog.key_id == RedemptionCode.id)
        .join(Product, UsageLog.category_id == Product.id)
    )

    if req.code:
        query = query.where(RedemptionCode.key_code.contains(req.code))
    if req.product_id:
        query = query.where(UsageLog.category_id == req.product_id)
    if req.action:
        query = query.where(UsageLog.action == req.action)
    if req.start_time:
        query = query.where(UsageLog.created_at >= req.start_time)
    if req.end_time:
        query = query.where(UsageLog.created_at <= req.end_time)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (req.page - 1) * req.page_size
    query = query.order_by(UsageLog.id.desc()).offset(offset).limit(req.page_size)
    result = await db.execute(query)
    rows = result.all()

    items = [
        UsageLogItem(
            id=row.id,
            code=row.key_code,
            product_name=row.product_name,
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
