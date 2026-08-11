"""Archival Domain Models.

This module defines the schemas for archival execution precedents.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase


class ArchivalPrecedentDTO(V2CoreBase):
    """Strict schema for a single retrieved execution precedent.

    Attributes:
        id: Opaque Stripe ID of the past execution.
        date: ISO formatted completion date.
        scores: Formatted string of judge scores.
        verdict: Truncated verdict from the execution.
    """
    model_config = ConfigDict(strict=True, extra="forbid")

    id: Annotated[str, Field(min_length=1, description="Opaque Stripe ID of the past execution.")]
    date: Annotated[str, Field(min_length=1, description="ISO formatted completion date.")]
    scores: Annotated[str, Field(min_length=1, description="Formatted string of judge scores.")]
    verdict: Annotated[str, Field(min_length=1, description="Truncated verdict from the execution.")]
