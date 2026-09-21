"""Node execution DTOs for DAG orchestration and logic step evaluation."""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.execution import ExecutionStep, ExecutionStepState
from backend_v2.models.domain.inputs import DomainInputValue
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO, GlobalContextVarsDTO
from backend_v2.models.dtos.step_output import StepOutputDTO
from backend_v2.models.dtos.trace import ExecutionUpdateDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import ErrorTraceEvent, TombstoneEvent, TraceEvent

__all__ = [
    "LogicEvaluationContextDTO",
    "LogicNodeStateDTO",
    "NodeExecutionUpdateDTO",
    "StepOutputContentDTO",
]


class NodeExecutionUpdateDTO(V2CoreBase):
    """Encapsulates parameters for updating execution state during commit_trace.

    Attributes:
        status: Target execution status.
        execution_trace: Current trace event list.
        step_states: Step states mapping.
        frozen_context: Frozen context snapshot.
        context_variables: Context variables mapping.
        error: Error message if failed.
        steps: Execution steps list.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    status: Annotated[ExecutionStatus, Field(description="Target execution status")]
    execution_trace: Annotated[
        list[ErrorTraceEvent | TombstoneEvent | TraceEvent],
        Field(description="Current trace event list"),
    ]
    step_states: Annotated[dict[str, ExecutionStepState], Field(description="Step states mapping")]
    frozen_context: Annotated[Any | None, Field(default=None, description="Frozen context snapshot")] = None
    context_variables: Annotated[
        dict[str, Any] | None, Field(default=None, description="Context variables mapping")
    ] = None
    error: Annotated[str | None, Field(default=None, description="Error message if failed")] = None
    steps: Annotated[list[ExecutionStep] | None, Field(default=None, description="Execution steps list")] = None

    def to_execution_update_dto(self) -> ExecutionUpdateDTO:
        """Convert to ExecutionUpdateDTO for repository persistence.

        Returns:
            ExecutionUpdateDTO populated with instance fields.
        """
        data: dict[str, Any] = {
            "status": self.status,
            "execution_trace": self.execution_trace,
            "step_states": self.step_states,
            "frozen_context": self.frozen_context,
            "context_variables": self.context_variables,
            "error": self.error,
        }
        if self.steps is not None:
            data["steps"] = self.steps
        return ExecutionUpdateDTO.model_validate(data)


class LogicNodeStateDTO(V2CoreBase):
    """Encapsulates the state snapshot for logic node evaluation.

    Attributes:
        steps: Projector snapshot steps list.
        dynamic_inputs: Dynamic inputs dictionary.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    steps: Annotated[
        list[StepOutputDTO],
        Field(default_factory=list, description="Projector snapshot steps list"),
    ] = Field(default_factory=list)
    dynamic_inputs: Annotated[
        dict[str, DomainInputValue],
        Field(default_factory=dict, description="Dynamic inputs dictionary"),
    ] = Field(default_factory=dict)


class LogicEvaluationContextDTO(V2CoreBase):
    """Encapsulates execution context parameters for logic step evaluation.

    Attributes:
        execution_id: Execution ID.
        workflow_id: Workflow ID.
        step_id: Step ID.
        task_blueprint: Blueprint ID.
        metadata: Execution metadata.
        global_context_vars: Global context variables.
        inputs: Execution inputs container.
        target_locale: Target locale code.
        user_role: User role.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    execution_id: Annotated[str, Field(description="Execution ID")]
    workflow_id: Annotated[str, Field(description="Workflow ID")]
    step_id: Annotated[str, Field(description="Step ID")]
    task_blueprint: Annotated[str, Field(description="Blueprint ID")]
    metadata: Annotated[ExecutionMetadata, Field(description="Execution metadata")]
    global_context_vars: Annotated[
        GlobalContextVarsDTO,
        Field(default_factory=GlobalContextVarsDTO, description="Global context variables"),
    ] = Field(default_factory=GlobalContextVarsDTO)
    inputs: Annotated[
        ExecutionInputsDTO,
        Field(default_factory=ExecutionInputsDTO, description="Execution inputs container"),
    ] = Field(default_factory=ExecutionInputsDTO)
    target_locale: Annotated[str | None, Field(default=None, description="Target locale code")] = None
    user_role: Annotated[str | None, Field(default=None, description="User role")] = None


class StepOutputContentDTO(V2CoreBase):
    """Encapsulates content payload for step output or input trace events.

    Attributes:
        data: Structured event payload content.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    data: Annotated[
        dict[str, Any],
        Field(default_factory=dict, description="Structured event payload content"),
    ] = Field(default_factory=dict)
