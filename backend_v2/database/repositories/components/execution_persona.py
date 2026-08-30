"""Extracted Repository for Execution Personas."""

import logging
from typing import Any

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase
from backend_v2.exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)


class ExecutionPersonaRepositoryImpl(AppendOnlyRepositoryBase):
    """Repository implementation for Execution Personas."""

    async def get_all_execution_personas(self) -> list[dict[str, Any]]:
        """Retrieves all execution personas from the database.

        Returns:
            List of execution persona dictionaries.
        """
        filters = [Filter("type", "==", "execution_persona")]
        return await self.driver.query("components", filters)

    async def get_execution_persona_by_id(self, persona_id: str) -> dict[str, Any] | None:
        """Retrieves an execution persona by its ID.

        Args:
            persona_id: Unique identifier for the execution persona.

        Returns:
            The execution persona dictionary if found, otherwise None.
        """
        return await self.driver.get("components", persona_id)

    async def create_execution_persona(self, persona_data: dict[str, Any]) -> str:
        """Creates a new execution persona.

        Args:
            persona_data: Dictionary containing execution persona fields.

        Returns:
            The created persona ID.
        """
        doc_id = persona_data["id"]
        persona_data["type"] = "execution_persona"
        return await self.driver.upsert("components", persona_data, doc_id)

    async def update_execution_persona(self, persona_id: str, updates: dict[str, Any]) -> str:
        """Updates an existing execution persona.

        Args:
            persona_id: Unique identifier for the execution persona.
            updates: Dictionary of fields to update.

        Returns:
            The updated persona ID.

        Raises:
            ResourceNotFoundError: If the persona does not exist.
        """
        comp = await self.get_execution_persona_by_id(persona_id)
        if not comp:
            raise ResourceNotFoundError(resource_type="ExecutionPersona", resource_id=persona_id)
        await self.driver.update("components", persona_id, updates)
        return persona_id

    async def delete_execution_persona(self, persona_id: str) -> bool:
        """Deletes an execution persona by ID.

        Args:
            persona_id: Unique identifier for the execution persona.

        Returns:
            True if deleted, False if persona does not exist.
        """
        comp = await self.get_execution_persona_by_id(persona_id)
        if not comp:
            return False
        return await self.driver.delete("components", persona_id)
