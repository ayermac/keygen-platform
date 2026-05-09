# Keygen Platform Implementation Plan

> **术语更新说明：** 本计划中的代码示例使用旧术语，实际代码已按以下对照更新：
> - 激活码(ActivationKey) → 兑换码(RedemptionCode)，分类(Category) → 产品(Product)
> - score/积分 → credits/额度，activate → redeem，deduct → consume
> - API 路径：`/api/v1/keys/*` → `/api/v1/codes/*`
> - 字段：`key_code` → `code`，`score_label` → `credit_unit`，`total_score` → `total_credits`

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a universal redemption code generation and management platform with credit consumption capability.

**Architecture:** FastAPI backend with MySQL persistence and Redis caching for C端 high-performance APIs. Vue3 + Element Plus frontend for admin management. Docker Compose deployment with Nginx reverse proxy.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy, Alembic, Redis, MySQL 8.0, Vue3, Element Plus, Pinia, Docker, Nginx

---

## File Structure

```
keygen-platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── redis_client.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── product.py
│   │   │   ├── redemption_code.py
│   │   │   ├── usage_log.py
│   │   │   ├── admin_user.py
│   │   │   └── audit_log.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── code.py
│   │   │   ├── product.py
│   │   │   └── admin.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── client_codes.py
│   │   │   ├── admin_auth.py
│   │   │   ├── admin_products.py
│   │   │   ├── admin_codes.py
│   │   │   ├── admin_stats.py
│   │   │   ├── admin_usage_logs.py
│   │   │   └── admin_audit.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── code_service.py
│   │   │   └── stats_service.py
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── api_key_auth.py
│   │   │   └── jwt_auth.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── key_generator.py
│   │       └── response.py
│   ├── alembic/
│   │   └── env.py
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── Dockerfile
│   └── tests/
│       ├── conftest.py
│       ├── test_key_generator.py
│       ├── test_key_service.py
│       ├── test_score_service.py
│       ├── test_api_keys.py
│       ├── test_admin_auth.py
│       └── test_admin_categories.py
├── frontend/
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── router/
│   │   │   └── index.ts
│   │   ├── stores/
│   │   │   └── auth.ts
│   │   ├── api/
│   │   │   ├── request.ts
│   │   │   ├── auth.ts
│   │   │   ├── products.ts
│   │   │   ├── codes.ts
│   │   │   ├── stats.ts
│   │   │   ├── usageLogs.ts
│   │   │   └── auditLogs.ts
│   │   ├── views/
│   │   │   ├── Login.vue
│   │   │   ├── Layout.vue
│   │   │   ├── Dashboard.vue
│   │   │   ├── Products.vue
│   │   │   ├── Keys.vue
│   │   │   ├── UsageLogs.vue
│   │   │   ├── AuditLogs.vue
│   │   │   └── ApiDocs.vue
│   │   └── utils/
│   │       └── format.ts
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── .env.example
└── .gitignore
```

---

### Task 1: Project Scaffolding & Docker Setup

**Files:**
- Create: `.gitignore`
- Create: `.env.example`
- Create: `docker-compose.yml`
- Create: `backend/Dockerfile`
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/app/main.py`

- [ ] **Step 1: Create .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
.eggs/
*.egg
.venv/
venv/
env/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Environment
.env

# Node
node_modules/
frontend/dist/

# Docker
docker-compose.override.yml

# Alembic
alembic/versions/*.pyc

# Test
.pytest_cache/
htmlcov/
.coverage
```

- [ ] **Step 2: Create .env.example**

```env
# MySQL
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=keygen
MYSQL_PASSWORD=change_me_in_production
MYSQL_DATABASE=keygen

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# JWT
JWT_SECRET_KEY=change_me_in_production_use_openssl_rand_hex_32
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=480

# Admin
ADMIN_DEFAULT_USERNAME=admin
ADMIN_DEFAULT_PASSWORD=admin123

# App
APP_ENV=development
APP_DEBUG=true
```

- [ ] **Step 3: Create backend/requirements.txt**

```txt
fastapi==0.115.0
uvicorn[standard]==0.30.6
sqlalchemy==2.0.35
alembic==1.13.2
pymysql==1.1.1
cryptography==43.0.0
redis==5.0.8
pydantic==2.9.2
pydantic-settings==2.5.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
httpx==0.27.2
pytest==8.3.3
pytest-asyncio==0.24.0
```

- [ ] **Step 4: Create backend/Dockerfile**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

- [ ] **Step 5: Create backend/app/config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MySQL
    mysql_host: str = "mysql"
    mysql_port: int = 3306
    mysql_user: str = "keygen"
    mysql_password: str = "change_me_in_production"
    mysql_database: str = "keygen"

    # Redis
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0

    # JWT
    jwt_secret_key: str = "change_me_in_production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480

    # Admin
    admin_default_username: str = "admin"
    admin_default_password: str = "admin123"

    # App
    app_env: str = "development"
    app_debug: bool = True

    @property
    def mysql_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    class Config:
        env_file = ".env"


settings = Settings()
```

- [ ] **Step 6: Create backend/app/main.py**

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="Keygen Platform",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 7: Create docker-compose.yml**

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./frontend/nginx.conf:/etc/nginx/conf.d/default.conf
      - frontend_dist:/usr/share/nginx/html
    depends_on:
      - backend
      - frontend

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    volumes:
      - frontend_dist:/app/dist

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./backend:/app
    depends_on:
      - mysql
      - redis

  mysql:
    image: mysql:8.0
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: keygen
      MYSQL_USER: keygen
      MYSQL_PASSWORD: ${MYSQL_PASSWORD:-change_me_in_production}
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  mysql_data:
  redis_data:
  frontend_dist:
```

- [ ] **Step 8: Commit**

```bash
git add .gitignore .env.example docker-compose.yml backend/Dockerfile backend/requirements.txt backend/app/__init__.py backend/app/config.py backend/app/main.py
git commit -m "feat: project scaffolding with Docker Compose setup"
```

---

### Task 2: Database Layer (SQLAlchemy Models & Alembic)

**Files:**
- Create: `backend/app/database.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/product.py`
- Create: `backend/app/models/redemption_code.py`
- Create: `backend/app/models/usage_log.py`
- Create: `backend/app/models/admin_user.py`
- Create: `backend/app/models/audit_log.py`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`

- [ ] **Step 1: Create backend/app/database.py**

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.mysql_url, echo=settings.app_debug)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

- [ ] **Step 2: Create backend/app/models/category.py**

```python
from datetime import datetime

from sqlalchemy import BigInteger, String, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    score_per_key: Mapped[int] = mapped_column(Integer, nullable=False)
    score_label: Mapped[str] = mapped_column(String(50), nullable=False, default="积分")
    max_activations: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    expiry_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    api_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    activation_keys = relationship("ActivationKey", back_populates="category")
```

- [ ] **Step 3: Create backend/app/models/activation_key.py**

```python
from datetime import datetime

from sqlalchemy import BigInteger, String, Integer, DateTime, Enum, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ActivationKey(Base):
    __tablename__ = "activation_key"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    key_code: Mapped[str] = mapped_column(String(19), unique=True, nullable=False)
    category_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("category.id"), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("unused", "activated", "expired", "disabled", name="key_status"),
        nullable=False,
        default="unused",
    )
    batch_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    total_score: Mapped[int] = mapped_column(Integer, nullable=False)
    remaining_score: Mapped[int] = mapped_column(Integer, nullable=False)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    category = relationship("Category", back_populates="activation_keys")
    logs = relationship("ActivationLog", back_populates="activation_key")
```

- [ ] **Step 4: Create backend/app/models/activation_log.py**

```python
from datetime import datetime

