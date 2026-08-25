"""Extracted Repository for Prompt Blocks."""

import logging
from typing import Any

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.prompt_blocks import PromptBlock, PromptBlockAdapter

logger = logging.getLogger(__name__)


class PromptBlockRepositoryImpl(AppendOnlyRepositoryBase):
    """Implementation of the IPromptBlockRepository.

    This repository is responsible for CRUD operations on prompt_blocks.
    It inherits from AppendOnlyRepositoryBase to support versioned documents.
    """

    def __init__(self, driver: StorageDriver):
        """Initializes the repository with a storage driver.

        Args:
            driver: The underlying storage driver for database operations.
        """
        super().__init__(driver)

    async def get_prompt_block_by_id(self, block_id: str) -> dict[str, Any] | None:
        """Retrieves a prompt block by its ID.

        Args:
            block_id: The unique identifier of the prompt block.

        Returns:
            A dictionary containing the prompt block data if found, otherwise None.

        Raises:
            AppException: Propagated from driver if the database query fails.
        """
        return await self.driver.get("prompt_blocks", block_id)

    async def get_prompt_block(self, block_id: str) -> dict[str, Any] | None:
        """Retrieves a prompt block by its ID (alias for get_prompt_block_by_id).

        Args:
            block_id: The unique identifier of the prompt block.

        Returns:
            A dictionary containing the prompt block data if found, otherwise None.

        Raises:
            AppException: Propagated from driver if the database query fails.
        """
        return await self.get_prompt_block_by_id(block_id)

    async def get_all_prompt_blocks(self) -> list[dict[str, Any]]:
        """Retrieves all prompt blocks from the database.

        Returns:
            A list of dictionaries representing the prompt blocks.

        Raises:
            AppException: Propagated from driver if the database query fails.
        """
        return await self.driver.query("prompt_blocks")

    async def get_prompt_blocks_by_ids(
        self,
        block_ids: list[str],
        strict: bool = True,
    ) -> list[PromptBlock]:
        """Batch resolve prompt blocks by ID with mathematical set validation.

        Args:
            block_ids: List of prompt block IDs to retrieve.
            strict: If True, raises AppException when any requested ID is missing.

        Returns:
            List of hydrated PromptBlock models.

        Raises:
            AppException: If strict=True and one or more block IDs are not found in DB.
        """
        if not block_ids:
            return []

        unique_ids = list(dict.fromkeys(block_ids))
        results: list[PromptBlock] = []

        for bid in unique_ids:
            doc = await self.get_prompt_block_by_id(bid)
            if doc:
                try:
                    results.append(PromptBlockAdapter.validate_python(doc, strict=False))
                except Exception as e:
                    logger.error("Failed to parse PromptBlock %s: %s", bid, e, exc_info=True)
                    raise AppException(
                        message=f"Failed to parse PromptBlock {bid} from database",
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from e

        found_ids = {b.id for b in results}
        missing_ids = [bid for bid in unique_ids if bid not in found_ids]

        if strict and missing_ids:
            msg = f"Failed to batch resolve prompt blocks. Missing block IDs: {missing_ids}"
            logger.error(
                "[PromptBlockRepo] %s: %s",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                msg,
                extra={
                    "error_code": ErrorCodes.RESOURCE_NOT_FOUND.name,
                    "missing_ids": missing_ids,
                },
            )
            raise AppException(
                message=msg,
                status_code=404,
                details={
                    "error_code": ErrorCodes.RESOURCE_NOT_FOUND.value,
                    "missing_ids": missing_ids,
                },
            )

        return results

    async def get_all_prompt_blocks_models(self) -> list[PromptBlock]:
        """Retrieves all prompt blocks and maps them to Pydantic models.

        Returns:
            A list of PromptBlock models.

        Raises:
            AppException: With VALIDATION_FAILED if a block cannot be parsed.
        """
        data = await self.get_all_prompt_blocks()
        models = []
        for b in data:
            try:
                models.append(PromptBlockAdapter.validate_python(b, strict=False))
            except Exception as e:
                logger.error("Failed to parse PromptBlock %s: %s", b.get("id"), e, exc_info=True)

                raise AppException(
                    message=f"Failed to parse PromptBlock {b.get('id')} from database",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e
        return models

    async def create_prompt_block(self, block_data: dict[str, Any]) -> str:
        """Creates a new prompt block.

        Args:
            block_data: The dictionary containing the prompt block data.

        Returns:
            The ID of the created prompt block.

        Raises:
            AppException: Propagated from driver if the upsert operation fails.
        """
        doc_id = block_data["id"]
        return await self.driver.upsert("prompt_blocks", block_data, doc_id)

    async def update_prompt_block(self, block_id: str, updates: dict[str, Any]) -> bool:
        """Updates an existing prompt block using versioned append-only logic.

        Args:
            block_id: The ID of the prompt block to update.
            updates: A dictionary of key-value pairs to update.

        Returns:
            True if the update was successful, False if the document was not found.

        Raises:
            AppException: Propagated from driver if database operations fail.
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
        """Deletes a prompt block by ID.

        If force_delete is False, the method checks if the prompt block is currently
        used by any existing step and blocks the deletion if it is.

        Args:
            block_id: The ID of the prompt block to delete.
            force_delete: If True, bypasses usage checks and forces deletion.

        Returns:
            True if successfully deleted, False if the document did not exist.

        Raises:
            AppException: With ErrorCodes.DELETE_BLOCKED_BY_USAGE if force_delete
                is False and the prompt block is used by a step.
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
