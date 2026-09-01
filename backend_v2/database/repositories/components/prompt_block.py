"""Extracted Repository for Prompt Blocks."""

from __future__ import annotations

import logging

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

    async def get_prompt_block_by_id(self, block_id: str) -> PromptBlock | None:
        """Retrieves a prompt block by its ID.

        Args:
            block_id: The unique identifier of the prompt block.

        Returns:
            The validated PromptBlock domain model if found, otherwise None.

        Raises:
            AppException: If database query or validation fails.
        """
        doc = await self.driver.get("prompt_blocks", block_id)
        if not doc:
            return None
        try:
            return PromptBlockAdapter.validate_python(doc, strict=False)
        except Exception as e:
            logger.error("Failed to parse PromptBlock %s: %s", block_id, e, exc_info=True)
            raise AppException(
                message=f"Failed to parse PromptBlock {block_id} from database",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

    async def get_prompt_block(self, block_id: str) -> PromptBlock | None:
        """Retrieves a prompt block by its ID (alias for get_prompt_block_by_id).

        Args:
            block_id: The unique identifier of the prompt block.

        Returns:
            The validated PromptBlock domain model if found, otherwise None.
        """
        return await self.get_prompt_block_by_id(block_id)

    async def get_all_prompt_blocks(self) -> list[PromptBlock]:
        """Retrieves all prompt blocks from the database.

        Returns:
            A list of validated PromptBlock domain models.

        Raises:
            AppException: If database query fails.
        """
        data = await self.driver.query("prompt_blocks")
        models: list[PromptBlock] = []
        for b in data:
            try:
                models.append(PromptBlockAdapter.validate_python(b, strict=False))
            except Exception as e:
                item_id = b["id"] if "id" in b else "unknown"
                logger.error("Failed to parse PromptBlock %s: %s", item_id, e, exc_info=True)
                raise AppException(
                    message=f"Failed to parse PromptBlock {item_id} from database",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e
        return models

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
            List of validated PromptBlock domain models.

        Raises:
            AppException: If strict=True and any requested block ID is missing.
        """
        if not block_ids:
            return []

        unique_ids = list(dict.fromkeys(block_ids))
        results: list[PromptBlock] = []
        missing_ids: list[str] = []

        for block_id in unique_ids:
            block = await self.get_prompt_block_by_id(block_id)
            if block is not None:
                results.append(block)
            else:
                missing_ids.append(block_id)

        if strict and missing_ids:
            raise AppException(
                message=f"Missing required prompt blocks: {', '.join(missing_ids)}",
                details={
                    "error_code": ErrorCodes.RESOURCE_NOT_FOUND.value,
                    "missing_ids": missing_ids,
                },
                status_code=404,
            )

        return results

    async def get_all_prompt_blocks_models(self) -> list[PromptBlock]:
        """Retrieves all prompt blocks and maps them to Pydantic models.

        Returns:
            A list of PromptBlock models.
        """
        return await self.get_all_prompt_blocks()

    async def create_prompt_block(self, block_data: PromptBlock) -> str:
        """Creates a new prompt block.

        Args:
            block_data: The PromptBlock model containing the prompt block data.

        Returns:
            The ID of the created prompt block.

        Raises:
            AppException: Propagated from driver if the upsert operation fails.
        """
        payload = block_data.model_dump(mode="json")
        doc_id = payload["id"]
        return await self.driver.upsert("prompt_blocks", payload, doc_id)

    async def update_prompt_block(self, block_id: str, updates: PromptBlock) -> bool:
        """Updates an existing prompt block using versioned append-only logic.

        Args:
            block_id: The ID of the prompt block to update.
            updates: PromptBlock domain model containing updated fields.

        Returns:
            True if the update was successful, False if the document was not found.

        Raises:
            AppException: Propagated from driver if database operations fail.
        """
        old_doc = await self.driver.get("prompt_blocks", block_id)
        if not old_doc:
            return False

        await self.driver.update("prompt_blocks", block_id, {"is_latest": False})

        base_id, new_id, ver = self._increment_version(block_id)

        new_doc = dict(old_doc)
        new_doc.update(updates.model_dump(mode="json", exclude_unset=True))
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
        block = await self.driver.get("prompt_blocks", block_id)
        if not block:
            return False

        if not force_delete:
            steps = await self.driver.query("steps")
            for s in steps:
                if "prompt_blocks" in s and isinstance(s["prompt_blocks"], list) and block_id in s["prompt_blocks"]:
                    step_ref = str(s["id"] if "id" in s else "unknown")
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
