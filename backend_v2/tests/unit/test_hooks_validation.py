from typing import cast
from unittest.mock import MagicMock

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
from backend_v2.hooks.validation import verify_output_language


def test_verify_output_language_detects_english_leakage() -> None:
    # Arrange
    mock_repo = MagicMock()
    # English text with heavy stop words
    inputs = {"evaluation_notes": "The user was very good and the system is fine."}

    deps = HookDependencies(repository=mock_repo)
    state = HookState(execution_id="exec-123", workflow_id="wf-123", metadata={"target_locale": "fi"}, inputs=inputs)

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
    mock_repo = MagicMock()
    # Finnish text lacking English stop words
    inputs = {"evaluation_notes": "Käyttäjä vaikutti erittäin fiksulta ja ymmärsi asian täydellisesti."}

    deps = HookDependencies(repository=mock_repo)
    state = HookState(execution_id="exec-123", workflow_id="wf-123", metadata={"target_locale": "fi"}, inputs=inputs)

    result = cast(HookResult, verify_output_language(state, deps))

    # Assert no warnings injected
    assert result.state_delta is not None
    assert "_system_warnings" not in result.state_delta


def test_verify_output_language_allows_english_when_target_en() -> None:
    mock_repo = MagicMock()
    # English text when English is requested
    inputs = {"evaluation_notes": "The user was very good and the system is fine."}

    deps = HookDependencies(repository=mock_repo)
    state = HookState(execution_id="exec-123", workflow_id="wf-123", metadata={"target_locale": "en"}, inputs=inputs)

    result = cast(HookResult, verify_output_language(state, deps))

    # Assert
    assert result.state_delta is not None
    assert "_system_warnings" not in result.state_delta
