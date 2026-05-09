# Keygen Platform

通用激活码生成与管理服务平台。

## 功能

- 激活码批量生成（分段式格式：XXXX-XXXX-XXXX-XXXX）
- 激活码校验与激活
- Score 积分管理（发放、扣减、查询）
- 多分类/渠道管理
- 数据看板与统计
- 操作日志与审计

## 技术栈

- **后端**: Python 3.12 + FastAPI + SQLAlchemy (async) + Alembic
- **前端**: Vue3 + TypeScript + Element Plus + Pinia
- **数据库**: MySQL 8.0
- **缓存**: Redis 7
- **部署**: Docker Compose + Nginx

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

## API 接口

启动后访问 Swagger 文档: http://localhost:8000/docs

### C端接口（需 API Key 鉴权，Header: `X-API-Key`）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/keys/activate` | 激活码激活 |
| POST | `/api/v1/keys/deduct` | 积分扣减 |
| POST | `/api/v1/keys/balance` | 查询余额 |

### B端管理接口（需 JWT 鉴权，Header: `Authorization: Bearer <token>`）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/admin/login` | 管理员登录 |
| GET | `/api/v1/admin/categories` | 分类列表 |
| POST | `/api/v1/admin/categories` | 创建分类 |
| PUT | `/api/v1/admin/categories/{id}` | 更新分类 |
| DELETE | `/api/v1/admin/categories/{id}` | 删除分类 |
| POST | `/api/v1/admin/keys/generate` | 批量生成激活码 |
| GET | `/api/v1/admin/keys` | 激活码列表 |
| GET | `/api/v1/admin/keys/{id}` | 激活码详情 |
| GET | `/api/v1/admin/stats/overview` | 数据总览 |
| GET | `/api/v1/admin/stats/categories` | 分类统计 |
| GET | `/api/v1/admin/usage-logs` | 使用日志 |
| GET | `/api/v1/admin/audit-logs` | 审计日志 |

## 项目结构

```
keygen-platform/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy 数据模型
│   │   ├── schemas/         # Pydantic 请求/响应模型
│   │   ├── routers/         # API 路由
│   │   ├── services/        # 业务逻辑
│   │   ├── middleware/       # 认证中间件
│   │   ├── utils/           # 工具函数
│   │   ├── config.py        # 配置管理
│   │   ├── database.py      # 数据库连接
│   │   ├── redis_client.py  # Redis 客户端
│   │   └── main.py          # 应用入口
│   ├── tests/               # 测试
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/             # API 请求封装
│   │   ├── router/          # 路由配置
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── utils/           # 工具函数
│   │   └── views/           # 页面组件
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── .env.example
```

## 许可证

MIT
