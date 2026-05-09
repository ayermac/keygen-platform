#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Keygen Platform — Production Deployment Script
# Usage: ./scripts/deploy.sh [--skip-backup] [--skip-health]
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SKIP_BACKUP=false
SKIP_HEALTH=false

for arg in "$@"; do
  case $arg in
    --skip-backup) SKIP_BACKUP=true ;;
    --skip-health) SKIP_HEALTH=true ;;
    *) echo "Unknown option: $arg"; exit 1 ;;
  esac
done

log()   { echo -e "${GREEN}[DEPLOY]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# ----------------------------------------------------------
# 1. Pre-flight checks
# ----------------------------------------------------------
log "Running pre-flight checks..."

command -v docker >/dev/null 2>&1 || error "Docker is not installed"
docker compose version >/dev/null 2>&1 || error "Docker Compose v2 is required"

if [ ! -f .env ]; then
  warn ".env not found, copying from .env.example"
  cp .env.example .env
  error "Please edit .env with production values before deploying"
fi

if grep -q "change_me_in_production" .env; then
  error "Default secrets detected in .env. Change MYSQL_PASSWORD, JWT_SECRET_KEY, and ADMIN_DEFAULT_PASSWORD"
fi

if grep -q "admin123" .env; then
  warn "Default admin password detected. Consider changing ADMIN_DEFAULT_PASSWORD"
fi

log "Pre-flight checks passed"

# ----------------------------------------------------------
# 2. Database backup
# ----------------------------------------------------------
if [ "$SKIP_BACKUP" = false ]; then
  log "Creating database backup..."
  BACKUP_DIR="./backups"
  mkdir -p "$BACKUP_DIR"
  BACKUP_FILE="$BACKUP_DIR/keygen_$(date +%Y%m%d_%H%M%S).sql.gz"

  if docker compose ps mysql --format json 2>/dev/null | grep -q "running"; then
    docker compose exec -T mysql mysqldump \
      -u root -proot_password \
      --single-transaction --routines --triggers \
      keygen | gzip > "$BACKUP_FILE" 2>/dev/null && \
      log "Backup saved to $BACKUP_FILE" || \
      warn "Backup failed (non-critical, continuing)"
  else
    warn "MySQL not running, skipping backup"
  fi
else
  warn "Skipping backup (--skip-backup)"
fi

# ----------------------------------------------------------
# 3. Pull latest code
# ----------------------------------------------------------
log "Pulling latest code..."
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git pull --rebase origin main
  log "Code updated to $(git rev-parse --short HEAD)"
else
  warn "Not a git repository, skipping git pull"
fi

# ----------------------------------------------------------
# 4. Build and deploy
# ----------------------------------------------------------
log "Building and deploying services..."
docker compose build --no-cache backend frontend
docker compose up -d --remove-orphans

# ----------------------------------------------------------
# 5. Wait for health check
# ----------------------------------------------------------
if [ "$SKIP_HEALTH" = false ]; then
  log "Waiting for services to be healthy..."
  MAX_RETRIES=30
  RETRY_INTERVAL=2

  for i in $(seq 1 $MAX_RETRIES); do
    if curl -sf http://localhost/api/v1/health >/dev/null 2>&1; then
      log "All services healthy!"
      break
    fi
    if [ "$i" -eq "$MAX_RETRIES" ]; then
      error "Health check failed after $((MAX_RETRIES * RETRY_INTERVAL))s. Check: docker compose logs"
    fi
    sleep $RETRY_INTERVAL
  done
else
  warn "Skipping health check (--skip-health)"
fi

# ----------------------------------------------------------
# 6. Post-deploy summary
# ----------------------------------------------------------
echo ""
log "=========================================="
log "  Deployment complete!"
log "=========================================="
log ""
log "  Admin Dashboard : http://localhost"
log "  API Server      : http://localhost/api/v1/health"
log "  Swagger Docs    : http://localhost:8000/docs"
log "  Agent API Docs  : http://localhost/api/v1/agent-docs"
log "  Web API Docs    : http://localhost/docs/api"
log ""
log "  Logs: docker compose logs -f"
log "  Stop: docker compose down"
log ""
