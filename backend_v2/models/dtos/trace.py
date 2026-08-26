from typing import TYPE_CHECKING, Annotated, Any, Literal

from pydantic import ConfigDict, Field

from backend_v2.models.dtos.base import BaseDTO
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO
from backend_v2.models.enums import LaxExecutionStatus

if TYPE_CHECKING:
    from backend_v2.models.domain.metadata import StepMetadataDTO


class DataStarvationEvent(BaseDTO):
    """Strict domain event emitted when SynthesisEngine aborts due to atom starvation."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    event_type: Annotated[Literal["starvation"], Field(default="starvation", description="Event discriminator")] = (
        "starvation"
    )
    total_atoms: Annotated[int, Field(ge=0, description="Total raw atoms extracted before synthesis")]
    reason: Annotated[
        str, Field(default="Data starvation: insufficient atoms", description="Reason for short-circuit")
    ] = "Data starvation: insufficient atoms"


class TraceEventMetadataEnvelope(BaseDTO):
    """Strict hydration schema for extracting metadata from a trace event."""

    model_config = ConfigDict(strict=True, extra="forbid")

    step_metadata: Annotated[StepMetadataDTO | None, Field(alias="_step_metadata", default=None)]


class TraceMatrixExtensionsDTO(BaseDTO):
    """Strict schema for trace matrix extensions."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    coaching: Annotated[str | None, Field(default=None)] = None
    falsification: Annotated[str | None, Field(default=None)] = None
    remediation_steps: Annotated[str | None, Field(default=None)] = None
    missing_context: Annotated[str | None, Field(default=None)] = None
    emotional_sentiment: Annotated[str | None, Field(default=None)] = None
    theory_link: Annotated[str | None, Field(default=None)] = None
    risk_flag: Annotated[bool | None, Field(default=None)] = None
    confidence: Annotated[float | None, Field(default=None)] = None
    evidence_type: Annotated[str | None, Field(default=None)] = None
    source_id: Annotated[str | None, Field(default=None)] = None
    citation: Annotated[str | None, Field(default=None)] = None
    google_citation: Annotated[str | None, Field(default=None)] = None
    contextual_override: Annotated[bool | None, Field(default=None)] = None
    semantic_reasoning: Annotated[str | None, Field(default=None)] = None


class TraceMatrixPayloadDTO(BaseDTO):
    """Strict hydration schema for extracting matrix payloads from execution trace."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    raw_score: Annotated[float | None, Field(description="The raw score calculated")] = None
    normalized_score: Annotated[float | None, Field(description="The normalized score")] = None
    justification: Annotated[str | None, Field(description="The justification text")] = None
    level_breakdown: Annotated[dict[str, LevelStatsDTO] | None, Field(description="Breakdown of levels")] = None
    extensions: Annotated[TraceMatrixExtensionsDTO | None, Field(description="Additional extensions")] = None
    evaluated_atoms: Annotated[dict[str, LaxExecutionStatus] | None, Field(description="Evaluated atoms mapping")] = (
        None
    )
    xai_log: Annotated[dict[str, Any] | None, Field(description="XAI audit log")] = None
    allowed_extensions: Annotated[list[str] | None, Field(description="List of allowed extensions")] = None


class TraceScoringPayloadDTO(BaseDTO):
    """Strict hydration schema for extracting scoring results in BlueprintTransformer."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    total_score: Annotated[float | None, Field(description="The total score")] = None
    final_score: Annotated[float | None, Field(description="The final computed score")] = None
    normalized_score: Annotated[float | None, Field(description="The normalized score projection")] = None
    penalties_applied: Annotated[list[Any] | None, Field(description="List of applied penalties")] = None
    aggregation_status: Annotated[str | None, Field(description="Status of aggregation")] = None
