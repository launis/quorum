"""Admin Schemas."""

from pydantic import BaseModel, ConfigDict, Field


class QueueStats(BaseModel):
    """Statistics for the Async Job Queue (ArQ)."""

    model_config = ConfigDict(from_attributes=True)

    queued_jobs: int = Field(..., description="Number of jobs currently waiting in the queue.")
    active_jobs: int = Field(..., description="Number of jobs currently being processed.")
    dead_jobs: int = Field(..., description="Number of jobs in the dead letter queue (failed).")
