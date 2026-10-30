"""Organization Management Service for tenant lifecycle and isolation."""

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
    Organization,
    OrganizationCreate,
    OrganizationUpdateDTO,
    SubscriptionStatus,
    SystemOrganizations,
    TokenData,
    UserCreate,
    UserRole,
)
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.enums import EntityPrefix, SystemLocale
from backend_v2.services.auth.constants import LEGACY_SYSTEM_ORG_ID
from backend_v2.services.auth.protocols import UserCreatorProtocol
from backend_v2.services.auth.repositories import (
    OrganizationRepository,
    UserRepository,
)

logger = logging.getLogger(__name__)

__all__ = ["OrganizationService"]


class OrganizationService:
    """Tenant Organization Management Service.

    Attributes:
        org_repo: Repository wrapper for organization operations.
        user_repo: Repository wrapper for user operations.
        audit_service: Optional service for recording audit logs.
        use_firebase: Flag indicating if Firebase integration is enabled.
        firebase_auth: Optional Firebase authentication module or mock.
        user_creator: Optional protocol handler for creating users.
    """

    def __init__(
        self,
        org_repo: OrganizationRepository,
        user_repo: UserRepository,
        audit_service: Any = None,
        use_firebase: bool = False,
        firebase_auth: Any = None,
        user_creator: UserCreatorProtocol | None = None,
    ) -> None:
        """Initializes the OrganizationService.

        Args:
            org_repo: Repository wrapper for organization operations.
            user_repo: Repository wrapper for user operations.
            audit_service: Optional service for recording audit logs.
            use_firebase: Flag indicating if Firebase integration is enabled.
            firebase_auth: Optional Firebase authentication module or mock.
            user_creator: Optional protocol handler for creating users.
        """
        self.org_repo = org_repo
        self.user_repo = user_repo
        self.audit_service = audit_service
        self.use_firebase = use_firebase
        self.firebase_auth = firebase_auth
        self.user_creator = user_creator

    async def create_organization(self, initiator: TokenData, org_create: OrganizationCreate) -> Organization:
        """Creates a new Tenant Organization and an initial Admin user for it.

        Args:
            initiator: Token data of the user creating the organization.
            org_create: The organization creation payload.

        Returns:
            The newly created organization.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the initiator is not ROOT.
            AppException: With ErrorCodes.CONFIGURATION_ERROR if UserCreatorProtocol is not configured.
        """
        if initiator.role != UserRole.ROOT:
            logger.error(
                "[OrganizationService] %s: Only ROOT can create organizations (initiator=%s).",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                exc_info=True,
            )
            raise PermissionDeniedError("Only ROOT can create organizations.")

        # Generate canonical 32-hex RFC 9562 UUIDv7 organization ID
        org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)

        new_org = Organization(
            id=org_id,
            name=org_create.name,
            created_at=datetime.now(timezone.utc),
            is_active=True,
            tier="enterprise",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=500.0,
            tpm_limit=org_create.tpm_limit,
            rpm_limit=org_create.rpm_limit,
        )

        await self.org_repo.create(new_org)

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

        if self.user_creator is None:
            logger.error(
                "[OrganizationService] %s: UserCreatorProtocol is not configured.",
                ErrorCodes.CONFIGURATION_ERROR.name,
                exc_info=True,
            )
            raise AppException(
                message="Cannot create organization: UserCreatorProtocol is not configured.",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        await self.user_creator(initiator.id, admin_payload, force_org_id=org_id)

        if self.audit_service is not None:
            await self.audit_service.log_event(
                actor_id=initiator.id,
                action="ORG_CREATED",
                organization_id=org_id,
                target_id=org_id,
                details={"name": new_org.name, "tier": new_org.tier},
            )

        return new_org

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

        Returns:
            None

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the initiator is not ROOT or targets system org.
            ConflictError: With ErrorCodes.CONFLICT_ERROR if the organization is not empty and force is False.
            AppException: With ErrorCodes.INTERNAL_SERVER_ERROR if Firebase cascade user deletion fails.
        """
        logger.info(
            "[OrganizationService] delete_organization called. Initiator: %s, Target: %s, Force: %s",
            initiator.id,
            target_org_id,
            force,
        )

        if initiator.role != UserRole.ROOT:
            logger.error(
                "[OrganizationService] %s: Only ROOT can delete organizations (initiator=%s, target=%s).",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                target_org_id,
                exc_info=True,
            )
            raise PermissionDeniedError("Only ROOT can delete organizations.")

        if target_org_id in (
            SystemOrganizations.ROOT_SYSTEM,
            SystemOrganizations.ROOT_SYSTEM.value,
            SystemOrganizations.LEGACY_SYSTEM,
            SystemOrganizations.LEGACY_SYSTEM.value,
            "system",
            LEGACY_SYSTEM_ORG_ID,
        ):
            logger.error(
                "[OrganizationService] %s: Attempted to delete protected system organization %s (initiator=%s).",
                ErrorCodes.PERMISSION_DENIED.name,
                target_org_id,
                initiator.id,
                exc_info=True,
            )
            raise PermissionDeniedError("CRITICAL: The 'system' organization is protected and CANNOT be deleted.")

        logger.info("[OrganizationService] Fetching users to check for safety...")

        all_users = await self.user_repo.list_all()
        org_users = [u for u in all_users if u.organization_id == target_org_id]

        user_count = len(org_users)
        logger.info("[OrganizationService] Organization %s has %s users.", target_org_id, user_count)

        if user_count > 0 and not force:
            logger.error(
                "[OrganizationService] %s: Organization is not empty (%s users). Use force=True to delete.",
                ErrorCodes.CONFLICT_ERROR.name,
                user_count,
                exc_info=True,
            )
            raise ConflictError(
                message=f"Organization is not empty ({user_count} users). Use force=True to delete.",
                details={"error_code": ErrorCodes.CONFLICT_ERROR.value, "reason": "ORG_NOT_EMPTY", "count": user_count},
            )

        if user_count > 0:
            logger.info("[OrganizationService] FORCE DELETE enabled. Removing %s users...", user_count)
            for user in org_users:
                if self.use_firebase and self.firebase_auth is not None:
                    try:
                        await asyncio.to_thread(self.firebase_auth.delete_user, user.id)
                    except (AppException, OSError, ValueError, KeyError, RuntimeError, TypeError) as fb_err:
                        logger.error(
                            "[OrganizationService] %s: Failed to cascade delete user %s in Firebase: %s",
                            ErrorCodes.INTERNAL_SERVER_ERROR.name,
                            user.id,
                            fb_err,
                            exc_info=True,
                        )
                        raise AppException(
                            message=f"Failed to cascade delete user {user.id} in Firebase: {fb_err}",
                            status_code=500,
                            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                        ) from fb_err

                await self.user_repo.delete(user.id)

        logger.info("[OrganizationService] Removing Organization %s from DB...", target_org_id)
        await self.org_repo.delete(target_org_id)

        if self.audit_service is not None:
            await self.audit_service.log_event(
                actor_id=initiator.id,
                action="ORG_DELETED",
                organization_id=target_org_id,
                target_id=target_org_id,
                details={"users_deleted": user_count, "force_used": force},
            )

    async def list_organizations(self, initiator: TokenData) -> list[Organization]:
        """List organizations securely scoped by Tenant/Organization.

        Args:
            initiator: The token data of the user requesting the list.

        Returns:
            A list of organizations scoped to the initiator's permissions.

        Raises:
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the tenant's organization does not exist.
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the initiator lacks access.
        """
        if initiator.role != UserRole.ROOT:
            if not initiator.organization_id:
                return []
            return [await self.get_organization(initiator, initiator.organization_id)]
        return await self.org_repo.list_all()

    async def get_organization(self, initiator: TokenData, org_id: str) -> Organization:
        """Fetch organization securely.

        Args:
            initiator: The token data of the user requesting the fetch.
            org_id: The ID of the organization to fetch.

        Returns:
            The requested organization model.

        Raises:
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the organization does not exist.
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the initiator lacks access.
        """
        org = await self.org_repo.get_by_id(org_id)

        if not org:
            logger.error(
                "[OrganizationService] %s: Organization not found (org_id=%s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                org_id,
                exc_info=True,
            )
            raise ResourceNotFoundError(resource_type="organization", resource_id=org_id)

        if initiator.role != UserRole.ROOT and initiator.organization_id != org_id:
            logger.error(
                "[OrganizationService] %s: %s tried to read foreign org %s",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                org_id,
                exc_info=True,
            )
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
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the initiator is not ROOT.
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the organization does not exist.
        """
        if initiator.role != UserRole.ROOT:
            logger.error(
                "[OrganizationService] %s: Only ROOT can update organizations (initiator=%s, org_id=%s).",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                org_id,
                exc_info=True,
            )
            raise PermissionDeniedError("Only ROOT can update organizations.")

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
        await self.org_repo.update(org_id, update_dto)

        return await self.get_organization(initiator, org_id)
