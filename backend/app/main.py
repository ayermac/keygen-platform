from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import select

from app.config import settings
from app.database import engine, Base, async_session
from app.middleware.jwt_auth import get_password_hash
from app.models.admin_user import AdminUser
from app.routers import api_keys, admin_auth, admin_categories, admin_keys, admin_stats, admin_usage_logs, admin_audit


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

app.include_router(api_keys.router)
app.include_router(admin_auth.router)
app.include_router(admin_categories.router)
app.include_router(admin_keys.router)
app.include_router(admin_stats.router)
app.include_router(admin_usage_logs.router)
app.include_router(admin_audit.router)


@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}
