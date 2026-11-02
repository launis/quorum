"""Organizations API Router.

Provides canonical SSOT endpoints for managing organizations securely under `/api/v2/iam/organizations`.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter

from backend_v2.api.dependencies import AuthServiceDep, CurrentUserDep
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import Organization, OrganizationCreate, OrganizationDeleteResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/organizations", tags=["Admin IAM V2 - Organizations"])


@router.get("/", response_model=list[Organization])
async def get_all_organizations(current_user: CurrentUserDep, auth_service: AuthServiceDep) -> list[Organization]:
    """Retrieve all organizations securely evaluated by SSOT Service Layer.

    Args:
        current_user: The authenticated user making the request.
        auth_service: The authentication service dependency.

    Returns:
        A list of organizations accessible by the user.

    Raises:
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if caller lacks privileges.
        AppException: If fetching organizations fails.
    """
    # Phase 2, Step 2.2: Propagate typed AppExceptions directly without catch-all swallowing
    return await auth_service.list_organizations(current_user)


@router.get("/{id}", response_model=Organization)
async def get_organization(id: str, current_user: CurrentUserDep, auth_service: AuthServiceDep) -> Organization:
    """Retrieve a specific organization securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the organization.
        current_user: The authenticated user making the request.
        auth_service: The authentication service dependency.

    Returns:
        The requested organization.

    Raises:
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the organization is not found.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the user lacks permission to view it.
        AppException: If fetching the organization fails.
    """
    return await auth_service.get_organization(current_user, id)


@router.put("/{id}", response_model=Organization)
async def save_organization(
    id: str, data: OrganizationCreate, current_user: CurrentUserDep, auth_service: AuthServiceDep
) -> Organization:
    """Create or update an organization securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the organization.
        data: The organization data to update or create.
        current_user: The authenticated user making the request.
        auth_service: The authentication service dependency.

    Returns:
        The updated or created organization.

    Raises:
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the user lacks permission.
        AppException: If saving the organization fails.
    """
    return await auth_service.update_organization(current_user, id, data)


@router.delete("/{id}", response_model=OrganizationDeleteResponse)
async def delete_organization(
    id: str, current_user: CurrentUserDep, auth_service: AuthServiceDep
) -> OrganizationDeleteResponse:
    """Delete an organization from the system securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the organization to delete.
        current_user: The authenticated user making the request.
        auth_service: The authentication service dependency.

    Returns:
        An OrganizationDeleteResponse confirming deletion.

    Raises:
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the organization is not found.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the user lacks permission.
        AppException: If deleting the organization fails.
    """
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
