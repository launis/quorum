from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

# Correct Service Imports
# Correct Service Imports
from backend.services.auth import AuthService 
from backend.models.auth import UserRole, TokenData, Organization 
from backend.dependencies import get_async_repository, CurrentUserDep, AuthServiceDep
from backend.database.repository import AbstractWorkflowRepository

# --- Pydantic Models ---
class OrganizationCreate(BaseModel):
    id: Optional[str] = None  # Auto-generated if empty
    name: str
    tier: str = "standard"  # standard, premium, enterprise
    contact_email: Optional[str] = None
    settings_override: Optional[Dict[str, Any]] = None

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    tier: Optional[str] = None
    contact_email: Optional[str] = None
    settings_override: Optional[Dict[str, Any]] = None

class OrganizationResponse(BaseModel):
    id: str
    name: str
    tier: str
    contact_email: Optional[str] = None
    created_at: Optional[str] = None

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"]
)

# --- Endpoints ---

@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org: OrganizationCreate,
    user: TokenData = Depends(AuthService.require_role(UserRole.ROOT)),
    repo: AbstractWorkflowRepository = Depends(get_async_repository)
):
    """
    Create a new Tenant Organization.
    ROOT Only.
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

@router.get("/", response_model=List[OrganizationResponse])
async def list_organizations(
    user: TokenData = Depends(AuthService.require_role(UserRole.ROOT)),
    repo: AbstractWorkflowRepository = Depends(get_async_repository)
):
    """
    List all organizations.
    ROOT Only.
    """
    items = await repo.list_organizations()
    # Items are raw dicts (Documents). Wrap in Organization to apply defaults, then dump.
    return [OrganizationResponse(**Organization(**i).model_dump()) for i in items]

@router.get("/me", response_model=OrganizationResponse)
async def get_my_organization(
    user: CurrentUserDep,
    repo: AbstractWorkflowRepository = Depends(get_async_repository)
):
    """
    Get the currently logged-in user's organization metadata.
    Accessible to: ROOT, ADMIN, MEMBER (Read-Only own org)
    
    Note: ROOT does not belong to an org primarily, but if they want to see 'an' org, 
    they should use get_organization_by_id logic. This endpoint is for Tenant Context.
    """
    if not user.organization_id:
        raise HTTPException(status_code=404, detail="User is not assigned to any organization.")
    
    org_data = await repo.get_organization(user.organization_id)
    
    if not org_data:
        raise HTTPException(status_code=404, detail="Organization not found in registry.")
        
    return OrganizationResponse(**Organization(**org_data).model_dump())

@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: str,
    user: CurrentUserDep,
    repo: AbstractWorkflowRepository = Depends(get_async_repository)
):
    """
    Get specific organization details.
    ROOT: Can access any.
    ADMIN: Can access OWN org only.
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
    repo: AbstractWorkflowRepository = Depends(get_async_repository)
):
    """
    Update Organization settings.
    ROOT: Can update any.
    ADMIN: Can update OWN org only.
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
    repo: AbstractWorkflowRepository = Depends(get_async_repository),
    auth_service: AuthService = Depends(AuthServiceDep)
):
    """
    Delete an organization.
    ROOT Only.
    Protected: Cannot delete 'system' org.
    """
    if org_id == "system":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Cannot delete System Organization."
        )

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
