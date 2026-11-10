"""Token exchange, RFC 8693 break-glass impersonation, and 0.1 ms RAM JWT verification service."""

from __future__ import annotations

import asyncio
import importlib.util
import json
import logging
import secrets
import time
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Literal

import jwt
from pydantic import ValidationError

if TYPE_CHECKING:
    from backend_v2.core.redis_security import RevocationCache

if importlib.util.find_spec("firebase_admin") is not None:
    import firebase_admin
    from firebase_admin import auth as firebase_auth_module
    from firebase_admin import credentials as firebase_credentials_module
else:
    firebase_admin = None
    firebase_auth_module = None
    firebase_credentials_module = None

from backend_v2.database.interfaces import get_registered_uow_factory
from backend_v2.exceptions import (
    AppException,
    AuthenticationError,
    ConfigurationError,
    ConflictError,
    ErrorCodes,
)
from backend_v2.models.auth import (
    SystemOrganizations,
    TokenData,
    TokenExchangeRequestDTO,
    TokenExchangeResponseDTO,
    User,
    UserRole,
)
from backend_v2.models.core_base import generate_uuid7
from backend_v2.models.enums import LLMProvider
from backend_v2.services.auth.repositories import UserRepository
from backend_v2.services.auth.secret_service import SecretService
from backend_v2.settings import Settings, get_settings

logger = logging.getLogger(__name__)

__all__ = ["TokenService", "initialize_firebase_admin_from_secrets"]

_SENTINEL = object()


async def initialize_firebase_admin_from_secrets(
    secret_service: SecretService,
    settings: Settings,
) -> None:
    """Initialize the Firebase Admin SDK default app using the encrypted Vertex AI Service Account secret.

    Resolves the Root System Organization ('org_0195f3a0000070008000000000000001') 'vertex_ai'
    credential from PostgreSQL 19 tenant_secrets when use_firebase_auth is True and no default
    Firebase Admin app is initialized.

    Args:
        secret_service: SecretService bound to the active persistence port.
        settings: Active application Settings instance.

    Raises:
        ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if firebase_admin is unavailable,
            the decrypted Vertex AI secret is not valid JSON, or Certificate initialization fails,
            or with ErrorCodes.SECRET_RESOLUTION_FAILED if the secret is missing in tenant_secrets.
    """
    if not settings.use_firebase_auth:
        return
    if firebase_admin is None or firebase_credentials_module is None:
        msg = "Firebase Admin SDK is not installed, but use_firebase_auth is enabled."
        logger.error(
            "[TokenService] %s: %s",
            ErrorCodes.CONFIGURATION_ERROR.name,
            msg,
            exc_info=True,
        )
        raise ConfigurationError(
            message=msg,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )
    if firebase_admin._apps:
        return

    cred_dto = await secret_service.resolve_llm_key(
        organization_id=SystemOrganizations.ROOT_SYSTEM.value,
        provider=LLMProvider.VERTEX_AI,
    )
    raw_sa_json = cred_dto.secret_value.get_secret_value().strip()
    if not raw_sa_json.startswith("{"):
        msg = "Vertex AI secret in tenant_secrets must be a valid JSON object for Firebase Admin initialization."
        logger.error(
            "[TokenService] %s: %s",
            ErrorCodes.CONFIGURATION_ERROR.name,
            msg,
            exc_info=True,
        )
        raise ConfigurationError(
            message=msg,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )
    try:
        sa_payload: object = json.loads(raw_sa_json)
    except ValueError as exc:
        msg = "Failed to parse Vertex AI Service Account JSON for Firebase Admin initialization."
        logger.error(
            "[TokenService] %s: %s",
            ErrorCodes.CONFIGURATION_ERROR.name,
            msg,
            exc_info=True,
        )
        raise ConfigurationError(
            message=msg,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        ) from exc

    try:
        cert = firebase_credentials_module.Certificate(sa_payload)
        firebase_admin.initialize_app(cert)
        logger.info("[TokenService] Firebase Admin SDK default app initialized from encrypted tenant_secrets.")
    except AppException:
        raise
    except Exception as exc:
        msg = "Failed to initialize Firebase Admin SDK from Service Account certificate."
        logger.error(
            "[TokenService] %s: %s",
            ErrorCodes.CONFIGURATION_ERROR.name,
            msg,
            exc_info=True,
        )
        raise ConfigurationError(
            message=msg,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        ) from exc


