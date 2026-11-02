"""Users API Router.

Provides canonical SSOT endpoints for managing user profiles securely under `/api/v2/iam/users`.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter

from backend_v2.api.dependencies import AuthServiceDep, CurrentUserDep
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import User, UserCreate, UserDeleteResponse, UserUpdate

logger = logging.getLogger(__name__)

__all__ = [
    "create_user",
    "delete_user",
    "get_all_users",
    "get_user",
    "router",
    "save_user",
]

router = APIRouter(prefix="/users", tags=["Admin IAM V2 - Users"])


@router.get("/", response_model=list[User])
async def get_all_users(current_user: CurrentUserDep, auth_service: AuthServiceDep) -> list[User]:
    """Retrieve all users securely evaluated by SSOT Service Layer.

    Args:
        current_user: The authenticated user making the request.
        auth_service: The authentication service dependency.

    Returns:
        A list of users accessible by the current user.

    Raises:
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if caller lacks privileges.
        AppException: With ErrorCodes.INTERNAL_SERVER_ERROR if retrieving users fails.
    """
    # Propagate typed AppExceptions directly without catch-all swallowing
    return await auth_service.list_users(current_user)


@router.post("/", response_model=User)
async def create_user(
    data: UserCreate,
    current_user: CurrentUserDep,
    auth_service: AuthServiceDep,
) -> User:
    """Create a new user profile securely via the canonical Users SSOT router.

    Args:
        data: The user creation payload.
        current_user: The authenticated user making the request.
        auth_service: The authentication service dependency.

    Returns:
        The created User profile.

    Raises:
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if caller lacks privileges.
        AppException: With ErrorCodes.VALIDATION_FAILED, ErrorCodes.RESOURCE_NOT_FOUND, or
            ErrorCodes.INTERNAL_SERVER_ERROR on invalid input or provisioning failure.
    """
    # Delegate user creation to the canonical AuthService layer
    return await auth_service.create_user(current_user.id, data)


@router.get("/{id}", response_model=User)
async def get_user(id: str, current_user: CurrentUserDep, auth_service: AuthServiceDep) -> User:
    """Retrieve a specific user profile securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the user to retrieve.
        current_user: The authenticated user making the request.
        auth_service: The authentication service dependency.

    Returns:
        The requested user profile.

    Raises:
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the user is not found.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the requesting user lacks permissions.
        AppException: With ErrorCodes.INTERNAL_SERVER_ERROR if fetching the user fails.
    """
    return await auth_service.get_user(current_user, id)


@router.put("/{id}", response_model=User)
async def save_user(id: str, data: UserUpdate, current_user: CurrentUserDep, auth_service: AuthServiceDep) -> User:
    """Update a user's role or profile attributes securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the user to update.
        data: The user data to update.
        current_user: The authenticated user making the request.
        auth_service: The authentication service dependency.

    Returns:
        The updated user profile.

    Raises:
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the requesting user lacks permissions.
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the user is not found.
        ConflictError: With ErrorCodes.CONFLICT_ERROR if Last Admin Protection is triggered.
        AppException: With ErrorCodes.RESOURCE_NOT_FOUND or ErrorCodes.INTERNAL_SERVER_ERROR if updating fails.
    """
    return await auth_service.update_user(current_user.id, id, data)


@router.delete("/{id}", response_model=UserDeleteResponse)
async def delete_user(id: str, current_user: CurrentUserDep, auth_service: AuthServiceDep) -> UserDeleteResponse:
    """Execute in-place GDPR Soft-Delete anonymization on a user securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the user to soft-delete.
        current_user: The authenticated user making the request.
        auth_service: The authentication service dependency.

    Returns:
        A UserDeleteResponse indicating success.

    Raises:
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the requesting user lacks permissions.
        ConflictError: With ErrorCodes.CONFLICT_ERROR if deleting the last admin.
        AppException: With ErrorCodes.RESOURCE_NOT_FOUND or ErrorCodes.INTERNAL_SERVER_ERROR if deleting fails.
    """
    try:
        # Execute in-place GDPR Soft-Delete anonymization via SSOT Service Layer
        await auth_service.delete_user(current_user.id, id)
        return UserDeleteResponse(status="success", id=id)
    except AppException:
        raise
    except Exception as e:
        msg = f"Error deleting user: {e}"
        logger.error(
            "[UserRouter] %s: %s",
            ErrorCodes.INTERNAL_SERVER_ERROR.name,
            msg,
            exc_info=True,
            extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value, "error": str(e), "target_id": id},
        )
        raise AppException(
            message=msg, status_code=500, details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
        ) from e
