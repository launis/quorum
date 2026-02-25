from typing import Annotated

from fastapi import APIRouter, Depends, Query

from backend.dependencies import CurrentUserDep, get_usage_service
from backend.exceptions import PermissionDeniedError
from backend.models.auth import UserRole
from backend.models.domain.usage import UsageReport
from backend.services.usage_service import UsageService

router = APIRouter(prefix="/v1/usage", tags=["usage"])

UsageServiceDep = Annotated[UsageService, Depends(get_usage_service)]

@router.get("/system", response_model=UsageReport)
async def get_system_usage(
    user: CurrentUserDep,
    service: UsageServiceDep,
    since: str | None = Query(None, description="ISO timestamp to filter from (e.g., '2026-02-01T00:00:00Z')")
):
    """Get system-wide usage statistics (Root only)."""
    if user.role != UserRole.ROOT:
        raise PermissionDeniedError("Only ROOT users can view system-wide usage.")
    
    return await service.get_usage_report(scope="system", since=since)

@router.get("/organization/{org_id}", response_model=UsageReport)
async def get_organization_usage(
    org_id: str,
    user: CurrentUserDep,
    service: UsageServiceDep,
    since: str | None = Query(None, description="ISO timestamp to filter from")
):
    """Get usage statistics for a specific organization."""
    if user.role != UserRole.ROOT and user.organization_id != org_id:
        raise PermissionDeniedError("Cannot view usage for other organizations.")
        
    return await service.get_usage_report(scope="organization", entity_id=org_id, since=since)

@router.get("/user/{user_id}", response_model=UsageReport)
async def get_user_usage(
    user_id: str,
    user: CurrentUserDep,
    service: UsageServiceDep,
    since: str | None = Query(None, description="ISO timestamp to filter from")
):
    """Get usage statistics for a specific user."""
    if user.role != UserRole.ROOT and user.id != user_id:
        # Organization admins could potentially view their users' usage here if we extended it.
        raise PermissionDeniedError("Cannot view usage for other users.")
        
    return await service.get_usage_report(scope="user", entity_id=user_id, since=since)
