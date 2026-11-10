"""Unit tests for structural, output language, and Guttman anomaly validation hooks."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookState,
)
from backend_v2.exceptions import AppException
from backend_v2.hooks.validation import verify_anomaly, verify_output_language, verify_structure
from backend_v2.models.domain.validation import GuttmanAtomItemDTO, ValidationResultDTO
from backend_v2.models.dtos.hook_delta import AnomalyRetryResultDTO
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


def _create_hook_deps(repo: InMemoryUnifiedWorkflowRepository | None = None) -> HookDependencies:
    """Create hermetic HookDependencies bound to InMemoryUnifiedWorkflowRepository."""
    r = repo or InMemoryUnifiedWorkflowRepository()
    return HookDependencies(
        exec_repo=r,
        workflow_repo=r,
        comp_repo=r,
        prompt_block_repo=r,
        output_profile_repo=r,
        identity_repo=r,
        audit_repo=r,
        system_repo=r,
    )


def test_verify_output_language_detects_english_leakage() -> None:
    """Verify English stop-word leakage detection when target locale is Finnish."""
    inputs = ExecutionInputsDTO(
        raw_inputs={"evaluation_notes": "The user was very good and the system is fine.", "language": "fi"},
        dynamic_inputs={},
    )

    deps = _create_hook_deps()
    state = HookState(
        execution_id="exec-123",
        workflow_id="wf-123",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
    )

    result = verify_output_language(state, deps)

    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, ValidationResultDTO)
    assert len(result.state_delta.delta.errors) == 1
    assert result.state_delta.delta.errors[0].error_code == "VALIDATION_FAILED"
    assert "leaked English" in result.state_delta.delta.errors[0].detail


def test_verify_output_language_appends_to_existing_system_warnings() -> None:
    """Verify language leakage warning appends cleanly when _system_warnings is present."""
    inputs = ExecutionInputsDTO(
        raw_inputs={
            "evaluation_notes": "The user was very good and the system is fine.",
            "target_locale": "fi",
            "_system_warnings": [],
        },
        dynamic_inputs={},
    )
    state = HookState(
        execution_id="exec-123",
        workflow_id="wf-123",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
    )
    deps = _create_hook_deps()

    result = verify_output_language(state, deps)

    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, ValidationResultDTO)
    assert len(result.state_delta.delta.errors) == 1


def test_verify_output_language_resolves_global_context_vars_locales() -> None:
    """Verify target locale resolution from global_context_vars target_locale and language."""
    inputs = ExecutionInputsDTO(
        raw_inputs={"custom_justification": "Käyttäjä onnistui tehtävässä erinomaisesti."},
        dynamic_inputs={},
    )
    deps = _create_hook_deps()

    state_target = HookState(
        execution_id="exec-123",
        workflow_id="wf-123",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(target_locale="fi"),
        inputs=inputs,
    )
    assert verify_output_language(state_target, deps).success is True

    state_lang = HookState(
        execution_id="exec-123",
        workflow_id="wf-123",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(language="fi"),
        inputs=inputs,
    )
    assert verify_output_language(state_lang, deps).success is True


def test_verify_output_language_ignores_finnish_text() -> None:
    """Verify Finnish text without English stop words produces no warnings."""
    inputs = ExecutionInputsDTO(
        raw_inputs={
            "evaluation_notes": "Käyttäjä vaikutti erittäin fiksulta ja ymmärsi asian täydellisesti.",
            "language": "fi",
        },
        dynamic_inputs={},
    )

    deps = _create_hook_deps()
    state = HookState(
        execution_id="exec-123",
        workflow_id="wf-123",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
    )

    result = verify_output_language(state, deps)

    assert result.state_delta is not None
    assert result.state_delta.delta is None


def test_verify_output_language_allows_english_when_target_en() -> None:
    """Verify English text passes without warnings when target locale is en."""
    inputs = ExecutionInputsDTO(
        raw_inputs={"evaluation_notes": "The user was very good and the system is fine.", "language": "en"},
        dynamic_inputs={},
    )

    deps = _create_hook_deps()
    state = HookState(
        execution_id="exec-123",
        workflow_id="wf-123",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
    )

    result = verify_output_language(state, deps)

    assert result.state_delta is not None
    assert result.state_delta.delta is None


def test_verify_structure_fails_fast_on_empty_raw_inputs() -> None:
    """Verify empty raw_inputs raises AppException with EMPTY_INPUT in warnings."""
    inputs = ExecutionInputsDTO(raw_inputs={}, dynamic_inputs={})
    state = HookState(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
    )
    deps = _create_hook_deps()

    with pytest.raises(AppException) as exc:
        verify_structure(state, deps)

    assert "EMPTY_INPUT" in str(exc.value)


def test_verify_structure_success_with_valid_content() -> None:
    """Verify valid content length passes verify_structure."""
    inputs = ExecutionInputsDTO(
        raw_inputs={"raw_inputs": {"document_text": "This is a valid long enough document text for testing purpose."}},
        dynamic_inputs={},
    )
    state = HookState(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
    )
    deps = _create_hook_deps()

    result = verify_structure(state, deps)
    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, ValidationResultDTO)
    assert result.state_delta.delta.is_valid is True


def test_verify_structure_fails_on_short_or_empty_field() -> None:
    """Verify short or empty field content triggers VALIDATION_FAILED AppException."""
    inputs = ExecutionInputsDTO(raw_inputs={"inputs": {"doc_a": "short", "doc_b": ""}}, dynamic_inputs={})
    state = HookState(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
    )
    deps = _create_hook_deps()

    with pytest.raises(AppException) as exc:
        verify_structure(state, deps)

    assert "VALIDATION_FAILED" in str(exc.value)


def test_verify_structure_ignored_keys_and_no_content() -> None:
    """Verify payload containing only ignored metadata keys fails with no-content warning."""
    inputs = ExecutionInputsDTO(
        raw_inputs={"language": "fi", "test_id": "12345", "exec_mode": "full", "_internal": "xyz"},
        dynamic_inputs={},
    )
    state = HookState(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
    )
    deps = _create_hook_deps()

    with pytest.raises(AppException) as exc:
        verify_structure(state, deps)
    assert exc.value.details["error_code"] == "VALIDATION_FAILED"
    assert "No valid analysis content was provided" in str(exc.value)


def test_verify_structure_nested_inputs_unpacked() -> None:
    """Verify nested raw_inputs and inputs dictionaries are unpacked and validated."""
    inputs = ExecutionInputsDTO(
        raw_inputs={
            "raw_inputs": {"nested_raw": "Valid text of good length for processing."},
            "inputs": {"nested_inputs": "Another valid string with sufficient length."},
        },
        dynamic_inputs={},
    )
    state = HookState(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
    )
    deps = _create_hook_deps()
    result = verify_structure(state, deps)
    assert result.success is True


def test_verify_output_language_invalid_inputs_raises() -> None:
    """Verify non-string field values are skipped safely during output language check."""
    state = HookState(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(raw_inputs={"evaluation_notes": 12345}, target_locale="fi", dynamic_inputs={}),
    )
    deps = _create_hook_deps()
    result = verify_output_language(state, deps)
    assert result.success is True


def test_verify_output_language_non_dict_payload_source_raises() -> None:
    """Verify non-dict inputs source in verify_output_language raises VALIDATION_FAILED."""
    mock_inputs = MagicMock()
    mock_inputs.raw_inputs = 12345
    state = HookState.model_construct(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=mock_inputs,
    )
    deps = _create_hook_deps()
    with pytest.raises(AppException) as exc:
        verify_output_language(state, deps)
    assert exc.value.details["error_code"] == "VALIDATION_FAILED"


def test_verify_anomaly_empty_inputs_returns_success() -> None:
    """Verify empty raw_inputs in verify_anomaly returns an empty state delta."""
    state = HookState(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(raw_inputs={}, dynamic_inputs={}),
    )
    deps = _create_hook_deps()
    result = verify_anomaly(state, deps)
    assert result.success is True


def test_verify_structure_invalid_payload_source_raises() -> None:
    """Verify non-mapping raw_inputs in verify_structure raises INVALID_OUTPUT_SCHEMA."""
    mock_inputs = MagicMock()
    mock_inputs.raw_inputs = 12345
    state = HookState.model_construct(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=mock_inputs,
    )
    deps = _create_hook_deps()
    with pytest.raises(AppException) as exc:
        verify_structure(state, deps)
    assert exc.value.details["error_code"] == "INVALID_OUTPUT_SCHEMA"


def test_verify_output_language_invalid_system_warnings_raises() -> None:
    """Verify malformed _system_warnings in verify_output_language raises INVALID_OUTPUT_SCHEMA."""
    inputs = ExecutionInputsDTO(
        raw_inputs={
            "evaluation_notes": "The user was very good and the system is fine.",
            "_system_warnings": "not_a_list",
        },
        target_locale="fi",
        dynamic_inputs={},
    )
    state = HookState(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
    )
    deps = _create_hook_deps()
    with pytest.raises(AppException) as exc:
        verify_output_language(state, deps)
    assert exc.value.details["error_code"] == "INVALID_OUTPUT_SCHEMA"


def test_verify_anomaly_invalid_atom_type() -> None:
    """Verify non-object atom item in verify_anomaly raises VALIDATION_FAILED."""
    mock_inputs = MagicMock()
    mock_inputs.raw_inputs = {
        "block_1": [
            "not_a_valid_dict_or_atom",
            {"score_level": 1.0, "hit": True},
        ]
    }
    state = HookState.model_construct(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=mock_inputs,
    )
    deps = _create_hook_deps()
    with pytest.raises(AppException) as exc_info:
        verify_anomaly(state, deps)
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"


def test_validation_hook_rejects_malformed_dto() -> None:
    """Verify atom item missing mandatory score_level attribute raises AppException."""
    mock_inputs = MagicMock()
    mock_inputs.raw_inputs = {
        "block_1": [
            {"hit": True},
        ]
    }
    state = HookState.model_construct(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=mock_inputs,
    )
    deps = _create_hook_deps()
    with pytest.raises(AppException) as exc_info:
        verify_anomaly(state, deps)
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"


def test_verify_structure_none_state_raises_empty_input() -> None:
    """Verify None state in verify_structure raises EMPTY_INPUT."""
    deps = _create_hook_deps()
    with pytest.raises(AppException) as exc:
        verify_structure(None, deps)
    assert exc.value.details["error_code"] == "EMPTY_INPUT"


def test_verify_output_language_none_state_returns_success() -> None:
    """Verify None state in verify_output_language returns empty delta."""
    deps = _create_hook_deps()
    result = verify_output_language(None, deps)
    assert result.success is True
    assert result.state_delta is None or not result.state_delta.delta


def test_verify_output_language_missing_target_locale_raises() -> None:
    """Verify missing target_locale in verify_output_language raises VALIDATION_FAILED."""
    inputs = ExecutionInputsDTO(raw_inputs={"evaluation_notes": "Test"}, dynamic_inputs={})
    state = HookState(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
    )
    deps = _create_hook_deps()
    with pytest.raises(AppException) as exc:
        verify_output_language(state, deps)
    assert exc.value.details["error_code"] == "VALIDATION_FAILED"


def test_verify_anomaly_detects_guttman_inversion() -> None:
    """Verify Guttman inversion across levels triggers llm_anomaly_retry_requested."""
    inputs = ExecutionInputsDTO(
        raw_inputs={
            "block_1": [
                GuttmanAtomItemDTO(score_level=1.0, hit=False),
                GuttmanAtomItemDTO(score_level=1.0, hit=False),
                GuttmanAtomItemDTO(score_level=2.0, hit=True),
                GuttmanAtomItemDTO(score_level=2.0, hit=True),
            ]
        },
        dynamic_inputs={},
    )
    state = HookState(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
    )
    deps = _create_hook_deps()

    result = verify_anomaly(state, deps)
    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, AnomalyRetryResultDTO)
    assert result.state_delta.delta.llm_anomaly_retry_requested is True


def test_verify_anomaly_passes_when_no_inversion() -> None:
    """Verify monotonic Guttman hit rates pass without requesting retry."""
    inputs = ExecutionInputsDTO(
        raw_inputs={
            "block_1": [
                GuttmanAtomItemDTO(score_level=1.0, hit=True),
                GuttmanAtomItemDTO(score_level=1.0, hit=True),
                GuttmanAtomItemDTO(score_level=2.0, hit=False),
                GuttmanAtomItemDTO(score_level=2.0, hit=False),
            ],
            "block_single_level": [
                GuttmanAtomItemDTO(score_level=1.0, hit=True),
            ],
        },
        dynamic_inputs={},
    )
    state = HookState(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=inputs,
    )
    deps = _create_hook_deps()

    result = verify_anomaly(state, deps)
    assert result.success is True
    assert result.state_delta is None or result.state_delta.delta is None


def test_verify_anomaly_none_state() -> None:
    """Verify None state in verify_anomaly returns success."""
    deps = _create_hook_deps()
    result = verify_anomaly(None, deps)
    assert result.success is True
