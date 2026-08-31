"""Unit tests for validation hooks (verify_structure, verify_output_language, verify_anomaly)."""

from typing import Any, cast

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDeltaDTO,
    HookDependencies,
    HookState,
)
from backend_v2.exceptions import AppException
from backend_v2.hooks.validation import (
    verify_anomaly,
    verify_output_language,
    verify_structure,
)
from backend_v2.models.execution_core import ExecutionMetadata


class MockRepository:
    """Mock repository."""


def test_verify_structure_missing_state_raises() -> None:
    """Test that missing state in verify_structure raises EMPTY_INPUT."""
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepository()),
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=cast(Any, MockRepository()),
        prompt_block_repo=cast(Any, MockRepository()),
        output_profile_repo=cast(Any, MockRepository()),
        identity_repo=cast(Any, MockRepository()),
        audit_repo=cast(Any, MockRepository()),
        system_repo=cast(Any, MockRepository()),
    )
    with pytest.raises(AppException) as exc_info:
        verify_structure(cast(Any, None), deps)

    assert exc_info.value.error_code == "EMPTY_INPUT"


def test_verify_structure_valid_inputs() -> None:
    """Test verify_structure with valid content."""
    state = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        step_id="step_1",
        metadata=ExecutionMetadata(target_locale="fi"),
        inputs=ExecutionInputsDTO(raw_inputs={"reflection_text": "Tämä on riittävän pitkä vastaus analyysiin."}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepository()),
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=cast(Any, MockRepository()),
        prompt_block_repo=cast(Any, MockRepository()),
        output_profile_repo=cast(Any, MockRepository()),
        identity_repo=cast(Any, MockRepository()),
        audit_repo=cast(Any, MockRepository()),
        system_repo=cast(Any, MockRepository()),
    )
    result = verify_structure(state, deps)
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta is not None
    assert "validation_result" in delta
    assert delta["validation_result"]["is_valid"] is True


def test_verify_structure_empty_input_warning_raises() -> None:
    """Test verify_structure with empty field raises VALIDATION_FAILED."""
    state = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        step_id="step_1",
        metadata=ExecutionMetadata(target_locale="fi"),
        inputs=ExecutionInputsDTO(raw_inputs={"reflection_text": "   "}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepository()),
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=cast(Any, MockRepository()),
        prompt_block_repo=cast(Any, MockRepository()),
        output_profile_repo=cast(Any, MockRepository()),
        identity_repo=cast(Any, MockRepository()),
        audit_repo=cast(Any, MockRepository()),
        system_repo=cast(Any, MockRepository()),
    )
    with pytest.raises(AppException) as exc_info:
        verify_structure(state, deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"


def test_verify_output_language_no_leakage() -> None:
    """Test verify_output_language when target language is Finnish and text is in Finnish."""
    state = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        step_id="step_1",
        metadata=ExecutionMetadata(target_locale="fi"),
        inputs=ExecutionInputsDTO(raw_inputs={"evaluation_notes": "Tämä arviointi on tehty suomeksi."}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepository()),
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=cast(Any, MockRepository()),
        prompt_block_repo=cast(Any, MockRepository()),
        output_profile_repo=cast(Any, MockRepository()),
        identity_repo=cast(Any, MockRepository()),
        audit_repo=cast(Any, MockRepository()),
        system_repo=cast(Any, MockRepository()),
    )
    result = verify_output_language(state, deps)
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta == {}


def test_verify_output_language_detects_english_leakage() -> None:
    """Test verify_output_language when English stop words leak into Finnish target."""
    state = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        step_id="step_1",
        metadata=ExecutionMetadata(target_locale="fi"),
        inputs=ExecutionInputsDTO(raw_inputs={"evaluation_notes": "This is from the report with that finding."}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepository()),
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=cast(Any, MockRepository()),
        prompt_block_repo=cast(Any, MockRepository()),
        output_profile_repo=cast(Any, MockRepository()),
        identity_repo=cast(Any, MockRepository()),
        audit_repo=cast(Any, MockRepository()),
        system_repo=cast(Any, MockRepository()),
    )
    result = verify_output_language(state, deps)
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta is not None
    assert "_system_warnings" in delta
    assert len(delta["_system_warnings"]) == 1


def test_verify_anomaly_detected() -> None:
    """Test verify_anomaly when Guttman inversion is detected."""
    # L1 has 0 hits out of 1 (rate 0.0), L2 has 1 hit out of 1 (rate 1.0) -> triggers anomaly
    atoms = [
        {"score_level": 1.0, "hit": False},
        {"score_level": 2.0, "hit": True},
    ]
    state = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        step_id="step_1",
        metadata=ExecutionMetadata(target_locale="fi"),
        inputs=ExecutionInputsDTO(raw_inputs={"matrix_results": atoms}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepository()),
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=cast(Any, MockRepository()),
        prompt_block_repo=cast(Any, MockRepository()),
        output_profile_repo=cast(Any, MockRepository()),
        identity_repo=cast(Any, MockRepository()),
        audit_repo=cast(Any, MockRepository()),
        system_repo=cast(Any, MockRepository()),
    )
    result = verify_anomaly(state, deps)
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta is not None
    assert delta.get("llm_anomaly_retry_requested") is True
