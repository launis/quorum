"""Sovereign AuthService Facade and Auth Subpackage Root."""

from __future__ import annotations

import asyncio
import importlib.util
import logging
import time
from typing import Any

if importlib.util.find_spec("firebase_admin") is not None:
    from firebase_admin import auth as firebase_auth_module
else:
    firebase_auth_module = None

from backend_v2.database.interfaces import EntityPersistencePort, IIdentityRepository
from backend_v2.exceptions import AuthenticationError, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import (
    SYSTEM_ROOT_USER_ID as SYSTEM_ROOT_USER_ID,
)
from backend_v2.models.auth import (
    ImpersonationRequest,
    ImpersonationResponse,
    LogoutRequestDTO,
    LogoutResponseDTO,
    Organization,
    OrganizationCreate,
    OrganizationUpdateDTO,
    TokenData,
    TokenExchangeRequestDTO,
    TokenExchangeResponseDTO,
    User,
    UserCreate,
    UserRole,
    UserUpdate,
)
from backend_v2.models.core_base import generate_uuid7
from backend_v2.services.auth.email_service import EmailService as EmailService
from backend_v2.services.auth.organization_service import OrganizationService
from backend_v2.services.auth.protocols import UserCreatorProtocol
from backend_v2.services.auth.repositories import OrganizationRepository, UserRepository
from backend_v2.services.auth.token_service import TokenService
from backend_v2.services.auth.user_service import UserService
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)
_FIREBASE_LOGOUT_TIMEOUT_SECONDS: float = 10.0
__all__ = [
    "AuthService",
    "EmailService",
    "OrganizationRepository",
    "OrganizationService",
    "SYSTEM_ROOT_USER_ID",
    "TokenService",
    "UserCreatorProtocol",
    "UserRepository",
    "UserService",
]


