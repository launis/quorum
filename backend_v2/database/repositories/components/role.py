import logging
from typing import Any

from backend_v2.database.driver import Filter
from backend_v2.database.interfaces import IRoleRepository
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase
from backend_v2.exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)


class RoleRepositoryImpl(AppendOnlyRepositoryBase, IRoleRepository):
    """Repository implementation for Roles."""

    async def get_all_roles(self) -> list[dict[str, Any]]:
        """Repository method implementation."""
        filters = [Filter("type", "==", "role")]
        return await self.driver.query("components", filters)

    async def get_role_by_id(self, role_id: str) -> dict[str, Any] | None:
        """Repository method implementation."""
        return await self.driver.get("components", role_id)

    async def create_role(self, role_data: dict[str, Any]) -> str:
        """Repository method implementation."""
        doc_id = role_data["id"]
        role_data["type"] = "role"
        return await self.driver.upsert("components", role_data, doc_id)

    async def update_role(self, role_id: str, updates: dict[str, Any]) -> str:
        """Repository method implementation."""
        comp = await self.get_role_by_id(role_id)
        if not comp:
            raise ResourceNotFoundError(resource_type="Role", resource_id=role_id)
        await self.driver.update("components", role_id, updates)
        return role_id

    async def delete_role(self, role_id: str) -> bool:
        """Repository method implementation."""
        comp = await self.get_role_by_id(role_id)
        if not comp:
            return False
        return await self.driver.delete("components", role_id)
