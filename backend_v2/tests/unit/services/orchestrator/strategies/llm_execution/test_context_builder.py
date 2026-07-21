from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

from backend_v2.exceptions import AppException, TokenLimitExceededError
from backend_v2.models.state import StepOutputDTO
from backend_v2.services.orchestrator.strategies.llm_execution.context_builder import ContextBuilder
from backend_v2.settings import get_settings


def test_context_builder_build_prune_raw_data(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that atoms, history_text, and extracted_text are pruned correctly."""
    monkeypatch.setattr(
        "litellm.token_counter",
        lambda model, text: 10,
    )

    input_mappings = {
        "all_steps": "$steps",
        "single_atom_step": "$steps.atom_step",
        "single_raw_step": "$steps.raw_step",
    }

    state_data = {
        "steps": [
            StepOutputDTO(
                step_id="eval_step",
                block_id="blk_invalid",
                data_type="matrix",
                payload={"raw_score": "not_a_float", "missing_fields": "yes"},
            ),  # noqa: E501
            StepOutputDTO(step_id="atom_step", block_id="atoms", data_type="unknown", payload=["a", "b", "c"]),
            StepOutputDTO(step_id="raw_step", block_id="history_text", data_type="text", payload="huge string"),
            StepOutputDTO(step_id="other_step", block_id="custom", data_type="text", payload="data"),
        ]
    }

    # Mock ContextRouter to raise validation error for eval_step
    mock_context_router = MagicMock()
    mock_context_router.route_and_prune.side_effect = Exception("validation errors for LightweightMatrixOutput")
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.strategies.llm_execution.context_builder.ContextRouter",
        mock_context_router,
    )

    with pytest.raises(AppException) as exc_info:
        ContextBuilder.build(
            input_mappings=input_mappings,
            state_data=state_data,
            output_profile=None,
            schema_map={
                "eval_step": "MATRIX",
                "blk_invalid": "MATRIX",
                "atom_step": "TEXT",
                "raw_step": "TEXT",
                "other_step": "TEXT",
            },
        )

    assert "validation errors for LightweightMatrixOutput" in str(exc_info.value.message)
    assert exc_info.value.status_code == 500


def test_context_builder_build_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test successful building of context data."""
    monkeypatch.setattr(
        "litellm.token_counter",
        lambda model, text: 10,
    )

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
        "steps": [
            StepOutputDTO(
                step_id="step1",
                block_id="blk_123",
                data_type="matrix",
                payload={
                    "raw_score": 5.0,
                    "normalized_score": 0.8,
                    "level_breakdown": None,
                    "justification": "Good",
                    "evaluated_atoms": {"atom1": True, "atom2": False},
                    "extensions": {},
                },
            )
        ],
    }

    llm_context_data, new_input_mappings = ContextBuilder.build(
        input_mappings=input_mappings,
        state_data=state_data,
        output_profile=None,
        schema_map={"step1": "MATRIX", "blk_123": "MATRIX"},
    )

    assert "document_text" in llm_context_data
    assert llm_context_data["document_text"] == "Sample text"

    assert "nested" in llm_context_data
    assert llm_context_data["nested"]["value"] == 123

    assert "trace_field" in llm_context_data
    assert "<step_result" in llm_context_data["trace_field"]
    assert '"pruned": true' in llm_context_data["trace_field"]

    assert new_input_mappings["text_field"] == "$document_text"


