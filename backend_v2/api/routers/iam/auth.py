"""API Router for Authentication and User Management.

This module provides endpoints for user login (token verification), registration,
profile management, and organization administration.
"""

import logging

from fastapi import APIRouter, Request
from pydantic import BaseModel

from backend_v2.api.dependencies import AuthServiceDep, CurrentUserDep, RepositoryDep
from backend_v2.core.rate_limit import limiter
from backend_v2.exceptions import (
    AppException,
    AuthenticationError,
    ConflictError,
    ErrorCodes,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from backend_v2.models.auth import User, UserCreate, UserDeleteResponse, UserRole, UserUpdate

# --- Local Imports ---

logger = logging.getLogger(__name__)

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

    target_id: str


class ImpersonationResponse(BaseModel):
    """Response containing the impersonation token."""

    access_token: str
    token_type: str = "bearer"


# CurrentUserDep imported from dependencies now


@router.post("/verify", response_model=LoginResponse)
@limiter.limit("5/minute")
async def verify_user_token(request: Request, payload: TokenPayload, auth_service: AuthServiceDep) -> LoginResponse:
    """Exchanges a Firebase ID Token (or mock token) for the Backend User Profile.

    Args:
        request (Request): The HTTP Request object.
        payload (TokenPayload): The token payload.
        auth_service (AuthServiceDep): Authentication service dependency.

    Returns:
        LoginResponse: The authenticated user profile and status.

    Raises:
        HTTPException: If the user is found in Firebase but not in the DB (404),
                       or if the token is invalid (401).
    """
    try:
        token_data = await auth_service.verify_token(payload.token)
        # Fetch full profile
        user = await auth_service.repo.get_by_id(token_data.id)

        if not user:
            logger.error(
                "[AuthRouter] %s: Profile not initialized",
                ErrorCodes.AUTHENTICATION_FAILED.name,
                extra={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value},
            )
            raise AuthenticationError(
                message="Profile not initialized", details={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value}
            )

        return LoginResponse(
            user=user,
            token_valid=True,
            debug_msg="Authenticated via Firebase" if auth_service.use_firebase else "Authenticated via Mock",
        )
    except ValueError as e:
        logger.error(
            "[AuthRouter] %s: Token verification failed: %s",
            ErrorCodes.AUTH_TOKEN_EXPIRED.name,
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.AUTH_TOKEN_EXPIRED.value, "error": str(e)},
        )
        raise AuthenticationError(
            message="Invalid Token",
            details={"error_code": ErrorCodes.AUTH_TOKEN_EXPIRED.value, "original_error": str(e)},
        ) from e
    except Exception as e:
        logger.error(
            "[AuthRouter] %s: Unexpected login failure: %s",
            ErrorCodes.AUTHENTICATION_FAILED.name,
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value, "error": str(e)},
        )
        raise AppException(
            message="Login failed",
            status_code=500,
            details={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value, "original_error": str(e)},
        ) from e


@router.post("/impersonate", response_model=ImpersonationResponse)
async def impersonate_user(
    request: ImpersonationRequest, current_user: CurrentUserDep, auth_service: AuthServiceDep
) -> ImpersonationResponse:
    """Generates an impersonation token for the target user. Requires ROOT.

    Args:
        request (ImpersonationRequest): Payload containing target_id.
        current_user (CurrentUserDep): The requesting user (must be ROOT).
        auth_service (AuthServiceDep): Auth service.

    Returns:
        ImpersonationResponse: The access token.

    Raises:
        HTTPException: If permission denied (403) or target not found (404).
    """
    requester = await auth_service.repo.get_by_id(current_user.id)
    if not requester or requester.role != UserRole.ROOT:
        logger.error(
            "[AuthRouter] %s: User %s attempted to impersonate without Root",
            ErrorCodes.PERMISSION_DENIED.name,
            current_user.id,
            extra={"error_code": ErrorCodes.PERMISSION_DENIED.value, "user_id": current_user.id},
        )
        raise PermissionDeniedError(
            message="Impersonation Denied", details={"error_code": ErrorCodes.PERMISSION_DENIED.value}
        )

    target = await auth_service.repo.get_by_id(request.target_id)
    if not target:
        logger.error(
            "[AuthRouter] %s: Impersonation target %s not found",
            ErrorCodes.RESOURCE_NOT_FOUND.name,
            request.target_id,
            extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "target_id": request.target_id},
        )
        raise ResourceNotFoundError("User", request.target_id)

    token = auth_service.create_impersonation_token(target.id)
    return ImpersonationResponse(access_token=token)


@router.get("/roles", response_model=list[str])
async def list_available_roles() -> list[str]:
    """List all valid User Roles.

    Used by frontend for dynamic dropdowns (Zero Hardcoding).
    """
    return [r.value for r in UserRole]


@router.post("/users", response_model=User)
@limiter.limit("5/minute")
async def create_user(
    request: Request, user_data: UserCreate, current_user: CurrentUserDep, auth_service: AuthServiceDep
) -> User:
    """Create a new user.

    Args:
        request (Request): The HTTP Request object.
        user_data (UserCreate): Payload for the new user.
        current_user (CurrentUserDep): The requesting user (must be ROOT, ADMIN, or MANAGER).
        auth_service (AuthServiceDep): Authentication service dependency.

    Returns:
        User: The created user profile.

    Raises:
        HTTPException: If permission denied (403) or validation fails (400).
    """
    try:
        return await auth_service.create_user(current_user.id, user_data)
    except PermissionError as e:
        logger.error(
            "[AuthRouter] %s: %s",
            ErrorCodes.PERMISSION_DENIED.name,
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.PERMISSION_DENIED.value, "error": str(e)},
        )
        raise PermissionDeniedError(message=str(e), details={"error_code": ErrorCodes.PERMISSION_DENIED.value}) from e
    except ValueError as e:
        logger.error(
            "[AuthRouter] %s: %s",
            ErrorCodes.VALIDATION_FAILED.name,
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "error": str(e)},
        )
        raise AppException(
            message=str(e), status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
        ) from e
    except Exception as e:
        logger.error(
            "[AuthRouter] %s: %s",
            ErrorCodes.INTERNAL_SERVER_ERROR.name,
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value, "error": str(e)},
        )
        raise AppException(
            message="User creation failed",
            status_code=500,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value, "original_error": str(e)},
        ) from e


