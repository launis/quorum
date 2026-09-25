"""Workflow State Management (Event Sourcing).

This module defines the new Event Sourcing state model, replacing the old mutable blackboard.
It uses an append-only log of `TraceEvent`s and a `ReasoningTrace` to capture cognitive processes.
"""

from __future__ import annotations

import json
import logging
import uuid
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Annotated, Any, Literal

if TYPE_CHECKING:
    from backend_v2.models.domain.system_config import MCPAuditTrace

from fastapi import status
from pydantic import BaseModel, ConfigDict, Field, JsonValue, ValidationError, field_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase


class StepExecutionEnvelope(V2CoreBase):
    """Base envelope for execution traces to prevent repetition and enforce DRY architecture.

    Attributes:
        execution_id: Unique execution identifier.
        workflow_id: Workflow definition identifier.
        step_id: Step definition identifier.
        initiator_id: Initiator user or system identifier.
        timestamp_isot: ISO timestamp string.
        unix_time: Unix epoch time.
        v2_engine: Engine flag indicator.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    execution_id: Annotated[str | None, Field(default=None)] = None
    workflow_id: Annotated[str | None, Field(default=None)] = None
    step_id: Annotated[str | None, Field(default=None)] = None
    initiator_id: Annotated[str | None, Field(default=None)] = None
    timestamp_isot: Annotated[str | None, Field(default=None)] = None
    unix_time: Annotated[int | None, Field(default=None)] = None
    v2_engine: Annotated[bool | None, Field(default=None)] = None


from backend_v2.models.domain.inputs import DomainInputValue, WorkflowInputs
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.atom_evaluation import LightweightMatrixDTO
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.dtos.node_execution import NodeExecutionUpdateDTO, StepOutputContentDTO
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.dtos.step_output import StepOutputDTO, StepPayloadValue
from backend_v2.models.dtos.trace import TraceEventMetadataDTO
from backend_v2.models.execution_core import ExecutionCoreFields, ExecutionMetadata
from backend_v2.utils.pydantic_utils import inflate

logger = logging.getLogger(__name__)

__all__ = [
    "ErrorTraceEvent",
    "EvidenceOverrideDTO",
    "ExecutionState",
    "ReasoningTrace",
    "StateProjector",
    "StepExecutionEnvelope",
    "StepOutputDTO",
    "TombstoneEvent",
    "TraceEvent",
    "WorkflowState",
]


class ReasoningTrace(V2CoreBase):
    """Stores hidden Chain-of-Thought (preserves 'Thinking Tokens').

    Attributes:
        thought_process: Raw chain-of-thought or reasoning trace.
        conclusion: Final conclusion derived from the reasoning.
        confidence_score: Confidence in the conclusion.
        model_name: Optional model used for reasoning.
        token_usage: Token usage statistics.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    thought_process: Annotated[
        str,
        Field(
            min_length=1,
            pattern=r"\S",
            description="The raw chain-of-thought or reasoning trace. "
            "MUST be written strictly in English to ensure cross-run determinism.",
        ),
    ]
    conclusion: Annotated[
        str,
        Field(
            min_length=1,
            pattern=r"\S",
            description="The final conclusion derived from the reasoning. MUST be written strictly in English.",
        ),
    ]
    confidence_score: Annotated[float, Field(description="Confidence in the conclusion.")]
    model_name: Annotated[str | None, Field(default=None, description="The model used for reasoning.")] = None
    token_usage: Annotated[
        TokenUsage,
        Field(
            default_factory=lambda: TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
            description="Token usage statistics.",
        ),
    ]

    @field_validator("confidence_score", mode="after")
    @classmethod
    def validate_confidence_score(cls, v: float) -> float:
        """Validates that confidence_score is between 0.0 and 1.0.

        Args:
            v: The confidence score.

        Returns:
            The validated confidence score.

        Raises:
            AppException: If score is out of bounds (VALIDATION_FAILED).
        """
        if not (0.0 <= v <= 1.0):
            msg = "confidence_score must be between 0.0 and 1.0"
            logger.error("[ReasoningTrace] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        return v


class EvidenceOverrideDTO(V2CoreBase):
    """Payload for evidence override events.

    Attributes:
        evq_id: The opaque evidence quote ID.
        user_rejected: Whether the user explicitly rejected this evidence.
        rejection_reason: The user-provided reason for rejection.
        rejected_by: User ID who made the rejection.
        rejected_at: Timestamp of the rejection.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    evq_id: Annotated[str, Field(description="The opaque evidence quote ID.")]
    user_rejected: Annotated[bool, Field(description="Whether the user explicitly rejected this evidence.")]
    rejection_reason: Annotated[str, Field(description="The user-provided reason for rejection.")]
    rejected_by: Annotated[str, Field(description="User ID who made the rejection.")]
    rejected_at: Annotated[datetime, Field(description="Timestamp of the rejection.")]


class TraceEvent(V2CoreBase):
    """Immutable event log item representing a distinct step or state change.

    Attributes:
        event_id: Unique event identifier.
        v: Schema version for forward compatibility and lazy upcasting.
        timestamp: Event timestamp.
        step_name: Name of the step that generated this event.
        event_type: Type of the event.
        content: Structured content of the event.
        reasoning: Associated reasoning trace.
        metadata: Additional metadata.
        mcp_audit_traces: Associated MCP tool audit traces.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    event_id: Annotated[uuid.UUID, "Unique event identifier."] = Field(
        default_factory=uuid.uuid4, description="Unique event identifier."
    )
    v: Annotated[int, Field(default=1, description="Schema version for forward compatibility and lazy upcasting.")] = 1
    timestamp: Annotated[datetime, "Event timestamp."] = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Event timestamp."
    )

    step_name: Annotated[
        str,
        Field(
            ...,
            min_length=1,
            pattern=r"\S",
            description="Name of the step that generated this event.",
            json_schema_extra={"x-ui-label": "Step Name"},
        ),
    ]

    event_type: Annotated[
        Literal["input", "reasoning", "decision", "error", "output", "tombstone", "evidence_override", "progress"],
        Field(..., description="Type of the event.", json_schema_extra={"x-ui-label": "Event Type"}),
    ]

    content: Annotated[
        StepPayloadValue
        | DomainInputValue
        | StepOutputContentDTO
        | Mapping[str, StepPayloadValue | DomainInputValue | JsonValue]
        | BaseModel
        | None,
        Field(default=None, description="Typed event payload"),
    ] = None
    reasoning: Annotated[ReasoningTrace | None, Field(default=None, description="Associated reasoning trace.")] = None
    metadata: Annotated[TraceEventMetadataDTO, "Additional metadata."] = Field(
        default_factory=TraceEventMetadataDTO, description="Additional metadata."
    )
    mcp_audit_traces: Annotated[list[MCPAuditTrace], "Associated MCP tool audit traces."] = Field(
        default_factory=list, description="Associated MCP tool audit traces."
    )


