from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.api_key_auth import get_category_by_api_key
from app.models.category import Category
from app.redis_client import get_redis
from app.schemas.key import (
    ActivateRequest,
    ActivateResponse,
    BalanceRequest,
    BalanceResponse,
    DeductRequest,
    DeductResponse,
)
from app.services.key_service import activate_key, deduct_score, get_balance
from app.utils.response import success, error

router = APIRouter(prefix="/api/v1/keys", tags=["C端接口"])


@router.post("/activate")
async def activate(
    req: ActivateRequest,
    request: Request,
    category: Category = Depends(get_category_by_api_key),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    try:
        client_ip = request.client.host if request.client else None
        result = await activate_key(
            db=db,
            redis_client=redis,
            key_code=req.key_code,
            category=category,
            client_ip=client_ip,
            metadata=req.metadata,
        )
        return success(result)
    except Exception as e:
        code = 1001
        msg = str(e)
        if "已激活" in msg:
            code = 1002
        elif "已过期" in msg:
            code = 1003
        elif "已禁用" in msg:
            code = 1004
        return error(code, msg)


@router.post("/deduct")
async def deduct(
    req: DeductRequest,
    request: Request,
    category: Category = Depends(get_category_by_api_key),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    try:
        client_ip = request.client.host if request.client else None
        result = await deduct_score(
            db=db,
            redis_client=redis,
            key_code=req.key_code,
            amount=req.amount,
            category=category,
            client_ip=client_ip,
            metadata=req.metadata,
        )
        return success(result)
    except Exception as e:
        code = 1101
        msg = str(e)
        if "余额不足" in msg:
            code = 1102
        elif "繁忙" in msg:
            code = 1103
        return error(code, msg)


@router.post("/balance")
async def balance(
    req: BalanceRequest,
    request: Request,
    category: Category = Depends(get_category_by_api_key),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    try:
        client_ip = request.client.host if request.client else None
        result = await get_balance(
            redis_client=redis,
            key_code=req.key_code,
            db=db,
            category=category,
            client_ip=client_ip,
            metadata=req.metadata,
        )
        return success(result)
    except Exception as e:
        return error(1001, str(e))
