from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activation_key import ActivationKey
from app.models.activation_log import ActivationLog
from app.models.category import Category


async def get_overview(db: AsyncSession) -> dict:
    total_result = await db.execute(select(func.count(ActivationKey.id)))
    total_keys = total_result.scalar() or 0

    activated_result = await db.execute(
        select(func.count(ActivationKey.id)).where(ActivationKey.status == "activated")
    )
    activated_keys = activated_result.scalar() or 0

    consumed_result = await db.execute(
        select(func.sum(ActivationLog.amount)).where(ActivationLog.action == "deduct")
    )
    total_score_consumed = consumed_result.scalar() or 0

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_result = await db.execute(
        select(func.count(ActivationLog.id))
        .where(ActivationLog.action == "activate")
        .where(ActivationLog.created_at >= today_start)
    )
    today_activations = today_result.scalar() or 0

    return {
        "total_keys": total_keys,
        "activated_keys": activated_keys,
        "total_score_consumed": total_score_consumed,
        "today_activations": today_activations,
    }


async def get_category_stats(db: AsyncSession, category_id: int) -> dict:
    cat_result = await db.execute(select(Category).where(Category.id == category_id))
    category = cat_result.scalar_one_or_none()
    if not category:
        raise Exception("分类不存在")

    total_result = await db.execute(
        select(func.count(ActivationKey.id)).where(ActivationKey.category_id == category_id)
    )
    total_keys = total_result.scalar() or 0

    activated_result = await db.execute(
        select(func.count(ActivationKey.id))
        .where(ActivationKey.category_id == category_id)
        .where(ActivationKey.status == "activated")
    )
    activated_keys = activated_result.scalar() or 0

    total_score_result = await db.execute(
        select(func.sum(ActivationKey.total_score)).where(ActivationKey.category_id == category_id)
    )
    total_score = total_score_result.scalar() or 0

    consumed_result = await db.execute(
        select(func.sum(ActivationLog.amount))
        .where(ActivationLog.category_id == category_id)
        .where(ActivationLog.action == "deduct")
    )
    consumed_score = consumed_result.scalar() or 0

    # 7-day trend
    trend = []
    for i in range(6, -1, -1):
        day_start = (datetime.now(timezone.utc) - timedelta(days=i)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        day_end = day_start + timedelta(days=1)
        count_result = await db.execute(
            select(func.count(ActivationLog.id))
            .where(ActivationLog.category_id == category_id)
            .where(ActivationLog.action == "activate")
            .where(ActivationLog.created_at >= day_start)
            .where(ActivationLog.created_at < day_end)
        )
        trend.append({"date": day_start.strftime("%Y-%m-%d"), "count": count_result.scalar() or 0})

    return {
        "category_id": category_id,
        "category_name": category.name,
        "total_keys": total_keys,
        "activated_keys": activated_keys,
        "total_score": total_score,
        "consumed_score": consumed_score,
        "activation_trend": trend,
    }
