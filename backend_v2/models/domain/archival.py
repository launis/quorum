"""Archival Domain Models.

Provides strict Pydantic V2 validation schemas for the archival hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

from pydantic import BaseModel, ConfigDict, Field


class ArchivalPrecedentDTO(BaseModel):
    """Strict schema for a single retrieved execution precedent."""

    id: str = Field(description="Opaque Stripe ID of the past execution.")
    date: str = Field(description="ISO formatted completion date.")
    scores: str = Field(description="Formatted string of judge scores.")
    verdict: str = Field(description="Truncated verdict from the execution.")

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