class ErrorTraceEvent(TraceEvent):
    """Specific event representing a fail-fast error katkos.

    Attributes:
        event_type: Constant 'error' event type.
        error_code: The standard ErrorCode string.
        error_message: Detailed error message.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    event_type: Annotated[Literal["error"], Field(default="error")] = "error"
    error_code: Annotated[str, Field(description="The standard ErrorCode string.")]
    error_message: Annotated[str, Field(description="Detailed error message.")]


class TombstoneEvent(TraceEvent):
    """Specific event representing GDPR-redacted or deleted data.

    Attributes:
        event_type: Constant 'tombstone' event type.
        redacted_hash: Cryptographic hash or identifier of the original redacted data.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    event_type: Annotated[Literal["tombstone"], Field(default="tombstone")] = "tombstone"
    redacted_hash: Annotated[str, Field(description="Cryptographic hash or identifier of the original redacted data.")]


from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.archivist import ArchivistOutput
from backend_v2.models.domain.causal import CausalOutput
from backend_v2.models.domain.coach import CoachingPlan

# Resolve deferred annotations on ExecutionCoreFields and ExecutionRecord (Pydantic V2 circular reference pattern).
# execution_core.py uses TYPE_CHECKING for TraceEvent types → annotations are strings.
from backend_v2.models.domain.execution import (
    ExecutionRecord,
    ExecutionStep,
    ExecutionStepState,
    ExecutionSummarySnapshot,
    FrozenContext,
)
from backend_v2.models.domain.falsifier import FalsifierOutput
from backend_v2.models.domain.inputs import WorkflowInputsIngress
from backend_v2.models.domain.interaction import InteractionAnalysis
from backend_v2.models.domain.judge import JudgeOutput
from backend_v2.models.domain.logician import LogicianOutput
from backend_v2.models.domain.overseer import OverseerOutput
from backend_v2.models.domain.performativity import PerformativityOutput
from backend_v2.models.domain.profiler import ProfilerOutput
from backend_v2.models.domain.security import InputProcessingOutputDTO
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.domain.xai import XAIOutput
from backend_v2.models.dtos.base import DataStarvationEvent
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO, ScorecardAtomDTO
from backend_v2.models.dtos.trace import ExecutionCreateDTO, ExecutionUpdateDTO
from backend_v2.models.view.sdui import AnySduiBlock

