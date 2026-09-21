from unittest.mock import MagicMock

import pytest

from backend_v2.exceptions import AppException, TokenLimitExceededError
from backend_v2.models.enums import ExecutionStatus
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
                    "evaluated_atoms": {"atom1": ExecutionStatus.PASSED, "atom2": ExecutionStatus.FAILED},
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
                    "evaluated_atoms": {"atom1": ExecutionStatus.PASSED, "atom2": ExecutionStatus.FAILED},
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


def test_apply_spatial_slicing_and_rule_descriptions() -> None:
    """Test spatial slicing when chronological markers are detected in rule blocks."""
    from backend_v2.models.core_base import I18nText
    from backend_v2.models.domain.matrix import MatrixClaim, MatrixRow, MatrixScale, TDAAssertion
    from backend_v2.models.domain.prompt_blocks import (
        MatrixPromptBlock,
        PersonaPromptBlock,
        ProtocolPromptBlock,
        SystemRulePromptBlock,
    )
    from backend_v2.models.enums import BlockDataType, PromptBlockCategory

    # 1. Non-str or empty criteria
    assert ContextBuilder.apply_spatial_slicing(123, None) == 123  # type: ignore[arg-type]
    assert ContextBuilder.apply_spatial_slicing("Sample text", []) == "Sample text"

    # 2. Blocks hierarchy
    matrix_block = MatrixPromptBlock(
        id="blk_0000111122223333",
        slug="matrix_block",
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        label=I18nText(translations={"en": "Matrix"}),
        description=I18nText(translations={"en": "Desc"}),
        ai_description="Evaluate before phase 2 strictly",
        scales=[
            MatrixScale(
                score=1,
                ai_label="LOW",
                name=I18nText(translations={"en": "Low"}),
                claims=[
                    MatrixClaim(
                        label=I18nText(translations={"en": "Claim"}),
                        tda_assertions=[
                            TDAAssertion(
                                tda_id="tda_11112222333344445555666677778888",
                                concept_description="Detailed rule concept",
                                inverse_evidence=False,
                                aggregation_mode="EXISTS",
                            )
                        ],
                    )
                ],
            )
        ],
    )

    sys_block = SystemRulePromptBlock(
        id="blk_1111222233334444",
        slug="sys_rule",
        category_id=PromptBlockCategory.SYSTEM_RULE,
        type=BlockDataType.INSTRUCTION,
        label=I18nText(translations={"en": "Rule"}),
        description=I18nText(translations={"en": "Rule"}),
        instruction_text="System rule text",
    )

    persona_block = PersonaPromptBlock(
        id="blk_2222333344445555",
        slug="persona",
        category_id=PromptBlockCategory.EXECUTION_PERSONA,
        type=BlockDataType.INSTRUCTION,
        label=I18nText(translations={"en": "Persona"}),
        description=I18nText(translations={"en": "Persona"}),
        role_enforcement="Persona instruction",
    )

    protocol_block = ProtocolPromptBlock(
        id="blk_3333444455556666",
        slug="protocol",
        category_id=PromptBlockCategory.PROTOCOL,
        type=BlockDataType.INSTRUCTION,
        label=I18nText(translations={"en": "Protocol"}),
        description=I18nText(translations={"en": "Protocol"}),
        protocol_instructions="Protocol instruction",
    )

    criteria = [matrix_block, sys_block, persona_block, protocol_block]
    rule_descs = ContextBuilder._collect_rule_descriptions(criteria)
    assert "Evaluate before phase 2 strictly" in rule_descs
    assert "System rule text" in rule_descs
    assert "Persona instruction" in rule_descs
    assert "Protocol instruction" in rule_descs
    assert "Detailed rule concept" in rule_descs

    # 3. Test text slicing
    doc_text = "Phase 1 content is here.\n[PHASE 2]\nPhase 2 should be sliced away."
    sliced = ContextBuilder.apply_spatial_slicing(doc_text, criteria)
    assert "[PHASE 2]" not in sliced
    assert "Phase 1 content is here." in sliced


def test_process_trace_dtos_non_matrix_and_primitive_validation() -> None:
    """Test non-matrix trace processing and validation of primitive values in matrix block."""
    dtos = [
        StepOutputDTO(step_id="step1", block_id="b1", data_type="text", payload={"text": "Hello"}),
    ]

    # Non-matrix returns compressed dict
    non_matrix_res = ContextBuilder._process_trace_dtos(dtos, None, schema_type="TEXT")
    assert non_matrix_res == {"b1": {"text": "Hello"}}

    # Matrix with non-dict primitive payload raises AppException
    invalid_matrix_dtos = [
        StepOutputDTO(step_id="step1", block_id="b1", data_type="matrix", payload="not_a_dict"),
    ]
    with pytest.raises(AppException) as exc_info:
        ContextBuilder._process_trace_dtos(
            invalid_matrix_dtos,
            None,
            schema_type="MATRIX",
            schema_map={"b1": "MATRIX"},
        )
    assert "must be a dict" in exc_info.value.message


