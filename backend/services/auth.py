"""Authentication and User Management Service."""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from typing import Any

import jwt
from tinydb import Query

from backend.database.wrapper import AbstractDatabase, AbstractTable
from backend.exceptions import ConflictError
from backend.models.auth import Organization, OrganizationCreate, TokenData, User, UserCreate, UserRole, UserUpdate

# Secure Secret for Local Tokens (Impersonation)
# In production, this MUST be set via environment variable.
JWT_SECRET = "cognitive-quorum-internal-secret-change-me"
JWT_ALGORITHM = "HS256"


logger = logging.getLogger(__name__)

# --- Repository Layer (Organization) ---


class OrganizationRepository:
    """Repository for Organization data access."""

    def __init__(self, db_client: AbstractDatabase):
        """Initialize OrganizationRepository."""
        self.table: AbstractTable = db_client.table("organizations")

    def get_by_id(self, org_id: str) -> Organization | None:
        """Retrieves an organization by ID.

        Args:
            org_id (str): Organization ID.

        Returns:
            Optional[Organization]: The organization object.
        """
        # TinyDB simulation for get
        result = self.table.get(lambda x: x.get("id") == org_id)
        if result:
            # Robustness: existing data might miss 'tier'
            if "tier" not in result:
                result["tier"] = "standard"
            return Organization(**result)
        return None

    def create(self, org: Organization) -> Organization:
        """Persists a new organization.

        Args:
            org (Organization): The object to save.

        Returns:
            Organization: The saved object.
        """
        self.table.insert(org.model_dump())
        return org

    def list_all(self) -> list[Organization]:
        """List all organizations."""
        results = []
        for o in self.table.all():
            if "tier" not in o:
                o["tier"] = "standard"
            results.append(Organization(**o))
        return results


# --- Repository Layer (User) ---


class UserRepository:
    """Handles persistence of User metadata (roles, display names, hierarchy).

    Persists to the underlying database (TinyDB or Firestore).
    """

    def __init__(self, db_client: AbstractDatabase):
        """Initialize UserRepository."""
        self.table: AbstractTable = db_client.table("users")

    def get_by_uid(self, uid: str) -> User | None:
        """Retrieves user by UID.

        Args:
            uid (str): User ID.

        Returns:
            Optional[User]: The user object.
        """
        # TinyDB / Memory filter approach
        result = self.table.get(lambda x: x.get("uid") == uid)
        if result:
            return User(**result)
        return None

    def get_by_email(self, email: str) -> User | None:
        """Retrieve user by email."""
        result = self.table.get(lambda x: x.get("email") == email)
        if result:
            return User(**result)
        return None

    def create(self, user: User) -> User:
        """Create a new user."""
        data = user.model_dump()
        self.table.insert(data)
        return user

    def update(self, uid: str, updates: UserUpdate) -> User | None:
        """Update a user."""
        user = self.get_by_uid(uid)
        if not user:
            return None

        update_data = updates.model_dump(exclude_unset=True)
        if not update_data:
            return user

        # Update in DB
        self.table.update(update_data, lambda x: x.get("uid") == uid)

        # Return updated
        return self.get_by_uid(uid)

    def list_all(self) -> list[User]:
        """List all users."""
        raw_users = self.table.all()
        return [User(**u) for u in raw_users]

    def delete(self, uid: str) -> bool:
        """Hard delete user from DB."""
        # TinyDB remove
        ids = self.table.remove(Query().uid == uid)
        return len(ids) > 0

    def get_by_organization(self, org_id: str) -> list[User]:
        """Retrieve all users associated with an organization ID."""
        results = self.table.search(Query().organization_id == org_id)
        return [User(**u) for u in results]


# --- Service Layer ---


