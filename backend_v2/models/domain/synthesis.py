"""Domain models for synthesis, multi-matrix grouping, and XAI extraction.

SSOT for SynthesisMetadataDTO, DistilledEvaluation, SynthesisStepDataDTO,
MatrixSynthesisGroup, RenderedSynthesisCache, BaseMatrixXAI, and BaseTDAExtraction.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Annotated, Any, Self

if TYPE_CHECKING:
    from backend_v2.models.dtos.base import DataStarvationEvent
    from backend_v2.models.view.sdui import AnySduiBlock

from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator, model_validator

from backend_v2.exceptions import ErrorCodes
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, I18nText, V2CoreBase
from backend_v2.models.domain.base import ReasoningTrace
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.atom_result import ExtensionMetricsDTO
from backend_v2.models.dtos.global_context import GlobalContextVarsDTO
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO
from backend_v2.models.dtos.quote_evidence import LLMExtractedQuote
from backend_v2.models.dtos.synthesis import XaiHighlightItem
from backend_v2.models.enums import LaxPresetView, PresetView

logger = logging.getLogger(__name__)

__all__ = [
    "BaseMatrixXAI",
    "BaseTDAExtraction",
    "DistilledEvaluation",
    "DistilledMatrixPayloadDTO",
    "MatrixSynthesisGroup",
    "RenderedSynthesisCache",
    "SynthesisMetadataDTO",
    "SynthesisStepDataDTO",
]


class BaseMatrixXAI(BaseModel):
    """Pydantic model for matrix XAI qualitative extensions without physical extraction guarantees."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    semantic_reasoning: str = Field(
        default="",
        description="Matrix-level assessment explanation.",
    )


