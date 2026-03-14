import logging
from typing import Any

from fastapi import APIRouter

from backend_v2.api.dependencies import AuthServiceDep, CurrentUserDep
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import Organization, OrganizationCreate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/organizations", tags=["Admin IAM V2 - Organizations"])

@router.get("/", response_model=list[Organization])
async def get_all_organizations(current_user: CurrentUserDep, auth_service: AuthServiceDep) -> list[Organization]:
    """Retrieve all organizations securely evaluated by SSOT Service Layer."""
    try:
        # Subject to Root-only visibility in practice, or own-org
        if current_user.role != "ROOT":
            org = await auth_service.get_organization(current_user, getattr(current_user, "organization_id", ""))
            return [org] if org else []
        return await auth_service.org_repo.list_all()
    except Exception as e:
        msg = f"Error retrieving organizations: {e}"
        logger.error(f"[OrganizationRouter] {ErrorCodes.INTERNAL_SERVER_ERROR.name}: {msg}", exc_info=True)
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
        ) from e

@router.get("/{id}", response_model=Organization)
async def get_organization(id: str, current_user: CurrentUserDep, auth_service: AuthServiceDep) -> Organization:
    """Retrieve a specific organization securely via SSOT Service Layer."""
    return await auth_service.get_organization(current_user, id)

@router.put("/{id}", response_model=Organization)
async def save_organization(id: str, data: OrganizationCreate, current_user: CurrentUserDep, auth_service: AuthServiceDep) -> Organization:
    """Create or update an organization securely via SSOT Service Layer."""
    # Strict fallback for creation vs update handled by underlying repo, shielded by Service guards
    existing = await auth_service.org_repo.get_by_id(id)
    if existing:
        await auth_service.org_repo.repo.update_organization(id, data.model_dump(exclude_unset=True))
        return await auth_service.get_organization(current_user, id)
    else:
        return await auth_service.create_organization(current_user, data)

@router.delete("/{id}")
async def delete_organization(id: str, current_user: CurrentUserDep, auth_service: AuthServiceDep) -> dict[str, Any]:
    """Delete an organization from the system securely via SSOT Service Layer."""
    await auth_service.delete_organization(current_user, id)
    return {"status": "success", "deleted_id": id}
