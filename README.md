<div align="center">

# Keygen Platform

**Universal Activation Code Generation & Management Service**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A production-ready platform for generating, verifying, and managing activation codes with built-in score management, multi-channel support, and real-time analytics.

[Quick Start](#quick-start) | [API Reference](#api-reference) | [Architecture](#architecture) | [Deployment](#deployment) | [Configuration](#configuration)

</div>

---

## Features

- **Activation Code Management** — Batch generate segmented codes (`XXXX-XXXX-XXXX-XXXX`) with configurable score and expiry
- **Code Verification & Activation** — Validate and activate codes via REST API with atomic operations
- **Score System** — Deduct, query, and manage scores with Redis-backed atomic counters
- **Multi-Channel Support** — Isolate business channels via categories, each with its own API key and configuration
- **Real-Time Analytics** — Dashboard with overview stats, 7-day trends, and per-category breakdowns
- **Audit Trail** — Full operation logging and admin audit history
- **Dual Authentication** — API Key for service integration, JWT for admin portal
- **High Performance** — Redis caching with distributed locks for concurrent-safe score deduction
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
| Cache | Redis 7 | Score cache, distributed locks |
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

## API Reference

### Authentication

**C-End (Service Integration)** — Pass API key in request header:

```http
X-API-Key: <your-category-api-key>
```

**B-End (Admin)** — JWT bearer token after login:

```http
Authorization: Bearer <jwt-token>
```

### C-End Endpoints

> All C-End endpoints use `POST` to avoid sensitive data exposure in URLs.

#### Activate Code

```http
POST /api/v1/keys/activate
Content-Type: application/json
X-API-Key: <key>

{
  "key_code": "A1B2-C3D4-E5F6-G7H8",
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
  "success": true,
  "data": {
    "key_code": "A1B2-C3D4-E5F6-G7H8",
    "total_score": 100,
    "remaining_score": 100,
    "expires_at": "2026-06-09T00:00:00",
    "category": {
      "id": 1,
      "name": "Game Credits",
      "score_label": "credits"
    }
  }
}
```

#### Deduct Score

```http
POST /api/v1/keys/deduct
X-API-Key: <key>

{
  "key_code": "A1B2-C3D4-E5F6-G7H8",
  "amount": 10,
  "metadata": {
    "order_id": "ORD-20260509",
    "description": "Purchase item X"
  }
}
```

#### Query Balance

```http
POST /api/v1/keys/balance
X-API-Key: <key>

{
  "key_code": "A1B2-C3D4-E5F6-G7H8"
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
<summary><strong>Category Management</strong></summary>

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/admin/categories` | List all categories |
| `POST` | `/api/v1/admin/categories` | Create category |
| `PUT` | `/api/v1/admin/categories/{id}` | Update category |
| `DELETE` | `/api/v1/admin/categories/{id}` | Delete category |

</details>

<details>
<summary><strong>Key Management</strong></summary>

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/admin/keys/generate` | Batch generate codes |
| `GET` | `/api/v1/admin/keys` | List codes (filterable) |
| `GET` | `/api/v1/admin/keys/{id}` | Code detail |

</details>

<details>
<summary><strong>Analytics & Logs</strong></summary>

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/admin/stats/overview` | Dashboard overview |
| `GET` | `/api/v1/admin/stats/categories` | Per-category stats with 7-day trend |
| `GET` | `/api/v1/admin/usage-logs` | Usage logs (filterable) |
| `GET` | `/api/v1/admin/audit-logs` | Admin audit trail |

</details>

## Data Model

### Category

| Field | Type | Description |
|-------|------|-------------|
| `name` | VARCHAR(100) | Display name |
| `code` | VARCHAR(50) | Unique identifier |
| `score_per_key` | INT | Score value per code |
| `score_label` | VARCHAR(50) | Label (e.g. "credits", "points") |
| `max_activations` | INT | Max activations per code (1 = one-time) |
| `expiry_days` | INT | Days until expiry after activation (NULL = never) |
| `api_key` | VARCHAR(64) | Unique API key for this category |

### Activation Key

| Field | Type | Description |
|-------|------|-------------|
| `key_code` | VARCHAR(19) | `XXXX-XXXX-XXXX-XXXX` format |
| `category_id` | FK | Reference to category |
| `status` | ENUM | `unused` / `activated` / `expired` / `disabled` |
| `batch_id` | VARCHAR(50) | Batch identifier |
| `total_score` | INT | Initial score (from category) |
| `remaining_score` | INT | Current remaining score |
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

### Docker Compose (Recommended)

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
│   │   │   ├── category.py
│   │   │   ├── activation_key.py
│   │   │   ├── activation_log.py
│   │   │   ├── admin_user.py
│   │   │   └── audit_log.py
│   │   ├── schemas/             # Pydantic validation models
│   │   │   ├── key.py
│   │   │   ├── category.py
│   │   │   └── admin.py
│   │   ├── routers/             # API route handlers
│   │   │   ├── api_keys.py      # C-End: activate, deduct, balance
│   │   │   ├── admin_auth.py    # B-End: login
│   │   │   ├── admin_categories.py
│   │   │   ├── admin_keys.py
│   │   │   ├── admin_stats.py
│   │   │   ├── admin_usage_logs.py
│   │   │   └── admin_audit.py
│   │   ├── services/            # Business logic
│   │   │   ├── key_service.py   # Core: activate, deduct, balance, generate
│   │   │   └── stats_service.py # Dashboard analytics
│   │   ├── middleware/          # Authentication
│   │   │   ├── api_key_auth.py  # X-API-Key validation
│   │   │   └── jwt_auth.py      # JWT + bcrypt
│   │   ├── utils/               # Utilities
│   │   │   ├── key_generator.py # Code generation (XXXX-XXXX-XXXX-XXXX)
│   │   │   └── response.py      # Standardized API responses
│   │   ├── config.py            # Pydantic Settings
│   │   ├── database.py          # Async SQLAlchemy engine
│   │   ├── redis_client.py      # Async Redis client
│   │   └── main.py              # FastAPI app entry
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/                 # Axios API layer
│   │   ├── router/              # Vue Router with auth guard
│   │   ├── stores/              # Pinia state management
│   │   ├── utils/               # Formatting helpers
│   │   └── views/               # Page components
│   │       ├── Login.vue
│   │       ├── Layout.vue
│   │       ├── Dashboard.vue
│   │       ├── Categories.vue
│   │       ├── Keys.vue
│   │       ├── UsageLogs.vue
│   │       └── AuditLogs.vue
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