class TokenService:
    """Service for managing authentication token exchange, impersonation, and RAM JWT verification.

    Attributes:
        repo: User repository wrapper instance.
        use_firebase: Whether Firebase Admin SDK integration is enabled.
        firebase_auth: Firebase Admin SDK auth module or test double.
        revocation_cache: Optional Redis revocation cache for kill-switch enforcement.
    """

    def __init__(
        self,
        repo: UserRepository,
        use_firebase: bool = False,
        firebase_module: Any = _SENTINEL,
        get_settings_fn: Callable[[], Settings] | None = None,
        revocation_cache: RevocationCache | None = None,
    ) -> None:
        """Initialize TokenService.

        Args:
            repo: The user repository instance.
            use_firebase: Boolean flag to enable Firebase authentication.
            firebase_module: Optional override for Firebase Admin SDK module.
            get_settings_fn: Optional callable returning application Settings.
            revocation_cache: Optional Redis revocation cache instance.
        """
        self.repo = repo
        self.use_firebase = use_firebase
        self._firebase_module = firebase_auth_module if firebase_module is _SENTINEL else firebase_module
        self._get_settings_fn = get_settings_fn
        self.revocation_cache: RevocationCache | None = revocation_cache
        self._initialized_firebase = False
        self.firebase_auth: Any = None

        if self.use_firebase:
            self._init_firebase()

    def _resolve_settings(self) -> Settings:
        """Resolve active application Settings instance.

        Returns:
            Resolved Settings instance.
        """
        if self._get_settings_fn is not None:
            return self._get_settings_fn()
        return get_settings()

    def _init_firebase(self) -> None:
        """Initialize the Firebase Admin SDK module reference."""
        if self._firebase_module:
            self.firebase_auth = self._firebase_module
            logger.info("[TokenService] Firebase Admin SDK initialized.")
            self._initialized_firebase = True
        else:
            logger.warning("[TokenService] Firebase SDK not installed. Falling back to Mock mode.")
            self.use_firebase = False

    async def exchange_firebase_token(
        self,
        payload: TokenExchangeRequestDTO,
    ) -> TokenExchangeResponseDTO:
        """Exchange an MFA-verified Firebase ID Token or headless CLI target_user_id for a Quorum Local JWT.

        Args:
            payload: Strict token exchange request DTO.

        Returns:
            TokenExchangeResponseDTO containing a 15-minute signed Quorum Local JWT and User profile.

        Raises:
            AuthenticationError: With ErrorCodes.MFA_REQUIRED if 2FA claim is missing,
                ErrorCodes.PERMISSION_DENIED if headless exchange is unauthorized,
                ErrorCodes.AUTH_TOKEN_EXPIRED if the user session is revoked, or
                ErrorCodes.AUTHENTICATION_FAILED if verification fails or user is inactive.
            ConflictError: With ErrorCodes.USER_ALREADY_ASSIGNED if pre-provisioned email is bound to another UID.
        """
        # Upgrade interactive Firebase 2FA or headless CLI credentials into a signed Quorum Local JWT.
        settings = self._resolve_settings()
        if payload.firebase_token is not None:
            if self.firebase_auth is firebase_auth_module and firebase_admin is not None and not firebase_admin._apps:
                await initialize_firebase_admin_from_secrets(
                    SecretService(uow_factory=get_registered_uow_factory()),
                    settings,
                )
            user = await self._resolve_interactive_firebase_user(payload.firebase_token, settings)
        else:
            if payload.target_user_id is None:
                logger.error(
                    "[TokenService] %s: Missing target_user_id in headless exchange.",
                    ErrorCodes.AUTHENTICATION_FAILED.name,
                    exc_info=True,
                )
                raise AuthenticationError(
                    message="Missing target_user_id in token exchange request.",
                    details={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value},
                )
            provided_secret: str | None = None
            if payload.service_auth_secret is not None:
                provided_secret = payload.service_auth_secret.get_secret_value()
            user = await self._resolve_headless_cli_user(
                payload.target_user_id,
                provided_secret,
                settings,
            )

        verified_user = await self._validate_active_user_and_revocation(user)
        expire_seconds = settings.jwt_access_token_expire_minutes * 60
        signed_jwt = self._encode_local_jwt(
            settings=settings,
            subject_id=verified_user.id,
            organization_id=verified_user.organization_id,
            role=verified_user.role,
            email=verified_user.email,
            duration_seconds=expire_seconds,
            token_type="access",
        )
        return TokenExchangeResponseDTO(
            access_token=signed_jwt,
            token_type="bearer",
            expires_in_seconds=expire_seconds,
            user=verified_user,
        )

    def _encode_local_jwt(
        self,
        *,
        settings: Settings,
        subject_id: str,
        organization_id: str | None,
        role: UserRole,
        email: str | None,
        duration_seconds: int,
        token_type: Literal["access", "impersonation"],
        actor_id: str | None = None,
    ) -> str:
        """Sign a stateless Quorum Local JWT using the configured HMAC secret and algorithm.

        Args:
            settings: Active application Settings instance.
            subject_id: Authenticated or impersonated target user Opaque Stripe ID.
            organization_id: Associated organization Opaque Stripe ID, if tenant-scoped.
            role: Effective permission role embedded in stateless claims.
            email: Associated user email address, if present.
            duration_seconds: Token validity lifetime in seconds.
            token_type: Canonical Quorum token discriminator ('access' or 'impersonation').
            actor_id: Optional RFC 8693 initiator user ID embedded under 'act.sub'.

        Returns:
            Signed Quorum Local JWT string.
        """
        now_epoch = int(time.time())
        jti_str = str(generate_uuid7())
        if actor_id is not None:
            return jwt.encode(
                {
                    "sub": subject_id,
                    "org": organization_id,
                    "role": role.value,
                    "email": email,
                    "mfa": True,
                    "jti": jti_str,
                    "iat": now_epoch,
                    "exp": now_epoch + duration_seconds,
                    "type": token_type,
                    "act": {"sub": actor_id},
                },
                settings.jwt_secret_key.get_secret_value(),
                algorithm=settings.jwt_algorithm,
            )
        return jwt.encode(
            {
                "sub": subject_id,
                "org": organization_id,
                "role": role.value,
                "email": email,
                "mfa": True,
                "jti": jti_str,
                "iat": now_epoch,
                "exp": now_epoch + duration_seconds,
                "type": token_type,
            },
            settings.jwt_secret_key.get_secret_value(),
            algorithm=settings.jwt_algorithm,
        )

    async def _resolve_interactive_firebase_user(
        self,
        firebase_token: str,
        settings: Settings,
    ) -> User | None:
        """Verify Firebase ID token, enforce mandatory 2FA, and resolve or bind the local User.

        Args:
            firebase_token: Raw Firebase ID token string.
            settings: Active application Settings instance.

        Returns:
            Resolved User domain model or None if not found.

        Raises:
            AuthenticationError: With ErrorCodes.AUTHENTICATION_FAILED if Firebase verification fails,
                or ErrorCodes.MFA_REQUIRED if mandatory 2FA second factor is absent.
            ConflictError: With ErrorCodes.USER_ALREADY_ASSIGNED if email matches a different bound UID.
        """
        if self.firebase_auth is None:
            logger.error(
                "[TokenService] %s: Firebase Admin SDK is not initialized for interactive token exchange.",
                ErrorCodes.AUTHENTICATION_FAILED.name,
                exc_info=True,
            )
            raise AuthenticationError(
                message="Firebase authentication is not available.",
                details={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value},
            )
        try:
            async with asyncio.timeout(settings.http_client_timeout_seconds):
                decoded_token = await asyncio.to_thread(self.firebase_auth.verify_id_token, firebase_token)
        except AppException:
            raise
        except Exception as exc:
            logger.error(
                "[TokenService] %s: Firebase ID token verification failed: %s",
                ErrorCodes.AUTHENTICATION_FAILED.name,
                exc,
                exc_info=True,
            )
            raise AuthenticationError(
                message="Invalid Firebase ID token.",
                details={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value},
            ) from exc

        self._enforce_firebase_mfa_claim(decoded_token, settings)
        if "uid" not in decoded_token or not decoded_token["uid"]:
            logger.error(
                "[TokenService] %s: Firebase token missing 'uid'.",
                ErrorCodes.AUTHENTICATION_FAILED.name,
                exc_info=True,
            )
            raise AuthenticationError(
                message="Invalid Firebase token: missing 'uid' claim.",
                details={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value},
            )
        firebase_uid = str(decoded_token["uid"])

        user = await self.repo.get_by_firebase_uid(firebase_uid)
        if user is not None:
            return user
        return await self._bind_preprovisioned_user_by_email(decoded_token, firebase_uid)

    def _enforce_firebase_mfa_claim(self, decoded_token: Any, settings: Settings) -> None:
        """Enforce NIST SP 800-63B AAL2 mandatory 2FA claim on decoded Firebase ID tokens.

        Args:
            decoded_token: Decoded Firebase ID token mapping.
            settings: Active application Settings instance.

        Raises:
            AuthenticationError: With ErrorCodes.MFA_REQUIRED when require_mfa is True and 2FA claim is missing.
        """
        if not settings.require_mfa:
            return
        second_factor = ""
        if "firebase" in decoded_token and decoded_token["firebase"] is not None:
            firebase_claim = decoded_token["firebase"]
            if "sign_in_second_factor" in firebase_claim and firebase_claim["sign_in_second_factor"]:
                second_factor = str(firebase_claim["sign_in_second_factor"]).strip()
        if not second_factor:
            logger.error(
                "[TokenService] %s: Interactive login rejected because firebase.sign_in_second_factor is missing.",
                ErrorCodes.MFA_REQUIRED.name,
                exc_info=True,
            )
            raise AuthenticationError(
                message="Multi-Factor Authentication (2FA) is required to establish a Quorum session.",
                details={"error_code": ErrorCodes.MFA_REQUIRED.value},
            )

    async def _bind_preprovisioned_user_by_email(
        self,
        decoded_token: Any,
        firebase_uid: str,
    ) -> User | None:
        """Bind a pre-provisioned User by verified email on first login or reject UID collisions.

        Args:
            decoded_token: Decoded Firebase ID token mapping.
            firebase_uid: Verified Firebase UID from the token.

        Returns:
            Bound User domain model if a pre-provisioned account matched, else None.

        Raises:
            ConflictError: With ErrorCodes.USER_ALREADY_ASSIGNED if the user is already bound to another UID.
        """
        email_verified = False
        if "email_verified" in decoded_token:
            email_verified = bool(decoded_token["email_verified"])
        email = ""
        if "email" in decoded_token and decoded_token["email"]:
            email = str(decoded_token["email"]).strip()
        if not email or not email_verified:
            return None

        user = await self.repo.get_by_email(email)
        if user is None:
            return None
        if user.firebase_uid is not None and user.firebase_uid != firebase_uid:
            logger.error(
                "[TokenService] %s: Pre-provisioned user %s already bound to a different Firebase UID.",
                ErrorCodes.USER_ALREADY_ASSIGNED.name,
                user.id,
                exc_info=True,
            )
            raise ConflictError(
                message="User account is already bound to a different identity provider UID.",
                details={"error_code": ErrorCodes.USER_ALREADY_ASSIGNED.value, "user_id": user.id},
            )
        if user.firebase_uid is None:
            bound_user = user.model_copy(update={"firebase_uid": firebase_uid})
            await self.repo.repo.create_user(bound_user)
            return bound_user
        return user

    async def _resolve_headless_cli_user(
        self,
        target_user_id: str,
        provided_secret: str | None,
        settings: Settings,
    ) -> User | None:
        """Validate headless CLI / E2E authorization and fetch the target User.

        Args:
            target_user_id: Target user Opaque Stripe ID.
            provided_secret: Optional shared secret string from request payload.
            settings: Active application Settings instance.

        Returns:
            Resolved User domain model or None if not found.

        Raises:
            AuthenticationError: With ErrorCodes.PERMISSION_DENIED if service_auth_secret does not match.
        """
        secret_matches = (
            provided_secret is not None
            and settings.service_auth_secret is not None
            and secrets.compare_digest(provided_secret, settings.service_auth_secret.get_secret_value())
        )
        if not secret_matches:
            logger.error(
                "[TokenService] %s: Unauthorized headless CLI token exchange attempt for user %s.",
                ErrorCodes.PERMISSION_DENIED.name,
                target_user_id,
                exc_info=True,
            )
            raise AuthenticationError(
                message="Headless token exchange is forbidden without a valid service authentication secret.",
                details={"error_code": ErrorCodes.PERMISSION_DENIED.value},
            )
        return await self.repo.get_by_id(target_user_id)

    async def _validate_active_user_and_revocation(self, user: User | None) -> User:
        """Verify that the resolved User exists, is active, is not soft-deleted, and is not revoked.

        Args:
            user: Resolved User domain model or None.

        Returns:
            Validated active User domain model.

        Raises:
            AuthenticationError: With ErrorCodes.AUTHENTICATION_FAILED if user is missing/inactive/deleted,
                or ErrorCodes.AUTH_TOKEN_EXPIRED if revoked in Redis.
        """
        if user is None or user.deleted_at is not None or not user.is_active:
            logger.error(
                "[TokenService] %s: Token exchange rejected because user is missing, inactive, or soft-deleted.",
                ErrorCodes.AUTHENTICATION_FAILED.name,
                exc_info=True,
            )
            raise AuthenticationError(
                message="User account is not found or inactive.",
                details={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value},
            )
        if self.revocation_cache is not None:
            probe_token = TokenData(
                id=user.id,
                role=user.role,
                organization_id=user.organization_id,
                email=user.email,
                mfa_verified=True,
                jti=str(generate_uuid7()),
            )
            await self.revocation_cache.assert_not_revoked(probe_token)
        return user

    def create_impersonation_token(
        self,
        target_id: str,
        duration_seconds: int | None = None,
        organization_id: str | None = None,
        role: UserRole = UserRole.MEMBER,
        email: str | None = None,
        actor_id: str | None = None,
    ) -> str:
        """Generate a signed RFC 8693 break-glass impersonation JWT.

        Args:
            target_id: Opaque Stripe ID of the target user to impersonate.
            duration_seconds: Optional token validity duration in seconds; resolves from
                Settings.jwt_access_token_expire_minutes when omitted.
            organization_id: Target user's organization ID.
            role: Target user's permission role.
            email: Target user's email address.
            actor_id: Optional RFC 8693 initiator user ID ('act.sub' claim).

        Returns:
            Signed Quorum Local JWT string.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if target_id is empty or
                duration_seconds is less than 1 second.
        """
        # Issue an RFC 8693 Section 4.1 break-glass impersonation JWT with optional actor claim.
        if not target_id or not target_id.strip():
            msg = "Target user ID cannot be empty for impersonation token creation."
            logger.error(
                "[TokenService] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        settings = self._resolve_settings()
        effective_duration = (
            settings.jwt_access_token_expire_minutes * 60 if duration_seconds is None else duration_seconds
        )
        if effective_duration < 1:
            msg = "Impersonation token duration must be at least 1 second."
            logger.error(
                "[TokenService] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        return self._encode_local_jwt(
            settings=settings,
            subject_id=target_id.strip(),
            organization_id=organization_id,
            role=role,
            email=email,
            duration_seconds=effective_duration,
            token_type="impersonation",
            actor_id=actor_id,
        )

    async def verify_token(self, token: str) -> TokenData:
        """Verify a Quorum Local JWT in RAM (< 0.1 ms) with zero database queries.

        Args:
            token: Raw Bearer JWT string.

        Returns:
            Validated TokenData instance constructed from signed stateless claims.

        Raises:
            AuthenticationError: With ErrorCodes.AUTH_TOKEN_EXPIRED if the JWT signature is expired,
                ErrorCodes.MFA_REQUIRED if require_mfa is True and mfa claim is not True, or
                ErrorCodes.AUTHENTICATION_FAILED if signature or claims are invalid.
        """
        # Verify Quorum Local JWT signature in RAM with zero database queries.
        settings = self._resolve_settings()
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key.get_secret_value(),
                algorithms=[settings.jwt_algorithm],
            )
        except jwt.ExpiredSignatureError:
            logger.error(
                "[TokenService] %s: Quorum Local JWT expired.",
                ErrorCodes.AUTH_TOKEN_EXPIRED.name,
                exc_info=True,
            )
            raise AuthenticationError(
                message="Token expired",
                details={"error_code": ErrorCodes.AUTH_TOKEN_EXPIRED.value},
            ) from None
        except jwt.PyJWTError as jwt_err:
            logger.error(
                "[TokenService] %s: Invalid JWT token: %s",
                ErrorCodes.AUTHENTICATION_FAILED.name,
                jwt_err,
                exc_info=True,
            )
            raise AuthenticationError(
                message=f"Invalid JWT token: {jwt_err}",
                details={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value},
            ) from jwt_err

        return self._hydrate_token_data_from_claims(payload, settings)

    def _hydrate_token_data_from_claims(self, payload: Any, settings: Settings) -> TokenData:
        """Validate decoded JWT claims and construct a strict TokenData model in RAM.

        Args:
            payload: Decoded JWT claim mapping.
            settings: Active application Settings instance.

        Returns:
            Validated TokenData model.

        Raises:
            AuthenticationError: With ErrorCodes.MFA_REQUIRED if MFA is missing or
                ErrorCodes.AUTHENTICATION_FAILED if required claims are missing or malformed.
        """
        if "sub" not in payload or not payload["sub"]:
            logger.error(
                "[TokenService] %s: Invalid token: missing 'sub'.",
                ErrorCodes.AUTHENTICATION_FAILED.name,
                exc_info=True,
            )
            raise AuthenticationError(
                message="Invalid internal token: missing 'sub'.",
                details={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value},
            )

        mfa_verified = False
        if "mfa" in payload:
            mfa_verified = bool(payload["mfa"])
        if settings.require_mfa and not mfa_verified:
            logger.error(
                "[TokenService] %s: Token rejected because 'mfa' claim is not True.",
                ErrorCodes.MFA_REQUIRED.name,
                exc_info=True,
            )
            raise AuthenticationError(
                message="Multi-Factor Authentication (2FA) is required.",
                details={"error_code": ErrorCodes.MFA_REQUIRED.value},
            )

        if "role" not in payload or not payload["role"]:
            logger.error(
                "[TokenService] %s: Invalid token: missing 'role'.",
                ErrorCodes.AUTHENTICATION_FAILED.name,
                exc_info=True,
            )
            raise AuthenticationError(
                message="Invalid token: missing 'role' claim.",
                details={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value},
            )

        org_val: str | None = None
        if "org" in payload and payload["org"] is not None:
            org_val = str(payload["org"])

        email_val: str | None = None
        if "email" in payload and payload["email"] is not None:
            email_val = str(payload["email"])

        jti_val: str | None = None
        if "jti" in payload and payload["jti"] is not None:
            jti_val = str(payload["jti"])

        actor_id: str | None = None
        if "act" in payload and payload["act"] is not None:
            act_claim = payload["act"]
            if "sub" in act_claim and act_claim["sub"] is not None:
                actor_id = str(act_claim["sub"])

        iat_val: int | None = None
        if "iat" in payload and payload["iat"] is not None:
            iat_val = int(payload["iat"])

        exp_val: int | None = None
        if "exp" in payload and payload["exp"] is not None:
            exp_val = int(payload["exp"])

        try:
            role_enum = UserRole(str(payload["role"]))
            return TokenData(
                id=str(payload["sub"]),
                role=role_enum,
                organization_id=org_val,
                email=email_val,
                mfa_verified=mfa_verified,
                jti=jti_val,
                actor_id=actor_id,
                iat=iat_val,
                exp=exp_val,
            )
        except (ValidationError, ValueError) as exc:
            logger.error(
                "[TokenService] %s: Malformed token claims: %s",
                ErrorCodes.AUTHENTICATION_FAILED.name,
                exc,
                exc_info=True,
            )
            raise AuthenticationError(
                message=f"Malformed token claims: {exc}",
                details={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value},
            ) from exc
