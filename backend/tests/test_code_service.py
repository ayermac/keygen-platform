from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.code_service import redeem_code, consume_credits, get_balance, generate_codes
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
async def test_consume_insufficient(mock_db, mock_redis, mock_product):
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
async def test_consume_system_busy(mock_db, mock_redis, mock_product):
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
async def test_consume_expired_code(mock_db, mock_redis, mock_product):
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
