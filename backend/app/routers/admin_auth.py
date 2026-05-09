from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.middleware.jwt_auth import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.models.admin_user import AdminUser
from app.schemas.admin import LoginRequest, LoginResponse
from app.utils.response import success, error

router = APIRouter(prefix="/api/v1/admin", tags=["管理后台-认证"])


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AdminUser).where(AdminUser.username == req.username))
    admin = result.scalar_one_or_none()

    if not admin:
        return error(1201, "用户名或密码错误")
    if not verify_password(req.password, admin.password_hash):
        return error(1201, "用户名或密码错误")

    token = create_access_token(data={"sub": admin.username})
    return success({"token": token})