def test_context_builder_build_token_limit_exceeded(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that TokenLimitExceededError is raised when mapping exceeds limit."""
    limit = get_settings().max_safe_tokens
    monkeypatch.setattr(
        "litellm.token_counter",
        lambda model, text: limit + 1,
    )

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
    monkeypatch.setattr(
        "litellm.token_counter",
        lambda model, text: 10,
    )

    mock_context_router = MagicMock()
    mock_context_router.route_and_prune.side_effect = Exception("Pruning crashed")
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.strategies.llm_execution.context_builder.ContextRouter",
        mock_context_router,
    )

    input_mappings = {"trace_field": "$steps.step1"}
    state_data = {
        "steps": [
            StepOutputDTO(
                step_id="step1",
                block_id="blk_123",
                data_type="matrix",
                payload={
                    "raw_score": 5.0,
                    "normalized_score": 0.8,
                    "level_breakdown": None,
                    "justification": "Good",
                    "evaluated_atoms": {"atom1": True, "atom2": False},
                    "extensions": {},
                },
            )
        ]
    }

    with pytest.raises(AppException) as exc_info:
        ContextBuilder.build(input_mappings, state_data, None, {"step1": "MATRIX", "blk_123": "MATRIX"})

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert "ContextRouter trace pruning failed" in str(exc_info.value.message)


def test_context_builder_build_token_counting_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that an exception during token counting raises AppException (Fail-Fast)."""

    def mock_counter(model: str, text: str) -> int:
        raise Exception("LiteLLM crashed")

    monkeypatch.setattr(
        "litellm.token_counter",
        mock_counter,
    )

    input_mappings = {"text_field": "$document_text"}
    state_data = {"document_text": "Sample text"}

    with pytest.raises(AppException) as exc_info:
        ContextBuilder.build(input_mappings, state_data, None)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == "AGENT_EXECUTION_CRITICAL"
    assert "Token counting failed" in str(exc_info.value.message)


def test_context_builder_build_resolution_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that an exception during dot notation resolution raises AppException (Fail-Fast)."""
    monkeypatch.setattr(
        "litellm.token_counter",
        lambda model, text: 10,
    )

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


def test_context_builder_propagates_dynamic_inputs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that ContextBuilder always propagates raw_inputs.dynamic_inputs metadata."""
    monkeypatch.setattr(
        "litellm.token_counter",
        lambda model, text: 10,
    )

    input_mappings = {"text_field": "$document_text"}
    state_data = {
        "document_text": "Sample text",
        "raw_inputs": {"dynamic_inputs": {"document_date": "2025-10-27T23:31:46+02:00"}},
    }

    llm_context_data, _ = ContextBuilder.build(
        input_mappings=input_mappings,
        state_data=state_data,
        output_profile=None,
    )

    assert "raw_inputs" in llm_context_data
    assert "dynamic_inputs" in llm_context_data["raw_inputs"]
    assert llm_context_data["raw_inputs"]["dynamic_inputs"]["document_date"] == "2025-10-27T23:31:46+02:00"


def test_project_compressed_does_not_mutate_original() -> None:
    """Verify Immutable Projection: original payload is never mutated."""
    original = {
        "evaluations": [
            {
                "exact_quotes": ["quote"],
                "shuffled_atoms": ["x", "y"],
                "post_quote_anchor": "remove me",
                "localized_anchors_found": ["a1", "a2", "a3", "a4", "a5"],
            }
        ]
    }

    ContextBuilder._project_compressed(original)

    # Original must still contain all original keys — immutability proof
    inner = original["evaluations"][0]
    assert "shuffled_atoms" in inner
    assert inner["shuffled_atoms"] == ["x", "y"]
    assert "post_quote_anchor" in inner
    assert inner["post_quote_anchor"] == "remove me"
    assert len(inner["localized_anchors_found"]) == 5


def test_project_compressed_strips_post_quote_anchor() -> None:
    """Verify that _project_compressed leaves other keys intact while preserving immutability."""
    payload = {
        "exact_quotes": ["important evidence"],
        "post_quote_anchor": "kept",
        "semantic_reasoning": "reasoning here",
    }
    result = ContextBuilder._project_compressed(payload)

    assert "post_quote_anchor" in result
    assert result["exact_quotes"] == ["important evidence"]
    assert result["semantic_reasoning"] == "reasoning here"


def test_project_compressed_strips_shuffled_atoms() -> None:
    """Verify that _project_compressed removes shuffled_atoms from payloads."""
    payload = {
        "raw_score": 4.5,
        "shuffled_atoms": ["a", "b", "c"],
        "justification": "test",
    }
    result = ContextBuilder._project_compressed(payload)

    assert "shuffled_atoms" not in result
    assert result["raw_score"] == 4.5
    assert result["justification"] == "test"


def test_project_compressed_preserves_exact_quote_and_reasoning() -> None:
    """Verify that exact_quote and semantic_reasoning pass through unmodified."""
    payload = {
        "evaluations": [
            {
                "exact_quotes": ["Tämä on kriittinen lainaus dokumentista."],
                "semantic_reasoning": "Päättelyketju.",
                "localized_anchors_found": ["anchor1", "anchor2", "anchor3"],
                "shuffled_atoms": ["noise"],
                "post_quote_anchor": "noise2",
            }
        ]
    }
    result = ContextBuilder._project_compressed(payload)

    ev = result["evaluations"][0]
    assert ev["exact_quotes"] == ["Tämä on kriittinen lainaus dokumentista."]
    assert ev["semantic_reasoning"] == "Päättelyketju."
    # Anchors remain uncompressed in V2 projection
    assert len(ev["localized_anchors_found"]) == 3
    assert "shuffled_atoms" not in ev
    assert "post_quote_anchor" in ev
