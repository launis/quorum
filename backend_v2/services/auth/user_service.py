"""User Lifecycle Management and Authorization Service."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import logging
from datetime import UTC, datetime
from typing import Any, Final

from backend_v2.exceptions import (
    AppException,
    AuthenticationError,
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
    UserDeleteResponse,
    UserRole,
    UserUpdate,
)
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.enums import EntityPrefix
from backend_v2.services.auth.repositories import (
    OrganizationRepository,
    UserRepository,
)
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = ["UserService"]


_ROLE_HIERARCHY: Final[dict[UserRole, int]] = {
    UserRole.ROOT: 40,
    UserRole.ADMIN: 30,
    UserRole.MANAGER: 20,
    UserRole.MEMBER: 10,
    UserRole.VIEWER: 5,
}
_SYSTEM_ORG_DEFAULT_QUOTA_LIMIT: Final[float] = 5000.0
_SYSTEM_ORG_DEFAULT_TPM_LIMIT: Final[int] = 50000
_SYSTEM_ORG_DEFAULT_RPM_LIMIT: Final[int] = 500


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
        """Initialize the UserService.

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

    async def _get_existing_user_or_raise(
        self,
        user_id: str,
        *,
        operation: str,
        not_found_message: str = "User not found",
    ) -> User:
        """Fetch an existing user by canonical identifier or raise a 404 AppException.

        Args:
            user_id: Canonical User identifier (usr_<hex32>) to resolve.
            operation: Calling operation label for structured error diagnostics.
            not_found_message: Client-facing 404 error message.

        Returns:
            Resolved User domain model.

        Raises:
            AppException: With ErrorCodes.RESOURCE_NOT_FOUND if the user does not exist, or
                ErrorCodes.STORAGE_ACCESS_FAILED if persistence lookup fails.
        """
        user = await self.repo.get_by_id(user_id)
        if user is None:
            logger.error(
                "[UserService] %s: User %s not found during %s.",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                user_id,
                operation,
                exc_info=True,
            )
            raise AppException(
                message=not_found_message,
                status_code=404,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )
        return user

    async def _ensure_not_last_org_admin(
        self,
        org_id: str,
        *,
        conflict_message: str,
    ) -> None:
        """Verify that an organization retains more than one active administrator.

        Args:
            org_id: Canonical Organization identifier (org_<hex32>) to inspect.
            conflict_message: Error message emitted when Last Admin Protection triggers.

        Raises:
            ConflictError: With ErrorCodes.CONFLICT_ERROR if only one active administrator remains.
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED if listing users fails.
        """
        admin_count = await self._count_org_admins(org_id)
        if admin_count <= 1:
            logger.error(
                "[UserService] %s: %s (org_id=%s).",
                ErrorCodes.CONFLICT_ERROR.name,
                conflict_message,
                org_id,
                exc_info=True,
            )
            raise ConflictError(
                message=conflict_message,
                details={"error_code": ErrorCodes.CONFLICT_ERROR.value, "reason": "LAST_ADMIN_PROTECTION"},
            )

    async def _ensure_target_deletable(
        self,
        target: User,
        *,
        conflict_message: str,
    ) -> None:
        """Enforce primary Root account immunity and Last Admin Protection prior to deletion.

        Args:
            target: Target User model scheduled for GDPR soft-deletion.
            conflict_message: Error message emitted when Last Admin Protection triggers.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if targeting SYSTEM_ROOT_USER_ID.
            ConflictError: With ErrorCodes.CONFLICT_ERROR if deleting the last active org administrator.
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED if listing users fails.
        """
        if target.id == SYSTEM_ROOT_USER_ID:
            logger.error(
                "[UserService] %s: Attempted to delete protected Root account %s.",
                ErrorCodes.PERMISSION_DENIED.name,
                target.id,
                exc_info=True,
            )
            raise PermissionDeniedError("The primary Root account cannot be deleted.")

        if target.role == UserRole.ADMIN and target.organization_id:
            await self._ensure_not_last_org_admin(
                target.organization_id,
                conflict_message=conflict_message,
            )

    async def _apply_user_update_or_raise(
        self,
        target_id: str,
        updates: UserUpdate,
        *,
        failure_message: str,
    ) -> User:
        """Persist an in-place user update and verify the refreshed model is returned.

        Args:
            target_id: Canonical User identifier (usr_<hex32>) to update.
            updates: Validated partial UserUpdate payload.
            failure_message: Error message emitted if persistence returns None.

        Returns:
            Refreshed User domain model after update.

        Raises:
            AppException: With ErrorCodes.INTERNAL_SERVER_ERROR if the updated user cannot be reloaded,
                or ErrorCodes.STORAGE_ACCESS_FAILED if persistence fails.
        """
        updated_user = await self.repo.update(target_id, updates)
        if updated_user is None:
            logger.error(
                "[UserService] %s: %s (target_id=%s).",
                ErrorCodes.INTERNAL_SERVER_ERROR.name,
                failure_message,
                target_id,
                exc_info=True,
            )
            raise AppException(
                message=failure_message,
                status_code=500,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
            )
        return updated_user

    async def _revoke_user_sessions_if_configured(self, user_id: str) -> None:
        """Revoke all active JWT sessions for a user when a Redis revocation cache is configured.

        Args:
            user_id: Canonical User identifier (usr_<hex32>) whose sessions must be revoked.

        Raises:
            AppException: With ErrorCodes.SERVICE_UNAVAILABLE if Redis revocation fails.
        """
        if self.revocation_cache is not None:
            await self.revocation_cache.revoke_user_sessions(
                user_id,
                ttl_seconds=get_settings().iam_revocation_ttl_seconds,
            )

    async def create_user(self, creator_id: str, user_data: UserCreate) -> User:
        """Create a new user while enforcing role hierarchy and multi-tenant isolation.

        Args:
            creator_id: Canonical ID of the user initiating the creation.
            user_data: Validated user creation payload.

        Returns:
            Newly created User domain model.

        Raises:
            AppException: With ErrorCodes.RESOURCE_NOT_FOUND if creator is not found,
                ErrorCodes.VALIDATION_FAILED if target organization does not exist, or
                ErrorCodes.INTERNAL_SERVER_ERROR if Firebase creation fails.
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if hierarchy or org constraints are violated.
            ConflictError: With ErrorCodes.CONFLICT_ERROR if the provisioned user ID already exists.
        """
        return await self._create_user_internal(creator_id, user_data)

    async def _create_user_internal(
        self, creator_id: str, user_data: UserCreate, force_org_id: str | None = None
    ) -> User:
        """Create a user internally with an optional forced organization assignment.

        Args:
            creator_id: Canonical ID of the user initiating the creation.
            user_data: Validated user creation payload.
            force_org_id: Optional organization ID overriding standard tenant derivation.

        Returns:
            Newly created User domain model.

        Raises:
            AppException: With ErrorCodes.RESOURCE_NOT_FOUND if creator is not found,
                ErrorCodes.VALIDATION_FAILED if target organization does not exist, or
                ErrorCodes.INTERNAL_SERVER_ERROR if Firebase creation fails.
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if hierarchy or org constraints are violated.
            ConflictError: With ErrorCodes.CONFLICT_ERROR if the provisioned user ID already exists.
        """
        creator = await self._get_existing_user_or_raise(
            creator_id,
            operation="create_user",
            not_found_message="Creator not found",
        )

        target_org_id = await self._resolve_target_org_for_creation(creator, user_data, force_org_id)
        self._enforce_hierarchy(creator, user_data.role)
        new_id = await self._provision_firebase_or_local_user_id(user_data)

        new_user = User(
            id=new_id,
            email=user_data.email,
            name=user_data.name,
            role=user_data.role,
            organization_id=target_org_id,
            created_at=datetime.now(UTC),
            created_by=creator.id,
            is_active=user_data.is_active,
            language=user_data.language,
            theme_mode=user_data.theme_mode,
        )
        saved_user = await self.repo.create(new_user)

        if self.audit_service is not None:
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

    async def _provision_firebase_or_local_user_id(self, user_data: UserCreate) -> str:
        """Provision a Firebase user ID within a bounded timeout or generate a canonical UUIDv7 user ID.

        Args:
            user_data: Validated UserCreate payload.

        Returns:
            Provisioned user ID string.

        Raises:
            AppException: With ErrorCodes.INTERNAL_SERVER_ERROR if Firebase creation or lookup fails.
        """
        if self.use_firebase and self.firebase_auth is not None and user_data.password:
            timeout_seconds = get_settings().http_client_timeout_seconds
            try:
                async with asyncio.timeout(timeout_seconds):
                    fb_user = await asyncio.to_thread(
                        self.firebase_auth.create_user,
                        email=user_data.email,
                        password=user_data.password,
                        name=user_data.name,
                    )
                return str(fb_user.id)
            except (AppException, OSError, ValueError, KeyError, RuntimeError, TypeError) as e:
                try:
                    async with asyncio.timeout(timeout_seconds):
                        existing = await asyncio.to_thread(
                            self.firebase_auth.get_user_by_email,
                            user_data.email,
                        )
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
        """Enforce role hierarchy rules for user creation.

        Args:
            creator: User attempting to create another user.
            target_role: Role being assigned to the new user.

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
        """Count the number of active, non-deleted administrators in an organization.

        Args:
            org_id: Canonical ID of the organization.

        Returns:
            Number of active, non-deleted admin users.

        Raises:
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED or ErrorCodes.VALIDATION_FAILED
                if listing users fails.
        """
        all_users = await self.repo.list_all()
        return sum(
            1
            for u in all_users
            if u.organization_id == org_id and u.role == UserRole.ADMIN and u.is_active and u.deleted_at is None
        )

    async def get_users_by_organization(self, organization_id: str) -> list[User]:
        """Retrieve all users belonging to a given organization.

        Args:
            organization_id: Target organization identifier (org_<hex32>).

        Returns:
            List of users belonging to the organization.

        Raises:
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED or ErrorCodes.VALIDATION_FAILED
                if persistence query fails.
        """
        return await self.repo.get_by_organization(organization_id)

    async def delete_user(self, initiator_id: str, target_id: str) -> bool:
        """Execute in-place GDPR Soft-Delete anonymization on a user with Last Admin Protection.

        Args:
            initiator_id: Canonical ID of the user attempting deletion.
            target_id: Canonical ID of the user to delete.

        Returns:
            True if soft-deletion succeeded.

        Raises:
            AppException: With ErrorCodes.RESOURCE_NOT_FOUND if either user is not found, or
                ErrorCodes.INTERNAL_SERVER_ERROR if Firebase deletion fails.
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if permissions are insufficient or target is protected.
            ConflictError: With ErrorCodes.CONFLICT_ERROR if deleting the user violates Last Admin Protection.
        """
        # Execute in-place GDPR Soft-Delete anonymization preserving execution foreign keys
        logger.info("[UserService] delete_user called. Initiator: %s, Target: %s", initiator_id, target_id)

        initiator = await self._get_existing_user_or_raise(initiator_id, operation="delete_user")
        target = await self._get_existing_user_or_raise(target_id, operation="delete_user")

        await self._validate_delete_user_permissions(initiator, target)
        await self._delete_firebase_user_if_enabled(target.id)
        await self._execute_gdpr_soft_delete(target)

        if self.audit_service is not None:
            await self.audit_service.log_event(
                actor_id=initiator_id,
                action="USER_DELETED",
                organization_id=target.organization_id,
                target_id=target_id,
                details={"email": target.email, "gdpr_soft_delete": True},
            )

        return True

    async def _validate_delete_user_permissions(self, initiator: User, target: User) -> None:
        """Validate RBAC permissions, Root protection, and Last Admin Protection for user deletion.

        Args:
            initiator: User initiating the deletion.
            target: Target user being deleted.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if permissions are insufficient or target is protected.
            ConflictError: With ErrorCodes.CONFLICT_ERROR if deleting the last active administrator.
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED if listing users fails.
        """
        if initiator.role != UserRole.ROOT:
            if initiator.role == UserRole.ADMIN:
                if target.organization_id != initiator.organization_id:
                    logger.error(
                        "[UserService] %s: Admin %s attempted to delete user %s from foreign organization %s.",
                        ErrorCodes.PERMISSION_DENIED.name,
                        initiator.id,
                        target.id,
                        target.organization_id,
                        exc_info=True,
                    )
                    raise PermissionDeniedError("Cannot delete users from other organizations")
            else:
                logger.error(
                    "[UserService] %s: User %s with role %s lacks permission to delete user %s.",
                    ErrorCodes.PERMISSION_DENIED.name,
                    initiator.id,
                    initiator.role.value,
                    target.id,
                    exc_info=True,
                )
                raise PermissionDeniedError("Insufficient permissions to delete users")

        await self._ensure_target_deletable(
            target,
            conflict_message=(
                "LAST_ADMIN_PROTECTION: Cannot delete the last Administrator of an Organization. "
                "Promote another user first."
            ),
        )

    async def _delete_firebase_user_if_enabled(self, user_id: str) -> None:
        """Delete the corresponding Firebase Auth user within a bounded timeout when enabled.

        Args:
            user_id: Target user identifier.

        Raises:
            AppException: With ErrorCodes.INTERNAL_SERVER_ERROR if Firebase deletion fails or times out.
        """
        if self.use_firebase and self.firebase_auth is not None:
            timeout_seconds = get_settings().http_client_timeout_seconds
            try:
                logger.info("[UserService] Deleting Firebase user %s...", user_id)
                async with asyncio.timeout(timeout_seconds):
                    await asyncio.to_thread(self.firebase_auth.delete_user, user_id)
            except (AppException, OSError, ValueError, KeyError, RuntimeError, TypeError) as fb_err:
                logger.error(
                    "[UserService] %s: Failed to delete user %s in Firebase: %s",
                    ErrorCodes.INTERNAL_SERVER_ERROR.name,
                    user_id,
                    fb_err,
                    exc_info=True,
                )
                raise AppException(
                    message=f"Failed to delete user {user_id} in Firebase: {fb_err}",
                    status_code=500,
                    details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                ) from fb_err

    async def _execute_gdpr_soft_delete(self, target: User) -> User:
        """Revoke active Redis sessions and anonymize the User record in-place.

        Args:
            target: Target User model to soft-delete.

        Returns:
            Anonymized User model persisted in the repository.

        Raises:
            AppException: With ErrorCodes.SERVICE_UNAVAILABLE if Redis revocation fails, or
                ErrorCodes.STORAGE_ACCESS_FAILED if persistence fails.
        """
        # Trigger RevocationCache kill-switch before anonymizing the user record
        await self._revoke_user_sessions_if_configured(target.id)

        # In-place GDPR anonymization preserving executions foreign keys
        anonymized = target.model_copy(
            update={
                "is_active": False,
                "deleted_at": datetime.now(UTC),
                "email": f"deleted_{target.id}@anonymized.quorum.local",
                "name": "Anonymized User",
                "firebase_uid": None,
            }
        )
        await self.repo.repo.create_user(anonymized)
        return anonymized

    async def soft_delete_by_firebase_uid(self, firebase_uid: str) -> bool:
        """Execute in-place GDPR Soft-Delete anonymization for a user identified by firebase_uid.

        Args:
            firebase_uid: External Firebase Auth UID or canonical user ID.

        Returns:
            True if the user was found and soft-deleted.

        Raises:
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if no user matches firebase_uid.
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if targeting SYSTEM_ROOT_USER_ID.
            ConflictError: With ErrorCodes.CONFLICT_ERROR if deleting the last active administrator.
            AppException: With ErrorCodes.SERVICE_UNAVAILABLE or ErrorCodes.STORAGE_ACCESS_FAILED
                if session revocation or persistence fails.
        """
        # Webhook-triggered GDPR Soft-Delete by firebase_uid
        target = await self.repo.get_by_firebase_uid(firebase_uid)
        if target is None:
            target = await self.repo.get_by_id(firebase_uid)
        if target is None:
            logger.error(
                "[UserService] %s: User with firebase_uid=%s not found for soft_delete_by_firebase_uid.",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                firebase_uid,
                exc_info=True,
            )
            raise ResourceNotFoundError(resource_type="user", resource_id=firebase_uid)

        await self._ensure_target_deletable(
            target,
            conflict_message="LAST_ADMIN_PROTECTION: Cannot delete the last Administrator of an Organization.",
        )

        await self._execute_gdpr_soft_delete(target)
        if self.audit_service is not None:
            await self.audit_service.log_event(
                actor_id=SYSTEM_ROOT_USER_ID,
                action="USER_DELETED",
                organization_id=target.organization_id,
                target_id=target.id,
                details={"source": "firebase_webhook", "gdpr_soft_delete": True},
            )
        return True

    async def verify_and_soft_delete_firebase_webhook(
        self,
        firebase_uid: str,
        signature_header: str | None,
        raw_body: bytes = b"",
    ) -> UserDeleteResponse:
        """Verify X-Quorum-Webhook-Signature HMAC against firebase_webhook_secret and soft-delete user.

        Args:
            firebase_uid: External Firebase UID of the deleted user.
            signature_header: Value of X-Quorum-Webhook-Signature request header.
            raw_body: Optional raw request body bytes signed by the webhook sender.

        Returns:
            UserDeleteResponse confirming GDPR soft-deletion.

        Raises:
            AppException: With ErrorCodes.CONFIGURATION_ERROR if firebase_webhook_secret is not configured.
            AuthenticationError: With ErrorCodes.AUTHENTICATION_FAILED if HMAC signature is missing or invalid.
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if user is not found.
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if targeting SYSTEM_ROOT_USER_ID.
            ConflictError: With ErrorCodes.CONFLICT_ERROR if deleting the last active administrator.
        """
        # Validate X-Quorum-Webhook-Signature HMAC against firebase_webhook_secret
        settings = get_settings()
        if settings.firebase_webhook_secret is None:
            msg = "Firebase webhook secret is not configured."
            logger.error("[UserService] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        if not signature_header or not signature_header.strip():
            msg = "Missing X-Quorum-Webhook-Signature header."
            logger.error("[UserService] %s: %s", ErrorCodes.AUTHENTICATION_FAILED.name, msg, exc_info=True)
            raise AuthenticationError(msg)

        secret_bytes = settings.firebase_webhook_secret.get_secret_value().encode("utf-8")
        normalized_sig = signature_header.strip().removeprefix("sha256=")
        expected_uid_sig = hmac.new(secret_bytes, firebase_uid.encode("utf-8"), hashlib.sha256).hexdigest()
        expected_body_sig = (
            hmac.new(secret_bytes, raw_body, hashlib.sha256).hexdigest() if raw_body else expected_uid_sig
        )

        if not (
            hmac.compare_digest(expected_uid_sig, normalized_sig)
            or hmac.compare_digest(expected_body_sig, normalized_sig)
        ):
            msg = "Invalid X-Quorum-Webhook-Signature header."
            logger.error("[UserService] %s: %s", ErrorCodes.AUTHENTICATION_FAILED.name, msg, exc_info=True)
            raise AuthenticationError(msg)

        await self.soft_delete_by_firebase_uid(firebase_uid)
        return UserDeleteResponse(status="success", id=firebase_uid)

    async def update_user(self, initiator_id: str, target_id: str, updates: UserUpdate) -> User:
        """Update user fields while enforcing 4-Tier RBAC, hierarchy, and Last Admin Protection.

        Args:
            initiator_id: Canonical ID of the user initiating the update.
            target_id: Canonical ID of the user to update.
            updates: Validated partial update payload.

        Returns:
            Updated User domain model.

        Raises:
            AppException: With ErrorCodes.RESOURCE_NOT_FOUND if user is not found, or
                ErrorCodes.INTERNAL_SERVER_ERROR if repository update fails.
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if hierarchy or org constraints are violated.
            ConflictError: With ErrorCodes.CONFLICT_ERROR if Last Admin Protection is violated.
        """
        initiator = await self._get_existing_user_or_raise(initiator_id, operation="update_user")
        target = await self._get_existing_user_or_raise(target_id, operation="update_user")

        self._validate_update_user_permissions(initiator, target, updates)
        await self._enforce_last_admin_protection_on_update(target, updates)

        updated_user = await self._apply_user_update_or_raise(
            target_id,
            updates,
            failure_message="User update failed (not found despite check).",
        )

        await self._maybe_revoke_sessions_on_update(target, updates)

        if self.audit_service is not None:
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
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED if listing users fails.
        """
        if target.role != UserRole.ADMIN or not target.organization_id:
            return
        if not target.is_active or target.deleted_at is not None:
            return

        demoting_admin = updates.role is not None and updates.role != UserRole.ADMIN
        deactivating_admin = updates.is_active is False
        if not demoting_admin and not deactivating_admin:
            return

        await self._ensure_not_last_org_admin(
            target.organization_id,
            conflict_message="LAST_ADMIN_PROTECTION: Cannot demote the last Administrator of an Organization.",
        )

    async def _maybe_revoke_sessions_on_update(self, target: User, updates: UserUpdate) -> None:
        """Trigger immediate Redis Kill-Switch when role, organization_id, or active status changes.

        Args:
            target: User record prior to update.
            updates: Applied UserUpdate payload.

        Raises:
            AppException: With ErrorCodes.SERVICE_UNAVAILABLE if Redis session revocation fails.
        """
        role_changed = updates.role is not None and updates.role != target.role
        org_changed = updates.organization_id is not None and updates.organization_id != target.organization_id
        deactivated = updates.is_active is False
        if role_changed or org_changed or deactivated:
            await self._revoke_user_sessions_if_configured(target.id)

    async def update_user_role(self, initiator_id: str, target_id: str, new_role: UserRole) -> User:
        """Update a user's role with strict Last Admin Protection and immediate Redis session revocation.

        Args:
            initiator_id: Canonical ID of the user changing the role.
            target_id: Canonical ID of the user whose role is changing.
            new_role: New role to assign.

        Returns:
            Updated User domain model.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if hierarchy or tenancy rules are violated.
            AppException: With ErrorCodes.RESOURCE_NOT_FOUND if user is not found, or
                ErrorCodes.INTERNAL_SERVER_ERROR if repository update fails.
            ConflictError: With ErrorCodes.CONFLICT_ERROR if Last Admin Protection is triggered.
        """
        initiator = await self._get_existing_user_or_raise(initiator_id, operation="update_user_role")
        target = await self._get_existing_user_or_raise(target_id, operation="update_user_role")

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

        if target.role == UserRole.ADMIN and new_role != UserRole.ADMIN and target.organization_id:
            await self._ensure_not_last_org_admin(
                target.organization_id,
                conflict_message="LAST_ADMIN_PROTECTION: Cannot demote the last Administrator.",
            )

        updated = await self._apply_user_update_or_raise(
            target_id,
            UserUpdate(role=new_role),
            failure_message="User update failed (user reference lost).",
        )

        if new_role != target.role:
            await self._revoke_user_sessions_if_configured(target_id)

        if self.audit_service is not None:
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
            initiator: Verified token data of the user requesting the list.

        Returns:
            List of users scoped to the initiator's role and organization.

        Raises:
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED or ErrorCodes.VALIDATION_FAILED
                if persistence query fails.
        """
        all_users: list[User] = await self.repo.list_all()

        if initiator.role == UserRole.ROOT:
            return all_users

        if initiator.role in (UserRole.MEMBER, UserRole.VIEWER):
            return [u for u in all_users if u.id == initiator.id]

        org_id = initiator.organization_id
        return [u for u in all_users if u.organization_id == org_id]

    async def get_user(self, initiator: TokenData, target_id: str) -> User:
        """Fetch a user securely enforcing the 4-Tier RBAC Governance Matrix.

        Args:
            initiator: Verified token data of the user requesting the fetch.
            target_id: Canonical ID of the user to fetch.

        Returns:
            Requested User domain model.

        Raises:
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the user does not exist.
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the initiator lacks access.
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED or ErrorCodes.VALIDATION_FAILED
                if persistence lookup fails.
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
        """Ensure the system organization exists and verify the canonical root user is anchored to it.

        Args:
            email: Fallback contact email parameter retained for bootstrap signature parity.

        Returns:
            Canonical root User domain model.

        Raises:
            AppException: With ErrorCodes.CONFIGURATION_ERROR if the root user is missing from the database,
                or ErrorCodes.INTERNAL_SERVER_ERROR if refreshing the root user fails.
        """
        _ = email
        if not await self.org_repo.get_by_id(SystemOrganizations.ROOT_SYSTEM):
            logger.info("[UserService] Creating 'system' Organization.")

            await self.org_repo.create(
                Organization(
                    id=SystemOrganizations.ROOT_SYSTEM,
                    name="System Administration",
                    created_at=datetime.now(UTC),
                    is_active=True,
                    tier="enterprise",
                    subscription_status=SubscriptionStatus.ACTIVE,
                    quota_limit=_SYSTEM_ORG_DEFAULT_QUOTA_LIMIT,
                    tpm_limit=_SYSTEM_ORG_DEFAULT_TPM_LIMIT,
                    rpm_limit=_SYSTEM_ORG_DEFAULT_RPM_LIMIT,
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
                message=(
                    "Root user 'root_master' missing from DB. Run 'uv run python backend_v2/seed/run_seed.py local'."
                ),
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        if root.organization_id != SystemOrganizations.ROOT_SYSTEM:
            logger.info(
                "Fixing root_master organization_id from '%s' to '%s'",
                root.organization_id,
                SystemOrganizations.ROOT_SYSTEM,
            )

            root = await self._apply_user_update_or_raise(
                SYSTEM_ROOT_USER_ID,
                UserUpdate(organization_id=SystemOrganizations.ROOT_SYSTEM),
                failure_message="Failed to obtain Root user.",
            )

        return root
