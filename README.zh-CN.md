<div align="center">

# Keygen Platform

**通用激活码生成与管理服务平台**

[English](README.md) | 中文

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

生产级激活码生成、校验与管理平台，内置积分系统、多渠道支持和实时数据分析。

[快速开始](#快速开始) | [API 文档](#api-文档) | [系统架构](#系统架构) | [部署指南](#部署指南) | [配置说明](#配置说明)

</div>

---

## 功能特性

- **激活码管理** — 批量生成分段式激活码（`XXXX-XXXX-XXXX-XXXX`），支持配置积分和有效期
- **校验与激活** — 通过 REST API 校验并激活激活码，操作原子化
- **积分系统** — 基于 Redis 原子计数器的积分扣减、查询与管理
- **多渠道隔离** — 通过分类隔离不同业务渠道，每个分类独立 API Key 和配置
- **实时数据分析** — 管理看板，包含总览统计、7 日趋势和分类维度分析
- **审计追踪** — 完整的操作日志和管理员审计记录
- **双模认证** — C端业务使用 API Key 鉴权，B端管理后台使用 JWT 认证
- **高性能** — Redis 缓存 + 分布式锁，支持并发安全的积分扣减
- **一键部署** — Docker Compose + Nginx 反向代理

## 系统架构

```
                            ┌─────────────────┐
                            │   Nginx :80     │
                            │   反向代理       │
                            └────┬───────┬────┘
                                 │       │
                    ┌────────────┘       └────────────┐
                    ▼                                 ▼
           ┌────────────────┐               ┌────────────────┐
           │  Vue3 管理后台  │               │  FastAPI :8000 │
           │  (静态 SPA)    │               │  (异步 API)    │
           └────────────────┘               └───┬────────┬───┘
                                                │        │
                                    ┌───────────┘        └───────────┐
                                    ▼                                ▼
                            ┌──────────────┐                ┌──────────────┐
                            │  MySQL 8.0   │                │  Redis 7     │
                            │  持久化存储   │                │  缓存/分布式锁│
                            └──────────────┘                └──────────────┘
```

| 层级 | 技术 | 用途 |
|------|------|------|
| 前端 | Vue 3 + TypeScript + Element Plus | 管理后台 SPA |
| 后端 | FastAPI + SQLAlchemy (异步) | 高性能 REST API |
| 数据库 | MySQL 8.0 | 持久化存储 |
| 缓存 | Redis 7 | 积分缓存、分布式锁 |
| 代理 | Nginx | 静态文件服务 + API 路由 |
| 部署 | Docker Compose | 容器编排 |

## 快速开始

### 环境要求

- Docker & Docker Compose v2
- Git

### 安装步骤

```bash
# 克隆仓库
git clone git@github.com:ayermac/keygen-platform.git
cd keygen-platform

# 配置环境变量
cp .env.example .env
# 编辑 .env，修改 MYSQL_PASSWORD、JWT_SECRET_KEY、ADMIN_DEFAULT_PASSWORD

# 启动所有服务
docker compose up -d
```

### 访问地址

| 服务 | 地址 | 账号密码 |
|------|------|----------|
| 管理后台 | http://localhost | `admin` / `admin123` |
| API 服务 | http://localhost:8000 | — |
| Swagger 文档 | http://localhost:8000/docs | — |
| ReDoc 文档 | http://localhost:8000/redoc | — |

## API 文档

### 认证方式

**C端接口（业务集成）** — 请求头携带 API Key：

```http
X-API-Key: <分类的 API Key>
```

**B端管理接口（管理员）** — 登录后获取 JWT Token：

```http
Authorization: Bearer <jwt-token>
```

### C端接口

> 所有 C端接口均使用 `POST` 方法，避免敏感数据暴露在 URL 中。

#### 激活码激活

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

**响应示例：**

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
      "name": "游戏积分卡",
      "score_label": "积分"
    }
  }
}
```

#### 积分扣减

```http
POST /api/v1/keys/deduct
X-API-Key: <key>

{
  "key_code": "A1B2-C3D4-E5F6-G7H8",
  "amount": 10,
  "metadata": {
    "order_id": "ORD-20260509",
    "description": "购买道具 X"
  }
}
```

#### 查询余额

```http
POST /api/v1/keys/balance
X-API-Key: <key>

{
  "key_code": "A1B2-C3D4-E5F6-G7H8"
}
```

### B端管理接口

<details>
<summary><strong>认证</strong></summary>

```http
POST /api/v1/admin/login

{ "username": "admin", "password": "admin123" }
```

</details>

<details>
<summary><strong>分类管理</strong></summary>

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/admin/categories` | 获取分类列表 |
| `POST` | `/api/v1/admin/categories` | 创建分类 |
| `PUT` | `/api/v1/admin/categories/{id}` | 更新分类 |
| `DELETE` | `/api/v1/admin/categories/{id}` | 删除分类 |

</details>

<details>
<summary><strong>激活码管理</strong></summary>

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/v1/admin/keys/generate` | 批量生成激活码 |
| `GET` | `/api/v1/admin/keys` | 激活码列表（支持筛选） |
| `GET` | `/api/v1/admin/keys/{id}` | 激活码详情 |

</details>

<details>
<summary><strong>统计与日志</strong></summary>

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/admin/stats/overview` | 数据总览 |
| `GET` | `/api/v1/admin/stats/categories` | 分类统计（含 7 日趋势） |
| `GET` | `/api/v1/admin/usage-logs` | 使用日志（支持筛选） |
| `GET` | `/api/v1/admin/audit-logs` | 管理员审计日志 |

