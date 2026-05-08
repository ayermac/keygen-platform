# Keygen Platform Design

> 通用激活码生成与管理服务平台

## 定位

通用激活码服务平台，核心能力：**生成激活码**、**校验激活**、**score 扣减**。通过分类区分不同业务渠道，提供标准化 API 供业务方集成。面向个人使用起步，架构支持未来多租户扩展。

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

- **C 端接口**：API Key 认证，每个分类分配一个 API Key，请求头携带 `X-API-Key`
- **B 端管理接口**：JWT 认证，管理员登录后获取 token

## 激活码格式

分段式：`XXXX-XXXX-XXXX-XXXX`（大写字母+数字，19 字符含分隔符）

## 数据模型

### category（分类/渠道）

```
id              BIGINT PK AUTO_INCREMENT
name            VARCHAR(100)     -- 分类名称，如 "A业务积分卡"
code            VARCHAR(50) UNIQUE -- 分类标识码
score_per_key   INT NOT NULL     -- 每个激活码的 score 值
score_label     VARCHAR(50)      -- score 含义标签，如 "积分"、"次数"
max_activations INT DEFAULT 1    -- 单码最大激活次数（1=一次性）
expiry_days     INT              -- 激活后有效期天数，NULL=永不过期
api_key         VARCHAR(64) UNIQUE -- 该分类的 API Key
created_at      DATETIME
updated_at      DATETIME
```

### activation_key（激活码）

```
id              BIGINT PK AUTO_INCREMENT
key_code        VARCHAR(19) UNIQUE -- XXXX-XXXX-XXXX-XXXX
category_id     BIGINT FK → category
status          ENUM('unused','activated','expired','disabled')
batch_id        VARCHAR(50)      -- 批次号，用于批量管理
total_score     INT              -- 初始 score（冗余自 category）
remaining_score INT              -- 剩余 score
activated_at    DATETIME
expires_at      DATETIME         -- 激活后计算的过期时间
created_at      DATETIME
metadata        JSON             -- 扩展字段，预留
```

### activation_log（激活码使用日志）

```
id              BIGINT PK AUTO_INCREMENT
key_id          BIGINT FK → activation_key
category_id     BIGINT FK → category
action          ENUM('activate','deduct')
amount          INT              -- 操作的 score 数量
remaining_after INT              -- 操作后剩余 score
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
  "message": "激活码不存在",
  "data": null
}
```

错误码规划：

| 范围 | 含义 |
|------|------|
| 0 | 成功 |
| 1001-1099 | 激活码相关错误（不存在、已激活、已过期、已禁用） |
| 1101-1199 | Score 相关错误（余额不足、扣减失败） |
| 1201-1299 | 认证相关错误（API Key 无效、JWT 过期） |
| 1301-1399 | 分类相关错误（分类不存在、名称重复） |
| 9999 | 未知错误 |

### C 端接口（API Key 认证）

所有 C 端接口统一为 POST + JSON body，敏感数据不出现在 URL 中。

#### POST /api/v1/keys/activate

激活激活码，返回 score 信息。

```json
// 请求
// Header: X-API-Key: <category_api_key>
{
  "key_code": "A1B2-C3D4-E5F6-G7H8",
  "metadata": {
    "user_name": "张三",
    "user_id": "10086",
    "client_ua": "Mozilla/5.0 ...",
    "platform": "Android"
  }
}

// 响应
{
  "code": 0,
  "message": "success",
  "data": {
    "key_code": "A1B2-C3D4-E5F6-G7H8",
    "score_label": "积分",
    "total_score": 100,
    "remaining_score": 100,
    "expires_at": "2026-06-09T00:00:00Z"
  }
}
```

#### POST /api/v1/keys/deduct

扣减 score，加分布式锁保证并发安全。

```json
// 请求
{
  "key_code": "A1B2-C3D4-E5F6-G7H8",
  "amount": 10,
  "metadata": {
    "user_name": "张三",
    "action": "兑换商品A"
  }
}

// 响应
{
  "code": 0,
  "data": {
    "remaining_score": 90
  }
}
```

#### POST /api/v1/keys/balance

查询剩余 score。

```json
// 请求
{
  "key_code": "A1B2-C3D4-E5F6-G7H8",
  "metadata": {
    "user_name": "张三"
  }
}
```

### B 端管理接口（JWT 认证）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/admin/login` | 管理员登录，返回 JWT |
| GET | `/api/v1/admin/categories` | 分类列表 |
| POST | `/api/v1/admin/categories` | 创建分类 |
| PUT | `/api/v1/admin/categories/{id}` | 更新分类 |
| DELETE | `/api/v1/admin/categories/{id}` | 删除分类 |
| POST | `/api/v1/admin/keys/generate` | 批量生成激活码 |
| POST | `/api/v1/admin/keys/search` | 激活码搜索（筛选条件放 body） |
| PUT | `/api/v1/admin/keys/{id}/disable` | 禁用激活码 |
| GET | `/api/v1/admin/stats` | 统计概览 |
| GET | `/api/v1/admin/stats/category/{id}` | 分类维度统计 |
| POST | `/api/v1/admin/usage-logs/search` | 使用日志查询 |
| GET | `/api/v1/admin/audit-logs` | 审计日志 |

