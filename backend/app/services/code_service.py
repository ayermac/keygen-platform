from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import (
    CodeNotFound,
    CodeAlreadyRedeemed,
    CodeExpired,
    CodeDisabled,
    ProductMismatch,
    CodeNotActivated,
    InsufficientCredits,
    SystemBusy,
)
from app.models.redemption_code import RedemptionCode
from app.models.usage_log import UsageLog
from app.models.product import Product
from app.utils.key_generator import generate_batch_key_codes


async def redeem_code(
    db: AsyncSession,
    redis_client: Any,
    code: str,
    product: Product,
    client_ip: str | None,
    metadata: dict | None,
) -> dict:
    result = await db.execute(
        select(RedemptionCode).where(RedemptionCode.key_code == code)
    )
    redemption_code = result.scalar_one_or_none()

    if not redemption_code:
        raise CodeNotFound()
    if redemption_code.category_id != product.id:
        raise ProductMismatch()
    if redemption_code.status == "activated":
        raise CodeAlreadyRedeemed()
    if redemption_code.status == "disabled":
        raise CodeDisabled()
    if redemption_code.status == "expired":
        raise CodeExpired()

    now = datetime.now(timezone.utc)
    expires_at = None
    effective_expiry_days = (
        redemption_code.expiry_days
        if redemption_code.expiry_days is not None
        else product.expiry_days
    )
    if effective_expiry_days:
        expires_at = now + timedelta(days=effective_expiry_days)

    redemption_code.status = "activated"
    redemption_code.activated_at = now
    redemption_code.expires_at = expires_at

    log = UsageLog(
        key_id=redemption_code.id,
        category_id=product.id,
        action="activate",
        amount=product.score_per_key,
        remaining_after=product.score_per_key,
        metadata_=metadata,
        client_ip=client_ip,
    )
    db.add(log)

    # Update Redis cache
    cache_data = {
        "status": "activated",
        "total_score": str(product.score_per_key),
        "remaining_score": str(product.score_per_key),
        "expires_at": expires_at.isoformat() if expires_at else "",
        "category_id": str(product.id),
    }
    await redis_client.hset(f"key:{code}", mapping=cache_data)
    await redis_client.expire(f"key:{code}", 1800)

    return {
        "code": code,
        "credit_unit": product.score_label,
        "total_credits": product.score_per_key,
        "remaining_credits": product.score_per_key,
        "expires_at": expires_at,
    }


# Lua script for atomic check-and-decrement in Redis
CONSUME_LUA = """
local key = KEYS[1]
local amount = tonumber(ARGV[1])
local remaining = tonumber(redis.call('HGET', key, 'remaining_score') or '-1')
if remaining < 0 then
    return -1
end
if remaining < amount then
    return -2
end
redis.call('HINCRBY', key, 'remaining_score', -amount)
return remaining - amount
"""


