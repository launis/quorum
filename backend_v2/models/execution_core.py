"""Shared SSOT structural core for workflow executions.

This module is an intentional LEAF MODULE in the import graph.
It uses TYPE_CHECKING for TraceEvent types from state.py to prevent
the circular import: state.py → execution_core.py → state.py.
Pydantic resolves deferred annotations via model_rebuild() in state.py.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.enums import ExecutionStatus, LaxExecutionStatus

if TYPE_CHECKING:
    from backend_v2.models.state import ErrorTraceEvent, TombstoneEvent, TraceEvent


class ExecutionMetadata(V2CoreBase):
    """Strictly typed metadata for execution runtime parameters and provenance."""

    model_config = ConfigDict(strict=True, extra="forbid")

    target_locale: Annotated[
        str,
        Field(description="Target locale for outputs, e.g. 'fi', 'en'."),
    ]
    profile_id: Annotated[
        str | None,
        Field(default=None, description="Active or default profile ID for the execution."),
    ] = None
    matrix_sampling_strategy: Annotated[
        int,
        Field(default=10, description="Sampling strategy limit for Matrix Flattening."),
    ] = 10
    workflow_version: Annotated[
        int,
        Field(default=1, description="Version number of the executing workflow."),
    ] = 1
    user_id: Annotated[
        str | None,
        Field(default=None, description="Executing user ID."),
    ] = None
    organization_id: Annotated[
        str | None,
        Field(default=None, description="Organization ID owning the execution."),
    ] = None
    global_context_vars: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Global context variables for hooks."),
    ] = None
    execution_summary: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Summary fingerprint of execution."),
    ] = None
    step_metrics: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Per-step performance and cost metrics."),
    ] = None
    dag_cost_usd: Annotated[
        float | None,
        Field(default=None, description="Total financial DAG execution cost in USD."),
    ] = None
    prompt_tokens: Annotated[
        int | None,
        Field(default=None, description="Total prompt tokens consumed."),
    ] = None
    completion_tokens: Annotated[
        int | None,
        Field(default=None, description="Total completion tokens generated."),
    ] = None
    cached_tokens: Annotated[
        int | None,
        Field(default=None, description="Total tokens read from context cache."),
    ] = None
    reasoning_tokens: Annotated[
        int | None,
        Field(default=None, description="Total thinking/reasoning tokens."),
    ] = None


class ExecutionCoreFields(V2CoreBase):
    """The Single Source of Truth (SSOT) structural core for workflow executions.

    Inherited by both the active domain state (WorkflowState) and the
    historical persistent database record (ExecutionRecord).

    Attributes:
        status: Current lifecycle status of the execution.
        target_locale: Target locale code for execution output.
        execution_trace: Append-only log of all trace events.
        execution_trace_storage_path: Cloud Storage offload path for large traces.
        context_variables: Dynamic blackboard for cross-step data sharing.
        context_variables_storage_path: Cloud Storage offload path for large context.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    status: Annotated[
        LaxExecutionStatus,
        Field(default=ExecutionStatus.PENDING, description="Current status of the workflow execution."),
    ]
    target_locale: Annotated[
        str,
        Field(default="en", description="Target locale code for execution outputs, e.g. 'fi'."),
    ] = "en"
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
