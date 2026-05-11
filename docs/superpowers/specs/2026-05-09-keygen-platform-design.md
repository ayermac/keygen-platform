# Keygen Platform Design

> 通用兑换码生成与管理服务平台

## 定位

通用兑换码服务平台，核心能力：**生成兑换码**、**校验兑换**、**额度消耗**。通过产品区分不同业务渠道，提供标准化 API 供业务方集成。面向个人使用起步，架构支持未来多租户扩展。

## 当前状态与路线图

截至 2026-05-11，项目已完成从 MVP 到生产预发布级别的基础加固：

- 后端测试、前端构建、Docker 生产配置和 Alembic 迁移链路已建立。
- C 端兑换/消费接口已使用业务异常体系、稳定错误码和 Redis Lua 原子扣减。
- B 端已具备登录限流、API Key 轮换、审计日志、Request ID、结构化日志和 readiness 健康检查。
- 生产环境启动会拒绝明显不安全的默认密钥/密码配置。

后续功能演进以版本计划文档为准：

- [2026-05-11-keygen-platform-version-roadmap.md](../plans/2026-05-11-keygen-platform-version-roadmap.md)

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端 | Python FastAPI | 高性能异步框架 |
| 前端 | Vue3 + Element Plus | 管理后台 |
| 数据库 | MySQL 8.0 | 持久化存储 |
| 缓存 | Redis 7 | C 端接口加速 |
| 部署 | Docker Compose | 容器化部署 |
| 反向代理 | Nginx | 前端静态文件 + API 转发 |

## 架构方案

前后端独立部署，Docker Compose 编排：

```
┌──────────────────────────────────────┐
│           Nginx (反向代理)             │
├──────────────────┬───────────────────┤
│   Vue3 Admin     │    FastAPI API    │
│   (Node 容器)    │   (Python 容器)   │
├──────────────────┴───────────────────┤
│       MySQL          │     Redis      │
└──────────────────────┴───────────────┘
```

Nginx 路由规则：
- `/` → 前端静态文件
- `/api/*` → 转发到 FastAPI 后端

## 认证机制

- **C 端接口**：API Key 认证，每个产品分配一个 API Key，请求头携带 `X-API-Key`
- **B 端管理接口**：JWT 认证，管理员登录后获取 token

## 兑换码格式

分段式：`XXXX-XXXX-XXXX-XXXX`（大写字母+数字，19 字符含分隔符）

## 数据模型

### product（产品/渠道）

```
id              BIGINT PK AUTO_INCREMENT
name            VARCHAR(100)     -- 产品名称，如 "A业务额度卡"
code            VARCHAR(50) UNIQUE -- 产品标识码
default_credits INT NOT NULL     -- 每个兑换码的默认额度
credit_unit     VARCHAR(50)      -- 额度单位标签，如 "积分"、"次数"
expiry_days     INT              -- 兑换后有效期天数，NULL=永不过期
api_key         VARCHAR(64) UNIQUE -- 该产品的 API Key
created_at      DATETIME
updated_at      DATETIME
```

### redemption_code（兑换码）

```
id              BIGINT PK AUTO_INCREMENT
code            VARCHAR(19) UNIQUE -- XXXX-XXXX-XXXX-XXXX
product_id      BIGINT FK → product
status          ENUM('unused','activated','expired','disabled')
batch_id        VARCHAR(50)      -- 批次号，用于批量管理
total_credits   INT              -- 初始额度（冗余自 product）
remaining_credits INT            -- 剩余额度
activated_at    DATETIME
expires_at      DATETIME         -- 兑换后计算的过期时间
created_at      DATETIME
metadata        JSON             -- 扩展字段，预留
```

### usage_log（兑换码使用日志）

```
id              BIGINT PK AUTO_INCREMENT
code_id         BIGINT FK → redemption_code
product_id      BIGINT FK → product
action          ENUM('redeem','consume')
amount          INT              -- 操作的额度数量
remaining_after INT              -- 操作后剩余额度
metadata        JSON             -- 业务方自定义上报数据（UA、用户名等）
client_ip       VARCHAR(45)
created_at      DATETIME
```

### admin_user（管理员）

```
id              BIGINT PK AUTO_INCREMENT
username        VARCHAR(50) UNIQUE
password_hash   VARCHAR(128)
created_at      DATETIME
```

### audit_log（操作审计）

```
id              BIGINT PK AUTO_INCREMENT
admin_id        BIGINT FK → admin_user
action          VARCHAR(50)      -- 如 "create_category", "batch_generate"
target_type     VARCHAR(50)      -- 如 "category", "activation_key"
target_id       BIGINT
detail          JSON
created_at      DATETIME
```

## API 接口设计

### 统一响应格式

