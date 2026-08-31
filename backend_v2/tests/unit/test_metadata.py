from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookResult,
    HookState,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.hooks.metadata import inject_step_metadata
from backend_v2.models.execution_core import ExecutionMetadata


def test_inject_step_metadata_empty_state() -> None:
    """Test behavior when state is None."""
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )

    result = cast(HookResult, inject_step_metadata(None, deps))  # type: ignore[arg-type]

    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.delta == {}


def test_inject_step_metadata_missing_execution_id_fails() -> None:
    state = HookState(
        execution_id="",
        workflow_id="wf_1",
        step_id="step_1",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(target_locale="en"),
    )
    deps = MagicMock(spec=HookDependencies)
    with pytest.raises(AppException) as exc_info:
        inject_step_metadata(state, deps)
    assert exc_info.value.status_code == 500
    assert "state.execution_id is strictly required" in exc_info.value.message


def test_inject_step_metadata_missing_step_id_fails() -> None:
    state = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        step_id="",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(target_locale="en"),
    )
    deps = MagicMock(spec=HookDependencies)
    with pytest.raises(AppException) as exc_info:
        inject_step_metadata(state, deps)
    assert exc_info.value.status_code == 500
    assert "state.step_id is strictly required" in exc_info.value.message


def test_inject_step_metadata_missing_workflow_id_fails() -> None:
    state = HookState(
        execution_id="exec_1",
        workflow_id="",
        step_id="step_1",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(target_locale="en"),
    )
    deps = MagicMock(spec=HookDependencies)
    with pytest.raises(AppException) as exc_info:
        inject_step_metadata(state, deps)
    assert exc_info.value.status_code == 500
    assert "state.workflow_id is strictly required" in exc_info.value.message


def test_inject_step_metadata_missing_global_context_vars_fails() -> None:
    state = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        step_id="step_1",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(target_locale="en"),
    )
    object.__setattr__(state, "global_context_vars", None)
    deps = MagicMock(spec=HookDependencies)
    with pytest.raises(AppException) as exc_info:
        inject_step_metadata(state, deps)
    assert exc_info.value.status_code == 500
    assert "state.global_context_vars is strictly required" in exc_info.value.message


def test_inject_step_metadata_custom_values() -> None:
    """Test metadata injection when specific IDs and initiator are provided."""
    state = HookState(
        execution_id="exec_555",
        workflow_id="wf_999",
        step_id="step_123",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(vars={"_sys_initiator_id": "usr_777"}),
        metadata=ExecutionMetadata(target_locale="en"),
    )
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )

    result = cast(HookResult, inject_step_metadata(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    meta = result.state_delta.delta["_step_metadata"]
    assert "step_metadata" not in result.state_delta.delta, "Hook must use underscore-prefixed SSOT key"
    assert meta["execution_id"] == "exec_555"
    assert meta["workflow_id"] == "wf_999"
    assert meta["step_id"] == "step_123"
    assert meta["initiator_id"] == "usr_777"

    audit_sig = result.state_delta.delta["_audit_signature"]
    assert audit_sig.startswith("step_123:exec_555:")


def test_inject_step_metadata_validation_failure() -> None:
    """Test that strict Pydantic validation fails if context vars contain invalid types."""
    # Since strict=True, passing an integer instead of a string for initiator_id should fail
    state = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        step_id="step_1",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(vars={"_sys_initiator_id": 12345}),  # Int instead of str
        metadata=ExecutionMetadata(target_locale="en"),
    )
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )

    with pytest.raises(AppException) as exc_info:
        inject_step_metadata(state, deps)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.INVALID_OUTPUT_SCHEMA.value
    assert "strictly validate global context" in exc_info.value.message
