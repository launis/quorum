import logging
from typing import Any

from backend_v2.database.driver import Filter
from backend_v2.database.interfaces import IExtractionProtocolRepository
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase
from backend_v2.exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)


class ExtractionProtocolRepositoryImpl(AppendOnlyRepositoryBase, IExtractionProtocolRepository):
    """Repository implementation for Extraction Protocols."""

    async def get_all_extraction_protocols(self) -> list[dict[str, Any]]:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        filters = [Filter("type", "==", "extraction_protocol")]
        return await self.driver.query("components", filters)

    async def get_extraction_protocol_by_id(self, protocol_id: str) -> dict[str, Any] | None:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        return await self.driver.get("components", protocol_id)

    async def create_extraction_protocol(self, protocol_data: dict[str, Any]) -> str:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        doc_id = protocol_data["id"]
        protocol_data["type"] = "extraction_protocol"
        return await self.driver.upsert("components", protocol_data, doc_id)

    async def update_extraction_protocol(self, protocol_id: str, updates: dict[str, Any]) -> str:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        comp = await self.get_extraction_protocol_by_id(protocol_id)
        if not comp:
            raise ResourceNotFoundError(resource_type="ExtractionProtocol", resource_id=protocol_id)
        await self.driver.update("components", protocol_id, updates)
        return protocol_id

    async def delete_extraction_protocol(self, protocol_id: str) -> bool:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        comp = await self.get_extraction_protocol_by_id(protocol_id)
        if not comp:
            return False
        return await self.driver.delete("components", protocol_id)
