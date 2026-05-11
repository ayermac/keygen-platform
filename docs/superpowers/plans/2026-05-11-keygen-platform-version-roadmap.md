# Keygen Platform Version Roadmap

> Version-by-version product plan after the production hardening pass.

## Purpose

This roadmap turns Keygen Platform from a production-ready redemption-code service into a mature commercial operations platform. It should be used as the primary planning document for new development after the initial implementation plan.

## Current Baseline: v1.0 Production Preview

Status: ready for staging / pre-release validation.

Delivered capabilities:

- Product management with per-product API Key.
- Redemption code generation, redemption, balance query, and credit consumption.
- Redis Lua based atomic credit consumption.
- Business exception hierarchy with stable error codes.
- JWT admin authentication and login rate limiting.
- API Key rotation with old key invalidation.
- Audit logs for critical admin operations.
- Request ID middleware, structured request logs, and readiness checks.
- Alembic migrations and production Docker Compose configuration.
- Vue + Element Plus admin UI with dashboard, products, codes, usage logs, audit logs, and API docs.

Pre-release validation checklist:

- Run `cd backend && python3 -m pytest tests -q`.
- Run `cd frontend && npm run build`.
- Run `cd backend && python3 -m alembic upgrade head --sql`.
- Run `docker compose -f docker-compose.prod.yml config` with real production-like secrets.
- Start a staging stack, run migrations, confirm `/api/v1/health/ready`.
- Complete an end-to-end flow: create product, rotate/copy API Key, generate codes, redeem, consume, query balance, inspect usage log and audit log.

## Version Strategy

Each version should ship as a coherent business capability, not a grab bag of unrelated improvements. Keep API compatibility unless the version explicitly defines a migration path.

Recommended order:

1. v1.1: Idempotent credit consumption.
2. v1.2: Batch operations and export.
3. v1.3: Role-based admin permissions.
4. v1.4: Operations reporting.
5. v1.5: Advanced API Key management.
6. v1.6: Risk controls and alerts.
7. v2.0: Multi-tenant SaaS foundation.

## v1.1: Idempotent Consumption

Status: **done** (2026-05-11)

Goal: prevent duplicate credit deductions caused by client retries, timeouts, or concurrent duplicate requests.

Scope:

- Add optional `request_id` to `POST /api/v1/codes/consume`.
- Add `request_id` to usage logs.
- Add an Alembic migration and an appropriate uniqueness constraint or equivalent locking strategy.
- When `request_id` is present, the same product + code + request_id + deduct action must deduct only once.
- Repeated requests with the same `request_id` must return the first successful `remaining_credits`.
- Keep `request_id` optional so existing clients remain compatible.
- Include `request_id` in admin usage log responses and UI.
- Update API docs, agent docs, README, and error handling notes.

Acceptance criteria:

- Repeating the same `request_id` 10 times deducts once.
- Concurrent duplicate requests with the same `request_id` produce one deduct log.
- Different `request_id` values deduct independently.
- Missing `request_id` preserves current non-idempotent behavior.
- Tests cover success, retry, concurrency, insufficient credits, and cache-miss rebuild.

## v1.2: Batch Management And Export

Status: **done** (2026-05-11)

Goal: make generated code batches operable by support and operations teams.

Scope:

- Introduce a `code_batch` model/table.
- Record batch metadata when codes are generated: batch id, product, card type, count, total credits, creator, remark, created time.
- Add batch list, batch detail, export, and batch disable APIs.
- Add admin UI page `/batches`.
- Support CSV export at minimum; XLSX can be added if needed.
- Support export filters such as all codes, unused only, activated only, disabled only.
- Batch disable must invalidate Redis caches for affected activated codes.
- Audit batch export and batch disable operations.

Suggested API:

- `GET /api/v1/admin/batches`
- `GET /api/v1/admin/batches/{batch_id}`
- `GET /api/v1/admin/batches/{batch_id}/export`
- `PUT /api/v1/admin/batches/{batch_id}/disable`

Acceptance criteria:

- Operators can find a batch, inspect all codes in it, export it, and disable it.
- Exported files match filters and include code, status, credits, expiration, and created time.
- Batch stats match the underlying redemption code table.
- Tests verify batch creation, listing, export, disable, Redis invalidation, and audit log writes.

## v1.3: Role-Based Admin Permissions

Goal: separate operational, audit, and super-admin capabilities.

Scope:

- Add `role` to `admin_user`.
- Store role in JWT claims.
- Add authorization dependencies such as `require_roles(...)`.
- Add roles:
  - `super_admin`: all actions.
  - `operator`: products, codes, batches, and reports.
  - `auditor`: read-only logs and reports.
  - `viewer`: dashboard and read-only lists.