```json
// 成功
{
  "code": 0,
  "message": "success",
  "data": { ... }
}

// 失败
{
  "code": 1001,
  "message": "兑换码不存在",
  "data": null
}
```

错误码规划：

| 范围 | 含义 |
|------|------|
| 0 | 成功 |
| 1001-1099 | 兑换码相关错误（不存在、已兑换、已过期、已禁用） |
| 1101-1199 | 额度相关错误（余额不足、消耗失败） |
| 1201-1299 | 认证相关错误（API Key 无效、JWT 过期） |
| 1301-1399 | 产品相关错误（产品不存在、名称重复） |
| 9999 | 未知错误 |

### C 端接口（API Key 认证）

所有 C 端接口统一为 POST + JSON body，敏感数据不出现在 URL 中。

#### POST /api/v1/codes/redeem

兑换兑换码，返回额度信息。

```json
// 请求
// Header: X-API-Key: <product_api_key>
{
  "code": "A1B2-C3D4-E5F6-G7H8",
  "metadata": {
    "username": "张三",
    "user_id": "10086",
    "user_agent": "Mozilla/5.0 ...",
    "channel": "mobile"
  }
}

// 响应
{
  "code": 0,
  "message": "success",
  "data": {
    "code": "A1B2-C3D4-E5F6-G7H8",
    "credit_unit": "积分",
    "total_credits": 100,
    "remaining_credits": 100,
    "expires_at": "2026-06-09T00:00:00"
  }
}
```

#### POST /api/v1/codes/consume

消耗额度，加分布式锁保证并发安全。

```json
// 请求
{
  "code": "A1B2-C3D4-E5F6-G7H8",
  "amount": 10,
  "metadata": {
    "username": "张三",
    "description": "购买商品A"
  }
}

// 响应
{
  "code": 0,
  "data": {
    "remaining_credits": 90
  }
}
```

#### POST /api/v1/codes/balance

查询剩余额度。

```json
// 请求
{
  "code": "A1B2-C3D4-E5F6-G7H8"
}
```

### B 端管理接口（JWT 认证）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/admin/login` | 管理员登录，返回 JWT |
| GET | `/api/v1/admin/products` | 产品列表 |
| POST | `/api/v1/admin/products` | 创建产品 |
| PUT | `/api/v1/admin/products/{id}` | 更新产品 |
| DELETE | `/api/v1/admin/products/{id}` | 删除产品 |
| POST | `/api/v1/admin/codes/generate` | 批量生成兑换码 |
| GET | `/api/v1/admin/codes` | 兑换码列表（支持筛选） |
| PUT | `/api/v1/admin/codes/{id}/disable` | 禁用兑换码 |
| GET | `/api/v1/admin/stats/overview` | 统计概览 |
| GET | `/api/v1/admin/stats/product/{id}` | 产品维度统计 |
| GET | `/api/v1/admin/usage-logs` | 使用日志查询 |
| GET | `/api/v1/admin/audit-logs` | 审计日志 |

## C 端性能与缓存策略

### Redis 缓存结构

```
code:{code} → Hash
  ├── status: "activated"
  ├── total_credits: 100
  ├── remaining_credits: 90
  ├── expires_at: "2026-06-09T00:00:00"
  └── product_id: 1
TTL: 30min，过期自动清除，下次访问从 MySQL 回填
```

### 校验流程

```
请求进入
  │
  ├─ 校验 API Key（Redis 缓存 product 信息）
  │
  ├─ 查询兑换码状态
  │   ├─ 优先查 Redis Hash: code:{code}
  │   ├─ 未命中 → 查 MySQL → 回写 Redis（TTL 30min）
  │   └─ 已命中 → 直接使用缓存数据
  │
  ├─ 过期判断：查询时判断 expires_at < NOW() 即失效，状态懒更新
  │
  ├─ 操作处理
  │   ├─ redeem: 写 MySQL → 写 Redis Hash
  │   ├─ consume: Redis 分布式锁 + HINCRBY 原子消耗 → 异步写 MySQL
  │   └─ balance: 直接读 Redis Hash
  │
  └─ 返回结果
```

### 消耗并发安全

```python
# 1. 加分布式锁（Redis SETNX，TTL 防死锁）
lock_key = f"lock:code:{code}"
acquired = SET lock_key 1 NX EX 5
if not acquired:
    return error("系统繁忙，请稍后重试")

try:
    # 2. 检查余额
    remaining = HGET code:{code} remaining_credits
    if remaining < amount:
        return error("余额不足")

    # 3. 原子消耗
    new_remaining = HINCRBY code:{code} remaining_credits -{amount}

    # 4. 异步写 MySQL
    async_save_to_mysql(code, amount, new_remaining)

    return { "remaining_credits": new_remaining }
finally:
    # 5. 释放锁
    DEL lock_key
```

