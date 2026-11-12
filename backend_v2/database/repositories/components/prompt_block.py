"""Repository implementation for Prompt Blocks."""

from __future__ import annotations

import logging

from backend_v2.database.repositories.base import BaseRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.prompt_blocks import PromptBlock

logger = logging.getLogger(__name__)

__all__ = ["PromptBlockRepositoryImpl"]


class PromptBlockRepositoryImpl(BaseRepository):
    """Repository implementation for CRUD operations on PromptBlock entities."""

    async def get_prompt_block_by_id(self, block_id: str) -> PromptBlock | None:
        """Retrieve a prompt block by primary key ID.

        Args:
            block_id: Canonical blk_<hex32> prompt block identifier.

        Returns:
            Validated PromptBlock domain model if found, otherwise None.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on hydration/query failure.
        """
        async with self._acquire_entities() as entities:
            return await entities.get_prompt_block(block_id)

    async def get_prompt_block(self, block_id: str) -> PromptBlock | None:
        """Retrieve a prompt block by primary key ID.

        Args:
            block_id: Canonical blk_<hex32> prompt block identifier.

        Returns:
            Validated PromptBlock domain model if found, otherwise None.
        """
        return await self.get_prompt_block_by_id(block_id)

    async def get_all_prompt_blocks(self) -> list[PromptBlock]:
        """Retrieve all persisted prompt blocks.

        Returns:
            List of validated PromptBlock domain models.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on hydration/query failure.
        """
        async with self._acquire_entities() as entities:
            return await entities.list_prompt_blocks()

    async def get_prompt_blocks_by_ids(
        self,
        block_ids: list[str],
        strict: bool = True,
    ) -> list[PromptBlock]:
        """Batch resolve prompt blocks by ID with deterministic missing-ID verification.

        Args:
            block_ids: Ordered list of canonical blk_<hex32> prompt block IDs to resolve.
            strict: When True, raises AppException if any requested ID is missing.

        Returns:
            List of validated PromptBlock domain models preserving unique request order.

        Raises:
            AppException: With RESOURCE_NOT_FOUND (HTTP 404) when strict=True and any block is missing.
        """
        if not block_ids:
            return []

        unique_ids = list(dict.fromkeys(block_ids))
        results: list[PromptBlock] = []
        missing_ids: list[str] = []

        async with self._acquire_entities() as entities:
            for block_id in unique_ids:
                block = await entities.get_prompt_block(block_id)
                if block is not None:
                    results.append(block)
                else:
                    missing_ids.append(block_id)

        if strict and missing_ids:
            logger.error(
                "[PromptBlockRepository] %s: Missing required prompt blocks: %s",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                missing_ids,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "missing_ids": missing_ids},
            )
            raise AppException(
                message=f"Missing required prompt blocks: {', '.join(missing_ids)}",
                details={
                    "error_code": ErrorCodes.RESOURCE_NOT_FOUND.value,
                    "missing_ids": [str(x) for x in missing_ids],
                },
                status_code=404,
            )

        return results

    async def get_all_prompt_blocks_models(self) -> list[PromptBlock]:
        """Retrieve all prompt blocks as validated domain models.

        Returns:
            List of validated PromptBlock domain models.
        """
        return await self.get_all_prompt_blocks()

    async def create_prompt_block(self, block_data: PromptBlock) -> str:
        """Persist a new PromptBlock record.

        Args:
            block_data: Validated PromptBlock domain model.

        Returns:
            Canonical blk_<hex32> identifier of the persisted prompt block.

        Raises:
            AppException: With STORAGE_ACCESS_FAILED if persistence fails.
        """
        async with self._acquire_entities() as entities:
            return await entities.upsert_prompt_block(block_data)

    async def update_prompt_block(self, block_id: str, updates: PromptBlock) -> bool:
        """Update an existing PromptBlock record in-place under its authoritative primary ID.

        Args:
            block_id: Canonical blk_<hex32> identifier of the prompt block to update.
            updates: Validated PromptBlock domain model containing updated fields.

        Returns:
            True if updated, False if the target prompt block does not exist.

        Raises:
            AppException: With STORAGE_ACCESS_FAILED if persistence fails.
        """
        async with self._acquire_entities() as entities:
            existing = await entities.get_prompt_block(block_id)
            if existing is None:
                return False
            persisted = updates if updates.id == block_id else updates.model_copy(update={"id": block_id})
            await entities.upsert_prompt_block(persisted)
            return True

    async def delete_prompt_block(self, block_id: str, force_delete: bool = False) -> bool:
        """Delete a PromptBlock by ID after checking active step references when force_delete is False.

        Args:
            block_id: Canonical blk_<hex32> prompt block identifier.
            force_delete: When True, bypasses active step usage checks.

        Returns:
            True if deleted, False if the prompt block did not exist.

        Raises:
            AppException: With DELETE_BLOCKED_BY_USAGE (HTTP 400) if referenced by a Step.
        """
        async with self._acquire_entities() as entities:
            existing = await entities.get_prompt_block(block_id)
            if existing is None:
                return False

            if not force_delete:
                steps = await entities.list_steps()
                for step in steps:
                    referenced_ids = {
                        step.role_block_id,
                        step.extraction_protocol_block_id,
                        step.execution_persona_block_id,
                        *step.criteria_block_ids,
                    }
                    if block_id in referenced_ids:
                        logger.error(
                            "[PromptBlockRepository] %s: PromptBlock %s delete blocked by step %s usage.",
                            ErrorCodes.DELETE_BLOCKED_BY_USAGE.name,
                            block_id,
                            step.id,
                            extra={
                                "error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value,
                                "prompt_block_id": block_id,
                                "step_id": step.id,
                            },
                        )
                        raise AppException(
                            message=f"PromptBlock delete blocked by step '{step.id}' usage.",
                            details={
                                "error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value,
                                "prompt_block_id": block_id,
                                "step_id": step.id,
                            },
                            status_code=400,
                        )

            return await entities.delete_prompt_block(block_id)
