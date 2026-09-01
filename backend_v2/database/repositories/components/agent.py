"""Extracted Repository for Agents."""

from __future__ import annotations

import logging

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.prompt_blocks import PromptBlock, PromptBlockAdapter

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

    async def get_agent_by_id(self, agent_id: str) -> PromptBlock | None:
        """Retrieves an agent by its ID.

        Args:
            agent_id: The unique identifier of the agent.

        Returns:
            The validated PromptBlock domain model if found, otherwise None.

        Raises:
            AppException: Propagated from driver if the database query fails.
        """
        doc = await self.driver.get("agents", agent_id)
        if not doc:
            return None
        try:
            return PromptBlockAdapter.validate_python(doc, strict=False)
        except Exception as e:
            logger.error("Failed to parse Agent %s: %s", agent_id, e, exc_info=True)
            raise AppException(
                message=f"Failed to parse Agent {agent_id} from database",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

    async def get_all_agents(self) -> list[PromptBlock]:
        """Retrieves all agents from the database.

        Returns:
            A list of validated PromptBlock domain models.

        Raises:
            AppException: Propagated from driver if the database query fails.
        """
        raw_items = await self.driver.query("agents")
        agents: list[PromptBlock] = []
        for item in raw_items:
            try:
                agents.append(PromptBlockAdapter.validate_python(item, strict=False))
            except Exception as e:
                item_id = item["id"] if "id" in item else "unknown"
                logger.error("Failed to parse Agent %s: %s", item_id, e, exc_info=True)
                raise AppException(
                    message=f"Failed to parse Agent {item_id} from database",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e
        return agents

    async def create_agent(self, agent_data: PromptBlock) -> str:
        """Creates a new agent.

        Args:
            agent_data: The PromptBlock domain model containing the agent data.

        Returns:
            The ID of the created agent.

        Raises:
            AppException: Propagated from driver if the upsert operation fails.
        """
        payload = agent_data.model_dump(mode="json")
        doc_id = payload["id"]
        return await self.driver.upsert("agents", payload, doc_id)

    async def update_agent(self, agent_id: str, updates: PromptBlock) -> bool:
        """Updates an existing agent using versioned append-only logic.

        Args:
            agent_id: The ID of the agent to update.
            updates: PromptBlock domain model containing updated fields.

        Returns:
            True if the update was successful, False if the document was not found.

        Raises:
            AppException: Propagated from driver if database operations fail.
        """
        old_doc = await self.driver.get("agents", agent_id)
        if not old_doc:
            return False

        await self.driver.update("agents", agent_id, {"is_latest": False})

        base_id, new_id, ver = self._increment_version(agent_id)

        new_doc = dict(old_doc)
        new_doc.update(updates.model_dump(mode="json", exclude_unset=True))
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
        agent = await self.driver.get("agents", agent_id)
        if not agent:
            return False
        return await self.driver.delete("agents", agent_id)
