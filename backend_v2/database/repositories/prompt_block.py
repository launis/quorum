"""Extracted Repository."""

import logging
from typing import Any

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.v2_core import PromptBlock

logger = logging.getLogger(__name__)


class PromptBlockRepositoryImpl(AppendOnlyRepositoryBase):
    """PromptBlockRepositoryImpl implementation."""

    def __init__(self, driver: StorageDriver):
        super().__init__(driver)

    async def get_prompt_block_by_id(self, block_id: str) -> dict[str, Any] | None:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        return await self.driver.get("prompt_blocks", block_id)

    async def get_prompt_block(self, block_id: str) -> dict[str, Any] | None:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        return await self.get_prompt_block_by_id(block_id)

    async def get_all_prompt_blocks(self) -> list[dict[str, Any]]:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        return await self.driver.query("prompt_blocks")

    async def get_all_prompt_blocks_models(self) -> list[PromptBlock]:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        data = await self.get_all_prompt_blocks()
        models = []
        for b in data:
            try:
                models.append(PromptBlock.model_validate(b, strict=False))
            except Exception as e:
                logger.error("Failed to parse PromptBlock %s: %s", b.get("id"), e, exc_info=True)

                raise AppException(
                    message=f"Failed to parse PromptBlock {b.get('id')} from database",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e
        return models

    async def create_prompt_block(self, block_data: dict[str, Any]) -> str:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        doc_id = block_data["id"]
        return await self.driver.upsert("prompt_blocks", block_data, doc_id)

    async def update_prompt_block(self, block_id: str, updates: dict[str, Any]) -> bool:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        old_doc = await self.get_prompt_block_by_id(block_id)
        if not old_doc:
            return False

        await self.driver.update("prompt_blocks", block_id, {"is_latest": False})

        base_id, new_id, ver = self._increment_version(block_id)

        new_doc = dict(old_doc)
        new_doc.update(updates)
        new_doc["id"] = new_id
        new_doc["is_latest"] = True
        new_doc["version"] = ver
        new_doc["slug"] = base_id

        await self.driver.upsert("prompt_blocks", new_doc, new_id)
        return True

    async def delete_prompt_block(self, block_id: str, force_delete: bool = False) -> bool:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        block = await self.get_prompt_block_by_id(block_id)
        if not block:
            return False

        if not force_delete:
            steps = await self.driver.query("steps")
            for s in steps:
                if block_id in s.get("prompt_blocks", []):
                    step_ref = str(s.get("id", "unknown"))
                    raise AppException(
                        message="PromptBlock delete blocked by step usage.",
                        details={
                            "error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value,
                            "prompt_block_id": block_id,
                            "step_id": step_ref,
                        },
                        status_code=400,
                    )

        return await self.driver.delete("prompt_blocks", block_id)
