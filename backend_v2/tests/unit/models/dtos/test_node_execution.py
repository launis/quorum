"""Unit tests for NodeExecutionUpdateDTO and Logic DTOs."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.execution import ExecutionStep, ExecutionStepState
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO, GlobalContextVarsDTO
from backend_v2.models.dtos.node_execution import (
    LogicEvaluationContextDTO,
    LogicNodeStateDTO,
    NodeExecutionUpdateDTO,
    StepOutputContentDTO,
)
from backend_v2.models.dtos.step_output import StepOutputDTO
from backend_v2.models.dtos.trace import ExecutionUpdateDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.execution_core import ExecutionMetadata


def test_node_execution_update_dto() -> None:
    """Test NodeExecutionUpdateDTO creation, conversion to ExecutionUpdateDTO, and immutability."""
    step_state = ExecutionStepState(
        id="stp_1234567890abcdef",
        label="Step 1",
        status=ExecutionStatus.PASSED,
    )
    dto = NodeExecutionUpdateDTO(
        status=ExecutionStatus.RUNNING,
        execution_trace=[],
        step_states={"stp_1234567890abcdef": step_state},
        frozen_context=None,
        context_variables={"key": "val"},
        error=None,
        steps=[ExecutionStep(id="stp_1234567890abcdef", label="Step 1", status=ExecutionStatus.PASSED)],
    )

    update_dto = dto.to_execution_update_dto()
    assert isinstance(update_dto, ExecutionUpdateDTO)
    assert update_dto.status == ExecutionStatus.RUNNING
    assert update_dto.step_states == {"stp_1234567890abcdef": step_state}
    assert update_dto.context_variables == {"key": "val"}
    assert update_dto.steps is not None
    assert len(update_dto.steps) == 1

    with pytest.raises(ValidationError):
        dto.status = ExecutionStatus.PASSED  # type: ignore[misc]


def test_logic_node_state_dto() -> None:
    """Test LogicNodeStateDTO default factory and assignment."""
    dto = LogicNodeStateDTO(
        steps=[StepOutputDTO(step_id="stp_1", block_id="blk_1", data_type="text", payload="output")],
        dynamic_inputs={"k": "v"},
    )
    assert len(dto.steps) == 1
    assert dto.dynamic_inputs["k"] == "v"


def test_logic_evaluation_context_dto() -> None:
    """Test LogicEvaluationContextDTO creation and validations."""
    metadata = ExecutionMetadata(workflow_version=1)
    dto = LogicEvaluationContextDTO(
        execution_id="exe_1",
        workflow_id="wf_1",
        step_id="stp_1",
        task_blueprint="bp_1",
        metadata=metadata,
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(),
        target_locale="fi",
        user_role="auditor",
    )
    assert dto.execution_id == "exe_1"
    assert dto.workflow_id == "wf_1"
    assert dto.step_id == "stp_1"
    assert dto.task_blueprint == "bp_1"
    assert dto.target_locale == "fi"
    assert dto.user_role == "auditor"


def test_step_output_content_dto() -> None:
    """Test StepOutputContentDTO payload encapsulation."""
    dto = StepOutputContentDTO(data={"score": 100})
    assert dto.data == {"score": 100}


def test_node_execution_update_dto_negative_extra_forbid() -> None:
    """Test NodeExecutionUpdateDTO rejects extra fields under extra='forbid'."""
    with pytest.raises(ValidationError):
        NodeExecutionUpdateDTO(
            status=ExecutionStatus.RUNNING,
            execution_trace=[],
            step_states={},
            forbidden_extra="invalid",  # type: ignore[call-arg]
        )


def test_logic_node_state_dto_negative_extra_forbid() -> None:
    """Test LogicNodeStateDTO rejects extra fields under extra='forbid'."""
    with pytest.raises(ValidationError):
        LogicNodeStateDTO(unsupported_extra=123)  # type: ignore[call-arg]


def test_logic_evaluation_context_dto_negative_missing_fields() -> None:
    """Test LogicEvaluationContextDTO raises ValidationError on missing required fields."""
    with pytest.raises(ValidationError):
        LogicEvaluationContextDTO(execution_id="exe_1")  # type: ignore[call-arg]


def test_step_output_content_dto_negative_extra_forbid() -> None:
    """Test StepOutputContentDTO rejects unexpected extra fields."""
    with pytest.raises(ValidationError):
        StepOutputContentDTO(data={"score": 100}, unexpected_extra="bad")  # type: ignore[call-arg]
