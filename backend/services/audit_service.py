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
    - actor_id: str (Who did it)
    - organization_id: str (Context, if any)
    - action: str (Enum-like string: USER_CREATED, ORG_DELETED)
    - target_id: str (Optional, who was affected)
    - details: dict (Metadata, diffs)
"""

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from backend.database.repository import AbstractWorkflowRepository
from backend.exceptions import AppException, ErrorCodes
from backend.models.audit import AuditEvent

logger = logging.getLogger(__name__)


class AuditService:
    """Service for handling audit log persistence."""

    def __init__(self, repo: AbstractWorkflowRepository):
        """Initialize AuditService.

        Args:
            repo (AbstractWorkflowRepository): The repository for audit log storage.
        """
        self.repo = repo

    async def log_event(
        self,
        actor_id: str,
        action: str,
        organization_id: str | None = None,
        target_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Records an audit event.

        Args:
            actor_id: ID of the user performing the action.
            action: Action identifier (e.g. 'USER_CREATED').
            organization_id: Optional context ID.
            target_id: Optional target ID.
            details: Optional metadata.

        Raises:
            AppException: If logging fails (Security/Compliance requirement: Audits must succeed).
        """
        try:
            # Fail Fast: Ensure core data is present
            if not actor_id or not action:
                raise ValueError("Audit log requires 'actor_id' and 'action'.")

            event = AuditEvent(
                id=uuid.uuid4().hex,
                timestamp=datetime.now(UTC),
                actor_id=actor_id,
                organization_id=organization_id,
                action=action.upper(),
                target_id=target_id,
                details=details or {},
            )

            entry = event.model_dump()

            await self.repo.log_audit_event(entry)
            logger.info(f"[AUDIT] {action} by {actor_id} in {organization_id}")

        except Exception as e:
            logger.error(f"[AUDIT_FAIL] Failed to persist log: {e}", exc_info=True)
            # CRITICAL: If audit logging fails, we must raise an exception to prevent un-audited actions
            # in high-security contexts.
            raise AppException(
                message=f"Audit logging failed: {str(e)}",
                status_code=500,
                details={"error_code": ErrorCodes.SECURITY_DB_ERROR},
            ) from e

    async def get_logs(
        self,
        organization_id: str | None = None,
        actor_id: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Retrieves audit logs.

        Args:
            organization_id: Filter by Org ID.
            actor_id: Filter by User ID.
            action: Filter by Action.
            limit: Max records to return.

        Returns:
            List[Dict[str, Any]]: List of audit log entries.
        """
        try:
            return await self.repo.get_audit_logs(
                organization_id=organization_id, actor_id=actor_id, action=action, limit=limit
            )
        except Exception as e:
            logger.error(f"Failed to retrieve audit logs: {e}", exc_info=True)
            raise AppException(
                message=f"Failed to retrieve audit logs: {str(e)}",
                status_code=500,
                details={"error_code": ErrorCodes.SECURITY_DB_ERROR},
            ) from e
