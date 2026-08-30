"""Extracted Repository for Task Blueprints."""

import logging
from typing import Any

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.v2_core import Step

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

    async def get_task_blueprint_by_id(self, blueprint_id: str) -> Step | None:
        """Retrieves a task blueprint by its ID.

        Args:
            blueprint_id: The unique identifier of the task blueprint.

        Returns:
            The validated Step domain model if found, otherwise None.

        Raises:
            AppException: If parsing fails.
        """
        doc = await self.driver.get("task_blueprints", blueprint_id)
        if not doc:
            return None
        try:
            return Step.model_validate(doc, strict=False)
        except Exception as e:
            logger.error("Failed to parse Step blueprint %s: %s", blueprint_id, e, exc_info=True)
            raise AppException(
                message=f"Failed to parse task blueprint {blueprint_id} from database",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

    async def get_all_task_blueprints(self) -> list[Step]:
        """Retrieves all task blueprints from the database.

        Returns:
            A list of validated Step domain models.
        """
        data = await self.driver.query("task_blueprints")
        blueprints: list[Step] = []
        for b in data:
            try:
                blueprints.append(Step.model_validate(b, strict=False))
            except Exception as e:
                item_id = b["id"] if "id" in b else "unknown"
                logger.error("Failed to parse Step blueprint %s: %s", item_id, e, exc_info=True)
                raise AppException(
                    message=f"Failed to parse task blueprint {item_id} from database",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e
        return blueprints

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
        old_doc = await self.driver.get("task_blueprints", blueprint_id)
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
        blueprint = await self.driver.get("task_blueprints", blueprint_id)
        if not blueprint:
            return False
        return await self.driver.delete("task_blueprints", blueprint_id)
