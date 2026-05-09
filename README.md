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
