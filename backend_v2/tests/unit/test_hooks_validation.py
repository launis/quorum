from typing import cast
from unittest.mock import MagicMock

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
from backend_v2.hooks.validation import verify_output_language


def test_verify_output_language_detects_english_leakage() -> None:
    # Arrange
    # English text with heavy stop words
    inputs = {"evaluation_notes": "The user was very good and the system is fine.", "language": "fi"}

    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )
    # mock_repo)
    state = HookState(
        execution_id="exec-123",
        workflow_id="wf-123",
        metadata={"target_locale": "fi"},
        global_context_vars={},
        inputs=inputs,
    )

    # Act
    result = cast(HookResult, verify_output_language(state, deps))

    # Assert
    assert result.success is True
    assert result.state_delta is not None
    assert "_system_warnings" in result.state_delta
    assert len(result.state_delta["_system_warnings"]) == 1
    assert result.state_delta["_system_warnings"][0]["error_code"] == "VALIDATION_FAILED"
    assert "leaked English" in result.state_delta["_system_warnings"][0]["detail"]


def test_verify_output_language_ignores_finnish_text() -> None:
    # Finnish text lacking English stop words
    inputs = {
        "evaluation_notes": "Käyttäjä vaikutti erittäin fiksulta ja ymmärsi asian täydellisesti.",
        "language": "fi",
    }  # noqa: E501

    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )
    # mock_repo)
    state = HookState(
        execution_id="exec-123",
        workflow_id="wf-123",
        metadata={"target_locale": "fi"},
        global_context_vars={},
        inputs=inputs,
    )

    result = cast(HookResult, verify_output_language(state, deps))

    # Assert no warnings injected
    assert result.state_delta is not None
    assert "_system_warnings" not in result.state_delta


def test_verify_output_language_allows_english_when_target_en() -> None:
    # English text when English is requested
    inputs = {"evaluation_notes": "The user was very good and the system is fine.", "language": "en"}

    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )
    # mock_repo)
    state = HookState(
        execution_id="exec-123",
        workflow_id="wf-123",
        metadata={"target_locale": "en"},
        global_context_vars={},
        inputs=inputs,
    )

    result = cast(HookResult, verify_output_language(state, deps))

    assert "_system_warnings" not in result.state_delta


def test_verify_structure_fails_fast_on_empty_raw_inputs() -> None:
    import pytest

    from backend_v2.exceptions import AppException
    from backend_v2.hooks.validation import verify_structure

    # Arrange
    inputs = {"raw_inputs": {}, "steps": [], "metadata": {"target_locale": "fi"}}
    state = HookState(
        execution_id="exec-1",
        workflow_id="wf-1",
        metadata={},
        global_context_vars={},
        inputs=inputs,
    )
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )

    # Act & Assert
    with pytest.raises(AppException) as exc:
        verify_structure(state, deps)

    assert "Structural Validation Failed" in str(exc.value)
    assert "EMPTY_INPUT" in str(exc.value)
