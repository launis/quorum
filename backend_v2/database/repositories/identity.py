"""Database repository implementation module for Users and Organizations."""

from __future__ import annotations

import logging

from backend_v2.database.driver import Filter, StorageDriver
from backend_v2.database.interfaces import EntityPersistencePort
from backend_v2.database.repositories.base import BaseRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import (
    Organization,
    OrganizationCreate,
    OrganizationUpdateDTO,
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
    """Repository implementation for Users and Organizations."""

    def __init__(
        self,
        driver: StorageDriver,
        entity_adapter: EntityPersistencePort | None = None,
    ) -> None:
        """Initializes the identity repository with a storage driver and optional entity persistence port.

        Args:
            driver: Underlying storage driver instance.
            entity_adapter: Optional typed PostgreSQL entity persistence port.
        """
        super().__init__(driver)
        self._entity_adapter: EntityPersistencePort | None = entity_adapter

    async def list_organizations(self) -> list[Organization]:
        """Retrieves all organizations.

        Returns:
            List of validated Organization domain models.

        Raises:
            AppException: If an organization record fails validation (ErrorCodes.VALIDATION_FAILED).
        """
        if self._entity_adapter is not None:
            return list(await self._entity_adapter.list_organizations())

        raw_orgs = await self.driver.query("organizations")
        orgs: list[Organization] = []
        for o in raw_orgs:
            try:
                orgs.append(Organization.model_validate(o, strict=False))
            except Exception as e:
                item_id = "unknown"
                if "id" in o:
                    item_id = str(o["id"])
                logger.error(
                    "[IdentityRepository] %s: Corrupted organization %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    item_id,
                    e,
                    exc_info=True,
                )
                raise AppException(
                    message=f"Corrupted organization {item_id}: {e}",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "item_id": item_id},
                ) from e
        return orgs

    async def get_organization(self, org_id: str) -> Organization | None:
        """Retrieves an organization by its ID.

        Args:
            org_id: Unique identifier for the organization.

        Returns:
            The validated Organization domain model if found, otherwise None.
        """
        if self._entity_adapter is not None:
            return await self._entity_adapter.get_organization(org_id)

        # Phase 1, Step 1: Use O(1) primary-key lookup instead of full-table scan
        raw_org = await self.driver.get("organizations", org_id)
        if raw_org is None:
            return None
        return Organization.model_validate(raw_org, strict=False)

    async def get_organization_model(self, org_id: str) -> Organization | None:
        """Retrieves an organization model by its ID.

        Args:
            org_id: Unique identifier for the organization.

        Returns:
            The validated Organization domain model if found, otherwise None.
        """
        return await self.get_organization(org_id)

    async def create_organization(self, org_data: OrganizationCreate | Organization) -> str:
        """Creates a new organization.

        Args:
            org_data: Organization domain model or creation DTO.

        Returns:
            The created organization ID.
        """
        if self._entity_adapter is not None and isinstance(org_data, Organization):
            return await self._entity_adapter.upsert_organization(org_data)

        payload = org_data.model_dump(mode="json")
        doc_id = str(payload["id"]) if "id" in payload else generate_opaque_id(EntityPrefix.ORG)
        payload["id"] = doc_id
        return await self.driver.upsert("organizations", payload, doc_id)

    async def update_organization(self, org_id: str, updates: OrganizationUpdateDTO) -> bool:
        """Updates an existing organization.

        Args:
            org_id: Unique identifier for the organization.
            updates: OrganizationUpdateDTO containing update fields.

        Returns:
            True if updated successfully, False otherwise.
        """
        payload = updates.model_dump(mode="json", exclude_unset=True)
        if not payload:
            return True
        return await self.driver.update("organizations", org_id, payload)

    async def delete_organization(self, org_id: str) -> bool:
        """Deletes an organization by ID.

        Args:
            org_id: Unique identifier for the organization.

        Returns:
            True if deleted successfully, False otherwise.
        """
        return await self.driver.delete("organizations", org_id)

    async def list_users(self, org_id: str | None = None) -> list[User]:
        """Retrieves all users matching an optional organization filter.

        Args:
            org_id: Optional organization ID filter.

        Returns:
            List of validated User domain models.

        Raises:
            AppException: If a user record fails validation (ErrorCodes.VALIDATION_FAILED).
        """
        if self._entity_adapter is not None:
            return list(await self._entity_adapter.list_users(org_id))

        filters = []
        if org_id:
            filters.append(Filter("organization_id", "==", org_id))
        raw_users = await self.driver.query("users", filters)
        users: list[User] = []
        for u in raw_users:
            try:
                users.append(User.model_validate(u, strict=False))
            except Exception as e:
                item_id = "unknown"
                if "id" in u:
                    item_id = str(u["id"])
                logger.error(
                    "[IdentityRepository] %s: Corrupted user %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    item_id,
                    e,
                    exc_info=True,
                )
                raise AppException(
                    message=f"Corrupted user {item_id}: {e}",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "item_id": item_id},
                ) from e
        return users

    async def get_user(self, user_id: str) -> User | None:
        """Retrieves a user by ID.

        Args:
            user_id: Unique identifier for the user.

        Returns:
            The validated User domain model if found, otherwise None.
        """
        if self._entity_adapter is not None:
            return await self._entity_adapter.get_user(user_id)

        # Phase 1, Step 1: Use O(1) primary-key lookup instead of full-table scan
        raw_user = await self.driver.get("users", user_id)
        if raw_user is None:
            return None
        return User.model_validate(raw_user, strict=False)

    async def get_user_by_email(self, email: str) -> User | None:
        """Retrieves a user by email address.

        Args:
            email: Email address of the user.

        Returns:
            The validated User domain model if found, otherwise None.
        """
        res = await self.driver.query("users", [Filter("email", "==", email)], limit=1)
        if not res:
            return None
        return User.model_validate(res[0], strict=False)

    async def create_user(self, user_data: UserCreate | User) -> str:
        """Creates a new user.

        Args:
            user_data: User domain model or creation DTO.

        Returns:
            The created user ID.
        """
        if self._entity_adapter is not None and isinstance(user_data, User):
            return await self._entity_adapter.upsert_user(user_data)

        payload = user_data.model_dump(mode="json")
        doc_id = str(payload["id"]) if "id" in payload else generate_opaque_id(EntityPrefix.USER)
        payload["id"] = doc_id
        return await self.driver.upsert("users", payload, doc_id)

    async def update_user(self, user_id: str, updates: UserUpdate) -> bool:
        """Updates an existing user.

        Args:
            user_id: Unique identifier for the user.
            updates: UserUpdate DTO containing update fields.

        Returns:
            True if updated successfully, False otherwise.
        """
        payload = updates.model_dump(mode="json", exclude_unset=True)
        if not payload:
            return True
        return await self.driver.update("users", user_id, payload)

    async def delete_user(self, user_id: str) -> bool:
        """Deletes a user by ID.

        Args:
            user_id: Unique identifier for the user.

        Returns:
            True if deleted successfully, False otherwise.
        """
        return await self.driver.delete("users", user_id)

    async def delete_org_data(self, org_id: str) -> None:
        """Cascades deletion of organization data including users, executions, and custom workflows.

        Args:
            org_id: Unique identifier for the organization to purge.
        """
        users = await self.list_users(org_id)
        for u in users:
            await self.driver.delete("users", u.id)

        execs = await self.driver.query("executions", [Filter("organization_id", "==", org_id)])
        for e in execs:
            if "id" in e and e["id"]:
                await self.driver.delete("executions", e["id"])

        wfs = await self.driver.query(
            "workflows", [Filter("organization_id", "in", [org_id, SystemOrganizations.ROOT_SYSTEM])]
        )
        for w in wfs:
            if "organization_id" in w and w["organization_id"] == org_id:
                if "id" in w and w["id"]:
                    await self.driver.delete("workflows", w["id"])

    async def get_org_usage_total(self, org_id: str, since: str | None = None) -> float:
        """Calculates total usage cost for an organization.

        Args:
            org_id: Unique identifier for the organization.
            since: Optional ISO timestamp filter.

        Returns:
            The total cost estimate in USD.
        """
        filters = [Filter("organization_id", "==", org_id)]
        if since:
            filters.append(Filter("completed_at", ">=", since))

        execs = await self.driver.query("executions", filters)
        total = 0.0
        for e in execs:
            if "cost_estimate" in e and e["cost_estimate"] is not None:
                total += float(e["cost_estimate"])
        return total
