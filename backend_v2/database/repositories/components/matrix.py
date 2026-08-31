"""Extracted Repository for Evaluation Matrices."""

import logging
from typing import Any

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase
from backend_v2.exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)


class MatrixRepositoryImpl(AppendOnlyRepositoryBase):
    """Repository implementation for Evaluation Matrices."""

    async def get_all_matrices(self) -> list[dict[str, Any]]:
        """Retrieves all evaluation matrix components from the database.

        Returns:
            List of evaluation matrix dictionaries.
        """
        filters = [Filter("type", "==", "evaluation_matrix")]
        return await self.driver.query("components", filters)

    async def get_matrix_by_id(self, matrix_id: str) -> dict[str, Any] | None:
        """Retrieves an evaluation matrix component by its ID.

        Args:
            matrix_id: Unique identifier for the matrix.

        Returns:
            The matrix dictionary if found, otherwise None.
        """
        return await self.driver.get("components", matrix_id)

    async def create_matrix(self, matrix_data: dict[str, Any]) -> str:
        """Creates a new evaluation matrix component.

        Args:
            matrix_data: Dictionary containing matrix fields.

        Returns:
            The created matrix ID.
        """
        doc_id = matrix_data["id"]
        matrix_data["type"] = "evaluation_matrix"
        return await self.driver.upsert("components", matrix_data, doc_id)

    async def update_matrix(self, matrix_id: str, updates: dict[str, Any]) -> str:
        """Updates an existing evaluation matrix component.

        Args:
            matrix_id: Unique identifier for the matrix.
            updates: Dictionary of fields to update.

        Returns:
            The updated matrix ID.

        Raises:
            ResourceNotFoundError: If the matrix does not exist.
        """
        comp = await self.get_matrix_by_id(matrix_id)
        if not comp:
            raise ResourceNotFoundError(resource_type="Matrix", resource_id=matrix_id)
        await self.driver.update("components", matrix_id, updates)
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
        raw_matrices = await self.get_all_matrices()
        matches: list[str] = []
        for m in raw_matrices:
            content = m.get("content")
            if content:
                try:
                    criteria = content.get("criteria") or []
                    for crit in criteria:
                        if crit.get("dimension_id") == dimension_id:
                            m_id = m.get("id")
                            if m_id:
                                matches.append(str(m_id))
                            break
                except AttributeError, TypeError:
                    continue
        return matches
