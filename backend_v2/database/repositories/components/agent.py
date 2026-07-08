"""Extracted Repository for Agents."""

import logging
from typing import Any

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase

logger = logging.getLogger(__name__)


class AgentRepositoryImpl(AppendOnlyRepositoryBase):
    """Implementation of the Agent Repository.

    This repository is responsible for CRUD operations on agents.
    It inherits from AppendOnlyRepositoryBase to support versioned documents.
    """

    def __init__(self, driver: StorageDriver):
        """Initializes the repository with a storage driver.

        Args:
            driver: The underlying storage driver for database operations.
        """
        super().__init__(driver)

    async def get_agent_by_id(self, agent_id: str) -> dict[str, Any] | None:
        """Retrieves an agent by its ID.

        Args:
            agent_id: The unique identifier of the agent.

        Returns:
            A dictionary containing the agent data if found, otherwise None.

        Raises:
            AppException: Propagated from driver if the database query fails.
        """
        return await self.driver.get("agents", agent_id)

    async def get_all_agents(self) -> list[dict[str, Any]]:
        """Retrieves all agents from the database.

        Returns:
            A list of dictionaries representing the agents.

        Raises:
            AppException: Propagated from driver if the database query fails.
        """
        return await self.driver.query("agents")

    async def create_agent(self, agent_data: dict[str, Any]) -> str:
        """Creates a new agent.

        Args:
            agent_data: The dictionary containing the agent data.

        Returns:
            The ID of the created agent.

        Raises:
            AppException: Propagated from driver if the upsert operation fails.
        """
        doc_id = agent_data["id"]
        return await self.driver.upsert("agents", agent_data, doc_id)

    async def update_agent(self, agent_id: str, updates: dict[str, Any]) -> bool:
        """Updates an existing agent using versioned append-only logic.

        Args:
            agent_id: The ID of the agent to update.
            updates: A dictionary of key-value pairs to update.

        Returns:
            True if the update was successful, False if the document was not found.

        Raises:
            AppException: Propagated from driver if database operations fail.
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
        """Deletes an agent by ID.

        Args:
            agent_id: The ID of the agent to delete.

        Returns:
            True if successfully deleted, False if the document did not exist.

        Raises:
            AppException: Propagated from driver if database operations fail.
        """
        agent = await self.get_agent_by_id(agent_id)
        if not agent:
            return False
        return await self.driver.delete("agents", agent_id)
