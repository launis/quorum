"""Sensor validation context DTO for extractive sensor services."""

from __future__ import annotations

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase

__all__ = ["SensorValidationContextDTO"]


class SensorValidationContextDTO(V2CoreBase):
    """Encapsulates context parameters for sensor evaluation and anchor validation.

    Attributes:
        sub_task: Subtask identifier or category.
        execution_id: Parent execution ID.
        step_id: Current step ID.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    sub_task: Annotated[str, Field(description="Subtask identifier or category")]
    execution_id: Annotated[str | None, Field(default=None, description="Parent execution ID")] = None
    step_id: Annotated[str | None, Field(default=None, description="Current step ID")] = None
