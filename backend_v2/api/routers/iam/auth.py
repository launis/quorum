"""API Router for Authentication, Session Exchange, Logout, and RFC 8693 Impersonation.

This module provides endpoints for token exchange (`POST /exchange`), server-side
session logout (`POST /logout`), break-glass impersonation (`POST /impersonate`),
available roles enumeration (`GET /roles`), and caller profile retrieval (`GET /me`).
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Request

from backend_v2.api.dependencies import AuthServiceDep, CurrentUserDep
from backend_v2.core.rate_limit import limiter
from backend_v2.models.auth import (
    ImpersonationRequest,
    ImpersonationResponse,
    LogoutRequestDTO,
    LogoutResponseDTO,
    TokenExchangeRequestDTO,
    TokenExchangeResponseDTO,
    User,
    UserRole,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication & Users"])


@router.post("/exchange", response_model=TokenExchangeResponseDTO)
@limiter.limit("5/minute")
async def exchange_firebase_token(
    request: Request,
    payload: TokenExchangeRequestDTO,
    auth_service: AuthServiceDep,
) -> TokenExchangeResponseDTO:
    """Exchange a Firebase ID Token or headless target_user_id for a 15-minute Quorum Local JWT.

    Args:
        request: The HTTP Request object used by the rate limiter.
        payload: The token exchange request payload.
        auth_service: Authentication service dependency.

    Returns:
        TokenExchangeResponseDTO containing the signed access token and user profile.

    Raises:
        AuthenticationError: With ErrorCodes.MFA_REQUIRED, ErrorCodes.AUTHENTICATION_FAILED,
            ErrorCodes.PERMISSION_DENIED, or ErrorCodes.AUTH_TOKEN_EXPIRED when exchange fails.
        ConflictError: With ErrorCodes.USER_ALREADY_ASSIGNED on Firebase UID collision.
    """
    # Phase 2, Step 2.2: Delegate token exchange strictly to AuthService
    return await auth_service.exchange_firebase_token(payload)


@router.post("/logout", response_model=LogoutResponseDTO)
async def logout_user(
    payload: LogoutRequestDTO,
    current_user: CurrentUserDep,
    auth_service: AuthServiceDep,
) -> LogoutResponseDTO:
    """Revoke the caller's Quorum Local JWT jti and optionally revoke all active sessions.

    Args:
        payload: Logout configuration specifying whether to revoke all sessions.
        current_user: Authenticated caller token data.
        auth_service: Authentication service dependency.

    Returns:
        LogoutResponseDTO confirming token revocation.
    """
    # Phase 2, Step 2.2: Delegate server-side logout strictly to AuthService
    return await auth_service.logout(current_user, payload)


@router.post("/impersonate", response_model=ImpersonationResponse)
async def impersonate_user(
    payload: ImpersonationRequest,
    current_user: CurrentUserDep,
    auth_service: AuthServiceDep,
) -> ImpersonationResponse:
    """Generate an RFC 8693 break-glass impersonation token for the target user (requires ROOT).

    Args:
        payload: Payload containing target_id and mandatory audit reason.
        current_user: The requesting user (must possess ROOT role).
        auth_service: Authentication service dependency.

    Returns:
        ImpersonationResponse containing the 15-minute signed JWT and audit metadata.

    Raises:
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if caller is not ROOT.
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if target user does not exist.
    """
    # Phase 2, Step 2.2: Delegate RFC 8693 break-glass impersonation strictly to AuthService
    return await auth_service.impersonate_user(current_user, payload)


@router.get("/roles", response_model=list[str])
async def list_available_roles() -> list[str]:
    """List all valid User Roles for dynamic Studio UI dropdowns.

    Returns:
        List of canonical UserRole string values.
    """
    return [r.value for r in UserRole]


@router.get("/me", response_model=User)
async def get_my_profile(current_user: CurrentUserDep, auth_service: AuthServiceDep) -> User:
    """Retrieve the currently authenticated user's profile.

    Args:
        current_user: The authenticated user token data.
        auth_service: Authentication service dependency.

    Returns:
        The full User profile.

    Raises:
        AuthenticationError: With ErrorCodes.AUTHENTICATION_FAILED if the user profile is not found.
    """
    return await auth_service.get_my_profile(current_user)
