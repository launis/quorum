"""Authentication and User Management Service."""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any

import jwt

try:
    from firebase_admin import auth as firebase_auth_module
except ImportError:
    firebase_auth_module = None

from backend_v2.database.interfaces import IIdentityRepository
from backend_v2.exceptions import (
    AppException,
    AuthenticationError,
    ConflictError,
    ErrorCodes,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from backend_v2.models.auth import (
    Organization,
    OrganizationCreate,
    SubscriptionStatus,
    SystemOrganizations,
    TokenData,
    User,
    UserCreate,
    UserRole,
    UserUpdate,
)

# Secure Secret for Local Tokens (Impersonation)
# In production, this MUST be set via environment variable.
JWT_SECRET = "cognitive-quorum-internal-secret-change-me"
JWT_ALGORITHM = "HS256"

# Constants for System Root Entities
SYSTEM_ROOT_USER_ID = "10fb2f60-5ee1-419f-a16c-b5cfdfc5f55b"
LEGACY_SYSTEM_ORG_ID = "436d84de-c526-43b7-93ef-634912be0d2f"
LEGACY_ROOT_MASTER_ID = "root_master"

logger = logging.getLogger(__name__)


# --- Repository Layer (Organization) ---


class OrganizationRepository:
    """Repository for Organization data access."""

    def __init__(self, repo: IIdentityRepository):
        """Initializes the Organization repository wrapper.

        Args:
            repo: The underlying identity repository interface.
        """
        self.repo = repo

    async def get_by_id(self, org_id: str) -> Organization | None:
        """Fetches an organization by its ID.

        Args:
            org_id: The ID of the organization to fetch.

        Returns:
            The Organization object if found, else None.
        """
        data = await self.repo.get_organization(org_id)
        if data:
            return Organization.model_validate(data, strict=False)
        return None

    async def create(self, org: Organization) -> Organization:
        """Creates a new organization in the database.

        Args:
            org: The Organization object to create.

        Returns:
            The created Organization object.
        """
        await self.repo.create_organization(org.model_dump(mode="json"))
        return org

    async def list_all(self) -> list[Organization]:
        """Lists all organizations.

        Returns:
            A list of all Organization objects.
        """
        results = []
        for o in await self.repo.list_organizations():
            results.append(Organization.model_validate(o, strict=False))
        return results


# --- Repository Layer (User) ---


class UserRepository:
    """Repository for User data access."""

    def __init__(self, repo: IIdentityRepository):
        """Initializes the User repository wrapper.

        Args:
            repo: The underlying identity repository interface.
        """
        self.repo = repo

    async def get_by_id(self, id: str) -> User | None:
        """Fetches a user by their ID.

        Args:
            id: The ID of the user to fetch.

        Returns:
            The User object if found, else None.
        """
        data = await self.repo.get_user(id)
        return User.model_validate(data, strict=False) if data else None

    async def get_by_email(self, email: str) -> User | None:
        """Fetches a user by their email address.

        Args:
            email: The email address of the user.

        Returns:
            The User object if found, else None.
        """
        data = await self.repo.get_user_by_email(email)
        return User.model_validate(data, strict=False) if data else None

    async def create(self, user: User) -> User:
        """Creates a new user in the database.

        Args:
            user: The User object to create.

        Returns:
            The created User object.

        Raises:
            AppException: If a user with the same ID already exists.
        """
        if await self.get_by_id(user.id):
            raise AppException(f"User with ID {user.id} already exists.", 409)

        await self.repo.create_user(user.model_dump(mode="json"))
        return user

    async def update(self, id: str, updates: UserUpdate) -> User | None:
        """Updates an existing user.

        Args:
            id: The ID of the user to update.
            updates: The update payload.

        Returns:
            The updated User object if successful, else None.
        """
        user = await self.get_by_id(id)

        if not user:
            return None

        update_data = updates.model_dump(exclude_unset=True)
        if update_data:
            await self.repo.update_user(id, update_data)

        return await self.get_by_id(id)

    async def list_all(self) -> list[User]:
        """Lists all users.

        Returns:
            A list of all User objects.
        """
        return [User.model_validate(u, strict=False) for u in await self.repo.list_users()]

    async def delete(self, id: str) -> bool:
        """Deletes a user by their ID.

        Args:
            id: The ID of the user to delete.

        Returns:
            True if deletion was successful, False otherwise.
        """
        return await self.repo.delete_user(id)

    async def get_by_organization(self, org_id: str) -> list[User]:
        """Fetches all users belonging to a specific organization.

        Args:
            org_id: The ID of the organization.

        Returns:
            A list of User objects.
        """
        return [User.model_validate(u, strict=False) for u in await self.repo.list_users(org_id)]


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
        self.use_firebase = use_firebase
        self.audit_service = audit_service  # Typed as Any to avoid circular import if strict
        self._initialized_firebase = False

        if self.use_firebase:
            self._init_firebase()

    def _init_firebase(self) -> None:
        """Initializes the Firebase Admin SDK.

        Returns:
            None
        """
        if firebase_auth_module:
            self.firebase_auth = firebase_auth_module
            logger.info("[AuthService] Firebase Admin SDK initialized.")
            self._initialized_firebase = True
        else:
            logger.warning("[AuthService] Firebase SDK not installed. Falling back to Mock mode.")
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
            AuthenticationError: If token is invalid or expired.
        """
        # 1. Local Signed Token (Impersonation / Internal)
        try:
            # We enforce the secret check here.
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            id = payload.get("sub")
            if not id:
                raise AuthenticationError(
                    message="Invalid internal token: missing 'sub'.", details={"error_code": "INVALID_TOKEN"}
                )

            user = await self.repo.get_by_id(id)
            if not user:
                raise AuthenticationError(
                    message=f"Impersonated User not found: {id}",
                    details={"error_code": ErrorCodes.AUTH_TOKEN_EXPIRED},
                )
            return TokenData(id=user.id, role=user.role, email=user.email, organization_id=user.organization_id)

        except jwt.ExpiredSignatureError:
            raise AuthenticationError(
                message="Token expired", details={"error_code": ErrorCodes.AUTH_TOKEN_EXPIRED}
            ) from None

        except jwt.PyJWTError as jwt_err:
            logger.debug("PyJWT decoding failed, falling back: %s", jwt_err)

        # 2. Mock/Dev Mode check
        if not self.use_firebase or token.startswith("mock-token:"):
            # Expect format "mock-token:<id>"
            if token.startswith("mock-token:"):
                id = token.split(":")[1]
            else:
                id = token

            # Check if user exists in our DB
            user = await self.repo.get_by_id(id)
            if not user:
                raise AuthenticationError(
                    message=f"Mock User not found for ID: {id}",
                    details={"error_code": ErrorCodes.PERMISSION_DENIED},  # Or similar
                )

            return TokenData(id=user.id, role=user.role, email=user.email, organization_id=user.organization_id)

        # 2. Firebase Mode
        try:
            # Verify ID token
            decoded_token = self.firebase_auth.verify_id_token(token)
            id = decoded_token["uid"]
            email = decoded_token.get("email")

            # Sync/Get User from our DB
            user = await self.repo.get_by_id(id)

            if not user:
                # Auto-registration for missing users found in Firebase
                if not email:
                    raise AuthenticationError(
                        message="Cannot auto-register user: Firebase token is missing email claim.",
                        details={"error_code": "AUTH_TOKEN_MISSING_EMAIL"},
                    )

                logger.info("User %s not found in local DB. Auto-registering as MEMBER (No Org).", id)

                new_user = User(
                    id=id,
                    email=email,
                    role=UserRole.MEMBER,
                    organization_id=None,  # Orphan user
                    created_at=datetime.now(timezone.utc),
                    is_active=True,
                    language="en",
                    theme_mode="system",
                    # Created by System/Self
                )

                await self.repo.create(new_user)
                return TokenData(id=id, role=UserRole.MEMBER, email=email, organization_id=None)

            return TokenData(id=user.id, role=user.role, email=user.email, organization_id=user.organization_id)

        except Exception as e:
            error_code = "AUTH_TOKEN_VERIFICATION_FAILED"
            logger.error("%s: %s", error_code, e, exc_info=True)
            raise AuthenticationError(message="Invalid credentials", details={"error_code": error_code}) from e

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
            language="en",
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
            raise AppException(message="Creator not found", status_code=404)

        target_org_id: str | None = None

        # Resolve Org ID
        if force_org_id:
            target_org_id = force_org_id
        elif creator.role == UserRole.ROOT:
            target_org_id = user_data.organization_id or creator.organization_id
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
                raise AppException(
                    message=f"Target Organization '{target_org_id}' does not exist.",
                    status_code=404,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED},
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
                        details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR},
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
            raise AppException(message="User not found", status_code=404)

        # Permission Check
        if initiator.role != UserRole.ROOT:
            if initiator.role == UserRole.ADMIN:
                if target.organization_id != initiator.organization_id:
                    raise PermissionDeniedError("Cannot delete users from other organizations")
            else:
                raise PermissionDeniedError("Insufficient permissions to delete users")

        # ROOT PROTECTION
        if target_id == LEGACY_ROOT_MASTER_ID or target_id == SYSTEM_ROOT_USER_ID:
            raise PermissionDeniedError("The primary Root account cannot be deleted.")

        # LAST ADMIN PROTECTION
        if target.role == UserRole.ADMIN and target.organization_id:
            # Run Admin Count in thread -> Count iterates list_all
            admin_count = await self._count_org_admins(target.organization_id)

            if admin_count <= 1:
                raise ConflictError(
                    message="LAST_ADMIN_PROTECTION: Cannot delete the last Administrator of an Organization. "
                    "Promote another user first.",
                    details={"error_code": "LAST_ADMIN_PROTECTION"},
                )

        # Execute
        # 1. Firebase (if enabled)
        if self.use_firebase:
            try:
                logger.info("[AuthService] Deleting Firebase user %s...", target.id)
                await asyncio.to_thread(self.firebase_auth.delete_user, target.id)
            except Exception as e:
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
            "[AuthService] delete_organization called. Initiator: %s, ",
            initiator.id,
            f"Target: {target_org_id}, Force: {force}",
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
            raise ConflictError(
                message=f"Organization is not empty ({user_count} users). Use force=True to delete.",
                details={"error_code": "ORG_NOT_EMPTY", "count": user_count},
            )

        # 3. Delete Logic (Cascading)
        if user_count > 0:
            logger.info("[AuthService] FORCE DELETE enabled. Removing %s users...", user_count)
            for user in org_users:
                if self.use_firebase:
                    try:
                        await asyncio.to_thread(self.firebase_auth.delete_user, user.id)
                    except Exception as fb_err:
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
            raise AppException(message="User not found", status_code=404)

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
                        raise ConflictError(
                            message="Cannot demote the last Administrator of an Organization.",
                            details={"error_code": "LAST_ADMIN_PROTECTION"},
                        )

        updated_user = await self.repo.update(target_id, updates)

        if not updated_user:
            logger.error(
                "[AuthService] %s: User update failed (not found despite check).", ErrorCodes.INTERNAL_SERVER_ERROR.name
            )
            raise AppException("User update failed (not found despite check).", status_code=500)

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
            raise AppException(message="User not found", status_code=404)

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

            init_val = role_values.get(initiator.role, 0)
            target_val = role_values.get(target.role, 0)
            new_val = role_values.get(new_role, 0)

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
                    # Specific error string to be caught by router
                    raise ConflictError(
                        message="LAST_ADMIN_PROTECTION: Cannot demote the last Administrator.",
                        details={"error_code": "LAST_ADMIN_PROTECTION"},
                    )

        # 3. Apply Update
        updated = await self.repo.update(target_id, UserUpdate(role=new_role))

        if not updated:
            logger.error(
                "[AuthService] %s: User update failed (user reference lost).", ErrorCodes.INTERNAL_SERVER_ERROR.name
            )
            raise AppException("User update failed (user reference lost).", status_code=500)

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

    async def update_organization(self, initiator: TokenData, org_id: str, data: OrganizationCreate) -> Organization:
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

        update_dict = data.model_dump(exclude_unset=True)
        if update_dict:
            await self.org_repo.repo.update_organization(org_id, update_dict)

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
            # STRICT DB AUTHORITY: No fallback creation.
            # User must run 'backend.seed.run_seed' to populate db.json.
            logger.critical("No Root user found in database! Strict Authority Enforced. Please run seed script.")

            raise AppException(
                message="Root user 'root_master' missing from DB. Run 'python -m backend_v2.seed.run_seed local'.",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
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
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR},
            )

        return root
