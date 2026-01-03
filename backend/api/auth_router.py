from fastapi import APIRouter, Depends, HTTPException, Header, Body
from typing import List, Annotated, Optional
from pydantic import BaseModel

from backend.dependencies import AuthServiceDep, CurrentUserDep
from backend.models.auth import User, UserCreate, UserUpdate, TokenData, UserRole, Organization, OrganizationCreate

router = APIRouter(prefix="/auth", tags=["Authentication & Users"])

class TokenPayload(BaseModel):
    token: str

class LoginResponse(BaseModel):
    user: User
    token_valid: bool
    debug_msg: Optional[str] = None

# CurrentUserDep imported from dependencies now

@router.post("/verify", response_model=LoginResponse)
async def verify_user_token(
    payload: TokenPayload,
    auth_service: AuthServiceDep
):
    """
    Exchanges a Firebase ID Token (or mock token) for the Backend User Profile (Role, etc).
    Call this immediately after Firebase Login on the client.
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
            debug_msg="Authenticated via Firebase" if auth_service.use_firebase else "Authenticated via Mock"
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/users", response_model=User)
async def create_user(
    user_data: UserCreate,
    current_user: CurrentUserDep,
    auth_service: AuthServiceDep
):
    """
    Create a new user.
    Requires Role: ROOT, ADMIN, or MANAGER.
    """
    # Authorization checks are handled inside auth_service._enforce_hierarchy,
    # but we need to fetch the full Creator User object first.
    creator_full = auth_service.repo.get_by_uid(current_user.uid)
    if not creator_full:
        raise HTTPException(status_code=401, detail="Creator not found")

    try:
        new_user = auth_service.create_user(creator_full.uid, user_data)
        return new_user
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/organizations", response_model=Organization)
async def create_organization(
    org_data: OrganizationCreate,
    current_user: CurrentUserDep,
    auth_service: AuthServiceDep
):
    """
    Create a new Tenant Organization.
    Requires Role: ROOT.
    """
    creator = auth_service.repo.get_by_uid(current_user.uid)
    if not creator or creator.role != UserRole.ROOT:
        raise HTTPException(status_code=403, detail="Only Root can create Organizations.")

    try:
        return auth_service.create_organization(creator.uid, org_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/users", response_model=List[User])
async def list_users(
    current_user: CurrentUserDep,
    auth_service: AuthServiceDep
):
    """
    List users visible to the current user (scoped by Organization).
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
        return org_users # Admin sees all in org
        
    if requester.role == UserRole.MANAGER:
        # Managers see Users they created OR just all in org?
        # Often easier if they see all testers/viewers in Org, but let's stick to created_by for strictness OR strict hierarchy
        # Simpler SaaS Model: Manager sees all Testers/Viewers in their Org.
        return [u for u in org_users if u.role in [UserRole.MEMBER, UserRole.VIEWER, UserRole.MANAGER]]
        
    # Testers/Viewers see nobody
    return [requester]

@router.delete("/users/{uid}")
async def delete_user(
    uid: str,
    current_user: CurrentUserDep,
    auth_service: AuthServiceDep
):
    """
    Delete a user.
    Requires Role: ROOT or ADMIN (within Org).
    Enforces Last Admin Protection.
    """
    try:
        auth_service.delete_user(current_user.uid, uid)
        return {"status": "deleted", "uid": uid}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        # Business logic errors (Last Admin) usually 400
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/users/{uid}", response_model=User)
async def update_user(
    uid: str,
    user_update: UserUpdate,
    current_user: CurrentUserDep,
    auth_service: AuthServiceDep
):
    """
    Update a user (Role, Display Name, etc).
    Requires Role: ROOT or ADMIN (within Org).
    Enforces Last Admin Protection if demoting an Admin.
    """
    try:
        updated_user = auth_service.update_user(current_user.uid, uid, user_update)
        return updated_user
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me", response_model=User)
async def get_my_profile(
    current_user: CurrentUserDep,
    auth_service: AuthServiceDep
):
    user = auth_service.repo.get_by_uid(current_user.uid)
    if not user:
        raise HTTPException(status_code=404)
    return user
