import secrets

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.jwt_auth import get_current_admin
from app.models.admin_user import AdminUser
from app.models.category import Category
from app.schemas.category import (
    CategoryCreate,
    CategoryItem,
    CategoryListResponse,
    CategoryUpdate,
)
from app.utils.response import success, error

router = APIRouter(prefix="/api/v1/admin/categories", tags=["管理后台-分类"])


@router.get("")
async def list_categories(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Category).order_by(Category.id.desc()))
    categories = result.scalars().all()
    items = [CategoryItem.model_validate(c) for c in categories]
    return success({"items": items})


@router.post("")
async def create_category(
    req: CategoryCreate,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(select(Category).where(Category.code == req.code))
    if existing.scalar_one_or_none():
        return error(1301, "分类标识码已存在")

    api_key = f"kg_{secrets.token_hex(32)}"
    category = Category(
        name=req.name,
        code=req.code,
        score_per_key=req.score_per_key,
        score_label=req.score_label,
        max_activations=req.max_activations,
        expiry_days=req.expiry_days,
        api_key=api_key,
    )
    db.add(category)
    await db.flush()
    await db.refresh(category)
    return success(CategoryItem.model_validate(category))


@router.put("/{category_id}")
async def update_category(
    category_id: int,
    req: CategoryUpdate,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        return error(1302, "分类不存在")

    if req.name is not None:
        category.name = req.name
    if req.score_per_key is not None:
        category.score_per_key = req.score_per_key
    if req.score_label is not None:
        category.score_label = req.score_label
    if req.max_activations is not None:
        category.max_activations = req.max_activations
    if req.expiry_days is not None:
        category.expiry_days = req.expiry_days

    await db.flush()
    await db.refresh(category)
    return success(CategoryItem.model_validate(category))


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        return error(1302, "分类不存在")

    # Check if category has activation keys
    from app.models.activation_key import ActivationKey
    key_count = await db.execute(
        select(ActivationKey).where(ActivationKey.category_id == category_id).limit(1)
    )
    if key_count.scalar_one_or_none():
        return error(1303, "该分类下存在激活码，无法删除")

    await db.delete(category)
    return success(None)
