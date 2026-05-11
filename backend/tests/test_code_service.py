from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.code_service import redeem_code, consume_credits, get_balance, generate_codes
from app.models.usage_log import UsageLog
from app.models.redemption_code import RedemptionCode
from app.exceptions import (
    CodeNotFound,
    CodeAlreadyRedeemed,
    CodeExpired,
    CodeDisabled,
    ProductMismatch,
    InsufficientCredits,
    SystemBusy,
    CodeNotActivated,
)


# ── redeem_code tests ──

@pytest.mark.asyncio
async def test_redeem_success(mock_db, mock_redis, mock_product, mock_redemption_code):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_redemption_code
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await redeem_code(
        db=mock_db, redis_client=mock_redis, code="A1B2-C3D4-E5F6-G7H8",
        product=mock_product, client_ip="127.0.0.1", metadata=None,
    )

    assert result["code"] == "A1B2-C3D4-E5F6-G7H8"
    assert result["total_credits"] == 100
    assert result["remaining_credits"] == 100
    assert mock_redemption_code.status == "activated"
    mock_redis.hset.assert_called_once()
    mock_db.add.assert_called_once()


@pytest.mark.asyncio
async def test_redeem_not_found(mock_db, mock_redis, mock_product):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(CodeNotFound):
        await redeem_code(
            db=mock_db, redis_client=mock_redis, code="XXXX-XXXX-XXXX-XXXX",
            product=mock_product, client_ip=None, metadata=None,
        )


@pytest.mark.asyncio
async def test_redeem_already_redeemed(mock_db, mock_redis, mock_product, mock_redemption_code):
    mock_redemption_code.status = "activated"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_redemption_code
    mock_db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(CodeAlreadyRedeemed):
        await redeem_code(
            db=mock_db, redis_client=mock_redis, code="A1B2-C3D4-E5F6-G7H8",
            product=mock_product, client_ip=None, metadata=None,
        )


@pytest.mark.asyncio
async def test_redeem_disabled(mock_db, mock_redis, mock_product, mock_redemption_code):
    mock_redemption_code.status = "disabled"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_redemption_code
    mock_db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(CodeDisabled):
        await redeem_code(
            db=mock_db, redis_client=mock_redis, code="A1B2-C3D4-E5F6-G7H8",
            product=mock_product, client_ip=None, metadata=None,
        )


@pytest.mark.asyncio
async def test_redeem_expired(mock_db, mock_redis, mock_product, mock_redemption_code):
    mock_redemption_code.status = "expired"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_redemption_code
    mock_db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(CodeExpired):
        await redeem_code(
            db=mock_db, redis_client=mock_redis, code="A1B2-C3D4-E5F6-G7H8",
            product=mock_product, client_ip=None, metadata=None,
        )


@pytest.mark.asyncio
async def test_redeem_product_mismatch(mock_db, mock_redis, mock_product, mock_redemption_code):
    mock_redemption_code.category_id = 999
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_redemption_code
    mock_db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(ProductMismatch):
        await redeem_code(
            db=mock_db, redis_client=mock_redis, code="A1B2-C3D4-E5F6-G7H8",
            product=mock_product, client_ip=None, metadata=None,
        )


@pytest.mark.asyncio
async def test_redeem_with_expiry(mock_db, mock_redis, mock_product, mock_redemption_code):
    mock_product.expiry_days = 30
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_redemption_code
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await redeem_code(
        db=mock_db, redis_client=mock_redis, code="A1B2-C3D4-E5F6-G7H8",
        product=mock_product, client_ip=None, metadata=None,
    )

    assert result["expires_at"] is not None
    assert mock_redemption_code.expires_at is not None


# ── consume_credits tests ──

