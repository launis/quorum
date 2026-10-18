"""Organization Management Service for tenant lifecycle and isolation."""

from __future__ import annotations

import asyncio
import logging
import uuid
from collections.abc import Callable, Coroutine
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
    User,
    UserCreate,
    UserRole,
)
from backend_v2.models.enums import SystemLocale
from backend_v2.services.auth.constants import LEGACY_SYSTEM_ORG_ID
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
        create_user_fn: Optional callable for creating users.
    """

    def __init__(
        self,
        org_repo: OrganizationRepository,
        user_repo: UserRepository,
        audit_service: Any = None,
        use_firebase: bool = False,
        firebase_auth: Any = None,
        create_user_fn: Callable[..., Coroutine[Any, Any, User]] | None = None,
    ) -> None:
        """Initializes the OrganizationService.

        Args:
            org_repo: Repository wrapper for organization operations.
            user_repo: Repository wrapper for user operations.
            audit_service: Optional service for recording audit logs.
            use_firebase: Flag indicating if Firebase integration is enabled.
            firebase_auth: Optional Firebase authentication module or mock.
            create_user_fn: Optional callable for creating users.
        """
        self.org_repo = org_repo
        self.user_repo = user_repo
        self.audit_service = audit_service
        self.use_firebase = use_firebase
        self.firebase_auth = firebase_auth
        self.create_user_fn = create_user_fn

    async def create_organization(self, initiator: TokenData, org_create: OrganizationCreate) -> Organization:
        """Creates a new Tenant Organization and an initial Admin user for it.

        Args:
            initiator: Token data of the user creating the organization.
            org_create: The organization creation payload.

        Returns:
            The newly created organization.

        Raises:
            PermissionDeniedError: If the initiator is not ROOT.
        """
        if initiator.role != UserRole.ROOT:
            raise PermissionDeniedError("Only ROOT can create organizations.")

        org_id = f"org_{uuid.uuid4().hex}"

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

        if self.create_user_fn is not None:
            await self.create_user_fn(initiator.id, admin_payload, force_org_id=org_id)

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
            PermissionDeniedError: If the initiator is not ROOT or targets system org.
            ConflictError: If the organization is not empty and force is False.
        """
        logger.info(
            "[OrganizationService] delete_organization called. Initiator: %s, Target: %s, Force: %s",
            initiator.id,
            target_org_id,
            force,
        )

        if initiator.role != UserRole.ROOT:
            raise PermissionDeniedError("Only ROOT can delete organizations.")

        if target_org_id in (
            SystemOrganizations.ROOT_SYSTEM,
            SystemOrganizations.ROOT_SYSTEM.value,
            SystemOrganizations.LEGACY_SYSTEM,
            SystemOrganizations.LEGACY_SYSTEM.value,
            "system",
            LEGACY_SYSTEM_ORG_ID,
        ):
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
                        if isinstance(fb_err, (KeyboardInterrupt, SystemExit)):
                            raise
                        logger.warning("Failed to cascade delete user %s in Firebase: %s", user.id, fb_err)

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
        """
        if initiator.role != UserRole.ROOT:
            if not initiator.organization_id:
                return []
            org = await self.get_organization(initiator, initiator.organization_id)
            if org:
                return [org]
            return []
        return await self.org_repo.list_all()

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

        if initiator.role != UserRole.ROOT and initiator.organization_id != org_id:
            logger.warning(
                "[OrganizationService] PERMISSION_DENIED: %s tried to read foreign org %s", initiator.id, org_id
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
            PermissionDeniedError: If the initiator is not ROOT.
            ResourceNotFoundError: If the organization does not exist.
        """
        if initiator.role != UserRole.ROOT:
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