class AuthService:
    """Sovereign Auth Service facade orchestrating Token, Org, and User subservices."""

    def __init__(
        self,
        repo: IIdentityRepository,
        use_firebase: bool = False,
        audit_service: Any = None,
        firebase_auth: Any = None,
        revocation_cache: Any = None,
        email_service: EmailService | None = None,
        entity_adapter: EntityPersistencePort | None = None,
    ) -> None:
        """Initialize AuthService facade with immutable dependency injection."""
        self.repo = UserRepository(repo)
        self.org_repo = OrganizationRepository(repo)
        self.audit_service = audit_service
        self.revocation_cache = revocation_cache
        effective_fb = firebase_auth if firebase_auth is not None else firebase_auth_module
        self.token_service = TokenService(
            repo=self.repo,
            use_firebase=use_firebase,
            firebase_module=effective_fb,
            get_settings_fn=lambda: get_settings(),
            revocation_cache=revocation_cache,
        )
        if firebase_auth is not None:
            self.token_service.firebase_auth = firebase_auth
        self.user_service = UserService(
            user_repo=self.repo,
            org_repo=self.org_repo,
            audit_service=self.audit_service,
            use_firebase=use_firebase,
            firebase_auth=self.token_service.firebase_auth,
        )
        self.org_service = OrganizationService(
            org_repo=self.org_repo,
            user_repo=self.repo,
            audit_service=self.audit_service,
            use_firebase=use_firebase,
            firebase_auth=self.token_service.firebase_auth,
            user_creator=self.user_service._create_user_internal,
            email_service=email_service,
            entity_adapter=entity_adapter,
        )

    @property
    def use_firebase(self) -> bool:
        """Whether Firebase authentication is enabled."""
        return self.token_service.use_firebase

    @property
    def firebase_auth(self) -> Any:
        """Firebase auth module or mock instance."""
        return self.token_service.firebase_auth

    @property
    def _initialized_firebase(self) -> bool:
        """Whether Firebase SDK has been initialized."""
        return self.token_service._initialized_firebase

    def _init_firebase(self) -> None:
        """Initialize the Firebase Admin SDK."""
        self.token_service._init_firebase()

    def create_impersonation_token(self, target_id: str, duration_seconds: int = 3600) -> str:
        """Generate a signed JWT for impersonating a user."""
        return self.token_service.create_impersonation_token(target_id=target_id, duration_seconds=duration_seconds)

    async def exchange_firebase_token(self, payload: TokenExchangeRequestDTO) -> TokenExchangeResponseDTO:
        """Exchange a Firebase ID token or headless target_user_id for a Quorum Local JWT."""
        return await self.token_service.exchange_firebase_token(payload)

    async def verify_token(self, token: str) -> TokenData:
        """Verify a Bearer token and return TokenData."""
        return await self.token_service.verify_token(token)

    async def logout(self, current_user: TokenData, payload: LogoutRequestDTO) -> LogoutResponseDTO:
        """Revoke the caller's JWT jti and optionally revoke all active sessions for the user."""
        now_epoch = int(time.time())
        remaining_ttl = 900 if current_user.exp is None else max(1, min(900, current_user.exp - now_epoch))
        revoked_jti = str(generate_uuid7()) if current_user.jti is None else current_user.jti
        if self.revocation_cache is not None:
            await self.revocation_cache.revoke_token_jti(revoked_jti, ttl_seconds=remaining_ttl)
        if payload.revoke_all_sessions:
            if self.revocation_cache is not None:
                await self.revocation_cache.revoke_user_sessions(current_user.id, ttl_seconds=900)
            if self.use_firebase and self.token_service.firebase_auth is not None:
                user = await self.repo.get_by_id(current_user.id)
                if user is not None and user.firebase_uid is not None:
                    fb_auth = self.token_service.firebase_auth
                    async with asyncio.timeout(_FIREBASE_LOGOUT_TIMEOUT_SECONDS):
                        await asyncio.to_thread(fb_auth.revoke_refresh_tokens, user.firebase_uid)
        if self.audit_service is not None:
            details = {"revoked_jti": revoked_jti, "all_sessions_revoked": payload.revoke_all_sessions}
            await self.audit_service.log_event(
                actor_id=current_user.id,
                action="USER_LOGGED_OUT",
                organization_id=current_user.organization_id,
                target_id=current_user.id,
                details=details,
            )
        return LogoutResponseDTO(
            status="logged_out", revoked_jti=revoked_jti, all_sessions_revoked=payload.revoke_all_sessions
        )

    async def impersonate_user(self, initiator: TokenData, payload: ImpersonationRequest) -> ImpersonationResponse:
        """Issue an RFC 8693 break-glass impersonation token for a target user (requires ROOT)."""
        if initiator.role != UserRole.ROOT:
            err_code = ErrorCodes.PERMISSION_DENIED
            logger.error("[AuthService] %s: Non-ROOT impersonation by %s.", err_code.name, initiator.id)
            raise PermissionDeniedError("Impersonation Denied", details={"error_code": err_code.value})
        target = await self.repo.get_by_id(payload.target_id)
        if target is None:
            logger.error("[AuthService] %s: Target %s missing.", ErrorCodes.RESOURCE_NOT_FOUND.name, payload.target_id)
            raise ResourceNotFoundError("User", payload.target_id)
        token = self.token_service.create_impersonation_token(
            target_id=target.id,
            duration_seconds=900,
            organization_id=target.organization_id,
            role=target.role,
            email=target.email,
            actor_id=initiator.id,
        )
        if self.audit_service is not None:
            await self.audit_service.log_event(
                actor_id=initiator.id,
                action="USER_IMPERSONATION_STARTED",
                organization_id=target.organization_id,
                target_id=target.id,
                details={"reason": payload.reason},
            )
        return ImpersonationResponse(
            access_token=token, token_type="bearer", target_id=target.id, reason=payload.reason
        )

    async def get_my_profile(self, current_user: TokenData) -> User:
        """Retrieve the authenticated caller's User profile from persistence."""
        user = await self.repo.get_by_id(current_user.id)
        if user is None:
            err_code = ErrorCodes.AUTHENTICATION_FAILED
            logger.error("[AuthService] %s: Profile for %s not found.", err_code.name, current_user.id)
            raise AuthenticationError("User not found", details={"error_code": err_code.value})
        return user

    async def create_organization(self, initiator: TokenData, org_create: OrganizationCreate) -> Organization:
        """Create a new Tenant Organization and an initial Admin user for it."""
        return await self.org_service.create_organization(initiator=initiator, org_create=org_create)

    async def delete_organization(self, initiator: TokenData, target_org_id: str, force: bool = False) -> None:
        """Delete an Organization."""
        await self.org_service.delete_organization(initiator=initiator, target_org_id=target_org_id, force=force)

    async def list_organizations(self, initiator: TokenData) -> list[Organization]:
        """List organizations securely scoped by Tenant/Organization."""
        return await self.org_service.list_organizations(initiator=initiator)

    async def get_organization(self, initiator: TokenData, org_id: str) -> Organization:
        """Fetch organization securely."""
        return await self.org_service.get_organization(initiator=initiator, org_id=org_id)

    async def update_organization(
        self, initiator: TokenData, org_id: str, data: OrganizationUpdateDTO | OrganizationCreate
    ) -> Organization:
        """Update an organization securely."""
        return await self.org_service.update_organization(initiator=initiator, org_id=org_id, data=data)

    async def create_user(self, creator_id: str, user_data: UserCreate) -> User:
        """Create a new user, enforcing hierarchy and tenancy."""
        return await self.user_service.create_user(creator_id=creator_id, user_data=user_data)

    async def _create_user_internal(
        self, creator_id: str, user_data: UserCreate, force_org_id: str | None = None
    ) -> User:
        """Create a user internally with optional forced organization."""
        return await self.user_service._create_user_internal(
            creator_id=creator_id, user_data=user_data, force_org_id=force_org_id
        )

    def _enforce_hierarchy(self, creator: User, target_role: UserRole) -> None:
        """Enforce role hierarchy rules for user creation."""
        self.user_service._enforce_hierarchy(creator=creator, target_role=target_role)

    async def _count_org_admins(self, org_id: str) -> int:
        """Count the number of active admins in an organization."""
        return await self.user_service._count_org_admins(org_id=org_id)

    async def get_users_by_organization(self, organization_id: str) -> list[User]:
        """Retrieve all users for a given organization."""
        return await self.user_service.get_users_by_organization(organization_id=organization_id)

    async def delete_user(self, initiator_id: str, target_id: str) -> bool:
        """Delete a user with Last Admin Protection."""
        return await self.user_service.delete_user(initiator_id=initiator_id, target_id=target_id)

    async def update_user(self, initiator_id: str, target_id: str, updates: UserUpdate) -> User:
        """Update user fields with RBAC validation."""
        return await self.user_service.update_user(initiator_id=initiator_id, target_id=target_id, updates=updates)

    async def update_user_role(self, initiator_id: str, target_id: str, new_role: UserRole) -> User:
        """Update a user's role with strict Last Admin Protection."""
        return await self.user_service.update_user_role(
            initiator_id=initiator_id, target_id=target_id, new_role=new_role
        )

    async def list_users(self, initiator: TokenData) -> list[User]:
        """List users securely scoped by Tenant/Organization."""
        return await self.user_service.list_users(initiator=initiator)

    async def get_user(self, initiator: TokenData, target_id: str) -> User:
        """Fetch user securely."""
        return await self.user_service.get_user(initiator=initiator, target_id=target_id)

    async def ensure_root_user(self, email: str = "root@example.com") -> User:
        """Bootstrap a root user and Development Scenario (Demo Corp) if needed."""
        return await self.user_service.ensure_root_user(email=email)
