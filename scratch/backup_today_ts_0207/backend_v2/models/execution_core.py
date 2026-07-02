"""Shared SSOT structural core for workflow executions.

This module is an intentional LEAF MODULE in the import graph.
It uses TYPE_CHECKING for TraceEvent types from state.py to prevent
the circular import: state.py → execution_core.py → state.py.
Pydantic resolves deferred annotations via model_rebuild() in state.py.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any

from pydantic import Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.enums import ExecutionStatus, LaxExecutionStatus

if TYPE_CHECKING:
    from backend_v2.models.state import ErrorTraceEvent, TombstoneEvent, TraceEvent


class ExecutionCoreFields(V2CoreBase):
    """The Single Source of Truth (SSOT) structural core for workflow executions.

    Inherited by both the active domain state (WorkflowState) and the
    historical persistent database record (ExecutionRecord).

    Attributes:
        status: Current lifecycle status of the execution.
        execution_trace: Append-only log of all trace events.
        execution_trace_storage_path: Cloud Storage offload path for large traces.
        context_variables: Dynamic blackboard for cross-step data sharing.
        context_variables_storage_path: Cloud Storage offload path for large context.
    """

    status: Annotated[
        LaxExecutionStatus,
        Field(default=ExecutionStatus.PENDING, description="Current status of the workflow execution."),
    ]
    execution_trace: Annotated[
        list[ErrorTraceEvent | TombstoneEvent | TraceEvent],
        Field(default_factory=list, description="Immutable log of all events."),
    ]
    execution_trace_storage_path: Annotated[
        str | None,
        Field(default=None, description="Path to offloaded trace JSON in Cloud Storage."),
    ]
    context_variables: Annotated[
        dict[str, Any],
        Field(default_factory=dict, description="Current snapshots of context variables (the dynamic blackboard)."),
    ]
    context_variables_storage_path: Annotated[
        str | None,
        Field(default=None, description="Path to offloaded context variables JSON in Cloud Storage."),
    ]
