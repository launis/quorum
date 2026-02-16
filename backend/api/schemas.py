from datetime import datetime
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class ExecutionResponse(BaseModel):
    """API DTO for Workflow Execution Details.
    
    Standardizes the output format regardless of the underlying database schema.
    """

    execution_id: str = Field(..., validation_alias=AliasChoices("id", "execution_id"))
    start_time: datetime | None = Field(None, validation_alias=AliasChoices("started_at", "timestamp", "start_time"))
    status: str = Field(default="unknown")

    # Workflow Context
    workflow_id: str | None = None
    workflow_name: str | None = None

    # Data
    inputs: dict[str, Any] = Field(default_factory=dict)
    result: dict[str, Any] = Field(default_factory=dict, validation_alias=AliasChoices("results", "result"))

    # Expanded Visibility
    audit_results: dict[str, Any] = Field(default_factory=dict)
    usage: dict[str, Any] = Field(default_factory=dict)
    execution_trace: list[dict[str, Any]] = Field(default_factory=list)

    # Metadata
    user_id: str | None = None
    organization_id: str | None = None

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",  # Include any other fields from DB automatically
        json_encoders={datetime: lambda v: v.isoformat()}
    )
