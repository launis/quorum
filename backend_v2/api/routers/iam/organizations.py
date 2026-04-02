import logging

from fastapi import APIRouter
from pydantic import BaseModel

from backend_v2.api.dependencies import AuthServiceDep, CurrentUserDep
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import Organization, OrganizationCreate


class OrganizationDeleteResponse(BaseModel):
    status: str
    deleted_id: str


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
        logger.error(
            "[OrganizationRouter] %s: %s",
            ErrorCodes.INTERNAL_SERVER_ERROR.name,
            msg,
            exc_info=True,
            extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value, "error": str(e)},
        )
        raise AppException(
            message=msg, status_code=500, details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
        ) from e


@router.get("/{id}", response_model=Organization)
async def get_organization(id: str, current_user: CurrentUserDep, auth_service: AuthServiceDep) -> Organization:
    """Retrieve a specific organization securely via SSOT Service Layer."""
    return await auth_service.get_organization(current_user, id)


@router.put("/{id}", response_model=Organization)
async def save_organization(
    id: str, data: OrganizationCreate, current_user: CurrentUserDep, auth_service: AuthServiceDep
) -> Organization:
    """Create or update an organization securely via SSOT Service Layer."""
    return await auth_service.update_organization(current_user, id, data)


@router.delete("/{id}", response_model=OrganizationDeleteResponse)
async def delete_organization(
    id: str, current_user: CurrentUserDep, auth_service: AuthServiceDep
) -> OrganizationDeleteResponse:
    """Delete an organization from the system securely via SSOT Service Layer."""
    try:
        await auth_service.delete_organization(current_user, id)
        return OrganizationDeleteResponse(status="success", deleted_id=id)
    except AppException:
        raise
    except Exception as e:
        msg = f"Error deleting organization: {e}"
        logger.error(
            "[OrganizationRouter] %s: %s",
            ErrorCodes.INTERNAL_SERVER_ERROR.name,
            msg,
            exc_info=True,
            extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value, "error": str(e), "target_id": id},
        )
        raise AppException(
            message=msg, status_code=500, details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
        ) from e
