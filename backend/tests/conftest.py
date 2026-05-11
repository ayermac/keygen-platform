from __future__ import annotations

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport

# Lazy import: app.main triggers database connection at import time.
# The client fixture imports it inside the function body instead.


@pytest_asyncio.fixture
async def client():
    from app.main import app  # lazy import to avoid DB connection at test collection
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_db():
    """Mock DB session — db.add/delete/flush are sync, db.execute/refresh are async."""
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
    redis.ping = AsyncMock(return_value=True)
    redis.eval = AsyncMock(return_value=90)
    return redis


@pytest.fixture
def mock_product():
    p = MagicMock()
    p.id = 1
    p.name = "测试产品"
    p.code = "test01"
    p.score_per_key = 100
    p.score_label = "积分"
    p.max_activations = 1
    p.expiry_days = 30
    p.api_key = "kg_test123"
    p.card_types = None
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
    k.batch_id = None
    k.card_type_name = None
    return k
