from unittest.mock import MagicMock

import pytest

from backend_v2.exceptions import AppException, TokenLimitExceededError
from backend_v2.services.orchestrator.strategies.llm_execution.context_builder import ContextBuilder


def test_context_builder_build_prune_raw_data(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that atoms, history_text, and extracted_text are pruned correctly."""
    monkeypatch.setattr("litellm.token_counter", lambda model, text: 10)

    input_mappings = {
        "all_steps": "$steps",
        "single_atom_step": "$steps.atom_step",
        "single_raw_step": "$steps.raw_step",
    }

    state_data = {
        "steps": {
            "eval_step": {
                "raw_score": 5.0,
                "normalized_score": 0.8,
                "level_breakdown": "3/5",
                "justification": "Good",
                "evaluated_atoms": {"atom1": True, "atom2": False},
                "extensions": {}
            },
            "atom_step": {"atoms": ["a", "b", "c"]},
            "raw_step": {"history_text": "huge string"},
            "other_step": {"custom": "data"},
        }
    }

    # Mock ContextRouter so eval_step pruning succeeds
    mock_context_router = MagicMock()
    mock_pruned = MagicMock()
    mock_pruned.model_dump.return_value = {"pruned": True}
    mock_pruned.model_dump_json.return_value = '{"pruned": True}'
    mock_context_router.route_and_prune.return_value = mock_pruned
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.strategies.llm_execution.context_builder.ContextRouter",
        mock_context_router,
    )

    with pytest.raises(AppException) as exc_info:
        ContextBuilder.build(
            input_mappings=input_mappings,
            state_data=state_data,
            output_profile=None,
        )

    assert "validation errors for LightweightMatrixOutput" in str(exc_info.value.message)
    assert exc_info.value.status_code == 400


def test_context_builder_build_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test successful building of context data."""
    # Mock litellm.token_counter to always return a small number
    monkeypatch.setattr("litellm.token_counter", lambda model, text: 10)

    # Mock ContextRouter
    mock_context_router = MagicMock()
    mock_pruned = MagicMock()
    mock_pruned.model_dump.return_value = {"pruned": True}
    mock_pruned.model_dump_json.return_value = '{"pruned": True}'
    mock_context_router.route_and_prune.return_value = mock_pruned
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.strategies.llm_execution.context_builder.ContextRouter",
        mock_context_router,
    )

    input_mappings = {
        "text_field": "$document_text",
        "nested_field": "$nested.value",
        "trace_field": "$steps.step1",
    }

    state_data = {
        "document_text": "Sample text",
        "nested": {"value": 123},
        "steps": {
            "step1": {
                "raw_score": 5.0,
                "normalized_score": 0.8,
                "level_breakdown": "3/5",
                "justification": "Good",
                "evaluated_atoms": {"atom1": True, "atom2": False},
                "extensions": {}
            }
        },
    }

    llm_context_data, new_input_mappings = ContextBuilder.build(
        input_mappings=input_mappings,
        state_data=state_data,
        output_profile=None,
    )

    assert "document_text" in llm_context_data
    assert llm_context_data["document_text"] == "Sample text"

    assert "nested" in llm_context_data
    assert llm_context_data["nested"]["value"] == 123

    assert "step1" in llm_context_data
    assert "<matrix_data>" in llm_context_data["step1"]
    assert '"pruned": true' in llm_context_data["step1"]

    assert new_input_mappings["text_field"] == "$document_text"


def test_context_builder_build_token_limit_exceeded(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that TokenLimitExceededError is raised when mapping exceeds limit."""
    from backend_v2.models.enums import SystemConcurrency
    # Mock litellm.token_counter to return a number larger than MAX_SAFE_TOKENS
    limit = SystemConcurrency.MAX_SAFE_TOKENS.value
    monkeypatch.setattr("litellm.token_counter", lambda model, text: limit + 1)

    input_mappings = {
        "large_text": "$document_text",
    }
    state_data = {
        "document_text": "This is a very large text that exceeds the limit.",
    }

    with pytest.raises(TokenLimitExceededError) as exc_info:
        ContextBuilder.build(
            input_mappings=input_mappings,
            state_data=state_data,
            output_profile=None,
        )

    assert "exceeded token limit" in str(exc_info.value)


def test_context_builder_build_trace_pruning_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that an exception during trace pruning raises AppException (Fail-Fast)."""
    monkeypatch.setattr("litellm.token_counter", lambda model, text: 10)

    mock_context_router = MagicMock()
    mock_context_router.route_and_prune.side_effect = Exception("Pruning crashed")
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.strategies.llm_execution.context_builder.ContextRouter",
        mock_context_router,
    )

    input_mappings = {"trace_field": "$steps.step1"}
    state_data = {
        "steps": {
            "step1": {
                "raw_score": 5.0,
                "normalized_score": 0.8,
                "level_breakdown": "3/5",
                "justification": "Good",
                "evaluated_atoms": {"atom1": True, "atom2": False},
                "extensions": {}
            }
        }
    }

    with pytest.raises(AppException) as exc_info:
        ContextBuilder.build(input_mappings, state_data, None)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert "ContextRouter trace pruning failed" in str(exc_info.value.message)


def test_context_builder_build_token_counting_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that an exception during token counting raises AppException (Fail-Fast)."""

    def mock_counter(model: str, text: str) -> int:
        raise Exception("LiteLLM crashed")

    monkeypatch.setattr("litellm.token_counter", mock_counter)

    input_mappings = {"text_field": "$document_text"}
    state_data = {"document_text": "Sample text"}

    with pytest.raises(AppException) as exc_info:
        ContextBuilder.build(input_mappings, state_data, None)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert "Token counting failed" in str(exc_info.value.message)


def test_context_builder_build_resolution_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that an exception during dot notation resolution raises AppException (Fail-Fast)."""
    monkeypatch.setattr("litellm.token_counter", lambda model, text: 10)

    from typing import Any

    def mock_resolve(data: dict[str, Any], path: str) -> Any:
        raise ValueError("Invalid path syntax")

    monkeypatch.setattr(
        "backend_v2.services.orchestrator.strategies.llm_execution.context_builder.resolve_dot_notation",
        mock_resolve,
    )

    input_mappings = {"bad_field": "$bad_path"}
    state_data = {"some": "data"}

    with pytest.raises(AppException) as exc_info:
        ContextBuilder.build(input_mappings, state_data, None)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert "Failed to resolve input mapping" in str(exc_info.value.message)
