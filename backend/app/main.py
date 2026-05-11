import logging
import sys
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from sqlalchemy import select, text

from app.config import settings
from app.database import engine, Base, async_session
from app.exceptions import BizError
from app.middleware.jwt_auth import get_password_hash
from app.models.admin_user import AdminUser
from app.routers import client_codes, admin_auth, admin_products, admin_codes, admin_stats, admin_usage_logs, admin_audit

# ── Structured Logging ──

logging.basicConfig(
    level=logging.DEBUG if settings.app_debug else logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("keygen")


# ── Startup Validation ──

def validate_production_config():
    """Refuse to start if production config has obvious unsafe defaults."""
    if settings.app_env == "production":
        errors = []
        if settings.jwt_secret_key in ("change_me_in_production", "change_me_in_production_use_openssl_rand_hex_32"):
            errors.append("JWT_SECRET_KEY is set to default value")
        if settings.mysql_password in ("change_me_in_production", ""):
            errors.append("MYSQL_PASSWORD is set to default value")
        if settings.admin_default_password in ("admin123", ""):
            errors.append("ADMIN_DEFAULT_PASSWORD is set to default value")
        if settings.app_debug:
            errors.append("APP_DEBUG must be false in production")
        if errors:
            for e in errors:
                logger.error(f"CONFIG ERROR: {e}")
            sys.exit(1)


# ── Lifespan ──

@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_production_config()

    # Startup — dev only: auto-create tables
    if settings.app_env != "production":
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

    logger.info("Keygen Platform started")
    yield
    # Shutdown
    await engine.dispose()
    logger.info("Keygen Platform stopped")


# ── App ──

app = FastAPI(
    title="Keygen Platform",
    version="1.0.0",
    lifespan=lifespan,
)


# ── Middleware: Request ID + Logging ──

@app.middleware("http")
async def request_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start = time.perf_counter()

    response = await call_next(request)

    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    client_ip = request.client.host if request.client else "-"
    status = response.status_code

    response.headers["X-Request-ID"] = request_id

    if status >= 500:
        logger.error("request_id=%s method=%s path=%s status=%d duration_ms=%.2f client_ip=%s",
                      request_id, request.method, request.url.path, status, duration_ms, client_ip)
    elif status >= 400:
        logger.warning("request_id=%s method=%s path=%s status=%d duration_ms=%.2f client_ip=%s",
                        request_id, request.method, request.url.path, status, duration_ms, client_ip)
    else:
        logger.info("request_id=%s method=%s path=%s status=%d duration_ms=%.2f client_ip=%s",
                     request_id, request.method, request.url.path, status, duration_ms, client_ip)

    return response


# ── Global Exception Handler ──

@app.exception_handler(BizError)
async def biz_error_handler(request: Request, exc: BizError):
    return JSONResponse(
        status_code=200,
        content={"code": exc.code, "message": exc.message, "data": None},
    )


# ── Routers ──

app.include_router(client_codes.router)
app.include_router(admin_auth.router)
app.include_router(admin_products.router)
app.include_router(admin_codes.router)
app.include_router(admin_stats.router)
app.include_router(admin_usage_logs.router)
app.include_router(admin_audit.router)


# ── Health Endpoints ──

@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}


@app.get("/api/v1/health/ready")
async def readiness():
    """Check MySQL and Redis connectivity."""
    checks = {}
    healthy = True

    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        checks["mysql"] = "ok"
    except Exception as e:
        checks["mysql"] = f"error: {type(e).__name__}"
        healthy = False

    try:
        from app.redis_client import redis_client
        await redis_client.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {type(e).__name__}"
        healthy = False

    status_code = 200 if healthy else 503
    return JSONResponse(
        status_code=status_code,
        content={"status": "ready" if healthy else "not_ready", "checks": checks},
    )


# ── Agent-Friendly API Docs ──

AGENT_DOCS = """# Keygen Platform API Documentation (Agent-Friendly)

Base URL: /api/v1
Authentication: X-API-Key header (product API key)

## Endpoints

### POST /api/v1/codes/redeem
Redeem a redemption code. Changes status from "unused" to "activated".

Request:
{
  "code": "XXXX-XXXX-XXXX-XXXX",
  "metadata": { "username": "user123", "channel": "mobile" }
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
- 1005: Product mismatch

---

### POST /api/v1/codes/consume
Consume credits from a redeemed code. Atomic operation with Redis Lua script.

Request:
{
  "code": "XXXX-XXXX-XXXX-XXXX",
  "amount": 10,
  "metadata": { "order_id": "ORD-123" }
}

Response (code=0):
{
  "code": 0,
  "message": "success",
  "data": { "remaining_credits": 90 }
}

Error codes:
- 1001: Code not found
- 1003: Expired
- 1102: Insufficient credits
- 1103: System busy (retry after a moment)
- 1104: Code not activated

---

### POST /api/v1/codes/balance
Query remaining credits and status of a code.

Request:
{ "code": "XXXX-XXXX-XXXX-XXXX" }

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

{ "code": 0, "message": "...", "data": {...} }

## Error Codes

| Code | Meaning |
|------|---------|
| 1001 | Code not found |
| 1002 | Already redeemed |
| 1003 | Expired |
| 1004 | Disabled |
| 1005 | Product mismatch |
| 1101 | Consume failed |
| 1102 | Insufficient credits |
| 1103 | System busy (retry) |
| 1104 | Code not activated |
| 1201 | Login failed |
| 1301 | Product code exists |
| 1302 | Product not found |
| 1303 | Product has codes |
| 1401 | Invalid generate count |
| 1501 | Invalid API key |

## Agent Integration Notes

1. Auth: X-API-Key header required
2. Redeem is NOT idempotent (1002 on repeat). Consume deducts each call.
3. Check code === 0 first. Retry on 1103 errors.
4. Consume uses Redis Lua script for atomic check-and-decrement.
5. metadata field supports audit context.
6. Code format: XXXX-XXXX-XXXX-XXXX (19 chars)
"""


@app.get("/api/v1/agent-docs", response_class=PlainTextResponse)
async def agent_docs():
    return AGENT_DOCS
