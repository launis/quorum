"""Domain models for workflow execution runs, steps, and runtime snapshots.

SSOT for FrozenContext, ExecutionCreate, ExecutionStep, ExecutionStepState,
ExecutionSummarySnapshot, EvaluatedMatrixContextDTO, ExecutionRecord,
JobAcceptedDTO, EvidenceRejectionRequest, and ExecutionAssignment.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Annotated

if TYPE_CHECKING:
    from backend_v2.models.domain.synthesis import RenderedSynthesisCache
    from backend_v2.models.dtos.context_variables import ContextVariablesDTO
    from backend_v2.models.state import ErrorTraceEvent, TombstoneEvent, TraceEvent

from pydantic import ConfigDict, EmailStr, Field, field_validator

from backend_v2.models.core_base import (
    OPAQUE_STRIPE_ID_REGEX,
    PrefixedUUID7,
    V2CoreBase,
    generate_uuid7_opaque_id,
)
from backend_v2.models.domain.inputs import WorkflowInputs, WorkflowInputsIngress
from backend_v2.models.domain.system_config import DataDictionaryField, MCPAuditTrace
from backend_v2.models.dtos.context_variables import EvaluatedMatrixContextDTO
from backend_v2.models.dtos.matrix_scorecard import ScorecardAtomDTO
from backend_v2.models.dtos.schema_manifest import GeneratedSchemaManifestDTO
from backend_v2.models.dtos.theory_manifest import InjectedTheoryManifestDTO
from backend_v2.models.enums import (
    AssignmentResultVisibility,
    AssignmentStatus,
    EmailDeliveryStatus,
    EntityPrefix,
    ExecutionStatus,
    LaxAssignmentResultVisibility,
    LaxAssignmentStatus,
    LaxEmailDeliveryStatus,
    LaxExecutionStatus,
    LaxSystemLocale,
    LaxUserRole,
    LLMProvider,
    SystemLocale,
    UserRole,
)
from backend_v2.models.execution_core import ExecutionCoreFields, ExecutionMetadata

logger = logging.getLogger(__name__)

__all__ = [
    "DEFAULT_MATRIX_SAMPLING_LIMIT",
    "EvaluatedMatrixContextDTO",
    "EvidenceRejectionRequest",
    "ExecutionAssignment",
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

    # Phase 2, Step 2.2: Convert bare Field(...) declarations to PEP 593 Annotated (QGR020 Check 20B)
    compiled_prompts: Annotated[dict[str, str], Field(default_factory=dict, description="Prompts sent to LLM.")]
    injected_theory: Annotated[
        InjectedTheoryManifestDTO,
        Field(default_factory=InjectedTheoryManifestDTO, description="Fetched theory texts."),
    ]
    generated_schemas: Annotated[
        GeneratedSchemaManifestDTO,
        Field(default_factory=GeneratedSchemaManifestDTO, description="JSON schemas used."),
    ]
    ui_hints_snapshot: Annotated[
        dict[str, DataDictionaryField],
        Field(default_factory=dict, description="UI rendering instructions."),
    ]
    mcp_tool_audit: Annotated[
        list[MCPAuditTrace],
        Field(
            default_factory=list,
            description="Immutable log of all external MCP tool calls made during execution.",
        ),
    ]


def _resolve_default_matrix_sampling_limit() -> int:
    """Resolve default matrix sampling limit dynamically from system settings.

    In production environment (matrix_sampling_limit=0), defaults to full evaluation (0 = all atoms).
    In development environment (matrix_sampling_limit=1), defaults to fast sampled execution.

    Returns:
        Configured integer matrix sampling limit from system settings.
    """
    from backend_v2.settings import get_settings

    return int(get_settings().matrix_sampling_limit)


DEFAULT_MATRIX_SAMPLING_LIMIT: int = 0


class ExecutionCreate(V2CoreBase):
    """Payload to instantiate a new workflow execution run."""

    model_config = ConfigDict(strict=True, extra="forbid")

    workflow_id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Target workflow ID to execute.")]
    target_locale: Annotated[str, Field(min_length=2, description="Target language/locale code (e.g., 'fi', 'en').")]
    profile_id: Annotated[
        str | None,
        Field(
            default=None,
            description="Optional Opaque ID of the Output Profile to apply. If omitted, fallback to workflow default.",
        ),
    ] = None
    matrix_sampling_strategy: Annotated[
        int,
        Field(
            default_factory=_resolve_default_matrix_sampling_limit,
            description=(
                "Explicit dynamic strategy for Matrix Flattening. Defaulted from settings "
                "(0 in production = all atoms, 1 in development)."
            ),
        ),
    ]
    raw_inputs: Annotated[
        WorkflowInputsIngress | WorkflowInputs,
        Field(default_factory=lambda: WorkflowInputsIngress(), description="User provided raw inputs"),
    ]
    provider_override: Annotated[
        LLMProvider | None,
        Field(default=None, description="Optional execution-level LLM provider override."),
    ] = None
    model_registry_id: Annotated[
        str | None,
        Field(default=None, description="Optional execution-level model registry stack override"),
    ] = None

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
            return _resolve_default_matrix_sampling_limit()
        return int(value)


ExecutionCreate.model_rebuild()


class ExecutionStep(V2CoreBase):
    """Real-time status tracking, scorecard outputs, and FinOps telemetry for a single DAG node."""

    model_config = ConfigDict(strict=True, extra="forbid")

    id: Annotated[str, Field(pattern=r"^([a-z0-9_]{2,15})_[a-zA-Z0-9_-]+$", description="Step ID")]
    label: Annotated[str, Field(description="Localized label for UI tracking")]
    status: Annotated[
        LaxExecutionStatus,
        Field(default=ExecutionStatus.PENDING, description="Status: pending, running, passed, failed"),
    ] = ExecutionStatus.PENDING
    last_error: Annotated[str | None, Field(default=None, description="Error message if the step failed")] = None
    message_code: Annotated[str | None, Field(default=None, description="Optional UX message code for SSE")] = None
    model_strategy: Annotated[
        str | None,
        Field(default=None, description="Logical strategy alias ('fast', 'reasoning')"),
    ] = None
    physical_model: Annotated[
        str | None,
        Field(default=None, description="Exact physical provider model string ('vertex_ai/gemini-2.5-flash')"),
    ] = None
    system_fingerprint: Annotated[
        str | None,
        Field(default=None, description="Provider system fingerprint / model weights version"),
    ] = None

    prompt_tokens: Annotated[int, Field(default=0, ge=0, description="Prompt tokens consumed by this step")] = 0
    completion_tokens: Annotated[
        int, Field(default=0, ge=0, description="Completion tokens generated by this step")
    ] = 0
    cached_tokens: Annotated[int, Field(default=0, ge=0, description="Cached tokens read by this step")] = 0
    reasoning_tokens: Annotated[
        int, Field(default=0, ge=0, description="Thinking/reasoning tokens generated by this step")
    ] = 0
    cost_usd: Annotated[
        float, Field(default=0.0, ge=0.0, description="Financial cost incurred by this step in USD")
    ] = 0.0
    duration_ms: Annotated[int, Field(default=0, ge=0, description="Step duration in milliseconds")] = 0
    chunk_count: Annotated[
        int, Field(default=1, ge=1, description="Number of parallel chunks processed in this step")
    ] = 1

    progress: Annotated[
        int | None, Field(default=None, ge=0, le=100, description="Step progress percentage for SSE streaming (0-100)")
    ] = None
    has_warning: Annotated[bool, Field(default=False, description="Whether the step completed with warnings")] = False
    input_merkle_hash: Annotated[
        str | None,
        Field(
            default=None,
            description="Canonical SHA-256 Merkle hash of step inputs, prompt blocks, and tier configuration",
        ),
    ] = None

    scorecard_atoms: Annotated[
        dict[str, ScorecardAtomDTO],
        Field(default_factory=dict, description="Presentation atoms including potential human overrides."),
    ]


ExecutionStepState = ExecutionStep


class ExecutionSummarySnapshot(V2CoreBase):
    """Typed DTO snapshot for non-FinOps execution telemetry."""

    model_config = ConfigDict(strict=True, extra="forbid")

    strictness_level: Annotated[
        int, Field(default=100, ge=0, le=100, description="Strictness level percentage for evaluation")
    ] = 100
    is_ensemble_run: Annotated[bool, Field(default=False, description="Whether ensemble evaluation was active")] = False
    is_degraded: Annotated[bool, Field(default=False, description="Whether execution finished in a degraded state")] = (
        False
    )
    system_concurrency_snapshot: Annotated[
        dict[str, int],
        Field(default_factory=dict, description="Concurrency metric snapshot at termination"),
    ]


class ExecutionRecord(ExecutionCoreFields):
    """Record of a workflow execution, including the frozen context and results."""

    model_config = ConfigDict(strict=True, extra="forbid")

    if TYPE_CHECKING:
        status: Annotated[LaxExecutionStatus, Field(default=ExecutionStatus.PENDING)] = ExecutionStatus.PENDING
        target_locale: Annotated[str, Field(description="Target locale")]
        execution_trace: Annotated[
            list[ErrorTraceEvent | TombstoneEvent | TraceEvent],
            Field(default_factory=list),
        ]
        execution_trace_storage_path: Annotated[str | None, Field(default=None)] = None
        context_variables: Annotated[
            ContextVariablesDTO,
            Field(default_factory=lambda: ContextVariablesDTO(variables={})),
        ]
        context_variables_storage_path: Annotated[str | None, Field(default=None)] = None
        progress: Annotated[int | None, Field(default=None)] = None
        status_message: Annotated[str | None, Field(default=None)] = None

    id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Execution ID, usually a uuid")]
    workflow_id: Annotated[str, Field(description="Workflow ID")]
    workflow_version: Annotated[int, Field(default=1, ge=1, description="Version number of the executing workflow")] = 1
    state_version: Annotated[
        int,
        Field(ge=1, default=1, description="Monotonically increasing optimistic concurrency control version"),
    ] = 1
    active_profile_id: Annotated[
        str | None,
        Field(default=None, description="The ID of the output profile selected for formatting and printing."),
    ] = None
    raw_inputs: Annotated[
        WorkflowInputs,
        Field(default_factory=lambda: WorkflowInputs(), description="Raw user inputs by role"),
    ]
    frozen_context: Annotated[
        FrozenContext | None,
        Field(default_factory=FrozenContext, description="Immutable snapshot of context"),
    ]
    frozen_context_storage_path: Annotated[
        str | None,
        Field(default=None, description="Optional path to Blob Storage offloaded Frozen Context JSON"),
    ] = None
    pdf_report_path: Annotated[
        str | None,
        Field(default=None, description="Path to the generated PDF Execution Report."),
    ] = None
    output_profile_id: Annotated[
        str | None,
        Field(default=None, description="Target profile ID for formatting instructions and synthesis."),
    ] = None
    steps: Annotated[
        list[ExecutionStep],
        Field(
            default_factory=list,
            description="Real-time status tracking and FinOps telemetry for DAG nodes (SSOT)",
        ),
    ]
    step_states: Annotated[
        dict[str, ExecutionStepState],
        Field(default_factory=dict, description="Transitional step_states lookup mapping"),
    ]
    profile_syntheses: Annotated[
        dict[str, RenderedSynthesisCache],
        Field(default_factory=dict, description="Multi-profile synthesis caching"),
    ]
    source_identity_manifest: Annotated[
        dict[str, str],
        Field(default_factory=dict, description="O(1) Snapshot mapping Opaque ID to Display Name for inputs."),
    ]
    is_resumable: Annotated[
        bool,
        Field(
            default=False,
            description="Dynamic flag indicating if a failed/pending execution can be safely resumed.",
        ),
    ] = False
    prompt_tokens: Annotated[int, Field(default=0, ge=0, description="Total prompt tokens consumed.")] = 0
    completion_tokens: Annotated[int, Field(default=0, ge=0, description="Total completion tokens generated.")] = 0
    cached_tokens: Annotated[int, Field(default=0, ge=0, description="Total tokens read from context cache.")] = 0
    reasoning_tokens: Annotated[int, Field(default=0, ge=0, description="Total thinking/reasoning tokens.")] = 0
    cumulative_synthesis_tokens: Annotated[
        int,
        Field(default=0, ge=0, description="Cumulative tokens used across all synthesis runs."),
    ] = 0

    dag_cost_usd: Annotated[
        float, Field(default=0.0, ge=0.0, description="Total financial DAG execution cost in USD.")
    ] = 0.0
    cumulative_synthesis_cost: Annotated[
        float,
        Field(default=0.0, ge=0.0, description="Cumulative cost in USD across all synthesis runs."),
    ] = 0.0
    cost_estimate: Annotated[
        float, Field(default=0.0, ge=0.0, description="Estimated total cost of the execution in USD")
    ] = 0.0

    models_used: Annotated[
        dict[str, int],
        Field(default_factory=dict, description="Dictionary of models used and their usage count/tokens"),
    ]
    execution_summary: Annotated[
        ExecutionSummarySnapshot | None,
        Field(default=None, description="Typed non-FinOps execution telemetry snapshot"),
    ] = None
    metadata: Annotated[
        ExecutionMetadata | None,
        Field(default=None, description="Configuration metadata for the execution"),
    ] = None
    duration_ms: Annotated[int, Field(default=0, ge=0, description="Total execution duration in milliseconds")] = 0
    error: Annotated[str | None, Field(default=None, description="Error message if failed")] = None
    created_at: Annotated[
        datetime,
        Field(default_factory=lambda: datetime.now(timezone.utc), description="UTC creation timestamp"),
    ]
    updated_at: Annotated[
        datetime,
        Field(default_factory=lambda: datetime.now(timezone.utc), description="UTC update timestamp"),
    ]
    completed_at: Annotated[datetime | None, Field(default=None, description="UTC completion timestamp")] = None
    created_by: Annotated[
        str | None,
        Field(default=None, description="ID of the user who started the execution"),
    ] = None
    organization_id: Annotated[
        str | None,
        Field(default=None, description="ID of the organization for this execution"),
    ] = None

    def without_profile_synthesis(self, profile_id: str) -> ExecutionRecord:
        """Return an immutable copy with the specified profile synthesis removed.

        Args:
            profile_id: Identifier of the presentation profile to invalidate.

        Returns:
            ExecutionRecord: Cloned execution record without the cached profile synthesis.
        """
        if profile_id not in self.profile_syntheses:
            return self
        updated_syntheses = {k: v for k, v in self.profile_syntheses.items() if k != profile_id}
        return self.model_copy(update={"profile_syntheses": updated_syntheses})

    def transition_step(
        self,
        step_id: str,
        status: ExecutionStatus,
        progress: int | None = None,
        label: str | None = None,
        last_error: str | None = None,
        has_warning: bool | None = None,
        input_merkle_hash: str | None = None,
    ) -> ExecutionRecord:
        """Atomically transition step state across steps list and step_states dictionary.

        Args:
            step_id: Canonical identifier of the execution step.
            status: Target execution status.
            progress: Optional completion progress percentage (0-100).
            label: Optional display label for the step.
            last_error: Optional error message string if failed.
            has_warning: Optional boolean flag indicating warnings.
            input_merkle_hash: Optional canonical SHA-256 Merkle hash of step inputs.

        Returns:
            ExecutionRecord: Cloned execution record with atomically synchronized steps.
        """
        existing_step: ExecutionStep | None = (
            self.step_states[step_id]
            if step_id in self.step_states
            else next((s for s in self.steps if s.id == step_id), None)
        )

        if existing_step is not None:
            updated_data = existing_step.model_dump(mode="python")
            updated_data["status"] = status
            if progress is not None:
                updated_data["progress"] = progress
            if label is not None:
                updated_data["label"] = label
            if last_error is not None:
                updated_data["last_error"] = last_error
            if has_warning is not None:
                updated_data["has_warning"] = has_warning
            if input_merkle_hash is not None:
                updated_data["input_merkle_hash"] = input_merkle_hash
            elif status in (ExecutionStatus.PENDING, ExecutionStatus.FAILED, ExecutionStatus.BLOCKED):
                updated_data["input_merkle_hash"] = None
            step_item = ExecutionStep.model_validate(updated_data)
        else:
            step_item = ExecutionStep.model_validate(
                {
                    "id": step_id,
                    "label": label if label is not None else step_id,
                    "status": status,
                    "progress": progress,
                    "last_error": last_error,
                    "has_warning": has_warning if has_warning is not None else False,
                    "input_merkle_hash": input_merkle_hash,
                }
            )

        new_step_states = {**self.step_states, step_id: step_item}
        new_steps = [step_item if s.id == step_id else s for s in self.steps]
        if not any(s.id == step_id for s in self.steps):
            new_steps.append(step_item)

        return self.model_copy(update={"step_states": new_step_states, "steps": new_steps})

    def with_step_passed(self, step_id: str, label: str = "Report Render") -> ExecutionRecord:
        """Return an immutable copy with the designated step marked PASSED at 100%.

        Args:
            step_id: Canonical identifier of the execution step.
            label: Human-readable display label for the step.

        Returns:
            ExecutionRecord: Cloned execution record with updated steps and step_states.
        """
        return self.transition_step(
            step_id=step_id,
            status=ExecutionStatus.PASSED,
            progress=100,
            label=label,
        )


class JobAcceptedDTO(V2CoreBase):
    """Omni-channel render endpoint accepted response."""

    model_config = ConfigDict(strict=True, extra="forbid")

    status: str
    message: str
    execution_id: str


class EvidenceRejectionRequest(V2CoreBase):
    """Request DTO for rejecting a specific evidence quote."""

    model_config = ConfigDict(strict=True, extra="forbid")

    rejection_reason: Annotated[str, Field(description="Reason for rejecting the evidence quote.")]


class ExecutionAssignment(V2CoreBase):
    """Single-use stateful workflow execution assignment bound to an organization and recipient.

    Attributes:
        id: Canonical Task Assignment Opaque Stripe ID (tsk_<hex32>).
        batch_id: Optional cohort batch identifier grouping bulk-created task assignments.
        organization_id: Owning Organization Opaque Stripe ID (org_<hex32>).
        assigned_email: Recipient email address.
        assigned_user_id: Bound User ID once activated (usr_<hex32>).
        invited_role: Permission role granted when auto-onboarding a new user.
        workflow_id: Target Workflow ID (wf_<hex32>).
        output_profile_id: Optional Output Profile ID (prf_<hex32>).
        target_locale: Target execution locale.
        locked_inputs: Immutable manager-locked workflow inputs.
        assignee_input_keys: ExpectedInput keys unlocked for assignee completion.
        draft_inputs: Server-side auto-saved draft inputs from the assignee.
        token_hash: SHA-256 hex digest of the single-use assignment link token.
        status: Lifecycle status of the task assignment.
        email_delivery_status: Transactional email delivery status.
        result_visibility: Post-submission result visibility policy.
        hard_deadline_at: Absolute UTC deadline timestamp.
        relative_duration_seconds: Optional countdown timer in seconds starting upon activation.
        activated_at: UTC timestamp when the assignee activated the assignment.
        submitted_at: UTC timestamp when the assignee submitted the assignment.
        execution_id: Triggered ExecutionRecord ID (exe_<hex32>).
        created_by: Creator User ID (usr_<hex32>).
        created_at: Creation UTC timestamp.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[
        PrefixedUUID7,
        Field(
            default_factory=lambda: generate_uuid7_opaque_id(EntityPrefix.ASSIGNMENT),
            description="Canonical Task Assignment ID (tsk_<hex32>)",
        ),
    ]
    batch_id: Annotated[
        PrefixedUUID7 | None,
        Field(default=None, description="Optional cohort batch identifier grouping bulk-created task assignments"),
    ] = None
    organization_id: Annotated[PrefixedUUID7, Field(description="Owning Organization ID (org_<hex32>)")]
    assigned_email: Annotated[EmailStr, Field(description="Recipient email address")]
    assigned_user_id: Annotated[
        PrefixedUUID7 | None,
        Field(default=None, description="Bound User ID once activated (usr_<hex32>)"),
    ] = None
    invited_role: Annotated[
        LaxUserRole,
        Field(default=UserRole.MEMBER, description="Role granted upon auto-onboarding"),
    ] = UserRole.MEMBER
    workflow_id: Annotated[PrefixedUUID7, Field(description="Target Workflow ID (wf_<hex32>)")]
    output_profile_id: Annotated[
        PrefixedUUID7 | None,
        Field(default=None, description="Optional Output Profile ID (prf_<hex32>)"),
    ] = None
    target_locale: Annotated[
        LaxSystemLocale,
        Field(default=SystemLocale.FI, description="Target execution locale"),
    ] = SystemLocale.FI
    locked_inputs: Annotated[
        WorkflowInputs,
        Field(default_factory=WorkflowInputs, description="Immutable manager-locked workflow inputs"),
    ]
    assignee_input_keys: Annotated[
        list[str],
        Field(default_factory=list, description="ExpectedInput keys unlocked for assignee completion"),
    ]
    draft_inputs: Annotated[
        WorkflowInputs,
        Field(default_factory=WorkflowInputs, description="Server-side auto-saved draft inputs from assignee"),
    ]
    token_hash: Annotated[
        str,
        Field(min_length=64, max_length=64, description="SHA-256 hex digest of the single-use assignment token"),
    ]
    status: Annotated[
        LaxAssignmentStatus,
        Field(default=AssignmentStatus.PENDING, description="Lifecycle status of the task assignment"),
    ] = AssignmentStatus.PENDING
    email_delivery_status: Annotated[
        LaxEmailDeliveryStatus,
        Field(default=EmailDeliveryStatus.PENDING, description="Transactional email delivery status"),
    ] = EmailDeliveryStatus.PENDING
    result_visibility: Annotated[
        LaxAssignmentResultVisibility,
        Field(
            default=AssignmentResultVisibility.CONFIRMATION_ONLY,
            description="Post-submission result visibility policy",
        ),
    ] = AssignmentResultVisibility.CONFIRMATION_ONLY
    hard_deadline_at: Annotated[datetime, Field(description="Absolute UTC deadline timestamp")]
    relative_duration_seconds: Annotated[
        int | None,
        Field(default=None, ge=60, description="Optional relative countdown timer in seconds from activation"),
    ] = None
    activated_at: Annotated[
        datetime | None,
        Field(default=None, description="UTC timestamp when the assignee activated the assignment"),
    ] = None
    submitted_at: Annotated[
        datetime | None,
        Field(default=None, description="UTC timestamp when the assignee submitted the assignment"),
    ] = None
    execution_id: Annotated[
        PrefixedUUID7 | None,
        Field(default=None, description="Triggered ExecutionRecord ID (exe_<hex32>)"),
    ] = None
    created_by: Annotated[PrefixedUUID7, Field(description="Creator User ID (usr_<hex32>)")]
    created_at: Annotated[
        datetime,
        Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation UTC timestamp"),
    ]

    @field_validator("hard_deadline_at", "activated_at", "submitted_at", "created_at", mode="before")
    @classmethod
    def _parse_iso_datetime(cls, value: datetime | str | None) -> datetime | None:
        """Coerce ISO 8601 datetime strings into timezone-aware datetime instances.

        Args:
            value: Raw timestamp value (ISO string, datetime object, or None).

        Returns:
            Parsed datetime instance or None.

        Raises:
            ValueError: If a string input is not a valid ISO 8601 timestamp.
        """
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value
