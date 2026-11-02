"""User Lifecycle Management and Authorization Service."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from backend_v2.exceptions import (
    AppException,
    ConflictError,
    ErrorCodes,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from backend_v2.models.auth import (
    SYSTEM_ROOT_USER_ID,
    Organization,
    SubscriptionStatus,
    SystemOrganizations,
    TokenData,
    User,
    UserCreate,
    UserRole,
    UserUpdate,
)
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.enums import EntityPrefix
from backend_v2.services.auth.repositories import (
    OrganizationRepository,
    UserRepository,
)

logger = logging.getLogger(__name__)

__all__ = ["UserService"]


_ROLE_HIERARCHY: dict[UserRole, int] = {
    UserRole.ROOT: 40,
    UserRole.ADMIN: 30,
    UserRole.MANAGER: 20,
    UserRole.MEMBER: 10,
    UserRole.VIEWER: 5,
}
_REVOCATION_TTL_SECONDS: int = 900


class UserService:
    """User Management, Role Hierarchy, and Lifecycle Service.

    Attributes:
        repo: Repository wrapper for user persistence operations.
        user_repo: Explicit alias for the user repository wrapper.
        org_repo: Repository wrapper for organization operations.
        audit_service: Optional audit event logging service.
        use_firebase: Flag indicating if Firebase Admin SDK integration is enabled.
        firebase_auth: Firebase authentication client instance or mock.
        revocation_cache: Optional Dual-Key Redis session revocation cache.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        org_repo: OrganizationRepository,
        audit_service: Any = None,
        use_firebase: bool = False,
        firebase_auth: Any = None,
        revocation_cache: Any = None,
    ) -> None:
        """Initializes the UserService.

        Args:
            user_repo: Repository wrapper for user operations.
            org_repo: Repository wrapper for organization operations.
            audit_service: Optional service for recording audit logs.
            use_firebase: Flag indicating if Firebase integration is enabled.
            firebase_auth: Optional Firebase authentication module or mock.
            revocation_cache: Optional Redis revocation cache for immediate session invalidation.
        """
        self.repo = user_repo
        self.user_repo = user_repo
        self.org_repo = org_repo
        self.audit_service = audit_service
        self.use_firebase = use_firebase
        self.firebase_auth = firebase_auth
        self.revocation_cache = revocation_cache

    async def create_user(self, creator_id: str, user_data: UserCreate) -> User:
        """Creates a new user, enforcing hierarchy and tenancy.

        Args:
            creator_id: The UID of the user initiating the creation.
            user_data: The user creation payload.

        Returns:
            The newly created user.

        Raises:
            AppException: With ErrorCodes.RESOURCE_NOT_FOUND if creator is not found,
                ErrorCodes.VALIDATION_FAILED if target org does not exist, or
                ErrorCodes.INTERNAL_SERVER_ERROR if Firebase creation fails.
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if hierarchy or org constraints are violated.
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
            AppException: With ErrorCodes.RESOURCE_NOT_FOUND if creator is not found,
                ErrorCodes.VALIDATION_FAILED if target org does not exist, or
                ErrorCodes.INTERNAL_SERVER_ERROR if Firebase creation fails.
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if hierarchy or org constraints are violated.
        """
        creator = await self.repo.get_by_id(creator_id)
        if not creator:
            logger.error(
                "[UserService] %s: Creator not found (creator_id=%s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                creator_id,
                exc_info=True,
            )
            raise AppException(
                message="Creator not found",
                status_code=404,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )

        target_org_id = await self._resolve_target_org_for_creation(creator, user_data, force_org_id)
        self._enforce_hierarchy(creator, user_data.role)
        new_id = self._provision_firebase_or_local_user_id(user_data)

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

        if self.audit_service:
            await self.audit_service.log_event(
                actor_id=creator_id,
                action="USER_CREATED",
                organization_id=target_org_id,
                target_id=new_id,
                details={"email": new_user.email, "role": new_user.role.value},
            )

        return saved_user

    async def _resolve_target_org_for_creation(
        self, creator: User, user_data: UserCreate, force_org_id: str | None
    ) -> str | None:
        """Resolve and validate the target organization for user creation.

        Args:
            creator: Authenticated creator User instance.
            user_data: Validated UserCreate payload.
            force_org_id: Optional forced organization ID.

        Returns:
            Resolved organization ID or None.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if tenancy or ROOT org rules are violated.
            AppException: With ErrorCodes.VALIDATION_FAILED if target organization does not exist.
        """
        if force_org_id:
            target_org_id: str | None = force_org_id
        elif creator.role == UserRole.ROOT:
            target_org_id = (
                user_data.organization_id if user_data.organization_id is not None else creator.organization_id
            )
        else:
            if user_data.organization_id and user_data.organization_id != creator.organization_id:
                logger.error(
                    "[UserService] %s: Creator %s cannot create users in foreign organization %s.",
                    ErrorCodes.PERMISSION_DENIED.name,
                    creator.id,
                    user_data.organization_id,
                    exc_info=True,
                )
                raise PermissionDeniedError("Cannot create users in other organizations.")
            target_org_id = creator.organization_id

        if user_data.role == UserRole.ROOT:
            if target_org_id != SystemOrganizations.ROOT_SYSTEM:
                logger.error(
                    "[UserService] %s: Attempted to create ROOT user outside System Organization (org_id=%s).",
                    ErrorCodes.PERMISSION_DENIED.name,
                    target_org_id,
                    exc_info=True,
                )
                raise PermissionDeniedError("Root users can only be created within the System Organization.")
            target_org_id = SystemOrganizations.ROOT_SYSTEM

        if target_org_id and target_org_id != SystemOrganizations.ROOT_SYSTEM:
            org_exists = await self.org_repo.get_by_id(target_org_id)
            if not org_exists:
                logger.error(
                    "[UserService] %s: Target Organization '%s' does not exist.",
                    ErrorCodes.VALIDATION_FAILED.name,
                    target_org_id,
                    exc_info=True,
                )
                raise AppException(
                    message=f"Target Organization '{target_org_id}' does not exist.",
                    status_code=404,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
        return target_org_id

    def _provision_firebase_or_local_user_id(self, user_data: UserCreate) -> str:
        """Provision a Firebase user ID when enabled or generate a canonical UUIDv7 user ID.

        Args:
            user_data: Validated UserCreate payload.

        Returns:
            Provisioned user ID string.

        Raises:
            AppException: With ErrorCodes.INTERNAL_SERVER_ERROR if Firebase creation fails.
        """
        if self.use_firebase and user_data.password:
            try:
                fb_user = self.firebase_auth.create_user(
                    email=user_data.email, password=user_data.password, name=user_data.name
                )
                return str(fb_user.id)
            except (AppException, OSError, ValueError, KeyError, RuntimeError, TypeError) as e:
                try:
                    existing = self.firebase_auth.get_user_by_email(user_data.email)
                    logger.info("User %s already in Firebase. Using existing UID.", existing.id)
                    return str(existing.id)
                except AppException, OSError, ValueError, KeyError, RuntimeError, TypeError:
                    logger.error(
                        "[UserService] %s: Failed to create Firebase user: %s",
                        ErrorCodes.INTERNAL_SERVER_ERROR.name,
                        e,
                        exc_info=True,
                    )
                    raise AppException(
                        message=f"Failed to create Firebase user: {e}",
                        status_code=500,
                        details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                    ) from e
        return generate_opaque_id(EntityPrefix.USER)

    def _enforce_hierarchy(self, creator: User, target_role: UserRole) -> None:
        """Enforces role hierarchy rules for user creation.

        Args:
            creator: The user attempting to create another user.
            target_role: The role being assigned to the new user.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the creator lacks sufficient privileges.
        """
        if creator.role == UserRole.ROOT:
            return

        if creator.role == UserRole.ADMIN:
            if target_role == UserRole.ROOT:
                logger.error(
                    "[UserService] %s: Admin %s attempted to create ROOT user.",
                    ErrorCodes.PERMISSION_DENIED.name,
                    creator.id,
                    exc_info=True,
                )
                raise PermissionDeniedError("Admins cannot create Roots.")
            return

        if creator.role == UserRole.MANAGER:
            logger.error(
                "[UserService] %s: Manager %s attempted to create user with role %s.",
                ErrorCodes.PERMISSION_DENIED.name,
                creator.id,
                target_role.value,
                exc_info=True,
            )
            raise PermissionDeniedError("Managers are Technical Leads and cannot manage users. Ask an Admin.")

        logger.error(
            "[UserService] %s: User %s with role %s cannot create users.",
            ErrorCodes.PERMISSION_DENIED.name,
            creator.id,
            creator.role.value,
            exc_info=True,
        )
        raise PermissionDeniedError("This user role cannot create users")

    async def _count_org_admins(self, org_id: str) -> int:
        """Counts the number of active, non-deleted admins in an organization.

        Args:
            org_id: The ID of the organization.

        Returns:
            The number of active, non-deleted admin users.
        """
        all_users = await self.repo.list_all()
        return sum(
            1
            for u in all_users
            if u.organization_id == org_id and u.role == UserRole.ADMIN and u.is_active and u.deleted_at is None
        )

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
            AppException: With ErrorCodes.RESOURCE_NOT_FOUND if either user is not found, or
                ErrorCodes.INTERNAL_SERVER_ERROR if Firebase deletion fails.
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if permissions are insufficient or target is protected.
            ConflictError: With ErrorCodes.CONFLICT_ERROR if deleting the user violates Last Admin Protection.
        """
        logger.info("[UserService] delete_user called. Initiator: %s, Target: %s", initiator_id, target_id)

        initiator = await self.repo.get_by_id(initiator_id)
        target = await self.repo.get_by_id(target_id)

        if not initiator or not target:
            logger.error(
                "[UserService] %s: Initiator %s or target %s not found for delete_user.",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                initiator_id,
                target_id,
                exc_info=True,
            )
            raise AppException(
                message="User not found",
                status_code=404,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )

        # Permission Check
        if initiator.role != UserRole.ROOT:
            if initiator.role == UserRole.ADMIN:
                if target.organization_id != initiator.organization_id:
                    logger.error(
                        "[UserService] %s: Admin %s attempted to delete user %s from foreign organization %s.",
                        ErrorCodes.PERMISSION_DENIED.name,
                        initiator_id,
                        target_id,
                        target.organization_id,
                        exc_info=True,
                    )
                    raise PermissionDeniedError("Cannot delete users from other organizations")
            else:
                logger.error(
                    "[UserService] %s: User %s with role %s lacks permission to delete user %s.",
                    ErrorCodes.PERMISSION_DENIED.name,
                    initiator_id,
                    initiator.role.value,
                    target_id,
                    exc_info=True,
                )
                raise PermissionDeniedError("Insufficient permissions to delete users")

        # ROOT PROTECTION
        if target_id == SYSTEM_ROOT_USER_ID:
            logger.error(
                "[UserService] %s: Attempted to delete protected Root account %s (initiator=%s).",
                ErrorCodes.PERMISSION_DENIED.name,
                target_id,
                initiator_id,
                exc_info=True,
            )
            raise PermissionDeniedError("The primary Root account cannot be deleted.")

        # LAST ADMIN PROTECTION
        if target.role == UserRole.ADMIN and target.organization_id:
            admin_count = await self._count_org_admins(target.organization_id)

            if admin_count <= 1:
                logger.error(
                    "[UserService] %s: Cannot delete the last Administrator of an Organization.",
                    ErrorCodes.CONFLICT_ERROR.name,
                    exc_info=True,
                )
                raise ConflictError(
                    message="LAST_ADMIN_PROTECTION: Cannot delete the last Administrator of an Organization. "
                    "Promote another user first.",
                    details={"error_code": ErrorCodes.CONFLICT_ERROR.value, "reason": "LAST_ADMIN_PROTECTION"},
                )

        # Execute
        # 1. Firebase (if enabled)
        if self.use_firebase and self.firebase_auth is not None:
            try:
                logger.info("[UserService] Deleting Firebase user %s...", target.id)
                await asyncio.to_thread(self.firebase_auth.delete_user, target.id)
            except (AppException, OSError, ValueError, KeyError, RuntimeError, TypeError) as fb_err:
                logger.error(
                    "[UserService] %s: Failed to delete user %s in Firebase: %s",
                    ErrorCodes.INTERNAL_SERVER_ERROR.name,
                    target.id,
                    fb_err,
                    exc_info=True,
                )
                raise AppException(
                    message=f"Failed to delete user {target.id} in Firebase: {fb_err}",
                    status_code=500,
                    details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                ) from fb_err

        # 2. Local DB
        logger.info("[UserService] Deleting Local DB user %s...", target_id)
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

    async def update_user(self, initiator_id: str, target_id: str, updates: UserUpdate) -> User:
        """General update method for users enforcing 4-Tier RBAC, hierarchy, and Last Admin Protection.

        Args:
            initiator_id: The UID of the user initiating the update.
            target_id: The UID of the user to update.
            updates: The update payload.

        Returns:
            The updated user model.

        Raises:
            AppException: With ErrorCodes.RESOURCE_NOT_FOUND if user is not found, or
                ErrorCodes.INTERNAL_SERVER_ERROR if repository update fails.
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if hierarchy or org constraints are violated.
            ConflictError: With ErrorCodes.CONFLICT_ERROR if Last Admin Protection is violated.
        """
        initiator = await self.repo.get_by_id(initiator_id)
        target = await self.repo.get_by_id(target_id)

        if not initiator or not target:
            logger.error(
                "[UserService] %s: Initiator %s or target %s not found for update_user.",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                initiator_id,
                target_id,
                exc_info=True,
            )
            raise AppException(
                message="User not found",
                status_code=404,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )

        self._validate_update_user_permissions(initiator, target, updates)
        await self._enforce_last_admin_protection_on_update(target, updates)

        updated_user = await self.repo.update(target_id, updates)
        if not updated_user:
            logger.error(
                "[UserService] %s: User update failed (not found despite check).",
                ErrorCodes.INTERNAL_SERVER_ERROR.name,
                exc_info=True,
            )
            raise AppException(
                message="User update failed (not found despite check).",
                status_code=500,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
            )

        await self._maybe_revoke_sessions_on_update(target, updates)

        if self.audit_service:
            changed_fields = updates.model_dump(exclude_unset=True)
            await self.audit_service.log_event(
                actor_id=initiator_id,
                action="USER_UPDATED",
                organization_id=target.organization_id,
                target_id=target_id,
                details=changed_fields,
            )

        return updated_user

    def _validate_update_user_permissions(self, initiator: User, target: User, updates: UserUpdate) -> None:
        """Validate 4-Tier RBAC, self-service profile limits, and hierarchy for user updates.

        Args:
            initiator: Authenticated user performing the update.
            target: Target user record being modified.
            updates: Requested UserUpdate payload.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if RBAC or hierarchy rules are violated.
        """
        if updates.organization_id is not None and updates.organization_id != target.organization_id:
            if initiator.role != UserRole.ROOT:
                logger.error(
                    "[UserService] %s: Non-ROOT user %s attempted to transfer user %s between organizations.",
                    ErrorCodes.PERMISSION_DENIED.name,
                    initiator.id,
                    target.id,
                    exc_info=True,
                )
                raise PermissionDeniedError("Only ROOT can transfer users between organizations.")

        if initiator.role == UserRole.ROOT:
            return

        if initiator.id == target.id:
            self._validate_self_update_fields(initiator, target, updates)
            return

        if initiator.role == UserRole.ADMIN:
            if target.organization_id != initiator.organization_id:
                logger.error(
                    "[UserService] %s: Admin %s attempted to update user %s in foreign organization %s.",
                    ErrorCodes.PERMISSION_DENIED.name,
                    initiator.id,
                    target.id,
                    target.organization_id,
                    exc_info=True,
                )
                raise PermissionDeniedError("Cannot update users from other organizations")
            self._enforce_role_modification_hierarchy(initiator, target, updates.role)
            return

        logger.error(
            "[UserService] %s: User %s with role %s lacks permission to update user %s.",
            ErrorCodes.PERMISSION_DENIED.name,
            initiator.id,
            initiator.role.value,
            target.id,
            exc_info=True,
        )
        raise PermissionDeniedError("Insufficient permissions to update users")

    def _validate_self_update_fields(self, initiator: User, target: User, updates: UserUpdate) -> None:
        """Enforce self-service profile restrictions (only name, language, and theme_mode permitted).

        Args:
            initiator: Non-ROOT user updating their own profile.
            target: Current user state.
            updates: Requested UserUpdate payload.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if restricted fields are mutated.
        """
        if updates.role is not None and updates.role != initiator.role:
            logger.error(
                "[UserService] %s: User %s attempted to change their own role.",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                exc_info=True,
            )
            raise PermissionDeniedError("Users cannot change their own role.")

        if updates.is_active is not None and updates.is_active != target.is_active:
            logger.error(
                "[UserService] %s: User %s attempted to mutate their own active status.",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                exc_info=True,
            )
            raise PermissionDeniedError("Users cannot change their own active status.")

        if updates.password is not None:
            logger.error(
                "[UserService] %s: User %s attempted to mutate password via self-service profile update.",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                exc_info=True,
            )
            raise PermissionDeniedError("Users cannot reset password via self-service profile update.")

    def _enforce_role_modification_hierarchy(self, initiator: User, target: User, new_role: UserRole | None) -> None:
        """Enforce numeric role hierarchy on target user modification and role assignment.

        Args:
            initiator: Non-ROOT user initiating the modification.
            target: Target user being modified.
            new_role: Optional new role being assigned.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if target or new_role exceeds initiator rank.
        """
        init_val = _ROLE_HIERARCHY[initiator.role]
        target_val = _ROLE_HIERARCHY[target.role]

        if init_val < target_val:
            logger.error(
                "[UserService] %s: User %s (%s) cannot modify user %s (%s) with higher privileges.",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                initiator.role.value,
                target.id,
                target.role.value,
                exc_info=True,
            )
            raise PermissionDeniedError("Cannot modify users with higher or equal privileges.")

        if new_role is not None:
            new_val = _ROLE_HIERARCHY[new_role]
            if init_val < new_val:
                logger.error(
                    "[UserService] %s: User %s (%s) cannot promote user %s to higher role %s.",
                    ErrorCodes.PERMISSION_DENIED.name,
                    initiator.id,
                    initiator.role.value,
                    target.id,
                    new_role.value,
                    exc_info=True,
                )
                raise PermissionDeniedError("Cannot promote user to a role higher than your own.")

    async def _enforce_last_admin_protection_on_update(self, target: User, updates: UserUpdate) -> None:
        """Enforce soft-delete aware LAST_ADMIN_PROTECTION on role demotion or account deactivation.

        Args:
            target: Target user record prior to update.
            updates: Requested UserUpdate payload.

        Raises:
            ConflictError: With ErrorCodes.CONFLICT_ERROR if demoting or deactivating the last active org ADMIN.
        """
        if target.role != UserRole.ADMIN or not target.organization_id:
            return
        if not target.is_active or target.deleted_at is not None:
            return

        demoting_admin = updates.role is not None and updates.role != UserRole.ADMIN
        deactivating_admin = updates.is_active is False
        if not demoting_admin and not deactivating_admin:
            return

        admin_count = await self._count_org_admins(target.organization_id)
        if admin_count <= 1:
            logger.error(
                "[UserService] %s: Cannot demote or deactivate the last Administrator of an Organization.",
                ErrorCodes.CONFLICT_ERROR.name,
                exc_info=True,
            )
            raise ConflictError(
                message="LAST_ADMIN_PROTECTION: Cannot demote the last Administrator of an Organization.",
                details={"error_code": ErrorCodes.CONFLICT_ERROR.value, "reason": "LAST_ADMIN_PROTECTION"},
            )

    async def _maybe_revoke_sessions_on_update(self, target: User, updates: UserUpdate) -> None:
        """Trigger immediate Redis Kill-Switch when role, organization_id, or active status changes.

        Args:
            target: User record prior to update.
            updates: Applied UserUpdate payload.

        Raises:
            AppException: If Redis session revocation fails when revocation_cache is configured.
        """
        if self.revocation_cache is None:
            return
        role_changed = updates.role is not None and updates.role != target.role
        org_changed = updates.organization_id is not None and updates.organization_id != target.organization_id
        deactivated = updates.is_active is False
        if role_changed or org_changed or deactivated:
            await self.revocation_cache.revoke_user_sessions(target.id, ttl_seconds=_REVOCATION_TTL_SECONDS)

    async def update_user_role(self, initiator_id: str, target_id: str, new_role: UserRole) -> User:
        """Updates a user's role with strict Last Admin Protection and immediate Redis session revocation.

        Args:
            initiator_id: The UID of the user changing the role.
            target_id: The UID of the user whose role is changing.
            new_role: The new role to assign.

        Returns:
            The updated user model.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if hierarchy is violated.
            AppException: With ErrorCodes.RESOURCE_NOT_FOUND if user is not found, or
                ErrorCodes.INTERNAL_SERVER_ERROR if repository update fails.
            ConflictError: With ErrorCodes.CONFLICT_ERROR if Last Admin Protection is triggered.
        """
        initiator = await self.repo.get_by_id(initiator_id)
        target = await self.repo.get_by_id(target_id)

        if not initiator or not target:
            logger.error(
                "[UserService] %s: Initiator %s or target %s not found for update_user_role.",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                initiator_id,
                target_id,
                exc_info=True,
            )
            raise AppException(
                message="User not found",
                status_code=404,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )

        if initiator.role != UserRole.ROOT:
            self._enforce_role_modification_hierarchy(initiator, target, new_role)
            if initiator.role == UserRole.ADMIN:
                if target.organization_id != initiator.organization_id:
                    logger.error(
                        "[UserService] %s: Admin %s cannot manage user %s in foreign organization %s.",
                        ErrorCodes.PERMISSION_DENIED.name,
                        initiator_id,
                        target_id,
                        target.organization_id,
                        exc_info=True,
                    )
                    raise PermissionDeniedError("Cannot manage users in other organizations.")
            else:
                logger.error(
                    "[UserService] %s: User %s with role %s lacks permission to update user roles.",
                    ErrorCodes.PERMISSION_DENIED.name,
                    initiator_id,
                    initiator.role.value,
                    exc_info=True,
                )
                raise PermissionDeniedError("Insufficient permissions to update user roles.")

        if target.role == UserRole.ADMIN and new_role != UserRole.ADMIN:
            if target.organization_id:
                count = await self._count_org_admins(target.organization_id)
                if count <= 1:
                    logger.error(
                        "[UserService] %s: LAST_ADMIN_PROTECTION: Cannot demote the last Administrator.",
                        ErrorCodes.CONFLICT_ERROR.name,
                        exc_info=True,
                    )
                    raise ConflictError(
                        message="LAST_ADMIN_PROTECTION: Cannot demote the last Administrator.",
                        details={"error_code": ErrorCodes.CONFLICT_ERROR.value, "reason": "LAST_ADMIN_PROTECTION"},
                    )

        updated = await self.repo.update(target_id, UserUpdate(role=new_role))
        if not updated:
            logger.error(
                "[UserService] %s: User update failed (user reference lost).",
                ErrorCodes.INTERNAL_SERVER_ERROR.name,
                exc_info=True,
            )
            raise AppException(
                message="User update failed (user reference lost).",
                status_code=500,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
            )

        if self.revocation_cache is not None and new_role != target.role:
            await self.revocation_cache.revoke_user_sessions(target_id, ttl_seconds=_REVOCATION_TTL_SECONDS)

        if self.audit_service:
            await self.audit_service.log_event(
                actor_id=initiator_id,
                action="USER_ROLE_UPDATED",
                organization_id=target.organization_id,
                target_id=target_id,
                details={"old_role": target.role.value, "new_role": new_role.value},
            )

        return updated

    async def list_users(self, initiator: TokenData) -> list[User]:
        """List users securely scoped by the 4-Tier RBAC Governance Matrix.

        Args:
            initiator: The token data of the user requesting the list.

        Returns:
            A list of users scoped to the initiator's role and organization.
        """
        all_users: list[User] = await self.repo.list_all()

        if initiator.role == UserRole.ROOT:
            return all_users

        if initiator.role in (UserRole.MEMBER, UserRole.VIEWER):
            return [u for u in all_users if u.id == initiator.id]

        org_id = initiator.organization_id
        return [u for u in all_users if u.organization_id == org_id]

    async def get_user(self, initiator: TokenData, target_id: str) -> User:
        """Fetch user securely enforcing the 4-Tier RBAC Governance Matrix.

        Args:
            initiator: The token data of the user requesting the fetch.
            target_id: The UID of the user to fetch.

        Returns:
            The requested user model.

        Raises:
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the user does not exist.
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the initiator lacks access.
        """
        user = await self.repo.get_by_id(target_id)

        if not user:
            logger.error(
                "[UserService] %s: User not found (target_id=%s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                target_id,
                exc_info=True,
            )
            raise ResourceNotFoundError(resource_type="user", resource_id=target_id)

        if initiator.role == UserRole.ROOT:
            return user

        if initiator.id == target_id:
            return user

        if initiator.role in (UserRole.ADMIN, UserRole.MANAGER) and user.organization_id == initiator.organization_id:
            return user

        logger.error(
            "[UserService] %s: User %s lacked permission to view user %s.",
            ErrorCodes.PERMISSION_DENIED.name,
            initiator.id,
            target_id,
            exc_info=True,
        )
        raise PermissionDeniedError("You do not have permission to view this user.")

    async def ensure_root_user(self, email: str = "root@example.com") -> User:
        """Bootstraps a root user and Development Scenario (Demo Corp) if needed.

        Args:
            email: Default email for root user if creation was supported.

        Returns:
            The root User object.

        Raises:
            AppException: With ErrorCodes.CONFIGURATION_ERROR if the root user is missing from the database,
                or ErrorCodes.INTERNAL_SERVER_ERROR if refreshing the root user fails.
        """
        if not await self.org_repo.get_by_id(SystemOrganizations.ROOT_SYSTEM):
            logger.info("[UserService] Creating 'system' Organization.")

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
                    allowed_email_domains=[],
                )
            )

        root = await self.repo.get_by_id(SYSTEM_ROOT_USER_ID)

        if not root:
            logger.error(
                "[UserService] %s: No Root user found in database! Strict Authority Enforced.",
                ErrorCodes.CONFIGURATION_ERROR.name,
                exc_info=True,
            )
            raise AppException(
                message="Root user 'root_master' missing from DB. Run 'python -m backend_v2.seed.run_seed local'.",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        if root.organization_id != SystemOrganizations.ROOT_SYSTEM:
            logger.info(
                "Fixing root_master organization_id from '%s' to '%s'",
                root.organization_id,
                SystemOrganizations.ROOT_SYSTEM,
            )

            await self.repo.update(
                SYSTEM_ROOT_USER_ID,
                UserUpdate(organization_id=SystemOrganizations.ROOT_SYSTEM),
            )

            root = await self.repo.get_by_id(SYSTEM_ROOT_USER_ID)

        if not root:
            logger.error(
                "[UserService] %s: Failed to obtain Root user.",
                ErrorCodes.INTERNAL_SERVER_ERROR.name,
                exc_info=True,
            )
            raise AppException(
                message="Failed to obtain Root user.",
                status_code=500,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
            )

        return root
