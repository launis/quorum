"""Extracted Repository for Output Profiles."""

from __future__ import annotations

import logging

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.output_profile import OutputProfile

logger = logging.getLogger(__name__)


class OutputProfileRepositoryImpl(AppendOnlyRepositoryBase):
    """Implementation of the Output Profile Repository.

    This repository is responsible for CRUD operations on output profiles.
    """

    def __init__(self, driver: StorageDriver):
        """Initializes the repository with a storage driver.

        Args:
            driver: The underlying storage driver for database operations.
        """
        super().__init__(driver)

    async def get_all_output_profiles(self) -> list[OutputProfile]:
        """Retrieves all output profiles from the database.

        Returns:
            A list of validated OutputProfile domain models.

        Raises:
            AppException: If database query or model validation fails.
        """
        data = await self.driver.query("output_profiles")
        models: list[OutputProfile] = []
        for pd in data:
            try:
                models.append(OutputProfile.model_validate(pd, strict=False))
            except Exception as e:
                item_id = pd["id"] if "id" in pd else "unknown"
                logger.error("Failed to parse OutputProfile %s: %s", item_id, e, exc_info=True)
                raise AppException(
                    message=f"Failed to parse profile {item_id} from database",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e
        return models

    async def get_all_output_profiles_models(self) -> list[OutputProfile]:
        """Retrieves all output profiles and maps them to Pydantic models.

        Returns:
            A list of OutputProfile models.
        """
        return await self.get_all_output_profiles()

    async def get_output_profile_by_id(self, profile_id: str) -> OutputProfile | None:
        """Retrieves an output profile by its ID.

        Args:
            profile_id: The unique identifier of the output profile.

        Returns:
            The validated OutputProfile domain model if found, otherwise None.

        Raises:
            AppException: If database query or parsing fails.
        """
        doc = await self.driver.get("output_profiles", profile_id)
        if not doc:
            return None
        try:
            return OutputProfile.model_validate(doc, strict=False)
        except Exception as e:
            logger.error("Failed to parse OutputProfile %s: %s", profile_id, e, exc_info=True)
            raise AppException(
                message=f"Failed to parse profile {profile_id} from database",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

    async def create_output_profile(self, profile_data: OutputProfile) -> str:
        """Creates a new output profile.

        Args:
            profile_data: The OutputProfile domain model.

        Returns:
            The ID of the created output profile.

        Raises:
            AppException: Propagated from driver if the upsert operation fails.
        """
        payload = profile_data.model_dump(mode="json")
        doc_id = payload["id"]
        return await self.driver.upsert("output_profiles", payload, doc_id)

    async def update_output_profile(self, profile_id: str, updates: OutputProfile) -> bool:
        """Updates an existing output profile.

        Args:
            profile_id: The ID of the output profile to update.
            updates: The OutputProfile domain model containing updated fields.

        Returns:
            True if the update was successful, False if the document was not found.

        Raises:
            AppException: Propagated from driver if database operations fail.
        """
        old_doc = await self.driver.get("output_profiles", profile_id)
        if not old_doc:
            return False

        payload = updates.model_dump(mode="json", exclude_unset=True)
        await self.driver.update("output_profiles", profile_id, payload)
        return True

    async def delete_output_profile(self, profile_id: str) -> bool:
        """Deletes an output profile by ID.

        Args:
            profile_id: The ID of the output profile to delete.

        Returns:
            True if successfully deleted, False if the document did not exist.

        Raises:
            AppException: Propagated from driver if database operations fail.
        """
        profile = await self.driver.get("output_profiles", profile_id)
        if not profile:
            return False
        return await self.driver.delete("output_profiles", profile_id)
