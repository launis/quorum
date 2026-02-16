"""API Router for Audit Logs.

Provides endpoints for retrieving system audit logs.
"""

import logging

from fastapi import APIRouter, Query, status

from backend.dependencies import AuditServiceDep, CurrentUserDep
from typing import List

from backend.models.audit import AuditEvent
from backend.models.auth import UserRole

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/logs", response_model=List[AuditEvent])
async def get_audit_logs(
    user: CurrentUserDep,
    audit_service: AuditServiceDep,
    organization_id: str | None = Query(None, description="Filter by Organization ID"),
    actor_uid: str | None = Query(None, description="Filter by Actor UID"),
    action: str | None = Query(None, description="Filter by Action type"),
    limit: int = Query(100, ge=1, le=1000),
):
    """Retrieve audit logs.

    Role Rules:
    - ROOT: Can see logs for ANY organization or system-wide (if org_id is None).
    - ADMIN: Can ONLY see logs for THEIR OWN organization.
    - MEMBER: Cannot see audit logs (403).
    """
    # 1. Access Control (Fail Fast)
    target_org = organization_id

    try:
        if user.role == UserRole.ROOT:
            # ROOT allows flexible filtering
            pass
        elif user.role == UserRole.ADMIN:
            # ADMIN is strictly scoped to own org
            if organization_id and organization_id != user.organization_id:
                from backend.exceptions import PermissionDeniedError

                error_code = "ACCESS_DENIED_ORGANIZATION_MISMATCH"
                logger.warning(f"{error_code}: Admin {user.uid} tried to access org {organization_id}")
                raise PermissionDeniedError(message="Organization mismatch", details={"error_code": error_code})
            
            # Auto-scope if not provided or provided correctly
            target_org = user.organization_id
        else:
            # MEMBER / Other
            from backend.exceptions import PermissionDeniedError

            error_code = "PERMISSION_DENIED_AUDIT_VIEW"
            logger.warning(f"{error_code}: User {user.uid} ({user.role}) denied audit access")
            raise PermissionDeniedError(message="Audit access denied", details={"error_code": error_code})

        # 2. Fetch Logs
        # Call service with strictly resolved target_org
        logs = await audit_service.get_logs(organization_id=target_org, actor_uid=actor_uid, action=action, limit=limit)
        return logs

    except Exception as e:
        from backend.exceptions import AppException

        # Allow specialized exceptions (PermissionDeniedError) to bubble up
        if isinstance(e, AppException):
            raise

        error_code = "AUDIT_LOG_RETRIEVAL_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code},
        ) from e