</details>

## 数据模型

### 分类（Category）

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | VARCHAR(100) | 分类名称 |
| `code` | VARCHAR(50) | 唯一标识码 |
| `score_per_key` | INT | 每个激活码的积分值 |
| `score_label` | VARCHAR(50) | 积分标签（如"积分"、"次数"） |
| `max_activations` | INT | 单码最大激活次数（1 = 一次性） |
| `expiry_days` | INT | 激活后有效天数（NULL = 永不过期） |
| `api_key` | VARCHAR(64) | 该分类的唯一 API Key |

### 激活码（Activation Key）

| 字段 | 类型 | 说明 |
|------|------|------|
| `key_code` | VARCHAR(19) | `XXXX-XXXX-XXXX-XXXX` 格式 |
| `category_id` | FK | 关联分类 |
| `status` | ENUM | `unused` / `activated` / `expired` / `disabled` |
| `batch_id` | VARCHAR(50) | 批次号 |
| `total_score` | INT | 初始积分（来自分类配置） |
| `remaining_score` | INT | 当前剩余积分 |
| `expires_at` | DATETIME | 过期时间（懒加载判断） |
| `metadata` | JSON | 扩展字段 |

## 配置说明

所有配置通过环境变量管理，复制 `.env.example` 为 `.env`：

```bash
# MySQL
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=keygen
MYSQL_PASSWORD=change_me_in_production    # 重要：生产环境必须修改
MYSQL_DATABASE=keygen

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# JWT
JWT_SECRET_KEY=change_me_in_production    # 重要：使用 openssl rand -hex 32 生成
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=480

# 管理员
ADMIN_DEFAULT_USERNAME=admin
ADMIN_DEFAULT_PASSWORD=admin123           # 重要：生产环境必须修改

# 应用
APP_ENV=development
APP_DEBUG=true
```

## 部署指南

### Docker Compose（推荐）

```bash
# 生产部署
docker compose up -d --build

# 查看日志
docker compose logs -f backend

# 停止所有服务
docker compose down

# 停止并删除数据卷（会丢失数据）
docker compose down -v
```

### 服务列表

| 服务 | 内部端口 | 外部端口 | 说明 |
|------|----------|----------|------|
| nginx | 80 | 80 | 反向代理 |
| frontend | — | — | 构建产物由 Nginx 托管 |
| backend | 8000 | 8000 | FastAPI 服务 |
| mysql | 3306 | 3306 | 数据库 |
| redis | 6379 | 6379 | 缓存 |

## 项目结构

```
keygen-platform/
├── backend/
│   ├── app/
│   │   ├── models/              # SQLAlchemy ORM 模型
│   │   │   ├── category.py
│   │   │   ├── activation_key.py
│   │   │   ├── activation_log.py
│   │   │   ├── admin_user.py
│   │   │   └── audit_log.py
│   │   ├── schemas/             # Pydantic 请求/响应模型
│   │   │   ├── key.py
│   │   │   ├── category.py
│   │   │   └── admin.py
│   │   ├── routers/             # API 路由处理器
│   │   │   ├── api_keys.py      # C端：激活、扣减、余额
│   │   │   ├── admin_auth.py    # B端：登录
│   │   │   ├── admin_categories.py
│   │   │   ├── admin_keys.py
│   │   │   ├── admin_stats.py
│   │   │   ├── admin_usage_logs.py
│   │   │   └── admin_audit.py
│   │   ├── services/            # 业务逻辑层
│   │   │   ├── key_service.py   # 核心：激活、扣减、余额、生成
│   │   │   └── stats_service.py # 看板数据分析
│   │   ├── middleware/          # 认证中间件
│   │   │   ├── api_key_auth.py  # X-API-Key 校验
│   │   │   └── jwt_auth.py      # JWT + bcrypt
│   │   ├── utils/               # 工具函数
│   │   │   ├── key_generator.py # 激活码生成（XXXX-XXXX-XXXX-XXXX）
│   │   │   └── response.py      # 统一 API 响应格式
│   │   ├── config.py            # Pydantic Settings 配置
│   │   ├── database.py          # 异步 SQLAlchemy 引擎
│   │   ├── redis_client.py      # 异步 Redis 客户端
│   │   └── main.py              # FastAPI 应用入口
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/                 # Axios API 封装层
│   │   ├── router/              # Vue Router（含路由守卫）
│   │   ├── stores/              # Pinia 状态管理
│   │   ├── utils/               # 格式化工具
│   │   └── views/               # 页面组件
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
│       ├── specs/               # 设计文档
│       └── plans/               # 实施计划
├── docker-compose.yml
├── .env.example
└── .gitignore
```

## 本地开发

### 不使用 Docker

```bash
# 后端
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 前端
cd frontend
npm install
npm run dev
```

### 运行测试

```bash
cd backend
pytest tests/ -v
```

## 开源协议

[MIT](LICENSE)

---

<div align="center">

**使用 FastAPI + Vue3 构建**

</div>
