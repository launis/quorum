"""API Router for Organization Management.

This module provides multitenancy endpoints for creating, updating, and
retrieving organization details.
"""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.dependencies import AuthServiceDep, CurrentUserDep, RepositoryDep
from backend.models.auth import Organization, SubscriptionStatus, TokenData, UserRole
from backend.services.auth import AuthService

logger = logging.getLogger(__name__)


# --- Pydantic Models ---
class OrganizationCreateRequest(BaseModel):
    """Payload for creating a new organization."""

    id: str | None = None  # Auto-generated if empty
    name: str
    tier: str = "standard"  # standard, premium, enterprise
    contact_email: str | None = None
    billing_id: str | None = None
    subscription_status: SubscriptionStatus = SubscriptionStatus.TRIAL
    quota_limit: float = 10.0
    settings_override: dict[str, Any] | None = None


class OrganizationUpdate(BaseModel):
    """Payload for updating an organization."""

    name: str | None = None
    tier: str | None = None
    contact_email: str | None = None
    billing_id: str | None = None
    subscription_status: SubscriptionStatus | None = None
    quota_limit: float | None = None
    tpm_limit: int | None = None
    rpm_limit: int | None = None
    settings_override: dict[str, Any] | None = None


class OrganizationResponse(BaseModel):
    """Response model for organization details."""

    id: str
    name: str
    tier: str
    contact_email: str | None = None
    created_at: str | None = None
    billing_id: str | None = None
    subscription_status: SubscriptionStatus = SubscriptionStatus.TRIAL
    quota_limit: float = 10.0
    tpm_limit: int = 100000
    rpm_limit: int = 60
    status: str = "PENDING"  # Mapped from is_active

    @classmethod
    def set_status_from_active_flag(cls, data: Any) -> Any:
        """Validator to derive status attribute from is_active flag."""
        if isinstance(data, dict):
            # Check is_active (default True if missing in dict, but safer to check)
            is_active = data.get("is_active", True)
            if "status" not in data:
                data["status"] = "ACTIVE" if is_active else "SUSPENDED"
        return data


# --- Strict Usage Models (No Defaults) ---
class OrganizationUserCreate(BaseModel):
    """Payload for creating a user within an organization.

    Strictly forbids default values for role and email.
    """

    email: str
    display_name: str
    role: UserRole
    password: str | None = None  # Optional initialization


router = APIRouter(prefix="/organizations", tags=["Organizations"])

# --- Endpoints ---


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org: OrganizationCreateRequest,
    user: Annotated[TokenData, Depends(AuthService.require_role(UserRole.ROOT))],
    repo: RepositoryDep,  # Injected
    auth: AuthServiceDep,
):
    """Create a new Tenant Organization.

    Args:
        org (OrganizationCreateRequest): Organization details.
        user (TokenData): Requesting user (ROOT required).
        auth (AuthServiceDep): Authentication service.
        repo (RepositoryDep): Repository dependency.

    Returns:
        OrganizationResponse: The created organization.

    Raises:
        HTTPException: If ID conflict (409).
    """
    import backend.utils.identifiers as id_gen

    # Generate ID if missing
    # Note: We do this BEFORE .dict() to ensure it's in the item.
    if not org.id:
        # Use name as base
        org.id = id_gen.generate_unique_id(base_name=org.name)

    # Check existence
    existing = await repo.get_organization(org.id)
    if existing:
        error_code = "ORGANIZATION_ALREADY_EXISTS"
        logger.error(f"{error_code}: ID {org.id}", exc_info=True)
        raise HTTPException(status_code=409, detail=error_code)

    # Create
    item = org.model_dump()

    # Add metadata
    import time

    if "created_at" not in item:
        item["created_at"] = str(time.time())
    if "is_active" not in item:
        item["is_active"] = True

    await repo.create_organization(item)

    # AUDIT LOG (Phase 3)
    try:
        from backend.services.audit_service import AuditService

        audit = AuditService(repo)
        await audit.log_event(
            actor_uid=user.uid,
            action="ORG_CREATED",
            organization_id=item["id"],
            details={"name": item["name"], "tier": item["tier"]},
        )

    except Exception as e:
        error_code = "AUDIT_LOG_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        # We generally don't block on audit failure, but if strict mode...
        # For now, log but raise to fail the request if audit is critical?
        # Actually, if audit fails, we should probably fail.
        raise HTTPException(status_code=500, detail=error_code) from e

    # Return as response (Organization has logic to default fields if needed, but input covers it)
    return OrganizationResponse(**item)


