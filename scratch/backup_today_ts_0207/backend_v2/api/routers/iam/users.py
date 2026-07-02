"""Users API Router.

Provides endpoints for managing user profiles securely.
"""

import logging

from fastapi import APIRouter

from backend_v2.api.dependencies import AuthServiceDep, CurrentUserDep
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import User, UserDeleteResponse, UserUpdate

logger = logging.getLogger(__name__)

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
        AppException: If retrieving users fails.
    """
    try:
        # AuthService implements tenant filtering internally based on current_user
        return await auth_service.list_users(current_user)
    except Exception as e:
        msg = f"Error retrieving users: {e}"
        logger.error(
            "[UserRouter] %s: %s",
            ErrorCodes.INTERNAL_SERVER_ERROR.name,
            msg,
            exc_info=True,
            extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value, "error": str(e)},
        )
        raise AppException(
            message=msg, status_code=500, details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
        ) from e


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
        ResourceNotFoundError: If the user is not found.
        PermissionDeniedError: If the requesting user lacks permissions.
        AppException: If fetching the user fails.
    """
    # Service layer ensures target user exists and current_user has right to view it
    return await auth_service.get_user(current_user, id)


@router.put("/{id}", response_model=User)
async def save_user(id: str, data: UserUpdate, current_user: CurrentUserDep, auth_service: AuthServiceDep) -> User:
    """Update a user's role or organization securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the user to update.
        data: The user data to update.
        current_user: The authenticated user making the request.
        auth_service: The authentication service dependency.

    Returns:
        The updated user profile.

    Raises:
        PermissionDeniedError: If the requesting user lacks permissions.
        ResourceNotFoundError: If the user is not found.
        AppException: If updating the user fails.
    """
    return await auth_service.update_user(current_user.id, id, data)


@router.delete("/{id}", response_model=UserDeleteResponse)
async def delete_user(id: str, current_user: CurrentUserDep, auth_service: AuthServiceDep) -> UserDeleteResponse:
    """Delete a user from the system securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the user to delete.
        current_user: The authenticated user making the request.
        auth_service: The authentication service dependency.

    Returns:
        A UserDeleteResponse indicating success.

    Raises:
        PermissionDeniedError: If the requesting user lacks permissions.
        ConflictError: If deleting the last admin.
        AppException: If deleting the user fails.
    """
    try:
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
