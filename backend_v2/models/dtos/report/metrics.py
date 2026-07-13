"""Execution metrics DTO."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ExecutionMetricsDTO(BaseModel):
    """Metrics for the execution."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    total_atoms: int
    evaluated: int
    short_circuited_na: int
    duration_ms: Annotated[int, Field(default=0, description="Execution duration in milliseconds for observability")]
