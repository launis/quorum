"""API Router for Authentication, Session Exchange, Logout, B2B Invitations, and RFC 8693 Impersonation.

This module provides endpoints for token exchange (`POST /exchange`), server-side
session logout (`POST /logout`), break-glass impersonation (`POST /impersonate`),
B2B invitation acceptance (`POST /invitations/accept`), available roles enumeration
(`GET /roles`), and caller profile retrieval (`GET /me`).
"""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Header, Query, Request

from backend_v2.api.dependencies import (
    AuthServiceDep,
    CurrentUserDep,
    TenantRateLimitServiceDep,
)
from backend_v2.models.auth import (
    ImpersonationRequest,
    ImpersonationResponse,
    InvitationAcceptRequestDTO,
    LogoutRequestDTO,
    LogoutResponseDTO,
    TokenExchangeRequestDTO,
    TokenExchangeResponseDTO,
    User,
    UserDeleteResponse,
    UserRole,
)

logger = logging.getLogger(__name__)

__all__ = [
    "accept_invitation",
    "exchange_firebase_token",
    "firebase_user_deleted_webhook",
    "get_my_profile",
    "impersonate_user",
    "list_available_roles",
    "logout_user",
    "router",
]

router = APIRouter(prefix="/auth", tags=["Authentication & Users"])


@router.post("/exchange", response_model=TokenExchangeResponseDTO)
async def exchange_firebase_token(
    request: Request,
    payload: TokenExchangeRequestDTO,
    auth_service: AuthServiceDep,
    rate_limit_service: TenantRateLimitServiceDep,
) -> TokenExchangeResponseDTO:
    """Exchange a Firebase ID Token or headless target_user_id for a 15-minute Quorum Local JWT.

    Args:
        request: The HTTP Request object used to extract the caller IP for edge rate limiting.
        payload: The token exchange request payload.
        auth_service: Authentication service dependency.
        rate_limit_service: Sliding-window tenant and auth-edge rate limit service dependency.

    Returns:
        TokenExchangeResponseDTO containing the signed access token and user profile.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED (400) if caller IP metadata is missing.
        TokenLimitExceededError: With ErrorCodes.RATE_LIMIT_EXCEEDED (429) if auth edge rate limit is exceeded.
        ServiceUnavailableError: With ErrorCodes.SERVICE_UNAVAILABLE (503) if Redis rate-limit store is unavailable.
        AuthenticationError: With ErrorCodes.MFA_REQUIRED, ErrorCodes.AUTHENTICATION_FAILED,
            ErrorCodes.PERMISSION_DENIED, or ErrorCodes.AUTH_TOKEN_EXPIRED when exchange fails.
        ConflictError: With ErrorCodes.USER_ALREADY_ASSIGNED on Firebase UID collision.
    """
    # Phase 2, Step 2: Enforce sliding-window auth-edge IP rate limit via TenantRateLimitService
    client_ip = ""
    if request.client is not None:
        client_ip = request.client.host
    await rate_limit_service.enforce_auth_edge_rate_limit(
        client_ip=client_ip,
        endpoint_scope="POST /api/v2/iam/auth/exchange",
    )
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

    Raises:
        ServiceUnavailableError: With ErrorCodes.SERVICE_UNAVAILABLE if the Redis revocation store fails.
        AppException: If upstream session revocation or audit persistence fails.
    """
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
    return await auth_service.impersonate_user(current_user, payload)


@router.post("/invitations/accept", response_model=User)
async def accept_invitation(
    payload: InvitationAcceptRequestDTO,
    current_user: CurrentUserDep,
    auth_service: AuthServiceDep,
) -> User:
    """Accept a cryptographic B2B organization invitation token.

    Args:
        payload: Validated InvitationAcceptRequestDTO containing the raw invitation token.
        current_user: Authenticated caller token data.
        auth_service: Authentication service dependency.

    Returns:
        Updated User profile assigned to the invited organization.

    Raises:
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if token is invalid.
        AppException: With ErrorCodes.INVITATION_EXPIRED if invitation has expired or been revoked.
        PermissionDeniedError: With ErrorCodes.IDENTITY_MISMATCH if caller email mismatches invitation.
        ConflictError: With ErrorCodes.USER_ALREADY_ASSIGNED on cross-tenant identity collision.
    """
    return await auth_service.org_service.accept_invitation(current_user, payload)


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


@router.post("/webhooks/firebase-user-deleted", response_model=UserDeleteResponse)
async def firebase_user_deleted_webhook(
    request: Request,
    auth_service: AuthServiceDep,
    firebase_uid: Annotated[str, Query(min_length=1, max_length=128)],
    x_quorum_webhook_signature: Annotated[str | None, Header(alias="X-Quorum-Webhook-Signature")] = None,
) -> UserDeleteResponse:
    """Process a signed Firebase user deletion webhook and execute GDPR Soft-Delete anonymization.

    Args:
        request: Incoming FastAPI Request containing optional raw webhook body.
        auth_service: Authentication service dependency.
        firebase_uid: External Firebase UID of the deleted user.
        x_quorum_webhook_signature: HMAC-SHA256 signature header verified against firebase_webhook_secret.

    Returns:
        UserDeleteResponse confirming GDPR soft-delete anonymization.

    Raises:
        AppException: With ErrorCodes.CONFIGURATION_ERROR if webhook secret is not configured.
        AuthenticationError: With ErrorCodes.AUTHENTICATION_FAILED if HMAC signature is missing or invalid.
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if user is not found.
    """
    # Validate X-Quorum-Webhook-Signature HMAC and execute GDPR soft-delete via UserService.
    raw_body = await request.body()
    return await auth_service.user_service.verify_and_soft_delete_firebase_webhook(
        firebase_uid=firebase_uid,
        signature_header=x_quorum_webhook_signature,
        raw_body=raw_body,
    )
