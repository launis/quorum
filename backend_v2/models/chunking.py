import logging
import uuid

from pydantic import Field, field_validator

from backend_v2.exceptions import ErrorCodes
from backend_v2.models.core_base import V2CoreBase

logger = logging.getLogger(__name__)


class Chunk[T](V2CoreBase):
    """Represents a chunk of a larger array, tracked by an Opaque Stripe ID."""

    id: str = Field(
        default_factory=lambda: f"chk_{uuid.uuid4().hex[:12]}",
        pattern=r"^chk_[a-zA-Z0-9]+$",
        description="Opaque Stripe ID for the chunk",
    )
    parent_id: str | None = Field(
        default=None,
        description="Optional Opaque Stripe ID of the parent sequence",
    )
    index: int = Field(
        ...,
        ge=0,
        description="The sequence order index of this chunk.",
    )
    items: list[T] = Field(
        ...,
        description="The actual chunked payload elements.",
    )


class ChunkingRequest[T](V2CoreBase):
    """Payload to request chunking operation."""

    parent_id: str | None = Field(
        default=None,
        description="Optional Opaque Stripe ID of the parent sequence",
    )
    items: list[T] = Field(
        ...,
        description="The payload elements to chunk.",
    )
    max_chunk_size: int = Field(
        ...,
        gt=0,
        description="Maximum number of items per chunk.",
    )

    @field_validator("items")
    @classmethod
    def validate_items_not_empty(cls, v: list[T]) -> list[T]:
        if not v:
            msg = "Cannot chunk an empty list. Items must contain at least one element."
            logger.error("[Chunking] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise ValueError(msg)
        return v