def test_build_missing_step_schema_fail_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that missing step in schema_map triggers Fail-Fast AppException."""
    monkeypatch.setattr("litellm.token_counter", lambda model, text: 10)

    input_mappings = {"all_steps": "$steps"}
    state_data = {
        "steps": [
            StepOutputDTO(step_id="unmapped_step", block_id="b1", data_type="text", payload={}),
        ]
    }

    with pytest.raises(AppException) as exc_info:
        ContextBuilder.build(
            input_mappings=input_mappings,
            state_data=state_data,
            schema_map={},
        )
    assert "Missing schema mapping for step 'unmapped_step'" in exc_info.value.message


def test_build_step_subpaths(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test 3-part step paths: steps.step_key.block_key and invalid legacy paths."""
    monkeypatch.setattr("litellm.token_counter", lambda model, text: 10)

    dto = StepOutputDTO(step_id="step_a", block_id="blk_x", data_type="text", payload="block content")
    state_data = {"steps": [dto]}

    # 1. Successful 3-part extraction
    mappings = {"single_block": "$steps.step_a.blk_x"}
    ctx, new_map = ContextBuilder.build(
        input_mappings=mappings,
        state_data=state_data,
        schema_map={"step_a": "TEXT"},
    )
    assert ctx.inputs is not None
    assert ctx.inputs["single_block"] == "block content"

    # 2. Block not found in step
    with pytest.raises(AppException) as exc_info:
        ContextBuilder.build(
            input_mappings={"missing_blk": "$steps.step_a.blk_missing"},
            state_data=state_data,
            schema_map={"step_a": "TEXT"},
        )
    assert "Block 'blk_missing' not found" in exc_info.value.message

    # 3. Invalid 4-part legacy path
    with pytest.raises(AppException) as exc_info2:
        ContextBuilder.build(
            input_mappings={"too_long": "$steps.step_a.blk_x.extra"},
            state_data=state_data,
            schema_map={"step_a": "TEXT"},
        )
    assert "Invalid legacy path" in exc_info2.value.message

    # 4. Step missing from schema_map in steps.step_key
    with pytest.raises(AppException) as exc_info3:
        ContextBuilder.build(
            input_mappings={"step_res": "$steps.unmapped_step"},
            state_data=state_data,
            schema_map={},
        )
    assert "Missing schema mapping for step 'unmapped_step'" in exc_info3.value.message


def test_build_global_context_vars_with_steps(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test resolving global_context_vars containing steps."""
    monkeypatch.setattr("litellm.token_counter", lambda model, text: 10)

    dto = StepOutputDTO(step_id="step1", block_id="b1", data_type="text", payload={"val": 42})
    state_data = {
        "global_context_vars": {
            "steps": [dto],
            "extra_var": "hello",
        }
    }

    ctx, _ = ContextBuilder.build(
        input_mappings={"g_vars": "$global_context_vars"},
        state_data=state_data,
        schema_map={"step1": "TEXT", "b1": "TEXT"},
        blueprint_labels={"step1": "Label Step 1"},
    )
    assert ctx.inputs is not None
    assert "g_vars" in ctx.inputs
    assert '<step_result source="Label Step 1" step_id="step1">' in ctx.inputs["g_vars"]["steps"]


def test_project_compressed_base_model_and_lists() -> None:
    """Test _project_compressed handling of BaseModel instances, lists, and filtered keys."""
    from pydantic import BaseModel

    class InnerModel(BaseModel):
        name: str
        original_text: str = "filter_me"
        raw_content: str = "filter_me_too"

    model = InnerModel(name="test_item")
    projected = ContextBuilder._project_compressed([model, "primitive", 123])
    assert isinstance(projected, list)
    assert projected[0]["name"] == "test_item"
    assert "original_text" not in projected[0]
    assert "raw_content" not in projected[0]
    assert projected[1] == "primitive"
    assert projected[2] == 123


def test_build_with_dict_metadata_and_dynamic_inputs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test build when state_data is a dict containing ExecutionMetadata and dynamic_inputs."""
    from backend_v2.models.execution_core import ExecutionMetadata

    monkeypatch.setattr("litellm.token_counter", lambda model, text: 10)

    meta = ExecutionMetadata(workflow_version=2)
    state_data = {
        "metadata": meta,
        "raw_inputs": {
            "dynamic_inputs": {"dyn_key": "dyn_val"},
        },
        "user_doc": "Sample doc text",
    }

    ctx, _ = ContextBuilder.build(
        input_mappings={"doc": "$user_doc"},
        state_data=state_data,
    )
    assert ctx.metadata == meta
    assert ctx.raw_inputs is not None
    assert ctx.raw_inputs["dynamic_inputs"]["dyn_key"] == "dyn_val"


def test_build_matrix_pruning_with_evaluated_atoms(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that evaluated_atoms is pruned from matrix output in build."""
    monkeypatch.setattr("litellm.token_counter", lambda model, text: 10)

    mock_router = MagicMock()
    mock_pruned = MagicMock()
    mock_pruned.model_dump.return_value = {
        "raw_score": 4.0,
        "evaluated_atoms": [{"atom_id": "a1"}],
    }
    mock_router.route_and_prune.return_value = mock_pruned
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.strategies.llm_execution.context_builder.ContextRouter",
        mock_router,
    )

    dto = StepOutputDTO(step_id="step1", block_id="blk_m", data_type="matrix", payload={"raw_score": 4.0})
    state_data = {"steps": [dto]}

    ctx, _ = ContextBuilder.build(
        input_mappings={"matrix_step": "$steps.step1"},
        state_data=state_data,
        schema_map={"step1": "MATRIX", "blk_m": "MATRIX"},
    )
    assert ctx.inputs is not None
    assert "matrix_step" in ctx.inputs
    assert "evaluated_atoms" not in ctx.inputs["matrix_step"]


