from __future__ import annotations

import logging
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog

logger = logging.getLogger("keygen.audit")


async def write_audit(
    db: AsyncSession,
    *,
    admin_id: int,
    action: str,
    target_type: str,
    target_id: Optional[int] = None,
    detail: Optional[dict[str, Any]] = None,
    client_ip: Optional[str] = None,
) -> None:
    """Write an audit log entry. Callers should ensure the outer transaction commits."""
    log = AuditLog(
        admin_id=admin_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail=detail,
        client_ip=client_ip,
    )
    db.add(log)
    logger.info("audit admin_id=%d action=%s target_type=%s target_id=%s", admin_id, action, target_type, target_id)
