from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class QueueStats(BaseModel):
    """Statistics for the Async Job Queue (ArQ)."""

    model_config = ConfigDict(from_attributes=True)

    queued_jobs: int = Field(..., description="Number of jobs currently waiting in the queue.")
    active_jobs: int = Field(..., description="Number of jobs currently being processed.")
    dead_jobs: int = Field(..., description="Number of jobs in the dead letter queue (failed).")


class AdminOperationResponse(BaseModel):
    """Generic response for administrative operations."""

    status: str = Field(..., description="Status of the operation (e.g. 'completed', 'failed').")
    message: str = Field(..., description="Human readable result message.")
    output: str | None = Field(None, description="Optional command output or details.")
    details: Any | None = Field(None, description="Additional structured details.")