锁粒度为单个 code，不同兑换码之间不互斥。锁 TTL 5 秒，防止异常时死锁。

## 管理后台页面

### 登录页 `/login`
- 单管理员账号密码登录
- JWT 存 localStorage，过期自动跳转登录

### 数据看板 `/dashboard`
- 总览卡片：总兑换码数、已兑换数、总额度消耗量、今日兑换数
- 图表：近 7 天/30 天兑换趋势折线图
- 各产品额度消耗占比饼图
- 最近兑换记录列表

### 产品管理 `/products`
- 产品列表表格：名称、标识码、默认额度、额度单位、API Key、创建时间
- 操作：新增、编辑、删除（删除前校验是否有关联兑换码）
- API Key 支持一键复制

### 兑换码管理 `/codes`
- 搜索筛选：按产品、状态、批次号、兑换码搜索
- 表格展示：兑换码、产品、状态、初始/剩余额度、兑换时间、过期时间
- 操作：批量生成（选产品 + 数量 + 批次号）、禁用单个、查看日志、导出
- 批量生成后支持导出为 CSV/JSON

### 兑换码使用日志 `/usage-logs`
- 搜索筛选：按兑换码、产品、操作类型（兑换/消耗）、时间范围
- 表格展示：兑换码、产品、操作类型、额度数量、操作后剩余、上报数据、客户端 IP、时间
- 上报数据列点击展开显示 metadata 的 key-value 列表
- 点击兑换码可查看该兑换码的完整操作时间线

### 审计日志 `/audit-logs`
- 时间线展示：谁、什么时间、对什么做了什么操作
- 支持按操作类型、时间范围筛选

## 后端目录结构

```
keygen-platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 入口
│   │   ├── config.py            # 配置（环境变量）
│   │   ├── database.py          # MySQL 连接（SQLAlchemy）
│   │   ├── redis_client.py      # Redis 连接
│   │   ├── models/              # 数据模型
│   │   │   ├── product.py
│   │   │   ├── redemption_code.py
│   │   │   ├── usage_log.py
│   │   │   ├── admin_user.py
│   │   │   └── audit_log.py
│   │   ├── schemas/             # Pydantic 请求/响应模型
│   │   │   ├── code.py
│   │   │   ├── product.py
│   │   │   └── admin.py
│   │   ├── routers/             # 路由
│   │   │   ├── client_codes.py  # C 端接口
│   │   │   ├── admin_auth.py    # 登录
│   │   │   ├── admin_products.py
│   │   │   ├── admin_codes.py
│   │   │   ├── admin_stats.py
│   │   │   ├── admin_usage_logs.py
│   │   │   └── admin_audit.py
│   │   ├── services/            # 业务逻辑
│   │   │   ├── code_service.py
│   │   │   └── stats_service.py
│   │   ├── middleware/          # 中间件
│   │   │   ├── api_key_auth.py  # API Key 认证
│   │   │   ├── jwt_auth.py      # JWT 认证
│   │   │   └── audit.py         # 审计日志
│   │   └── utils/
│   │       ├── key_generator.py # 兑换码生成算法
│   │       └── response.py      # 统一响应格式
│   ├── alembic/                 # 数据库迁移
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── Login.vue
│   │   │   ├── Layout.vue
│   │   │   ├── Dashboard.vue
│   │   │   ├── Products.vue
│   │   │   ├── Keys.vue
│   │   │   ├── UsageLogs.vue
│   │   │   ├── AuditLogs.vue
│   │   │   └── ApiDocs.vue
│   │   ├── components/
│   │   ├── api/
│   │   ├── router/
│   │   ├── stores/
│   │   └── utils/
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── .env.example
```

## Docker Compose 服务

| 服务 | 镜像 | 端口 | 说明 |
|------|------|------|------|
| nginx | nginx:alpine | 80 | 反向代理 + 静态文件 |
| frontend | node:18 (构建阶段) | - | Vue3 构建后由 nginx 托管 |
| backend | python:3.12 | 8000 | FastAPI + Uvicorn |
| mysql | mysql:8.0 | 3306 | 数据库 |
| redis | redis:7 | 6379 | 缓存 |

## 设计决策

| 决策 | 理由 |
|------|------|
| 过期判断懒更新，不用定时任务 | 查询时判断 expires_at 即可，简单可靠 |
| Redis Hash 存兑换码缓存 | 支持 HINCRBY 原子消耗，结构清晰 |
| 消耗加分布式锁 | 防止检查余额和消耗之间的竞态条件 |
| C 端接口全 POST | 敏感数据不出现在 URL 中 |
| metadata 可扩展 | 业务方自定义字段，平台不约束 |
| 前后端独立部署 | 独立扩展，独立更新，职责清晰 |
