"""Extracted Repository for Execution Personas."""

from __future__ import annotations

import logging

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.domain.prompt_blocks import PromptBlock, PromptBlockAdapter

logger = logging.getLogger(__name__)


class ExecutionPersonaRepositoryImpl(AppendOnlyRepositoryBase):
    """Repository implementation for Execution Personas."""

    async def get_all_execution_personas(self) -> list[PromptBlock]:
        """Retrieves all execution personas from the database.

        Returns:
            List of execution persona PromptBlock models.
        """
        filters = [Filter("type", "==", "execution_persona")]
        raw_items = await self.driver.query("components", filters)
        personas: list[PromptBlock] = []
        for item in raw_items:
            try:
                personas.append(PromptBlockAdapter.validate_python(item, strict=False))
            except Exception as e:
                item_id = item["id"] if "id" in item else "unknown"
                logger.error("Failed to parse ExecutionPersona %s: %s", item_id, e, exc_info=True)
                raise AppException(
                    message=f"Failed to parse ExecutionPersona {item_id} from database",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e
        return personas

    async def get_execution_persona_by_id(self, persona_id: str) -> PromptBlock | None:
        """Retrieves an execution persona by its ID.

        Args:
            persona_id: Unique identifier for the execution persona.

        Returns:
            The execution persona PromptBlock if found, otherwise None.
        """
        doc = await self.driver.get("components", persona_id)
        if not doc:
            return None
        try:
            return PromptBlockAdapter.validate_python(doc, strict=False)
        except Exception as e:
            logger.error("Failed to parse ExecutionPersona %s: %s", persona_id, e, exc_info=True)
            raise AppException(
                message=f"Failed to parse ExecutionPersona {persona_id} from database",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

    async def create_execution_persona(self, persona_data: PromptBlock) -> str:
        """Creates a new execution persona.

        Args:
            persona_data: PromptBlock containing execution persona fields.

        Returns:
            The created persona ID.
        """
        payload = persona_data.model_dump(mode="json")
        doc_id = payload["id"]
        payload["type"] = "execution_persona"
        return await self.driver.upsert("components", payload, doc_id)

    async def update_execution_persona(self, persona_id: str, updates: PromptBlock) -> str:
        """Updates an existing execution persona.

        Args:
            persona_id: Unique identifier for the execution persona.
            updates: PromptBlock containing fields to update.

        Returns:
            The updated persona ID.

        Raises:
            ResourceNotFoundError: If the persona does not exist.
        """
        comp = await self.get_execution_persona_by_id(persona_id)
        if not comp:
            raise ResourceNotFoundError(resource_type="ExecutionPersona", resource_id=persona_id)
        payload = updates.model_dump(mode="json", exclude_unset=True)
        await self.driver.update("components", persona_id, payload)
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
