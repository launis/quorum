from __future__ import annotations

from pydantic import Field

from backend_v2.models.core_base import V2CoreBase


class ArchivalPrecedentDTO(V2CoreBase):
    """Strict schema for a single retrieved execution precedent.

    Attributes:
        id: Opaque Stripe ID of the past execution.
        date: ISO formatted completion date.
        scores: Formatted string of judge scores.
        verdict: Truncated verdict from the execution.
    """

    id: str = Field(..., min_length=1, description="Opaque Stripe ID of the past execution.")
    date: str = Field(..., min_length=1, description="ISO formatted completion date.")
    scores: str = Field(..., min_length=1, description="Formatted string of judge scores.")
    verdict: str = Field(..., min_length=1, description="Truncated verdict from the execution.")
