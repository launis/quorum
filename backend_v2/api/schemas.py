from datetime import datetime
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class ExecutionResponse(BaseModel):
    """API DTO for Workflow Execution Details.

    Standardizes the output format regardless of the underlying database schema.
    """

    execution_id: str = Field(..., validation_alias=AliasChoices("id", "execution_id"))
    start_time: datetime = Field(..., validation_alias=AliasChoices("started_at", "timestamp", "start_time"))
    status: str = Field(...)

    # Workflow Context
    workflow_id: str = Field(...)
    workflow_name: str | None = None

    # Data
    inputs: dict[str, Any] = Field(...)
    result: dict[str, Any] = Field(..., validation_alias=AliasChoices("results", "result"))

    # Expanded Visibility
    audit_results: dict[str, Any] = Field(...)
    usage: dict[str, Any] = Field(...)
    execution_trace: list[dict[str, Any]] = Field(...)

    # Metadata
    user_id: str | None = None
    organization_id: str | None = None

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
        strict=True,
        frozen=True,
    )
