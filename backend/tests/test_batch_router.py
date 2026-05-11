"""Tests for admin batch management endpoints."""
from __future__ import annotations

from datetime import datetime

import pytest
from unittest.mock import AsyncMock, MagicMock, patch as _patch
from httpx import AsyncClient

from app.main import app
from app.database import get_db
from app.middleware.jwt_auth import get_current_admin


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_admin():
    a = MagicMock()
    a.id = 1
    a.username = "admin"
    return a


@pytest.fixture
def override_admin(mock_admin):
    app.dependency_overrides[get_current_admin] = lambda: mock_admin


@pytest.mark.asyncio
async def test_batch_search(client: AsyncClient, mock_admin, override_admin):
    mock_batch = MagicMock()
    mock_batch.id = 1
    mock_batch.batch_id = "B001"
    mock_batch.product_name = "测试产品"
    mock_batch.card_type_name = None
    mock_batch.count = 10
    mock_batch.total_score = 100
    mock_batch.creator = "admin"
    mock_batch.remark = None
    mock_batch.created_at = "2026-05-11T00:00:00"

    mock_db = MagicMock()
    count_result = MagicMock()
    count_result.scalar.return_value = 1
    search_result = MagicMock()
    search_result.all.return_value = [mock_batch]
    mock_db.execute = AsyncMock(side_effect=[count_result, search_result])
    app.dependency_overrides[get_db] = lambda: mock_db

    resp = await client.post("/api/v1/admin/batches/search", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0
    assert data["data"]["total"] == 1
    assert data["data"]["items"][0]["batch_id"] == "B001"


@pytest.mark.asyncio
async def test_batch_detail(client: AsyncClient, mock_admin, override_admin):
    mock_batch = MagicMock()
    mock_batch.id = 1
    mock_batch.batch_id = "B001"
    mock_batch.product_name = "测试产品"
    mock_batch.card_type_name = None
    mock_batch.count = 2
    mock_batch.total_score = 100
    mock_batch.creator = "admin"
    mock_batch.remark = None
    mock_batch.created_at = "2026-05-11T00:00:00"

    mock_code = MagicMock()
    mock_code.id = 1
    mock_code.key_code = "A1B2-C3D4-E5F6-G7H8"
    mock_code.status = "unused"
    mock_code.total_score = 100
    mock_code.remaining_score = 100
    mock_code.activated_at = None
    mock_code.expires_at = None
    mock_code.created_at = "2026-05-11T00:00:00"

    mock_db = MagicMock()
    batch_result = MagicMock()
    batch_result.one_or_none.return_value = mock_batch
    codes_result = MagicMock()
    codes_result.scalars.return_value.all.return_value = [mock_code]
    mock_db.execute = AsyncMock(side_effect=[batch_result, codes_result])
    app.dependency_overrides[get_db] = lambda: mock_db

    resp = await client.get("/api/v1/admin/batches/B001")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0
    assert data["data"]["batch_id"] == "B001"
    assert len(data["data"]["codes"]) == 1
    assert data["data"]["codes"][0]["code"] == "A1B2-C3D4-E5F6-G7H8"


@pytest.mark.asyncio
async def test_batch_detail_not_found(client: AsyncClient, mock_admin, override_admin):
    mock_db = MagicMock()
    batch_result = MagicMock()
    batch_result.one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=batch_result)
    app.dependency_overrides[get_db] = lambda: mock_db

    resp = await client.get("/api/v1/admin/batches/INVALID")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 1402


@pytest.mark.asyncio
async def test_batch_disable(client: AsyncClient, mock_admin, override_admin):
    mock_batch = MagicMock()
    mock_batch.id = 1
    mock_batch.batch_id = "B001"

    mock_code1 = MagicMock()
    mock_code1.key_code = "AAAA-BBBB-CCCC-DDDD"
    mock_code1.status = "activated"
    mock_code2 = MagicMock()
    mock_code2.key_code = "EEEE-FFFF-GGGG-HHHH"
    mock_code2.status = "unused"

    mock_db = MagicMock()
    batch_result = MagicMock()
    batch_result.scalar_one_or_none.return_value = mock_batch
    activated_result = MagicMock()
    activated_result.scalars.return_value.all.return_value = [mock_code1]
    all_codes_result = MagicMock()
    all_codes_result.scalars.return_value.all.return_value = [mock_code1, mock_code2]
    mock_db.execute = AsyncMock(side_effect=[batch_result, activated_result, all_codes_result])
    app.dependency_overrides[get_db] = lambda: mock_db

    with _patch("app.redis_client.redis_client") as mock_redis:
        mock_redis.delete = AsyncMock()
        resp = await client.put("/api/v1/admin/batches/B001/disable")

    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0
    assert mock_code1.status == "disabled"
    assert mock_code2.status == "disabled"


@pytest.mark.asyncio
async def test_batch_export(client: AsyncClient, mock_admin, override_admin):
    mock_batch = MagicMock()
    mock_batch.id = 1
    mock_batch.batch_id = "B001"

    mock_code = MagicMock()
    mock_code.key_code = "AAAA-BBBB-CCCC-DDDD"
    mock_code.status = "unused"
    mock_code.total_score = 100
    mock_code.remaining_score = 100
    mock_code.expires_at = None
    mock_code.created_at = datetime(2026, 5, 11, 0, 0, 0)

    mock_db = MagicMock()
    batch_result = MagicMock()
    batch_result.scalar_one_or_none.return_value = mock_batch
    codes_result = MagicMock()
    codes_result.scalars.return_value.all.return_value = [mock_code]
    mock_db.execute = AsyncMock(side_effect=[batch_result, codes_result])
    app.dependency_overrides[get_db] = lambda: mock_db

    resp = await client.get("/api/v1/admin/batches/B001/export")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment" in resp.headers.get("content-disposition", "")
    body = resp.text
    assert "AAAA-BBBB-CCCC-DDDD" in body
    assert "unused" in body
