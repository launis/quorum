from __future__ import annotations

"""Variance DTOs for Mechanical-Cognitive Variance Validation."""

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.dtos.base import BaseDTO
from backend_v2.models.enums import AlignmentVerdict

__all__ = [
    "VarianceEngineResultDTO",
]


class VarianceEngineResultDTO(BaseDTO):
    """Result of mechanical-cognitive variance calculation.

    Attributes:
        mechanical_metric_ref: Reference key of the mechanical metric.
        cognitive_metric_ref: Reference key of the cognitive metric.
        variance_score: Absolute variance score between mechanical and cognitive metrics.
        alignment_verdict: Verdict describing the alignment state.
    """

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="forbid", frozen=True)

    mechanical_metric_ref: Annotated[str, Field(description="Reference key of the mechanical metric.")]
    cognitive_metric_ref: Annotated[str, Field(description="Reference key of the cognitive metric.")]
    variance_score: Annotated[
        float,
        Field(ge=0.0, description="Absolute variance score between mechanical and cognitive metrics."),
    ]
    alignment_verdict: Annotated[
        AlignmentVerdict,
        Field(description="Verdict describing the alignment state."),
    ]