- Add admin management only for `super_admin` if user management is introduced in this version.
- Filter frontend routes and menu entries by role.
- Ensure denied operations return stable error codes.

Acceptance criteria:

- `auditor` cannot generate codes, disable codes, delete products, or rotate API Keys.
- `operator` cannot manage admin users.
- `viewer` cannot mutate data.
- `super_admin` can perform every admin action.
- Audit logs include the actor and denied high-risk attempts where useful.

## v1.4: Operations Reporting

Goal: help teams understand distribution, redemption, consumption, and remaining liabilities.

Scope:

- Add report APIs for overview, product performance, batch performance, and trends.
- Add filters by product, batch, card type, status, date range, and metadata channel where feasible.
- Track:
  - Generated count.
  - Redeemed count.
  - Unused count.
  - Disabled count.
  - Expired count.
  - Total credits.
  - Consumed credits.
  - Remaining credits.
  - Redemption rate.
  - Consumption rate.
- Add export support for report data.
- Update dashboard to present operational metrics rather than only raw totals.

Suggested API:

- `GET /api/v1/admin/reports/overview`
- `GET /api/v1/admin/reports/products`
- `GET /api/v1/admin/reports/batches`
- `GET /api/v1/admin/reports/trends`
- `GET /api/v1/admin/reports/export`

Acceptance criteria:

- Report numbers reconcile with redemption code and usage log records.
- Large datasets are paginated or aggregated efficiently.
- Dashboard can answer: what was generated, what was redeemed, what was consumed, and what remains.

## v1.5: Advanced API Key Management

Goal: support safer integrations and smoother key rotation for real clients.

Scope:

- Replace single product `api_key` storage with a `product_api_key` table.
- Store only key hash and key prefix; full keys are shown only once on creation.
- Support multiple active keys per product.
- Support key status: `active`, `disabled`, `expired`.
- Add key remark, created time, last used time, and expiration time.
- Allow planned rotation where old and new keys overlap until a configured expiration.
- Track which key prefix was used in request logs and usage logs where appropriate.
- Add per-key rate limit settings if not deferred to v1.6.

Acceptance criteria:

- A product can have multiple API Keys.
- Disabling one key does not affect other active keys for the product.
- Expired keys fail authentication.
- Full API Key values are never stored in plaintext.
- New keys are displayed once and then only masked.

## v1.6: Risk Controls And Alerts

Goal: reduce abuse and surface suspicious activity before it becomes operational damage.

Scope:

- Add IP/product/API-Key/code-level rate limits.
- Add blacklists for IP and optionally metadata user identifiers.
- Add `risk_event` records for suspicious activity.
- Add admin UI for risk events and blocklists.
- Add optional webhook alerts for high-risk events.
- Add high-risk operation confirmation for API Key rotation, batch disable, and bulk actions.

Suggested triggers:

- Many failed redemptions from one IP.
- Many redemptions from one IP across many codes.
- Sudden consumption spike for one product.
- Repeated system-busy or insufficient-credit responses.
- Frequent API Key rotation.
- Large batch disable.

Acceptance criteria:

- Risk hits return stable error codes.
- Operators can inspect risk events.
- Blocklist changes are audited.
- Webhook failures do not break core redemption/consumption flows.

## v2.0: Multi-Tenant SaaS Foundation

Goal: evolve from a single-organization platform to a SaaS-ready service.

Scope:

- Add tenant/organization model.
- Scope products, codes, batches, logs, API Keys, reports, and admin users by tenant.
- Add tenant-aware RBAC.
- Add tenant-level quotas and billing hooks.
- Add tenant isolation tests.
- Add migration strategy from single-tenant data to default tenant.

Acceptance criteria:

- No cross-tenant reads or writes through API or admin UI.
- Existing single-tenant deployment can migrate to a default tenant.
- Reports, audit logs, and API Key authentication are tenant-scoped.

## Cross-Version Engineering Rules

- Every schema change requires an Alembic migration.
- Every API change requires README/API docs and agent docs updates.
- Critical business paths require tests before merge.
- Keep response envelope as `{ code, message, data }`.
- Preserve backward compatibility unless the version explicitly documents a migration.
- Admin mutations must write audit logs.
- C-end calls should be safe under retry, concurrency, and cache rebuild scenarios.
- Production compose/config changes must be verified with `docker compose -f docker-compose.prod.yml config`.

## Backlog Parking Lot

These are useful, but should not interrupt v1.1-v1.6 unless there is a concrete business need:

- SDKs for Python/Node/Go.
- Postman collection export.
- Webhook event delivery for redeem/consume events.
- Scheduled expiration materialization job.
- Data retention and log archiving.
- Backup/restore runbook.
- OpenAPI client generation.
- Admin 2FA.
- Prometheus metrics endpoint.
