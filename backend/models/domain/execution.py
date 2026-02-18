"""Execution Domain Models.

This module defines strict Pydantic models for Workflow Executions.
"""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.models.state import WorkflowState


class ExecutionRecord(BaseModel):
    """Strict model for a stored Workflow Execution."""
    
    id: str = Field(..., description="Unique Execution ID.")
    status: str = Field(..., description="Current status (e.g. running, completed, failed).")
    
    # We store the state dump in 'results'. 
    # Using WorkflowState type here forces validation on load.
    results: WorkflowState | Dict[str, Any] | None = Field(
        default=None, 
        description="The full workflow state dump."
    )
    
    current_step: str | None = Field(default=None, description="ID of the current step.")
    execution_trace_count: int | None = Field(default=0, description="Number of events in trace.")
    
    workflow_id: str | None = Field(default=None, description="ID of the workflow definition.")
    organization_id: str | None = Field(default=None, description="Owner Organization ID.")
    user_id: str | None = Field(default=None, description="Owner User ID.")
    
    created_at: datetime | None = Field(default=None, description="Creation timestamp.")
    started_at: datetime | None = Field(default=None, description="Execution start time.")
    completed_at: datetime | None = Field(default=None, description="Execution completion time.")
    
    cost_estimate: float | None = Field(default=0.0, description="Estimated cost in USD.")
    
    # Metadata for filtering/matrices
    settings: Dict[str, Any] | None = Field(default=None, description="Execution settings (e.g. matrix_id).")
    
    # Error message if failed
    error: str | None = Field(default=None, description="Error message if execution failed.")

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("id", "status")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

    @field_validator("cost_estimate")
    @classmethod
    def validate_non_negative(cls, v: float | None) -> float | None:
        if v is not None and v < 0:
            raise ValueError("Cost cannot be negative.")
        return v
    
    @field_validator('created_at', 'started_at', 'completed_at', mode='before')
    @classmethod
    def parse_datetime(cls, v: Any) -> Any:
        if isinstance(v, str):
            # Handle ISO strings
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v
