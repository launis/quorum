"""Database repository implementation module for Users and Organizations."""

from __future__ import annotations

import logging

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.base import BaseRepository
from backend_v2.exceptions import ErrorCodes
from backend_v2.models.auth import (
    Organization,
    OrganizationCreate,
    OrganizationUpdateDTO,
    SystemOrganizations,
    User,
    UserCreate,
    UserUpdate,
)

logger = logging.getLogger(__name__)


class IdentityRepositoryImpl(BaseRepository):
    """Repository implementation for Users and Organizations."""

    async def list_organizations(self) -> list[Organization]:
        """Retrieves all organizations.

        Returns:
            List of validated Organization domain models.
        """
        raw_orgs = await self.driver.query("organizations")
        orgs: list[Organization] = []
        for o in raw_orgs:
            try:
                orgs.append(Organization.model_validate(o, strict=False))
            except Exception as e:
                item_id = o["id"] if "id" in o else "unknown"
                logger.error(
                    "[IdentityRepository] %s: Skipping corrupted organization %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    item_id,
                    e,
                    exc_info=True,
                )
        return orgs

    async def get_organization(self, org_id: str) -> Organization | None:
        """Retrieves an organization by its ID.

        Args:
            org_id: Unique identifier for the organization.

        Returns:
            The validated Organization domain model if found, otherwise None.
        """
        data = await self.driver.get("organizations", org_id)
        if not data:
            return None
        return Organization.model_validate(data, strict=False)

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
        payload = org_data.model_dump(mode="json")
        doc_id = payload["id"] if "id" in payload else f"org_{payload['name'].lower()}"
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
        """
        filters = []
        if org_id:
            filters.append(Filter("organization_id", "==", org_id))
        raw_users = await self.driver.query("users", filters)
        users: list[User] = []
        for u in raw_users:
            try:
                users.append(User.model_validate(u, strict=False))
            except Exception as e:
                item_id = u["id"] if "id" in u else "unknown"
                logger.error(
                    "[IdentityRepository] %s: Skipping corrupted user %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    item_id,
                    e,
                    exc_info=True,
                )
        return users

    async def get_user(self, user_id: str) -> User | None:
        """Retrieves a user by ID.

        Args:
            user_id: Unique identifier for the user.

        Returns:
            The validated User domain model if found, otherwise None.
        """
        data = await self.driver.get("users", user_id)
        if not data:
            return None
        return User.model_validate(data, strict=False)

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
        payload = user_data.model_dump(mode="json")
        doc_id = payload["id"]
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
