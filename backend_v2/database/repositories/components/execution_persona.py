import logging
from typing import Any

from backend_v2.database.driver import Filter
from backend_v2.database.interfaces import IExecutionPersonaRepository
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase
from backend_v2.exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)


class ExecutionPersonaRepositoryImpl(AppendOnlyRepositoryBase, IExecutionPersonaRepository):
    """Repository implementation for Execution Personas."""

    async def get_all_execution_personas(self) -> list[dict[str, Any]]:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        filters = [Filter("type", "==", "execution_persona")]
        return await self.driver.query("components", filters)

    async def get_execution_persona_by_id(self, persona_id: str) -> dict[str, Any] | None:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        return await self.driver.get("components", persona_id)

    async def create_execution_persona(self, persona_data: dict[str, Any]) -> str:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        doc_id = persona_data["id"]
        persona_data["type"] = "execution_persona"
        return await self.driver.upsert("components", persona_data, doc_id)

    async def update_execution_persona(self, persona_id: str, updates: dict[str, Any]) -> str:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        comp = await self.get_execution_persona_by_id(persona_id)
        if not comp:
            raise ResourceNotFoundError(resource_type="ExecutionPersona", resource_id=persona_id)
        await self.driver.update("components", persona_id, updates)
        return persona_id

    async def delete_execution_persona(self, persona_id: str) -> bool:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        comp = await self.get_execution_persona_by_id(persona_id)
        if not comp:
            return False
        return await self.driver.delete("components", persona_id)
