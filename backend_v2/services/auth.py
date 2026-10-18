"""Authentication and User Management Service."""

from __future__ import annotations

import asyncio
import importlib.util
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

if importlib.util.find_spec("firebase_admin") is not None:
    from firebase_admin import auth as firebase_auth_module
else:
    firebase_auth_module = None

from pathlib import Path

from backend_v2.database.interfaces import IIdentityRepository
from backend_v2.exceptions import (
    AppException,
    ConflictError,
    ErrorCodes,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from backend_v2.models.auth import (
    Organization,
    OrganizationCreate,
    OrganizationUpdateDTO,
    SubscriptionStatus,
    SystemOrganizations,
    TokenData,
    User,
    UserCreate,
    UserRole,
    UserUpdate,
)
from backend_v2.models.enums import SystemLocale
from backend_v2.settings import get_settings

__path__ = [str(Path(__file__).parent / "auth")]

from backend_v2.services.auth.constants import (
    JWT_ALGORITHM as JWT_ALGORITHM,
)
from backend_v2.services.auth.constants import (
    JWT_SECRET as JWT_SECRET,
)
from backend_v2.services.auth.constants import (
    LEGACY_ROOT_MASTER_ID as LEGACY_ROOT_MASTER_ID,
)
from backend_v2.services.auth.constants import (
    LEGACY_SYSTEM_ORG_ID as LEGACY_SYSTEM_ORG_ID,
)
from backend_v2.services.auth.constants import (
    LEGACY_SYSTEM_ROOT_USER_ID as LEGACY_SYSTEM_ROOT_USER_ID,
)
from backend_v2.services.auth.constants import (
    SYSTEM_ROOT_USER_ID as SYSTEM_ROOT_USER_ID,
)
from backend_v2.services.auth.repositories import (
    OrganizationRepository as OrganizationRepository,
)
from backend_v2.services.auth.repositories import (
    UserRepository as UserRepository,
)
from backend_v2.services.auth.token_service import (
    TokenService as TokenService,
)

logger = logging.getLogger(__name__)

__all__ = [
    "JWT_ALGORITHM",
    "JWT_SECRET",
    "LEGACY_ROOT_MASTER_ID",
    "LEGACY_SYSTEM_ORG_ID",
    "LEGACY_SYSTEM_ROOT_USER_ID",
    "SYSTEM_ROOT_USER_ID",
    "AuthService",
    "OrganizationRepository",
    "TokenService",
    "UserRepository",
]


# --- Service Layer ---


class AuthService:
    """Hybrid Auth Service with Multi-Tenancy (SaaS)."""

    def __init__(self, repo: IIdentityRepository, use_firebase: bool = False, audit_service: Any = None):
        """Initialize AuthService.

        Args:
            repo: The underlying identity repository interface.
            use_firebase: Boolean flag to enable Firebase authentication.
            audit_service: Optional service for logging audit events.
        """
        self.repo = UserRepository(repo)
        self.org_repo = OrganizationRepository(repo)
        self.audit_service = audit_service  # Typed as Any to avoid circular import if strict
        self.token_service = TokenService(
            repo=self.repo,
            use_firebase=use_firebase,
            firebase_module=firebase_auth_module,
            get_settings_fn=lambda: get_settings(),
        )

    @property
    def use_firebase(self) -> bool:
        """Whether Firebase authentication is enabled."""
        return self.token_service.use_firebase

    @use_firebase.setter
    def use_firebase(self, value: bool) -> None:
        self.token_service.use_firebase = value

    @property
    def firebase_auth(self) -> Any:
        """Firebase auth module or mock instance."""
        return self.token_service.firebase_auth

    @firebase_auth.setter
    def firebase_auth(self, value: Any) -> None:
        self.token_service.firebase_auth = value

    @property
    def _initialized_firebase(self) -> bool:
        """Whether Firebase SDK has been initialized."""
        return self.token_service._initialized_firebase

    @_initialized_firebase.setter
    def _initialized_firebase(self, value: bool) -> None:
        self.token_service._initialized_firebase = value

    def _init_firebase(self) -> None:
        """Initializes the Firebase Admin SDK.

        Returns:
            None
        """
        self.token_service._init_firebase()

    def create_impersonation_token(self, target_id: str, duration_seconds: int = 3600) -> str:
        """Generates a signed JWT for impersonating a user.

        Args:
            target_id: The UID of the user to impersonate.
            duration_seconds: Token validity duration in seconds.

        Returns:
            Signed JWT string.
        """
        return self.token_service.create_impersonation_token(target_id=target_id, duration_seconds=duration_seconds)

    async def verify_token(self, token: str) -> TokenData:
        """Verifies a Bearer token.

        Args:
            token: The raw JWT token string.

        Returns:
            TokenData for the verified user.

        Raises:
            AuthenticationError: If token is invalid or expired.
        """
        return await self.token_service.verify_token(token)

    async def create_organization(self, initiator: TokenData, org_create: OrganizationCreate) -> Organization:
        """Creates a new Tenant Organization and an initial Admin user for it.

        Strictly Async.

        Args:
            initiator: Token data of the user creating the organization.
            org_create: The organization creation payload.

        Returns:
            The newly created organization.

        Raises:
            PermissionDeniedError: If the initiator is not ROOT.
            AppException: If the creation fails.
        """
        if initiator.role != UserRole.ROOT:
            raise PermissionDeniedError("Only ROOT can create organizations.")

        # 1. Create Organization (Sync DB call in thread? Or just sync for now)
        # We'll run it sync as TinyDB is fast, but logically the method is async.
        org_id = f"org_{uuid.uuid4().hex}"

        new_org = Organization(
            id=org_id,
            name=org_create.name,
            created_at=datetime.now(timezone.utc),
            is_active=True,
            tier="enterprise",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=500.0,
            tpm_limit=50000,
            rpm_limit=500,
        )

        await self.org_repo.create(new_org)

        # 2. Create the Org Admin
        admin_payload = UserCreate(
            email=org_create.admin_email,
            password=org_create.admin_password,
            name=org_create.admin_name,
            role=UserRole.ADMIN,
            organization_id=org_id,
            is_active=True,
            language=SystemLocale.EN,
            theme_mode="system",
        )

        # Bypass hierarchy check since we are ROOT acting explicitly
        await self._create_user_internal(initiator.id, admin_payload, force_org_id=org_id)

        # Audit
        if self.audit_service:
            await self.audit_service.log_event(
                actor_id=initiator.id,
                action="ORG_CREATED",
                organization_id=org_id,
                target_id=org_id,
                details={"name": new_org.name, "tier": new_org.tier},
            )

        return new_org

    async def create_user(self, creator_id: str, user_data: UserCreate) -> User:
        """Creates a new user, enforcing hierarchy and tenancy.

        Args:
            creator_id: The UID of the user initiating the creation.
            user_data: The user creation payload.

        Returns:
            The newly created user.

        Raises:
            AppException: If the creator is not found or target org does not exist.
            PermissionDeniedError: If hierarchy constraints are violated.
        """
        return await self._create_user_internal(creator_id, user_data)

    async def _create_user_internal(
        self, creator_id: str, user_data: UserCreate, force_org_id: str | None = None
    ) -> User:
        """Internal method to create a user with optional forced organization.

        Args:
            creator_id: The UID of the user initiating the creation.
            user_data: The user creation payload.
            force_org_id: Optional organization ID to bypass standard derivation.

        Returns:
            The newly created user.

        Raises:
            AppException: If creator is not found or Firebase fails.
            PermissionDeniedError: If hierarchy or org constraints are violated.
        """
        creator = await self.repo.get_by_id(creator_id)

        if not creator:
            raise AppException(
                message="Creator not found",
                status_code=404,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )

        target_org_id: str | None = None

        # Resolve Org ID
        if force_org_id:
            target_org_id = force_org_id
        elif creator.role == UserRole.ROOT:
            target_org_id = (
                user_data.organization_id if user_data.organization_id is not None else creator.organization_id
            )
        else:
            if user_data.organization_id and user_data.organization_id != creator.organization_id:
                raise PermissionDeniedError("Cannot create users in other organizations.")
            target_org_id = creator.organization_id

        if user_data.role == UserRole.ROOT:
            if target_org_id != SystemOrganizations.ROOT_SYSTEM:
                raise PermissionDeniedError("Root users can only be created within the System Organization.")
            target_org_id = SystemOrganizations.ROOT_SYSTEM  # Redundant safety, but ensures it matches

        # RULE: Organization MUST exist
        if target_org_id:
            if target_org_id == SystemOrganizations.ROOT_SYSTEM:
                # System org acts as a special bootstrap case, but usually should exist.
                pass

            org_exists = await self.org_repo.get_by_id(target_org_id)

            if not org_exists and target_org_id != SystemOrganizations.ROOT_SYSTEM:
                logger.error(
                    "[AuthService] %s: Target Organization '%s' does not exist.",
                    ErrorCodes.VALIDATION_FAILED.name,
                    target_org_id,
                )
                raise AppException(
                    message=f"Target Organization '{target_org_id}' does not exist.",
                    status_code=404,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

        # Enforce Role Hierarchy
        self._enforce_hierarchy(creator, user_data.role)

        new_id = ""

        # 1. Create in Firebase (if enabled)
        if self.use_firebase and user_data.password:
            try:
                fb_user = self.firebase_auth.create_user(
                    email=user_data.email, password=user_data.password, name=user_data.name
                )
                new_id = fb_user.id
            except Exception as e:
                # Check for existing
                try:
                    # Logic to reuse existing...
                    existing = self.firebase_auth.get_user_by_email(user_data.email)
                    new_id = existing.id
                    logger.info("User %s already in Firebase. Using existing UID.", user_data.email)
                except Exception:
                    logger.error(
                        "[AuthService] %s: Failed to create Firebase user: %s",
                        ErrorCodes.INTERNAL_SERVER_ERROR.name,
                        e,
                        exc_info=True,
                    )
                    raise AppException(
                        message=f"Failed to create Firebase user: {e}",
                        status_code=500,
                        details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                    ) from e
        else:
            # Generate a mock UID
            new_id = f"local_{uuid.uuid4().hex[:8]}"

        # 2. Create in Local DB
        new_user = User(
            id=new_id,
            email=user_data.email,
            name=user_data.name,
            role=user_data.role,
            organization_id=target_org_id,
            created_at=datetime.now(timezone.utc),
            created_by=creator.id,
            is_active=user_data.is_active,
            language=user_data.language,
            theme_mode=user_data.theme_mode,
        )

        saved_user = await self.repo.create(new_user)

        # Audit
        if self.audit_service:
            await self.audit_service.log_event(
                actor_id=creator_id,
                action="USER_CREATED",
                organization_id=target_org_id,
                target_id=new_id,
                details={"email": new_user.email, "role": new_user.role.value},
            )

        return saved_user

    def _enforce_hierarchy(self, creator: User, target_role: UserRole) -> None:
        """Enforces role hierarchy rules for user creation.

        Args:
            creator: The user attempting to create another user.
            target_role: The role being assigned to the new user.

        Raises:
            PermissionDeniedError: If the creator lacks sufficient privileges.
        """
        if creator.role == UserRole.ROOT:
            return

        if creator.role == UserRole.ADMIN:
            if target_role == UserRole.ROOT:
                raise PermissionDeniedError("Admins cannot create Roots.")
            return

        if creator.role == UserRole.MANAGER:
            raise PermissionDeniedError("Managers are Technical Leads and cannot manage users. Ask an Admin.")

        if creator.role == UserRole.MEMBER:
            raise PermissionDeniedError("This user role cannot create users")

        raise PermissionDeniedError("This user role cannot create users")

    async def _count_org_admins(self, org_id: str) -> int:
        """Counts the number of active admins in an organization.

        Args:
            org_id: The ID of the organization.

        Returns:
            The number of admin users.
        """
        if not org_id:
            return 0

        all_users = await self.repo.list_all()
        return sum(1 for u in all_users if u.organization_id == org_id and u.role == UserRole.ADMIN)

    async def get_users_by_organization(self, organization_id: str) -> list[User]:
        """Async retrieval of all users for a given organization.

        Args:
            organization_id: The target organization ID.

        Returns:
            A list of users belonging to the organization.
        """
        return await self.repo.get_by_organization(organization_id)

    async def delete_user(self, initiator_id: str, target_id: str) -> bool:
        """Delete a user, with Last Admin Protection.

        Args:
            initiator_id: The UID of the user attempting deletion.
            target_id: The UID of the user to delete.

        Returns:
            True if deletion was successful.

        Raises:
            AppException: If either user is not found.
            PermissionDeniedError: If permissions are insufficient or target is protected.
            ConflictError: If deleting the user violates Last Admin Protection.
        """
        logger.info("[AuthService] delete_user called. Initiator: %s, Target: %s", initiator_id, target_id)

        # Run Read operations in thread
        initiator = await self.repo.get_by_id(initiator_id)
        target = await self.repo.get_by_id(target_id)

        if not initiator or not target:
            raise AppException(
                message="User not found",
                status_code=404,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )

        # Permission Check
        if initiator.role != UserRole.ROOT:
            if initiator.role == UserRole.ADMIN:
                if target.organization_id != initiator.organization_id:
                    raise PermissionDeniedError("Cannot delete users from other organizations")
            else:
                raise PermissionDeniedError("Insufficient permissions to delete users")

        # ROOT PROTECTION
        if target_id in (LEGACY_ROOT_MASTER_ID, SYSTEM_ROOT_USER_ID, LEGACY_SYSTEM_ROOT_USER_ID):
            raise PermissionDeniedError("The primary Root account cannot be deleted.")

        # LAST ADMIN PROTECTION
        if target.role == UserRole.ADMIN and target.organization_id:
            # Run Admin Count in thread -> Count iterates list_all
            admin_count = await self._count_org_admins(target.organization_id)

            if admin_count <= 1:
                logger.error(
                    "[AuthService] %s: Cannot delete the last Administrator of an Organization.",
                    ErrorCodes.CONFLICT_ERROR.name,
                )
                raise ConflictError(
                    message="LAST_ADMIN_PROTECTION: Cannot delete the last Administrator of an Organization. "
                    "Promote another user first.",
                    details={"error_code": ErrorCodes.CONFLICT_ERROR.value, "reason": "LAST_ADMIN_PROTECTION"},
                )

        # Execute
        # 1. Firebase (if enabled)
        if self.use_firebase:
            try:
                logger.info("[AuthService] Deleting Firebase user %s...", target.id)
                await asyncio.to_thread(self.firebase_auth.delete_user, target.id)
            except (AppException, OSError, ValueError, KeyError, RuntimeError, TypeError) as e:
                if isinstance(e, (KeyboardInterrupt, SystemExit)):
                    raise
                logger.warning("Firebase delete failed (might be local user): %s", e)

        # 2. Local DB
        logger.info("[AuthService] Deleting Local DB user %s...", target_id)
        await self.repo.delete(target_id)

        # Audit
        if self.audit_service:
            await self.audit_service.log_event(
                actor_id=initiator_id,
                action="USER_DELETED",
                organization_id=target.organization_id,
                target_id=target_id,
                details={"email": target.email},
            )

        return True

    async def delete_organization(self, initiator: TokenData, target_org_id: str, force: bool = False) -> None:
        """Deletes an Organization.

        Safety Rules:
        - Cannot delete 'system' organization.
        - Cannot delete non-empty organization unless force=True.
        - force=True cascades delete to all users.

        Args:
            initiator: Token data of the user deleting the organization.
            target_org_id: The ID of the organization to delete.
            force: If True, cascades deletion to all users in the org.

        Raises:
            PermissionDeniedError: If the initiator is not ROOT or targets system org.
            ConflictError: If the organization is not empty and force is False.
        """
        logger.info(
            "[AuthService] delete_organization called. Initiator: %s, Target: %s, Force: %s",
            initiator.id,
            target_org_id,
            force,
        )

        if initiator.role != UserRole.ROOT:
            raise PermissionDeniedError("Only ROOT can delete organizations.")

        if target_org_id == SystemOrganizations.ROOT_SYSTEM or target_org_id == LEGACY_SYSTEM_ORG_ID:
            raise PermissionDeniedError("CRITICAL: The 'system' organization is protected and CANNOT be deleted.")

        # 2. Check Users
        logger.info("[AuthService] Fetching users to check for safety...")

        all_users = await self.repo.list_all()
        org_users = [u for u in all_users if u.organization_id == target_org_id]

        user_count = len(org_users)
        logger.info("[AuthService] Organization %s has %s users.", target_org_id, user_count)

        if user_count > 0 and not force:
            logger.error(
                "[AuthService] %s: Organization is not empty (%s users). Use force=True to delete.",
                ErrorCodes.CONFLICT_ERROR.name,
                user_count,
            )
            raise ConflictError(
                message=f"Organization is not empty ({user_count} users). Use force=True to delete.",
                details={"error_code": ErrorCodes.CONFLICT_ERROR.value, "reason": "ORG_NOT_EMPTY", "count": user_count},
            )

        # 3. Delete Logic (Cascading)
        if user_count > 0:
            logger.info("[AuthService] FORCE DELETE enabled. Removing %s users...", user_count)
            for user in org_users:
                if self.use_firebase:
                    try:
                        await asyncio.to_thread(self.firebase_auth.delete_user, user.id)
                    except (AppException, OSError, ValueError, KeyError, RuntimeError, TypeError) as fb_err:
                        if isinstance(fb_err, (KeyboardInterrupt, SystemExit)):
                            raise
                        logger.warning("Failed to cascade delete user %s in Firebase: %s", user.id, fb_err)

                await self.repo.delete(user.id)

        # 4. Delete Org Entity
        logger.info("[AuthService] Removing Organization %s from DB...", target_org_id)
        await self.org_repo.repo.delete_organization(target_org_id)

        # Audit
        if self.audit_service:
            await self.audit_service.log_event(
                actor_id=initiator.id,
                action="ORG_DELETED",
                organization_id=target_org_id,
                target_id=target_org_id,
                details={"users_deleted": user_count, "force_used": force},
            )

    async def update_user(self, initiator_id: str, target_id: str, updates: UserUpdate) -> User:
        """General update method for users.

        If 'role' is being changed, we must enforce Last Admin Protection.

        Args:
            initiator_id: The UID of the user initiating the update.
            target_id: The UID of the user to update.
            updates: The update payload.

        Returns:
            The updated user model.

        Raises:
            AppException: If user not found.
            PermissionDeniedError: If hierarchy or org constraints are violated.
            ConflictError: If Last Admin Protection is violated.
        """
        initiator = await self.repo.get_by_id(initiator_id)
        target = await self.repo.get_by_id(target_id)

        if not initiator or not target:
            raise AppException(
                message="User not found",
                status_code=404,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )

        # Permission Check
        if initiator.role != UserRole.ROOT:
            # Self-Update Rule (Language/Theme)
            if initiator_id == target_id:
                # Allowed to update self, but check for Restricted fields (Role)
                if updates.role is not None and updates.role != initiator.role:
                    raise PermissionDeniedError("Users cannot change their own role.")

            # Org Admin Check
            elif initiator.role == UserRole.ADMIN:
                if target.organization_id != initiator.organization_id:
                    raise PermissionDeniedError("Cannot update users from other organizations")

            else:
                raise PermissionDeniedError("Insufficient permissions to update users")

        # Organization Change Protection (Only ROOT can move users)
        if updates.organization_id is not None and updates.organization_id != target.organization_id:
            if initiator.role != UserRole.ROOT:
                raise PermissionDeniedError("Only ROOT can transfer users between organizations.")

        # LAST ADMIN PROTECTION (Role Change)
        if updates.role is not None and target.role == UserRole.ADMIN:
            # If we are changing FROM Admin TO something else
            if updates.role != UserRole.ADMIN:
                if target.organization_id:
                    admin_count = await self._count_org_admins(target.organization_id)

                    if admin_count <= 1:
                        logger.error(
                            "[AuthService] %s: Cannot demote the last Administrator of an Organization.",
                            ErrorCodes.CONFLICT_ERROR.name,
                        )
                        raise ConflictError(
                            message="LAST_ADMIN_PROTECTION: Cannot demote the last Administrator of an Organization.",
                            details={"error_code": ErrorCodes.CONFLICT_ERROR.value, "reason": "LAST_ADMIN_PROTECTION"},
                        )

        updated_user = await self.repo.update(target_id, updates)

        if not updated_user:
            logger.error(
                "[AuthService] %s: User update failed (not found despite check).", ErrorCodes.INTERNAL_SERVER_ERROR.name
            )
            raise AppException(
                message="User update failed (not found despite check).",
                status_code=500,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
            )

        # Audit
        if self.audit_service:
            # Determine what changed for details
            changed_fields = updates.model_dump(exclude_unset=True)

            await self.audit_service.log_event(
                actor_id=initiator_id,
                action="USER_UPDATED",
                organization_id=target.organization_id,  # Log under target's org
                target_id=target_id,
                details=changed_fields,
            )

        return updated_user

    async def update_user_role(self, initiator_id: str, target_id: str, new_role: UserRole) -> User:
        """Updates a user's role with strict Last Admin Protection.

        Args:
            initiator_id: The UID of the user changing the role.
            target_id: The UID of the user whose role is changing.
            new_role: The new role to assign.

        Returns:
            The updated user model.

        Raises:
            PermissionDeniedError: If hierarchy is violated.
            AppException: If user not found.
            ConflictError: If Last Admin Protection is triggered.
        """
        initiator = await self.repo.get_by_id(initiator_id)
        target = await self.repo.get_by_id(target_id)

        if not initiator or not target:
            raise AppException(
                message="User not found",
                status_code=404,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )

        # 1. Access Control (Hierarchy)
        if initiator.role != UserRole.ROOT:
            # Check privileges: Initiator >= Target AND Initiator >= New Role
            # Roles are Enums, but we can compare values if defined, or explicitly check.
            # Hierarchy: ROOT > ADMIN > MANAGER > MEMBER
            # Simple int mapping for comparison
            role_values = {
                UserRole.ROOT: 40,
                UserRole.ADMIN: 30,
                UserRole.MANAGER: 20,
                UserRole.MEMBER: 10,
                UserRole.VIEWER: 5,  # Assuming VIEWER exists or mapping it low
            }

            init_val = 0
            if initiator.role in role_values:
                init_val = role_values[initiator.role]
            target_val = 0
            if target.role in role_values:
                target_val = role_values[target.role]
            new_val = 0
            if new_role in role_values:
                new_val = role_values[new_role]

            if init_val < target_val:
                raise PermissionDeniedError("Cannot modify users with higher or equal privileges.")

            if init_val < new_val:
                raise PermissionDeniedError("Cannot promote user to a role higher than your own.")

            # Org Constraint
            if initiator.role == UserRole.ADMIN:
                if target.organization_id != initiator.organization_id:
                    raise PermissionDeniedError("Cannot manage users in other organizations.")

        # 2. Last Admin Protection
        if target.role == UserRole.ADMIN and new_role != UserRole.ADMIN:
            if target.organization_id:
                count = await self._count_org_admins(target.organization_id)

                if count <= 1:
                    logger.error(
                        "[AuthService] %s: LAST_ADMIN_PROTECTION: Cannot demote the last Administrator.",
                        ErrorCodes.CONFLICT_ERROR.name,
                    )
                    raise ConflictError(
                        message="LAST_ADMIN_PROTECTION: Cannot demote the last Administrator.",
                        details={"error_code": ErrorCodes.CONFLICT_ERROR.value, "reason": "LAST_ADMIN_PROTECTION"},
                    )

        # 3. Apply Update
        updated = await self.repo.update(target_id, UserUpdate(role=new_role))

        if not updated:
            logger.error(
                "[AuthService] %s: User update failed (user reference lost).", ErrorCodes.INTERNAL_SERVER_ERROR.name
            )
            raise AppException(
                message="User update failed (user reference lost).",
                status_code=500,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
            )

        # 4. Audit
        if self.audit_service:
            await self.audit_service.log_event(
                actor_id=initiator_id,
                action="USER_ROLE_UPDATED",
                organization_id=target.organization_id,
                target_id=target_id,
                details={"old_role": target.role.value, "new_role": new_role.value},
            )

        return updated

    # --- Tenant Isolation Wrappers for Routers ---

    async def list_users(self, initiator: TokenData) -> list[User]:
        """List users securely scoped by Tenant/Organization.

        Args:
            initiator: The token data of the user requesting the list.

        Returns:
            A list of users scoped to the initiator's permissions.
        """
        all_users: list[User] = await self.repo.list_all()

        if initiator.role == UserRole.ROOT:
            return all_users

        org_id = initiator.organization_id
        return [u for u in all_users if u.organization_id == org_id]

    async def list_organizations(self, initiator: TokenData) -> list[Organization]:
        """List organizations securely scoped by Tenant/Organization.

        Args:
            initiator: The token data of the user requesting the list.

        Returns:
            A list of organizations scoped to the initiator's permissions.
        """
        if initiator.role != UserRole.ROOT:
            if not initiator.organization_id:
                return []
            org = await self.get_organization(initiator, initiator.organization_id)
            if org:
                return [org]
            return []
        return await self.org_repo.list_all()

    async def get_user(self, initiator: TokenData, target_id: str) -> User:
        """Fetch user securely.

        Args:
            initiator: The token data of the user requesting the fetch.
            target_id: The UID of the user to fetch.

        Returns:
            The requested user model.

        Raises:
            ResourceNotFoundError: If the user does not exist.
            PermissionDeniedError: If the initiator lacks access.
        """
        user = await self.repo.get_by_id(target_id)

        if not user:
            raise ResourceNotFoundError(resource_type="user", resource_id=target_id)

        # Tenant Isolation
        if initiator.role == UserRole.ROOT:
            return user

        if initiator.id == target_id:
            return user

        if initiator.role == UserRole.ADMIN and user.organization_id == initiator.organization_id:
            return user

        raise PermissionDeniedError("You do not have permission to view this user.")

    async def get_organization(self, initiator: TokenData, org_id: str) -> Organization:
        """Fetch organization securely.

        Args:
            initiator: The token data of the user requesting the fetch.
            org_id: The ID of the organization to fetch.

        Returns:
            The requested organization model.

        Raises:
            ResourceNotFoundError: If the organization does not exist.
            PermissionDeniedError: If the initiator lacks access.
        """
        org = await self.org_repo.get_by_id(org_id)

        if not org:
            raise ResourceNotFoundError(resource_type="organization", resource_id=org_id)

        # Tenant Isolation
        if initiator.role != UserRole.ROOT and initiator.organization_id != org_id:
            logger.warning("[AuthService] PERMISSION_DENIED: %s tried to read foreign org %s", initiator.id, org_id)
            raise PermissionDeniedError("You do not have permission to view this organization.")

        return org

    async def update_organization(
        self, initiator: TokenData, org_id: str, data: OrganizationUpdateDTO | OrganizationCreate
    ) -> Organization:
        """Update an organization securely.

        Args:
            initiator: The token data of the user initiating the update.
            org_id: The ID of the organization to update.
            data: The update payload.

        Returns:
            The updated organization model.

        Raises:
            PermissionDeniedError: If the initiator is not ROOT.
            ResourceNotFoundError: If the organization does not exist.
        """
        if initiator.role != UserRole.ROOT:
            raise PermissionDeniedError("Only ROOT can update organizations.")

        # Verify it exists
        await self.get_organization(initiator, org_id)

        update_dto = (
            data
            if isinstance(data, OrganizationUpdateDTO)
            else OrganizationUpdateDTO(
                name=data.name,
                tpm_limit=data.tpm_limit,
                rpm_limit=data.rpm_limit,
            )
        )
        await self.org_repo.repo.update_organization(org_id, update_dto)

        return await self.get_organization(initiator, org_id)

    async def ensure_root_user(self, email: str = "root@example.com") -> User:
        """Bootstraps a root user and Development Scenario (Demo Corp) if needed.

        Args:
            email: Default email for root user if creation was supported.

        Returns:
            The root User object.

        Raises:
            AppException: If the root user is missing from the database.
        """
        # 0. Ensure SYSTEM Org exists (Container for Root)
        # Note: Must use model_dump(mode="json") to avoid datetime serialization errors
        if not await self.org_repo.get_by_id(SystemOrganizations.ROOT_SYSTEM):
            logger.info("[AuthService] Creating 'system' Organization.")

            await self.org_repo.create(
                Organization(
                    id=SystemOrganizations.ROOT_SYSTEM,
                    name="System Administration",
                    created_at=datetime.now(timezone.utc),
                    is_active=True,
                    tier="enterprise",
                    subscription_status=SubscriptionStatus.ACTIVE,
                    quota_limit=5000.0,
                    tpm_limit=50000,
                    rpm_limit=500,
                )
            )

        # 1. ROOT
        root = await self.repo.get_by_id(SYSTEM_ROOT_USER_ID)

        if not root:
            logger.critical(
                "[AuthService] %s: No Root user found in database! Strict Authority Enforced.",
                ErrorCodes.CONFIGURATION_ERROR.name,
            )

            raise AppException(
                message="Root user 'root_master' missing from DB. Run 'python -m backend_v2.seed.run_seed local'.",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        if root.organization_id not in [
            SystemOrganizations.ROOT_SYSTEM,
            LEGACY_SYSTEM_ORG_ID,
        ]:
            # Fix casing or drift if it was "SYSTEM" or None
            logger.info(
                "Fixing root_master organization_id from "
                f"'{root.organization_id}' to '{SystemOrganizations.ROOT_SYSTEM}'"
            )

            await self.repo.update(
                SYSTEM_ROOT_USER_ID,
                UserUpdate(organization_id=SystemOrganizations.ROOT_SYSTEM),
            )

            root = await self.repo.get_by_id(SYSTEM_ROOT_USER_ID)  # Refresh

        if not root:
            logger.error("[AuthService] %s: Failed to obtain Root user.", ErrorCodes.INTERNAL_SERVER_ERROR.name)
            raise AppException(
                message="Failed to obtain Root user.",
                status_code=500,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
            )

        return root
