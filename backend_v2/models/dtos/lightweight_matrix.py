from typing import Annotated, Any

from pydantic import ConfigDict, Field, field_validator

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.enums import LaxExecutionStatus, LaxXaiExtensionType


class OutputProfileConfig(V2CoreBase):
    """Configuration for Output Profile extensions.

    Attributes:
        visible_block_extensions: List of extensions enabled at the block level.
        visible_workflow_extensions: List of extensions enabled globally across the workflow.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    visible_block_extensions: list[LaxXaiExtensionType]
    visible_workflow_extensions: list[LaxXaiExtensionType]


class XAILogDto(V2CoreBase):
    """Structured XAI Log separating UI-facing translations from mathematical traces.

    Attributes:
        pedagogical_key: The designated mapping key for UI-facing explanations.
        engine_debug_trace: System dictionary containing mathematical/diagnostic reasoning.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    pedagogical_key: str
    engine_debug_trace: Annotated[dict[str, Any], Field(default_factory=dict)]


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
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    raw_score: float | None = None
    normalized_score: float | None = None
    level_breakdown: dict[str, dict[str, int]] | None = None
    justification: str = ""
    xai_log: XAILogDto | None = None
    evaluated_atoms: Annotated[dict[str, LaxExecutionStatus], Field(default_factory=dict)]
    extensions: Annotated[dict[LaxXaiExtensionType, Any], Field(default_factory=dict)]
    allowed_extensions: list[LaxXaiExtensionType] | None = None

    @field_validator("normalized_score")
    @classmethod
    def _validate_normalized_score(cls, v: float | None) -> float | None:
        if v is not None and not (0.0 <= v <= 100.0):
            raise ValueError("normalized_score must be between 0.0 and 100.0")
        return v


class LevelStatsDTO(V2CoreBase):
    """Strict execution stats per scale level (Phase 1, Step 1: Define DTO).

    Attributes:
        hits: Number of passing criteria at this level.
        total: Total number of criteria at this level.
        dlqs: Number of items that hit the dead letter queue (defaults to 0).
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    hits: int | float
    total: int | float
    dlqs: int = 0


class MergedFactsDTO(V2CoreBase):
    """Holds global aggregation results safely with ConfigDict(strict=True, extra="forbid").

    Attributes:
        model_config: Pydantic configuration allowing extra attributes.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