from sqlalchemy import BigInteger, String, Integer, DateTime, Enum, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ActivationLog(Base):
    __tablename__ = "activation_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    key_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("activation_key.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("category.id"), nullable=False)
    action: Mapped[str] = mapped_column(
        Enum("activate", "deduct", name="log_action"), nullable=False
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    remaining_after: Mapped[int] = mapped_column(Integer, nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    client_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    activation_key = relationship("ActivationKey", back_populates="logs")
```

- [ ] **Step 5: Create backend/app/models/admin_user.py**

```python
from datetime import datetime

from sqlalchemy import BigInteger, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AdminUser(Base):
    __tablename__ = "admin_user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
```

- [ ] **Step 6: Create backend/app/models/audit_log.py**

```python
from datetime import datetime

from sqlalchemy import BigInteger, String, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    admin_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("admin_user.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    detail: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
```

- [ ] **Step 7: Create backend/app/models/__init__.py**

```python
from app.models.category import Category
from app.models.activation_key import ActivationKey
from app.models.activation_log import ActivationLog
from app.models.admin_user import AdminUser
from app.models.audit_log import AuditLog

__all__ = ["Category", "ActivationKey", "ActivationLog", "AdminUser", "AuditLog"]
```

- [ ] **Step 8: Setup Alembic and generate initial migration**

```bash
cd backend
alembic init alembic
# Edit alembic/env.py to import Base and configure async engine
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

- [ ] **Step 9: Commit**

```bash
git add backend/app/database.py backend/app/models/ backend/alembic.ini backend/alembic/
git commit -m "feat: database models and Alembic migration setup"
```

---

### Task 3: Redis Client & Utility Modules

**Files:**
- Create: `backend/app/redis_client.py`
- Create: `backend/app/utils/__init__.py`
- Create: `backend/app/utils/response.py`
- Create: `backend/app/utils/key_generator.py`
- Create: `backend/tests/test_key_generator.py`

- [ ] **Step 1: Write test for key generator**

```python
# backend/tests/test_key_generator.py
import re
from app.utils.key_generator import generate_key_code, generate_batch_key_codes


def test_generate_key_code_format():
    code = generate_key_code()
    assert len(code) == 19
    assert re.match(r"^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$", code)


def test_generate_key_code_uniqueness():
    codes = {generate_key_code() for _ in range(1000)}
    assert len(codes) == 1000


def test_generate_batch_key_codes():
    codes = generate_batch_key_codes(100)
    assert len(codes) == 100
    assert len(set(codes)) == 100


def test_generate_batch_key_codes_format():
    codes = generate_batch_key_codes(10)
    for code in codes:
        assert len(code) == 19
        assert re.match(r"^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$", code)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend && python -m pytest tests/test_key_generator.py -v
```
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Implement key generator**

```python
# backend/app/utils/key_generator.py
import random
import string

CHARS = string.ascii_uppercase + string.digits


def generate_key_code() -> str:
    segments = ["".join(random.choices(CHARS, k=4)) for _ in range(4)]
    return "-".join(segments)


def generate_batch_key_codes(count: int) -> list[str]:
    codes: set[str] = set()
    while len(codes) < count:
        codes.add(generate_key_code())
    return list(codes)
```

- [ ] **Step 4: Implement response utility**

```python
# backend/app/utils/response.py
from typing import Any

from pydantic import BaseModel


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = None


def success(data: Any = None) -> dict:
    return ApiResponse(code=0, message="success", data=data).model_dump()


def error(code: int, message: str) -> dict:
    return ApiResponse(code=code, message=message, data=None).model_dump()
```

- [ ] **Step 5: Create Redis client**

```python
# backend/app/redis_client.py
import redis.asyncio as redis

from app.config import settings

redis_client = redis.from_url(settings.redis_url, decode_responses=True)


async def get_redis() -> redis.Redis:
    return redis_client
```

- [ ] **Step 6: Run test to verify it passes**

```bash
cd backend && python -m pytest tests/test_key_generator.py -v
```
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add backend/app/utils/ backend/app/redis_client.py backend/tests/test_key_generator.py
git commit -m "feat: key generator, response utility, and Redis client"
```

---

### Task 4: Schemas (Pydantic Models)

**Files:**
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/schemas/code.py`
- Create: `backend/app/schemas/product.py`
- Create: `backend/app/schemas/admin.py`

- [ ] **Step 1: Create backend/app/schemas/key.py**

```python
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ActivateRequest(BaseModel):
    key_code: str
    metadata: dict[str, Any] | None = None


class ActivateResponse(BaseModel):
    key_code: str
    score_label: str
    total_score: int
    remaining_score: int
    expires_at: datetime | None


class DeductRequest(BaseModel):
    key_code: str
    amount: int
    metadata: dict[str, Any] | None = None


class DeductResponse(BaseModel):
    remaining_score: int


class BalanceRequest(BaseModel):
    key_code: str
    metadata: dict[str, Any] | None = None


class BalanceResponse(BaseModel):
    key_code: str
    score_label: str
    total_score: int
    remaining_score: int
    status: str
    expires_at: datetime | None


class KeyGenerateRequest(BaseModel):
    category_id: int
    count: int
    batch_id: str | None = None


class KeyGenerateResponse(BaseModel):
    batch_id: str
    count: int
    keys: list[str]


class KeySearchRequest(BaseModel):
    category_id: int | None = None
    status: str | None = None
    batch_id: str | None = None
    key_code: str | None = None
    page: int = 1
    page_size: int = 20


class KeyItem(BaseModel):
    id: int
    key_code: str
    category_name: str
    status: str
    total_score: int
    remaining_score: int
    batch_id: str | None
    activated_at: datetime | None
    expires_at: datetime | None
    created_at: datetime


class KeySearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[KeyItem]


class UsageLogSearchRequest(BaseModel):
    key_code: str | None = None
    category_id: int | None = None
    action: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    page: int = 1
    page_size: int = 20


class UsageLogItem(BaseModel):
    id: int
    key_code: str
    category_name: str
    action: str
    amount: int
    remaining_after: int
    metadata: dict[str, Any] | None
    client_ip: str | None
    created_at: datetime


class UsageLogSearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[UsageLogItem]
```

- [ ] **Step 2: Create backend/app/schemas/category.py**

```python
from datetime import datetime

from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    code: str
    score_per_key: int
    score_label: str = "积分"
    max_activations: int = 1
    expiry_days: int | None = None


class CategoryUpdate(BaseModel):
    name: str | None = None
    score_per_key: int | None = None
    score_label: str | None = None
    max_activations: int | None = None
    expiry_days: int | None = None


class CategoryItem(BaseModel):
    id: int
    name: str
    code: str
    score_per_key: int
    score_label: str
    max_activations: int
    expiry_days: int | None
    api_key: str
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    items: list[CategoryItem]
```

- [ ] **Step 3: Create backend/app/schemas/admin.py**

```python
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str


class AuditLogItem(BaseModel):
    id: int
    admin_username: str
    action: str
    target_type: str
    target_id: int | None
    detail: dict | None
    created_at: str


class AuditLogListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[AuditLogItem]


class StatsOverview(BaseModel):
    total_keys: int
    activated_keys: int
    total_score_consumed: int
    today_activations: int


class CategoryStats(BaseModel):
    category_id: int
    category_name: str
    total_keys: int
    activated_keys: int
    total_score: int
    consumed_score: int
    activation_trend: list[dict]
```

- [ ] **Step 4: Create backend/app/schemas/__init__.py**

```python
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/schemas/
git commit -m "feat: Pydantic request/response schemas"
```

---

### Task 5: Auth Middleware (API Key + JWT)

**Files:**
- Create: `backend/app/middleware/__init__.py`
- Create: `backend/app/middleware/api_key_auth.py`
- Create: `backend/app/middleware/jwt_auth.py`

- [ ] **Step 1: Implement API Key auth middleware**

```python
# backend/app/middleware/api_key_auth.py
from fastapi import Depends, HTTPException, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.category import Category


async def get_category_by_api_key(
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> Category:
    result = await db.execute(select(Category).where(Category.api_key == x_api_key))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return category
```

- [ ] **Step 2: Implement JWT auth middleware**

```python
# backend/app/middleware/jwt_auth.py
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Header
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.admin_user import AdminUser

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


async def get_current_admin(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
) -> AdminUser:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")

    token = authorization[7:]
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(AdminUser).where(AdminUser.username == username))
    admin = result.scalar_one_or_none()
    if admin is None:
        raise HTTPException(status_code=401, detail="User not found")
    return admin
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/middleware/
git commit -m "feat: API Key and JWT authentication middleware"
```

---

### Task 6: Key Service (Core Business Logic)

**Files:**
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/key_service.py`
- Create: `backend/tests/test_key_service.py`

- [ ] **Step 1: Write tests for key service**

```python
# backend/tests/test_key_service.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend && python -m pytest tests/test_key_service.py -v
```
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Implement key service**

```python
# backend/app/services/key_service.py
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activation_key import ActivationKey
from app.models.activation_log import ActivationLog
from app.models.category import Category
from app.utils.key_generator import generate_batch_key_codes


async def activate_key(
    db: AsyncSession,
    redis_client: Any,
    key_code: str,
    category: Category,
    client_ip: str | None,
    metadata: dict | None,
) -> dict:
    result = await db.execute(
        select(ActivationKey).where(ActivationKey.key_code == key_code)
    )
    activation_key = result.scalar_one_or_none()

    if not activation_key:
        raise Exception("激活码不存在")
    if activation_key.category_id != category.id:
        raise Exception("激活码不属于该分类")
    if activation_key.status == "activated":
        raise Exception("激活码已激活")
    if activation_key.status == "disabled":
        raise Exception("激活码已禁用")
    if activation_key.status == "expired":
        raise Exception("激活码已过期")

    now = datetime.now(timezone.utc)
    expires_at = None
    if category.expiry_days:
        expires_at = now + timedelta(days=category.expiry_days)

    activation_key.status = "activated"
    activation_key.activated_at = now
    activation_key.expires_at = expires_at

    log = ActivationLog(
        key_id=activation_key.id,
        category_id=category.id,
        action="activate",
        amount=category.score_per_key,
        remaining_after=category.score_per_key,
        metadata_=metadata,
        client_ip=client_ip,
    )
    db.add(log)

    # Update Redis cache
    cache_data = {
        "status": "activated",
        "total_score": str(category.score_per_key),
        "remaining_score": str(category.score_per_key),
        "expires_at": expires_at.isoformat() if expires_at else "",
        "category_id": str(category.id),
    }
    await redis_client.hset(f"key:{key_code}", mapping=cache_data)
    await redis_client.expire(f"key:{key_code}", 1800)

    return {
        "key_code": key_code,
        "score_label": category.score_label,
        "total_score": category.score_per_key,
        "remaining_score": category.score_per_key,
        "expires_at": expires_at,
    }


async def deduct_score(
    db: AsyncSession,
    redis_client: Any,
    key_code: str,
    amount: int,
    category: Category,
    client_ip: str | None,
    metadata: dict | None,
) -> dict:
    # Check cache first
    cache = await redis_client.hgetall(f"key:{key_code}")

    if not cache:
        result = await db.execute(
            select(ActivationKey).where(ActivationKey.key_code == key_code)
        )
        activation_key = result.scalar_one_or_none()
        if not activation_key:
            raise Exception("激活码不存在")
        if activation_key.status != "activated":
            raise Exception("激活码未激活或已过期")
        cache = {
            "status": activation_key.status,
            "remaining_score": str(activation_key.remaining_score),
            "expires_at": activation_key.expires_at.isoformat() if activation_key.expires_at else "",
        }
        await redis_client.hset(f"key:{key_code}", mapping=cache)
        await redis_client.expire(f"key:{key_code}", 1800)

    if cache.get("expires_at"):
        expires_at = datetime.fromisoformat(cache["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            raise Exception("激活码已过期")

    remaining = int(cache.get("remaining_score", 0))
    if remaining < amount:
        raise Exception("余额不足")

    # Atomic decrement with lock
    lock_key = f"lock:key:{key_code}"
    acquired = await redis_client.set(lock_key, "1", nx=True, ex=5)
    if not acquired:
        raise Exception("系统繁忙，请稍后重试")

    try:
        new_remaining = await redis_client.hincrby(f"key:{key_code}", "remaining_score", -amount)

        # Async write to MySQL
        result = await db.execute(
            select(ActivationKey).where(ActivationKey.key_code == key_code)
        )
        activation_key = result.scalar_one_or_none()
        if activation_key:
            activation_key.remaining_score = new_remaining
            log = ActivationLog(
                key_id=activation_key.id,
                category_id=category.id,
                action="deduct",
                amount=amount,
                remaining_after=new_remaining,
                metadata_=metadata,
                client_ip=client_ip,
            )
            db.add(log)

        return {"remaining_score": new_remaining}
    finally:
        await redis_client.delete(lock_key)


async def get_balance(
    redis_client: Any,
    key_code: str,
    db: AsyncSession,
    category: Category,
    client_ip: str | None,
    metadata: dict | None,
) -> dict:
    cache = await redis_client.hgetall(f"key:{key_code}")

    if not cache:
        result = await db.execute(
            select(ActivationKey).where(ActivationKey.key_code == key_code)
        )
        activation_key = result.scalar_one_or_none()
        if not activation_key:
            raise Exception("激活码不存在")
        if activation_key.category_id != category.id:
            raise Exception("激活码不属于该分类")

        cache = {
            "status": activation_key.status,
            "total_score": str(activation_key.total_score),
            "remaining_score": str(activation_key.remaining_score),
            "expires_at": activation_key.expires_at.isoformat() if activation_key.expires_at else "",
        }
        await redis_client.hset(f"key:{key_code}", mapping=cache)
        await redis_client.expire(f"key:{key_code}", 1800)

        return {
            "key_code": key_code,
            "score_label": category.score_label,
            "total_score": activation_key.total_score,
            "remaining_score": activation_key.remaining_score,
            "status": activation_key.status,
            "expires_at": activation_key.expires_at,
        }

    return {
        "key_code": key_code,
        "score_label": category.score_label,
        "total_score": int(cache.get("total_score", 0)),
        "remaining_score": int(cache.get("remaining_score", 0)),
        "status": cache.get("status", "unknown"),
        "expires_at": cache.get("expires_at") or None,
    }


async def generate_keys(
    db: AsyncSession,
    category: Category,
    count: int,
    batch_id: str | None,
) -> tuple[str, list[str]]:
    if not batch_id:
        batch_id = f"B{int(datetime.now(timezone.utc).timestamp())}"

    codes = generate_batch_key_codes(count)

    for code in codes:
        key = ActivationKey(
            key_code=code,
            category_id=category.id,
            status="unused",
            batch_id=batch_id,
            total_score=category.score_per_key,
            remaining_score=category.score_per_key,
        )
        db.add(key)

    return batch_id, codes
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd backend && python -m pytest tests/test_key_service.py -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/key_service.py backend/tests/test_key_service.py
git commit -m "feat: key service with activate, deduct, balance, and generate"
```

---

### Task 7: C端 API Routes

**Files:**
- Create: `backend/app/routers/__init__.py`
- Create: `backend/app/routers/client_codes.py`
- Modify: `backend/app/main.py` (register router)

- [ ] **Step 1: Implement C端 API routes**

```python
# backend/app/routers/api_keys.py
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.api_key_auth import get_category_by_api_key
from app.models.category import Category
from app.redis_client import get_redis
from app.schemas.key import (
    ActivateRequest,
    ActivateResponse,
    BalanceRequest,
    BalanceResponse,
    DeductRequest,
    DeductResponse,
)
from app.services.key_service import activate_key, deduct_score, get_balance
from app.utils.response import success, error

router = APIRouter(prefix="/api/v1/keys", tags=["C端接口"])


@router.post("/activate")
async def activate(
    req: ActivateRequest,
    request: Request,
    category: Category = Depends(get_category_by_api_key),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    try:
        client_ip = request.client.host if request.client else None
        result = await activate_key(
            db=db,
            redis_client=redis,
            key_code=req.key_code,
            category=category,
            client_ip=client_ip,
            metadata=req.metadata,
        )
        return success(result)
    except Exception as e:
        code = 1001
        msg = str(e)
        if "已激活" in msg:
            code = 1002
        elif "已过期" in msg:
            code = 1003
        elif "已禁用" in msg:
            code = 1004
        return error(code, msg)


@router.post("/deduct")
async def deduct(
    req: DeductRequest,
    request: Request,
    category: Category = Depends(get_category_by_api_key),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    try:
        client_ip = request.client.host if request.client else None
        result = await deduct_score(
            db=db,
            redis_client=redis,
            key_code=req.key_code,
            amount=req.amount,
            category=category,
            client_ip=client_ip,
            metadata=req.metadata,
        )
        return success(result)
    except Exception as e:
        code = 1101
        msg = str(e)
        if "余额不足" in msg:
            code = 1102
        elif "繁忙" in msg:
            code = 1103
        return error(code, msg)


@router.post("/balance")
async def balance(
    req: BalanceRequest,
    request: Request,
    category: Category = Depends(get_category_by_api_key),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    try:
        client_ip = request.client.host if request.client else None
        result = await get_balance(
            redis_client=redis,
            key_code=req.key_code,
            db=db,
            category=category,
            client_ip=client_ip,
            metadata=req.metadata,
        )
        return success(result)
    except Exception as e:
        return error(1001, str(e))
```

- [ ] **Step 2: Register router in main.py**

```python
# backend/app/main.py - add after app creation
from app.routers import api_keys

app.include_router(api_keys.router)
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/routers/api_keys.py backend/app/main.py
git commit -m "feat: C端 activation code API routes"
```

---

### Task 8: B端 Admin Auth & Category Routes

**Files:**
- Create: `backend/app/routers/admin_auth.py`
- Create: `backend/app/routers/admin_products.py`
- Modify: `backend/app/main.py` (register routers)

- [ ] **Step 1: Implement admin auth routes**

```python
# backend/app/routers/admin_auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.middleware.jwt_auth import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.models.admin_user import AdminUser
from app.schemas.admin import LoginRequest, LoginResponse
from app.utils.response import success, error

router = APIRouter(prefix="/api/v1/admin", tags=["管理后台-认证"])


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AdminUser).where(AdminUser.username == req.username))
    admin = result.scalar_one_or_none()

    if not admin:
        return error(1201, "用户名或密码错误")
    if not verify_password(req.password, admin.password_hash):
        return error(1201, "用户名或密码错误")

    token = create_access_token(data={"sub": admin.username})
    return success({"token": token})
```

- [ ] **Step 2: Implement admin category routes**

```python
# backend/app/routers/admin_categories.py
import secrets

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.jwt_auth import get_current_admin
from app.models.admin_user import AdminUser
from app.models.category import Category
from app.schemas.category import (
    CategoryCreate,
    CategoryItem,
    CategoryListResponse,
    CategoryUpdate,
)
from app.utils.response import success, error

router = APIRouter(prefix="/api/v1/admin/categories", tags=["管理后台-分类"])


@router.get("")
async def list_categories(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Category).order_by(Category.id.desc()))
    categories = result.scalars().all()
    items = [CategoryItem.model_validate(c) for c in categories]
    return success({"items": items})


@router.post("")
async def create_category(
    req: CategoryCreate,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(select(Category).where(Category.code == req.code))
    if existing.scalar_one_or_none():
        return error(1301, "分类标识码已存在")

    api_key = f"kg_{secrets.token_hex(32)}"
    category = Category(
        name=req.name,
        code=req.code,
        score_per_key=req.score_per_key,
        score_label=req.score_label,
        max_activations=req.max_activations,
        expiry_days=req.expiry_days,
        api_key=api_key,
    )
    db.add(category)
    await db.flush()
    await db.refresh(category)
    return success(CategoryItem.model_validate(category))


@router.put("/{category_id}")
async def update_category(
    category_id: int,
    req: CategoryUpdate,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        return error(1302, "分类不存在")

    if req.name is not None:
        category.name = req.name
    if req.score_per_key is not None:
        category.score_per_key = req.score_per_key
    if req.score_label is not None:
        category.score_label = req.score_label
    if req.max_activations is not None:
        category.max_activations = req.max_activations
    if req.expiry_days is not None:
        category.expiry_days = req.expiry_days

    await db.flush()
    await db.refresh(category)
    return success(CategoryItem.model_validate(category))


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        return error(1302, "分类不存在")

    # Check if category has activation keys
    from app.models.activation_key import ActivationKey
    key_count = await db.execute(
        select(ActivationKey).where(ActivationKey.category_id == category_id).limit(1)
    )
    if key_count.scalar_one_or_none():
        return error(1303, "该分类下存在激活码，无法删除")

    await db.delete(category)
    return success(None)
```

- [ ] **Step 3: Register routers in main.py**

```python
# backend/app/main.py - add after api_keys router
from app.routers import admin_auth, admin_categories

app.include_router(admin_auth.router)
app.include_router(admin_categories.router)
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/routers/admin_auth.py backend/app/routers/admin_categories.py backend/app/main.py
git commit -m "feat: admin auth and category management routes"
```

---

### Task 9: B端 Admin Keys, Stats, Logs Routes

**Files:**
- Create: `backend/app/routers/admin_keys.py`
- Create: `backend/app/routers/admin_stats.py`
- Create: `backend/app/routers/admin_usage_logs.py`
- Create: `backend/app/routers/admin_audit.py`
- Create: `backend/app/services/stats_service.py`
- Modify: `backend/app/main.py` (register routers)

- [ ] **Step 1: Implement admin keys routes**

```python
# backend/app/routers/admin_keys.py
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.jwt_auth import get_current_admin
from app.models.activation_key import ActivationKey
from app.models.activation_log import ActivationLog
from app.models.admin_user import AdminUser
from app.models.category import Category
from app.schemas.key import (
    KeyGenerateRequest,
    KeyGenerateResponse,
    KeyItem,
    KeySearchRequest,
    KeySearchResponse,
)
from app.services.key_service import generate_keys
from app.utils.response import success, error

router = APIRouter(prefix="/api/v1/admin/keys", tags=["管理后台-激活码"])


@router.post("/generate")
async def generate(
    req: KeyGenerateRequest,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Category).where(Category.id == req.category_id))
    category = result.scalar_one_or_none()
    if not category:
        return error(1302, "分类不存在")

    if req.count < 1 or req.count > 10000:
        return error(1401, "生成数量需在 1-10000 之间")

    batch_id, codes = await generate_keys(db, category, req.count, req.batch_id)
    return success({"batch_id": batch_id, "count": len(codes), "keys": codes})


@router.post("/search")
async def search_keys(
    req: KeySearchRequest,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(
        ActivationKey.id,
        ActivationKey.key_code,
        Category.name.label("category_name"),
        ActivationKey.status,
        ActivationKey.total_score,
        ActivationKey.remaining_score,
        ActivationKey.batch_id,
        ActivationKey.activated_at,
        ActivationKey.expires_at,
        ActivationKey.created_at,
    ).join(Category, ActivationKey.category_id == Category.id)

    if req.category_id:
        query = query.where(ActivationKey.category_id == req.category_id)
    if req.status:
        query = query.where(ActivationKey.status == req.status)
    if req.batch_id:
        query = query.where(ActivationKey.batch_id == req.batch_id)
    if req.key_code:
        query = query.where(ActivationKey.key_code.contains(req.key_code))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    offset = (req.page - 1) * req.page_size
    query = query.order_by(ActivationKey.id.desc()).offset(offset).limit(req.page_size)
    result = await db.execute(query)
    rows = result.all()

    items = [
        KeyItem(
            id=row.id,
            key_code=row.key_code,
            category_name=row.category_name,
            status=row.status,
            total_score=row.total_score,
            remaining_score=row.remaining_score,
            batch_id=row.batch_id,
            activated_at=row.activated_at,
            expires_at=row.expires_at,
            created_at=row.created_at,
        )
        for row in rows
    ]

    return success({"total": total, "page": req.page, "page_size": req.page_size, "items": items})


@router.put("/{key_id}/disable")
async def disable_key(
    key_id: int,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ActivationKey).where(ActivationKey.id == key_id))
    key = result.scalar_one_or_none()
    if not key:
        return error(1001, "激活码不存在")

    key.status = "disabled"
    return success(None)
```

- [ ] **Step 2: Implement stats service**

```python
# backend/app/services/stats_service.py
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activation_key import ActivationKey
from app.models.activation_log import ActivationLog
from app.models.category import Category


async def get_overview(db: AsyncSession) -> dict:
    total_result = await db.execute(select(func.count(ActivationKey.id)))
    total_keys = total_result.scalar() or 0

    activated_result = await db.execute(
        select(func.count(ActivationKey.id)).where(ActivationKey.status == "activated")
    )
    activated_keys = activated_result.scalar() or 0

    consumed_result = await db.execute(
        select(func.sum(ActivationLog.amount)).where(ActivationLog.action == "deduct")
    )
    total_score_consumed = consumed_result.scalar() or 0

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_result = await db.execute(
        select(func.count(ActivationLog.id))
        .where(ActivationLog.action == "activate")
        .where(ActivationLog.created_at >= today_start)
    )
    today_activations = today_result.scalar() or 0

    return {
        "total_keys": total_keys,
        "activated_keys": activated_keys,
        "total_score_consumed": total_score_consumed,
        "today_activations": today_activations,
    }


async def get_category_stats(db: AsyncSession, category_id: int) -> dict:
    cat_result = await db.execute(select(Category).where(Category.id == category_id))
    category = cat_result.scalar_one_or_none()
    if not category:
        raise Exception("分类不存在")

    total_result = await db.execute(
        select(func.count(ActivationKey.id)).where(ActivationKey.category_id == category_id)
    )
    total_keys = total_result.scalar() or 0

    activated_result = await db.execute(
        select(func.count(ActivationKey.id))
        .where(ActivationKey.category_id == category_id)
        .where(ActivationKey.status == "activated")
    )
    activated_keys = activated_result.scalar() or 0

    total_score_result = await db.execute(
        select(func.sum(ActivationKey.total_score)).where(ActivationKey.category_id == category_id)
    )
    total_score = total_score_result.scalar() or 0

    consumed_result = await db.execute(
        select(func.sum(ActivationLog.amount))
        .where(ActivationLog.category_id == category_id)
        .where(ActivationLog.action == "deduct")
    )
    consumed_score = consumed_result.scalar() or 0

    # 7-day trend
    trend = []
    for i in range(6, -1, -1):
        day_start = (datetime.now(timezone.utc) - timedelta(days=i)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        day_end = day_start + timedelta(days=1)
        count_result = await db.execute(
            select(func.count(ActivationLog.id))
            .where(ActivationLog.category_id == category_id)
            .where(ActivationLog.action == "activate")
            .where(ActivationLog.created_at >= day_start)
            .where(ActivationLog.created_at < day_end)
        )
        trend.append({"date": day_start.strftime("%Y-%m-%d"), "count": count_result.scalar() or 0})

    return {
        "category_id": category_id,
        "category_name": category.name,
        "total_keys": total_keys,
        "activated_keys": activated_keys,
        "total_score": total_score,
        "consumed_score": consumed_score,
        "activation_trend": trend,
    }
```

- [ ] **Step 3: Implement stats routes**

```python
# backend/app/routers/admin_stats.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.jwt_auth import get_current_admin
from app.models.admin_user import AdminUser
from app.services.stats_service import get_overview, get_category_stats
from app.utils.response import success, error

router = APIRouter(prefix="/api/v1/admin/stats", tags=["管理后台-统计"])


@router.get("")
async def overview(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await get_overview(db)
    return success(result)


@router.get("/category/{category_id}")
async def category_stats(
    category_id: int,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await get_category_stats(db, category_id)
        return success(result)
    except Exception as e:
        return error(1302, str(e))
```

- [ ] **Step 4: Implement usage logs route**

```python
# backend/app/routers/admin_usage_logs.py
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.jwt_auth import get_current_admin
from app.models.activation_key import ActivationKey
from app.models.activation_log import ActivationLog
from app.models.admin_user import AdminUser
from app.models.category import Category
from app.schemas.key import UsageLogItem, UsageLogSearchRequest, UsageLogSearchResponse
from app.utils.response import success

router = APIRouter(prefix="/api/v1/admin/usage-logs", tags=["管理后台-使用日志"])


@router.post("/search")
async def search_usage_logs(
    req: UsageLogSearchRequest,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(
            ActivationLog.id,
            ActivationKey.key_code,
            Category.name.label("category_name"),
            ActivationLog.action,
            ActivationLog.amount,
            ActivationLog.remaining_after,
            ActivationLog.metadata_.label("metadata"),
            ActivationLog.client_ip,
            ActivationLog.created_at,
        )
        .join(ActivationKey, ActivationLog.key_id == ActivationKey.id)
        .join(Category, ActivationLog.category_id == Category.id)
    )

    if req.key_code:
        query = query.where(ActivationKey.key_code.contains(req.key_code))
    if req.category_id:
        query = query.where(ActivationLog.category_id == req.category_id)
    if req.action:
        query = query.where(ActivationLog.action == req.action)
    if req.start_time:
        query = query.where(ActivationLog.created_at >= req.start_time)
    if req.end_time:
        query = query.where(ActivationLog.created_at <= req.end_time)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (req.page - 1) * req.page_size
    query = query.order_by(ActivationLog.id.desc()).offset(offset).limit(req.page_size)
    result = await db.execute(query)
    rows = result.all()

    items = [
        UsageLogItem(
            id=row.id,
            key_code=row.key_code,
            category_name=row.category_name,
            action=row.action,
            amount=row.amount,
            remaining_after=row.remaining_after,
            metadata=row.metadata,
            client_ip=row.client_ip,
            created_at=row.created_at,
        )
        for row in rows
    ]

    return success({"total": total, "page": req.page, "page_size": req.page_size, "items": items})
```

- [ ] **Step 5: Implement audit logs route**

```python
# backend/app/routers/admin_audit.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.jwt_auth import get_current_admin
from app.models.admin_user import AdminUser
from app.models.audit_log import AuditLog
from app.schemas.admin import AuditLogItem, AuditLogListResponse
from app.utils.response import success

router = APIRouter(prefix="/api/v1/admin/audit-logs", tags=["管理后台-审计日志"])


@router.get("")
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(AuditLog, AdminUser.username.label("admin_username"))
        .join(AdminUser, AuditLog.admin_id == AdminUser.id)
    )

    count_query = select(func.count()).select_from(AuditLog.__table__)
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * page_size
    query = query.order_by(AuditLog.id.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    rows = result.all()

    items = [
        AuditLogItem(
            id=row.AuditLog.id,
            admin_username=row.admin_username,
            action=row.AuditLog.action,
            target_type=row.AuditLog.target_type,
            target_id=row.AuditLog.target_id,
            detail=row.AuditLog.detail,
            created_at=row.AuditLog.created_at.isoformat(),
        )
        for row in rows
    ]

    return success({"total": total, "page": page, "page_size": page_size, "items": items})
```

- [ ] **Step 6: Register all routers in main.py**

```python
# backend/app/main.py - final version
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import engine, Base
from app.routers import api_keys, admin_auth, admin_categories, admin_keys, admin_stats, admin_usage_logs, admin_audit


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="Keygen Platform", version="1.0.0", lifespan=lifespan)

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
```

- [ ] **Step 7: Commit**

```bash
git add backend/app/routers/admin_keys.py backend/app/routers/admin_stats.py backend/app/routers/admin_usage_logs.py backend/app/routers/admin_audit.py backend/app/services/stats_service.py backend/app/main.py
git commit -m "feat: admin keys, stats, usage logs, and audit routes"
```

---

### Task 10: Admin Default User Initialization

**Files:**
- Modify: `backend/app/main.py` (add init admin on startup)

- [ ] **Step 1: Add admin initialization to lifespan**

```python
# Add to backend/app/main.py lifespan function
from app.config import settings
from app.middleware.jwt_auth import get_password_hash
from app.models.admin_user import AdminUser


@asynccontextmanager
async def lifespan(app: FastAPI):
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
    await engine.dispose()
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/main.py
git commit -m "feat: auto-create default admin user on startup"
```

---

### Task 11: Frontend Scaffolding

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/index.html`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/router/index.ts`
- Create: `frontend/src/stores/auth.ts`
- Create: `frontend/src/api/request.ts`
- Create: `frontend/Dockerfile`
- Create: `frontend/nginx.conf`

- [ ] **Step 1: Create frontend/package.json**

```json
{
  "name": "keygen-platform-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.3.0",
    "pinia": "^2.2.0",
    "element-plus": "^2.8.0",
    "axios": "^1.7.0",
    "@element-plus/icons-vue": "^2.3.0",
    "echarts": "^5.5.0",
    "vue-echarts": "^7.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.1.0",
    "typescript": "^5.5.0",
    "vite": "^5.4.0",
    "vue-tsc": "^2.1.0"
  }
}
```

- [ ] **Step 2: Create frontend/vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 3: Create frontend/tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

- [ ] **Step 4: Create frontend/index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Keygen Platform</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

- [ ] **Step 5: Create frontend/src/main.ts**

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
```

- [ ] **Step 6: Create frontend/src/App.vue**

```vue
<template>
  <router-view />
</template>
```

- [ ] **Step 7: Create frontend/src/router/index.ts**

```typescript
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue'),
    },
    {
      path: '/',
      component: () => import('../views/Layout.vue'),
      redirect: '/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('../views/Dashboard.vue'),
          meta: { title: '数据看板' },
        },
        {
          path: 'categories',
          name: 'Categories',
          component: () => import('../views/Categories.vue'),
          meta: { title: '分类管理' },
        },
        {
          path: 'keys',
          name: 'Keys',
          component: () => import('../views/Keys.vue'),
          meta: { title: '激活码管理' },
        },
        {
          path: 'usage-logs',
          name: 'UsageLogs',
          component: () => import('../views/UsageLogs.vue'),
          meta: { title: '使用日志' },
        },
        {
          path: 'audit-logs',
          name: 'AuditLogs',
          component: () => import('../views/AuditLogs.vue'),
          meta: { title: '审计日志' },
        },
      ],
    },
  ],
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  if (to.path !== '/login' && !authStore.token) {
    next('/login')
  } else {
    next()
  }
})

export default router
```

- [ ] **Step 8: Create frontend/src/stores/auth.ts**

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')

  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  function logout() {
    token.value = ''
    localStorage.removeItem('token')
  }

  return { token, setToken, logout }
})
```

- [ ] **Step 9: Create frontend/src/api/request.ts**

```typescript
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
})

request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => {
    const data = response.data
    if (data.code !== 0) {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(data)
    }
    return data
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      router.push('/login')
    }
    ElMessage.error(error.message || '网络错误')
    return Promise.reject(error)
  }
)

export default request
```

- [ ] **Step 10: Create frontend/Dockerfile**

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
```

- [ ] **Step 11: Create frontend/nginx.conf**

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

- [ ] **Step 12: Commit**

```bash
git add frontend/
git commit -m "feat: Vue3 frontend scaffolding with router, store, and API layer"
```

---

### Task 12: Frontend - Login & Layout Pages

**Files:**
- Create: `frontend/src/views/Login.vue`
- Create: `frontend/src/views/Layout.vue`

- [ ] **Step 1: Create Login.vue**

```vue
<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2 class="login-title">Keygen Platform</h2>
      <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" style="width: 100%" @click="handleLogin">
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import request from '../api/request'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  await formRef.value?.validate()
  loading.value = true
  try {
    const res: any = await request.post('/admin/login', form)
    authStore.setToken(res.data.token)
    router.push('/')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  width: 400px;
  padding: 20px;
}
.login-title {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
}
</style>
```

- [ ] **Step 2: Create Layout.vue**

```vue
<template>
  <el-container style="min-height: 100vh">
    <el-aside width="220px" style="background: #304156">
      <div style="padding: 20px; text-align: center; color: #fff; font-size: 18px; font-weight: bold">
        Keygen Platform
      </div>
      <el-menu
        :default-active="route.path"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据看板</span>
        </el-menu-item>
        <el-menu-item index="/categories">
          <el-icon><Folder /></el-icon>
          <span>分类管理</span>
        </el-menu-item>
        <el-menu-item index="/keys">
          <el-icon><Key /></el-icon>
          <span>激活码管理</span>
        </el-menu-item>
        <el-menu-item index="/usage-logs">
          <el-icon><Document /></el-icon>
          <span>使用日志</span>
        </el-menu-item>
        <el-menu-item index="/audit-logs">
          <el-icon><Notebook /></el-icon>
          <span>审计日志</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="display: flex; align-items: center; justify-content: flex-end; border-bottom: 1px solid #e6e6e6">
        <el-dropdown @command="handleLogout">
          <span style="cursor: pointer">
            <el-icon><User /></el-icon>
            管理员
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

function handleLogout(command: string) {
  if (command === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}
</script>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/Login.vue frontend/src/views/Layout.vue
git commit -m "feat: login and layout pages"
```

---

### Task 13: Frontend - Dashboard & Categories Pages

**Files:**
- Create: `frontend/src/api/stats.ts`
- Create: `frontend/src/api/categories.ts`
- Create: `frontend/src/views/Dashboard.vue`
- Create: `frontend/src/views/Categories.vue`

- [ ] **Step 1: Create API modules**

```typescript
// frontend/src/api/stats.ts
import request from './request'

export function getStatsOverview() {
  return request.get('/admin/stats')
}

export function getCategoryStats(categoryId: number) {
  return request.get(`/admin/stats/category/${categoryId}`)
}
```

```typescript
// frontend/src/api/categories.ts
import request from './request'

export function getCategories() {
  return request.get('/admin/categories')
}

export function createCategory(data: any) {
  return request.post('/admin/categories', data)
}

export function updateCategory(id: number, data: any) {
  return request.put(`/admin/categories/${id}`, data)
}

export function deleteCategory(id: number) {
  return request.delete(`/admin/categories/${id}`)
}
```

- [ ] **Step 2: Create Dashboard.vue**

```vue
<template>
  <div>
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>总激活码数</template>
          <div class="stat-value">{{ overview.total_keys }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>已激活数</template>
          <div class="stat-value">{{ overview.activated_keys }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>总 Score 消耗</template>
          <div class="stat-value">{{ overview.total_score_consumed }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>今日激活</template>
          <div class="stat-value">{{ overview.today_activations }}</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getStatsOverview } from '../api/stats'

const overview = ref({
  total_keys: 0,
  activated_keys: 0,
  total_score_consumed: 0,
  today_activations: 0,
})

onMounted(async () => {
  const res: any = await getStatsOverview()
  overview.value = res.data
})
</script>

<style scoped>
.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  text-align: center;
}
</style>
```

- [ ] **Step 3: Create Categories.vue**

```vue
<template>
  <div>
    <el-button type="primary" @click="showCreate" style="margin-bottom: 16px">
      新增分类
    </el-button>

    <el-table :data="categories" border stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="code" label="标识码" />
      <el-table-column prop="score_per_key" label="Score 值" width="100" />
      <el-table-column prop="score_label" label="Score 标签" width="100" />
      <el-table-column label="API Key" min-width="200">
        <template #default="{ row }">
          <el-text truncated>{{ row.api_key }}</el-text>
          <el-button link type="primary" @click="copyApiKey(row.api_key)">复制</el-button>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button link type="primary" @click="showEdit(row)">编辑</el-button>
          <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button link type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑分类' : '新增分类'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="标识码" prop="code">
          <el-input v-model="form.code" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="Score 值" prop="score_per_key">
          <el-input-number v-model="form.score_per_key" :min="1" />
        </el-form-item>
        <el-form-item label="Score 标签" prop="score_label">
          <el-input v-model="form.score_label" />
        </el-form-item>
        <el-form-item label="有效期天数">
          <el-input-number v-model="form.expiry_days" :min="0" placeholder="留空为永久" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getCategories, createCategory, updateCategory, deleteCategory } from '../api/categories'

const categories = ref<any[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(0)
const formRef = ref()

const form = reactive({
  name: '',
  code: '',
  score_per_key: 100,
  score_label: '积分',
  expiry_days: null as number | null,
})

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入标识码', trigger: 'blur' }],
  score_per_key: [{ required: true, message: '请输入 Score 值', trigger: 'blur' }],
}

async function loadCategories() {
  const res: any = await getCategories()
  categories.value = res.data.items
}

function showCreate() {
  isEdit.value = false
  Object.assign(form, { name: '', code: '', score_per_key: 100, score_label: '积分', expiry_days: null })
  dialogVisible.value = true
}

function showEdit(row: any) {
  isEdit.value = true
  editId.value = row.id
  Object.assign(form, {
    name: row.name,
    code: row.code,
    score_per_key: row.score_per_key,
    score_label: row.score_label,
    expiry_days: row.expiry_days,
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value?.validate()
  if (isEdit.value) {
    await updateCategory(editId.value, form)
  } else {
    await createCategory(form)
  }
  ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
  dialogVisible.value = false
  loadCategories()
}

async function handleDelete(id: number) {
  await deleteCategory(id)
  ElMessage.success('删除成功')
  loadCategories()
}

function copyApiKey(key: string) {
  navigator.clipboard.writeText(key)
  ElMessage.success('已复制')
}

onMounted(loadCategories)
</script>
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/api/stats.ts frontend/src/api/categories.ts frontend/src/views/Dashboard.vue frontend/src/views/Categories.vue
git commit -m "feat: dashboard and categories management pages"
```

---

### Task 14: Frontend - Keys, UsageLogs, AuditLogs Pages

**Files:**
- Create: `frontend/src/api/keys.ts`
- Create: `frontend/src/api/usageLogs.ts`
- Create: `frontend/src/api/auditLogs.ts`
- Create: `frontend/src/views/Keys.vue`
- Create: `frontend/src/views/UsageLogs.vue`
- Create: `frontend/src/views/AuditLogs.vue`
- Create: `frontend/src/utils/format.ts`

- [ ] **Step 1: Create API modules**

```typescript
// frontend/src/api/keys.ts
import request from './request'

export function searchKeys(data: any) {
  return request.post('/admin/keys/search', data)
}

export function generateKeys(data: any) {
  return request.post('/admin/keys/generate', data)
}

export function disableKey(id: number) {
  return request.put(`/admin/keys/${id}/disable`)
}
```

```typescript
// frontend/src/api/usageLogs.ts
import request from './request'

export function searchUsageLogs(data: any) {
  return request.post('/admin/usage-logs/search', data)
}
```

```typescript
// frontend/src/api/auditLogs.ts
import request from './request'

export function getAuditLogs(params: any) {
  return request.get('/admin/audit-logs', { params })
}
```

```typescript
// frontend/src/utils/format.ts
export function formatDateTime(iso: string | null): string {
  if (!iso) return '-'
  return new Date(iso).toLocaleString('zh-CN')
}

export function statusLabel(status: string): string {
  const map: Record<string, string> = {
    unused: '未使用',
    activated: '已激活',
    expired: '已过期',
    disabled: '已禁用',
  }
  return map[status] || status
}

export function statusType(status: string): string {
  const map: Record<string, string> = {
    unused: 'info',
    activated: 'success',
    expired: 'warning',
    disabled: 'danger',
  }
  return map[status] || 'info'
}
```

- [ ] **Step 2: Create Keys.vue**

```vue
<template>
  <div>
    <el-form :inline="true" style="margin-bottom: 16px">
      <el-form-item label="分类">
        <el-select v-model="searchForm.category_id" clearable placeholder="全部" style="width: 160px">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="searchForm.status" clearable placeholder="全部" style="width: 120px">
          <el-option label="未使用" value="unused" />
          <el-option label="已激活" value="activated" />
          <el-option label="已过期" value="expired" />
          <el-option label="已禁用" value="disabled" />
        </el-select>
      </el-form-item>
      <el-form-item label="Key Code">
        <el-input v-model="searchForm.key_code" placeholder="搜索" clearable style="width: 200px" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="loadKeys">搜索</el-button>
        <el-button type="success" @click="showGenerate">批量生成</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="keys" border stripe>
      <el-table-column prop="key_code" label="Key Code" width="200" />
      <el-table-column prop="category_name" label="分类" width="120" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="total_score" label="初始 Score" width="100" />
      <el-table-column prop="remaining_score" label="剩余 Score" width="100" />
      <el-table-column prop="batch_id" label="批次" width="150" />
      <el-table-column label="激活时间" width="180">
        <template #default="{ row }">{{ formatDateTime(row.activated_at) }}</template>
      </el-table-column>
      <el-table-column label="过期时间" width="180">
        <template #default="{ row }">{{ formatDateTime(row.expires_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-popconfirm title="确定禁用？" @confirm="handleDisable(row.id)">
            <template #reference>
              <el-button link type="danger" :disabled="row.status !== 'unused'">禁用</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      style="margin-top: 16px; justify-content: flex-end"
      v-model:current-page="searchForm.page"
      v-model:page-size="searchForm.page_size"
      :total="total"
      :page-sizes="[20, 50, 100]"
      layout="total, sizes, prev, pager, next"
      @current-change="loadKeys"
      @size-change="loadKeys"
    />

    <el-dialog v-model="generateDialogVisible" title="批量生成激活码" width="400px">
      <el-form :model="generateForm" label-width="80px">
        <el-form-item label="分类">
          <el-select v-model="generateForm.category_id" style="width: 100%">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="数量">
          <el-input-number v-model="generateForm.count" :min="1" :max="10000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="批次号">
          <el-input v-model="generateForm.batch_id" placeholder="留空自动生成" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="generateDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleGenerate">生成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { searchKeys, generateKeys, disableKey } from '../api/keys'
import { getCategories } from '../api/categories'
import { formatDateTime, statusLabel, statusType } from '../utils/format'

const keys = ref<any[]>([])
const categories = ref<any[]>([])
const total = ref(0)
const generateDialogVisible = ref(false)

const searchForm = reactive({
  category_id: null as number | null,
  status: null as string | null,
  key_code: '',
  page: 1,
  page_size: 20,
})

const generateForm = reactive({
  category_id: null as number | null,
  count: 100,
  batch_id: '',
})

async function loadCategories() {
  const res: any = await getCategories()
  categories.value = res.data.items
}

async function loadKeys() {
  const res: any = await searchKeys(searchForm)
  keys.value = res.data.items
  total.value = res.data.total
}

function showGenerate() {
  generateForm.category_id = null
  generateForm.count = 100
  generateForm.batch_id = ''
  generateDialogVisible.value = true
}

async function handleGenerate() {
  if (!generateForm.category_id) {
    ElMessage.warning('请选择分类')
    return
  }
  const res: any = await generateKeys(generateForm)
  ElMessage.success(`成功生成 ${res.data.count} 个激活码`)
  generateDialogVisible.value = false
  loadKeys()
}

async function handleDisable(id: number) {
  await disableKey(id)
  ElMessage.success('已禁用')
  loadKeys()
}

onMounted(() => {
  loadCategories()
  loadKeys()
})
</script>
```

- [ ] **Step 3: Create UsageLogs.vue**

```vue
<template>
  <div>
    <el-form :inline="true" style="margin-bottom: 16px">
      <el-form-item label="Key Code">
        <el-input v-model="searchForm.key_code" placeholder="搜索" clearable style="width: 200px" />
      </el-form-item>
      <el-form-item label="分类">
        <el-select v-model="searchForm.category_id" clearable placeholder="全部" style="width: 160px">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="操作类型">
        <el-select v-model="searchForm.action" clearable placeholder="全部" style="width: 120px">
          <el-option label="激活" value="activate" />
          <el-option label="扣减" value="deduct" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="loadLogs">搜索</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="logs" border stripe>
      <el-table-column prop="key_code" label="Key Code" width="200" />
      <el-table-column prop="category_name" label="分类" width="120" />
      <el-table-column label="操作" width="80">
        <template #default="{ row }">
          <el-tag :type="row.action === 'activate' ? 'success' : 'warning'">
            {{ row.action === 'activate' ? '激活' : '扣减' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="amount" label="Score 数量" width="100" />
      <el-table-column prop="remaining_after" label="操作后剩余" width="100" />
      <el-table-column label="上报数据" min-width="200">
        <template #default="{ row }">
          <el-popover v-if="row.metadata && Object.keys(row.metadata).length" trigger="hover" width="300">
            <template #reference>
              <el-button link type="primary">查看</el-button>
            </template>
            <div v-for="(v, k) in row.metadata" :key="k" style="margin-bottom: 4px">
              <strong>{{ k }}:</strong> {{ v }}
            </div>
          </el-popover>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="client_ip" label="IP" width="140" />
      <el-table-column label="时间" width="180">
        <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
      </el-table-column>
    </el-table>

    <el-pagination
      style="margin-top: 16px; justify-content: flex-end"
      v-model:current-page="searchForm.page"
      v-model:page-size="searchForm.page_size"
      :total="total"
      :page-sizes="[20, 50, 100]"
      layout="total, sizes, prev, pager, next"
      @current-change="loadLogs"
      @size-change="loadLogs"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { searchUsageLogs } from '../api/usageLogs'
import { getCategories } from '../api/categories'
import { formatDateTime } from '../utils/format'

const logs = ref<any[]>([])
const categories = ref<any[]>([])
const total = ref(0)

const searchForm = reactive({
  key_code: '',
  category_id: null as number | null,
  action: null as string | null,
  page: 1,
  page_size: 20,
})

async function loadCategories() {
  const res: any = await getCategories()
  categories.value = res.data.items
}

async function loadLogs() {
  const res: any = await searchUsageLogs(searchForm)
  logs.value = res.data.items
  total.value = res.data.total
}

onMounted(() => {
  loadCategories()
  loadLogs()
})
</script>
```

- [ ] **Step 4: Create AuditLogs.vue**

```vue
<template>
  <div>
    <el-table :data="logs" border stripe>
      <el-table-column prop="admin_username" label="操作人" width="120" />
      <el-table-column prop="action" label="操作" width="160" />
      <el-table-column prop="target_type" label="目标类型" width="120" />
      <el-table-column prop="target_id" label="目标 ID" width="100" />
      <el-table-column label="详情" min-width="200">
        <template #default="{ row }">
          <el-text truncated>{{ row.detail ? JSON.stringify(row.detail) : '-' }}</el-text>
        </template>
      </el-table-column>
      <el-table-column label="时间" width="180">
        <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
      </el-table-column>
    </el-table>

    <el-pagination
      style="margin-top: 16px; justify-content: flex-end"
      v-model:current-page="page"
      v-model:page-size="pageSize"
      :total="total"
      :page-sizes="[20, 50, 100]"
      layout="total, sizes, prev, pager, next"
      @current-change="loadLogs"
      @size-change="loadLogs"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getAuditLogs } from '../api/auditLogs'
import { formatDateTime } from '../utils/format'

const logs = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

async function loadLogs() {
  const res: any = await getAuditLogs({ page: page.value, page_size: pageSize.value })
  logs.value = res.data.items
  total.value = res.data.total
}

onMounted(loadLogs)
</script>
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/api/keys.ts frontend/src/api/usageLogs.ts frontend/src/api/auditLogs.ts frontend/src/utils/format.ts frontend/src/views/Keys.vue frontend/src/views/UsageLogs.vue frontend/src/views/AuditLogs.vue
git commit -m "feat: keys management, usage logs, and audit logs pages"
```

---

### Task 15: Integration Testing & Docker Verification

**Files:**
- Modify: `backend/app/main.py` (finalize)
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_api_keys.py`

- [ ] **Step 1: Create test conftest.py**

```python
# backend/tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
```

- [ ] **Step 2: Write health check test**

```python
# backend/tests/test_api_keys.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
```

- [ ] **Step 3: Start Docker and verify**

```bash
# Copy .env.example to .env
cp .env.example .env

# Start all services
docker compose up -d

# Check all services are running
docker compose ps

# Test health endpoint
curl http://localhost:8000/api/v1/health

# Test frontend
curl http://localhost:80
```

- [ ] **Step 4: Commit**

```bash
git add backend/tests/ .env.example
git commit -m "test: integration tests and Docker verification"
```

---

### Task 16: Final Polish & Documentation

**Files:**
- Create: `.env.example` (update with final values)
- Modify: `docker-compose.yml` (finalize)
- Create: `README.md`

- [ ] **Step 1: Create README.md**

```markdown
# Keygen Platform

通用激活码生成与管理服务平台。

## 功能

- 激活码批量生成（分段式格式：XXXX-XXXX-XXXX-XXXX）
- 激活码校验与激活
- Score 积分管理（发放、扣减、查询）
- 多分类/渠道管理
- 数据看板与统计
- 操作日志与审计

## 快速开始

```bash
# 复制环境变量
cp .env.example .env

# 修改 .env 中的密码和密钥
# MYSQL_PASSWORD, JWT_SECRET_KEY, ADMIN_DEFAULT_PASSWORD

# 启动服务
docker compose up -d

# 访问
# 前端管理后台: http://localhost
# 后端 API: http://localhost:8000
# 默认管理员: admin / admin123
```

## API 文档

启动后访问: http://localhost:8000/docs

## 技术栈

- 后端: Python FastAPI + SQLAlchemy + Alembic
- 前端: Vue3 + Element Plus + Pinia
- 数据库: MySQL 8.0
- 缓存: Redis 7
- 部署: Docker Compose + Nginx
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with setup instructions"
```
