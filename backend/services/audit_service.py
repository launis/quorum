"""Audit Service Module.

Provides centralized auditing for cross-tenant actions.
Logs critical security and administrative events (User creation, Org deletion, Settings changes).

Architecture:
    - Uses a dedicated TinyDB table 'audit_logs'.
    - Async-first implementation.
    - JSON-serializable log entries.

Schema:
    - id: str (UUID)
    - timestamp: float (UTC)
    - actor_uid: str (Who did it)
    - organization_id: str (Context, if any)
    - action: str (Enum-like string: USER_CREATED, ORG_DELETED)
    - target_uid: str (Optional, who was affected)
    - details: dict (Metadata, diffs)
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from backend.database.repository import AbstractWorkflowRepository
from backend.models.audit import AuditEvent

logger = logging.getLogger(__name__)





class AuditService:
    """Service for handling audit log persistence."""

    def __init__(self, repo: AbstractWorkflowRepository):
        """Initialize AuditService."""
        self.repo = repo

    async def log_event(
        self,
        actor_uid: str,
        action: str,
        organization_id: str | None = None,
        target_uid: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        """Records an audit event."""
        event = AuditEvent(
            id=uuid.uuid4().hex,
            timestamp=datetime.utcnow().isoformat(),
            actor_uid=actor_uid,
            organization_id=organization_id,
            action=action.upper(),
            target_uid=target_uid,
            details=details or {},
        )

        entry = event.model_dump()

        try:
            await self.repo.log_audit_event(entry)
            logger.info(f"[AUDIT] {action} by {actor_uid} in {organization_id}")
        except Exception as e:
            logger.error(f"[AUDIT_FAIL] Failed to persist log: {e}")

    async def get_logs(
        self,
        organization_id: str | None = None,
        actor_uid: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Retrieves audit logs."""
        return await self.repo.get_audit_logs(
            organization_id=organization_id, actor_uid=actor_uid, action=action, limit=limit
        )
