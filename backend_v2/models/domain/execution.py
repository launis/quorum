"""Domain models for workflow execution runs, steps, and runtime snapshots.

SSOT for FrozenContext, ExecutionCreate, ExecutionStep, ExecutionStepState,
ExecutionSummarySnapshot, EvaluatedMatrixContextDTO, ExecutionRecord,
JobAcceptedDTO, and EvidenceRejectionRequest.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Annotated, Any

if TYPE_CHECKING:
    from backend_v2.models.domain.synthesis import RenderedSynthesisCache
    from backend_v2.models.state import ErrorTraceEvent, TombstoneEvent, TraceEvent

from pydantic import ConfigDict, Field, field_validator

from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, V2CoreBase
from backend_v2.models.domain.inputs import WorkflowInputs, WorkflowInputsIngress
from backend_v2.models.domain.system_config import DataDictionaryField, MCPAuditTrace
from backend_v2.models.dtos.atom_result import EvaluatedAtomDTO
from backend_v2.models.dtos.matrix_scorecard import ScorecardAtomDTO
from backend_v2.models.dtos.schema_manifest import GeneratedSchemaManifestDTO
from backend_v2.models.dtos.theory_manifest import InjectedTheoryManifestDTO
from backend_v2.models.enums import (
    ExecutionStatus,
    LaxExecutionStatus,
    LLMProvider,
)
from backend_v2.models.execution_core import ExecutionCoreFields, ExecutionMetadata

logger = logging.getLogger(__name__)

__all__ = [
    "DEFAULT_MATRIX_SAMPLING_LIMIT",
    "EvaluatedMatrixContextDTO",
    "EvidenceRejectionRequest",
    "ExecutionCreate",
    "ExecutionRecord",
    "ExecutionStep",
    "ExecutionStepState",
    "ExecutionSummarySnapshot",
    "FrozenContext",
    "JobAcceptedDTO",
]


class FrozenContext(V2CoreBase):
    """Deep copy of context state at execution time for auditability."""

    model_config = ConfigDict(strict=True, extra="forbid")

    compiled_prompts: dict[str, str] = Field(default_factory=dict, description="Prompts sent to LLM.")
    injected_theory: InjectedTheoryManifestDTO = Field(
        default_factory=InjectedTheoryManifestDTO, description="Fetched theory texts."
    )
    generated_schemas: GeneratedSchemaManifestDTO = Field(
        default_factory=GeneratedSchemaManifestDTO, description="JSON schemas used."
    )
    ui_hints_snapshot: dict[str, DataDictionaryField] = Field(
        default_factory=dict, description="UI rendering instructions."
    )
    mcp_tool_audit: list[MCPAuditTrace] = Field(
        default_factory=list, description="Immutable log of all external MCP tool calls made during execution."
    )


DEFAULT_MATRIX_SAMPLING_LIMIT: int = 1


class ExecutionCreate(V2CoreBase):
    """Payload to instantiate a new workflow execution run."""

    model_config = ConfigDict(strict=True, extra="forbid")

    workflow_id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Target workflow ID to execute.")]
    target_locale: Annotated[str, Field(min_length=2, description="Target language/locale code (e.g., 'fi', 'en').")]
    profile_id: str | None = Field(
        default=None,
        description="Optional Opaque ID of the Output Profile to apply. If omitted, fallback to workflow default.",
    )
    matrix_sampling_strategy: Annotated[
        int,
        Field(
            default=DEFAULT_MATRIX_SAMPLING_LIMIT,
            description=(
                "Explicit dynamic strategy for Matrix Flattening. Defaulted from ALL to "
                "10 locally to mitigate LLM JSON schema context limits."
            ),
        ),
    ] = DEFAULT_MATRIX_SAMPLING_LIMIT
    raw_inputs: WorkflowInputsIngress | WorkflowInputs = Field(
        default_factory=lambda: WorkflowInputsIngress(), description="User provided raw inputs"
    )
    provider_override: LLMProvider | None = Field(
        default=None, description="Optional execution-level LLM provider override."
    )
    model_registry_id: str | None = Field(
        default=None, description="Optional execution-level model registry stack override"
    )

    @field_validator("matrix_sampling_strategy", mode="before")
    @classmethod
    def _resolve_matrix_sampling_strategy(cls, value: int | None) -> int:
        """Resolve matrix_sampling_strategy if passed explicitly as None.

        Args:
            value: The input sampling strategy value or None.

        Returns:
            The resolved integer matrix sampling limit.
        """
        if value is None:
            return DEFAULT_MATRIX_SAMPLING_LIMIT
        return int(value)


ExecutionCreate.model_rebuild()


class ExecutionStep(V2CoreBase):
    """Real-time status tracking, scorecard outputs, and FinOps telemetry for a single DAG node."""

    model_config = ConfigDict(strict=True, extra="forbid")

    id: str = Field(pattern=r"^([a-z0-9_]{2,15})_[a-zA-Z0-9_-]+$", description="Step ID")
    label: str = Field(description="Localized label for UI tracking")
    status: LaxExecutionStatus = Field(
        default=ExecutionStatus.PENDING, description="Status: pending, running, passed, failed"
    )
    last_error: str | None = Field(default=None, description="Error message if the step failed")
    message_code: str | None = Field(default=None, description="Optional UX message code for SSE")
    model_strategy: str | None = Field(default=None, description="Logical strategy alias ('fast', 'reasoning')")
    physical_model: str | None = Field(
        default=None, description="Exact physical provider model string ('vertex_ai/gemini-2.5-flash')"
    )
    system_fingerprint: str | None = Field(
        default=None, description="Provider system fingerprint / model weights version"
    )

    prompt_tokens: int = Field(default=0, ge=0, description="Prompt tokens consumed by this step")
    completion_tokens: int = Field(default=0, ge=0, description="Completion tokens generated by this step")
    cached_tokens: int = Field(default=0, ge=0, description="Cached tokens read by this step")
    reasoning_tokens: int = Field(default=0, ge=0, description="Thinking/reasoning tokens generated by this step")
    cost_usd: float = Field(default=0.0, ge=0.0, description="Financial cost incurred by this step in USD")
    duration_ms: int = Field(default=0, ge=0, description="Step duration in milliseconds")
    chunk_count: int = Field(default=1, ge=1, description="Number of parallel chunks processed in this step")

    progress: Annotated[
        int | None, Field(default=None, ge=0, le=100, description="Step progress percentage for SSE streaming (0-100)")
    ] = None
    has_warning: Annotated[bool, Field(default=False, description="Whether the step completed with warnings")] = False

    scorecard_atoms: dict[str, ScorecardAtomDTO] = Field(
        default_factory=dict, description="Presentation atoms including potential human overrides."
    )


ExecutionStepState = ExecutionStep


class ExecutionSummarySnapshot(V2CoreBase):
    """Typed DTO snapshot for non-FinOps execution telemetry."""

    model_config = ConfigDict(strict=True, extra="forbid")

    strictness_level: int = Field(default=100, ge=1, description="Strictness level percentage for evaluation")
    is_ensemble_run: bool = Field(default=False, description="Whether ensemble evaluation was active")
    is_degraded: bool = Field(default=False, description="Whether execution finished in a degraded state")
    system_concurrency_snapshot: dict[str, int] = Field(
        default_factory=dict, description="Concurrency metric snapshot at termination"
    )


class EvaluatedMatrixContextDTO(V2CoreBase):
    """DTO for evaluated matrix context within execution context_variables."""

    model_config = ConfigDict(strict=True, extra="forbid")
    evaluated_atoms: Annotated[
        dict[str, str],
        Field(default_factory=dict, description="Map of atom IDs to evaluation status"),
    ]
    raw_atoms: Annotated[
        list[EvaluatedAtomDTO],
        Field(default_factory=list, description="Raw evaluated atom payloads"),
    ] = Field(default_factory=list)


class ExecutionRecord(ExecutionCoreFields):
    """Record of a workflow execution, including the frozen context and results."""

    model_config = ConfigDict(strict=True, extra="forbid")

    if TYPE_CHECKING:
        status: LaxExecutionStatus = Field(default=ExecutionStatus.PENDING)
        target_locale: str = Field(...)
        execution_trace: list[ErrorTraceEvent | TombstoneEvent | TraceEvent] = Field(default_factory=list)
        execution_trace_storage_path: str | None = Field(default=None)
        context_variables: dict[str, Any] = Field(default_factory=dict)
        context_variables_storage_path: str | None = Field(default=None)
        progress: int | None = Field(default=None)
        status_message: str | None = Field(default=None)

    id: str = Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Execution ID, usually a uuid")
    workflow_id: str = Field(description="Workflow ID")
    workflow_version: int = Field(default=1, ge=1, description="Version number of the executing workflow")
    active_profile_id: str | None = Field(
        default=None, description="The ID of the output profile selected for formatting and printing."
    )
    raw_inputs: WorkflowInputs = Field(default_factory=lambda: WorkflowInputs(), description="Raw user inputs by role")
    frozen_context: FrozenContext | None = Field(
        default_factory=FrozenContext, description="Immutable snapshot of context"
    )
    frozen_context_storage_path: str | None = Field(
        default=None, description="Optional path to Blob Storage offloaded Frozen Context JSON"
    )
    pdf_report_path: str | None = Field(default=None, description="Path to the generated PDF Execution Report.")
    output_profile_id: Annotated[
        str | None,
        Field(default=None, description="Target profile ID for formatting instructions and synthesis."),
    ] = None
    steps: list[ExecutionStep] = Field(
        default_factory=list, description="Real-time status tracking and FinOps telemetry for DAG nodes (SSOT)"
    )
    step_states: dict[str, ExecutionStepState] = Field(
        default_factory=dict, description="Transitional step_states lookup mapping"
    )
    profile_syntheses: dict[str, RenderedSynthesisCache] = Field(
        default_factory=dict, description="Multi-profile synthesis caching"
    )
    source_identity_manifest: dict[str, str] = Field(
        default_factory=dict, description="O(1) Snapshot mapping Opaque ID to Display Name for inputs."
    )
    is_resumable: bool = Field(
        default=False, description="Dynamic flag indicating if a failed/pending execution can be safely resumed."
    )
    prompt_tokens: int = Field(default=0, ge=0, description="Total prompt tokens consumed.")
    completion_tokens: int = Field(default=0, ge=0, description="Total completion tokens generated.")
    cached_tokens: int = Field(default=0, ge=0, description="Total tokens read from context cache.")
    reasoning_tokens: int = Field(default=0, ge=0, description="Total thinking/reasoning tokens.")
    cumulative_synthesis_tokens: int = Field(
        default=0, ge=0, description="Cumulative tokens used across all synthesis runs."
    )

    dag_cost_usd: float = Field(default=0.0, ge=0.0, description="Total financial DAG execution cost in USD.")
    cumulative_synthesis_cost: float = Field(
        default=0.0, ge=0.0, description="Cumulative cost in USD across all synthesis runs."
    )
    cost_estimate: float = Field(default=0.0, ge=0.0, description="Estimated total cost of the execution in USD")

    models_used: dict[str, int] = Field(
        default_factory=dict, description="Dictionary of models used and their usage count/tokens"
    )
    execution_summary: ExecutionSummarySnapshot | None = Field(
        default=None, description="Typed non-FinOps execution telemetry snapshot"
    )
    metadata: ExecutionMetadata | None = Field(default=None, description="Configuration metadata for the execution")
    duration_ms: int = Field(default=0, ge=0, description="Total execution duration in milliseconds")
    error: str | None = Field(default=None, description="Error message if failed")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="UTC creation timestamp"
    )
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="UTC update timestamp")
    completed_at: datetime | None = Field(default=None, description="UTC completion timestamp")
    created_by: str | None = Field(default=None, description="ID of the user who started the execution")
    organization_id: str | None = Field(default=None, description="ID of the organization for this execution")


class JobAcceptedDTO(V2CoreBase):
    """Omni-channel render endpoint accepted response."""

    model_config = ConfigDict(strict=True, extra="forbid")

    status: str
    message: str
    execution_id: str


class EvidenceRejectionRequest(V2CoreBase):
    """Request DTO for rejecting a specific evidence quote."""

    model_config = ConfigDict(strict=True, extra="forbid")

    rejection_reason: str = Field(description="Reason for rejecting the evidence quote.")
