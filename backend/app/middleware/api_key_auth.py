from fastapi import Depends, HTTPException, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.category import Category


async def get_category_by_api_key(
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> Category:
    result = await db.execute(select(Category).where(Category.api_key == x_api_key))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return category
