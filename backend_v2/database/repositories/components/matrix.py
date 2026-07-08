import logging
from typing import Any

from backend_v2.database.driver import Filter
from backend_v2.database.interfaces import IMatrixRepository
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase
from backend_v2.exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)


class MatrixRepositoryImpl(AppendOnlyRepositoryBase, IMatrixRepository):
    """Repository implementation for Evaluation Matrices."""

    async def get_all_matrices(self) -> list[dict[str, Any]]:
        """Repository method implementation."""
        filters = [Filter("type", "==", "evaluation_matrix")]
        return await self.driver.query("components", filters)

    async def get_matrix_by_id(self, matrix_id: str) -> dict[str, Any] | None:
        """Repository method implementation."""
        return await self.driver.get("components", matrix_id)

    async def create_matrix(self, matrix_data: dict[str, Any]) -> str:
        """Repository method implementation."""
        doc_id = matrix_data["id"]
        matrix_data["type"] = "evaluation_matrix"
        return await self.driver.upsert("components", matrix_data, doc_id)

    async def update_matrix(self, matrix_id: str, updates: dict[str, Any]) -> str:
        """Repository method implementation."""
        comp = await self.get_matrix_by_id(matrix_id)
        if not comp:
            raise ResourceNotFoundError(resource_type="Matrix", resource_id=matrix_id)
        await self.driver.update("components", matrix_id, updates)
        return matrix_id

    async def delete_matrix(self, matrix_id: str) -> bool:
        """Repository method implementation."""
        comp = await self.get_matrix_by_id(matrix_id)
        if not comp:
            return False
        return await self.driver.delete("components", matrix_id)

    async def get_matrices_using_dimension(self, dimension_id: str) -> list[str]:
        """Repository method implementation."""
        matrices = await self.get_all_matrices()
        matches = []
        for m in matrices:
            content = m.get("content", {})
            if not isinstance(content, dict):
                continue
            criteria = content.get("criteria", [])
            if not isinstance(criteria, list):
                continue
            for crit in criteria:
                if isinstance(crit, dict) and crit.get("dimension_id") == dimension_id:
                    matches.append(m["id"])
                    break
        return matches
