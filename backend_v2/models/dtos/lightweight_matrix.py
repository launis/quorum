"""Lightweight matrix output and scoring result DTOs.

Defines schemas for matrix scoring outputs, level statistics, and XAI logs.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import ConfigDict, Field, JsonValue, field_validator

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.enums import LaxExecutionStatus, LaxXaiExtensionType

__all__ = [
    "LevelStatsDTO",
    "LightweightMatrixOutput",
    "MergedFactsDTO",
    "OutputProfileConfig",
    "ScoringResultDTO",
    "XAILogDto",
]


class OutputProfileConfig(V2CoreBase):
    """Configuration for Output Profile extensions.

    Attributes:
        visible_block_extensions: List of extensions enabled at the block level.
        visible_workflow_extensions: List of extensions enabled globally across the workflow.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    visible_block_extensions: Annotated[
        list[LaxXaiExtensionType], Field(description="List of extensions enabled at the block level")
    ]
    visible_workflow_extensions: Annotated[
        list[LaxXaiExtensionType], Field(description="List of extensions enabled globally across the workflow")
    ]


class XAILogDto(V2CoreBase):
    """Structured XAI Log separating UI-facing translations from mathematical traces.

    Attributes:
        pedagogical_key: The designated mapping key for UI-facing explanations.
        engine_debug_trace: System dictionary containing mathematical/diagnostic reasoning.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    pedagogical_key: Annotated[str, Field(description="The designated mapping key for UI-facing explanations")]
    engine_debug_trace: Annotated[
        dict[str, JsonValue],
        Field(default_factory=dict, description="System dictionary containing mathematical/diagnostic reasoning"),
    ]


class LevelStatsDTO(V2CoreBase):
    """Strict execution stats per scale level.

    Attributes:
        hits: Number of passing criteria at this level.
        total: Total number of criteria at this level.
        dlqs: Number of items that hit the dead letter queue (defaults to 0).
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    hits: Annotated[int | float, Field(description="Number of passing criteria at this level")]
    total: Annotated[int | float, Field(description="Total number of criteria at this level")]
    dlqs: Annotated[int, Field(default=0, description="Number of items that hit the dead letter queue")] = 0


class LightweightMatrixOutput(V2CoreBase):
    """Strict schema for the Lightweight Matrix Output.

    Attributes:
        raw_score: Original unnormalized float evaluation score.
        normalized_score: Final scaled score ranging from 0.0 to 100.0.
        level_breakdown: Complex dictionary mapping multi-tier performance indicators.
        justification: Primary text string explaining the dimension result.
        xai_log: Nested logging details isolating debugging data.
        evaluated_atoms: Mapping tracking which structural logic atoms were hit.
        extensions: Arbitrarily mapped XAI extensions dict for UI components.
        allowed_extensions: Explicit list restricting dynamic schema mappings.
        atom_quotes: Atom quotes list if provided.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    raw_score: Annotated[
        float | None, Field(default=None, description="Original unnormalized float evaluation score")
    ] = None
    normalized_score: Annotated[
        float | None, Field(default=None, description="Final scaled score ranging from 0.0 to 100.0")
    ] = None
    level_breakdown: Annotated[
        dict[str, LevelStatsDTO] | None,
        Field(default=None, description="Complex dictionary mapping multi-tier performance indicators"),
    ] = None
    justification: Annotated[
        str, Field(default="", description="Primary text string explaining the dimension result")
    ] = ""
    xai_log: Annotated[
        XAILogDto | None, Field(default=None, description="Nested logging details isolating debugging data")
    ] = None
    evaluated_atoms: Annotated[
        dict[str, LaxExecutionStatus],
        Field(default_factory=dict, description="Mapping tracking which structural logic atoms were hit"),
    ]
    extensions: Annotated[
        dict[LaxXaiExtensionType, JsonValue],
        Field(default_factory=dict, description="Arbitrarily mapped XAI extensions dict for UI components"),
    ]
    allowed_extensions: Annotated[
        list[LaxXaiExtensionType] | None,
        Field(default=None, description="Explicit list restricting dynamic schema mappings"),
    ] = None
    atom_quotes: Annotated[
        list[str] | None, Field(default=None, description="Atom quotes list if provided")
    ] = None

    @field_validator("normalized_score")
    @classmethod
    def _validate_normalized_score(cls, v: float | None) -> float | None:
        if v is not None and not (0.0 <= v <= 100.0):
            raise ValueError("normalized_score must be between 0.0 and 100.0")
        return v


class MergedFactsDTO(V2CoreBase):
    """Holds global aggregation results safely with ConfigDict(strict=True, extra="forbid").

    Attributes:
        model_config: Pydantic configuration allowing extra attributes.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


class ScoringResultDTO(V2CoreBase):
    """Encapsulates the typed output of a matrix scoring calculation.

    Attributes:
        score: The calculated raw score mapped between math_min and math_max.
        xai_log: Structured XAI trace and pedagogical key.
        breakdown: Level breakdown dictionary mapping levels to metric counts.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    score: Annotated[float, Field(description="The calculated raw score mapped between math_min and math_max")]
    xai_log: Annotated[XAILogDto, Field(description="Structured XAI trace and pedagogical key")]
    breakdown: Annotated[
        dict[str, LevelStatsDTO], Field(description="Level breakdown dictionary mapping levels to metric counts")
    ]
