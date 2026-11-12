"""Repository implementation for reusable human-facing TaskBrief entities."""

from __future__ import annotations

from backend_v2.database.repositories.base import BaseRepository
from backend_v2.models.domain.task_brief import TaskBrief

__all__ = ["TaskBriefRepositoryImpl"]


class TaskBriefRepositoryImpl(BaseRepository):
    """Repository implementation for CRUD operations on TaskBrief records."""

    async def get_all_task_briefs(self) -> list[TaskBrief]:
        """Retrieve all task briefs from PostgreSQL 19.

        Returns:
            List of validated TaskBrief domain models.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on hydration/query failure.
        """
        async with self._acquire_entities() as entities:
            return await entities.list_task_briefs()

    async def get_task_brief_by_id(self, brief_id: str) -> TaskBrief | None:
        """Retrieve a task brief by its primary key ID in O(1) indexed time.

        Args:
            brief_id: Canonical tbr_<hex32> task brief identifier.

        Returns:
            Validated TaskBrief domain model if found, otherwise None.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on hydration/query failure.
        """
        async with self._acquire_entities() as entities:
            return await entities.get_task_brief(brief_id)

    async def create_task_brief(self, brief_data: TaskBrief) -> str:
        """Create or upsert a TaskBrief record.

        Args:
            brief_data: Validated TaskBrief domain model.

        Returns:
            Canonical tbr_<hex32> identifier of the persisted task brief.

        Raises:
            AppException: With STORAGE_ACCESS_FAILED if persistence fails.
        """
        async with self._acquire_entities() as entities:
            return await entities.upsert_task_brief(brief_data)

    async def update_task_brief(self, brief_id: str, updates: TaskBrief) -> bool:
        """Update an existing TaskBrief record in-place.

        Args:
            brief_id: Canonical tbr_<hex32> identifier of the task brief to update.
            updates: Validated TaskBrief domain model containing updated fields.

        Returns:
            True if updated, False if the task brief does not exist.

        Raises:
            AppException: With STORAGE_ACCESS_FAILED if persistence fails.
        """
        async with self._acquire_entities() as entities:
            existing = await entities.get_task_brief(brief_id)
            if existing is None:
                return False
            persisted = updates if updates.id == brief_id else updates.model_copy(update={"id": brief_id})
            await entities.upsert_task_brief(persisted)
            return True

    async def delete_task_brief(self, brief_id: str) -> bool:
        """Delete a TaskBrief record by ID.

        Args:
            brief_id: Canonical tbr_<hex32> identifier of the task brief to delete.

        Returns:
            True if deleted, False if the task brief did not exist.

        Raises:
            AppException: With STORAGE_ACCESS_FAILED if deletion fails.
        """
        async with self._acquire_entities() as entities:
            return await entities.delete_task_brief(brief_id)
