"""Workflow State Management (Event Sourcing).

This module defines the new Event Sourcing state model, replacing the old mutable blackboard.
It uses an append-only log of `TraceEvent`s and a `ReasoningTrace` to capture cognitive processes.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReasoningTrace(BaseModel):
    """Stores hidden Chain-of-Thought (preserves "Thinking Tokens")."""

    thought_process: str = Field(description="The raw chain-of-thought or reasoning trace.")
    conclusion: str = Field(description="The final conclusion derived from the reasoning.")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence in the conclusion.")
    model_name: str | None = Field(default=None, description="The model used for reasoning.")
    token_usage: dict[str, int] = Field(default_factory=dict, description="Token usage statistics.")

    model_config = ConfigDict(frozen=True)

    @field_validator("thought_process", "conclusion")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class TraceEvent(BaseModel):
    """Immutable event log item representing a distinct step or state change."""

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique event identifier.")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Event timestamp.")

    step_name: str = Field(
        ..., description="Name of the step that generated this event.", json_schema_extra={"x-ui-label": "Step Name"}
    )

    event_type: Literal["input", "reasoning", "decision", "error", "output"] = Field(
        ..., description="Type of the event.", json_schema_extra={"x-ui-label": "Event Type"}
    )

    content: dict[str, Any] = Field(default_factory=dict, description="Structured content of the event.")
    reasoning: ReasoningTrace | None = Field(default=None, description="Associated reasoning trace.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata.")

    model_config = ConfigDict(frozen=True)

    @field_validator("step_name")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class WorkflowState(BaseModel):
    """Aggregate root containing the execution trace and current state."""

    execution_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique execution identifier.")
    workflow_id: str = Field(..., description="The ID of the workflow definition.")

    status: Literal["pending", "running", "completed", "failed"] = Field(
        default="pending",
        description="Current status of the workflow execution.",
        json_schema_extra={"x-ui-label": "Status"},
    )

    execution_trace: list[TraceEvent] = Field(default_factory=list, description="Immutable log of all events.")
    context_variables: dict[str, Any] = Field(
        default_factory=dict, description="Current snapshots of context variables."
    )
    workflow_name: str | None = Field(default=None, description="Human-readable name of the workflow.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp.")

    @property
    def start_time(self) -> datetime:
        return self.created_at

    @property
    def reasoning_context(self) -> Any | None:
        """Legacy accessor for reasoning context (now largely superseded by step_analyst)."""
        return self.context_variables.get("reasoning_context")

    model_config = ConfigDict(frozen=True)

    @field_validator("workflow_id")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

    def add_event(self, event: TraceEvent) -> WorkflowState:
        """Returns a new WorkflowState with the added event (Functional style)."""
        new_trace = self.execution_trace + [event]
        return self.model_copy(update={"execution_trace": new_trace})

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
            # Avoid circular import at module level
            from backend.utils.pydantic_utils import inflate

            return inflate(val, model_class)

        return val

    # --- Type-Safe Accessors for Common Steps (Bridge for State Presenter) ---
    # These properties perform Lazy Inflation: they convert the raw dict from context_variables
    # into a strict Pydantic model on access. This ensures that the backend logic always
    # works with validated objects, while the database remains a simple JSON store.

    @property
    def step_guard(self) -> Any | None:
        """Type-Safe Accessor for Guard Output."""
        from backend.models.domain.guard import GuardOutput

        return self.get_context("step_guard", GuardOutput)

    @property
    def step_interaction(self) -> Any | None:
        """Type-Safe Accessor for Interaction Analysis."""
        from backend.models.domain.interaction import InteractionAnalysis

        return self.get_context("step_interaction", InteractionAnalysis)

    @property
    def step_analyst(self) -> Any | None:
        """Type-Safe Accessor for Analyst Output."""
        from backend.models.domain.analyst import AnalystOutput

        return self.get_context("step_analyst", AnalystOutput)

    @property
    def step_panel(self) -> Any | None:
        """Type-Safe Accessor for Panel Output (Fused)."""
        from backend.models.domain.panel import PanelOutput

        return self.get_context("step_panel", PanelOutput)

    @property
    def step_judge(self) -> Any | None:
        """Type-Safe Accessor for Judge Output."""
        from backend.models.domain.judge import JudgeOutput

        return self.get_context("step_judge", JudgeOutput)

    @property
    def step_coach(self) -> Any | None:
        """Type-Safe Accessor for Coach Output."""
        from backend.models.domain.coach import CoachingPlan

        return self.get_context("step_coach", CoachingPlan)

    @property
    def step_xai(self) -> Any | None:
        """Type-Safe Accessor for XAI Reporter Output."""
        from backend.models.domain.xai import XAIOutput

        return self.get_context("step_xai", XAIOutput)

    # --- Legacy / Sub-Step Accessors (Still useful for direct access if needed) ---

    @property
    def step_logician(self) -> Any | None:
        from backend.models.domain.logician import LogicianOutput

        return self.get_context("step_logician", LogicianOutput)

    @property
    def step_falsifier(self) -> Any | None:
        from backend.models.domain.falsifier import FalsifierOutput

        return self.get_context("step_falsifier", FalsifierOutput)

    @property
    def step_profiler(self) -> Any | None:
        from backend.models.domain.profiler import ProfilerOutput

        return self.get_context("step_profiler", ProfilerOutput)

    @property
    def step_archivist(self) -> Any | None:
        from backend.models.domain.archivist import ArchivistOutput

        return self.get_context("step_archivist", ArchivistOutput)

    @property
    def step_overseer(self) -> Any | None:
        from backend.models.domain.overseer import OverseerOutput

        return self.get_context("step_overseer", OverseerOutput)

    @property
    def step_causal(self) -> Any | None:
        from backend.models.domain.causal import CausalOutput

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
        from backend.models.domain.performativity import PerformativityOutput

        return self.get_context("step_detector", PerformativityOutput)

    @property
    def step_judge_cognitive(self) -> Any | None:
        from backend.models.domain.judge import JudgeOutput

        return self.get_context("step_judge_cognitive", JudgeOutput)