class AuthService:
    """Hybrid Auth Service with Multi-Tenancy (SaaS)."""

    def __init__(self, db_client: AbstractDatabase, use_firebase: bool = False, audit_service: Any = None):
        """Initialize AuthService."""
        self.repo = UserRepository(db_client)
        self.org_repo = OrganizationRepository(db_client)
        self.use_firebase = use_firebase
        self.audit_service = audit_service  # Typed as Any to avoid circular import if strict
        self._initialized_firebase = False

        if self.use_firebase:
            self._init_firebase()

    def _init_firebase(self):
        try:
            from firebase_admin import auth

            self.firebase_auth = auth
            logger.info("[AuthService] Firebase Admin SDK initialized.")
            self._initialized_firebase = True
        except ImportError:
            logger.warning("[AuthService] Firebase SDK not installed. Falling back to Mock mode.")
            self.use_firebase = False

    def create_impersonation_token(self, target_uid: str, duration_seconds: int = 3600) -> str:
        """Generates a signed JWT for impersonating a user.

        Args:
            target_uid (str): The UID of the user to impersonate.
            duration_seconds (int): Token validity duration.

        Returns:
            str: Signed JWT string.
        """
        payload = {
            "sub": target_uid,
            "exp": time.time() + duration_seconds,
            "iat": time.time(),
            "type": "impersonation",
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token

    def verify_token(self, token: str) -> TokenData:
        """Verifies a Bearer token.

        Returns TokenData (uid, role, organization_id).
        """
        # 1. Local Signed Token (Impersonation / Internal)
        try:
            # We enforce the secret check here.
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            uid = payload.get("sub")
            if uid:
                user = self.repo.get_by_uid(uid)
                if not user:
                    raise ValueError(f"Impersonated User not found: {uid}")
                return TokenData(uid=user.uid, role=user.role, email=user.email, organization_id=user.organization_id)
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired") from None
        except jwt.PyJWTError:
            pass

        # 2. Mock/Dev Mode check
        if not self.use_firebase or token.startswith("mock-token:"):
            # Expect format "mock-token:<uid>"
            if token.startswith("mock-token:"):
                uid = token.split(":")[1]
            else:
                uid = token

            # Check if user exists in our DB
            user = self.repo.get_by_uid(uid)
            if not user:
                raise ValueError(f"Mock User not found for UID: {uid}")

            return TokenData(uid=user.uid, role=user.role, email=user.email, organization_id=user.organization_id)

        # 2. Firebase Mode
        try:
            # Verify ID token
            decoded_token = self.firebase_auth.verify_id_token(token)
            uid = decoded_token["uid"]
            email = decoded_token.get("email")

            # Sync/Get User from our DB
            user = self.repo.get_by_uid(uid)

            if not user:
                # Auto-registration for missing users found in Firebase
                logger.info(f"User {uid} not found in local DB. Auto-registering as MEMBER (No Org).")
                new_user = User(
                    uid=uid,
                    email=email if email else "unknown@example.com",
                    role=UserRole.MEMBER,
                    organization_id=None,  # Orphan user
                    created_at=str(time.time()),
                )
                self.repo.create(new_user)
                return TokenData(uid=uid, role=UserRole.MEMBER, email=email, organization_id=None)

            return TokenData(uid=user.uid, role=user.role, email=user.email, organization_id=user.organization_id)

        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise ValueError("Invalid credentials") from e

    async def create_organization(self, creator_uid: str, org_create: OrganizationCreate) -> Organization:
        """Creates a new Tenant Organization and an initial Admin user for it.

        Strictly Async.
        """
        creator = self.repo.get_by_uid(creator_uid)
        if not creator or creator.role != UserRole.ROOT:
            raise PermissionError("Only ROOT can create organizations.")

        # 1. Create Organization (Sync DB call in thread? Or just sync for now)
        # We'll run it sync as TinyDB is fast, but logically the method is async.
        org_id = uuid.uuid4().hex[:8]
        new_org = Organization(id=org_id, name=org_create.name, created_at=str(time.time()), is_active=True)
        self.org_repo.create(new_org)

        # 2. Create the Org Admin
        admin_payload = UserCreate(
            email=org_create.admin_email,
            password=org_create.admin_password,
            display_name=org_create.admin_name,
            role=UserRole.ADMIN,
            organization_id=org_id,
        )

        # Bypass hierarchy check since we are ROOT acting explicitly
        await self._create_user_internal(creator.uid, admin_payload, force_org_id=org_id)

        # Audit
        if self.audit_service:
            await self.audit_service.log_event(
                actor_uid=creator_uid,
                action="ORG_CREATED",
                organization_id=org_id,
                target_uid=org_id,
                details={"name": new_org.name, "tier": new_org.tier},
            )

        return new_org

    async def create_user(self, creator_uid: str, user_data: UserCreate) -> User:
        """Creates a new user, enforcing hierarchy and tenancy."""
        return await self._create_user_internal(creator_uid, user_data)

    async def _create_user_internal(
        self, creator_uid: str, user_data: UserCreate, force_org_id: str | None = None
    ) -> User:
        creator = self.repo.get_by_uid(creator_uid)
        if not creator:
            raise ValueError("Creator not found")

        target_org_id: str | None = None
        # Resolve Org ID
        if force_org_id:
            target_org_id = force_org_id
        elif creator.role == UserRole.ROOT:
            target_org_id = user_data.organization_id or creator.organization_id
        else:
            if user_data.organization_id and user_data.organization_id != creator.organization_id:
                raise PermissionError("Cannot create users in other organizations.")
            target_org_id = creator.organization_id

        if user_data.role == UserRole.ROOT:
            if target_org_id != "system":
                raise ValueError("Root users can only be created within the System Organization.")
            target_org_id = "system"  # Redundant safety, but ensures it matches

        # RULE: Organization MUST exist
        if target_org_id:
            if target_org_id == "system":
                # System org acts as a special bootstrap case, but usually should exist.
                # We'll allow it specifically if we are bootstrapping, otherwise check valid.
                # Given ensure_root_user creates it, we can enforce check or just pass for resilience.
                # Let's check it strictly.
                pass

            org_exists = self.org_repo.get_by_id(target_org_id)
            if not org_exists:
                raise ValueError(f"Target Organization '{target_org_id}' does not exist.")

        # Enforce Role Hierarchy
        self._enforce_hierarchy(creator, user_data.role)

        new_uid = ""

        # 1. Create in Firebase (if enabled)
        if self.use_firebase and user_data.password:
            try:
                fb_user = self.firebase_auth.create_user(
                    email=user_data.email, password=user_data.password, display_name=user_data.display_name
                )
                new_uid = fb_user.uid
            except Exception:
                try:
                    existing = self.firebase_auth.get_user_by_email(user_data.email)
                    new_uid = existing.uid
                    logger.info(f"User {user_data.email} already in Firebase. Using existing UID.")
                except Exception as e:
                    raise ValueError(f"Failed to create Firebase user: {e}") from e
        else:
            # Generate a mock UID
            new_uid = f"local_{uuid.uuid4().hex[:8]}"

        # 2. Create in Local DB
        new_user = User(
            uid=new_uid,
            email=user_data.email,
            display_name=user_data.display_name,
            role=user_data.role,
            organization_id=target_org_id,
            created_at=str(time.time()),
            created_by=creator.uid,
        )

        saved_user = self.repo.create(new_user)

        # Audit
        if self.audit_service:
            await self.audit_service.log_event(
                actor_uid=creator_uid,
                action="USER_CREATED",
                organization_id=target_org_id,
                target_uid=new_uid,
                details={"email": new_user.email, "role": new_user.role.value},
            )

        return saved_user

    def _enforce_hierarchy(self, creator: User, target_role: UserRole):
        if creator.role == UserRole.ROOT:
            return
        if creator.role == UserRole.ADMIN:
            if target_role == UserRole.ROOT:
                raise PermissionError("Admins cannot create Roots.")
            return
        if creator.role == UserRole.MANAGER:
            raise PermissionError("Managers are Technical Leads and cannot manage users. Ask an Admin.")
        if creator.role == UserRole.MEMBER:
            raise PermissionError("This user role cannot create users")

        raise PermissionError("This user role cannot create users")

    def _count_org_admins(self, org_id: str) -> int:
        if not org_id:
            return 0
        all_users = self.repo.list_all()
        return sum(1 for u in all_users if u.organization_id == org_id and u.role == UserRole.ADMIN)

    async def get_users_by_organization(self, organization_id: str) -> list[User]:
        """Async retrieval of all users for a given organization."""
        return await asyncio.to_thread(self.repo.get_by_organization, organization_id)

    async def delete_user(self, initiator_uid: str, target_uid: str) -> bool:
        """Delete a user, with Last Admin Protection. (Non-blocking)."""
        logger.info(f"[AuthService] delete_user called. Initiator: {initiator_uid}, Target: {target_uid}")

        # Run Read operations in thread
        initiator = await asyncio.to_thread(self.repo.get_by_uid, initiator_uid)
        target = await asyncio.to_thread(self.repo.get_by_uid, target_uid)

        if not initiator or not target:
            raise ValueError("User not found")

        # Permission Check
        if initiator.role != UserRole.ROOT:
            if initiator.role == UserRole.ADMIN:
                if target.organization_id != initiator.organization_id:
                    raise PermissionError("Cannot delete users from other organizations")
            else:
                raise PermissionError("Insufficient permissions to delete users")

        # ROOT PROTECTION
        if target_uid == "root_master":
            raise PermissionError("The primary Root account cannot be deleted.")

        # LAST ADMIN PROTECTION
        if target.role == UserRole.ADMIN and target.organization_id:
            # Run Admin Count in thread -> Count iterates list_all
            admin_count = await asyncio.to_thread(self._count_org_admins, target.organization_id)
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
                logger.info(f"[AuthService] Deleting Firebase user {target.uid}...")
                await asyncio.to_thread(self.firebase_auth.delete_user, target.uid)
            except Exception as e:
                logger.warning(f"Firebase delete failed (might be local user): {e}")

        # 2. Local DB
        logger.info(f"[AuthService] Deleting Local DB user {target_uid}...")
        await asyncio.to_thread(self.repo.delete, target_uid)

        # Audit
        if self.audit_service:
            await self.audit_service.log_event(
                actor_uid=initiator_uid,
                action="USER_DELETED",
                organization_id=target.organization_id,
                target_uid=target_uid,
                details={"email": target.email},
            )

        return True

    async def delete_organization(self, initiator_uid: str, target_org_id: str, force: bool = False) -> None:
        """Deletes an Organization.

        Safety Rules:
        - Cannot delete 'system' organization.
        - Cannot delete non-empty organization unless force=True.
        - force=True cascades delete to all users.
        """
        logger.info(
            f"[AuthService] delete_organization called. Initiator: {initiator_uid}, "
            f"Target: {target_org_id}, Force: {force}"
        )

        initiator = await asyncio.to_thread(self.repo.get_by_uid, initiator_uid)

        if not initiator or initiator.role != UserRole.ROOT:
            raise PermissionError("Only ROOT can delete organizations.")

        if target_org_id == "system":
            raise PermissionError("CRITICAL: The 'system' organization is protected and CANNOT be deleted.")

        # 2. Check Users
        logger.info("[AuthService] Fetching users to check for safety...")
        all_users = await asyncio.to_thread(self.repo.list_all)
        org_users = [u for u in all_users if u.organization_id == target_org_id]

        user_count = len(org_users)
        logger.info(f"[AuthService] Organization {target_org_id} has {user_count} users.")

        if user_count > 0 and not force:
            # Revert to standard ValueError (which FastAPI can allow routing exceptions for,
            # 2. Check strict non-empty rule (unless force=False/True?)
            # Usually we block unless force provided.
            # or we map it to 409 Conflict in router).
            # The client needs a specific code. We'll rely on the exception message or type.
            # Best practice: Custom exception, but ValueError is standard for logic.
            raise ConflictError(
                message=f"Organization is not empty ({user_count} users). Use force=True to delete.",
                details={"error_code": "ORG_NOT_EMPTY", "count": user_count},
            )

        # 3. Delete Logic (Cascading)
        if user_count > 0:
            logger.info(f"[AuthService] FORCE DELETE enabled. Removing {user_count} users...")
            for user in org_users:
                if self.use_firebase:
                    try:
                        await asyncio.to_thread(self.firebase_auth.delete_user, user.uid)
                    except Exception:
                        pass

                await asyncio.to_thread(self.repo.delete, user.uid)

        # 4. Delete Org Entity
        logger.info(f"[AuthService] Removing Organization {target_org_id} from DB...")

        def _delete_org():
            self.org_repo.table.remove(Query().id == target_org_id)

        await asyncio.to_thread(_delete_org)

        # Audit
        if self.audit_service:
            await self.audit_service.log_event(
                actor_uid=initiator_uid,
                action="ORG_DELETED",
                organization_id=target_org_id,
                target_uid=target_org_id,
                details={"users_deleted": user_count, "force_used": force},
            )

    async def update_user(self, initiator_uid: str, target_uid: str, updates: UserUpdate) -> User:
        """General update method.

        If 'role' is being changed, we must enforce Last Admin Protection.
        """
        initiator = self.repo.get_by_uid(initiator_uid)
        target = self.repo.get_by_uid(target_uid)

        if not initiator or not target:
            raise ValueError("User not found")

        # Permission Check
        if initiator.role != UserRole.ROOT:
            # Self-Update Rule (Language/Theme)
            if initiator_uid == target_uid:
                # Allowed to update self, but check for Restricted fields (Role)
                if updates.role is not None and updates.role != initiator.role:
                    raise PermissionError("Users cannot change their own role.")
            # Org Admin Check
            elif initiator.role == UserRole.ADMIN:
                if target.organization_id != initiator.organization_id:
                    raise PermissionError("Cannot update users from other organizations")
            else:
                raise PermissionError("Insufficient permissions to update users")

        # LAST ADMIN PROTECTION (Role Change)
        if updates.role is not None and target.role == UserRole.ADMIN:
            # If we are changing FROM Admin TO something else
            if updates.role != UserRole.ADMIN:
                if target.organization_id:
                    admin_count = self._count_org_admins(target.organization_id)
                    if admin_count <= 1:
                        raise ConflictError(
                            message="Cannot demote the last Administrator of an Organization.",
                            details={"error_code": "LAST_ADMIN_PROTECTION"},
                        )

        updated_user = self.repo.update(target_uid, updates)

        if not updated_user:
            raise ValueError("User update failed (not found despite check).")

        # Audit
        if self.audit_service:
            # Determine what changed for details
            changed_fields = updates.dict(exclude_unset=True)
            await self.audit_service.log_event(
                actor_uid=initiator_uid,
                action="USER_UPDATED",
                organization_id=target.organization_id,  # Log under target's org
                target_uid=target_uid,
                details=changed_fields,
            )

        return updated_user

    async def update_user_role(self, initiator_uid: str, target_uid: str, new_role: UserRole) -> User:
        """Updates a user's role with strict Last Admin Protection.

        Raises:
            PermissionError: If hierarchy is violated.
            ValueError: If user not found.
            ConflictError: If Last Admin Protection is triggered.
        """
        initiator = self.repo.get_by_uid(initiator_uid)
        target = self.repo.get_by_uid(target_uid)

        if not initiator or not target:
            raise ValueError("User not found")

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
                raise PermissionError("Cannot modify users with higher or equal privileges.")
            if init_val < new_val:
                raise PermissionError("Cannot promote user to a role higher than your own.")

            # Org Constraint
            if initiator.role == UserRole.ADMIN:
                if target.organization_id != initiator.organization_id:
                    raise PermissionError("Cannot manage users in other organizations.")

        # 2. Last Admin Protection
        if target.role == UserRole.ADMIN and new_role != UserRole.ADMIN:
            if target.organization_id:
                count = await asyncio.to_thread(self._count_org_admins, target.organization_id)
                if count <= 1:
                    # Specific error string to be caught by router
                    raise RuntimeError("LAST_ADMIN_PROTECTION: Cannot demote the last Administrator.")

        # 3. Apply Update
        updated = self.repo.update(target_uid, UserUpdate(role=new_role))
        if not updated:
            raise ValueError("User update failed (user reference lost).")

        # 4. Audit
        if self.audit_service:
            await self.audit_service.log_event(
                actor_uid=initiator_uid,
                action="USER_ROLE_UPDATED",
                organization_id=target.organization_id,
                target_uid=target_uid,
                details={"old_role": target.role.value, "new_role": new_role.value},
            )

        return updated

    def ensure_root_user(self, email: str = "root@example.com") -> User:
        """Bootstraps a root user and Development Scenario (Demo Corp) if needed."""
        # 0. Ensure SYSTEM Org exists (Container for Root)
        if not self.org_repo.get_by_id("system"):
            logger.info("[AuthService] Creating 'system' Organization.")
            self.org_repo.create(
                Organization(id="system", name="System Administration", created_at=str(time.time()), tier="enterprise")
            )

        # 1. ROOT
        root = self.repo.get_by_uid("root_master")
        if not root:
            logger.warning(f"No Root user found. Creating bootstrap root: {email}")
            root = User(
                uid="root_master",
                email=email,
                role=UserRole.ROOT,
                organization_id="system",
                display_name="System Root",
                created_at=str(time.time()),
            )
            self.repo.create(root)
        elif root.organization_id != "system":
            # Fix casing or drift if it was "SYSTEM" or None
            logger.info(f"Fixing root_master organization_id from '{root.organization_id}' to 'system'")
            self.repo.update("root_master", UserUpdate(organization_id="system"))
            root = self.repo.get_by_uid("root_master")  # Refresh

            self.repo.update("root_master", UserUpdate(organization_id="system"))
            root = self.repo.get_by_uid("root_master")  # Refresh

        if not root:
            raise ValueError("Failed to obtain Root user.")

        return root

    # --- Dependency Injection Helpers (Static) ---
    @staticmethod
    def require_role(required_role: UserRole):
        """Returns a dependency that validates the user has the required role.

        Implicitly allows ROOT for everything.
        """
        from fastapi import Depends, HTTPException

        from backend.dependencies import get_current_user_from_header  # Lazy import

        async def _role_checker(user: TokenData = Depends(get_current_user_from_header)):  # noqa: B008
            if user.role == UserRole.ROOT:
                return user

            if user.role != required_role:
                raise HTTPException(status_code=403, detail=f"Insufficient privileges. Required: {required_role.value}")
            return user

        return _role_checker

    @staticmethod
    def get_current_user(
        from_header=None,  # Placeholder to match Depends signature if needed, but we delegate
    ):
        """Dependency alias for getting current user via header.

        Intended usage: user: TokenData = Depends(AuthService.get_current_user).
        """
        from backend.dependencies import get_current_user_from_header

        # This one is tricky because Depends() needs a callable.
        # If we return a callable that Depends uses...
        return get_current_user_from_header