@router.get("/me", response_model=OrganizationResponse)
async def get_my_organization(
    user: CurrentUserDep,
    repo: RepositoryDep,
):
    """Get the organization of the current user.

    Args:
        user (CurrentUserDep): Requesting user.
        repo (RepositoryDep): Repository dependency.

    Returns:
        OrganizationResponse: organization details.
    """
    if not user.organization_id:
        error_code = "AUTH_USER_NO_ORG"
        logger.error(f"{error_code}: User {user.uid} has no org.", exc_info=True)
        raise HTTPException(status_code=404, detail=error_code)

    org = await repo.get_organization(user.organization_id)
    if not org:
        error_code = "ORGANIZATION_NOT_FOUND"
        logger.error(f"{error_code}: ID {user.organization_id}", exc_info=True)
        raise HTTPException(status_code=404, detail=error_code)

    return OrganizationResponse(**Organization(**org).model_dump())


@router.get("/", response_model=list[OrganizationResponse])
async def list_organizations(
    user: Annotated[TokenData, Depends(AuthService.require_role(UserRole.ROOT))],
    repo: RepositoryDep,
):
    """List all organizations.

    Args:
        user (TokenData): Requesting user (must be ROOT).
        repo (RepositoryDep): Repository dependency.

    Returns:
        list[OrganizationResponse]: List of all organizations.
    """
    items = await repo.list_organizations()
    # Items are raw dicts (Documents). Wrap in Organization to apply defaults, then dump.
    return [OrganizationResponse(**Organization(**i).model_dump()) for i in items]


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: str,
    user: CurrentUserDep,
    repo: RepositoryDep,
):
    """Get organization details.

    Args:
        org_id (str): Organization ID.
        user (CurrentUserDep): Requesting user.
        repo (RepositoryDep): Repository dependency.

    Returns:
        OrganizationResponse: organization details.
    """
    # 1. Access Control
    if user.role != UserRole.ROOT:
        if user.organization_id != org_id:
            error_code = "PERMISSION_DENIED"
            logger.error(f"{error_code}: User {user.uid} denied access to {org_id}", exc_info=True)
            raise HTTPException(status_code=403, detail=error_code)

    # 2. Fetch
    org = await repo.get_organization(org_id)
    if not org:
        error_code = "ORGANIZATION_NOT_FOUND"
        logger.error(f"{error_code}: ID {org_id}", exc_info=True)
        raise HTTPException(status_code=404, detail=error_code)

    return OrganizationResponse(**Organization(**org).model_dump())


@router.get("/{org_id}/usage", response_model=dict[str, Any])
async def get_organization_usage(
    org_id: str,
    user: CurrentUserDep,
    repo: RepositoryDep,
):
    """Get current usage statistics and limits for an organization.

    Args:
        org_id (str): Organization ID.
        user (CurrentUserDep): Requesting user.
        repo (RepositoryDep): Repository dependency.

    Returns:
        dict: Usage stats (cost, limits, percentage).
    """
    # 1. Access Control
    if user.role != UserRole.ROOT:
        if user.organization_id != org_id:
            error_code = "PERMISSION_DENIED"
            logger.error(f"{error_code}: User {user.uid} denied usage view.", exc_info=True)
            raise HTTPException(status_code=403, detail=error_code)

    try:
        # 2. Fetch Limits
        org = await repo.get_organization(org_id)
        if not org:
            error_code = "ORGANIZATION_NOT_FOUND"
            logger.error(f"{error_code}: ID {org_id}", exc_info=True)
            raise HTTPException(status_code=404, detail=error_code)

        org_model = Organization(**org)

        # 3. Calculate Usage
        from datetime import UTC, datetime

        # Current Month
        now = datetime.now(UTC)
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()

        total_cost = await repo.get_org_usage_total(org_id, since=start_of_month)

        percentage = 0.0
        if org_model.quota_limit > 0:
            percentage = (total_cost / org_model.quota_limit) * 100

        return {
            "total_cost_usd": round(total_cost, 4),
            "quota_limit_usd": org_model.quota_limit,
            "tpm_limit": org_model.tpm_limit,
            "rpm_limit": org_model.rpm_limit,
            "percentage_used": round(percentage, 2),
            "period": f"{now.year}-{now.month:02d}",
        }

    except HTTPException:
        raise
    except Exception as e:
        error_code = "USAGE_STATS_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_code) from e