async def consume_credits(
    db: AsyncSession,
    redis_client: Any,
    code: str,
    amount: int,
    product: Product,
    client_ip: str | None,
    metadata: dict | None,
    request_id: str | None = None,
) -> dict:
    # ── Resolve code first (needed for idempotency scope + validation) ──
    result = await db.execute(
        select(RedemptionCode).where(RedemptionCode.key_code == code)
    )
    redemption_code = result.scalar_one_or_none()
    if not redemption_code:
        raise CodeNotFound()
    if redemption_code.category_id != product.id:
        raise ProductMismatch()

    key_id = redemption_code.id

    # ── Idempotency check: product + code + request_id + action ──
    if request_id:
        existing = await db.execute(
            select(UsageLog).where(
                UsageLog.category_id == product.id,
                UsageLog.key_id == key_id,
                UsageLog.action == "deduct",
                UsageLog.request_id == request_id,
            )
        )
        prior_log = existing.scalar_one_or_none()
        if prior_log:
            return {"remaining_credits": prior_log.remaining_after}

    # ── Check cache ──
    cache = await redis_client.hgetall(f"key:{code}")

    if not cache:
        if redemption_code.status != "activated":
            raise CodeNotActivated()
        cache = {
            "status": redemption_code.status,
            "remaining_score": str(redemption_code.remaining_score),
            "expires_at": (
                redemption_code.expires_at.isoformat()
                if redemption_code.expires_at
                else ""
            ),
        }
        await redis_client.hset(f"key:{code}", mapping=cache)
        await redis_client.expire(f"key:{code}", 1800)

    if cache.get("expires_at"):
        expires_at = datetime.fromisoformat(cache["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            raise CodeExpired()

    # ── Acquire locks: idempotency lock (if request_id) + consume lock ──
    idem_key = f"idem:consume:{product.id}:{code}:{request_id}" if request_id else None
    lock_key = f"lock:key:{code}"

    if idem_key:
        idem_acquired = await redis_client.set(idem_key, "1", nx=True, ex=30)
        if not idem_acquired:
            # Another request with same request_id is in progress; check for result
            existing = await db.execute(
                select(UsageLog).where(
                    UsageLog.category_id == product.id,
                    UsageLog.key_id == key_id,
                    UsageLog.action == "deduct",
                    UsageLog.request_id == request_id,
                )
            )
            prior_log = existing.scalar_one_or_none()
            if prior_log:
                return {"remaining_credits": prior_log.remaining_after}
            raise SystemBusy()

    acquired = await redis_client.set(lock_key, "1", nx=True, ex=5)
    if not acquired:
        if idem_key:
            await redis_client.delete(idem_key)
        raise SystemBusy()

    try:
        new_remaining = await redis_client.eval(
            CONSUME_LUA, 1, f"key:{code}", amount
        )
        if new_remaining == -1:
            raise CodeNotFound()
        if new_remaining == -2:
            raise InsufficientCredits()

        # Write to MySQL
        redemption_code.remaining_score = new_remaining
        log = UsageLog(
            key_id=key_id,
            category_id=product.id,
            action="deduct",
            amount=amount,
            remaining_after=new_remaining,
            metadata_=metadata,
            client_ip=client_ip,
            request_id=request_id,
        )
        db.add(log)

        return {"remaining_credits": new_remaining}
    finally:
        await redis_client.delete(lock_key)
        if idem_key:
            await redis_client.delete(idem_key)


async def get_balance(
    redis_client: Any,
    code: str,
    db: AsyncSession,
    product: Product,
    client_ip: str | None,
    metadata: dict | None,
) -> dict:
    cache = await redis_client.hgetall(f"key:{code}")

    if not cache:
        result = await db.execute(
            select(RedemptionCode).where(RedemptionCode.key_code == code)
        )
        redemption_code = result.scalar_one_or_none()
        if not redemption_code:
            raise CodeNotFound()
        if redemption_code.category_id != product.id:
            raise ProductMismatch()

        cache = {
            "status": redemption_code.status,
            "total_score": str(redemption_code.total_score),
            "remaining_score": str(redemption_code.remaining_score),
            "expires_at": (
                redemption_code.expires_at.isoformat()
                if redemption_code.expires_at
                else ""
            ),
        }
        await redis_client.hset(f"key:{code}", mapping=cache)
        await redis_client.expire(f"key:{code}", 1800)

        return {
            "code": code,
            "credit_unit": product.score_label,
            "total_credits": redemption_code.total_score,
            "remaining_credits": redemption_code.remaining_score,
            "status": redemption_code.status,
            "expires_at": redemption_code.expires_at,
        }

    return {
        "code": code,
        "credit_unit": product.score_label,
        "total_credits": int(cache.get("total_score", 0)),
        "remaining_credits": int(cache.get("remaining_score", 0)),
        "status": cache.get("status", "unknown"),
        "expires_at": cache.get("expires_at") or None,
    }


async def generate_codes(
    db: AsyncSession,
    product: Product,
    count: int,
    batch_id: str | None,
    card_type: str | None = None,
) -> tuple[str, list[str]]:
    if not batch_id:
        batch_id = f"B{int(datetime.now(timezone.utc).timestamp())}"

    # Resolve card type values
    total_score = product.score_per_key
    expiry_days = product.expiry_days
    card_type_name = None

    if card_type and product.card_types:
        for ct in product.card_types:
            if ct.get("name") == card_type:
                total_score = ct["total_score"]
                expiry_days = ct.get("expiry_days")
                card_type_name = card_type
                break

    codes = generate_batch_key_codes(count)

    for code in codes:
        key = RedemptionCode(
            key_code=code,
            category_id=product.id,
            status="unused",
            batch_id=batch_id,
            card_type_name=card_type_name,
            total_score=total_score,
            remaining_score=total_score,
            expiry_days=expiry_days,
        )
        db.add(key)

    return batch_id, codes
