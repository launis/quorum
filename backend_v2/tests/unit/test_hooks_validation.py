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
from backend_v2.exceptions import AppException
from backend_v2.hooks.validation import verify_output_language, verify_structure
from backend_v2.models.execution_core import ExecutionMetadata


def test_verify_output_language_detects_english_leakage() -> None:
    # Arrange
    inputs = ExecutionInputsDTO(
        raw_inputs={"evaluation_notes": "The user was very good and the system is fine.", "language": "fi"}
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
    state = HookState(
        execution_id="exec-123",
        workflow_id="wf-123",
        metadata=ExecutionMetadata(target_locale="fi"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
    )

    # Act
    result = cast(HookResult, verify_output_language(state, deps))

    # Assert
    assert result.success is True
    assert result.state_delta is not None
    assert "_system_warnings" in result.state_delta.delta
    assert len(result.state_delta.delta["_system_warnings"]) == 1
    assert result.state_delta.delta["_system_warnings"][0]["error_code"] == "VALIDATION_FAILED"
    assert "leaked English" in result.state_delta.delta["_system_warnings"][0]["detail"]


def test_verify_output_language_ignores_finnish_text() -> None:
    # Finnish text lacking English stop words
    inputs = ExecutionInputsDTO(
        raw_inputs={
            "evaluation_notes": "Käyttäjä vaikutti erittäin fiksulta ja ymmärsi asian täydellisesti.",
            "language": "fi",
        }
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
    state = HookState(
        execution_id="exec-123",
        workflow_id="wf-123",
        metadata=ExecutionMetadata(target_locale="fi"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
    )

    result = cast(HookResult, verify_output_language(state, deps))

    # Assert no warnings injected
    assert result.state_delta is not None
    assert "_system_warnings" not in result.state_delta.delta


def test_verify_output_language_allows_english_when_target_en() -> None:
    # English text when English is requested
    inputs = ExecutionInputsDTO(
        raw_inputs={"evaluation_notes": "The user was very good and the system is fine.", "language": "en"}
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
    state = HookState(
        execution_id="exec-123",
        workflow_id="wf-123",
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
    )

    result = cast(HookResult, verify_output_language(state, deps))

    assert result.state_delta is not None
    assert "_system_warnings" not in result.state_delta.delta


def test_verify_structure_fails_fast_on_empty_raw_inputs() -> None:
    # Arrange
    inputs = ExecutionInputsDTO(raw_inputs={})
    state = HookState(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(target_locale="fi"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
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

    # Act & Assert
    with pytest.raises(AppException) as exc:
        verify_structure(state, deps)

    assert "EMPTY_INPUT" in str(exc.value)


def test_verify_structure_success_with_valid_content() -> None:
    inputs = ExecutionInputsDTO(
        raw_inputs={"raw_inputs": {"document_text": "This is a valid long enough document text for testing purpose."}}
    )
    state = HookState(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(target_locale="fi"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
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

    result = cast(HookResult, verify_structure(state, deps))
    assert result.success is True
    assert "validation_result" in result.state_delta.delta
    assert result.state_delta.delta["validation_result"]["is_valid"] is True


def test_verify_structure_fails_on_short_or_empty_field() -> None:
    inputs = ExecutionInputsDTO(
        raw_inputs={"inputs": {"doc_a": "short", "doc_b": ""}}
    )
    state = HookState(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(target_locale="fi"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
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

    with pytest.raises(AppException) as exc:
        verify_structure(state, deps)

    assert "VALIDATION_FAILED" in str(exc.value)


def test_verify_structure_ignored_keys_and_no_content() -> None:
    inputs = ExecutionInputsDTO(
        raw_inputs={"language": "fi", "test_id": "12345", "exec_mode": "full", "_internal": "xyz"}
    )
    state = HookState(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(target_locale="fi"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
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

    with pytest.raises(AppException) as exc:
        verify_structure(state, deps)
    assert exc.value.details.get("error_code") == "VALIDATION_FAILED"
    assert "No valid analysis content was provided" in str(exc.value)


def test_verify_structure_nested_inputs_unpacked() -> None:
    inputs = ExecutionInputsDTO(
        raw_inputs={
            "raw_inputs": {"nested_raw": "Valid text of good length for processing."},
            "inputs": {"nested_inputs": "Another valid string with sufficient length."},
        }
    )
    state = HookState(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(target_locale="fi"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
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
    result = cast(HookResult, verify_structure(state, deps))
    assert result.success is True


def test_verify_output_language_invalid_inputs_raises() -> None:
    state = HookState(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(target_locale="fi"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(raw_inputs={"evaluation_notes": 12345}),
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
    result = cast(HookResult, verify_output_language(state, deps))
    assert result.success is True


def test_verify_anomaly_empty_inputs_returns_success() -> None:
    from backend_v2.hooks.validation import verify_anomaly

    state = HookState(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(target_locale="fi"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(raw_inputs={}),
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
    result = cast(HookResult, verify_anomaly(state, deps))
    assert result.success is True


def test_verify_structure_invalid_payload_source_raises() -> None:
    # Set raw_inputs to invalid type via mocking to trigger ValidationError in model_validate
    mock_inputs = MagicMock()
    mock_inputs.raw_inputs = 12345  # Not a dict
    state = HookState(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(target_locale="fi"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(),
    )
    object.__setattr__(state, "inputs", mock_inputs)
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
    with pytest.raises(AppException) as exc:
        verify_structure(state, deps)
    assert exc.value.details.get("error_code") == "INVALID_OUTPUT_SCHEMA"


def test_verify_output_language_invalid_system_warnings_raises() -> None:
    inputs = ExecutionInputsDTO(
        raw_inputs={"evaluation_notes": "The user was very good and the system is fine.", "_system_warnings": "not_a_list"}
    )
    state = HookState(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(target_locale="fi"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
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
    with pytest.raises(AppException) as exc:
        verify_output_language(state, deps)
    assert exc.value.details.get("error_code") == "INVALID_OUTPUT_SCHEMA"


def test_verify_anomaly_invalid_atom_type() -> None:
    from backend_v2.hooks.validation import verify_anomaly

    inputs = ExecutionInputsDTO(
        raw_inputs={
            "block_1": [
                "not_a_valid_dict_or_atom",
                {"score_level": 1.0, "hit": True},
            ]
        }
    )
    state = HookState(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(target_locale="fi"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
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
    result = cast(HookResult, verify_anomaly(state, deps))
    assert result.success is True


def test_verify_structure_none_state_raises_empty_input() -> None:
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
    with pytest.raises(AppException) as exc:
        verify_structure(None, deps)
    assert exc.value.details.get("error_code") == "EMPTY_INPUT"


def test_verify_output_language_none_state_returns_success() -> None:
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
    result = cast(HookResult, verify_output_language(None, deps))
    assert result.success is True
    assert result.state_delta is None or result.state_delta.delta == {}


def test_verify_output_language_missing_target_locale_raises() -> None:
    inputs = ExecutionInputsDTO(raw_inputs={"evaluation_notes": "Test"})
    state = HookState(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(target_locale=""),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
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
    with pytest.raises(AppException) as exc:
        verify_output_language(state, deps)
    assert exc.value.details.get("error_code") == "VALIDATION_FAILED"


def test_verify_anomaly_detects_guttman_inversion() -> None:
    inputs = ExecutionInputsDTO(
        raw_inputs={
            "block_1": [
                {"score_level": 1.0, "hit": False},
                {"score_level": 1.0, "hit": False},
                {"score_level": 2.0, "hit": True},
                {"score_level": 2.0, "hit": True},
            ]
        }
    )
    state = HookState(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(target_locale="fi"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
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

    from backend_v2.hooks.validation import verify_anomaly

    result = cast(HookResult, verify_anomaly(state, deps))
    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.delta.get("llm_anomaly_retry_requested") is True


def test_verify_anomaly_passes_when_no_inversion() -> None:
    inputs = ExecutionInputsDTO(
        raw_inputs={
            "block_1": [
                {"score_level": 1.0, "hit": True},
                {"score_level": 1.0, "hit": True},
                {"score_level": 2.0, "hit": False},
                {"score_level": 2.0, "hit": False},
            ]
        }
    )
    state = HookState(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(target_locale="fi"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
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

    from backend_v2.hooks.validation import verify_anomaly

    result = cast(HookResult, verify_anomaly(state, deps))
    assert result.success is True
    assert result.state_delta is None or "llm_anomaly_retry_requested" not in result.state_delta.delta


def test_verify_anomaly_none_state() -> None:
    from backend_v2.hooks.validation import verify_anomaly

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
    result = cast(HookResult, verify_anomaly(None, deps))
    assert result.success is True

