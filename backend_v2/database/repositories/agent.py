"""Extracted Repository."""

import logging
from typing import Any

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase

logger = logging.getLogger(__name__)


class AgentRepositoryImpl(AppendOnlyRepositoryBase):
    """AgentRepositoryImpl implementation."""

    def __init__(self, driver: StorageDriver):
        super().__init__(driver)

    async def get_agent_by_id(self, agent_id: str) -> dict[str, Any] | None:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        return await self.driver.get("agents", agent_id)

    async def get_all_agents(self) -> list[dict[str, Any]]:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        return await self.driver.query("agents")

    async def create_agent(self, agent_data: dict[str, Any]) -> str:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        doc_id = agent_data["id"]
        return await self.driver.upsert("agents", agent_data, doc_id)

    async def update_agent(self, agent_id: str, updates: dict[str, Any]) -> bool:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        old_doc = await self.get_agent_by_id(agent_id)
        if not old_doc:
            return False

        await self.driver.update("agents", agent_id, {"is_latest": False})

        base_id, new_id, ver = self._increment_version(agent_id)

        new_doc = dict(old_doc)
        new_doc.update(updates)
        new_doc["id"] = new_id
        new_doc["is_latest"] = True
        new_doc["version"] = ver
        new_doc["slug"] = base_id

        await self.driver.upsert("agents", new_doc, new_id)
        return True

    async def delete_agent(self, agent_id: str) -> bool:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        agent = await self.get_agent_by_id(agent_id)
        if not agent:
            return False
        return await self.driver.delete("agents", agent_id)
