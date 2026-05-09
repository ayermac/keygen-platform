from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activation_key import ActivationKey
from app.models.activation_log import ActivationLog
from app.models.category import Category
from app.utils.key_generator import generate_batch_key_codes


async def activate_key(
    db: AsyncSession,
    redis_client: Any,
    key_code: str,
    category: Category,
    client_ip: str | None,
    metadata: dict | None,
) -> dict:
    result = await db.execute(
        select(ActivationKey).where(ActivationKey.key_code == key_code)
    )
    activation_key = result.scalar_one_or_none()

    if not activation_key:
        raise Exception("激活码不存在")
    if activation_key.category_id != category.id:
        raise Exception("激活码不属于该分类")
    if activation_key.status == "activated":
        raise Exception("激活码已激活")
    if activation_key.status == "disabled":
        raise Exception("激活码已禁用")
    if activation_key.status == "expired":
        raise Exception("激活码已过期")

    now = datetime.now(timezone.utc)
    expires_at = None
    if category.expiry_days:
        expires_at = now + timedelta(days=category.expiry_days)

    activation_key.status = "activated"
    activation_key.activated_at = now
    activation_key.expires_at = expires_at

    log = ActivationLog(
        key_id=activation_key.id,
        category_id=category.id,
        action="activate",
        amount=category.score_per_key,
        remaining_after=category.score_per_key,
        metadata_=metadata,
        client_ip=client_ip,
    )
    db.add(log)

    # Update Redis cache
    cache_data = {
        "status": "activated",
        "total_score": str(category.score_per_key),
        "remaining_score": str(category.score_per_key),
        "expires_at": expires_at.isoformat() if expires_at else "",
        "category_id": str(category.id),
    }
    await redis_client.hset(f"key:{key_code}", mapping=cache_data)
    await redis_client.expire(f"key:{key_code}", 1800)

    return {
        "key_code": key_code,
        "score_label": category.score_label,
        "total_score": category.score_per_key,
        "remaining_score": category.score_per_key,
        "expires_at": expires_at,
    }


async def deduct_score(
    db: AsyncSession,
    redis_client: Any,
    key_code: str,
    amount: int,
    category: Category,
    client_ip: str | None,
    metadata: dict | None,
) -> dict:
    # Check cache first
    cache = await redis_client.hgetall(f"key:{key_code}")

    if not cache:
        result = await db.execute(
            select(ActivationKey).where(ActivationKey.key_code == key_code)
        )
        activation_key = result.scalar_one_or_none()
        if not activation_key:
            raise Exception("激活码不存在")
        if activation_key.status != "activated":
            raise Exception("激活码未激活或已过期")
        cache = {
            "status": activation_key.status,
            "remaining_score": str(activation_key.remaining_score),
            "expires_at": activation_key.expires_at.isoformat() if activation_key.expires_at else "",
        }
        await redis_client.hset(f"key:{key_code}", mapping=cache)
        await redis_client.expire(f"key:{key_code}", 1800)

    if cache.get("expires_at"):
        expires_at = datetime.fromisoformat(cache["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            raise Exception("激活码已过期")

    remaining = int(cache.get("remaining_score", 0))
    if remaining < amount:
        raise Exception("余额不足")

    # Atomic decrement with lock
    lock_key = f"lock:key:{key_code}"
    acquired = await redis_client.set(lock_key, "1", nx=True, ex=5)
    if not acquired:
        raise Exception("系统繁忙，请稍后重试")

    try:
        new_remaining = await redis_client.hincrby(f"key:{key_code}", "remaining_score", -amount)

        # Async write to MySQL
        result = await db.execute(
            select(ActivationKey).where(ActivationKey.key_code == key_code)
        )
        activation_key = result.scalar_one_or_none()
        if activation_key:
            activation_key.remaining_score = new_remaining
            log = ActivationLog(
                key_id=activation_key.id,
                category_id=category.id,
                action="deduct",
                amount=amount,
                remaining_after=new_remaining,
                metadata_=metadata,
                client_ip=client_ip,
            )
            db.add(log)

        return {"remaining_score": new_remaining}
    finally:
        await redis_client.delete(lock_key)


async def get_balance(
    redis_client: Any,
    key_code: str,
    db: AsyncSession,
    category: Category,
    client_ip: str | None,
    metadata: dict | None,
) -> dict:
    cache = await redis_client.hgetall(f"key:{key_code}")

    if not cache:
        result = await db.execute(
            select(ActivationKey).where(ActivationKey.key_code == key_code)
        )
        activation_key = result.scalar_one_or_none()
        if not activation_key:
            raise Exception("激活码不存在")
        if activation_key.category_id != category.id:
            raise Exception("激活码不属于该分类")

        cache = {
            "status": activation_key.status,
            "total_score": str(activation_key.total_score),
            "remaining_score": str(activation_key.remaining_score),
            "expires_at": activation_key.expires_at.isoformat() if activation_key.expires_at else "",
        }
        await redis_client.hset(f"key:{key_code}", mapping=cache)
        await redis_client.expire(f"key:{key_code}", 1800)

        return {
            "key_code": key_code,
            "score_label": category.score_label,
            "total_score": activation_key.total_score,
            "remaining_score": activation_key.remaining_score,
            "status": activation_key.status,
            "expires_at": activation_key.expires_at,
        }

    return {
        "key_code": key_code,
        "score_label": category.score_label,
        "total_score": int(cache.get("total_score", 0)),
        "remaining_score": int(cache.get("remaining_score", 0)),
        "status": cache.get("status", "unknown"),
        "expires_at": cache.get("expires_at") or None,
    }


async def generate_keys(
    db: AsyncSession,
    category: Category,
    count: int,
    batch_id: str | None,
) -> tuple[str, list[str]]:
    if not batch_id:
        batch_id = f"B{int(datetime.now(timezone.utc).timestamp())}"

    codes = generate_batch_key_codes(count)

    for code in codes:
        key = ActivationKey(
            key_code=code,
            category_id=category.id,
            status="unused",
            batch_id=batch_id,
            total_score=category.score_per_key,
            remaining_score=category.score_per_key,
        )
        db.add(key)

    return batch_id, codes
