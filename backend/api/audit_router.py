"""API Router for Audit Logs.

Provides endpoints for retrieving system audit logs.
"""

import logging

from fastapi import APIRouter, HTTPException, Query, status

from backend.dependencies import AuditServiceDep, CurrentUserDep
from backend.models.audit import AuditEvent
from backend.models.auth import UserRole

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/logs", response_model=list[AuditEvent])
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
    # 1. Access Control
    try:
        if user.role == UserRole.ROOT:
            # ROOT can filter by anything.
            target_org = organization_id
        elif user.role == UserRole.ADMIN:
            # ADMIN is forced to their own org.
            if organization_id and organization_id != user.organization_id:
                error_code = "ACCESS_DENIED_ORGANIZATION_MISMATCH"
                logger.warning(f"{error_code}: Admin {user.uid} tried to access org {organization_id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=error_code,
                )
            target_org = user.organization_id
        else:
            error_code = "PERMISSION_DENIED"
            logger.warning(f"{error_code}: User {user.uid} with role {user.role} denied audit access")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=error_code
            )

        # 2. Fetch Logs
        logs = await audit_service.get_logs(organization_id=target_org, actor_uid=actor_uid, action=action, limit=limit)
        return logs

    except HTTPException:
        raise
    except Exception as e:
        error_code = "AUDIT_LOG_RETRIEVAL_FAILED"
        logger.error(f"{error_code}: Failed to retrieve audit logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_code) from e
