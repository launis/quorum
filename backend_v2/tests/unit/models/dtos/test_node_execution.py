"""Unit tests for NodeExecutionUpdateDTO and Logic DTOs."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.domain.execution import ExecutionStep
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO, GlobalContextVarsDTO
from backend_v2.models.dtos.node_execution import (
    LogicEvaluationContextDTO,
    LogicNodeStateDTO,
    NodeExecutionUpdateDTO,
    StepOutputContentDTO,
)
from backend_v2.models.dtos.step_output import StepOutputDTO
from backend_v2.models.dtos.trace import ExecutionUpdateDTO
from backend_v2.models.enums import EntityPrefix, ExecutionStatus
from backend_v2.models.execution_core import ExecutionMetadata


def test_node_execution_update_dto() -> None:
    """Test NodeExecutionUpdateDTO creation, conversion to ExecutionUpdateDTO, and immutability."""
    step_id = generate_opaque_id(EntityPrefix.STEP)
    cv = ContextVariablesDTO(variables={"key": "val"})
    dto = NodeExecutionUpdateDTO(
        status=ExecutionStatus.RUNNING,
        execution_trace=[],
        frozen_context=None,
        context_variables=cv,
        error=None,
        steps=[ExecutionStep(id=step_id, label="Step 1", status=ExecutionStatus.PASSED)],
        expected_state_version=1,
        state_version=2,
    )

    update_dto = dto.to_execution_update_dto()
    assert isinstance(update_dto, ExecutionUpdateDTO)
    assert update_dto.status == ExecutionStatus.RUNNING
    assert update_dto.context_variables == cv
    assert update_dto.context_variables is not None
    assert update_dto.context_variables["key"] == "val"
    assert update_dto.steps is not None
    assert len(update_dto.steps) == 1
    assert update_dto.expected_state_version == 1
    assert update_dto.state_version == 2

    with pytest.raises(ValidationError):
        dto.status = ExecutionStatus.PASSED


def test_logic_node_state_dto() -> None:
    """Test LogicNodeStateDTO default factory and assignment."""
    step_id = generate_opaque_id(EntityPrefix.STEP)
    block_id = generate_opaque_id(EntityPrefix.PROMPT_BLOCK)
    dto = LogicNodeStateDTO(
        steps=[StepOutputDTO(step_id=step_id, block_id=block_id, data_type="text", payload="output")],
        dynamic_inputs={"k": "v"},
    )
    assert len(dto.steps) == 1
    assert dto.dynamic_inputs["k"] == "v"


def test_logic_evaluation_context_dto() -> None:
    """Test LogicEvaluationContextDTO creation and validations."""
    exe_id = generate_opaque_id(EntityPrefix.EXECUTION)
    wf_id = generate_opaque_id(EntityPrefix.WORKFLOW)
    step_id = generate_opaque_id(EntityPrefix.STEP)
    metadata = ExecutionMetadata(workflow_version=1)
    dto = LogicEvaluationContextDTO(
        execution_id=exe_id,
        workflow_id=wf_id,
        step_id=step_id,
        task_blueprint="logic_evaluator",
        metadata=metadata,
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(),
        target_locale="fi",
        user_role="auditor",
    )
    assert dto.execution_id == exe_id
    assert dto.workflow_id == wf_id
    assert dto.step_id == step_id
    assert dto.task_blueprint == "logic_evaluator"
    assert dto.target_locale == "fi"
    assert dto.user_role == "auditor"


def test_step_output_content_dto() -> None:
    """Test StepOutputContentDTO payload encapsulation and mapping protocol methods."""
    dto = StepOutputContentDTO(data={"score": 100})
    assert dto.data == {"score": 100}
    assert list(dto.items()) == [("score", 100)]
    assert dto["score"] == 100
    assert "score" in dto
    assert "missing" not in dto


def test_node_execution_update_dto_negative_extra_forbid() -> None:
    """Test NodeExecutionUpdateDTO rejects extra fields under extra='forbid'."""
    with pytest.raises(ValidationError):
        NodeExecutionUpdateDTO.model_validate(
            {
                "status": ExecutionStatus.RUNNING,
                "execution_trace": [],
                "forbidden_extra": "invalid",
            }
        )


def test_node_execution_update_dto_negative_state_version_bounds() -> None:
    """Test NodeExecutionUpdateDTO rejects state_version and expected_state_version below 1 (BVA min-1)."""
    with pytest.raises(ValidationError):
        NodeExecutionUpdateDTO(
            status=ExecutionStatus.RUNNING,
            execution_trace=[],
            expected_state_version=0,
        )
    with pytest.raises(ValidationError):
        NodeExecutionUpdateDTO(
            status=ExecutionStatus.RUNNING,
            execution_trace=[],
            state_version=0,
        )


def test_logic_node_state_dto_negative_extra_forbid() -> None:
    """Test LogicNodeStateDTO rejects extra fields under extra='forbid'."""
    with pytest.raises(ValidationError):
        LogicNodeStateDTO.model_validate({"unsupported_extra": 123})


def test_logic_evaluation_context_dto_negative_missing_fields() -> None:
    """Test LogicEvaluationContextDTO raises ValidationError on missing required fields."""
    with pytest.raises(ValidationError):
        LogicEvaluationContextDTO.model_validate({"execution_id": generate_opaque_id(EntityPrefix.EXECUTION)})


def test_step_output_content_dto_negative_extra_forbid_and_missing_key() -> None:
    """Test StepOutputContentDTO rejects unexpected extra fields and raises KeyError on missing key."""
    with pytest.raises(ValidationError):
        StepOutputContentDTO.model_validate({"data": {"score": 100}, "unexpected_extra": "bad"})
    dto = StepOutputContentDTO(data={"score": 100})
    with pytest.raises(KeyError):
        _ = dto["nonexistent"]
