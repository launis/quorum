"""API Router for Organization Management.

This module provides multitenancy endpoints for creating, updating, and
retrieving organization details.
"""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.dependencies import AuthServiceDep, CurrentUserDep, RepositoryDep
from backend.models.auth import Organization, TokenData, UserRole

# Correct Service Imports
# Correct Service Imports
from backend.services.auth import AuthService


# --- Pydantic Models ---
class OrganizationCreate(BaseModel):
    id: str | None = None  # Auto-generated if empty
    name: str
    tier: str = "standard"  # standard, premium, enterprise
    contact_email: str | None = None
    settings_override: dict[str, Any] | None = None


class OrganizationUpdate(BaseModel):
    name: str | None = None
    tier: str | None = None
    contact_email: str | None = None
    settings_override: dict[str, Any] | None = None


class OrganizationResponse(BaseModel):
    id: str
    name: str
    tier: str
    contact_email: str | None = None
    created_at: str | None = None


router = APIRouter(prefix="/organizations", tags=["Organizations"])

# --- Endpoints ---


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org: OrganizationCreate,
    user: TokenData = Depends(AuthService.require_role(UserRole.ROOT)),
    repo: RepositoryDep = None,  # Injected
):
    """Create a new Tenant Organization.

    Args:
        org (OrganizationCreate): Organization details.
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
    item = org.dict(exclude_unset=True)

    # Add metadata
    import time

    if "created_at" not in item:
        item["created_at"] = str(time.time())
    if "is_active" not in item:
        item["is_active"] = True

    await repo.create_organization(item)

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
    user: TokenData = Depends(AuthService.require_role(UserRole.ROOT)),
    repo: RepositoryDep = None,
    auth_service: AuthService = Depends(AuthServiceDep),
):
    """Delete an organization.

    Args:
        org_id (str): Organization ID.
        user (TokenData): Requesting user (must be ROOT).
        repo (RepositoryDep): Repository.
        auth_service (AuthService): Auth service for user deletion.

    Returns:
        None

    Raises:
        HTTPException: If system org (403) or not found (404).
    """
    if org_id == "system":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete System Organization.")

    # 1. Check Existence
    existing = await repo.get_organization(org_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Organization not found.")

    # 2. Delete Users & Org Entity (AuthService)
    # This also enforces constraints like checking if org is system (redundant but safe)
    try:
        auth_service.delete_organization(user.uid, org_id)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 3. Cascade Delete Data (Workflows/Executions - Clean up orphan data)
    await repo.delete_org_data(org_id)

    return None
