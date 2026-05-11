from __future__ import annotations

import csv
import io

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import BatchNotFound
from app.middleware.jwt_auth import get_current_admin
from app.models.admin_user import AdminUser
from app.models.code_batch import CodeBatch
from app.models.product import Product
from app.models.redemption_code import RedemptionCode
from app.schemas.code import (
    BatchSearchRequest,
    BatchItem,
    BatchSearchResponse,
    BatchCodeItem,
    BatchDetailResponse,
)
from app.utils.audit import write_audit
from app.utils.response import success, error

router = APIRouter(prefix="/api/v1/admin/batches", tags=["管理后台-批次"])


@router.post("/search")
async def search_batches(
    req: BatchSearchRequest,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(
            CodeBatch.id,
            CodeBatch.batch_id,
            Product.name.label("product_name"),
            CodeBatch.card_type_name,
            CodeBatch.count,
            CodeBatch.total_score,
            CodeBatch.creator,
            CodeBatch.remark,
            CodeBatch.created_at,
        )
        .join(Product, CodeBatch.category_id == Product.id)
    )

    if req.product_id:
        query = query.where(CodeBatch.category_id == req.product_id)
    if req.batch_id:
        query = query.where(CodeBatch.batch_id.contains(req.batch_id))

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (req.page - 1) * req.page_size
    query = query.order_by(CodeBatch.id.desc()).offset(offset).limit(req.page_size)
    result = await db.execute(query)
    rows = result.all()

    items = [
        BatchItem(
            id=row.id,
            batch_id=row.batch_id,
            product_name=row.product_name,
            card_type_name=row.card_type_name,
            count=row.count,
            total_score=row.total_score,
            creator=row.creator,
            remark=row.remark,
            created_at=row.created_at,
        )
        for row in rows
    ]

    return success(BatchSearchResponse(total=total, page=req.page, page_size=req.page_size, items=items).model_dump())


@router.get("/{batch_id}")
async def get_batch_detail(
    batch_id: str,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    batch_row = await db.execute(
        select(
            CodeBatch.id,
            CodeBatch.batch_id,
            Product.name.label("product_name"),
            CodeBatch.card_type_name,
            CodeBatch.count,
            CodeBatch.total_score,
            CodeBatch.creator,
            CodeBatch.remark,
            CodeBatch.created_at,
        )
        .join(Product, CodeBatch.category_id == Product.id)
        .where(CodeBatch.batch_id == batch_id)
    )
    batch = batch_row.one_or_none()
    if not batch:
        return error(BatchNotFound.code, BatchNotFound.message)

    codes_result = await db.execute(
        select(RedemptionCode)
        .where(RedemptionCode.batch_id == batch_id)
        .order_by(RedemptionCode.id)
    )
    codes = codes_result.scalars().all()

    code_items = [
        BatchCodeItem(
            id=c.id,
            code=c.key_code,
            status=c.status,
            total_score=c.total_score,
            remaining_score=c.remaining_score,
            activated_at=c.activated_at,
            expires_at=c.expires_at,
            created_at=c.created_at,
        )
        for c in codes
    ]

    detail = BatchDetailResponse(
        id=batch.id,
        batch_id=batch.batch_id,
        product_name=batch.product_name,
        card_type_name=batch.card_type_name,
        count=batch.count,
        total_score=batch.total_score,
        creator=batch.creator,
        remark=batch.remark,
        created_at=batch.created_at,
        codes=code_items,
    )

    return success(detail.model_dump())


@router.get("/{batch_id}/export")
async def export_batch(
    batch_id: str,
    status: str | None = None,
    request: Request = None,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    batch_result = await db.execute(
        select(CodeBatch).where(CodeBatch.batch_id == batch_id)
    )
    batch = batch_result.scalar_one_or_none()
    if not batch:
        return error(BatchNotFound.code, BatchNotFound.message)

    query = select(RedemptionCode).where(RedemptionCode.batch_id == batch_id)
    if status:
        query = query.where(RedemptionCode.status == status)
    query = query.order_by(RedemptionCode.id)

    result = await db.execute(query)
    codes = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["code", "status", "total_score", "remaining_score", "expires_at", "created_at"])
    for c in codes:
        writer.writerow([
            c.key_code,
            c.status,
            c.total_score,
            c.remaining_score,
            c.expires_at.isoformat() if c.expires_at else "",
            c.created_at.isoformat() if c.created_at else "",
        ])
    output.seek(0)

    client_ip = request.client.host if request.client else "unknown"
    await write_audit(
        db, admin_id=admin.id, action="export_batch", target_type="batch",
        target_id=batch.id, detail={"batch_id": batch_id, "status_filter": status, "count": len(codes)},
        client_ip=client_ip,
    )

    filename = f"batch_{batch_id}.csv"
    if status:
        filename = f"batch_{batch_id}_{status}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.put("/{batch_id}/disable")
async def disable_batch(
    batch_id: str,
    request: Request,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    batch_result = await db.execute(
        select(CodeBatch).where(CodeBatch.batch_id == batch_id)
    )
    batch = batch_result.scalar_one_or_none()
    if not batch:
        return error(BatchNotFound.code, BatchNotFound.message)

    # Find all activated codes in this batch for cache invalidation
    codes_result = await db.execute(
        select(RedemptionCode).where(
            RedemptionCode.batch_id == batch_id,
            RedemptionCode.status == "activated",
        )
    )
    activated_codes = codes_result.scalars().all()

    # Disable all codes in batch
    all_codes_result = await db.execute(
        select(RedemptionCode).where(RedemptionCode.batch_id == batch_id)
    )
    all_codes = all_codes_result.scalars().all()
    for c in all_codes:
        c.status = "disabled"

    # Invalidate Redis caches for activated codes
    from app.redis_client import redis_client
    for c in activated_codes:
        await redis_client.delete(f"key:{c.key_code}")

    client_ip = request.client.host if request.client else "unknown"
    await write_audit(
        db, admin_id=admin.id, action="disable_batch", target_type="batch",
        target_id=batch.id,
        detail={"batch_id": batch_id, "disabled_count": len(all_codes), "cache_invalidated": len(activated_codes)},
        client_ip=client_ip,
    )

    return success(None)
