"""Workflow State Management (Event Sourcing).

This module defines the new Event Sourcing state model, replacing the old mutable blackboard.
It uses an append-only log of `TraceEvent`s and a `ReasoningTrace` to capture cognitive processes.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ReasoningTrace(BaseModel):
    """Stores hidden Chain-of-Thought (preserves "Thinking Tokens")."""

    thought_process: str = Field(description="The raw chain-of-thought or reasoning trace.")
    conclusion: str = Field(description="The final conclusion derived from the reasoning.")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence in the conclusion.")
    model_name: str | None = Field(default=None, description="The model used for reasoning.")
    token_usage: dict[str, int] = Field(default_factory=dict, description="Token usage statistics.")

    model_config = ConfigDict(frozen=True)


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

    model_config = ConfigDict(frozen=True)

    def add_event(self, event: TraceEvent) -> WorkflowState:
        """Returns a new WorkflowState with the added event (Functional style)."""
        new_trace = self.execution_trace + [event]
        return self.model_copy(update={"execution_trace": new_trace})
