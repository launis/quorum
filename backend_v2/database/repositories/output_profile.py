"""Extracted Repository."""

import logging
from typing import Any

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.output_profile import OutputProfile

logger = logging.getLogger(__name__)


class OutputProfileRepositoryImpl(AppendOnlyRepositoryBase):
    """OutputProfileRepositoryImpl implementation."""

    def __init__(self, driver: StorageDriver):
        super().__init__(driver)

    async def get_all_output_profiles(self) -> list[dict[str, Any]]:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        return await self.driver.query("output_profiles")

    async def get_all_output_profiles_models(self) -> list[OutputProfile]:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        data = await self.get_all_output_profiles()
        models = []
        for pd in data:
            try:
                models.append(OutputProfile.model_validate(pd, strict=False))
            except Exception as e:
                logger.error("Failed to parse OutputProfile %s: %s", pd.get("id"), e, exc_info=True)

                raise AppException(
                    message="Failed to parse profile from database",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e
        return models

    async def get_output_profile_by_id(self, profile_id: str) -> dict[str, Any] | None:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        return await self.driver.get("output_profiles", profile_id)

    async def create_output_profile(self, profile_data: dict[str, Any]) -> str:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        doc_id = profile_data["id"]
        return await self.driver.upsert("output_profiles", profile_data, doc_id)

    async def update_output_profile(self, profile_id: str, updates: dict[str, Any]) -> bool:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        return await self.driver.update("output_profiles", profile_id, updates)

    async def delete_output_profile(self, profile_id: str) -> bool:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        return await self.driver.delete("output_profiles", profile_id)