_state_localns = {
    "WorkflowInputs": WorkflowInputs,
    "WorkflowInputsIngress": WorkflowInputsIngress,
    "DomainInputValue": DomainInputValue,
    "StepOutputDTO": StepOutputDTO,
    "StepPayloadValue": StepPayloadValue,
    "TraceEventMetadataDTO": TraceEventMetadataDTO,
    "Any": Any,
    "ContextVariablesDTO": ContextVariablesDTO,
    "ExecutionMetadata": ExecutionMetadata,
    "MCPAuditTrace": MCPAuditTrace,
    "TraceEvent": TraceEvent,
    "ErrorTraceEvent": ErrorTraceEvent,
    "TombstoneEvent": TombstoneEvent,
    "DataStarvationEvent": DataStarvationEvent,
    "AnySduiBlock": AnySduiBlock,
    "ExecutionStep": ExecutionStep,
    "ExecutionStepState": ExecutionStepState,
    "ExecutionSummarySnapshot": ExecutionSummarySnapshot,
    "FrozenContext": FrozenContext,
    "RenderedSynthesisCache": RenderedSynthesisCache,
    "ScorecardAtomDTO": ScorecardAtomDTO,
    "MatrixScorecardRowDTO": MatrixScorecardRowDTO,
}
TraceEvent.model_rebuild(_types_namespace=_state_localns)
ErrorTraceEvent.model_rebuild(_types_namespace=_state_localns)
TombstoneEvent.model_rebuild(_types_namespace=_state_localns)
ExecutionCoreFields.model_rebuild(_types_namespace=_state_localns)
ExecutionRecord.model_rebuild(_types_namespace=_state_localns)
ExecutionCreateDTO.model_rebuild(_types_namespace=_state_localns)
ExecutionUpdateDTO.model_rebuild(_types_namespace=_state_localns)
NodeExecutionUpdateDTO.model_rebuild(_types_namespace=_state_localns)


