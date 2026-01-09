"""API Router for Authentication and User Management.

This module provides endpoints for user login (token verification), registration,
profile management, and organization administration.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.dependencies import AuthServiceDep, CurrentUserDep
from backend.models.auth import Organization, OrganizationCreate, User, UserCreate, UserRole, UserUpdate

router = APIRouter(prefix="/auth", tags=["Authentication & Users"])


class TokenPayload(BaseModel):
    """Payload for token verification.

    Attributes:
        token (str): The Firebase or Mock ID Token.
    """

    token: str


class LoginResponse(BaseModel):
    """Response model for successful login.

    Attributes:
        user (User): The full user profile.
        token_valid (bool): Confirmation of token validity.
        debug_msg (Optional[str]): Debug information (mock vs real).
    """

    user: User
    token_valid: bool
    debug_msg: str | None = None


class ImpersonationRequest(BaseModel):
    """Request payload for impersonation."""

    target_uid: str


class ImpersonationResponse(BaseModel):
    """Response containing the impersonation token."""

    access_token: str
    token_type: str = "bearer"


# CurrentUserDep imported from dependencies now


@router.post("/verify", response_model=LoginResponse)
async def verify_user_token(payload: TokenPayload, auth_service: AuthServiceDep):
    """Exchanges a Firebase ID Token (or mock token) for the Backend User Profile.

    Args:
        payload (TokenPayload): The token payload.
        auth_service (AuthServiceDep): Authentication service dependency.

    Returns:
        LoginResponse: The authenticated user profile and status.

    Raises:
        HTTPException: If the user is found in Firebase but not in the DB (404),
                       or if the token is invalid (401).
    """
    try:
        token_data = auth_service.verify_token(payload.token)
        # Fetch full profile
        user = auth_service.repo.get_by_uid(token_data.uid)

        if not user:
            # Should match logic in verify_token, handled there usually,
            # but verify_token basic returns TokenData not full User object sometimes if simplified.
            # Our service logic handles auto-registration, so user should exist.
            raise HTTPException(status_code=404, detail="User profile not initialized")

        return LoginResponse(
            user=user,
            token_valid=True,
            debug_msg="Authenticated via Firebase" if auth_service.use_firebase else "Authenticated via Mock",
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/impersonate", response_model=ImpersonationResponse)
async def impersonate_user(request: ImpersonationRequest, current_user: CurrentUserDep, auth_service: AuthServiceDep):
    """Generates an impersonation token for the target user. Requires ROOT.

    Args:
        request (ImpersonationRequest): Payload containing target_uid.
        current_user (CurrentUserDep): The requesting user (must be ROOT).
        auth_service (AuthServiceDep): Auth service.

    Returns:
        ImpersonationResponse: The access token.

    Raises:
        HTTPException: If permission denied (403) or target not found (404).
    """
    requester = auth_service.repo.get_by_uid(current_user.uid)
    if not requester or requester.role != UserRole.ROOT:
        raise HTTPException(status_code=403, detail="Only ROOT can impersonate users.")

    target = auth_service.repo.get_by_uid(request.target_uid)
    if not target:
        raise HTTPException(status_code=404, detail="Target user not found.")

    token = auth_service.create_impersonation_token(target.uid)
    return ImpersonationResponse(access_token=token)


@router.get("/roles", response_model=list[str])
async def list_available_roles():
    """List all valid User Roles.

    Used by frontend for dynamic dropdowns (Zero Hardcoding).
    """
    return [r.value for r in UserRole]


@router.post("/users", response_model=User)
async def create_user(user_data: UserCreate, current_user: CurrentUserDep, auth_service: AuthServiceDep):
    """Create a new user.

    Args:
        user_data (UserCreate): Payload for the new user.
        current_user (CurrentUserDep): The requesting user (must be ROOT, ADMIN, or MANAGER).
        auth_service (AuthServiceDep): Authentication service dependency.

    Returns:
        User: The created user profile.

    Raises:
        HTTPException: If permission denied (403) or validation fails (400).
    """
    # Authorization checks are handled inside auth_service._enforce_hierarchy,
    # but we need to fetch the full Creator User object first.
    creator_full = auth_service.repo.get_by_uid(current_user.uid)
    if not creator_full:
        raise HTTPException(status_code=401, detail="Creator not found")

    try:
        new_user = await auth_service.create_user(creator_full.uid, user_data)
        return new_user
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/organizations", response_model=Organization)
async def create_organization(org_data: OrganizationCreate, current_user: CurrentUserDep, auth_service: AuthServiceDep):
    """Create a new Tenant Organization.

    Args:
        org_data (OrganizationCreate): Payload for the new organization.
        current_user (CurrentUserDep): The requesting user (must be ROOT).
        auth_service (AuthServiceDep): Authentication service dependency.

    Returns:
        Organization: The created organization.

    Raises:
        HTTPException: If user is not ROOT (403).
    """
    creator = auth_service.repo.get_by_uid(current_user.uid)
    if not creator or creator.role != UserRole.ROOT:
        raise HTTPException(status_code=403, detail="Only Root can create Organizations.")

    try:
        return await auth_service.create_organization(creator.uid, org_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/users", response_model=list[User])
async def list_users(current_user: CurrentUserDep, auth_service: AuthServiceDep):
    """List users visible to the current user (scoped by Organization).

    Args:
        current_user (CurrentUserDep): The requesting user.
        auth_service (AuthServiceDep): Authorization service.

    Returns:
        list[User]: A list of accessible user profiles.
    """
    requester = auth_service.repo.get_by_uid(current_user.uid)
    if not requester:
        raise HTTPException(status_code=401)

    all_users = auth_service.repo.list_all()

    # 1. Root sees everyone
    if requester.role == UserRole.ROOT:
        return all_users

    # 2. Others see only their Organization
    org_users = [u for u in all_users if u.organization_id == requester.organization_id]

    if requester.role == UserRole.ADMIN:
        return org_users  # Admin sees all in org

    if requester.role == UserRole.MANAGER:
        # Managers see Users they created OR just all in org?
        # Often easier if they see all testers/viewers in Org, but let's stick to created_by for strictness OR strict hierarchy
        # Simpler SaaS Model: Manager sees all Testers/Viewers in their Org.
        return [u for u in org_users if u.role in [UserRole.MEMBER, UserRole.VIEWER, UserRole.MANAGER]]

    # Testers/Viewers see nobody
    return [requester]


@router.delete("/users/{uid}")
async def delete_user(uid: str, current_user: CurrentUserDep, auth_service: AuthServiceDep):
    """Delete a user.

    Enforces Last Admin Protection.

    Args:
        uid (str): The UID of the user to delete.
        current_user (CurrentUserDep): The requesting user (ROOT or ADMIN).
        auth_service (AuthServiceDep): Authorization service.

    Returns:
        dict: Status confirmation.

    Raises:
        HTTPException: Permission denied (403) or business logic error (400).
    """
    try:
        await auth_service.delete_user(current_user.uid, uid)
        return {"status": "deleted", "uid": uid}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        # Business logic errors (Last Admin) usually 400
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/users/{uid}", response_model=User)
async def update_user(uid: str, user_update: UserUpdate, current_user: CurrentUserDep, auth_service: AuthServiceDep):
    """Update a user (Role, Display Name, etc).

    Args:
        uid (str): The UID of the user to update.
        user_update (UserUpdate): Fields to update.
        current_user (CurrentUserDep): Requesting user.
        auth_service (AuthServiceDep): Authorization service.

    Returns:
        User: The updated user profile.
    """
    try:
        updated_user = await auth_service.update_user(current_user.uid, uid, user_update)
        return updated_user
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", response_model=User)
async def get_my_profile(current_user: CurrentUserDep, auth_service: AuthServiceDep):
    """Get the currently authenticated user's profile.

    Args:
        current_user (CurrentUserDep): The authenticated user.
        auth_service (AuthServiceDep): Auth service.

    Returns:
        User: The full user profile.
    """
    user = auth_service.repo.get_by_uid(current_user.uid)
    if not user:
        raise HTTPException(status_code=404)
    return user
