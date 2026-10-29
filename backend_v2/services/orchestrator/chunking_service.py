"""Service for splitting arrays of prompt blocks into deterministic chunks."""

from __future__ import annotations

import logging

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.chunking import Chunk, ChunkingRequest

logger = logging.getLogger(__name__)

__all__ = ["ChunkingService"]


class ChunkingService:
    """Isolated Chunking Service.

    Provides deterministic chunking of large arrays (Prompt Blocks/Atoms)
    into manageable sub-arrays tracked by Opaque Stripe IDs.
    Zero external dependencies, zero DB, zero LLM integration. T=0.0 pure deterministic logic.
    """

    @classmethod
    def chunk_payload[T](cls, request: ChunkingRequest[T]) -> list[Chunk[T]]:
        """Splits an array of items into N deterministic chunks.

        Args:
            request: The validated chunking request containing items and chunk parameters.

        Returns:
            List of chunk envelopes with generic item payloads.

        Raises:
            AppException: If items list is empty or max_chunk_size is not positive
                (ErrorCodes.VALIDATION_FAILED).
        """
        chunks: list[Chunk[T]] = []
        items = request.items
        n = request.max_chunk_size
        parent_id = request.parent_id

        if not items or n <= 0:
            msg = (
                f"Invalid chunking parameters: items count={len(items)}, "
                f"max_chunk_size={n}. Both must be strictly positive."
            )
            logger.error(
                "[ChunkingService] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={
                    "error_code": ErrorCodes.VALIDATION_FAILED.value,
                    "parent_id": parent_id,
                    "items_count": len(items),
                    "max_chunk_size": n,
                },
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=422,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        for index, i in enumerate(range(0, len(items), n)):
            chunk_items = items[i : i + n]

            chunk = Chunk[T](
                parent_id=parent_id,
                index=index,
                items=chunk_items,
            )
            chunks.append(chunk)

        return chunks
