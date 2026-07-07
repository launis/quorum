"""Extracted Repository."""

import logging
from typing import Any

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase

logger = logging.getLogger(__name__)


class TaskBlueprintRepositoryImpl(AppendOnlyRepositoryBase):
    """TaskBlueprintRepositoryImpl implementation."""

    def __init__(self, driver: StorageDriver):
        super().__init__(driver)

    async def get_task_blueprint_by_id(self, blueprint_id: str) -> dict[str, Any] | None:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        return await self.driver.get("task_blueprints", blueprint_id)

    async def get_all_task_blueprints(self) -> list[dict[str, Any]]:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        return await self.driver.query("task_blueprints")

    async def create_task_blueprint(self, blueprint_data: dict[str, Any]) -> str:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        doc_id = blueprint_data["id"]
        return await self.driver.upsert("task_blueprints", blueprint_data, doc_id)

    async def update_task_blueprint(self, blueprint_id: str, updates: dict[str, Any]) -> bool:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        old_doc = await self.get_task_blueprint_by_id(blueprint_id)
        if not old_doc:
            return False

        await self.driver.update("task_blueprints", blueprint_id, {"is_latest": False})

        base_id, new_id, ver = self._increment_version(blueprint_id)

        new_doc = dict(old_doc)
        new_doc.update(updates)
        new_doc["id"] = new_id
        new_doc["is_latest"] = True
        new_doc["version"] = ver
        new_doc["slug"] = base_id

        await self.driver.upsert("task_blueprints", new_doc, new_id)
        return True

    async def delete_task_blueprint(self, blueprint_id: str) -> bool:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        blueprint = await self.get_task_blueprint_by_id(blueprint_id)
        if not blueprint:
            return False
        return await self.driver.delete("task_blueprints", blueprint_id)