@router.get("/users", response_model=list[User])
async def list_users(current_user: CurrentUserDep, auth_service: AuthServiceDep) -> list[User]:
    """List users visible to the current user (scoped by Organization)."""
    return await auth_service.list_users(current_user)


@router.delete("/users/{id}", response_model=UserDeleteResponse)
async def delete_user(
    id: str, current_user: CurrentUserDep, auth_service: AuthServiceDep, repo: RepositoryDep
) -> UserDeleteResponse:
    """Delete a user.

    Enforces Last Admin Protection.

    Args:
        id (str): The UID of the user to delete.
        current_user (CurrentUserDep): The requesting user (ROOT or ADMIN).
        auth_service (AuthServiceDep): Authorization service.
        repo (RepositoryDep): Repository dependency.

    Returns:
        UserDeleteResponse: Status confirmation.

    Raises:
        HTTPException: Permission denied (403) or business logic error (400).
    """
    try:
        await auth_service.delete_user(current_user.id, id)
        return UserDeleteResponse(status="deleted", id=id)
    except PermissionError as e:
        logger.error(
            "[AuthRouter] %s: %s",
            ErrorCodes.PERMISSION_DENIED.name,
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.PERMISSION_DENIED.value, "error": str(e)},
        )
        raise PermissionDeniedError(message=str(e), details={"error_code": ErrorCodes.PERMISSION_DENIED.value}) from e
    except ValueError as e:
        logger.error(
            "[AuthRouter] %s: %s",
            ErrorCodes.VALIDATION_FAILED.name,
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "error": str(e)},
        )
        raise AppException(
            message=str(e), status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
        ) from e
    except RuntimeError as e:
        if "LAST_ADMIN_PROTECTION" in str(e):
            logger.error(
                "[AuthRouter] %s: %s",
                ErrorCodes.CONFLICT_ERROR.name,
                str(e),
                exc_info=True,
                extra={"error_code": ErrorCodes.CONFLICT_ERROR.value, "error": str(e)},
            )
            raise ConflictError(
                message="Last Admin Protection", details={"error_code": ErrorCodes.CONFLICT_ERROR.value}
            ) from e

        logger.error(
            "[AuthRouter] %s: %s",
            ErrorCodes.INTERNAL_SERVER_ERROR.name,
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value, "error": str(e)},
        )
        raise AppException(
            message="Deletion failed",
            status_code=500,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value, "original_error": str(e)},
        ) from e


@router.patch("/users/{id}", response_model=User)
async def update_user(
    id: str, user_update: UserUpdate, current_user: CurrentUserDep, auth_service: AuthServiceDep
) -> User:
    """Update a user (Role, Display Name, etc).

    Args:
        id (str): The UID of the user to update.
        user_update (UserUpdate): Fields to update.
        current_user (CurrentUserDep): Requesting user.
        auth_service (AuthServiceDep): Authorization service.

    Returns:
        User: The updated user profile.
    """
    try:
        return await auth_service.update_user(current_user.id, id, user_update)
    except PermissionError as e:
        logger.error(
            "[AuthRouter] %s: %s",
            ErrorCodes.PERMISSION_DENIED.name,
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.PERMISSION_DENIED.value, "error": str(e)},
        )
        raise PermissionDeniedError(message=str(e), details={"error_code": ErrorCodes.PERMISSION_DENIED.value}) from e
    except ValueError as e:
        logger.error(
            "[AuthRouter] %s: %s",
            ErrorCodes.RESOURCE_NOT_FOUND.name,
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "error": str(e)},
        )
        raise ResourceNotFoundError("User", id) from e
    except Exception as e:
        if "LAST_ADMIN_PROTECTION" in str(e):
            logger.error(
                "[AuthRouter] %s: %s",
                ErrorCodes.CONFLICT_ERROR.name,
                str(e),
                exc_info=True,
                extra={"error_code": ErrorCodes.CONFLICT_ERROR.value, "error": str(e)},
            )
            raise ConflictError(
                message="Last Admin Protection", details={"error_code": ErrorCodes.CONFLICT_ERROR.value}
            ) from e

        logger.error(
            "[AuthRouter] %s: %s",
            ErrorCodes.INTERNAL_SERVER_ERROR.name,
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value, "error": str(e)},
        )
        raise AppException(
            message="Update failed",
            status_code=500,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value, "original_error": str(e)},
        ) from e


@router.get("/me", response_model=User)
async def get_my_profile(current_user: CurrentUserDep, auth_service: AuthServiceDep) -> User:
    """Get the currently authenticated user's profile.

    Args:
        current_user (CurrentUserDep): The authenticated user.
        auth_service (AuthServiceDep): Auth service.

    Returns:
        User: The full user profile.
    """
    user = await auth_service.repo.get_by_id(current_user.id)
    if not user:
        logger.error(
            "[AuthRouter] %s: Profile for %s not found",
            ErrorCodes.AUTHENTICATION_FAILED.name,
            current_user.id,
            extra={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value, "user_id": current_user.id},
        )
        raise AuthenticationError(
            message="User not found", details={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value}
        )
    return user
