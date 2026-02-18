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
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Event timestamp."
    )

    step_name: str = Field(
        ...,
        description="Name of the step that generated this event.",
        json_schema_extra={"x-ui-label": "Step Name"}
    )

    event_type: Literal["input", "reasoning", "decision", "error", "output"] = Field(
        ...,
        description="Type of the event.",
        json_schema_extra={"x-ui-label": "Event Type"}
    )

    content: dict[str, Any] = Field(
        default_factory=dict, description="Structured content of the event."
    )
    reasoning: ReasoningTrace | None = Field(
        default=None, description="Associated reasoning trace."
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata."
    )



    model_config = ConfigDict(frozen=True)

    @field_validator("step_name")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class WorkflowState(BaseModel):
    """Aggregate root containing the execution trace and current state."""

    execution_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Unique execution identifier."
    )
    workflow_id: str = Field(..., description="The ID of the workflow definition.")

    status: Literal["pending", "running", "completed", "failed"] = Field(
        default="pending",
        description="Current status of the workflow execution.",
        json_schema_extra={"x-ui-label": "Status"}
    )

    execution_trace: list[TraceEvent] = Field(
        default_factory=list, description="Immutable log of all events."
    )
    context_variables: dict[str, Any] = Field(
        default_factory=dict, description="Current snapshots of context variables."
    )
    workflow_name: str | None = Field(
        default=None, description="Human-readable name of the workflow."
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp."
    )

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

    def add_event(self, event: TraceEvent) -> "WorkflowState":
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

    @property
    def step_analyst(self) -> Any | None:
        return self.context_variables.get("step_analyst")

    @property
    def step_profiler(self) -> Any | None:
        return self.context_variables.get("step_profiler")

    @property
    def step_archivist(self) -> Any | None:
        return self.context_variables.get("step_archivist")

    @property
    def step_logician(self) -> Any | None:
        return self.context_variables.get("step_logician")

    @property
    def step_falsifier(self) -> Any | None:
        return self.context_variables.get("step_falsifier")

    @property
    def step_causal(self) -> Any | None:
        return self.context_variables.get("step_causal")

    @property
    def step_detector(self) -> Any | None:
        return self.context_variables.get("step_detector")

    @property
    def step_overseer(self) -> Any | None:
        return self.context_variables.get("step_overseer")

    @property
    def step_panel(self) -> Any | None:
        return self.context_variables.get("step_panel")

    @property
    def step_judge(self) -> Any | None:
        return self.context_variables.get("step_judge")

    @property
    def step_judge_cognitive(self) -> Any | None:
        return self.context_variables.get("step_judge_cognitive")

    @property
    def step_coach(self) -> Any | None:
        return self.context_variables.get("step_coach")

    @property
    def step_interaction(self) -> Any | None:
        return self.context_variables.get("step_interaction")
        
    @property
    def audit_results(self) -> Any | None:
        return self.context_variables.get("audit_results")

    @property
    def step_guard(self) -> Any | None:
        return self.context_variables.get("step_guard")
    
    @property
    def step_xai(self) -> Any | None:
        return self.context_variables.get("step_xai")

    @property
    def organization_id(self) -> str | None:
        return self.context_variables.get("organization_id")
    
    @property
    def user_id(self) -> str | None:
        return self.context_variables.get("user_id")

