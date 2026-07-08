"""Extracted Repository for Task Blueprints."""

import logging
from typing import Any

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase

logger = logging.getLogger(__name__)


class TaskBlueprintRepositoryImpl(AppendOnlyRepositoryBase):
    """Implementation of the Task Blueprint Repository.

    This repository is responsible for CRUD operations on task blueprints.
    It inherits from AppendOnlyRepositoryBase to support versioned documents.
    """

    def __init__(self, driver: StorageDriver):
        """Initializes the repository with a storage driver.

        Args:
            driver: The underlying storage driver for database operations.
        """
        super().__init__(driver)

    async def get_task_blueprint_by_id(self, blueprint_id: str) -> dict[str, Any] | None:
        """Retrieves a task blueprint by its ID.

        Args:
            blueprint_id: The unique identifier of the task blueprint.

        Returns:
            A dictionary containing the task blueprint data if found, otherwise None.

        Raises:
            AppException: Propagated from driver if the database query fails.
        """
        return await self.driver.get("task_blueprints", blueprint_id)

    async def get_all_task_blueprints(self) -> list[dict[str, Any]]:
        """Retrieves all task blueprints from the database.

        Returns:
            A list of dictionaries representing the task blueprints.

        Raises:
            AppException: Propagated from driver if the database query fails.
        """
        return await self.driver.query("task_blueprints")

    async def create_task_blueprint(self, blueprint_data: dict[str, Any]) -> str:
        """Creates a new task blueprint.

        Args:
            blueprint_data: The dictionary containing the task blueprint data.

        Returns:
            The ID of the created task blueprint.

        Raises:
            AppException: Propagated from driver if the upsert operation fails.
        """
        doc_id = blueprint_data["id"]
        return await self.driver.upsert("task_blueprints", blueprint_data, doc_id)

    async def update_task_blueprint(self, blueprint_id: str, updates: dict[str, Any]) -> bool:
        """Updates an existing task blueprint using versioned append-only logic.

        Args:
            blueprint_id: The ID of the task blueprint to update.
            updates: A dictionary of key-value pairs to update.

        Returns:
            True if the update was successful, False if the document was not found.

        Raises:
            AppException: Propagated from driver if database operations fail.
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
        """Deletes a task blueprint by ID.

        Args:
            blueprint_id: The ID of the task blueprint to delete.

        Returns:
            True if successfully deleted, False if the document did not exist.

        Raises:
            AppException: Propagated from driver if database operations fail.
        """
        blueprint = await self.get_task_blueprint_by_id(blueprint_id)
        if not blueprint:
            return False
        return await self.driver.delete("task_blueprints", blueprint_id)
