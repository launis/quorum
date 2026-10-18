"""Token verification and impersonation token service."""

from __future__ import annotations

import importlib.util
import logging
import time
from datetime import datetime, timezone
from typing import Any

import jwt

if importlib.util.find_spec("firebase_admin") is not None:
    from firebase_admin import auth as firebase_auth_module
else:
    firebase_auth_module = None

from backend_v2.exceptions import AuthenticationError, ErrorCodes
from backend_v2.models.auth import TokenData, User, UserRole
from backend_v2.models.enums import SystemLocale
from backend_v2.services.auth.constants import JWT_ALGORITHM, JWT_SECRET
from backend_v2.services.auth.repositories import UserRepository
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = ["TokenService"]

_SENTINEL = object()


class TokenService:
    """Service for managing authentication tokens, impersonation, and verification."""

    def __init__(
        self,
        repo: UserRepository,
        use_firebase: bool = False,
        firebase_module: Any = _SENTINEL,
        get_settings_fn: Any = None,
    ) -> None:
        """Initialize TokenService.

        Args:
            repo: The user repository instance.
            use_firebase: Boolean flag to enable Firebase authentication.
            firebase_module: Optional override for Firebase Admin SDK module.
            get_settings_fn: Optional callable returning application Settings.
        """
        self.repo = repo
        self.use_firebase = use_firebase
        self._firebase_module = firebase_auth_module if firebase_module is _SENTINEL else firebase_module
        self._get_settings_fn = get_settings_fn
        self._initialized_firebase = False
        self.firebase_auth: Any = None

        if self.use_firebase:
            self._init_firebase()

    def _init_firebase(self) -> None:
        """Initializes the Firebase Admin SDK.

        Returns:
            None
        """
        if self._firebase_module:
            self.firebase_auth = self._firebase_module
            logger.info("[TokenService] Firebase Admin SDK initialized.")
            self._initialized_firebase = True
        else:
            logger.warning("[TokenService] Firebase SDK not installed. Falling back to Mock mode.")
            self.use_firebase = False

    def create_impersonation_token(self, target_id: str, duration_seconds: int = 3600) -> str:
        """Generates a signed JWT for impersonating a user.

        Args:
            target_id: The UID of the user to impersonate.
            duration_seconds: Token validity duration in seconds.

        Returns:
            Signed JWT string.
        """
        payload = {
            "sub": target_id,
            "exp": time.time() + duration_seconds,
            "iat": time.time(),
            "type": "impersonation",
        }

        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token

    async def verify_token(self, token: str) -> TokenData:
        """Verifies a Bearer token.

        Args:
            token: The raw JWT token string.

        Returns:
            TokenData for the verified user.

        Raises:
            AuthenticationError: If token is invalid, expired, or forbidden.
        """
        # 1. Local Signed Token (Impersonation / Internal)
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            if "sub" not in payload or not payload["sub"]:
                logger.error(
                    "[TokenService] %s: Invalid internal token: missing 'sub'.",
                    ErrorCodes.AUTHENTICATION_FAILED.name,
                )
                raise AuthenticationError(
                    message="Invalid internal token: missing 'sub'.",
                    details={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value},
                )
            user_id = str(payload["sub"])

            user = await self.repo.get_by_id(user_id)
            if not user:
                logger.error(
                    "[TokenService] %s: Impersonated user not found: %s",
                    ErrorCodes.AUTH_TOKEN_EXPIRED.name,
                    user_id,
                )
                raise AuthenticationError(
                    message=f"Impersonated User not found: {user_id}",
                    details={"error_code": ErrorCodes.AUTH_TOKEN_EXPIRED.value},
                )
            return TokenData(id=user.id, role=user.role, email=user.email, organization_id=user.organization_id)

        except jwt.ExpiredSignatureError:
            logger.error("[TokenService] %s: Token expired.", ErrorCodes.AUTH_TOKEN_EXPIRED.name)
            raise AuthenticationError(
                message="Token expired", details={"error_code": ErrorCodes.AUTH_TOKEN_EXPIRED.value}
            ) from None

        except jwt.PyJWTError as jwt_err:
            if not self.use_firebase and not token.startswith("mock-token:"):
                logger.error(
                    "[TokenService] %s: Invalid JWT token: %s",
                    ErrorCodes.AUTHENTICATION_FAILED.name,
                    jwt_err,
                )
                raise AuthenticationError(
                    message=f"Invalid JWT token: {jwt_err}",
                    details={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value},
                ) from jwt_err
            logger.debug("PyJWT decoding failed, falling back: %s", jwt_err)

        # 2. Mock/Dev Mode check
        settings = self._get_settings_fn() if self._get_settings_fn is not None else get_settings()
        is_mock_token = token.startswith("mock-token:")

        # Reject mock tokens in production or cloud environments immediately (Fail-Fast)
        if is_mock_token and not settings.allow_mock_tokens:
            logger.error(
                "[TokenService] %s: Mock tokens are strictly forbidden in production.",
                ErrorCodes.PERMISSION_DENIED.name,
            )
            raise AuthenticationError(
                message="Mock tokens are strictly forbidden in production.",
                details={"error_code": ErrorCodes.PERMISSION_DENIED.value},
            )

        if not self.use_firebase or (is_mock_token and settings.allow_mock_tokens):
            if token.startswith("mock-token:"):
                mock_user_id = token.split(":")[1]
            else:
                mock_user_id = token

            user = await self.repo.get_by_id(mock_user_id)
            if not user:
                logger.error(
                    "[TokenService] %s: Mock User not found for ID: %s",
                    ErrorCodes.PERMISSION_DENIED.name,
                    mock_user_id,
                )
                raise AuthenticationError(
                    message=f"Mock User not found for ID: {mock_user_id}",
                    details={"error_code": ErrorCodes.PERMISSION_DENIED.value},
                )

            return TokenData(id=user.id, role=user.role, email=user.email, organization_id=user.organization_id)

        # 3. Firebase Mode
        try:
            decoded_token = self.firebase_auth.verify_id_token(token)
            firebase_user_id = decoded_token["uid"]
            email = None
            if "email" in decoded_token:
                email = decoded_token["email"]

            user = await self.repo.get_by_id(firebase_user_id)

            if not user:
                if not email:
                    logger.error(
                        "[TokenService] %s: Firebase token missing email claim.",
                        ErrorCodes.AUTHENTICATION_FAILED.name,
                    )
                    raise AuthenticationError(
                        message="Cannot auto-register user: Firebase token is missing email claim.",
                        details={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value},
                    )

                logger.info("User %s not found in local DB. Auto-registering as MEMBER (No Org).", firebase_user_id)

                new_user = User(
                    id=firebase_user_id,
                    email=email,
                    role=UserRole.MEMBER,
                    organization_id=None,
                    created_at=datetime.now(timezone.utc),
                    is_active=True,
                    language=SystemLocale.EN,
                    theme_mode="system",
                )

                await self.repo.create(new_user)
                return TokenData(id=firebase_user_id, role=UserRole.MEMBER, email=email, organization_id=None)

            return TokenData(id=user.id, role=user.role, email=user.email, organization_id=user.organization_id)

        except AuthenticationError:
            raise
        except Exception as e:
            logger.error("[TokenService] %s: %s", ErrorCodes.AUTHENTICATION_FAILED.name, e, exc_info=True)
            raise AuthenticationError(
                message="Invalid credentials", details={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value}
            ) from e
