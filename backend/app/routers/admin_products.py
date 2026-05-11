from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import ProductCodeExists, ProductNotFound, ProductHasCodes
from app.middleware.jwt_auth import get_current_admin
from app.models.admin_user import AdminUser
from app.models.product import Product
from app.schemas.product import (
    ProductCreate,
    ProductItem,
    ProductUpdate,
)
from app.utils.audit import write_audit
from app.utils.response import success, error

router = APIRouter(prefix="/api/v1/admin/products", tags=["管理后台-产品"])


@router.get("")
async def list_products(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Product).order_by(Product.id.desc()))
    products = result.scalars().all()
    items = []
    for p in products:
        items.append(ProductItem(
            id=p.id,
            name=p.name,
            code=p.code,
            default_credits=p.score_per_key,
            credit_unit=p.score_label,
            max_activations=p.max_activations,
            expiry_days=p.expiry_days,
            api_key=p.api_key[:10] + "..." if len(p.api_key) > 10 else p.api_key,
            card_types=p.card_types,
            created_at=p.created_at,
        ))
    return success({"items": items})


@router.post("")
async def create_product(
    req: ProductCreate,
    request: Request,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(select(Product).where(Product.code == req.code))
    if existing.scalar_one_or_none():
        return error(ProductCodeExists.code, ProductCodeExists.message)

    api_key = f"kg_{secrets.token_hex(32)}"
    product = Product(
        name=req.name,
        code=req.code,
        score_per_key=req.default_credits,
        score_label=req.credit_unit,
        max_activations=req.max_activations,
        expiry_days=req.expiry_days,
        api_key=api_key,
        card_types=[ct.model_dump() for ct in req.card_types] if req.card_types else None,
    )
    db.add(product)
    await db.flush()
    await db.refresh(product)

    client_ip = request.client.host if request.client else "unknown"
    await write_audit(db, admin_id=admin.id, action="create", target_type="product", target_id=product.id, detail={"name": product.name, "code": product.code}, client_ip=client_ip)

    return success(ProductItem(
        id=product.id,
        name=product.name,
        code=product.code,
        default_credits=product.score_per_key,
        credit_unit=product.score_label,
        max_activations=product.max_activations,
        expiry_days=product.expiry_days,
        api_key=product.api_key,
        card_types=product.card_types,
        created_at=product.created_at,
    ))


@router.put("/{product_id}")
async def update_product(
    product_id: int,
    req: ProductUpdate,
    request: Request,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        return error(ProductNotFound.code, ProductNotFound.message)

    if req.name is not None:
        product.name = req.name
    if req.default_credits is not None:
        product.score_per_key = req.default_credits
    if req.credit_unit is not None:
        product.score_label = req.credit_unit
    if req.max_activations is not None:
        product.max_activations = req.max_activations
    if req.expiry_days is not None:
        product.expiry_days = req.expiry_days
    if req.card_types is not None:
        product.card_types = [ct.model_dump() for ct in req.card_types]

    await db.flush()
    await db.refresh(product)

    client_ip = request.client.host if request.client else "unknown"
    await write_audit(db, admin_id=admin.id, action="update", target_type="product", target_id=product.id, detail={"name": product.name}, client_ip=client_ip)

    return success(ProductItem(
        id=product.id,
        name=product.name,
        code=product.code,
        default_credits=product.score_per_key,
        credit_unit=product.score_label,
        max_activations=product.max_activations,
        expiry_days=product.expiry_days,
        api_key=product.api_key[:10] + "..." if len(product.api_key) > 10 else product.api_key,
        card_types=product.card_types,
        created_at=product.created_at,
    ))


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    request: Request,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        return error(ProductNotFound.code, ProductNotFound.message)

    from app.models.redemption_code import RedemptionCode
    code_count = await db.execute(
        select(RedemptionCode).where(RedemptionCode.category_id == product_id).limit(1)
    )
    if code_count.scalar_one_or_none():
        return error(ProductHasCodes.code, ProductHasCodes.message)

    client_ip = request.client.host if request.client else "unknown"
    await write_audit(db, admin_id=admin.id, action="delete", target_type="product", target_id=product.id, detail={"name": product.name}, client_ip=client_ip)
    await db.delete(product)
    return success(None)


@router.post("/{product_id}/rotate-key")
async def rotate_api_key(
    product_id: int,
    request: Request,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        return error(ProductNotFound.code, ProductNotFound.message)

    old_key = product.api_key
    new_key = f"kg_{secrets.token_hex(32)}"
    product.api_key = new_key

    # Invalidate Redis caches for activated codes of this product
    from app.redis_client import redis_client
    from app.models.redemption_code import RedemptionCode
    codes_result = await db.execute(
        select(RedemptionCode.key_code).where(
            RedemptionCode.category_id == product_id,
            RedemptionCode.status == "activated",
        )
    )
    for row in codes_result.scalars().all():
        await redis_client.delete(f"key:{row}")

    await db.flush()
    await db.refresh(product)

    client_ip = request.client.host if request.client else "unknown"
    await write_audit(db, admin_id=admin.id, action="rotate_key", target_type="product", target_id=product.id, detail={"old_key_prefix": old_key[:10] + "..."}, client_ip=client_ip)

    return success({
        "api_key": new_key,
        "old_key_prefix": old_key[:10] + "...",
    })