## C 端性能与缓存策略

### Redis 缓存结构

```
key:{key_code} → Hash
  ├── status: "activated"
  ├── total_score: 100
  ├── remaining_score: 90
  ├── expires_at: "2026-06-09T00:00:00Z"
  └── category_id: 1
TTL: 30min，过期自动清除，下次访问从 MySQL 回填
```

### 校验流程

```
请求进入
  │
  ├─ 校验 API Key（Redis 缓存 category 信息）
  │
  ├─ 查询激活码状态
  │   ├─ 优先查 Redis Hash: key:{key_code}
  │   ├─ 未命中 → 查 MySQL → 回写 Redis（TTL 30min）
  │   └─ 已命中 → 直接使用缓存数据
  │
  ├─ 过期判断：查询时判断 expires_at < NOW() 即失效，状态懒更新
  │
  ├─ 操作处理
  │   ├─ activate: 写 MySQL → 写 Redis Hash
  │   ├─ deduct: Redis 分布式锁 + HINCRBY 原子扣减 → 异步写 MySQL
  │   └─ balance: 直接读 Redis Hash
  │
  └─ 返回结果
```

### 扣减并发安全

```python
# 1. 加分布式锁（Redis SETNX，TTL 防死锁）
lock_key = f"lock:key:{key_code}"
acquired = SET lock_key 1 NX EX 5
if not acquired:
    return error("系统繁忙，请稍后重试")

try:
    # 2. 检查余额
    remaining = HGET key:{key_code} remaining_score
    if remaining < amount:
        return error("余额不足")

    # 3. 原子扣减
    new_remaining = HINCRBY key:{key_code} remaining_score -{amount}

    # 4. 异步写 MySQL
    async_save_to_mysql(key_code, amount, new_remaining)

    return { "remaining_score": new_remaining }
finally:
    # 5. 释放锁
    DEL lock_key
```

锁粒度为单个 key，不同激活码之间不互斥。锁 TTL 5 秒，防止异常时死锁。

## 管理后台页面

### 登录页 `/login`
- 单管理员账号密码登录
- JWT 存 localStorage，过期自动跳转登录

### 数据看板 `/dashboard`
- 总览卡片：总激活码数、已激活数、总 score 消耗量、今日激活数
- 图表：近 7 天/30 天激活趋势折线图
- 各分类 score 消耗占比饼图
- 最近激活记录列表

### 分类管理 `/categories`
- 分类列表表格：名称、标识码、score 值、score 标签、API Key、创建时间
- 操作：新增、编辑、删除（删除前校验是否有关联激活码）
- API Key 支持一键复制

### 激活码管理 `/keys`
- 搜索筛选：按分类、状态、批次号、key_code 搜索
- 表格展示：key_code、分类、状态、初始/剩余 score、激活时间、过期时间
- 操作：批量生成（选分类 + 数量 + 批次号）、禁用单个、查看日志、导出
- 批量生成后支持导出为 CSV/JSON

### 激活码使用日志 `/usage-logs`
- 搜索筛选：按 key_code、分类、操作类型（激活/扣减）、时间范围
- 表格展示：key_code、分类、操作类型、score 数量、操作后剩余、上报数据、客户端 IP、时间
- 上报数据列点击展开显示 metadata 的 key-value 列表
- 点击 key_code 可查看该激活码的完整操作时间线

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
│   │   │   ├── category.py
│   │   │   ├── activation_key.py
│   │   │   ├── activation_log.py
│   │   │   ├── admin_user.py
│   │   │   └── audit_log.py
│   │   ├── schemas/             # Pydantic 请求/响应模型
│   │   │   ├── key.py
│   │   │   ├── category.py
│   │   │   └── admin.py
│   │   ├── routers/             # 路由
│   │   │   ├── api_keys.py      # C 端接口
│   │   │   ├── admin_auth.py    # 登录
│   │   │   ├── admin_categories.py
│   │   │   ├── admin_keys.py
│   │   │   ├── admin_stats.py
│   │   │   └── admin_audit.py
│   │   ├── services/            # 业务逻辑
│   │   │   ├── key_service.py
│   │   │   ├── score_service.py
│   │   │   └── stats_service.py
│   │   ├── middleware/          # 中间件
│   │   │   ├── api_key_auth.py  # API Key 认证
│   │   │   ├── jwt_auth.py      # JWT 认证
│   │   │   └── audit.py         # 审计日志
│   │   └── utils/
│   │       ├── key_generator.py # 激活码生成算法
│   │       └── response.py      # 统一响应格式
│   ├── alembic/                 # 数据库迁移
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── Login.vue
│   │   │   ├── Dashboard.vue
│   │   │   ├── Categories.vue
│   │   │   ├── Keys.vue
│   │   │   ├── UsageLogs.vue
│   │   │   └── AuditLogs.vue
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
| Redis Hash 存激活码缓存 | 支持 HINCRBY 原子扣减，结构清晰 |
| 扣减加分布式锁 | 防止检查余额和扣减之间的竞态条件 |
| C 端接口全 POST | 敏感数据不出现在 URL 中 |
| metadata 可扩展 | 业务方自定义字段，平台不约束 |
| 前后端独立部署 | 独立扩展，独立更新，职责清晰 |
