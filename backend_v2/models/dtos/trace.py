from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Annotated, Any

from pydantic import ConfigDict, Field

from backend_v2.models.dtos.base import BaseDTO, DataStarvationEvent
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO
from backend_v2.models.enums import LaxExecutionStatus
from backend_v2.models.execution_core import ExecutionMetadata

if TYPE_CHECKING:
    from backend_v2.models.domain.inputs import WorkflowInputsIngress
    from backend_v2.models.domain.usage import TokenUsage
    from backend_v2.models.state import ErrorTraceEvent, TombstoneEvent, TraceEvent
    from backend_v2.models.v2_core import (
        ExecutionStep,
        ExecutionStepState,
        ExecutionSummarySnapshot,
        FrozenContext,
        RenderedSynthesisCache,
    )

__all__ = [
    "DataStarvationEvent",
    "StepTraceMetadataDTO",
    "TraceEventMetadataEnvelope",
    "TraceMatrixExtensionsDTO",
    "TraceMatrixPayloadDTO",
    "TraceScoringPayloadDTO",
    "ExecutionCreateDTO",
    "ExecutionUpdateDTO",
]


class ExecutionCreateDTO(BaseDTO):
    """DTO for creating a new execution record at ingress boundary."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    workflow_id: Annotated[str, Field(min_length=1, description="Target workflow ID")]
    id: Annotated[str | None, Field(default=None, description="Optional execution ID")] = None
    target_locale: Annotated[str, Field(default="fi", description="Target locale code")] = "fi"
    status: Annotated[str, Field(default="PENDING", description="Initial lifecycle status")] = "PENDING"
    active_profile_id: Annotated[str | None, Field(default=None, description="Active profile ID")] = None
    output_profile_id: Annotated[str, Field(min_length=1, description="Target profile ID")]
    raw_inputs: Annotated[WorkflowInputsIngress | None, Field(default=None, description="Raw workflow inputs")] = None
    organization_id: Annotated[str | None, Field(default=None, description="Organization ID")] = None
    created_by: Annotated[str | None, Field(default=None, description="Creator user ID")] = None
    metadata: Annotated[ExecutionMetadata | None, Field(default=None, description="Typed metadata SSOT")] = None


class ExecutionUpdateDTO(BaseDTO):
    """Single Source of Truth (SSOT) DTO for partial execution updates."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    status: Annotated[LaxExecutionStatus | None, Field(default=None, description="Lifecycle status")] = None
    current_step: Annotated[str | None, Field(default=None, description="Current progress activity description")] = None
    current_step_name: Annotated[str | None, Field(default=None, description="Current step name")] = None
    progress: Annotated[int | None, Field(default=None, ge=0, le=100, description="Completion percentage 0-100")] = None
    error: Annotated[str | None, Field(default=None, description="Failure error message")] = None
    steps: Annotated[list[ExecutionStep] | None, Field(default=None, description="DAG steps list (SSOT)")] = None
    step_states: Annotated[
        dict[str, ExecutionStepState] | None, Field(default=None, description="DAG step states mapping")
    ] = None
    execution_trace: Annotated[
        list[ErrorTraceEvent | TombstoneEvent | TraceEvent] | None,
        Field(default=None, description="Execution trace events"),
    ] = None
    frozen_context: Annotated[FrozenContext | None, Field(default=None, description="Frozen context snapshot")] = None
    profile_syntheses: Annotated[
        dict[str, RenderedSynthesisCache] | None, Field(default=None, description="Rendered synthesis cache (SSOT)")
    ] = None
    pdf_report_path: Annotated[str | None, Field(default=None, description="Generated PDF report path")] = None
    active_profile_id: Annotated[str | None, Field(default=None, description="Active profile ID")] = None
    output_profile_id: Annotated[str | None, Field(default=None, description="Target profile ID")] = None
    metadata: Annotated[ExecutionMetadata | None, Field(default=None, description="Execution metadata SSOT")] = None
    context_variables: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Dynamic blackboard dictionary"),
    ] = None
    is_resumable: Annotated[bool | None, Field(default=None, description="Resumable execution flag")] = None
    prompt_tokens: Annotated[int | None, Field(default=None, ge=0, description="Total prompt tokens")] = None
    completion_tokens: Annotated[int | None, Field(default=None, ge=0, description="Total completion tokens")] = None
    cached_tokens: Annotated[int | None, Field(default=None, ge=0, description="Total cached tokens")] = None
    reasoning_tokens: Annotated[int | None, Field(default=None, ge=0, description="Total reasoning tokens")] = None
    cumulative_synthesis_tokens: Annotated[
        int | None, Field(default=None, ge=0, description="Cumulative synthesis tokens")
    ] = None
    dag_cost_usd: Annotated[
        float | None, Field(default=None, ge=0.0, description="Total DAG execution cost in USD")
    ] = None
    cumulative_synthesis_cost: Annotated[
        float | None, Field(default=None, ge=0.0, description="Cumulative synthesis cost in USD")
    ] = None
    duration_ms: Annotated[int | None, Field(default=None, ge=0, description="Duration in milliseconds")] = None
    cost_estimate: Annotated[float | None, Field(default=None, ge=0.0, description="Estimated cost in USD")] = None
    models_used: Annotated[dict[str, int] | None, Field(default=None, description="Models token usage summary")] = None
    execution_summary: Annotated[
        ExecutionSummarySnapshot | None,
        Field(default=None, description="Typed non-FinOps execution telemetry snapshot"),
    ] = None
    created_at: Annotated[datetime | None, Field(default=None, description="Creation timestamp")] = None
    updated_at: Annotated[datetime | None, Field(default=None, description="Update timestamp")] = None
    completed_at: Annotated[datetime | None, Field(default=None, description="Completion timestamp")] = None


