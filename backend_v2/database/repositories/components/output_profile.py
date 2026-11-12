"""Repository implementation for Output Profiles."""

from __future__ import annotations

from backend_v2.database.repositories.base import BaseRepository
from backend_v2.models.domain.output_profile import OutputProfile

__all__ = ["OutputProfileRepositoryImpl"]


class OutputProfileRepositoryImpl(BaseRepository):
    """Repository implementation for CRUD operations on OutputProfile entities."""

    async def get_all_output_profiles(self) -> list[OutputProfile]:
        """Retrieve all persisted output profiles.

        Returns:
            List of validated OutputProfile domain models.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on hydration/query failure.
        """
        async with self._acquire_entities() as entities:
            return await entities.list_output_profiles()

    async def get_all_output_profiles_models(self) -> list[OutputProfile]:
        """Retrieve all output profiles as validated domain models.

        Returns:
            List of validated OutputProfile domain models.
        """
        return await self.get_all_output_profiles()

    async def get_output_profile_by_id(self, profile_id: str) -> OutputProfile | None:
        """Retrieve an output profile by primary key ID.

        Args:
            profile_id: Canonical prof_<hex32> output profile identifier.

        Returns:
            Validated OutputProfile domain model if found, otherwise None.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on hydration/query failure.
        """
        async with self._acquire_entities() as entities:
            return await entities.get_output_profile(profile_id)

    async def create_output_profile(self, profile_data: OutputProfile) -> str:
        """Persist a new OutputProfile record.

        Args:
            profile_data: Validated OutputProfile domain model.

        Returns:
            Canonical prof_<hex32> identifier of the persisted output profile.

        Raises:
            AppException: With STORAGE_ACCESS_FAILED if persistence fails.
        """
        async with self._acquire_entities() as entities:
            return await entities.upsert_output_profile(profile_data)

    async def update_output_profile(self, profile_id: str, updates: OutputProfile) -> bool:
        """Update an existing OutputProfile record in-place.

        Args:
            profile_id: Canonical prof_<hex32> identifier of the output profile to update.
            updates: Validated OutputProfile domain model containing updated fields.

        Returns:
            True if updated, False if the output profile does not exist.

        Raises:
            AppException: With STORAGE_ACCESS_FAILED if persistence fails.
        """
        async with self._acquire_entities() as entities:
            existing = await entities.get_output_profile(profile_id)
            if existing is None:
                return False
            persisted = updates if updates.id == profile_id else updates.model_copy(update={"id": profile_id})
            await entities.upsert_output_profile(persisted)
            return True

    async def delete_output_profile(self, profile_id: str) -> bool:
        """Delete an OutputProfile record by ID.

        Args:
            profile_id: Canonical prof_<hex32> identifier of the output profile to delete.

        Returns:
            True if deleted, False if the output profile did not exist.

        Raises:
            AppException: With STORAGE_ACCESS_FAILED if deletion fails.
        """
        async with self._acquire_entities() as entities:
            return await entities.delete_output_profile(profile_id)
