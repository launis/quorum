"""API Router for Organization Management.

This module provides multitenancy endpoints for creating, updating, and
retrieving organization details.
"""

import logging
from typing import Any

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
    status: str = "PENDING"  # Mapped from is_active

    from pydantic import model_validator

    @model_validator(mode="before")
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
    user: TokenData = Depends(AuthService.require_role(UserRole.ROOT)),
    repo: RepositoryDep = None,  # Injected
):
    """Create a new Tenant Organization.

    Args:
        org (OrganizationCreateRequest): Organization details.
        user (TokenData): Requesting user (must be ROOT).
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
        raise HTTPException(status_code=409, detail=f"Organization '{org.id}' already exists.")

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
        logger.error(f"AUDIT ERROR: {e}", exc_info=True)
        raise e

    # Return as response (Organization has logic to default fields if needed, but input covers it)
    return OrganizationResponse(**item)


@router.get("/", response_model=list[OrganizationResponse])
async def list_organizations(
    user: TokenData = Depends(AuthService.require_role(UserRole.ROOT)),
    repo: RepositoryDep = None,
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


@router.get("/me", response_model=OrganizationResponse)
async def get_my_organization(user: CurrentUserDep, repo: RepositoryDep):
    """Get the currently logged-in user's organization metadata.

    Accessible to: ROOT, ADMIN, MEMBER (Read-Only own org)

    Note: ROOT does not belong to an org primarily, but if they want to see 'an' org,
    they should use get_organization_by_id logic. This endpoint is for Tenant Context.

    Args:
        user (CurrentUserDep): The authenticated user.
        repo (RepositoryDep): Repository dependency.

    Returns:
        OrganizationResponse: The user's organization details.

    Raises:
        HTTPException: If not assigned (404).
    """
    if not user.organization_id:
        raise HTTPException(status_code=404, detail="User is not assigned to any organization.")

    org_data = await repo.get_organization(user.organization_id)

    if not org_data:
        raise HTTPException(status_code=404, detail="Organization not found in registry.")

    return OrganizationResponse(**Organization(**org_data).model_dump())


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(org_id: str, user: CurrentUserDep, repo: RepositoryDep):
    """Get specific organization details.

    ROOT: Can access any.
    ADMIN: Can access OWN org only.

    Args:
        org_id (str): Organization ID.
        user (CurrentUserDep): Requesting user.
        repo (RepositoryDep): Repository.

    Returns:
        OrganizationResponse: The organization details.

    Raises:
        HTTPException: If access denied (403) or not found (404).
    """
    # 1. Access Control
    if user.role != UserRole.ROOT:
        if user.organization_id != org_id:
            raise HTTPException(status_code=403, detail="Access denied to other organization.")

    org_data = await repo.get_organization(org_id)

    if not org_data:
        raise HTTPException(status_code=404, detail="Organization not found.")

    return OrganizationResponse(**Organization(**org_data).model_dump())


@router.put("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: str,
    updates: OrganizationUpdate,
    user: CurrentUserDep,
    repo: RepositoryDep,
):
    """Update Organization settings.

    ROOT: Can update any.
    ADMIN: Can update OWN org only.

    Args:
        org_id (str): Organization ID.
        updates (OrganizationUpdate): Fields to update.
        user (CurrentUserDep): Requesting user.
        repo (RepositoryDep): Repository.

    Returns:
        OrganizationResponse: Updated organization.

    Raises:
        HTTPException: If permission denied (403) or not found (404).
    """
    # 1. Access Control
    if user.role != UserRole.ROOT:
        if user.organization_id != org_id:
            raise HTTPException(status_code=403, detail="Access denied. Cannot modify other organization.")
        if user.role != UserRole.ADMIN:
            # Even if it's my org, I need to be ADMIN to update it
            raise HTTPException(status_code=403, detail="Insufficient privileges. Organization Admin required.")

    # Check existence
    existing = await repo.get_organization(org_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Organization not found.")

    # Apply Updates
    update_data = updates.dict(exclude_unset=True)
    await repo.update_organization(org_id, update_data)

    # Fetch fresh
    fresh = await repo.get_organization(org_id)
    return OrganizationResponse(**Organization(**fresh).model_dump())


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    org_id: str,
    force: bool = False,
    user: TokenData = Depends(AuthService.require_role(UserRole.ROOT)),
    repo: RepositoryDep = None,
    auth_service: AuthServiceDep = None,
):
    """Delete an organization.

    Args:
        org_id (str): Organization ID.
        force (bool): Functionally cascade delete users if True.
        user (TokenData): Requesting user (must be ROOT).
        repo (RepositoryDep): Repository.
        auth_service (AuthService): Auth service for user deletion.

    Returns:
        None

    Raises:
        HTTPException: If system org (403), not found (404), or not empty (409).
    """
    if org_id == "system":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete System Organization.")

    # 1. Check Existence
    existing = await repo.get_organization(org_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Organization not found.")

    # 2. Integrity Check: Active Executions
    # Prevent deleting Org if it has running jobs.
    all_execs = await repo.get_all_executions(organization_id=org_id)
    active_execs = [e for e in all_execs if e.get("status") in ["running", "pending", "queued"]]

    if active_execs:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Cannot delete Organization '{org_id}' while it has {len(active_execs)} active execution(s). "
                "Cancel them first."
            ),
        )

    # 3. Delete Users & Org Entity (AuthService)
    try:
        await auth_service.delete_organization(user.uid, org_id, force=force)

        # AUDIT LOG (Phase 3)
        try:
            from backend.services.audit_service import AuditService

            audit = AuditService(repo)
            await audit.log_event(
                actor_uid=user.uid,
                action="ORG_DELETED",
                organization_id=org_id,
                details={"reason": "admin_action", "force": force},
            )
        except Exception:
            pass

    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        msg = str(e)
        if "Organization is not empty" in msg:
            # Client relies on this specific detail or code to trigger confirmation dialog
            raise HTTPException(status_code=409, detail="ORG_HAS_USERS") from e
        raise HTTPException(status_code=400, detail=msg) from e

    # 4. Cascade Delete Data (Workflows/Executions - Clean up orphan data)
    await repo.delete_org_data(org_id)

    return None


@router.get("/{org_id}/users", response_model=list[dict[str, Any]])
async def list_organization_users(
    org_id: str,
    user: CurrentUserDep,
    repo: RepositoryDep,
):
    """List users within an organization.

    Args:
        org_id (str): Organization ID.
        user (CurrentUserDep): Requesting user.
        repo (RepositoryDep): Repository.

    Returns:
        list[dict]: List of users (serialized).
    """
    # 1. Access Control
    if user.role != UserRole.ROOT:
        if user.organization_id != org_id:
            raise HTTPException(status_code=403, detail="Access denied.")

    # 2. Fetch using Repository Pattern (Async)
    users = await repo.list_users(organization_id=org_id)
    return users


@router.post("/{org_id}/users", status_code=status.HTTP_201_CREATED)
async def create_organization_user(
    org_id: str,
    user_data: OrganizationUserCreate,
    user: CurrentUserDep,
    auth_service: AuthServiceDep,
):
    """Create a user within an organization.

    Enforces strict typing and no defaults.
    """
    from backend.models.auth import UserCreate

    # 1. Access Control
    if user.role != UserRole.ROOT:
        if user.organization_id != org_id:
            raise HTTPException(status_code=403, detail="Access denied.")
        if user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Organization Admin required.")

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
            audit = AuditService(auth_service.repo)
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
        raise HTTPException(status_code=403, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


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
            raise HTTPException(status_code=403, detail="Access denied.")
        if user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Organization Admin required.")

    # 2. Integrity Check: Active Ownership
    # Users own Executions. If they have active ones, block delete.
    # Note: Workflows are Org-owned, so no check needed there.
    user_execs = await repo.get_all_executions(organization_id=org_id)
    active_user_execs = [
        e
        for e in user_execs
        if e.get("user_id") == target_uid and e.get("status") in ["running", "pending", "queued"]
    ]

    if active_user_execs:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete user '{target_uid}'. They have {len(active_user_execs)} active execution(s).",
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
        raise HTTPException(status_code=400, detail=str(e)) from e

    return None