class BaseTDAExtraction(BaseModel):
    """Core Pydantic model for Micro-CoT extraction with deterministic cross-validation."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    @field_validator("exact_quotes", mode="before")
    @classmethod
    def _coerce_exact_quotes(cls, v: Any) -> Any:
        if v is None:
            return []
        return v

    exact_quotes: list[LLMExtractedQuote] = Field(
        default_factory=list,
        max_length=3,
        description="List of verbatim quotes from original text.",
    )
    localized_anchors_found: list[str] = Field(
        max_length=15, description="Keywords in target language mapping English rule."
    )
    contextual_override: bool = Field(description="Escape hatch for implicit matches.")
    semantic_reasoning: str = Field(description="Mapping logic explanation in target language.")

    @model_validator(mode="after")
    def validate_override_logic(self) -> Self:
        """Validates the consistency of the extraction rules after typed hydration."""
        if self.contextual_override:
            if self.exact_quotes:
                raise ValueError("contextual_override=True cannot be combined with exact_quotes")
        else:
            for q in self.exact_quotes:
                if q.text == "[CONTEXTUAL_OVERRIDE_APPLIED]":
                    msg = (
                        "Cross-validation failed: exact_quotes cannot contain "
                        "'[CONTEXTUAL_OVERRIDE_APPLIED]' if contextual_override is False."
                    )
                    logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                    raise ValueError(msg)
        return self


class DistilledEvaluation(V2CoreBase):
    """Schema for distilled evaluation data used in synthesis."""

    model_config = ConfigDict(strict=True, extra="forbid")

    atom_id: Annotated[str | None, Field(default=None, description="Opaque atom identifier")] = None
    status: Annotated[
        str | None, Field(default=None, description="Evaluation status, specifically: PASSED, FAILED")
    ] = None
    exact_quotes: Annotated[list[str], Field(default_factory=list, description="Extracted verbatim quotes")]
    semantic_reasoning: Annotated[str | None, Field(default=None, description="Semantic reasoning for evaluation")] = (
        None
    )
    extensions: Annotated[
        dict[str, str | int | float | bool | list[str]] | None,
        Field(default=None, description="Qualitative evaluation extensions"),
    ] = None


class DistilledMatrixPayloadDTO(V2CoreBase):
    """Typed synthesis payload for distilled matrix evaluations."""

    model_config = ConfigDict(strict=True, extra="forbid")

    results: Annotated[list[DistilledEvaluation], Field(min_length=1, description="Stratified evaluations")]
    normalized_score: Annotated[float | None, Field(default=None, description="Normalized score (0-100)")] = None
    level_breakdown: Annotated[
        dict[str, LevelStatsDTO] | None,
        Field(default=None, description="Level statistics breakdown"),
    ] = None


class MatrixSynthesisGroup(V2CoreBase):
    """Represents a comparative matrix synthesis group for 2D/3D graphs and multi-matrix synthesis."""

    model_config = ConfigDict(strict=True, extra="forbid")

    id: str = Field(
        default_factory=lambda: f"grp_{uuid.uuid4().hex[:16]}",
        pattern=OPAQUE_STRIPE_ID_REGEX,
        description="Unique Opaque Synthesis Group ID (e.g. grp_440a5fef9331451b)",
    )
    title: I18nText = Field(description="Localized title for the synthesis group")
    target_blocks: list[str] = Field(min_length=1, description="List of prompt block IDs targeted by this group")
    view_type: LaxPresetView = Field(
        default=PresetView.METRICS_1D,
        description=(
            "UI presentation preset view for this matrix group (e.g. 1d_metrics, 2d_compare, 3d_matrix, text_only)."
        ),
    )

    @model_validator(mode="after")
    def validate_dimensional_cardinality(self) -> Self:
        """Enforce strict dimensional cardinality coupling between view_type and target_blocks."""
        num_blocks = len(self.target_blocks)
        if self.view_type == PresetView.METRICS_1D:
            if num_blocks != 1:
                msg = (
                    f"MatrixSynthesisGroup '{self.id}': view_type '1d_metrics' requires exactly 1 target block, "
                    f"but received {num_blocks} ({self.target_blocks})."
                )
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
        elif self.view_type == PresetView.COMPARE_2D:
            if num_blocks != 2:
                msg = (
                    f"MatrixSynthesisGroup '{self.id}': view_type '2d_compare' requires exactly 2 target blocks, "
                    f"but received {num_blocks} ({self.target_blocks})."
                )
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
        elif self.view_type == PresetView.MATRIX_3D:
            if num_blocks != 3:
                msg = (
                    f"MatrixSynthesisGroup '{self.id}': view_type '3d_matrix' requires exactly 3 target blocks, "
                    f"but received {num_blocks} ({self.target_blocks})."
                )
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
        elif self.view_type == PresetView.TEXT_ONLY:
            if num_blocks < 1:
                msg = (
                    f"MatrixSynthesisGroup '{self.id}': view_type 'text_only' requires at least 1 target block, "
                    f"but received {num_blocks}."
                )
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
        return self


class RenderedSynthesisCache(V2CoreBase):
    """Cached synthesis results tied to a specific OutputProfile ID."""

    model_config = ConfigDict(strict=True, extra="forbid")

    section_syntheses: dict[str, list[AnySduiBlock]] = Field(
        default_factory=dict, description="Mapping of layout ID to LLM generated Section-Level synthesis blocks"
    )
    row_explanations: dict[str, str] = Field(
        default_factory=dict, description="Synthesized row explanations by matrix ID"
    )
    row_curated_quotes: dict[str, list[str]] = Field(default_factory=dict, description="Curated quotes by matrix ID")
    variance_explanation: Annotated[
        str | None, Field(default=None, description="Synthesized cognitive-mechanical variance explanation")
    ] = None
    authenticity_explanation: Annotated[
        str | None, Field(default=None, description="Synthesized authenticity evaluation explanation")
    ] = None
    cited_sources: list[str] = Field(default_factory=list, description="Citations used in this profile's synthesis")
    xai_highlights: list[XaiHighlightItem] = Field(
        default_factory=list, description="Synthesized XAI highlights and tips"
    )
    user_role: str | None = Field(default=None, description="User role")
    user_role_justification: str | None = Field(default=None, description="User role justification")
    extension_metrics: ExtensionMetricsDTO | None = Field(
        default=None, description="Pre-calculated numeric or boolean metrics for UI adapters"
    )
    data_starvation: DataStarvationEvent | None = Field(
        default=None, description="Domain event indicating synthesis short-circuit due to atom starvation"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Import StepExecutionEnvelope and StepOutputDTO after RenderedSynthesisCache to break circular dependency with state.py
from backend_v2.models.dtos.step_output import StepOutputDTO
from backend_v2.models.state import StepExecutionEnvelope


class SynthesisMetadataDTO(V2CoreBase):
    """Strict schema for execution metadata used during synthesis."""

    model_config = ConfigDict(strict=True, extra="forbid")

    target_locale: Annotated[str, Field(min_length=1)]
    token_usage: Annotated[
        TokenUsage,
        Field(
            default_factory=lambda: TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
            description="Aggregated token usage across synthesis steps",
        ),
    ]
    step_results: Annotated[
        list[StepOutputDTO],
        Field(default_factory=list, description="List of step results evaluated during synthesis"),
    ]
    profile_id: Annotated[str | None, Field()] = None
    target_profile_id: Annotated[str | None, Field()] = None
    matrix_sampling_strategy: Annotated[int | None, Field()] = None
    workflow_version: Annotated[int | None, Field()] = None

    # Injected by worker.py during execution trace iterations for token usage tracking
    total_tokens: Annotated[int | None, Field()] = None
    prompt_tokens: Annotated[int | None, Field()] = None
    completion_tokens: Annotated[int | None, Field()] = None
    cost_estimate: Annotated[float | None, Field()] = None
    synthesis_cost_usd: Annotated[float | None, Field()] = None
    dag_cost_usd: Annotated[float | None, Field()] = None

    # Injected by System 2 Reliability Tracker in worker.py
    global_context_vars: Annotated[
        GlobalContextVarsDTO | None, Field(default=None, description="Global context variables")
    ] = None
    execution_summary: Annotated[dict[str, JsonValue] | None, Field(default=None, description="Execution summary")] = (
        None
    )
    step_metrics: Annotated[dict[str, JsonValue] | None, Field(default=None, description="Step metrics")] = None


class SynthesisStepDataDTO(StepExecutionEnvelope):
    """Schema to safely extract required synthesis flags from generic step outputs."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    reasoning_trace: Annotated[ReasoningTrace | None, Field()] = None
    token_usage: Annotated[
        TokenUsage,
        Field(
            default_factory=lambda: TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
            description="Step token usage",
        ),
    ]


from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.dtos.base import DataStarvationEvent
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO
from backend_v2.models.view.sdui import AnySduiBlock

RenderedSynthesisCache.model_rebuild(
    _types_namespace={
        "DataStarvationEvent": DataStarvationEvent,
        "AnySduiBlock": AnySduiBlock,
        "MatrixScorecardRowDTO": MatrixScorecardRowDTO,
        "MCPAuditTrace": MCPAuditTrace,
    }
)
