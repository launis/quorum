"""Execution Envelope base model.

Provides StepExecutionEnvelope as a foundational leaf model to prevent circular
imports between domain models and state management.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase

__all__ = ["StepExecutionEnvelope"]


class StepExecutionEnvelope(V2CoreBase):
    """Base envelope for execution traces to prevent repetition and enforce DRY architecture.

    Attributes:
        execution_id: Unique execution identifier.
        workflow_id: Workflow definition identifier.
        step_id: Step definition identifier.
        initiator_id: Initiator user or system identifier.
        timestamp_isot: ISO timestamp string.
        unix_time: Unix epoch time.
        v2_engine: Engine flag indicator.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    execution_id: Annotated[str | None, Field(default=None)] = None
    workflow_id: Annotated[str | None, Field(default=None)] = None
    step_id: Annotated[str | None, Field(default=None)] = None
    initiator_id: Annotated[str | None, Field(default=None)] = None
    timestamp_isot: Annotated[str | None, Field(default=None)] = None
    unix_time: Annotated[int | None, Field(default=None)] = None
    v2_engine: Annotated[bool | None, Field(default=None)] = None