class StepTraceMetadataDTO(BaseDTO):
    """Strictly typed trace metadata for DAG steps including telemetry."""

    model_config = ConfigDict(strict=True, extra="forbid")

    task_blueprint: Annotated[str | None, Field(default=None)] = None
    model_strategy: Annotated[str, Field(default="unknown")] = "unknown"
    physical_model: Annotated[str | None, Field(default=None, description="Exact physical provider model string")] = (
        None
    )
    system_fingerprint: Annotated[str | None, Field(default=None, description="Provider system fingerprint")] = None
    chunk_size: Annotated[int, Field(default=1)] = 1
    token_usage: Annotated[
        TokenUsage | None,
        Field(
            default=None,
            description="Token usage statistics.",
        ),
    ] = None
    execution_id: Annotated[str | None, Field(default=None)] = None
    workflow_id: Annotated[str | None, Field(default=None)] = None
    step_id: Annotated[str | None, Field(default=None)] = None
    initiator_id: Annotated[str | None, Field(default=None)] = None
    timestamp_isot: Annotated[str | None, Field(default=None)] = None
    unix_time: Annotated[int | None, Field(default=None)] = None
    v2_engine: Annotated[bool | None, Field(default=None)] = None


class TraceEventMetadataEnvelope(BaseDTO):
    """Strict hydration schema for extracting metadata from a trace event."""

    model_config = ConfigDict(strict=True, extra="forbid")

    step_metadata: Annotated[StepTraceMetadataDTO | None, Field(alias="_step_metadata", default=None)]


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
    xai_log: Annotated[
        dict[str, str | int | float | bool | list[str]] | None,
        Field(default=None, description="Typed XAI audit log scalar metadata"),
    ] = None
    allowed_extensions: Annotated[list[str] | None, Field(description="List of allowed extensions")] = None


class TraceScoringPayloadDTO(BaseDTO):
    """Strict hydration schema for extracting scoring results in BlueprintTransformer."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    total_score: Annotated[float | None, Field(description="The total score")] = None
    final_score: Annotated[float | None, Field(description="The final computed score")] = None
    normalized_score: Annotated[float | None, Field(description="The normalized score projection")] = None
    penalties_applied: Annotated[
        list[str] | None, Field(default=None, description="List of applied penalty identifier strings")
    ] = None
    aggregation_status: Annotated[str | None, Field(description="Status of aggregation")] = None


from backend_v2.models.domain.usage import TokenUsage as _TokenUsage

StepTraceMetadataDTO.model_rebuild(_types_namespace={"TokenUsage": _TokenUsage})
TraceEventMetadataEnvelope.model_rebuild(_types_namespace={"StepTraceMetadataDTO": StepTraceMetadataDTO})
