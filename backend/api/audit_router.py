"""API Router for Audit Logs.

Provides endpoints for retrieving system audit logs.
"""

from fastapi import APIRouter, HTTPException, Query, status

from backend.dependencies import AuditServiceDep, CurrentUserDep
from backend.models.audit import AuditEvent
from backend.models.auth import UserRole

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
    if user.role == UserRole.ROOT:
        # ROOT can filter by anything.
        target_org = organization_id
    elif user.role == UserRole.ADMIN:
        # ADMIN is forced to their own org.
        if organization_id and organization_id != user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You can only view logs for your own organization.",
            )
        target_org = user.organization_id
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. Insufficient privileges to view audit logs."
        )

    # 2. Fetch Logs
    logs = await audit_service.get_logs(organization_id=target_org, actor_uid=actor_uid, action=action, limit=limit)

    return logs
