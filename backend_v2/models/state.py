"""Workflow State Management (Event Sourcing).

This module defines the new Event Sourcing state model, replacing the old mutable blackboard.
It uses an append-only log of `TraceEvent`s and a `ReasoningTrace` to capture cognitive processes.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.archivist import ArchivistOutput
from backend_v2.models.domain.causal import CausalOutput
from backend_v2.models.domain.coach import CoachingPlan
from backend_v2.models.domain.falsifier import FalsifierOutput
from backend_v2.models.domain.guard import GuardOutput
from backend_v2.models.domain.interaction import InteractionAnalysis
from backend_v2.models.domain.judge import JudgeOutput
from backend_v2.models.domain.logician import LogicianOutput
from backend_v2.models.domain.overseer import OverseerOutput
from backend_v2.models.domain.performativity import PerformativityOutput
from backend_v2.models.domain.profiler import ProfilerOutput
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.domain.xai import XAIOutput
from backend_v2.models.execution_core import ExecutionCoreFields
from backend_v2.utils.pydantic_utils import inflate

logger = logging.getLogger(__name__)


class StepExecutionEnvelope(V2CoreBase):
    """Base envelope for execution traces to prevent repetition and enforce DRY architecture."""

    execution_id: str | None = Field(default=None)
    workflow_id: str | None = Field(default=None)
    step_id: str | None = Field(default=None)
    initiator_id: str | None = Field(default=None)
    timestamp_isot: str | None = Field(default=None)
    unix_time: int | None = Field(default=None)
    v2_engine: bool | None = Field(default=None)


class ReasoningTrace(V2CoreBase):
    """Stores hidden Chain-of-Thought (preserves "Thinking Tokens")."""

    thought_process: str = Field(
        min_length=1,
        pattern=r"\S",
        description="The raw chain-of-thought or reasoning trace. "
        "MUST be written strictly in English to ensure cross-run determinism.",
    )
    conclusion: str = Field(
        min_length=1,
        pattern=r"\S",
        description="The final conclusion derived from the reasoning. MUST be written strictly in English.",
    )
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence in the conclusion.")
    model_name: str | None = Field(default=None, description="The model used for reasoning.")
    token_usage: TokenUsage = Field(
        default_factory=lambda: TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
        description="Token usage statistics.",
    )


class TraceEvent(V2CoreBase):
    """Immutable event log item representing a distinct step or state change."""

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique event identifier.")
    v: int = Field(default=1, description="Schema version for forward compatibility and lazy upcasting.")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Event timestamp.")

    step_name: str = Field(
        ...,
        min_length=1,
        pattern=r"\S",
        description="Name of the step that generated this event.",
        json_schema_extra={"x-ui-label": "Step Name"},
    )

    event_type: Literal["input", "reasoning", "decision", "error", "output", "tombstone"] = Field(
        ..., description="Type of the event.", json_schema_extra={"x-ui-label": "Event Type"}
    )

    content: dict[str, Any] = Field(default_factory=dict, description="Structured content of the event.")
    reasoning: ReasoningTrace | None = Field(default=None, description="Associated reasoning trace.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata.")


class ErrorTraceEvent(TraceEvent):
    """Specific event representing a fail-fast error katkos."""

    event_type: Literal["error"] = "error"
    error_code: str = Field(description="The standard ErrorCode string.")
    error_message: str = Field(description="Detailed error message.")


class TombstoneEvent(TraceEvent):
    """Specific event representing GDPR-redacted or deleted data."""

    event_type: Literal["tombstone"] = "tombstone"
    redacted_hash: str = Field(description="Cryptographic hash or identifier of the original redacted data.")


class StepOutputDTO(V2CoreBase):
    """Strict execution trace payload format."""

    step_id: str = Field(description="The opaque DAG Step ID.")
    block_id: str = Field(description="The opaque PromptBlock ID.")
    data_type: Literal["text", "matrix", "unknown"] = Field(
        description="Inferred or explicitly parsed data type (e.g. matrix, text)."
    )
    payload: Any = Field(description="The actual data payload.")


# Resolve deferred annotations on ExecutionCoreFields (Pydantic V2 circular reference pattern).
# execution_core.py uses TYPE_CHECKING for TraceEvent types → annotations are strings.
# Now that TraceEvent, ErrorTraceEvent, TombstoneEvent are defined, resolve them.
from backend_v2.models.v2_core import ExecutionRecord

ExecutionCoreFields.model_rebuild()
ExecutionRecord.model_rebuild()


class WorkflowState(ExecutionCoreFields):
    """Aggregate root containing the execution trace and current state."""

    execution_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique execution identifier.")
    workflow_id: str = Field(
        ...,
        min_length=1,
        pattern=r"^([a-z]{2,5})_[a-zA-Z0-9]{8,}$",
        description="The ID of the workflow definition.",
    )
    trace_version: int = Field(default=0, description="Optimistic Concurrency Control version.")
    # Phase 2: status, execution_trace, execution_trace_storage_path,
    # context_variables, context_variables_storage_path are inherited
    # from ExecutionCoreFields (SSOT).

    workflow_name: str | None = Field(default=None, description="Human-readable name of the workflow.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp.")

    @property
    def start_time(self) -> datetime:
        return self.created_at

    def add_event(self, event: TraceEvent) -> WorkflowState:
        """Returns a new WorkflowState with the added event (Functional style)."""
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
        val = self.context_variables.get(key)
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
    def step_guard(self) -> Any | None:
        """Type-Safe Accessor for Guard Output."""
        return self.get_context("step_guard", GuardOutput)

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

    # --- Legacy / Sub-Step Accessors (Still useful for direct access if needed) ---

    @property
    def step_logician(self) -> Any | None:
        return self.get_context("step_logician", LogicianOutput)

    @property
    def step_falsifier(self) -> Any | None:
        return self.get_context("step_falsifier", FalsifierOutput)

    @property
    def step_profiler(self) -> Any | None:
        return self.get_context("step_profiler", ProfilerOutput)

    @property
    def step_archivist(self) -> Any | None:
        return self.get_context("step_archivist", ArchivistOutput)

    @property
    def step_overseer(self) -> Any | None:
        return self.get_context("step_overseer", OverseerOutput)

    @property
    def step_causal(self) -> Any | None:
        return self.get_context("step_causal", CausalOutput)

    @property
    def organization_id(self) -> str | None:
        return self.context_variables.get("organization_id")

    @property
    def user_id(self) -> str | None:
        return self.context_variables.get("user_id")

    @property
    def audit_results(self) -> dict[str, Any] | None:
        return self.context_variables.get("audit_results")

    @property
    def step_detector(self) -> Any | None:
        return self.get_context("step_detector", PerformativityOutput)

    @property
    def step_judge_cognitive(self) -> Any | None:
        return self.get_context("step_judge_cognitive", JudgeOutput)


class StateProjector:
    """In-Memory cache and reducer for Event Sourcing read models.

    Maintains a folded O(1) read model of the execution trace.
    """

    def __init__(self, trace: list[TraceEvent] | None = None) -> None:
        self._snapshot: dict[str, Any] = {}
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
        """Folds the entire trace into a strictly typed list of StepOutputDTOs.

        If max_tokens is provided, reads the trace backwards (newest first),
        accumulating events until the estimated token limit is reached,
        dropping older events to prevent LLM Token Explosion.
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
                event_str = json.dumps(event.content) if isinstance(event.content, dict) else str(event.content)
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
        output: list[StepOutputDTO] = []
        for step_id, step_output in self._snapshot.items():
            if not isinstance(step_output, dict):
                # Epic 43 Phase 2 Fail-Fast: Legacy unstructured traces are strictly forbidden.
                msg = (
                    f"Legacy flat trace detected for step '{step_id}'. "
                    "Zero-Compromise Pledge forbids unstructured data."
                )
                logger.error("[StateProjector] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)

                raise AppException(
                    status_code=500, message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED.name}
                )

            for block_id, payload in step_output.items():
                output.append(StepOutputDTO(step_id=step_id, block_id=block_id, data_type="unknown", payload=payload))
        return output

    def apply_delta(self, event: TraceEvent) -> None:
        """Applies a single event to the snapshot in O(1) time."""
        if event.v > self._schema_version:
            self._schema_version = event.v

        self._trace_length += 1

        if event.event_type in ["output", "input"]:
            self._snapshot[event.step_name] = event.content
        elif event.event_type == "tombstone":
            # For GDPR redactions, replace content with a tombstone marker
            redacted_hash = getattr(event, "redacted_hash", "unknown")
            self._snapshot[event.step_name] = {"_redacted": True, "hash": redacted_hash}
