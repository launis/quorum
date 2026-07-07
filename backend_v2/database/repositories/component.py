"""Database repository implementation module."""

import logging
from typing import Any

logger = logging.getLogger(__name__)

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase
from backend_v2.exceptions import ResourceNotFoundError


class ComponentRepositoryImpl(AppendOnlyRepositoryBase):
    """Repository implementation for Components, PromptBlocks, Agents, Blueprints and Output Profiles."""

    async def get_all_components(
        self, type: str | None = None, exclude_types: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        filters = []
        if type:
            filters.append(Filter("type", "==", type))

        components = await self.driver.query("components", filters)

        if exclude_types:
            components = [c for c in components if c.get("type") not in exclude_types]

        return components

    async def get_component_by_id(self, component_id: str) -> dict[str, Any] | None:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        return await self.driver.get("components", component_id)

    async def get_component_by_name(self, name: str) -> dict[str, Any] | None:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        res = await self.driver.query("components", [Filter("name", "==", name)], limit=1)
        return res[0] if res else None

    async def update_component_metadata(self, component_id: str, module: str, component_class: str) -> bool:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        comp = await self.get_component_by_id(component_id)
        if not comp:
            return False
        return await self.driver.update("components", component_id, {"module": module, "class_name": component_class})

    async def register_component(self, component_data: dict[str, Any]) -> str:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        doc_id = component_data["id"]
        return await self.driver.upsert("components", component_data, doc_id)

    async def create_component(self, component_data: dict[str, Any]) -> str:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        return await self.register_component(component_data)

    async def update_component(self, component_id: str, updates: dict[str, Any]) -> str:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        comp = await self.get_component_by_id(component_id)
        if not comp:
            raise ResourceNotFoundError(resource_type="LegacyPromptBlock", resource_id=component_id)
        await self.driver.update("components", component_id, updates)
        return component_id

    async def delete_component(self, component_id: str) -> bool:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        comp = await self.get_component_by_id(component_id)
        if not comp:
            return False
        return await self.driver.delete("components", component_id)

    async def get_components_using_dimension(self, dimension_id: str) -> list[str]:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        matrices = await self.get_all_components(type="evaluation_matrix")
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
