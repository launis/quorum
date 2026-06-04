import logging

from fastapi import APIRouter, status

from backend_v2.api.dependencies import AuthServiceDep, CurrentUserDep
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import Organization, OrganizationCreate, OrganizationDeleteResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/organizations", tags=["Admin IAM V2 - Organizations"])


@router.get("/", response_model=list[Organization])
async def get_all_organizations(current_user: CurrentUserDep, auth_service: AuthServiceDep) -> list[Organization]:
    """Retrieve all organizations securely evaluated by SSOT Service Layer.

    All business logic filtering based on roles or organization parameters is fully delegated
    to the injected AuthService to enforce the Anemic Routers mandate.
    """
    try:
        res: list[Organization] = await auth_service.list_organizations(current_user)  # type: ignore[attr-defined]
        return res
    except AppException as e:
        logger.error("AppException in get_all_organizations: %s", e.message, exc_info=True)
        raise
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
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        ) from e


@router.get("/{id}", response_model=Organization)
async def get_organization(id: str, current_user: CurrentUserDep, auth_service: AuthServiceDep) -> Organization:
    """Retrieve a specific organization securely via SSOT Service Layer."""
    try:
        res: Organization = await auth_service.get_organization(current_user, id)
        return res
    except AppException as e:
        logger.error("AppException in get_organization for id %s: %s", id, e.message, exc_info=True)
        raise
    except Exception as e:
        msg = f"Error retrieving organization {id}: {e}"
        logger.error(
            "[OrganizationRouter] %s: %s",
            ErrorCodes.INTERNAL_SERVER_ERROR.name,
            msg,
            exc_info=True,
            extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value, "error": str(e), "target_id": id},
        )
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        ) from e


@router.put("/{id}", response_model=Organization)
async def save_organization(
    id: str, data: OrganizationCreate, current_user: CurrentUserDep, auth_service: AuthServiceDep
) -> Organization:
    """Create or update an organization securely via SSOT Service Layer."""
    try:
        res: Organization = await auth_service.update_organization(current_user, id, data)
        return res
    except AppException as e:
        logger.error("AppException in save_organization for id %s: %s", id, e.message, exc_info=True)
        raise
    except Exception as e:
        msg = f"Error saving organization {id}: {e}"
        logger.error(
            "[OrganizationRouter] %s: %s",
            ErrorCodes.INTERNAL_SERVER_ERROR.name,
            msg,
            exc_info=True,
            extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value, "error": str(e), "target_id": id},
        )
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        ) from e


@router.delete("/{id}", response_model=OrganizationDeleteResponse)
async def delete_organization(
    id: str, current_user: CurrentUserDep, auth_service: AuthServiceDep
) -> OrganizationDeleteResponse:
    """Delete an organization from the system securely via SSOT Service Layer."""
    try:
        await auth_service.delete_organization(current_user, id)
        return OrganizationDeleteResponse(status="success", deleted_id=id)
    except AppException as e:
        logger.error("AppException in delete_organization for id %s: %s", id, e.message, exc_info=True)
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
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        ) from e
