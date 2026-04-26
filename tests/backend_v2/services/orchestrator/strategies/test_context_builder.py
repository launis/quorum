from unittest.mock import MagicMock

import pytest

from backend_v2.exceptions import TokenLimitExceededError
from backend_v2.services.orchestrator.strategies.llm_execution.context_builder import ContextBuilder


def test_context_builder_build_success(monkeypatch):
    """Test successful building of context data."""
    # Mock litellm.token_counter to always return a small number
    monkeypatch.setattr("litellm.token_counter", lambda model, text: 10)

    # Mock ContextRouter
    mock_context_router = MagicMock()
    mock_pruned = MagicMock()
    mock_pruned.model_dump_json.return_value = '{"pruned": True}'
    mock_context_router.route_and_prune.return_value = mock_pruned
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.strategies.llm_execution.context_builder.ContextRouter",
        mock_context_router,
    )

    input_mappings = {
        "text_field": "$.document_text",
        "nested_field": "$.nested.value",
        "trace_field": "$.steps.step1",
        "text_trace_field": "$.steps.step2",
    }

    state_data = {
        "document_text": "Sample text",
        "nested": {"value": 123},
        "steps": {
            "step1": {"normalized_score": 0.8, "raw": "data"},
            "step2": "This is a simple text trace that should bypass pruning."
        },
    }
    
    schema_map = {
        "step1": "MATRIX",
        "step2": "TEXT",
    }

    llm_context_data, new_input_mappings = ContextBuilder.build(
        input_mappings=input_mappings,
        state_data=state_data,
        output_profile=None,
        schema_map=schema_map,
    )

    assert "document_text" in llm_context_data
    assert llm_context_data["document_text"] == "Sample text"

    assert "nested" in llm_context_data
    assert llm_context_data["nested"]["value"] == 123

    assert "step1" in llm_context_data
    assert "<matrix_data>" in llm_context_data["step1"]
    assert '{"pruned": True}' in llm_context_data["step1"]
    
    assert "step2" in llm_context_data
    assert llm_context_data["step2"] == "This is a simple text trace that should bypass pruning."

    assert new_input_mappings["text_field"] == "$document_text"


def test_context_builder_build_token_limit_exceeded(monkeypatch):
    """Test that TokenLimitExceededError is raised when mapping exceeds limit."""
    # Mock litellm.token_counter to return a number larger than MAX_SAFE_TOKENS
    monkeypatch.setattr("litellm.token_counter", lambda model, text: ContextBuilder.MAX_SAFE_TOKENS + 1)

    input_mappings = {
        "large_text": "$.document_text",
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
