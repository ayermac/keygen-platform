from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.redemption_code import RedemptionCode
from app.models.usage_log import UsageLog
from app.models.product import Product


async def get_overview(db: AsyncSession) -> dict:
    total_result = await db.execute(select(func.count(RedemptionCode.id)))
    total_codes = total_result.scalar() or 0

    activated_result = await db.execute(
        select(func.count(RedemptionCode.id)).where(RedemptionCode.status == "activated")
    )
    activated_codes = activated_result.scalar() or 0

    consumed_result = await db.execute(
        select(func.sum(UsageLog.amount)).where(UsageLog.action == "deduct")
    )
    total_credits_consumed = consumed_result.scalar() or 0

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_result = await db.execute(
        select(func.count(UsageLog.id))
        .where(UsageLog.action == "activate")
        .where(UsageLog.created_at >= today_start)
    )
    today_redemptions = today_result.scalar() or 0

    return {
        "total_codes": total_codes,
        "activated_codes": activated_codes,
        "total_credits_consumed": total_credits_consumed,
        "today_redemptions": today_redemptions,
    }


async def get_product_stats(db: AsyncSession, product_id: int) -> dict:
    prod_result = await db.execute(select(Product).where(Product.id == product_id))
    product = prod_result.scalar_one_or_none()
    if not product:
        raise Exception("产品不存在")

    total_result = await db.execute(
        select(func.count(RedemptionCode.id)).where(RedemptionCode.category_id == product_id)
    )
    total_codes = total_result.scalar() or 0

    activated_result = await db.execute(
        select(func.count(RedemptionCode.id))
        .where(RedemptionCode.category_id == product_id)
        .where(RedemptionCode.status == "activated")
    )
    activated_codes = activated_result.scalar() or 0

    total_credits_result = await db.execute(
        select(func.sum(RedemptionCode.total_score)).where(RedemptionCode.category_id == product_id)
    )
    total_credits = total_credits_result.scalar() or 0

    consumed_result = await db.execute(
        select(func.sum(UsageLog.amount))
        .where(UsageLog.category_id == product_id)
        .where(UsageLog.action == "deduct")
    )
    consumed_credits = consumed_result.scalar() or 0

    # 7-day trend
    trend = []
    for i in range(6, -1, -1):
        day_start = (datetime.now(timezone.utc) - timedelta(days=i)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        day_end = day_start + timedelta(days=1)
        count_result = await db.execute(
            select(func.count(UsageLog.id))
            .where(UsageLog.category_id == product_id)
            .where(UsageLog.action == "activate")
            .where(UsageLog.created_at >= day_start)
            .where(UsageLog.created_at < day_end)
        )
        trend.append({"date": day_start.strftime("%Y-%m-%d"), "count": count_result.scalar() or 0})

    return {
        "product_id": product_id,
        "product_name": product.name,
        "total_codes": total_codes,
        "activated_codes": activated_codes,
        "total_credits": total_credits,
        "consumed_credits": consumed_credits,
        "redemption_trend": trend,
    }