def _mock_code_resolve(mock_db, redemption_code):
    """Set up mock_db.execute to return a code resolution result."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = redemption_code
    mock_db.execute = AsyncMock(return_value=mock_result)

@pytest.mark.asyncio
async def test_consume_success(mock_db, mock_redis, mock_product, mock_redemption_code):
    mock_redis.hgetall = AsyncMock(return_value={
        "status": "activated", "remaining_score": "100", "expires_at": "",
    })
    mock_redis.eval = AsyncMock(return_value=90)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_redemption_code
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await consume_credits(
        db=mock_db, redis_client=mock_redis, code="A1B2-C3D4-E5F6-G7H8",
        amount=10, product=mock_product, client_ip=None, metadata=None,
    )

    assert result["remaining_credits"] == 90
    mock_redis.eval.assert_called_once()
    mock_db.add.assert_called_once()


@pytest.mark.asyncio
async def test_consume_insufficient(mock_db, mock_redis, mock_product, mock_redemption_code):
    _mock_code_resolve(mock_db, mock_redemption_code)
    mock_redis.hgetall = AsyncMock(return_value={
        "status": "activated", "remaining_score": "5", "expires_at": "",
    })
    mock_redis.eval = AsyncMock(return_value=-2)

    with pytest.raises(InsufficientCredits):
        await consume_credits(
            db=mock_db, redis_client=mock_redis, code="A1B2-C3D4-E5F6-G7H8",
            amount=10, product=mock_product, client_ip=None, metadata=None,
        )


@pytest.mark.asyncio
async def test_consume_system_busy(mock_db, mock_redis, mock_product, mock_redemption_code):
    _mock_code_resolve(mock_db, mock_redemption_code)
    mock_redis.hgetall = AsyncMock(return_value={
        "status": "activated", "remaining_score": "100", "expires_at": "",
    })
    mock_redis.set = AsyncMock(return_value=None)

    with pytest.raises(SystemBusy):
        await consume_credits(
            db=mock_db, redis_client=mock_redis, code="A1B2-C3D4-E5F6-G7H8",
            amount=10, product=mock_product, client_ip=None, metadata=None,
        )


@pytest.mark.asyncio
async def test_consume_expired_code(mock_db, mock_redis, mock_product, mock_redemption_code):
    _mock_code_resolve(mock_db, mock_redemption_code)
    mock_redis.hgetall = AsyncMock(return_value={
        "status": "activated", "remaining_score": "100", "expires_at": "2020-01-01T00:00:00+00:00",
    })

    with pytest.raises(CodeExpired):
        await consume_credits(
            db=mock_db, redis_client=mock_redis, code="A1B2-C3D4-E5F6-G7H8",
            amount=10, product=mock_product, client_ip=None, metadata=None,
        )


@pytest.mark.asyncio
async def test_consume_cache_miss_rebuilds(mock_db, mock_redis, mock_product, mock_redemption_code):
    mock_redemption_code.status = "activated"
    mock_redis.hgetall = AsyncMock(return_value={})
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_redemption_code
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_redis.eval = AsyncMock(return_value=90)

    result = await consume_credits(
        db=mock_db, redis_client=mock_redis, code="A1B2-C3D4-E5F6-G7H8",
        amount=10, product=mock_product, client_ip=None, metadata=None,
    )

    mock_redis.hset.assert_called()
    assert result["remaining_credits"] == 90


@pytest.mark.asyncio
async def test_consume_not_found(mock_db, mock_redis, mock_product):
    mock_redis.hgetall = AsyncMock(return_value={})
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(CodeNotFound):
        await consume_credits(
            db=mock_db, redis_client=mock_redis, code="XXXX-XXXX-XXXX-XXXX",
            amount=10, product=mock_product, client_ip=None, metadata=None,
        )


@pytest.mark.asyncio
async def test_consume_not_activated(mock_db, mock_redis, mock_product, mock_redemption_code):
    mock_redis.hgetall = AsyncMock(return_value={})
    mock_redemption_code.status = "unused"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_redemption_code
    mock_db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(CodeNotActivated):
        await consume_credits(
            db=mock_db, redis_client=mock_redis, code="A1B2-C3D4-E5F6-G7H8",
            amount=10, product=mock_product, client_ip=None, metadata=None,
        )


# ── get_balance tests ──

@pytest.mark.asyncio
async def test_balance_from_cache(mock_db, mock_redis, mock_product):
    mock_redis.hgetall = AsyncMock(return_value={
        "status": "activated", "total_score": "100", "remaining_score": "70",
        "expires_at": "2026-06-01T00:00:00+00:00",
    })

    result = await get_balance(
        redis_client=mock_redis, code="A1B2-C3D4-E5F6-G7H8",
        db=mock_db, product=mock_product, client_ip=None, metadata=None,
    )

    assert result["total_credits"] == 100
    assert result["remaining_credits"] == 70
    assert result["status"] == "activated"


@pytest.mark.asyncio
async def test_balance_from_db(mock_db, mock_redis, mock_product, mock_redemption_code):
    mock_redis.hgetall = AsyncMock(return_value={})
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_redemption_code
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await get_balance(
        redis_client=mock_redis, code="A1B2-C3D4-E5F6-G7H8",
        db=mock_db, product=mock_product, client_ip=None, metadata=None,
    )

    assert result["total_credits"] == 100
    mock_redis.hset.assert_called()


@pytest.mark.asyncio
async def test_balance_not_found(mock_db, mock_redis, mock_product):
    mock_redis.hgetall = AsyncMock(return_value={})
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(CodeNotFound):
        await get_balance(
            redis_client=mock_redis, code="XXXX-XXXX-XXXX-XXXX",
            db=mock_db, product=mock_product, client_ip=None, metadata=None,
        )


@pytest.mark.asyncio
async def test_balance_product_mismatch(mock_db, mock_redis, mock_product, mock_redemption_code):
    mock_redis.hgetall = AsyncMock(return_value={})
    mock_redemption_code.category_id = 999
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_redemption_code
    mock_db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(ProductMismatch):
        await get_balance(
            redis_client=mock_redis, code="A1B2-C3D4-E5F6-G7H8",
            db=mock_db, product=mock_product, client_ip=None, metadata=None,
        )


# ── generate_codes tests ──

@pytest.mark.asyncio
async def test_generate_codes(mock_db, mock_product):
    batch_id, codes = await generate_codes(
        db=mock_db, product=mock_product, count=5, batch_id="B001",
    )

    assert batch_id == "B001"
    assert len(codes) == 5
    assert mock_db.add.call_count == 5


@pytest.mark.asyncio
async def test_generate_codes_auto_batch(mock_db, mock_product):
    batch_id, codes = await generate_codes(
        db=mock_db, product=mock_product, count=3, batch_id=None,
    )

    assert batch_id.startswith("B")
    assert len(codes) == 3


@pytest.mark.asyncio
async def test_generate_codes_with_card_type(mock_db, mock_product):
    mock_product.card_types = [
        {"name": "月卡", "total_score": 200, "expiry_days": 30},
        {"name": "年卡", "total_score": 2400, "expiry_days": 365},
    ]

    batch_id, codes = await generate_codes(
        db=mock_db, product=mock_product, count=2, batch_id="B002", card_type="月卡",
    )

    assert len(codes) == 2
    first_call = mock_db.add.call_args_list[0][0][0]
    assert first_call.total_score == 200
    assert first_call.expiry_days == 30
    assert first_call.card_type_name == "月卡"


# ── Idempotent consume tests (request_id) ──
# Flow: 1st db.execute = code resolution, 2nd db.execute = idempotency check

def _make_prior_log(remaining: int) -> MagicMock:
    """Create a mock UsageLog row for idempotency lookup."""
    log = MagicMock(spec=UsageLog)
    log.remaining_after = remaining
    return log


@pytest.mark.asyncio
async def test_consume_with_request_id_success(mock_db, mock_redis, mock_product, mock_redemption_code):
    """First call with request_id proceeds normally."""
    mock_redis.hgetall = AsyncMock(return_value={
        "status": "activated", "remaining_score": "100", "expires_at": "",
    })
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.eval = AsyncMock(return_value=90)

    found_code = MagicMock(); found_code.scalar_one_or_none.return_value = mock_redemption_code
    no_prior = MagicMock(); no_prior.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(side_effect=[found_code, no_prior])

    result = await consume_credits(
        db=mock_db, redis_client=mock_redis, code="A1B2-C3D4-E5F6-G7H8",
        amount=10, product=mock_product, client_ip=None, metadata=None,
        request_id="req-abc-123",
    )

    assert result["remaining_credits"] == 90
    mock_redis.eval.assert_called_once()
    mock_db.add.assert_called_once()


@pytest.mark.asyncio
async def test_consume_same_request_id_returns_cached(mock_db, mock_redis, mock_product, mock_redemption_code):
    """Duplicate request_id returns the prior result without deducting again."""
    prior_log = _make_prior_log(90)
    found_code = MagicMock(); found_code.scalar_one_or_none.return_value = mock_redemption_code
    found_prior = MagicMock(); found_prior.scalar_one_or_none.return_value = prior_log
    mock_db.execute = AsyncMock(side_effect=[found_code, found_prior])

    result = await consume_credits(
        db=mock_db, redis_client=mock_redis, code="A1B2-C3D4-E5F6-G7H8",
        amount=10, product=mock_product, client_ip=None, metadata=None,
        request_id="req-abc-123",
    )

    assert result["remaining_credits"] == 90
    mock_redis.hgetall.assert_not_called()
    mock_redis.eval.assert_not_called()


@pytest.mark.asyncio
async def test_consume_different_request_ids_deduct_independently(mock_db, mock_redis, mock_product, mock_redemption_code):
    """Different request_id values each perform their own deduction."""
    mock_redis.hgetall = AsyncMock(return_value={
        "status": "activated", "remaining_score": "100", "expires_at": "",
    })
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.eval = AsyncMock(side_effect=[90, 80])

    # Each call: 1st execute=code resolution, 2nd=idempotency check
    found_code = MagicMock(); found_code.scalar_one_or_none.return_value = mock_redemption_code
    no_prior = MagicMock(); no_prior.scalar_one_or_none.return_value = None
    found_code2 = MagicMock(); found_code2.scalar_one_or_none.return_value = mock_redemption_code
    no_prior2 = MagicMock(); no_prior2.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(side_effect=[found_code, no_prior, found_code2, no_prior2])

    result1 = await consume_credits(
        db=mock_db, redis_client=mock_redis, code="A1B2-C3D4-E5F6-G7H8",
        amount=10, product=mock_product, client_ip=None, metadata=None,
        request_id="req-001",
    )
    assert result1["remaining_credits"] == 90

    result2 = await consume_credits(
        db=mock_db, redis_client=mock_redis, code="A1B2-C3D4-E5F6-G7H8",
        amount=10, product=mock_product, client_ip=None, metadata=None,
        request_id="req-002",
    )
    assert result2["remaining_credits"] == 80
    assert mock_redis.eval.call_count == 2


@pytest.mark.asyncio
async def test_consume_different_codes_same_request_id_deduct_independently(
    mock_db, mock_redis, mock_product, mock_redemption_code,
):
    """Same product + same request_id + different codes must deduct independently."""
    mock_redis.hgetall = AsyncMock(return_value={
        "status": "activated", "remaining_score": "100", "expires_at": "",
    })
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.eval = AsyncMock(side_effect=[90, 80])

    code_a = MagicMock(spec=RedemptionCode)
    code_a.id = 1; code_a.key_code = "AAAA-BBBB-CCCC-DDDD"
    code_a.category_id = mock_product.id; code_a.status = "activated"
    code_a.remaining_score = 100; code_a.expires_at = None

    code_b = MagicMock(spec=RedemptionCode)
    code_b.id = 2; code_b.key_code = "EEEE-FFFF-GGGG-HHHH"
    code_b.category_id = mock_product.id; code_b.status = "activated"
    code_b.remaining_score = 100; code_b.expires_at = None

    found_a = MagicMock(); found_a.scalar_one_or_none.return_value = code_a
    no_prior_a = MagicMock(); no_prior_a.scalar_one_or_none.return_value = None
    found_b = MagicMock(); found_b.scalar_one_or_none.return_value = code_b
    no_prior_b = MagicMock(); no_prior_b.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(side_effect=[found_a, no_prior_a, found_b, no_prior_b])

    result1 = await consume_credits(
        db=mock_db, redis_client=mock_redis, code="AAAA-BBBB-CCCC-DDDD",
        amount=10, product=mock_product, client_ip=None, metadata=None,
        request_id="req-shared",
    )
    assert result1["remaining_credits"] == 90

    result2 = await consume_credits(
        db=mock_db, redis_client=mock_redis, code="EEEE-FFFF-GGGG-HHHH",
        amount=10, product=mock_product, client_ip=None, metadata=None,
        request_id="req-shared",
    )
    assert result2["remaining_credits"] == 80
    assert mock_redis.eval.call_count == 2


@pytest.mark.asyncio
async def test_consume_no_request_id_skips_idempotency(mock_db, mock_redis, mock_product, mock_redemption_code):
    """Without request_id, idempotency check is skipped entirely."""
    mock_redis.hgetall = AsyncMock(return_value={
        "status": "activated", "remaining_score": "100", "expires_at": "",
    })
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.eval = AsyncMock(return_value=90)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_redemption_code
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await consume_credits(
        db=mock_db, redis_client=mock_redis, code="A1B2-C3D4-E5F6-G7H8",
        amount=10, product=mock_product, client_ip=None, metadata=None,
        request_id=None,
    )

    assert result["remaining_credits"] == 90
    mock_redis.eval.assert_called_once()


@pytest.mark.asyncio
async def test_consume_idem_lock_contention_with_prior_result(mock_db, mock_redis, mock_product, mock_redemption_code):
    """When idempotency lock not acquired but prior log exists, return cached result."""
    prior_log = _make_prior_log(85)
    mock_redis.set = AsyncMock(return_value=None)  # idem lock not acquired

    found_code = MagicMock(); found_code.scalar_one_or_none.return_value = mock_redemption_code
    found_prior = MagicMock(); found_prior.scalar_one_or_none.return_value = prior_log
    mock_db.execute = AsyncMock(side_effect=[found_code, found_prior])

    result = await consume_credits(
        db=mock_db, redis_client=mock_redis, code="A1B2-C3D4-E5F6-G7H8",
        amount=10, product=mock_product, client_ip=None, metadata=None,
        request_id="req-concurrent",
    )

    assert result["remaining_credits"] == 85


@pytest.mark.asyncio
async def test_consume_idem_lock_contention_no_prior_raises_busy(
    mock_db, mock_redis, mock_product, mock_redemption_code,
):
    """When idempotency lock not acquired and no prior log, raise SystemBusy."""
    mock_redis.hgetall = AsyncMock(return_value={
        "status": "activated", "remaining_score": "90", "expires_at": "",
    })
    mock_redis.set = AsyncMock(side_effect=[None])

    found_code = MagicMock(); found_code.scalar_one_or_none.return_value = mock_redemption_code
    no_prior = MagicMock(); no_prior.scalar_one_or_none.return_value = None
    no_prior2 = MagicMock(); no_prior2.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(side_effect=[found_code, no_prior, no_prior2])

    with pytest.raises(SystemBusy):
        await consume_credits(
            db=mock_db, redis_client=mock_redis, code="A1B2-C3D4-E5F6-G7H8",
            amount=10, product=mock_product, client_ip=None, metadata=None,
            request_id="req-stuck",
        )
