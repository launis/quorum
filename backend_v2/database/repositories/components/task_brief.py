"""Repository implementation for reusable human-facing TaskBrief entities."""

from __future__ import annotations

import logging

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.task_brief import TaskBrief

logger = logging.getLogger(__name__)

__all__ = ["TaskBriefRepositoryImpl"]


class TaskBriefRepositoryImpl(AppendOnlyRepositoryBase):
    """Repository implementation for CRUD operations on TaskBrief records."""

    def __init__(self, driver: StorageDriver) -> None:
        """Initialize the repository with a storage driver.

        Args:
            driver: The underlying storage driver for database operations.
        """
        super().__init__(driver)

    async def get_all_task_briefs(self) -> list[TaskBrief]:
        """Retrieve all task briefs from the database.

        Returns:
            List of validated TaskBrief domain models.

        Raises:
            AppException: If the database query or model validation fails
                (ErrorCodes.VALIDATION_FAILED, ErrorCodes.STORAGE_ACCESS_FAILED).
        """
        data = await self.driver.query("task_briefs")
        models: list[TaskBrief] = []
        for raw in data:
            try:
                models.append(TaskBrief.model_validate(raw, strict=False))
            except Exception as exc:
                item_id = "unknown"
                if "id" in raw:
                    item_id = str(raw["id"])
                logger.error(
                    "[TaskBriefRepository] %s: Failed to parse TaskBrief %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    item_id,
                    exc,
                    exc_info=True,
                )
                raise AppException(
                    message=f"Failed to parse task brief {item_id} from database",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from exc
        return models

    async def get_task_brief_by_id(self, brief_id: str) -> TaskBrief | None:
        """Retrieve a task brief by its primary key ID in O(1) indexed time.

        Args:
            brief_id: Canonical tbr_<32_hex> task brief identifier.

        Returns:
            Validated TaskBrief domain model if found, otherwise None.

        Raises:
            AppException: If the database query or model validation fails
                (ErrorCodes.VALIDATION_FAILED, ErrorCodes.STORAGE_ACCESS_FAILED).
        """
        doc = await self.driver.get("task_briefs", brief_id)
        if not doc:
            return None
        try:
            return TaskBrief.model_validate(doc, strict=False)
        except Exception as exc:
            logger.error(
                "[TaskBriefRepository] %s: Failed to parse TaskBrief %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                brief_id,
                exc,
                exc_info=True,
            )
            raise AppException(
                message=f"Failed to parse task brief {brief_id} from database",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from exc

    async def create_task_brief(self, brief_data: TaskBrief) -> str:
        """Create or upsert a TaskBrief record.

        Args:
            brief_data: Validated TaskBrief domain model.

        Returns:
            Canonical tbr_<32_hex> identifier of the persisted task brief.

        Raises:
            AppException: Propagated from driver if the upsert operation fails
                (ErrorCodes.STORAGE_ACCESS_FAILED).
        """
        payload = brief_data.model_dump(mode="json")
        return await self.driver.upsert("task_briefs", payload, brief_data.id)

    async def update_task_brief(self, brief_id: str, updates: TaskBrief) -> bool:
        """Update an existing TaskBrief record.

        Args:
            brief_id: Canonical tbr_<32_hex> identifier of the task brief to update.
            updates: Validated TaskBrief domain model containing updated fields.

        Returns:
            True if the update was successful, False if the document was not found.

        Raises:
            AppException: Propagated from driver if database operations fail
                (ErrorCodes.STORAGE_ACCESS_FAILED).
        """
        old_doc = await self.driver.get("task_briefs", brief_id)
        if not old_doc:
            return False

        payload = updates.model_dump(mode="json", exclude_unset=True)
        await self.driver.update("task_briefs", brief_id, payload)
        return True

    async def delete_task_brief(self, brief_id: str) -> bool:
        """Delete a TaskBrief record by ID.

        Args:
            brief_id: Canonical tbr_<32_hex> identifier of the task brief to delete.

        Returns:
            True if successfully deleted, False if the document did not exist.

        Raises:
            AppException: Propagated from driver if database operations fail
                (ErrorCodes.STORAGE_ACCESS_FAILED).
        """
        existing = await self.driver.get("task_briefs", brief_id)
        if not existing:
            return False
        return await self.driver.delete("task_briefs", brief_id)
