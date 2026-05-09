from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from sqlalchemy import select

from app.config import settings
from app.database import engine, Base, async_session
from app.middleware.jwt_auth import get_password_hash
from app.models.admin_user import AdminUser
from app.routers import client_codes, admin_auth, admin_products, admin_codes, admin_stats, admin_usage_logs, admin_audit


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Initialize default admin user
    async with async_session() as session:
        result = await session.execute(
            select(AdminUser).where(AdminUser.username == settings.admin_default_username)
        )
        if not result.scalar_one_or_none():
            admin = AdminUser(
                username=settings.admin_default_username,
                password_hash=get_password_hash(settings.admin_default_password),
            )
            session.add(admin)
            await session.commit()

    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="Keygen Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(client_codes.router)
app.include_router(admin_auth.router)
app.include_router(admin_products.router)
app.include_router(admin_codes.router)
app.include_router(admin_stats.router)
app.include_router(admin_usage_logs.router)
app.include_router(admin_audit.router)


@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}


AGENT_DOCS = """# Keygen Platform API Documentation (Agent-Friendly)

Base URL: /api/v1
Authentication: X-API-Key header (product API key)

## Endpoints

### POST /api/v1/codes/redeem
Redeem a redemption code. Changes status from "unused" to "activated".

Request:
{
  "code": "XXXX-XXXX-XXXX-XXXX",
  "metadata": { "username": "user123", "channel": "mobile" }  // optional
}

Response (code=0):
{
  "code": 0,
  "message": "success",
  "data": {
    "code": "XXXX-XXXX-XXXX-XXXX",
    "credit_unit": "credits",
    "total_credits": 100,
    "remaining_credits": 100,
    "expires_at": "2026-06-09T00:00:00"
  }
}

Error codes:
- 1001: Code not found
- 1002: Already redeemed
- 1003: Expired
- 1004: Disabled

---

### POST /api/v1/codes/consume
Consume credits from a redeemed code. Atomic operation with Redis distributed lock.

Request:
{
  "code": "XXXX-XXXX-XXXX-XXXX",
  "amount": 10,  // required, must be > 0
  "metadata": { "order_id": "ORD-123", "description": "Purchase item" }  // optional
}

Response (code=0):
{
  "code": 0,
  "message": "success",
  "data": {
    "remaining_credits": 90
  }
}

Error codes:
- 1001: Code not found or not activated
- 1101: Consume failed
- 1102: Insufficient credits
- 1103: System busy (retry after a moment)

---

### POST /api/v1/codes/balance
Query remaining credits and status of a code.

Request:
{
  "code": "XXXX-XXXX-XXXX-XXXX"
}

Response (code=0):
{
  "code": 0,
  "message": "success",
  "data": {
    "code": "XXXX-XXXX-XXXX-XXXX",
    "credit_unit": "credits",
    "total_credits": 100,
    "remaining_credits": 90,
    "status": "activated",
    "expires_at": "2026-06-09T00:00:00"
  }
}

Status values: unused, activated, expired, disabled

---

## Response Format

All responses follow this envelope:
{
  "code": 0,       // 0 = success, non-zero = error
  "message": "...", // "success" or error description
  "data": {...}     // null on error
}

## Agent Integration Notes

1. Authentication: All requests require X-API-Key header with the product API key
2. Idempotency: Redeem is NOT idempotent (1002 on repeat). Consume is NOT idempotent (deducts each call).
3. Error handling: Check code === 0 first, then read data. For non-zero codes, decide retry strategy based on error code.
4. Concurrency: Consume uses Redis distributed lock, safe for concurrent calls. Retry on 1103 errors.
5. metadata: All endpoints support optional metadata field for context (user ID, device, operation type, etc.) for audit trail.
6. Code format: XXXX-XXXX-XXXX-XXXX (4 uppercase alphanumeric segments separated by hyphens, 19 chars total)
"""


@app.get("/api/v1/agent-docs", response_class=PlainTextResponse)
async def agent_docs():
    return AGENT_DOCS
