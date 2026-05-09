from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.jwt_auth import get_current_admin
from app.models.redemption_code import RedemptionCode
from app.models.usage_log import UsageLog
from app.models.admin_user import AdminUser
from app.models.product import Product
from app.schemas.code import (
    CodeGenerateRequest,
    CodeGenerateResponse,
    CodeItem,
    CodeSearchRequest,
    CodeSearchResponse,
)
from app.services.code_service import generate_codes
from app.utils.response import success, error

router = APIRouter(prefix="/api/v1/admin/codes", tags=["管理后台-兑换码"])


@router.post("/generate")
async def generate(
    req: CodeGenerateRequest,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Product).where(Product.id == req.product_id))
    product = result.scalar_one_or_none()
    if not product:
        return error(1302, "产品不存在")

    if req.count < 1 or req.count > 10000:
        return error(1401, "生成数量需在 1-10000 之间")

    batch_id, codes = await generate_codes(db, product, req.count, req.batch_id, req.card_type)
    return success({"batch_id": batch_id, "count": len(codes), "codes": codes})


@router.post("/search")
async def search_codes(
    req: CodeSearchRequest,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(
        RedemptionCode.id,
        RedemptionCode.key_code,
        Product.name.label("product_name"),
        RedemptionCode.status,
        RedemptionCode.total_score,
        RedemptionCode.remaining_score,
        RedemptionCode.batch_id,
        RedemptionCode.activated_at,
        RedemptionCode.expires_at,
        RedemptionCode.created_at,
    ).join(Product, RedemptionCode.category_id == Product.id)

    if req.product_id:
        query = query.where(RedemptionCode.category_id == req.product_id)
    if req.status:
        query = query.where(RedemptionCode.status == req.status)
    if req.batch_id:
        query = query.where(RedemptionCode.batch_id == req.batch_id)
    if req.code:
        query = query.where(RedemptionCode.key_code.contains(req.code))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    offset = (req.page - 1) * req.page_size
    query = query.order_by(RedemptionCode.id.desc()).offset(offset).limit(req.page_size)
    result = await db.execute(query)
    rows = result.all()

    items = [
        CodeItem(
            id=row.id,
            code=row.key_code,
            product_name=row.product_name,
            status=row.status,
            total_credits=row.total_score,
            remaining_credits=row.remaining_score,
            batch_id=row.batch_id,
            activated_at=row.activated_at,
            expires_at=row.expires_at,
            created_at=row.created_at,
        )
        for row in rows
    ]

    return success({"total": total, "page": req.page, "page_size": req.page_size, "items": items})


@router.put("/{code_id}/disable")
async def disable_code(
    code_id: int,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(RedemptionCode).where(RedemptionCode.id == code_id))
    code = result.scalar_one_or_none()
    if not code:
        return error(1001, "兑换码不存在")

    code.status = "disabled"
    return success(None)
