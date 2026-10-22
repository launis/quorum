"""Sovereign AuthService Facade and Auth Subpackage Root."""

from __future__ import annotations

import importlib.util
import logging
from typing import Any

if importlib.util.find_spec("firebase_admin") is not None:
    from firebase_admin import auth as firebase_auth_module
else:
    firebase_auth_module = None

from backend_v2.database.interfaces import IIdentityRepository
from backend_v2.models.auth import (
    Organization,
    OrganizationCreate,
    OrganizationUpdateDTO,
    TokenData,
    User,
    UserCreate,
    UserRole,
    UserUpdate,
)
from backend_v2.services.auth.constants import (
    JWT_ALGORITHM,
    JWT_SECRET,
    LEGACY_ROOT_MASTER_ID,
    LEGACY_SYSTEM_ORG_ID,
    LEGACY_SYSTEM_ROOT_USER_ID,
    SYSTEM_ROOT_USER_ID,
)
from backend_v2.services.auth.organization_service import OrganizationService
from backend_v2.services.auth.protocols import UserCreatorProtocol
from backend_v2.services.auth.repositories import OrganizationRepository, UserRepository
from backend_v2.services.auth.token_service import TokenService
from backend_v2.services.auth.user_service import UserService
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = [
    "AuthService",
    "JWT_ALGORITHM",
    "JWT_SECRET",
    "LEGACY_ROOT_MASTER_ID",
    "LEGACY_SYSTEM_ORG_ID",
    "LEGACY_SYSTEM_ROOT_USER_ID",
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
    ) -> None:
        """Initialize AuthService facade with immutable dependency injection.

        Args:
            repo: The underlying identity repository interface.
            use_firebase: Boolean flag to enable Firebase authentication.
            audit_service: Optional service for logging audit events.
            firebase_auth: Optional Firebase auth module or mock instance.
        """
        self.repo = UserRepository(repo)
        self.org_repo = OrganizationRepository(repo)
        self.audit_service = audit_service
        effective_firebase_module = firebase_auth if firebase_auth is not None else firebase_auth_module
        self.token_service = TokenService(
            repo=self.repo,
            use_firebase=use_firebase,
            firebase_module=effective_firebase_module,
            get_settings_fn=lambda: get_settings(),
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
        """Initializes the Firebase Admin SDK."""
        self.token_service._init_firebase()

    def create_impersonation_token(self, target_id: str, duration_seconds: int = 3600) -> str:
        """Generates a signed JWT for impersonating a user."""
        return self.token_service.create_impersonation_token(target_id=target_id, duration_seconds=duration_seconds)

    async def verify_token(self, token: str) -> TokenData:
        """Verifies a Bearer token and returns TokenData."""
        return await self.token_service.verify_token(token)

    async def create_organization(self, initiator: TokenData, org_create: OrganizationCreate) -> Organization:
        """Creates a new Tenant Organization and an initial Admin user for it."""
        return await self.org_service.create_organization(initiator=initiator, org_create=org_create)

    async def delete_organization(self, initiator: TokenData, target_org_id: str, force: bool = False) -> None:
        """Deletes an Organization."""
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
        """Creates a new user, enforcing hierarchy and tenancy."""
        return await self.user_service.create_user(creator_id=creator_id, user_data=user_data)

    async def _create_user_internal(
        self, creator_id: str, user_data: UserCreate, force_org_id: str | None = None
    ) -> User:
        """Internal method to create a user with optional forced organization."""
        return await self.user_service._create_user_internal(
            creator_id=creator_id, user_data=user_data, force_org_id=force_org_id
        )

    def _enforce_hierarchy(self, creator: User, target_role: UserRole) -> None:
        """Enforces role hierarchy rules for user creation."""
        self.user_service._enforce_hierarchy(creator=creator, target_role=target_role)

    async def _count_org_admins(self, org_id: str) -> int:
        """Counts the number of active admins in an organization."""
        return await self.user_service._count_org_admins(org_id=org_id)

    async def get_users_by_organization(self, organization_id: str) -> list[User]:
        """Async retrieval of all users for a given organization."""
        return await self.user_service.get_users_by_organization(organization_id=organization_id)

    async def delete_user(self, initiator_id: str, target_id: str) -> bool:
        """Delete a user, with Last Admin Protection."""
        return await self.user_service.delete_user(initiator_id=initiator_id, target_id=target_id)

    async def update_user(self, initiator_id: str, target_id: str, updates: UserUpdate) -> User:
        """General update method for users."""
        return await self.user_service.update_user(initiator_id=initiator_id, target_id=target_id, updates=updates)

    async def update_user_role(self, initiator_id: str, target_id: str, new_role: UserRole) -> User:
        """Updates a user's role with strict Last Admin Protection."""
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
        """Bootstraps a root user and Development Scenario (Demo Corp) if needed."""
        return await self.user_service.ensure_root_user(email=email)
