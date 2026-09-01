"""Extracted Repository for Evaluation Matrices."""

from __future__ import annotations

import logging

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, PromptBlock, PromptBlockAdapter

logger = logging.getLogger(__name__)


class MatrixRepositoryImpl(AppendOnlyRepositoryBase):
    """Repository implementation for Evaluation Matrices."""

    async def get_all_matrices(self) -> list[PromptBlock]:
        """Retrieves all evaluation matrix components from the database.

        Returns:
            List of evaluation matrix prompt block models.
        """
        filters = [Filter("type", "==", "evaluation_matrix")]
        raw_items = await self.driver.query("components", filters)
        matrices: list[PromptBlock] = []
        for item in raw_items:
            try:
                matrices.append(PromptBlockAdapter.validate_python(item, strict=False))
            except Exception as e:
                item_id = item["id"] if "id" in item else "unknown"
                logger.error("Failed to parse Matrix %s: %s", item_id, e, exc_info=True)
                raise AppException(
                    message=f"Failed to parse Matrix {item_id} from database",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e
        return matrices

    async def get_matrix_by_id(self, matrix_id: str) -> PromptBlock | None:
        """Retrieves an evaluation matrix component by its ID.

        Args:
            matrix_id: Unique identifier for the matrix.

        Returns:
            The matrix PromptBlock if found, otherwise None.
        """
        doc = await self.driver.get("components", matrix_id)
        if not doc:
            return None
        try:
            return PromptBlockAdapter.validate_python(doc, strict=False)
        except Exception as e:
            logger.error("Failed to parse Matrix %s: %s", matrix_id, e, exc_info=True)
            raise AppException(
                message=f"Failed to parse Matrix {matrix_id} from database",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

    async def create_matrix(self, matrix_data: PromptBlock) -> str:
        """Creates a new evaluation matrix component.

        Args:
            matrix_data: PromptBlock domain model containing matrix fields.

        Returns:
            The created matrix ID.
        """
        payload = matrix_data.model_dump(mode="json")
        doc_id = payload["id"]
        payload["type"] = "evaluation_matrix"
        return await self.driver.upsert("components", payload, doc_id)

    async def update_matrix(self, matrix_id: str, updates: PromptBlock) -> str:
        """Updates an existing evaluation matrix component.

        Args:
            matrix_id: Unique identifier for the matrix.
            updates: PromptBlock domain model containing updated fields.

        Returns:
            The updated matrix ID.

        Raises:
            ResourceNotFoundError: If the matrix does not exist.
        """
        comp = await self.get_matrix_by_id(matrix_id)
        if not comp:
            raise ResourceNotFoundError(resource_type="Matrix", resource_id=matrix_id)
        payload = updates.model_dump(mode="json", exclude_unset=True)
        await self.driver.update("components", matrix_id, payload)
        return matrix_id

    async def delete_matrix(self, matrix_id: str) -> bool:
        """Deletes an evaluation matrix component by ID.

        Args:
            matrix_id: Unique identifier for the matrix.

        Returns:
            True if deleted, False if matrix does not exist.
        """
        comp = await self.get_matrix_by_id(matrix_id)
        if not comp:
            return False
        return await self.driver.delete("components", matrix_id)

    async def get_matrices_using_dimension(self, dimension_id: str) -> list[str]:
        """Finds all matrix component IDs referencing a given dimension ID.

        Args:
            dimension_id: Unique identifier for the dimension.

        Returns:
            List of matching matrix IDs.
        """
        matrices = await self.get_all_matrices()
        matches: list[str] = []
        for m in matrices:
            if isinstance(m, MatrixPromptBlock) and m.rows is not None:
                for row in m.rows:
                    if dimension_id in row.label.translations.values() or dimension_id in row.ai_description:
                        matches.append(m.id)
                        break
        return matches
