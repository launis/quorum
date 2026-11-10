"""Organization Management Service for tenant lifecycle, B2B invitations, and isolation."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import secrets
from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from typing import Any, NoReturn

from pydantic import SecretStr

from backend_v2.database.interfaces import (
    EntityPersistencePort,
    UnitOfWorkFactory,
    get_registered_uow_factory,
)
from backend_v2.exceptions import (
    AppException,
    ConfigurationError,
    ConflictError,
    ErrorCodes,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from backend_v2.models.auth import (
    Invitation,
    InvitationAcceptRequestDTO,
    InvitationBatchCreateDTO,
    InvitationBatchResponseDTO,
    InvitationCreateDTO,
    InvitationResponseDTO,
    Organization,
    OrganizationCreate,
    OrganizationUpdateDTO,
    SubscriptionStatus,
    SystemOrganizations,
    TokenData,
    TransactionalEmailItemDTO,
    User,
    UserCreate,
    UserRole,
    UserUpdate,
)
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.enums import (
    EmailDeliveryStatus,
    EntityPrefix,
    InvitationStatus,
    SystemLocale,
)
from backend_v2.services.auth.email_service import EmailService
from backend_v2.services.auth.protocols import UserCreatorProtocol
from backend_v2.services.auth.repositories import (
    OrganizationRepository,
    UserRepository,
)
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = ["OrganizationService"]


class OrganizationService:
    """Tenant Organization Management and B2B Invitation Service.

    Attributes:
        org_repo: Repository wrapper for organization operations.
        user_repo: Repository wrapper for user operations.
        audit_service: Optional service for recording audit logs.
        use_firebase: Flag indicating if Firebase integration is enabled.
        firebase_auth: Optional Firebase authentication module or mock.
        user_creator: Optional protocol handler for creating users.
        email_service: Transactional email dispatch service.
    """

    def __init__(
        self,
        org_repo: OrganizationRepository,
        user_repo: UserRepository,
        audit_service: Any = None,
        use_firebase: bool = False,
        firebase_auth: Any = None,
        user_creator: UserCreatorProtocol | None = None,
        email_service: EmailService | None = None,
        entity_adapter: EntityPersistencePort | None = None,
        uow_factory: UnitOfWorkFactory | None = None,
    ) -> None:
        """Initialize the OrganizationService.

        Args:
            org_repo: Repository wrapper for organization operations.
            user_repo: Repository wrapper for user operations.
            audit_service: Optional service for recording audit logs.
            use_firebase: Flag indicating if Firebase integration is enabled.
            firebase_auth: Optional Firebase authentication module or mock.
            user_creator: Optional protocol handler for creating users.
            email_service: Optional EmailService instance for invitation dispatch.
            entity_adapter: Optional hexagonal entity persistence port for invitations.
            uow_factory: Optional UnitOfWork factory for transactional invitation persistence.
        """
        self.org_repo = org_repo
        self.user_repo = user_repo
        self.audit_service = audit_service
        self.use_firebase = use_firebase
        self.firebase_auth = firebase_auth
        self.user_creator = user_creator
        self.email_service: EmailService = email_service if email_service is not None else EmailService()
        self._entity_adapter: EntityPersistencePort | None = entity_adapter
        self._uow_factory: UnitOfWorkFactory | None = uow_factory
        self._last_generated_tokens: dict[str, str] = {}

    def _resolve_uow_factory(self) -> UnitOfWorkFactory | None:
        """Resolve explicit or globally registered UnitOfWork factory.

        Returns:
            Configured UnitOfWorkFactory callable or None.
        """
        return self._uow_factory if self._uow_factory is not None else get_registered_uow_factory()

    @staticmethod
    def _raise_unconfigured_persistence_error() -> NoReturn:
        """Raise Fail-Fast ConfigurationError when no persistence port or UoW is configured.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR.
        """
        # Enforce single-pipeline invitation persistence with zero local dict fallback
        logger.error(
            "[OrganizationService] %s: OrganizationService requires an entity_adapter or uow_factory.",
            ErrorCodes.CONFIGURATION_ERROR.name,
            exc_info=True,
        )
        raise ConfigurationError(
            message="OrganizationService requires an entity_adapter or uow_factory for invitation persistence.",
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )

    @asynccontextmanager
    async def _acquire_entity_port(
        self,
        *,
        commit: bool = False,
    ) -> AsyncIterator[EntityPersistencePort]:
        """Yield the active EntityPersistencePort from entity_adapter or a UnitOfWork transaction.

        Args:
            commit: Whether to commit the UnitOfWork transaction upon successful exit.

        Yields:
            Configured EntityPersistencePort instance.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
        """
        if self._entity_adapter is not None:
            yield self._entity_adapter
            return
        uow_factory = self._resolve_uow_factory()
        if uow_factory is not None:
            async with uow_factory() as uow:
                yield uow.entities
                if commit:
                    await uow.commit()
            return
        self._raise_unconfigured_persistence_error()

    def get_last_generated_token(self, invitation_id: str) -> str | None:
        """Return the raw token generated for an invitation ID in test/local workflows.

        Args:
            invitation_id: Canonical Invitation ID (inv_<hex32>).

        Returns:
            Raw URL-safe invitation token if generated in this service instance, else None.
        """
        if invitation_id in self._last_generated_tokens:
            return self._last_generated_tokens[invitation_id]
        return None

    async def create_organization(self, initiator: TokenData, org_create: OrganizationCreate) -> Organization:
        """Create a new Tenant Organization and an initial Admin user for it.

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

        org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)

        new_org = Organization(
            id=org_id,
            name=org_create.name,
            created_at=datetime.now(UTC),
            is_active=True,
            tier="enterprise",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=500.0,
            tpm_limit=org_create.tpm_limit,
            rpm_limit=org_create.rpm_limit,
            allowed_email_domains=[],
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
        """Delete an Organization with safety checks and optional cascade user removal.

        Args:
            initiator: Token data of the user deleting the organization.
            target_org_id: The ID of the organization to delete.
            force: If True, cascades deletion to all users in the org.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the initiator is not ROOT or targets system org.
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if target_org_id does not exist.
            ConflictError: With ErrorCodes.CONFLICT_ERROR if the organization is not empty and force is False.
            AppException: With ErrorCodes.INTERNAL_SERVER_ERROR if Firebase cascade user deletion fails.
        """
        if initiator.role != UserRole.ROOT:
            logger.error(
                "[OrganizationService] %s: Only ROOT can delete organizations (initiator=%s, target=%s).",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                target_org_id,
                exc_info=True,
            )
            raise PermissionDeniedError("Only ROOT can delete organizations.")

        if SystemOrganizations.is_system(target_org_id) or target_org_id == "system":
            logger.error(
                "[OrganizationService] %s: Attempted to delete protected system organization %s (initiator=%s).",
                ErrorCodes.PERMISSION_DENIED.name,
                target_org_id,
                initiator.id,
                exc_info=True,
            )
            raise PermissionDeniedError("CRITICAL: The 'system' organization is protected and CANNOT be deleted.")

        await self._fetch_org_or_raise(target_org_id)

        all_users = await self.user_repo.list_all()
        org_users = [u for u in all_users if u.organization_id == target_org_id]
        user_count = len(org_users)

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
            timeout_seconds = get_settings().http_client_timeout_seconds
            for user in org_users:
                if self.use_firebase and self.firebase_auth is not None:
                    try:
                        async with asyncio.timeout(timeout_seconds):
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
        """List organizations securely scoped by the 4-Tier RBAC Governance Matrix.

        Args:
            initiator: The token data of the user requesting the list.

        Returns:
            A list of organizations scoped to the initiator's permissions.

        Raises:
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the tenant's organization does not exist.
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the initiator is MEMBER or VIEWER.
        """
        if initiator.role in (UserRole.MEMBER, UserRole.VIEWER):
            logger.error(
                "[OrganizationService] %s: Role %s denied access to list_organizations (initiator=%s).",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.role.value,
                initiator.id,
                exc_info=True,
            )
            raise PermissionDeniedError("Insufficient permissions to view organization configuration.")

        if initiator.role != UserRole.ROOT:
            if not initiator.organization_id:
                return []
            return [await self.get_organization(initiator, initiator.organization_id)]
        return await self.org_repo.list_all()

    async def get_organization(self, initiator: TokenData, org_id: str) -> Organization:
        """Fetch organization securely enforcing the 4-Tier RBAC Governance Matrix.

        Args:
            initiator: The token data of the user requesting the fetch.
            org_id: The ID of the organization to fetch.

        Returns:
            The requested organization model.

        Raises:
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the organization does not exist.
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the initiator lacks access.
        """
        if initiator.role in (UserRole.MEMBER, UserRole.VIEWER):
            logger.error(
                "[OrganizationService] %s: Role %s denied access to get_organization %s (initiator=%s).",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.role.value,
                org_id,
                initiator.id,
                exc_info=True,
            )
            raise PermissionDeniedError("You do not have permission to view this organization.")

        org = await self._fetch_org_or_raise(org_id)

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

    async def update_organization(self, initiator: TokenData, org_id: str, data: OrganizationUpdateDTO) -> Organization:
        """Update an organization securely enforcing the 4-Tier RBAC Governance Matrix.

        Args:
            initiator: The token data of the user initiating the update.
            org_id: The ID of the organization to update.
            data: Validated OrganizationUpdateDTO payload.

        Returns:
            The updated organization model.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if RBAC or FinOps field rules are violated.
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the organization does not exist.
        """
        self._validate_organization_update_permissions(initiator=initiator, org_id=org_id, data=data)
        await self._fetch_org_or_raise(org_id)
        await self.org_repo.update(org_id, data)

        if self.audit_service is not None:
            await self.audit_service.log_event(
                actor_id=initiator.id,
                action="ORGANIZATION_UPDATED",
                organization_id=org_id,
                target_id=org_id,
                details=data.model_dump(mode="json", exclude_unset=True),
            )

        return await self._fetch_org_or_raise(org_id)

    def _validate_organization_update_permissions(
        self, initiator: TokenData, org_id: str, data: OrganizationUpdateDTO
    ) -> None:
        """Validate 4-Tier RBAC permissions and FinOps field locks for organization updates.

        Args:
            initiator: Authenticated caller token data.
            org_id: Target organization identifier.
            data: Validated OrganizationUpdateDTO payload.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if caller lacks privileges or mutates FinOps limits.
        """
        if initiator.role == UserRole.ROOT:
            return

        if initiator.role not in (UserRole.ADMIN, UserRole.MANAGER):
            logger.error(
                "[OrganizationService] %s: User %s (%s) denied update on organization %s.",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                initiator.role.value,
                org_id,
                exc_info=True,
            )
            raise PermissionDeniedError("Insufficient permissions to update organization.")

        if initiator.organization_id != org_id:
            logger.error(
                "[OrganizationService] %s: User %s attempted cross-tenant update on organization %s.",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                org_id,
                exc_info=True,
            )
            raise PermissionDeniedError("Cannot update foreign organization.")

        has_finops_mutation = any(
            field_val is not None
            for field_val in (
                data.quota_limit,
                data.tpm_limit,
                data.rpm_limit,
                data.tier,
                data.subscription_status,
                data.is_active,
                data.billing_id,
            )
        )
        if has_finops_mutation:
            logger.error(
                "[OrganizationService] %s: Non-ROOT user %s (%s) attempted to mutate FinOps limits on %s.",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                initiator.role.value,
                org_id,
                exc_info=True,
            )
            raise PermissionDeniedError("Only ROOT can modify platform FinOps limits or billing status.")

        if initiator.role == UserRole.MANAGER and data.allowed_email_domains is not None:
            logger.error(
                "[OrganizationService] %s: MANAGER %s attempted to mutate allowed_email_domains on %s.",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                org_id,
                exc_info=True,
            )
            raise PermissionDeniedError("Only ADMIN or ROOT can modify allowed email domains.")

    async def create_invitation(
        self,
        initiator: TokenData,
        org_id: str,
        payload: InvitationCreateDTO,
    ) -> InvitationResponseDTO:
        """Create a single cryptographic B2B organization invitation and dispatch email.

        Args:
            initiator: Authenticated caller token data (must be org ADMIN or ROOT).
            org_id: Target organization identifier (org_<hex32>).
            payload: Validated InvitationCreateDTO specifying recipient email and role.

        Returns:
            Redacted InvitationResponseDTO without exposing token_hash.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if caller lacks privileges,
                attempts to invite ROOT as non-ROOT, or email domain violates allowed_email_domains.
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if org_id does not exist.
            ConflictError: With ErrorCodes.CONFLICT_ERROR if a pending invitation already exists.
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if persistence or email transport is misconfigured.
        """
        self._verify_invitation_admin_access(initiator=initiator, org_id=org_id)
        org = await self._fetch_org_or_raise(org_id)
        now = datetime.now(UTC)
        existing_pending = await self._get_active_pending_emails(org_id=org_id, now=now)

        normalized_email = self._validate_invitation_recipient(
            initiator=initiator,
            org=org,
            payload=payload,
            existing_pending_emails=existing_pending,
        )

        persisted_list = await self._dispatch_and_persist_invitations(
            initiator=initiator,
            org=org,
            recipients={normalized_email: payload},
            now=now,
        )
        persisted = persisted_list[0]

        if self.audit_service is not None:
            await self.audit_service.log_event(
                actor_id=initiator.id,
                action="INVITATION_CREATED",
                organization_id=org_id,
                target_id=persisted.id,
                details={
                    "invitation_id": persisted.id,
                    "role": persisted.role.value,
                    "email_delivery_status": persisted.email_delivery_status.value,
                },
            )
        return self._to_invitation_response(persisted)

    async def create_invitation_batch(
        self,
        initiator: TokenData,
        org_id: str,
        payload: InvitationBatchCreateDTO,
    ) -> InvitationBatchResponseDTO:
        """Create a cohort batch of cryptographic B2B invitations after all-or-nothing preflight validation.

        Args:
            initiator: Authenticated caller token data (must be org ADMIN or ROOT).
            org_id: Target organization identifier (org_<hex32>).
            payload: Validated InvitationBatchCreateDTO containing 1 to 500 recipients.

        Returns:
            InvitationBatchResponseDTO with created count and materialized InvitationResponseDTOs.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if caller lacks privileges,
                attempts to invite ROOT as non-ROOT, or any recipient violates allowed_email_domains.
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if org_id does not exist.
            ConflictError: With ErrorCodes.CONFLICT_ERROR if any recipient already has a pending invitation.
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if persistence or email transport is misconfigured.
        """
        self._verify_invitation_admin_access(initiator=initiator, org_id=org_id)
        org = await self._fetch_org_or_raise(org_id)
        now = datetime.now(UTC)
        existing_pending = await self._get_active_pending_emails(org_id=org_id, now=now)

        deduplicated_by_email: dict[str, InvitationCreateDTO] = {}
        for recipient_dto in payload.recipients:
            normalized_email = self._validate_invitation_recipient(
                initiator=initiator,
                org=org,
                payload=recipient_dto,
                existing_pending_emails=existing_pending,
            )
            if normalized_email not in deduplicated_by_email:
                deduplicated_by_email[normalized_email] = recipient_dto

        persisted_invitations = await self._dispatch_and_persist_invitations(
            initiator=initiator,
            org=org,
            recipients=deduplicated_by_email,
            now=now,
        )
        persisted_dtos = [self._to_invitation_response(inv) for inv in persisted_invitations]
        sent_count = sum(1 for inv in persisted_invitations if inv.email_delivery_status == EmailDeliveryStatus.SENT)

        if self.audit_service is not None:
            await self.audit_service.log_event(
                actor_id=initiator.id,
                action="INVITATION_CREATED",
                organization_id=org_id,
                target_id=org_id,
                details={
                    "batch_size": len(persisted_dtos),
                    "sent_count": sent_count,
                },
            )
        return InvitationBatchResponseDTO(
            created_count=len(persisted_dtos),
            invitations=persisted_dtos,
        )

    async def list_invitations(
        self,
        initiator: TokenData,
        org_id: str,
    ) -> list[InvitationResponseDTO]:
        """List all organization invitations for the specified organization.

        Args:
            initiator: Authenticated caller token data (must be org ADMIN or ROOT).
            org_id: Target organization identifier (org_<hex32>).

        Returns:
            List of redacted InvitationResponseDTO records.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if caller lacks privileges.
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if org_id does not exist.
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if persistence is unconfigured.
        """
        self._verify_invitation_admin_access(initiator=initiator, org_id=org_id)
        await self._fetch_org_or_raise(org_id)
        records = await self._list_org_invitations(org_id)
        return [self._to_invitation_response(inv) for inv in records]

    async def revoke_invitation(
        self,
        initiator: TokenData,
        org_id: str,
        invitation_id: str,
    ) -> InvitationResponseDTO:
        """Revoke a pending organization invitation.

        Args:
            initiator: Authenticated caller token data (must be org ADMIN or ROOT).
            org_id: Owning organization identifier (org_<hex32>).
            invitation_id: Canonical Invitation ID (inv_<hex32>) to revoke.

        Returns:
            Updated InvitationResponseDTO with status='revoked'.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if caller lacks privileges.
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if invitation does not exist in org_id.
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if persistence is unconfigured.
        """
        self._verify_invitation_admin_access(initiator=initiator, org_id=org_id)
        await self._fetch_org_or_raise(org_id)
        existing = await self._get_invitation_by_id(invitation_id)
        if existing is None or existing.organization_id != org_id:
            logger.error(
                "[OrganizationService] %s: Invitation '%s' not found in organization '%s'.",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                invitation_id,
                org_id,
                exc_info=True,
            )
            raise ResourceNotFoundError(resource_type="invitation", resource_id=invitation_id)

        revoked = existing.model_copy(update={"status": InvitationStatus.REVOKED})
        await self._save_invitation(revoked)
        if self.audit_service is not None:
            await self.audit_service.log_event(
                actor_id=initiator.id,
                action="INVITATION_REVOKED",
                organization_id=org_id,
                target_id=revoked.id,
                details={"invitation_id": revoked.id},
            )
        return self._to_invitation_response(revoked)

    async def accept_invitation(
        self,
        initiator_or_payload: TokenData | InvitationAcceptRequestDTO,
        payload: InvitationAcceptRequestDTO | None = None,
    ) -> User:
        """Accept a B2B organization invitation enforcing the 1:1 Flat Identity Collision Guard.

        Args:
            initiator_or_payload: Authenticated caller TokenData or InvitationAcceptRequestDTO.
            payload: InvitationAcceptRequestDTO when initiator TokenData is provided as first argument.

        Returns:
            Updated or newly provisioned User assigned to the target organization.

        Raises:
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if token digest does not match any invitation.
            AppException: With ErrorCodes.INVITATION_EXPIRED if invitation is expired or revoked,
                or ErrorCodes.VALIDATION_FAILED if payload is missing.
            PermissionDeniedError: With ErrorCodes.IDENTITY_MISMATCH if caller email does not match invitation.
            ConflictError: With ErrorCodes.USER_ALREADY_ASSIGNED if user already belongs to another organization,
                or ErrorCodes.CONFLICT_ERROR if invitation was already accepted.
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if persistence is unconfigured.
        """
        initiator, accept_dto = self._unpack_accept_arguments(initiator_or_payload, payload)
        token_hash = hashlib.sha256(accept_dto.raw_token.encode("utf-8")).hexdigest()
        invitation = await self._find_invitation_by_token_hash(token_hash)
        if invitation is None:
            logger.error(
                "[OrganizationService] %s: Invitation token digest not found.",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                exc_info=True,
            )
            raise ResourceNotFoundError(resource_type="invitation", resource_id="token")

        now = datetime.now(UTC)
        await self._verify_invitation_acceptability(invitation=invitation, now=now)

        existing_user = await self._resolve_accepting_user(initiator=initiator, invitation=invitation)
        self._enforce_flat_identity_collision_guard(
            initiator=initiator,
            existing_user=existing_user,
            target_org_id=invitation.organization_id,
        )

        updated_user = await self._bind_user_to_invited_org(
            initiator=initiator,
            existing_user=existing_user,
            invitation=invitation,
            accept_dto=accept_dto,
            now=now,
        )

        accepted_inv = invitation.model_copy(update={"status": InvitationStatus.ACCEPTED})
        await self._save_invitation(accepted_inv)

        if self.audit_service is not None:
            await self.audit_service.log_event(
                actor_id=updated_user.id,
                action="INVITATION_ACCEPTED",
                organization_id=invitation.organization_id,
                target_id=invitation.id,
                details={
                    "invitation_id": invitation.id,
                    "user_id": updated_user.id,
                    "role": invitation.role.value,
                },
            )
        return updated_user

    def _verify_invitation_admin_access(self, *, initiator: TokenData, org_id: str) -> None:
        """Verify that the caller is ROOT or an ADMIN of the target organization.

        Args:
            initiator: Caller TokenData.
            org_id: Target organization ID.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if caller is not authorized.
        """
        if initiator.role == UserRole.ROOT:
            return
        if initiator.role == UserRole.ADMIN and initiator.organization_id == org_id:
            return
        logger.error(
            "[OrganizationService] %s: Caller '%s' (role=%s, org=%s) denied invitation management for org '%s'.",
            ErrorCodes.PERMISSION_DENIED.name,
            initiator.id,
            initiator.role.value,
            initiator.organization_id,
            org_id,
            exc_info=True,
        )
        raise PermissionDeniedError("Only organization ADMIN or ROOT can manage invitations.")

    async def _fetch_org_or_raise(self, org_id: str) -> Organization:
        """Fetch an Organization by ID or raise ResourceNotFoundError.

        Args:
            org_id: Target organization ID.

        Returns:
            Organization domain model.

        Raises:
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if organization is missing.
        """
        org = await self.org_repo.get_by_id(org_id)
        if org is None:
            logger.error(
                "[OrganizationService] %s: Organization not found (org_id=%s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                org_id,
                exc_info=True,
            )
            raise ResourceNotFoundError(resource_type="organization", resource_id=org_id)
        return org

    def _validate_invitation_recipient(
        self,
        *,
        initiator: TokenData,
        org: Organization,
        payload: InvitationCreateDTO,
        existing_pending_emails: set[str],
    ) -> str:
        """Validate role hierarchy, allowed_email_domains, and duplicate pending status for an invitation.

        Args:
            initiator: Caller TokenData.
            org: Target Organization model.
            payload: Recipient InvitationCreateDTO.
            existing_pending_emails: Lowercase emails with active PENDING invitations in the org.

        Returns:
            Normalized lowercase recipient email address.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED on role escalation or domain violation.
            ConflictError: With ErrorCodes.CONFLICT_ERROR if a pending invitation already exists.
        """
        if payload.role == UserRole.ROOT and initiator.role != UserRole.ROOT:
            logger.error(
                "[OrganizationService] %s: Non-ROOT caller '%s' attempted to invite ROOT role.",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                exc_info=True,
            )
            raise PermissionDeniedError("Non-ROOT administrators cannot invite users with ROOT role.")

        normalized_email = str(payload.email).strip().lower()
        email_domain = normalized_email.split("@")[-1].lower()
        if org.allowed_email_domains:
            allowed_domains = {d.strip().lower() for d in org.allowed_email_domains if d.strip()}
            if allowed_domains and email_domain not in allowed_domains:
                logger.error(
                    "[OrganizationService] %s: Email domain '%s' not in allowed_email_domains for org '%s'.",
                    ErrorCodes.PERMISSION_DENIED.name,
                    email_domain,
                    org.id,
                    exc_info=True,
                )
                raise PermissionDeniedError(
                    f"Recipient domain '{email_domain}' is not permitted for organization '{org.id}'."
                )

        if normalized_email in existing_pending_emails:
            logger.error(
                "[OrganizationService] %s: Duplicate pending invitation for org '%s'.",
                ErrorCodes.CONFLICT_ERROR.name,
                org.id,
                exc_info=True,
            )
            raise ConflictError(
                message="A pending invitation already exists for this email in the organization.",
                details={"error_code": ErrorCodes.CONFLICT_ERROR.value, "organization_id": org.id},
            )
        return normalized_email

    def _build_invitation(
        self,
        *,
        initiator: TokenData,
        org: Organization,
        normalized_email: str,
        role: UserRole,
        expires_in_hours: int,
        raw_token: str,
        now: datetime,
    ) -> Invitation:
        """Construct an Invitation domain model from validated parameters.

        Args:
            initiator: Caller TokenData.
            org: Target Organization model.
            normalized_email: Lowercase recipient email.
            role: Invited UserRole.
            expires_in_hours: Validity window in hours.
            raw_token: Newly generated 256-bit raw URL-safe token.
            now: Current UTC timestamp.

        Returns:
            Instantiated Invitation model with SHA-256 token_hash.
        """
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        inv_id = generate_opaque_id(EntityPrefix.INVITATION)
        expires_at = now + timedelta(hours=expires_in_hours)

        return Invitation(
            id=inv_id,
            organization_id=org.id,
            email=normalized_email,
            role=role,
            token_hash=token_hash,
            status=InvitationStatus.PENDING,
            email_delivery_status=EmailDeliveryStatus.PENDING,
            invited_by=initiator.id,
            expires_at=expires_at,
            created_at=now,
        )

    @staticmethod
    def _build_invitation_email(
        *,
        org: Organization,
        invitation: Invitation,
        raw_token: str,
    ) -> TransactionalEmailItemDTO:
        """Construct a TransactionalEmailItemDTO for an organization invitation.

        Args:
            org: Target Organization model.
            invitation: Persisted or draft Invitation model.
            raw_token: Raw URL-safe invitation token for the magic link.

        Returns:
            TransactionalEmailItemDTO with SecretStr-wrapped action_url.
        """
        base_url = get_settings().frontend_app_base_url.rstrip("/")
        action_url = f"{base_url}/invite/accept?token={raw_token}"
        subject = f"Invitation to join {org.name} on Quorum"
        html_body = (
            f"<p>You have been invited to join <strong>{org.name}</strong> "
            f"with role <strong>{invitation.role.value}</strong>.</p>"
        )
        return TransactionalEmailItemDTO(
            entity_id=invitation.id,
            recipient_email=invitation.email,
            locale=SystemLocale.EN,
            subject=subject,
            html_body=html_body,
            action_url=SecretStr(action_url),
        )

    async def _dispatch_and_persist_invitations(
        self,
        *,
        initiator: TokenData,
        org: Organization,
        recipients: Mapping[str, InvitationCreateDTO],
        now: datetime,
    ) -> list[Invitation]:
        """Materialize, email-dispatch, and persist validated B2B invitations.

        Args:
            initiator: Caller TokenData.
            org: Target Organization model.
            recipients: Ordered mapping of normalized lowercase email to InvitationCreateDTO.
            now: Current UTC timestamp.

        Returns:
            List of persisted Invitation domain models updated with email_delivery_status.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if persistence or email transport is misconfigured.
        """
        draft_invitations: list[Invitation] = []
        email_items: list[TransactionalEmailItemDTO] = []
        raw_tokens_by_id: dict[str, str] = {}
        for normalized_email, recipient_dto in recipients.items():
            raw_token = secrets.token_urlsafe(32)
            inv = self._build_invitation(
                initiator=initiator,
                org=org,
                normalized_email=normalized_email,
                role=recipient_dto.role,
                expires_in_hours=recipient_dto.expires_in_hours,
                raw_token=raw_token,
                now=now,
            )
            email_item = self._build_invitation_email(
                org=org,
                invitation=inv,
                raw_token=raw_token,
            )
            draft_invitations.append(inv)
            email_items.append(email_item)
            raw_tokens_by_id[inv.id] = raw_token

        batch_result = await self.email_service.send_invitation_emails(email_items)

        persisted_invitations: list[Invitation] = []
        for inv in draft_invitations:
            status_val = (
                batch_result.delivery_statuses[inv.id]
                if inv.id in batch_result.delivery_statuses
                else EmailDeliveryStatus.FAILED
            )
            final_inv = inv.model_copy(update={"email_delivery_status": status_val})
            await self._save_invitation(final_inv)
            self._last_generated_tokens[final_inv.id] = raw_tokens_by_id[final_inv.id]
            persisted_invitations.append(final_inv)
        return persisted_invitations

    @staticmethod
    def _unpack_accept_arguments(
        initiator_or_payload: TokenData | InvitationAcceptRequestDTO,
        payload: InvitationAcceptRequestDTO | None,
    ) -> tuple[TokenData | None, InvitationAcceptRequestDTO]:
        """Normalize arguments passed to accept_invitation.

        Args:
            initiator_or_payload: Either TokenData or InvitationAcceptRequestDTO.
            payload: Optional InvitationAcceptRequestDTO when first arg is TokenData.

        Returns:
            Tuple of (Optional TokenData, InvitationAcceptRequestDTO).

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if payload is missing.
        """
        if isinstance(initiator_or_payload, InvitationAcceptRequestDTO):
            return None, initiator_or_payload
        if payload is None:
            msg = "InvitationAcceptRequestDTO payload is required."
            logger.error(
                "[OrganizationService] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        return initiator_or_payload, payload

    async def _verify_invitation_acceptability(
        self,
        *,
        invitation: Invitation,
        now: datetime,
    ) -> None:
        """Verify that an invitation is PENDING and not expired.

        Args:
            invitation: Target Invitation model.
            now: Current UTC timestamp.

        Raises:
            AppException: With ErrorCodes.INVITATION_EXPIRED if expired or revoked.
            ConflictError: With ErrorCodes.CONFLICT_ERROR if already accepted.
        """
        if invitation.status == InvitationStatus.ACCEPTED:
            logger.error(
                "[OrganizationService] %s: Invitation '%s' was already accepted.",
                ErrorCodes.CONFLICT_ERROR.name,
                invitation.id,
                exc_info=True,
            )
            raise ConflictError(
                message="Invitation has already been accepted.",
                details={"error_code": ErrorCodes.CONFLICT_ERROR.value, "invitation_id": invitation.id},
            )

        if invitation.status in (InvitationStatus.EXPIRED, InvitationStatus.REVOKED) or invitation.expires_at <= now:
            if invitation.status == InvitationStatus.PENDING and invitation.expires_at <= now:
                await self._save_invitation(invitation.model_copy(update={"status": InvitationStatus.EXPIRED}))
            logger.error(
                "[OrganizationService] %s: Invitation '%s' is expired or revoked (status=%s).",
                ErrorCodes.INVITATION_EXPIRED.name,
                invitation.id,
                invitation.status.value,
                exc_info=True,
            )
            raise AppException(
                message="Invitation has expired or been revoked.",
                status_code=410,
                details={"error_code": ErrorCodes.INVITATION_EXPIRED.value, "invitation_id": invitation.id},
            )

    @staticmethod
    def _verify_email_matches_invitation(
        *,
        candidate_email: str,
        subject_id: str,
        invitation: Invitation,
    ) -> None:
        """Verify case-insensitive identity parity between authenticated email and invitation email.

        Args:
            candidate_email: Email address from caller TokenData or persisted User record.
            subject_id: Canonical user identifier for structured error logging.
            invitation: Target Invitation model.

        Raises:
            PermissionDeniedError: With ErrorCodes.IDENTITY_MISMATCH if candidate_email mismatches invitation.email.
        """
        if candidate_email.lower() != invitation.email.lower():
            logger.error(
                "[OrganizationService] %s: Caller '%s' email mismatch for invitation '%s'.",
                ErrorCodes.IDENTITY_MISMATCH.name,
                subject_id,
                invitation.id,
                exc_info=True,
            )
            raise PermissionDeniedError(
                message="Authenticated user email does not match invitation recipient.",
                details={"error_code": ErrorCodes.IDENTITY_MISMATCH.value, "invitation_id": invitation.id},
            )

    async def _resolve_accepting_user(
        self,
        *,
        initiator: TokenData | None,
        invitation: Invitation,
    ) -> User | None:
        """Resolve the existing User record for an invitation acceptance and verify email identity.

        Args:
            initiator: Optional caller TokenData.
            invitation: Target Invitation model.

        Returns:
            Matching User record if already persisted, else None.

        Raises:
            PermissionDeniedError: With ErrorCodes.IDENTITY_MISMATCH if caller email mismatches invitation.
        """
        if initiator is not None:
            if initiator.email is not None:
                self._verify_email_matches_invitation(
                    candidate_email=initiator.email,
                    subject_id=initiator.id,
                    invitation=invitation,
                )
            by_id = await self.user_repo.get_by_id(initiator.id)
            if by_id is not None:
                self._verify_email_matches_invitation(
                    candidate_email=by_id.email,
                    subject_id=by_id.id,
                    invitation=invitation,
                )
                return by_id

        return await self.user_repo.get_by_email(invitation.email)

    @staticmethod
    def _enforce_flat_identity_collision_guard(
        *,
        initiator: TokenData | None,
        existing_user: User | None,
        target_org_id: str,
    ) -> None:
        """Enforce the 1:1 Flat Identity Collision Guard preventing cross-tenant account hijacking.

        Args:
            initiator: Optional caller TokenData.
            existing_user: Existing persisted User if found.
            target_org_id: Organization ID on the invitation.

        Raises:
            ConflictError: With ErrorCodes.USER_ALREADY_ASSIGNED if user belongs to another organization.
        """
        current_org_id: str | None = None
        subject_id: str = "unknown"
        if existing_user is not None:
            current_org_id = existing_user.organization_id
            subject_id = existing_user.id
        elif initiator is not None:
            current_org_id = initiator.organization_id
            subject_id = initiator.id

        if current_org_id is not None and current_org_id != target_org_id:
            logger.error(
                "[OrganizationService] %s: User '%s' already belongs to organization '%s' (invited to '%s').",
                ErrorCodes.USER_ALREADY_ASSIGNED.name,
                subject_id,
                current_org_id,
                target_org_id,
                exc_info=True,
            )
            raise ConflictError(
                message=f"User '{subject_id}' is already assigned to organization '{current_org_id}'.",
                details={
                    "error_code": ErrorCodes.USER_ALREADY_ASSIGNED.value,
                    "user_id": subject_id,
                    "current_organization_id": current_org_id,
                    "target_organization_id": target_org_id,
                },
            )

    async def _bind_user_to_invited_org(
        self,
        *,
        initiator: TokenData | None,
        existing_user: User | None,
        invitation: Invitation,
        accept_dto: InvitationAcceptRequestDTO,
        now: datetime,
    ) -> User:
        """Update an existing unassigned/same-org user or provision a new user for the invitation.

        Args:
            initiator: Optional caller TokenData.
            existing_user: Optional existing User record.
            invitation: Accepted Invitation model.
            accept_dto: InvitationAcceptRequestDTO payload.
            now: Current UTC timestamp.

        Returns:
            Persisted User model bound to invitation.organization_id and invitation.role.
        """
        if existing_user is not None:
            updated_name = accept_dto.name if accept_dto.name is not None else existing_user.name
            persisted = await self.user_repo.update(
                existing_user.id,
                UserUpdate(
                    organization_id=invitation.organization_id,
                    role=invitation.role,
                    name=updated_name,
                    is_active=True,
                ),
            )
            updated_user = (
                persisted
                if persisted is not None
                else existing_user.model_copy(
                    update={
                        "organization_id": invitation.organization_id,
                        "role": invitation.role,
                        "name": updated_name,
                        "is_active": True,
                    }
                )
            )
            if self._entity_adapter is not None:
                await self._entity_adapter.upsert_user(updated_user)
            return updated_user

        user_id = initiator.id if initiator is not None else generate_opaque_id(EntityPrefix.USER)
        display_name = accept_dto.name if accept_dto.name is not None else invitation.email.split("@")[0]
        new_user = User(
            id=user_id,
            email=invitation.email,
            name=display_name,
            role=invitation.role,
            organization_id=invitation.organization_id,
            is_active=True,
            created_at=now,
            language=SystemLocale.EN,
            theme_mode="system",
        )
        await self.user_repo.create(new_user)
        if self._entity_adapter is not None:
            await self._entity_adapter.upsert_user(new_user)
        return new_user

    async def _save_invitation(self, invitation: Invitation) -> None:
        """Persist an Invitation to the entity adapter or UnitOfWork.

        Args:
            invitation: Validated Invitation model to store.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
        """
        # Route invitation persistence exclusively through _acquire_entity_port
        async with self._acquire_entity_port(commit=True) as entities:
            await entities.upsert_invitation(invitation)

    async def _get_invitation_by_id(self, invitation_id: str) -> Invitation | None:
        """Fetch an Invitation by its canonical ID.

        Args:
            invitation_id: Canonical Invitation ID (inv_<hex32>).

        Returns:
            Invitation model if found, else None.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
        """
        async with self._acquire_entity_port() as entities:
            return await entities.get_invitation(invitation_id)

    async def _list_org_invitations(self, org_id: str) -> list[Invitation]:
        """List all invitations belonging to a specific organization.

        Args:
            org_id: Owning organization ID (org_<hex32>).

        Returns:
            List of Invitation models for the organization.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
        """
        async with self._acquire_entity_port() as entities:
            persisted = await entities.list_invitations(organization_id=org_id)
        return [item for item in persisted if item.organization_id == org_id]

    async def _get_active_pending_emails(self, *, org_id: str, now: datetime) -> set[str]:
        """Return lowercase email addresses that currently have an unexpired PENDING invitation in org_id.

        Args:
            org_id: Owning organization ID.
            now: Current UTC timestamp.

        Returns:
            Set of lowercase email strings.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
        """
        invitations = await self._list_org_invitations(org_id)
        return {
            inv.email.lower() for inv in invitations if inv.status == InvitationStatus.PENDING and inv.expires_at > now
        }

    async def _find_invitation_by_token_hash(self, token_hash: str) -> Invitation | None:
        """Locate an Invitation matching the given SHA-256 token digest using constant-time comparison.

        Args:
            token_hash: 64-character hex SHA-256 digest of the raw invitation token.

        Returns:
            Matching Invitation model if found, else None.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
        """
        async with self._acquire_entity_port() as entities:
            persisted = await entities.list_invitations()
        for item in persisted:
            if secrets.compare_digest(item.token_hash, token_hash):
                return item
        return None

    @staticmethod
    def _to_invitation_response(invitation: Invitation) -> InvitationResponseDTO:
        """Project an Invitation model into a redacted InvitationResponseDTO.

        Args:
            invitation: Persisted Invitation domain model.

        Returns:
            InvitationResponseDTO excluding token_hash.
        """
        return InvitationResponseDTO(
            id=invitation.id,
            organization_id=invitation.organization_id,
            email=invitation.email,
            role=invitation.role,
            status=invitation.status,
            email_delivery_status=invitation.email_delivery_status,
            invited_by=invitation.invited_by,
            expires_at=invitation.expires_at,
            created_at=invitation.created_at,
        )
