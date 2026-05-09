import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta

from app.services.key_service import activate_key, deduct_score, get_balance


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.hgetall = AsyncMock(return_value={})
    redis.hset = AsyncMock()
    redis.expire = AsyncMock()
    redis.hincrby = AsyncMock(return_value=90)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock()
    return redis


@pytest.fixture
def mock_category():
    cat = MagicMock()
    cat.id = 1
    cat.score_per_key = 100
    cat.score_label = "积分"
    cat.max_activations = 1
    cat.expiry_days = 30
    return cat


@pytest.fixture
def mock_activation_key():
    key = MagicMock()
    key.id = 1
    key.key_code = "A1B2-C3D4-E5F6-G7H8"
    key.category_id = 1
    key.status = "unused"
    key.total_score = 100
    key.remaining_score = 100
    key.activated_at = None
    key.expires_at = None
    return key


@pytest.mark.asyncio
async def test_activate_key_success(mock_db, mock_redis, mock_category, mock_activation_key):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_activation_key
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await activate_key(
        db=mock_db,
        redis_client=mock_redis,
        key_code="A1B2-C3D4-E5F6-G7H8",
        category=mock_category,
        client_ip="127.0.0.1",
        metadata=None,
    )

    assert result["key_code"] == "A1B2-C3D4-E5F6-G7H8"
    assert result["total_score"] == 100
    assert result["remaining_score"] == 100
    assert mock_activation_key.status == "activated"


@pytest.mark.asyncio
async def test_activate_key_already_activated(mock_db, mock_redis, mock_category, mock_activation_key):
    mock_activation_key.status = "activated"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_activation_key
    mock_db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(Exception) as exc_info:
        await activate_key(
            db=mock_db,
            redis_client=mock_redis,
            key_code="A1B2-C3D4-E5F6-G7H8",
            category=mock_category,
            client_ip="127.0.0.1",
            metadata=None,
        )
    assert "已激活" in str(exc_info.value)