@router.put("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: str,
    organization_update: OrganizationUpdate,
    user: CurrentUserDep,
    repo: RepositoryDep,
):
    """Update organization details.

    Args:
        org_id (str): Organization ID.
        organization_update (OrganizationUpdate): Fields to update.
        user (CurrentUserDep): Requesting user.
        repo (RepositoryDep): Repository dependency.

    Returns:
        OrganizationResponse: Updated organization.
    """
    # 1. Access Control
    if user.role != UserRole.ROOT:
        if user.organization_id != org_id:
            error_code = "PERMISSION_DENIED"
            logger.error(f"{error_code}: User {user.uid} denied update.", exc_info=True)
            raise HTTPException(status_code=403, detail=error_code)
        if user.role != UserRole.ADMIN:
            error_code = "PERMISSION_DENIED_ORG_ADMIN"
            logger.error(f"{error_code}: User {user.uid} not admin.", exc_info=True)
            raise HTTPException(status_code=403, detail=error_code)

    # 2. Update
    try:
        current_data = await repo.get_organization(org_id)
        if not current_data:
            error_code = "ORGANIZATION_NOT_FOUND"
            logger.error(f"{error_code}: ID {org_id}", exc_info=True)
            raise HTTPException(status_code=404, detail=error_code)

        # Merge
        updates = organization_update.model_dump(exclude_unset=True)
        await repo.update_organization(org_id, updates)
    except Exception as e:
        error_code = "ORGANIZATION_UPDATE_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_code) from e

    # Fetch fresh
    fresh = await repo.get_organization(org_id)
    if not fresh:
        error_code = "ORGANIZATION_NOT_FOUND"
        logger.error(f"{error_code}: ID {org_id}", exc_info=True)
        raise HTTPException(status_code=404, detail=error_code)
    return OrganizationResponse(**Organization(**fresh).model_dump())


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    org_id: str,
    user: CurrentUserDep,
    repo: RepositoryDep,
    force: bool = False,
):
    """Delete an organization.

    Args:
        org_id (str): Organization ID.
        user (CurrentUserDep): Requesting user.
        repo (RepositoryDep): Repository dependency.
        force (bool): If True, delete even if users exist.
    """
    # 1. Access Control
    if user.role != UserRole.ROOT:
        error_code = "PERMISSION_DENIED_ROOT_ONLY"
        logger.error(f"{error_code}: User {user.uid} denied.", exc_info=True)
        raise HTTPException(status_code=403, detail=error_code)

    # 2. System Protection
    if org_id == "system":
        error_code = "PERMISSION_DENIED_SYSTEM_ORG"
        logger.error(f"{error_code}: Cannot delete system org.", exc_info=True)
        raise HTTPException(status_code=403, detail=error_code)

    # 3. Validation
    if not force:
        # Check for users
        users = await repo.list_users(org_id)
        if users:
            error_code = "ORGANIZATION_NOT_EMPTY"
            logger.error(f"{error_code}: Org {org_id} has users.", exc_info=True)
            raise HTTPException(
                status_code=409,
                detail=error_code,
            )

    # 4. Execute
    try:
        await repo.delete_organization(org_id)
        if force:
            # Cascade delete users/data
            await repo.delete_org_data(org_id)

        # AUDIT LOG (Phase 3)
        try:
            from backend.services.audit_service import AuditService

            audit = AuditService(repo)
            await audit.log_event(
                actor_uid=user.uid,
                action="ORG_DELETED",
                organization_id=org_id,
                details={"force": force},
            )

        except Exception as e:
            logger.error(f"AUDIT ERROR: {e}", exc_info=True)

    except Exception as e:
        error_code = "ORGANIZATION_DELETE_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_code) from e


