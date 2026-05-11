from __future__ import annotations

"""Legacy test file — now tests app.services.code_service (renamed from key_service)."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.code_service import redeem_code, consume_credits, get_balance
from app.exceptions import CodeAlreadyRedeemed, CodeNotFound


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.execute = AsyncMock()
    db.refresh = AsyncMock()
    db.flush = AsyncMock()
    return db


@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.hgetall = AsyncMock(return_value={})
    redis.hset = AsyncMock()
    redis.expire = AsyncMock()
    redis.hincrby = AsyncMock(return_value=90)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock()
    redis.eval = AsyncMock(return_value=90)
    return redis


@pytest.fixture
def mock_product():
    p = MagicMock()
    p.id = 1
    p.score_per_key = 100
    p.score_label = "积分"
    p.max_activations = 1
    p.expiry_days = 30
    return p


@pytest.fixture
def mock_redemption_code():
    k = MagicMock()
    k.id = 1
    k.key_code = "A1B2-C3D4-E5F6-G7H8"
    k.category_id = 1
    k.status = "unused"
    k.total_score = 100
    k.remaining_score = 100
    k.activated_at = None
    k.expires_at = None
    k.expiry_days = None
    return k


@pytest.mark.asyncio
async def test_activate_key_success(mock_db, mock_redis, mock_product, mock_redemption_code):
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


@pytest.mark.asyncio
async def test_activate_key_already_activated(mock_db, mock_redis, mock_product, mock_redemption_code):
    mock_redemption_code.status = "activated"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_redemption_code
    mock_db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(CodeAlreadyRedeemed):
        await redeem_code(
            db=mock_db, redis_client=mock_redis, code="A1B2-C3D4-E5F6-G7H8",
            product=mock_product, client_ip="127.0.0.1", metadata=None,
        )
