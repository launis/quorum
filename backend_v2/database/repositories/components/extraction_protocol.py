"""Extracted Repository for Extraction Protocols."""

import logging
from typing import Any

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase
from backend_v2.exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)


class ExtractionProtocolRepositoryImpl(AppendOnlyRepositoryBase):
    """Repository implementation for Extraction Protocols."""

    async def get_all_extraction_protocols(self) -> list[dict[str, Any]]:
        """Retrieves all extraction protocols from the database.

        Returns:
            List of extraction protocol dictionaries.
        """
        filters = [Filter("type", "==", "extraction_protocol")]
        return await self.driver.query("components", filters)

    async def get_extraction_protocol_by_id(self, protocol_id: str) -> dict[str, Any] | None:
        """Retrieves an extraction protocol by its ID.

        Args:
            protocol_id: Unique identifier for the extraction protocol.

        Returns:
            The extraction protocol dictionary if found, otherwise None.
        """
        return await self.driver.get("components", protocol_id)

    async def create_extraction_protocol(self, protocol_data: dict[str, Any]) -> str:
        """Creates a new extraction protocol.

        Args:
            protocol_data: Dictionary containing extraction protocol fields.

        Returns:
            The created protocol ID.
        """
        doc_id = protocol_data["id"]
        protocol_data["type"] = "extraction_protocol"
        return await self.driver.upsert("components", protocol_data, doc_id)

    async def update_extraction_protocol(self, protocol_id: str, updates: dict[str, Any]) -> str:
        """Updates an existing extraction protocol.

        Args:
            protocol_id: Unique identifier for the extraction protocol.
            updates: Dictionary of fields to update.

        Returns:
            The updated protocol ID.

        Raises:
            ResourceNotFoundError: If the protocol does not exist.
        """
        comp = await self.get_extraction_protocol_by_id(protocol_id)
        if not comp:
            raise ResourceNotFoundError(resource_type="ExtractionProtocol", resource_id=protocol_id)
        await self.driver.update("components", protocol_id, updates)
        return protocol_id

    async def delete_extraction_protocol(self, protocol_id: str) -> bool:
        """Deletes an extraction protocol by ID.

        Args:
            protocol_id: Unique identifier for the extraction protocol.

        Returns:
            True if deleted, False if protocol does not exist.
        """
        comp = await self.get_extraction_protocol_by_id(protocol_id)
        if not comp:
            return False
        return await self.driver.delete("components", protocol_id)
