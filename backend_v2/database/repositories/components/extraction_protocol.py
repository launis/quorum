"""Extracted Repository for Extraction Protocols."""

from __future__ import annotations

import logging

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.domain.prompt_blocks import PromptBlock, PromptBlockAdapter

logger = logging.getLogger(__name__)


class ExtractionProtocolRepositoryImpl(AppendOnlyRepositoryBase):
    """Repository implementation for Extraction Protocols."""

    async def get_all_extraction_protocols(self) -> list[PromptBlock]:
        """Retrieves all extraction protocols from the database.

        Returns:
            List of extraction protocol PromptBlock models.
        """
        filters = [Filter("type", "==", "extraction_protocol")]
        raw_items = await self.driver.query("components", filters)
        protocols: list[PromptBlock] = []
        for item in raw_items:
            try:
                protocols.append(PromptBlockAdapter.validate_python(item, strict=False))
            except Exception as e:
                item_id = item["id"] if "id" in item else "unknown"
                logger.error("Failed to parse ExtractionProtocol %s: %s", item_id, e, exc_info=True)
                raise AppException(
                    message=f"Failed to parse ExtractionProtocol {item_id} from database",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e
        return protocols

    async def get_extraction_protocol_by_id(self, protocol_id: str) -> PromptBlock | None:
        """Retrieves an extraction protocol by its ID.

        Args:
            protocol_id: Unique identifier for the extraction protocol.

        Returns:
            The extraction protocol PromptBlock if found, otherwise None.
        """
        doc = await self.driver.get("components", protocol_id)
        if not doc:
            return None
        try:
            return PromptBlockAdapter.validate_python(doc, strict=False)
        except Exception as e:
            logger.error("Failed to parse ExtractionProtocol %s: %s", protocol_id, e, exc_info=True)
            raise AppException(
                message=f"Failed to parse ExtractionProtocol {protocol_id} from database",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

    async def create_extraction_protocol(self, protocol_data: PromptBlock) -> str:
        """Creates a new extraction protocol.

        Args:
            protocol_data: PromptBlock containing extraction protocol fields.

        Returns:
            The created protocol ID.
        """
        payload = protocol_data.model_dump(mode="json")
        doc_id = payload["id"]
        payload["type"] = "extraction_protocol"
        return await self.driver.upsert("components", payload, doc_id)

    async def update_extraction_protocol(self, protocol_id: str, updates: PromptBlock) -> str:
        """Updates an existing extraction protocol.

        Args:
            protocol_id: Unique identifier for the extraction protocol.
            updates: PromptBlock containing fields to update.

        Returns:
            The updated protocol ID.

        Raises:
            ResourceNotFoundError: If the protocol does not exist.
        """
        comp = await self.get_extraction_protocol_by_id(protocol_id)
        if not comp:
            raise ResourceNotFoundError(resource_type="ExtractionProtocol", resource_id=protocol_id)
        payload = updates.model_dump(mode="json", exclude_unset=True)
        await self.driver.update("components", protocol_id, payload)
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
