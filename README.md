<div align="center">

# Keygen Platform

**Universal Redemption Code Generation & Management Service**

English | [中文](README.zh-CN.md)

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A production-ready platform for generating, verifying, and managing redemption codes with built-in credit management, multi-product support, and real-time analytics.

[Quick Start](#quick-start) | [API Reference](#api-reference) | [Architecture](#architecture) | [Deployment](#deployment) | [Configuration](#configuration)

</div>

---

## Features

- **Redemption Code Management** — Batch generate segmented codes (`XXXX-XXXX-XXXX-XXXX`) with configurable credits and expiry
- **Code Verification & Redemption** — Validate and redeem codes via REST API with atomic operations
- **Credit System** — Consume, query, and manage credits with Redis-backed atomic counters
- **Multi-Product Support** — Isolate products via API keys, each with its own configuration
- **Real-Time Analytics** — Dashboard with overview stats, 7-day trends, and per-product breakdowns
- **Audit Trail** — Full operation logging and admin audit history
- **Dual Authentication** — API Key for service integration, JWT for admin portal
- **High Performance** — Redis caching with distributed locks for concurrent-safe credit consumption
- **One-Click Deploy** — Docker Compose with Nginx reverse proxy

## Architecture

```
                            ┌─────────────────┐
                            │   Nginx :80     │
                            │  Reverse Proxy  │
                            └────┬───────┬────┘
                                 │       │
                    ┌────────────┘       └────────────┐
                    ▼                                 ▼
           ┌────────────────┐               ┌────────────────┐
           │  Vue3 Admin    │               │  FastAPI :8000 │
           │  (Static SPA)  │               │  (Async API)   │
           └────────────────┘               └───┬────────┬───┘
                                                │        │
                                    ┌───────────┘        └───────────┐
                                    ▼                                ▼
                            ┌──────────────┐                ┌──────────────┐
                            │  MySQL 8.0   │                │  Redis 7     │
                            │  Persistence │                │  Cache/Lock  │
                            └──────────────┘                └──────────────┘
```

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Vue 3 + TypeScript + Element Plus | Admin dashboard SPA |
| Backend | FastAPI + SQLAlchemy (async) | High-performance REST API |
| Database | MySQL 8.0 | Persistent storage |
| Cache | Redis 7 | Credit cache, distributed locks |
| Proxy | Nginx | Static serving + API routing |
| Deploy | Docker Compose | Container orchestration |

## Quick Start

### Prerequisites

- Docker & Docker Compose v2
- Git

### Installation

```bash
# Clone the repository
git clone git@github.com:ayermac/keygen-platform.git
cd keygen-platform

# Configure environment
cp .env.example .env
# Edit .env — change MYSQL_PASSWORD, JWT_SECRET_KEY, ADMIN_DEFAULT_PASSWORD

# Launch all services
docker compose up -d
```

### Access

| Service | URL | Credentials |
|---------|-----|-------------|
| Admin Dashboard | http://localhost | `admin` / `admin123` |
| API Server | http://localhost:8000 | — |
| Swagger Docs | http://localhost:8000/docs | — |
| ReDoc | http://localhost:8000/redoc | — |

## API Documentation

| Type | URL | Description |
|------|-----|-------------|
| Web API Docs | [/docs/api](http://localhost/docs/api) | Interactive documentation page (no auth required) |
| Agent-Friendly | [/api/v1/agent-docs](http://localhost/api/v1/agent-docs) | Plain text API docs for AI agents |
| Swagger UI | [:8000/docs](http://localhost:8000/docs) | Auto-generated OpenAPI docs |
| ReDoc | [:8000/redoc](http://localhost:8000/redoc) | Alternative OpenAPI docs |

## API Reference

### Authentication

**C-End (Service Integration)** — Pass API key in request header:

```http
X-API-Key: <your-product-api-key>
```

**B-End (Admin)** — JWT bearer token after login:

```http
Authorization: Bearer <jwt-token>
```

### C-End Endpoints

> All C-End endpoints use `POST` to avoid sensitive data exposure in URLs.

#### Redeem Code

```http
POST /api/v1/codes/redeem
Content-Type: application/json
X-API-Key: <key>

{
  "code": "A1B2-C3D4-E5F6-G7H8",
  "metadata": {
    "username": "user123",
    "channel": "mobile",
    "user_agent": "Mozilla/5.0 ..."
  }
}
```

**Response:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "code": "A1B2-C3D4-E5F6-G7H8",
    "credit_unit": "credits",
    "total_credits": 100,
    "remaining_credits": 100,
    "expires_at": "2026-06-09T00:00:00"
  }
}
```

#### Consume Credits

```http
POST /api/v1/codes/consume
X-API-Key: <key>

{
  "code": "A1B2-C3D4-E5F6-G7H8",
  "amount": 10,
  "metadata": {
    "order_id": "ORD-20260509",
    "description": "Purchase item X"
  }
}
```

#### Query Balance

```http
POST /api/v1/codes/balance
X-API-Key: <key>

{
  "code": "A1B2-C3D4-E5F6-G7H8"
}
```

### B-End Admin Endpoints

<details>
<summary><strong>Authentication</strong></summary>

```http
POST /api/v1/admin/login

{ "username": "admin", "password": "admin123" }
```

</details>

<details>
<summary><strong>Product Management</strong></summary>

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/admin/products` | List all products |
| `POST` | `/api/v1/admin/products` | Create product |
| `PUT` | `/api/v1/admin/products/{id}` | Update product |
| `DELETE` | `/api/v1/admin/products/{id}` | Delete product |

</details>

<details>
<summary><strong>Code Management</strong></summary>

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/admin/codes/generate` | Batch generate codes |
| `GET` | `/api/v1/admin/codes` | List codes (filterable) |
| `PUT` | `/api/v1/admin/codes/{id}/disable` | Disable a code |

</details>

<details>
<summary><strong>Analytics & Logs</strong></summary>

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/admin/stats/overview` | Dashboard overview |
| `GET` | `/api/v1/admin/stats/product/{id}` | Per-product stats with 7-day trend |
| `GET` | `/api/v1/admin/usage-logs` | Usage logs (filterable) |
| `GET` | `/api/v1/admin/audit-logs` | Admin audit trail |

</details>

## Data Model

### Product

| Field | Type | Description |
|-------|------|-------------|
| `name` | VARCHAR(100) | Display name |
| `code` | VARCHAR(50) | Unique identifier |
| `default_credits` | INT | Default credits per code |
| `credit_unit` | VARCHAR(50) | Unit label (e.g. "credits", "points") |
| `expiry_days` | INT | Days until expiry after redemption (NULL = never) |
| `api_key` | VARCHAR(64) | Unique API key for this product |

### Redemption Code

| Field | Type | Description |
|-------|------|-------------|
| `code` | VARCHAR(19) | `XXXX-XXXX-XXXX-XXXX` format |
| `product_id` | FK | Reference to product |
| `status` | ENUM | `unused` / `activated` / `expired` / `disabled` |
| `batch_id` | VARCHAR(50) | Batch identifier |
| `total_credits` | INT | Initial credits (from product config) |
| `remaining_credits` | INT | Current remaining credits |
| `expires_at` | DATETIME | Expiry timestamp (lazy evaluation) |
| `metadata` | JSON | Extensible custom data |

## Configuration

All configuration is via environment variables. Copy `.env.example` to `.env`:

```bash
# MySQL
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=keygen
MYSQL_PASSWORD=change_me_in_production    # IMPORTANT: Change in production
MYSQL_DATABASE=keygen

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# JWT
JWT_SECRET_KEY=change_me_in_production    # IMPORTANT: Use openssl rand -hex 32
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=480

# Admin
ADMIN_DEFAULT_USERNAME=admin
ADMIN_DEFAULT_PASSWORD=admin123           # IMPORTANT: Change in production

# App
APP_ENV=development
APP_DEBUG=true
```

## Deployment

### Production Deploy (Recommended)

```bash
# One-command deploy with backup, health check, and status report
./scripts/deploy.sh

# Skip database backup
./scripts/deploy.sh --skip-backup

# Skip health check
./scripts/deploy.sh --skip-health
```

The deploy script will:
1. Verify `.env` is configured (not default secrets)
2. Backup MySQL database to `backups/`
3. Pull latest code from `main`
4. Build and restart all containers
5. Wait for health check to pass
6. Print service URLs

### Manual Docker Compose

```bash
# Production deployment
docker compose up -d --build

# View logs
docker compose logs -f backend

# Stop all services
docker compose down

# Stop and remove volumes (destroys data)
docker compose down -v
```

### Services

| Service | Internal Port | External Port | Description |
|---------|--------------|---------------|-------------|
| nginx | 80 | 80 | Reverse proxy |
| frontend | — | — | Build output served by Nginx |
| backend | 8000 | 8000 | FastAPI server |
| mysql | 3306 | 3306 | Database |
| redis | 6379 | 6379 | Cache |

## Project Structure

```
keygen-platform/
├── backend/
│   ├── app/
│   │   ├── models/              # SQLAlchemy ORM models
│   │   │   ├── product.py
│   │   │   ├── redemption_code.py
│   │   │   ├── usage_log.py
│   │   │   ├── admin_user.py
│   │   │   └── audit_log.py
│   │   ├── schemas/             # Pydantic validation models
│   │   │   ├── code.py
│   │   │   ├── product.py
│   │   │   └── admin.py
│   │   ├── routers/             # API route handlers
│   │   │   ├── client_codes.py  # C-End: redeem, consume, balance
│   │   │   ├── admin_auth.py    # B-End: login
│   │   │   ├── admin_products.py
│   │   │   ├── admin_codes.py
│   │   │   ├── admin_stats.py
│   │   │   ├── admin_usage_logs.py
│   │   │   └── admin_audit.py
│   │   ├── services/            # Business logic
│   │   │   ├── code_service.py  # Core: redeem, consume, balance, generate
│   │   │   └── stats_service.py # Dashboard analytics
│   │   ├── middleware/          # Authentication
│   │   │   ├── api_key_auth.py  # X-API-Key validation
│   │   │   └── jwt_auth.py      # JWT + bcrypt
│   │   ├── utils/               # Utilities
│   │   │   ├── key_generator.py # Code generation (XXXX-XXXX-XXXX-XXXX)
│   │   │   ├── response.py      # Standardized API responses
│   │   │   └── audit.py         # Audit log writer
│   │   ├── exceptions.py        # Business exception hierarchy
│   │   ├── config.py            # Pydantic Settings
│   │   ├── database.py          # Async SQLAlchemy engine
│   │   ├── redis_client.py      # Async Redis client
│   │   └── main.py              # FastAPI app entry
│   ├── alembic/                 # Database migrations
│   │   ├── versions/            # Migration scripts
│   │   └── env.py               # Async-aware Alembic config
│   ├── alembic.ini
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/                 # Axios API layer
│   │   │   ├── products.ts
│   │   │   ├── codes.ts
│   │   │   ├── stats.ts
│   │   │   ├── usageLogs.ts
│   │   │   ├── auditLogs.ts
│   │   │   └── request.ts
│   │   ├── router/              # Vue Router with auth guard
│   │   ├── stores/              # Pinia state management
│   │   ├── utils/               # Formatting helpers
│   │   └── views/               # Page components
│   │       ├── Login.vue
│   │       ├── Layout.vue
│   │       ├── Dashboard.vue
│   │       ├── Products.vue
│   │       ├── Codes.vue
│   │       ├── UsageLogs.vue
│   │       ├── AuditLogs.vue
│   │       └── ApiDocs.vue
│   ├── Dockerfile
│   └── nginx.conf
├── docs/
│   └── superpowers/
│       ├── specs/               # Design specification
│       └── plans/               # Implementation plan
├── docker-compose.yml
├── .env.example
└── .gitignore
```

## Database Migrations

Uses Alembic for schema migrations:

```bash
# Generate a new migration after model changes
cd backend
alembic revision --autogenerate -m "description"

# Apply pending migrations
alembic upgrade head

# Rollback one revision
alembic downgrade -1
```

The initial migration captures the full schema. Always generate a new migration after changing models.

## Security

| Feature | Description |
|---------|-------------|
| **Startup validation** | Refuses to start if `JWT_SECRET_KEY`, `MYSQL_PASSWORD`, or `ADMIN_DEFAULT_PASSWORD` are defaults in production |
| **Login rate limiting** | 5 attempts per IP per 60s window via Redis counter |
| **API key rotation** | `POST /api/v1/admin/products/{id}/rotate-key` invalidates old key and all related Redis caches |
| **Redis Lua atomic consume** | Credit deduction uses a Lua script to prevent race conditions |
| **Audit logging** | All admin mutations (create/update/delete product, generate/disable codes, login) are recorded |
| **Nginx security headers** | `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `Referrer-Policy` |
| **Request ID tracing** | Every request gets a `X-Request-ID` header for log correlation |

## Error Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
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

## Development

### Local Setup (without Docker)

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
cd backend
pytest tests/ -v
```

## License

[MIT](LICENSE)

---

<div align="center">

**Built with FastAPI + Vue3**

</div>
