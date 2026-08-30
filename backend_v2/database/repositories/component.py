"""Database repository implementation module for generic Components."""

import logging
from typing import Any

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase
from backend_v2.exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)


class ComponentRepositoryImpl(AppendOnlyRepositoryBase):
    """Repository implementation for generic Components."""

    async def get_all_components(
        self, type: str | None = None, exclude_types: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Retrieves all components with optional type filter.

        Args:
            type: Optional component type filter.
            exclude_types: Optional list of component types to exclude.

        Returns:
            List of component dictionaries.
        """
        filters = []
        if type:
            filters.append(Filter("type", "==", type))

        components = await self.driver.query("components", filters)

        if exclude_types:
            components = [c for c in components if ("type" not in c or c["type"] not in exclude_types)]

        return components

    async def get_component_by_id(self, component_id: str) -> dict[str, Any] | None:
        """Retrieves a component by its ID.

        Args:
            component_id: Unique identifier for the component.

        Returns:
            The component dictionary if found, otherwise None.
        """
        return await self.driver.get("components", component_id)

    async def get_component_by_name(self, name: str) -> dict[str, Any] | None:
        """Retrieves a component by name.

        Args:
            name: Name of the component.

        Returns:
            The component dictionary if found, otherwise None.
        """
        res = await self.driver.query("components", [Filter("name", "==", name)], limit=1)
        return res[0] if res else None

    async def update_component_metadata(self, component_id: str, module: str, component_class: str) -> bool:
        """Updates module and class name metadata for a component.

        Args:
            component_id: Unique identifier for the component.
            module: Target module path.
            component_class: Target class name.

        Returns:
            True if updated, False if component does not exist.
        """
        comp = await self.get_component_by_id(component_id)
        if not comp:
            return False
        return await self.driver.update("components", component_id, {"module": module, "class_name": component_class})

    async def register_component(self, component_data: dict[str, Any]) -> str:
        """Registers a component into storage.

        Args:
            component_data: Dictionary containing component fields.

        Returns:
            The component ID.
        """
        doc_id = component_data["id"]
        return await self.driver.upsert("components", component_data, doc_id)

    async def create_component(self, component_data: dict[str, Any]) -> str:
        """Creates a new component.

        Args:
            component_data: Dictionary containing component fields.

        Returns:
            The created component ID.
        """
        return await self.register_component(component_data)

    async def update_component(self, component_id: str, updates: dict[str, Any]) -> str:
        """Updates an existing component.

        Args:
            component_id: Unique identifier for the component.
            updates: Dictionary of fields to update.

        Returns:
            The updated component ID.

        Raises:
            ResourceNotFoundError: If the component does not exist.
        """
        comp = await self.get_component_by_id(component_id)
        if not comp:
            raise ResourceNotFoundError(resource_type="LegacyPromptBlock", resource_id=component_id)
        await self.driver.update("components", component_id, updates)
        return component_id

    async def delete_component(self, component_id: str) -> bool:
        """Deletes a component by ID.

        Args:
            component_id: Unique identifier for the component.

        Returns:
            True if deleted, False if component does not exist.
        """
        comp = await self.get_component_by_id(component_id)
        if not comp:
            return False
        return await self.driver.delete("components", component_id)

    async def get_components_using_dimension(self, dimension_id: str) -> list[str]:
        """Finds all evaluation matrix component IDs using a given dimension.

        Args:
            dimension_id: Unique identifier for the dimension.

        Returns:
            List of matching matrix IDs.
        """
        matrices = await self.get_all_components(type="evaluation_matrix")
        matches = []
        for m in matrices:
            if "content" in m and isinstance(m["content"], dict):
                content = m["content"]
                if "criteria" in content and isinstance(content["criteria"], list):
                    for crit in content["criteria"]:
                        if isinstance(crit, dict) and "dimension_id" in crit and crit["dimension_id"] == dimension_id:
                            if "id" in m:
                                matches.append(m["id"])
                            break
        return matches
