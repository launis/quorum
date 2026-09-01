"""Database repository implementation module for generic Components."""

from __future__ import annotations

import logging

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, PromptBlock, PromptBlockAdapter

logger = logging.getLogger(__name__)


class ComponentRepositoryImpl(AppendOnlyRepositoryBase):
    """Repository implementation for generic Components."""

    async def get_all_components(
        self, type: str | None = None, exclude_types: list[str] | None = None
    ) -> list[PromptBlock]:
        """Retrieves all components with optional type filter.

        Args:
            type: Optional component type filter.
            exclude_types: Optional list of component types to exclude.

        Returns:
            List of PromptBlock domain models.
        """
        filters = []
        if type:
            filters.append(Filter("type", "==", type))

        raw_items = await self.driver.query("components", filters)

        if exclude_types:
            raw_items = [c for c in raw_items if ("type" not in c or c["type"] not in exclude_types)]

        components: list[PromptBlock] = []
        for item in raw_items:
            try:
                components.append(PromptBlockAdapter.validate_python(item, strict=False))
            except Exception as e:
                item_id = item["id"] if "id" in item else "unknown"
                logger.error("Failed to parse Component %s: %s", item_id, e, exc_info=True)
                raise AppException(
                    message=f"Failed to parse Component {item_id} from database",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e
        return components

    async def get_component_by_id(self, component_id: str) -> PromptBlock | None:
        """Retrieves a component by its ID.

        Args:
            component_id: Unique identifier for the component.

        Returns:
            The PromptBlock model if found, otherwise None.
        """
        doc = await self.driver.get("components", component_id)
        if not doc:
            return None
        try:
            return PromptBlockAdapter.validate_python(doc, strict=False)
        except Exception as e:
            logger.error("Failed to parse Component %s: %s", component_id, e, exc_info=True)
            raise AppException(
                message=f"Failed to parse Component {component_id} from database",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

    async def get_component_by_name(self, name: str) -> PromptBlock | None:
        """Retrieves a component by name.

        Args:
            name: Name of the component.

        Returns:
            The PromptBlock model if found, otherwise None.
        """
        res = await self.driver.query("components", [Filter("name", "==", name)], limit=1)
        if not res:
            return None
        try:
            return PromptBlockAdapter.validate_python(res[0], strict=False)
        except Exception as e:
            logger.error("Failed to parse Component with name %s: %s", name, e, exc_info=True)
            raise AppException(
                message=f"Failed to parse Component {name} from database",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

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

    async def register_component(self, component_data: PromptBlock) -> str:
        """Registers a component into storage.

        Args:
            component_data: PromptBlock domain model containing component fields.

        Returns:
            The component ID.
        """
        payload = component_data.model_dump(mode="json")
        doc_id = payload["id"]
        return await self.driver.upsert("components", payload, doc_id)

    async def create_component(self, component_data: PromptBlock) -> str:
        """Creates a new component.

        Args:
            component_data: PromptBlock domain model containing component fields.

        Returns:
            The created component ID.
        """
        return await self.register_component(component_data)

    async def update_component(self, component_id: str, updates: PromptBlock) -> str:
        """Updates an existing component.

        Args:
            component_id: Unique identifier for the component.
            updates: PromptBlock domain model containing fields to update.

        Returns:
            The updated component ID.

        Raises:
            ResourceNotFoundError: If the component does not exist.
        """
        comp = await self.get_component_by_id(component_id)
        if not comp:
            raise ResourceNotFoundError(resource_type="LegacyPromptBlock", resource_id=component_id)
        payload = updates.model_dump(mode="json", exclude_unset=True)
        await self.driver.update("components", component_id, payload)
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
        components = await self.get_all_components(type="evaluation_matrix")
        matches: list[str] = []
        for c in components:
            if isinstance(c, MatrixPromptBlock) and c.rows is not None:
                for row in c.rows:
                    if dimension_id in row.label.translations.values() or dimension_id in row.ai_description:
                        matches.append(c.id)
                        break
        return matches
