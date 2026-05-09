from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.jwt_auth import get_current_admin
from app.models.activation_key import ActivationKey
from app.models.activation_log import ActivationLog
from app.models.admin_user import AdminUser
from app.models.category import Category
from app.schemas.key import (
    KeyGenerateRequest,
    KeyGenerateResponse,
    KeyItem,
    KeySearchRequest,
    KeySearchResponse,
)
from app.services.key_service import generate_keys
from app.utils.response import success, error

router = APIRouter(prefix="/api/v1/admin/keys", tags=["管理后台-激活码"])


@router.post("/generate")
async def generate(
    req: KeyGenerateRequest,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Category).where(Category.id == req.category_id))
    category = result.scalar_one_or_none()
    if not category:
        return error(1302, "分类不存在")

    if req.count < 1 or req.count > 10000:
        return error(1401, "生成数量需在 1-10000 之间")

    batch_id, codes = await generate_keys(db, category, req.count, req.batch_id)
    return success({"batch_id": batch_id, "count": len(codes), "keys": codes})


@router.post("/search")
async def search_keys(
    req: KeySearchRequest,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(
        ActivationKey.id,
        ActivationKey.key_code,
        Category.name.label("category_name"),
        ActivationKey.status,
        ActivationKey.total_score,
        ActivationKey.remaining_score,
        ActivationKey.batch_id,
        ActivationKey.activated_at,
        ActivationKey.expires_at,
        ActivationKey.created_at,
    ).join(Category, ActivationKey.category_id == Category.id)

    if req.category_id:
        query = query.where(ActivationKey.category_id == req.category_id)
    if req.status:
        query = query.where(ActivationKey.status == req.status)
    if req.batch_id:
        query = query.where(ActivationKey.batch_id == req.batch_id)
    if req.key_code:
        query = query.where(ActivationKey.key_code.contains(req.key_code))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    offset = (req.page - 1) * req.page_size
    query = query.order_by(ActivationKey.id.desc()).offset(offset).limit(req.page_size)
    result = await db.execute(query)
    rows = result.all()

    items = [
        KeyItem(
            id=row.id,
            key_code=row.key_code,
            category_name=row.category_name,
            status=row.status,
            total_score=row.total_score,
            remaining_score=row.remaining_score,
            batch_id=row.batch_id,
            activated_at=row.activated_at,
            expires_at=row.expires_at,
            created_at=row.created_at,
        )
        for row in rows
    ]

    return success({"total": total, "page": req.page, "page_size": req.page_size, "items": items})


@router.put("/{key_id}/disable")
async def disable_key(
    key_id: int,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ActivationKey).where(ActivationKey.id == key_id))
    key = result.scalar_one_or_none()
    if not key:
        return error(1001, "激活码不存在")

    key.status = "disabled"
    return success(None)
