"""Chunking Models.

This module defines models for chunking and splitting large data payloads
across the execution lifecycle to stay within rate limits.
"""

from __future__ import annotations

import logging
import uuid
from typing import Annotated

from pydantic import ConfigDict, Field, field_validator

from backend_v2.exceptions import ErrorCodes
from backend_v2.models.core_base import V2CoreBase

logger = logging.getLogger(__name__)

__all__ = [
    "Chunk",
    "ChunkingRequest",
]


class Chunk[T](V2CoreBase):
    """Represents a chunk of a larger array, tracked by an Opaque Stripe ID.

    Attributes:
        id (str): Opaque Stripe ID for the chunk.
        parent_id (Optional[str]): Optional Opaque Stripe ID of the parent sequence.
        index (int): The sequence order index of this chunk.
        items (list[T]): The actual chunked payload elements.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[
        str,
        Field(
            default_factory=lambda: f"chk_{uuid.uuid4().hex[:12]}",
            pattern=r"^chk_[a-zA-Z0-9]+$",
            description="Opaque Stripe ID for the chunk",
        ),
    ]
    parent_id: Annotated[
        str | None,
        Field(
            default=None,
            description="Optional Opaque Stripe ID of the parent sequence",
        ),
    ] = None
    index: Annotated[
        int,
        Field(
            ge=0,
            description="The sequence order index of this chunk.",
        ),
    ]
    items: Annotated[
        list[T],
        Field(
            description="The actual chunked payload elements.",
        ),
    ]


class ChunkingRequest[T](V2CoreBase):
    """Payload to request chunking operation.

    Attributes:
        parent_id (Optional[str]): Optional Opaque Stripe ID of the parent sequence.
        items (list[T]): The payload elements to chunk.
        max_chunk_size (int): Maximum number of items per chunk.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    parent_id: Annotated[
        str | None,
        Field(
            default=None,
            description="Optional Opaque Stripe ID of the parent sequence",
        ),
    ] = None
    items: Annotated[
        list[T],
        Field(
            description="The payload elements to chunk.",
        ),
    ]
    max_chunk_size: Annotated[
        int,
        Field(
            gt=0,
            description="Maximum number of items per chunk.",
        ),
    ]

    @field_validator("items")
    @classmethod
    def validate_items_not_empty(cls, v: list[T]) -> list[T]:
        """Validates that items list is not empty.

        Args:
            v: Input list of items.

        Returns:
            list[T]: Validated list.

        Raises:
            ValueError: If list is empty.
        """
        if not v:
            msg = "Cannot chunk an empty list. Items must contain at least one element."
            logger.error("[Chunking] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)
        return v
