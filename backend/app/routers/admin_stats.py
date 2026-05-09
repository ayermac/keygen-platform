from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.jwt_auth import get_current_admin
from app.models.admin_user import AdminUser
from app.services.stats_service import get_overview, get_category_stats
from app.utils.response import success, error

router = APIRouter(prefix="/api/v1/admin/stats", tags=["管理后台-统计"])


@router.get("")
async def overview(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await get_overview(db)
    return success(result)


@router.get("/category/{category_id}")
async def category_stats(
    category_id: int,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await get_category_stats(db, category_id)
        return success(result)
    except Exception as e:
        return error(1302, str(e))
