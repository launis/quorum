"""Database repository implementation module for Users and Organizations."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from backend_v2.database.interfaces import EntityPersistencePort, UnitOfWorkFactory
from backend_v2.database.repositories.base import BaseRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import (
    Organization,
    OrganizationCreate,
    OrganizationUpdateDTO,
    SubscriptionStatus,
    SystemOrganizations,
    User,
    UserCreate,
    UserUpdate,
)
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.enums import EntityPrefix

logger = logging.getLogger(__name__)

__all__ = ["IdentityRepositoryImpl"]


class IdentityRepositoryImpl(BaseRepository):
    """Repository implementation for Users and Organizations backed by EntityPersistencePort."""

    def __init__(
        self,
        uow_factory: UnitOfWorkFactory | None = None,
        *,
        entity_adapter: EntityPersistencePort | None = None,
    ) -> None:
        """Initialize the identity repository with an optional UnitOfWorkFactory or direct EntityPersistencePort.

        Args:
            uow_factory: Optional zero-argument callable returning a QuorumUnitOfWork.
            entity_adapter: Optional pre-bound EntityPersistencePort inside an active UoW transaction.
        """
        super().__init__(uow_factory)
        self._entity_adapter: EntityPersistencePort | None = entity_adapter

    @asynccontextmanager
    async def _acquire_entities(self) -> AsyncIterator[EntityPersistencePort]:
        """Yield the injected EntityPersistencePort if bound, else open/reuse a QuorumUnitOfWork session."""
        if self._entity_adapter is not None:
            yield self._entity_adapter
            return
        async with super()._acquire_entities() as entities:
            yield entities

    async def list_organizations(self) -> list[Organization]:
        """Retrieve all persisted organizations.

        Returns:
            List of validated Organization domain models.
        """
        async with self._acquire_entities() as entities:
            return list(await entities.list_organizations())

    async def get_organization(self, org_id: str) -> Organization | None:
        """Retrieve an organization by primary key ID in O(1) indexed time.

        Args:
            org_id: Canonical org_<hex32> organization identifier.

        Returns:
            Validated Organization domain model if found, otherwise None.
        """
        async with self._acquire_entities() as entities:
            return await entities.get_organization(org_id)

    async def get_organization_model(self, org_id: str) -> Organization | None:
        """Retrieve an organization model by ID.

        Args:
            org_id: Canonical org_<hex32> organization identifier.

        Returns:
            Validated Organization domain model if found, otherwise None.
        """
        return await self.get_organization(org_id)

    async def create_organization(self, org_data: OrganizationCreate | Organization) -> str:
        """Create or upsert an organization record.

        Args:
            org_data: Organization domain model or OrganizationCreate DTO.

        Returns:
            Created canonical org_<hex32> identifier.
        """
        if isinstance(org_data, Organization):
            org_model = org_data
        else:
            org_model = Organization(
                id=generate_opaque_id(EntityPrefix.ORG),
                name=org_data.name,
                created_at=datetime.now(UTC),
                is_active=True,
                tier="standard",
                contact_email=str(org_data.admin_email),
                subscription_status=SubscriptionStatus.ACTIVE,
                quota_limit=100.0,
                tpm_limit=org_data.tpm_limit,
                rpm_limit=org_data.rpm_limit,
                allowed_email_domains=[],
            )
        async with self._acquire_entities() as entities:
            return await entities.upsert_organization(org_model)

    async def update_organization(self, org_id: str, updates: OrganizationUpdateDTO) -> bool:
        """Update an existing organization record in-place.

        Args:
            org_id: Canonical org_<hex32> organization identifier.
            updates: OrganizationUpdateDTO containing partial update fields.

        Returns:
            True if updated, False if the organization does not exist.
        """
        fields_set = updates.model_fields_set
        async with self._acquire_entities() as entities:
            existing = await entities.get_organization(org_id)
            if existing is None:
                return False
            if not fields_set:
                return True

            next_name = existing.name
            if updates.name is not None:
                next_name = updates.name
            next_tier = existing.tier
            if updates.tier is not None:
                next_tier = updates.tier
            next_active = existing.is_active
            if updates.is_active is not None:
                next_active = updates.is_active
            next_contact = existing.contact_email
            if "contact_email" in fields_set:
                next_contact = updates.contact_email
            next_billing = existing.billing_id
            if "billing_id" in fields_set:
                next_billing = updates.billing_id
            next_sub = existing.subscription_status
            if updates.subscription_status is not None:
                next_sub = updates.subscription_status
            next_quota = existing.quota_limit
            if updates.quota_limit is not None:
                next_quota = updates.quota_limit
            next_tpm = existing.tpm_limit
            if updates.tpm_limit is not None:
                next_tpm = updates.tpm_limit
            next_rpm = existing.rpm_limit
            if updates.rpm_limit is not None:
                next_rpm = updates.rpm_limit
            next_domains = existing.allowed_email_domains
            if updates.allowed_email_domains is not None:
                next_domains = updates.allowed_email_domains

            updated = Organization(
                id=existing.id,
                slug=existing.slug,
                name=next_name,
                created_at=existing.created_at,
                is_active=next_active,
                tier=next_tier,
                contact_email=next_contact,
                billing_id=next_billing,
                subscription_status=next_sub,
                quota_limit=next_quota,
                tpm_limit=next_tpm,
                rpm_limit=next_rpm,
                allowed_email_domains=next_domains,
            )
            await entities.upsert_organization(updated)
            return True

    async def delete_organization(self, org_id: str) -> bool:
        """Delete an organization by primary key ID.

        Args:
            org_id: Canonical org_<hex32> organization identifier.

        Returns:
            True if deleted, False if not found.
        """
        async with self._acquire_entities() as entities:
            return await entities.delete_organization(org_id)

    async def list_users(self, org_id: str | None = None) -> list[User]:
        """Retrieve all users matching an optional organization filter.

        Args:
            org_id: Optional canonical org_<hex32> organization filter.

        Returns:
            List of validated User domain models.
        """
        async with self._acquire_entities() as entities:
            return list(await entities.list_users(org_id))

    async def get_user(self, user_id: str) -> User | None:
        """Retrieve a user by primary key ID in O(1) indexed time.

        Args:
            user_id: Canonical usr_<hex32> user identifier.

        Returns:
            Validated User domain model if found, otherwise None.
        """
        async with self._acquire_entities() as entities:
            return await entities.get_user(user_id)

    async def get_user_by_email(self, email: str) -> User | None:
        """Retrieve a user by case-insensitive email address.

        Args:
            email: Email address of the user.

        Returns:
            Validated User domain model if found, otherwise None.
        """
        async with self._acquire_entities() as entities:
            return await entities.get_user_by_email(email)

    async def create_user(self, user_data: UserCreate | User) -> str:
        """Create or upsert a user record.

        Args:
            user_data: User domain model or UserCreate DTO.

        Returns:
            Created canonical usr_<hex32> identifier.
        """
        if isinstance(user_data, User):
            user_model = user_data
        else:
            user_model = User(
                id=generate_opaque_id(EntityPrefix.USER),
                email=user_data.email,
                name=user_data.name,
                role=user_data.role,
                organization_id=user_data.organization_id,
                is_active=user_data.is_active,
                language=user_data.language,
                theme_mode=user_data.theme_mode,
                created_at=datetime.now(UTC),
                created_by=user_data.created_by,
            )
        async with self._acquire_entities() as entities:
            return await entities.upsert_user(user_model)

    async def update_user(self, user_id: str, updates: UserUpdate) -> bool:
        """Update an existing user record in-place.

        Args:
            user_id: Canonical usr_<hex32> user identifier.
            updates: UserUpdate DTO containing partial update fields.

        Returns:
            True if updated, False if the user does not exist.
        """
        fields_set = updates.model_fields_set
        persisted_fields = fields_set - {"password"}
        async with self._acquire_entities() as entities:
            existing = await entities.get_user(user_id)
            if existing is None:
                return False
            if not persisted_fields:
                return True

            next_name = existing.name
            if "name" in persisted_fields:
                next_name = updates.name
            next_role = existing.role
            if updates.role is not None:
                next_role = updates.role
            next_active = existing.is_active
            if updates.is_active is not None:
                next_active = updates.is_active
            next_lang = existing.language
            if updates.language is not None:
                next_lang = updates.language
            next_theme = existing.theme_mode
            if updates.theme_mode is not None:
                next_theme = updates.theme_mode
            next_org = existing.organization_id
            if "organization_id" in persisted_fields:
                next_org = updates.organization_id

            updated = User(
                id=existing.id,
                slug=existing.slug,
                email=existing.email,
                name=next_name,
                role=next_role,
                organization_id=next_org,
                is_active=next_active,
                language=next_lang,
                theme_mode=next_theme,
                created_at=existing.created_at,
                created_by=existing.created_by,
                firebase_uid=existing.firebase_uid,
                deleted_at=existing.deleted_at,
            )
            await entities.upsert_user(updated)
            return True

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user by primary key ID.

        Args:
            user_id: Canonical usr_<hex32> user identifier.

        Returns:
            True if deleted, False if not found.
        """
        async with self._acquire_entities() as entities:
            return await entities.delete_user(user_id)

    async def delete_org_data(self, org_id: str) -> None:
        """Atomically purge an organization and its cascade-owned tenant records inside one UoW transaction.

        Args:
            org_id: Canonical org_<hex32> organization identifier to purge.

        Raises:
            AppException: With PERMISSION_DENIED (HTTP 403) if org_id belongs to the protected system scope.
        """
        if SystemOrganizations.is_system(org_id):
            msg = f"Cannot purge protected system organization '{org_id}'."
            logger.error(
                "[IdentityRepository] %s: %s",
                ErrorCodes.PERMISSION_DENIED.name,
                msg,
                extra={"error_code": ErrorCodes.PERMISSION_DENIED.value, "organization_id": org_id},
            )
            raise AppException(
                message=msg,
                status_code=403,
                details={"error_code": ErrorCodes.PERMISSION_DENIED.value, "organization_id": org_id},
            )
        async with self._acquire_entities() as entities:
            await entities.delete_organization(org_id)

    async def get_org_usage_total(self, org_id: str, since: str | None = None) -> float:
        """Calculate total FinOps USD cost for an organization from append-only usage_records.

        Args:
            org_id: Canonical org_<hex32> organization identifier.
            since: Optional ISO 8601 UTC lower-bound timestamp filter.

        Returns:
            Total aggregated USD cost for the organization.

        Raises:
            AppException: With VALIDATION_FAILED (HTTP 400) if since is malformed.
        """
        since_dt: datetime | None = None
        if since:
            try:
                parsed = datetime.fromisoformat(since.replace("Z", "+00:00"))
            except ValueError as exc:
                msg = f"Invalid date format '{since}': {exc}"
                logger.error(
                    "[IdentityRepository] %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    msg,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "since": since},
                )
                raise AppException(
                    message=msg,
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "since": since},
                ) from exc
            since_dt = parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)

        async with self._acquire_entities() as entities:
            rollup = await entities.aggregate_organization_usage(organization_id=org_id, since=since_dt)
            return float(rollup.total_cost_usd)
