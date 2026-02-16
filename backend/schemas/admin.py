from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class QueueStats(BaseModel):
    """Statistics for the Async Job Queue (ArQ)."""

    model_config = ConfigDict(from_attributes=True, strict=True)

    queued_jobs: int = Field(..., description="Number of jobs currently waiting in the queue.")
    active_jobs: int = Field(..., description="Number of jobs currently being processed.")
    dead_jobs: int = Field(..., description="Number of jobs in the dead letter queue (failed).")


class AdminOperationResponse(BaseModel):
    """Generic response for administrative operations."""

    status: str = Field(..., description="Status of the operation (e.g. 'completed', 'failed').")
    message: str = Field(..., description="Human readable result message.")
    output: str | None = Field(None, description="Optional command output or details.")
    details: Any | None = Field(None, description="Additional structured details.")

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("status", "message")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class AsyncJobResponse(BaseModel):
    """Standard response for asynchronous operations."""

    job_id: str = Field(..., description="Unique Identifier for the background job.")
    status: str = Field(..., description="Initial status (e.g. 'queued', 'starting').")
    message: str | None = Field(None, description="Optional detail message.")

    model_config = ConfigDict(frozen=True, strict=True)