@router.post("/{org_id}/users", status_code=status.HTTP_201_CREATED)
async def create_organization_user(
    org_id: str,
    user_data: OrganizationUserCreate,
    user: CurrentUserDep,
    auth_service: AuthServiceDep,
    repo: RepositoryDep,
):
    """Create a user within an organization.

    Enforces strict typing and no defaults.
    """
    from backend.models.auth import UserCreate

    # 1. Access Control
    if user.role != UserRole.ROOT:
        if user.organization_id != org_id:
            error_code = "PERMISSION_DENIED"
            logger.error(f"{error_code}: User {user.uid} denied.", exc_info=True)
            raise HTTPException(status_code=403, detail=error_code)
        if user.role != UserRole.ADMIN:
            error_code = "PERMISSION_DENIED_ORG_ADMIN"
            logger.error(f"{error_code}: User {user.uid} not admin.", exc_info=True)
            raise HTTPException(status_code=403, detail=error_code)

    # 2. Logic Delegate to AuthService (for consisten creation logic)
    # We map Strict model to internal UserCreate model
    internal_payload = UserCreate(
        email=user_data.email,
        display_name=user_data.display_name,
        role=user_data.role,
        password=user_data.password,
        organization_id=org_id,
    )

    try:
        # AuthService handles the heavy lifting (hashing, hierarchy check)
        # Note: AuthService is sync, but running in FastApi threadpool is acceptable pattern for now
        # given the complexity of refactoring it fully.
        new_user = await auth_service.create_user(creator_uid=user.uid, user_data=internal_payload)

        # AUDIT LOG (Phase 3)
        try:
            from backend.services.audit_service import AuditService

            # We need Repo for Audit, but AuthServiceDep might opaque it.
            # Usually AuthService has .repo.
            audit = AuditService(repo)
            await audit.log_event(
                actor_uid=user.uid,
                action="USER_CREATED",
                organization_id=org_id,
                target_uid=new_user.uid,
                details={"email": new_user.email, "role": new_user.role},
            )
        except Exception:
            pass

        return new_user
    except PermissionError as e:
        error_code = "PERMISSION_DENIED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise HTTPException(status_code=403, detail=error_code) from e
    except ValueError as e:
        error_code = "USER_CREATION_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=error_code) from e


@router.delete("/{org_id}/users/{target_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization_user(
    org_id: str,
    target_uid: str,
    user: CurrentUserDep,
    repo: RepositoryDep,
    auth_service: AuthServiceDep,
):
    """Delete a user from an organization."""
    # 1. Access Control
    if user.role != UserRole.ROOT:
        if user.organization_id != org_id:
            error_code = "PERMISSION_DENIED"
            logger.error(f"{error_code}: User {user.uid} denied.", exc_info=True)
            raise HTTPException(status_code=403, detail=error_code)
        if user.role != UserRole.ADMIN:
            error_code = "PERMISSION_DENIED_ORG_ADMIN"
            logger.error(f"{error_code}: User {user.uid} not admin.", exc_info=True)
            raise HTTPException(status_code=403, detail=error_code)

    # 2. Integrity Check: Active Ownership
    # Users own Executions. If they have active ones, block delete.
    # Note: Workflows are Org-owned, so no check needed there.
    user_execs = await repo.get_all_executions(organization_id=org_id)
    active_user_execs = [
        e for e in user_execs if e.get("user_id") == target_uid and e.get("status") in ["running", "pending", "queued"]
    ]

    if active_user_execs:
        error_code = "USER_HAS_ACTIVE_EXECUTIONS"
        logger.error(f"{error_code}: User {target_uid} has active execs.", exc_info=True)
        raise HTTPException(
            status_code=409,
            detail=error_code,
        )

    # 3. Delete via AuthService
    try:
        await auth_service.delete_user(initiator_uid=user.uid, target_uid=target_uid)

        # AUDIT LOG (Phase 3)
        try:
            from backend.services.audit_service import AuditService

            audit = AuditService(repo)
            await audit.log_event(
                actor_uid=user.uid, action="USER_DELETED", organization_id=org_id, target_uid=target_uid, details={}
            )
        except Exception:
            pass

    except Exception as e:
        error_code = "USER_DELETE_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=error_code) from e

    return None
