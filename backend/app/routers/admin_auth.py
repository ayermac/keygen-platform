from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import LoginFailed, SystemBusy
from app.middleware.jwt_auth import (
    create_access_token,
    verify_password,
)
from app.models.admin_user import AdminUser
from app.redis_client import redis_client
from app.schemas.admin import LoginRequest
from app.utils.audit import write_audit
from app.utils.response import success, error

router = APIRouter(prefix="/api/v1/admin", tags=["管理后台-认证"])
logger = logging.getLogger("keygen.auth")

LOGIN_RATE_LIMIT = 5       # max attempts
LOGIN_RATE_WINDOW = 60     # per seconds


@router.post("/login")
async def login(req: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    rate_key = f"login_attempts:{client_ip}"

    # Rate limit check
    attempts = await redis_client.incr(rate_key)
    if attempts == 1:
        await redis_client.expire(rate_key, LOGIN_RATE_WINDOW)
    if attempts > LOGIN_RATE_LIMIT:
        logger.warning("login rate_limit_exceeded ip=%s", client_ip)
        raise SystemBusy()

    result = await db.execute(select(AdminUser).where(AdminUser.username == req.username))
    admin = result.scalar_one_or_none()

    if not admin or not verify_password(req.password, admin.password_hash):
        logger.warning("login failed username=%s ip=%s", req.username, client_ip)
        raise LoginFailed()

    # Clear rate limit on success
    await redis_client.delete(rate_key)

    token = create_access_token(data={"sub": admin.username})

    await write_audit(db, admin_id=admin.id, action="login", target_type="admin", target_id=admin.id, detail={"ip": client_ip}, client_ip=client_ip)
    await db.flush()

    return success({"token": token})