class WorkflowState(ExecutionCoreFields):
    """Aggregate root containing the execution trace and current state.

    Attributes:
        execution_id: Unique execution identifier.
        workflow_id: The ID of the workflow definition.
        trace_version: Optimistic Concurrency Control version.
        workflow_name: Optional human-readable name of the workflow.
        created_at: Creation timestamp.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    execution_id: Annotated[uuid.UUID, "Unique execution identifier."] = Field(
        default_factory=uuid.uuid4, description="Unique execution identifier."
    )
    workflow_id: Annotated[
        str,
        Field(
            ...,
            min_length=1,
            pattern=r"^([a-z]{2,5})_[a-zA-Z0-9]{8,}$",
            description="The ID of the workflow definition.",
        ),
    ]
    trace_version: Annotated[int, Field(default=0, description="Optimistic Concurrency Control version.")] = 0
    # Phase 2: status, execution_trace, execution_trace_storage_path,
    # context_variables, context_variables_storage_path are inherited
    # from ExecutionCoreFields (SSOT).

    workflow_name: Annotated[str | None, Field(default=None, description="Human-readable name of the workflow.")] = None
    created_at: Annotated[datetime, "Creation timestamp."] = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp."
    )

    @property
    def start_time(self) -> datetime:
        """Returns the creation timestamp representing start time."""
        return self.created_at

    def add_event(self, event: TraceEvent) -> WorkflowState:
        """Returns a new WorkflowState with the added event (Functional style).

        Args:
            event: The TraceEvent to add.

        Returns:
            A new WorkflowState instance.
        """
        new_trace = self.execution_trace + [event]
        return self.model_copy(update={"execution_trace": new_trace, "trace_version": self.trace_version + 1})

    def get_context(self, key: str, model_class: type[BaseModel] | None = None) -> Any | None:
        """Best Practice: Typed Accessor for Context Variables.

        Retrieves a variable from context. If `model_class` is provided,
        attempts to inflate the value (dict) into the Pydantic model.

        Args:
            key: The context variable key.
            model_class: The expected Pydantic model class.

        Returns:
            The value (Model or Any) or None if missing/invalid.
        """
        if key not in self.context_variables:
            return None
        val = self.context_variables[key]
        if val is None:
            return None

        if model_class:
            return inflate(val, model_class)

        return val

    # --- Type-Safe Accessors for Common Steps (Bridge for State Presenter) ---
    # These properties perform Lazy Inflation: they convert the raw dict from context_variables
    # into a strict Pydantic model on access. This ensures that the backend logic always
    # works with validated objects, while the database remains a simple JSON store.

    @property
    def step_input_processing(self) -> Any | None:
        """Type-Safe Accessor for Input Processing Output."""
        return self.get_context("step_input_processing", InputProcessingOutputDTO)

    @property
    def step_interaction(self) -> Any | None:
        """Type-Safe Accessor for Interaction Analysis."""
        return self.get_context("step_interaction", InteractionAnalysis)

    @property
    def step_analyst(self) -> Any | None:
        """Type-Safe Accessor for Analyst Output."""
        return self.get_context("step_analyst", AnalystOutput)

    @property
    def step_judge(self) -> Any | None:
        """Type-Safe Accessor for Judge Output."""
        return self.get_context("step_judge", JudgeOutput)

    @property
    def step_coach(self) -> Any | None:
        """Type-Safe Accessor for Coach Output."""
        return self.get_context("step_coach", CoachingPlan)

    @property
    def step_xai(self) -> Any | None:
        """Type-Safe Accessor for XAI Reporter Output."""
        return self.get_context("step_xai", XAIOutput)

    # --- Sub-Step Accessors ---

    @property
    def step_logician(self) -> Any | None:
        """Retrieves parsed logician step output from context."""
        return self.get_context("step_logician", LogicianOutput)

    @property
    def step_falsifier(self) -> Any | None:
        """Retrieves parsed falsifier step output from context."""
        return self.get_context("step_falsifier", FalsifierOutput)

    @property
    def step_profiler(self) -> Any | None:
        """Retrieves parsed profiler step output from context."""
        return self.get_context("step_profiler", ProfilerOutput)

    @property
    def step_archivist(self) -> Any | None:
        """Retrieves parsed archivist step output from context."""
        return self.get_context("step_archivist", ArchivistOutput)

    @property
    def step_overseer(self) -> Any | None:
        """Retrieves parsed overseer step output from context."""
        return self.get_context("step_overseer", OverseerOutput)

    @property
    def step_causal(self) -> Any | None:
        """Retrieves parsed causal step output from context."""
        return self.get_context("step_causal", CausalOutput)

    @property
    def organization_id(self) -> str | None:
        """Retrieves organization ID from context variables."""
        if "organization_id" in self.context_variables:
            val = self.context_variables["organization_id"]
            if val is not None:
                return str(val)
        return None

    @property
    def user_id(self) -> str | None:
        """Retrieves user ID from context variables."""
        if "user_id" in self.context_variables:
            val = self.context_variables["user_id"]
            if val is not None:
                return str(val)
        return None

    @property
    def audit_results(self) -> Any:
        """Retrieves audit results from context variables."""
        if "audit_results" in self.context_variables:
            return self.context_variables["audit_results"]
        return None

    @property
    def step_detector(self) -> Any | None:
        """Retrieves parsed performativity detector step output from context."""
        return self.get_context("step_detector", PerformativityOutput)

    @property
    def step_judge_cognitive(self) -> Any | None:
        """Retrieves parsed cognitive judge step output from context."""
        return self.get_context("step_judge_cognitive", JudgeOutput)


class StateProjector:
    """In-Memory cache and reducer for Event Sourcing read models.

    Maintains a folded O(1) read model of the execution trace.
    """

    def __init__(self, trace: list[TraceEvent] | None = None) -> None:
        """Initializes the state projector and optionally folds an initial trace.

        Args:
            trace: Optional list of TraceEvents to initialize snapshot.
        """
        self._snapshot: dict[str, StepOutputContentDTO] = {}
        self._schema_version: int = 0
        self._trace_length: int = 0
        if trace:
            self.fold_trace(trace)

    @property
    def snapshot(self) -> list[StepOutputDTO]:
        """Returns the current flattened read model as a strictly typed list."""
        return self._build_dto_list()

    @property
    def schema_version(self) -> int:
        """Returns the highest applied schema version from events."""
        return self._schema_version

    def fold_trace(self, trace: list[TraceEvent], max_tokens: int | None = None) -> list[StepOutputDTO]:
        """Calculates and folds the read-model snapshot from the given trace.

        Optimized with token-window compaction: drops old events if max_tokens is exceeded.

        Args:
            trace: List of TraceEvents to fold.
            max_tokens: Maximum estimated tokens to include.

        Returns:
            List of StepOutputDTOs.
        """
        self._snapshot = {}
        self._schema_version = 0
        self._trace_length = 0

        # Sort newest first to prioritize recent state
        sorted_trace = sorted(trace, key=lambda e: e.timestamp, reverse=True)

        current_tokens = 0
        accepted_events = []

        for event in sorted_trace:
            if max_tokens is not None:
                content = event.content
                if isinstance(content, str):
                    event_str = content
                else:
                    event_str = json.dumps(content, default=str)
                est_tokens = len(event_str) // 4
                if current_tokens + est_tokens > max_tokens:
                    # Token limit reached, drop older events from LLM context
                    break
                current_tokens += est_tokens

            accepted_events.append(event)

        # Apply accepted events in chronological order to build the snapshot
        for event in reversed(accepted_events):
            self.apply_delta(event)

        return self._build_dto_list()

    def _build_dto_list(self) -> list[StepOutputDTO]:
        """Builds a list of StepOutputDTOs from the snapshot.

        Returns:
            List of StepOutputDTOs.

        Raises:
            AppException: If a legacy unstructured trace is detected (VALIDATION_FAILED).
        """
        output: list[StepOutputDTO] = []
        for step_id, step_output in self._snapshot.items():
            try:
                items_iter = step_output.data.items()
            except (AttributeError, TypeError) as err:
                # Epic 43 Phase 2 Fail-Fast: Legacy unstructured traces are strictly forbidden.
                msg = (
                    f"Legacy flat trace detected for step '{step_id}'. "
                    "Zero-Compromise Pledge forbids unstructured data."
                )
                logger.error("[StateProjector] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)

                raise AppException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=msg,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from err

            for block_id, payload in items_iter:
                try:
                    output.append(
                        StepOutputDTO(
                            step_id=step_id,
                            block_id=block_id,
                            data_type="unknown",
                            payload=payload,  # type: ignore[arg-type]
                        )
                    )
                except ValidationError as err:
                    msg = f"Invalid step output payload for step '{step_id}', block '{block_id}'."
                    logger.error("[StateProjector] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                    raise AppException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        message=msg,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from err
        return output

    def apply_delta(self, event: TraceEvent) -> None:
        """Applies a single Delta / Event to the in-memory cache.

        Supports nested step payloads and automatically unpacks ExecutionInputsDTO,
        WorkflowInputs, StepOutputContentDTO, and LightweightMatrixDTO into typed StepOutputContentDTO.

        Args:
            event: The TraceEvent to apply.
        """
        if event.v > self._schema_version:
            self._schema_version = event.v

        self._trace_length += 1

        if event.event_type in ["output", "input"]:
            content = event.content
            if isinstance(content, StepOutputContentDTO):
                self._snapshot[event.step_name] = content
            elif isinstance(content, ExecutionInputsDTO):
                merged: dict[str, DomainInputValue] = {
                    **dict(content.raw_inputs),
                    **dict(content.dynamic_inputs),
                }
                self._snapshot[event.step_name] = StepOutputContentDTO(data={str(k): v for k, v in merged.items()})
            elif isinstance(content, WorkflowInputs):
                self._snapshot[event.step_name] = StepOutputContentDTO(
                    data={str(k): v for k, v in content.dynamic_inputs.items()}
                )
            elif isinstance(content, LightweightMatrixDTO):
                self._snapshot[event.step_name] = StepOutputContentDTO(data={"reduced_atoms": content.reduced_atoms})
            elif isinstance(content, LightweightMatrixOutput):
                self._snapshot[event.step_name] = StepOutputContentDTO(data={event.step_name: content})
            elif type(content) is dict:
                self._snapshot[event.step_name] = StepOutputContentDTO(data={str(k): v for k, v in content.items()})
            else:
                self._snapshot[event.step_name] = content  # type: ignore[assignment]
        elif event.event_type == "tombstone":
            # For GDPR redactions, replace content with a tombstone marker
            redacted_hash = "unknown"
            if isinstance(event, TombstoneEvent):
                redacted_hash = event.redacted_hash
            self._snapshot[event.step_name] = StepOutputContentDTO(data={"_redacted": True, "hash": redacted_hash})


class ExecutionState(V2CoreBase):
    """Headless, strongly-typed Pydantic model representing the overall execution state.

    Attributes:
        executive_summary: Concise overview of findings from execution run.
        evidence_quotes: Selected quotes to support the findings.
        urgency_level: Urgency or severity level.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    executive_summary: Annotated[str, Field(description="Concise overview of findings from execution run.")]
    evidence_quotes: Annotated[
        list[QuoteEvidenceDTO],
        Field(default_factory=list, description="Selected quotes to support the findings."),
    ]
    urgency_level: Annotated[int, Field(description="Urgency or severity level.")]
