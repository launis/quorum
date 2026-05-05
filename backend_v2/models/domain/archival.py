"""Archival Domain Models.

Provides strict Pydantic V2 validation schemas for the archival hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

from pydantic import Field

from backend_v2.models.core_base import V2CoreBase


class ArchivalPrecedentDTO(V2CoreBase):
    """Strict schema for a single retrieved execution precedent."""

    id: str = Field(..., min_length=1, description="Opaque Stripe ID of the past execution.")
    date: str = Field(..., min_length=1, description="ISO formatted completion date.")
    scores: str = Field(..., min_length=1, description="Formatted string of judge scores.")
    verdict: str = Field(..., min_length=1, description="Truncated verdict from the execution.")
