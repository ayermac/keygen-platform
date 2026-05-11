from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import BizError
from app.middleware.api_key_auth import get_category_by_api_key
from app.models.product import Product
from app.redis_client import get_redis
from app.schemas.code import (
    RedeemRequest,
    BalanceRequest,
    ConsumeRequest,
)
from app.services.code_service import redeem_code, consume_credits, get_balance
from app.utils.response import success, error

router = APIRouter(prefix="/api/v1/codes", tags=["C端接口"])


@router.post("/redeem")
async def redeem(
    req: RedeemRequest,
    request: Request,
    product: Product = Depends(get_category_by_api_key),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    try:
        client_ip = request.client.host if request.client else None
        result = await redeem_code(
            db=db,
            redis_client=redis,
            code=req.code,
            product=product,
            client_ip=client_ip,
            metadata=req.metadata,
        )
        return success(result)
    except BizError as e:
        return error(e.code, e.message)


@router.post("/consume")
async def consume(
    req: ConsumeRequest,
    request: Request,
    product: Product = Depends(get_category_by_api_key),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    try:
        client_ip = request.client.host if request.client else None
        result = await consume_credits(
            db=db,
            redis_client=redis,
            code=req.code,
            amount=req.amount,
            product=product,
            client_ip=client_ip,
            metadata=req.metadata,
            request_id=req.request_id,
        )
        return success(result)
    except BizError as e:
        return error(e.code, e.message)


@router.post("/balance")
async def balance(
    req: BalanceRequest,
    request: Request,
    product: Product = Depends(get_category_by_api_key),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    try:
        client_ip = request.client.host if request.client else None
        result = await get_balance(
            redis_client=redis,
            code=req.code,
            db=db,
            product=product,
            client_ip=client_ip,
            metadata=req.metadata,
        )
        return success(result)
    except BizError as e:
        return error(e.code, e.message)
