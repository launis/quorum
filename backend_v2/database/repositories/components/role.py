"""Extracted Repository for Roles."""

import logging
from typing import Any

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.v2_core import Role

logger = logging.getLogger(__name__)


class RoleRepositoryImpl(AppendOnlyRepositoryBase):
    """Repository implementation for Roles."""

    async def get_all_roles(self) -> list[Role]:
        """Retrieves all roles from the database.

        Returns:
            List of validated Role domain models.
        """
        filters = [Filter("type", "==", "role")]
        raw = await self.driver.query("components", filters)
        roles: list[Role] = []
        for r in raw:
            try:
                roles.append(Role.model_validate(r, strict=False))
            except Exception as e:
                item_id = r["id"] if "id" in r else "unknown"
                logger.error("Failed to parse Role %s: %s", item_id, e, exc_info=True)
                raise AppException(
                    message=f"Failed to parse role {item_id} from database",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e
        return roles

    async def get_role_by_id(self, role_id: str) -> Role | None:
        """Retrieves a role by its ID.

        Args:
            role_id: Unique identifier for the role.

        Returns:
            The validated Role domain model if found, otherwise None.
        """
        doc = await self.driver.get("components", role_id)
        if not doc:
            return None
        try:
            return Role.model_validate(doc, strict=False)
        except Exception as e:
            logger.error("Failed to parse Role %s: %s", role_id, e, exc_info=True)
            raise AppException(
                message=f"Failed to parse role {role_id} from database",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

    async def create_role(self, role_data: dict[str, Any]) -> str:
        """Creates a new role.

        Args:
            role_data: Dictionary containing role fields.

        Returns:
            The created role ID.
        """
        doc_id = role_data["id"]
        role_data["type"] = "role"
        return await self.driver.upsert("components", role_data, doc_id)

    async def update_role(self, role_id: str, updates: dict[str, Any]) -> str:
        """Updates an existing role.

        Args:
            role_id: Unique identifier for the role.
            updates: Dictionary of fields to update.

        Returns:
            The updated role ID.

        Raises:
            ResourceNotFoundError: If the role does not exist.
        """
        doc = await self.driver.get("components", role_id)
        if not doc:
            raise ResourceNotFoundError(resource_type="Role", resource_id=role_id)
        await self.driver.update("components", role_id, updates)
        return role_id

    async def delete_role(self, role_id: str) -> bool:
        """Deletes a role by ID.

        Args:
            role_id: Unique identifier for the role.

        Returns:
            True if deleted, False if role does not exist.
        """
        doc = await self.driver.get("components", role_id)
        if not doc:
            return False
        return await self.driver.delete("components", role_id)
