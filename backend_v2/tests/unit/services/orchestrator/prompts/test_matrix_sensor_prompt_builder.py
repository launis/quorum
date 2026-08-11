import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.dag_models import ExtractedAtom, LinkedAtomGraph
from backend_v2.models.dtos.engine import FlattenedAtom, MatrixEvaluationContext
from backend_v2.models.v2_core import TheoryGrounding
from backend_v2.services.orchestrator.prompts.matrix_sensor_prompt_builder import MatrixSensorPromptBuilder


def test_build_caching_prefix_with_context() -> None:
    """Test building a caching prefix when full matrix context is provided."""
    theory_grounding = TheoryGrounding(
        source_url="Test Framework",
        citation_reference="Test Citation",
    )
    matrix_context = MatrixEvaluationContext(
        theory_grounding=theory_grounding,
        matrix_objective="Evaluate matrix rules.",
        allow_contextual_override=True,
    )

    context_text = "Here is a massive document."
    prompt = MatrixSensorPromptBuilder.build_caching_prefix(context_text, matrix_context)

    # Validate the generated compiled prompt
    assert len(prompt.static_messages) == 2
    assert prompt.static_messages[0]["role"] == "system"
    assert "Evaluate matrix rules." in prompt.static_messages[0]["content"]
    assert "Test Framework" in prompt.static_messages[0]["content"]

    assert prompt.static_messages[1]["role"] == "user"
    assert "Here is a massive document." in prompt.static_messages[1]["content"]

    assert len(prompt.dynamic_messages) == 0


def test_build_caching_prefix_without_context() -> None:
    """Test building a caching prefix without an optional matrix context."""
    context_text = "Some small document."
    prompt = MatrixSensorPromptBuilder.build_caching_prefix(context_text, None)

    assert len(prompt.static_messages) == 2
    assert prompt.static_messages[0]["role"] == "system"
    assert "Evaluate" in prompt.static_messages[0]["content"]

    assert prompt.static_messages[1]["role"] == "user"
    assert "Some small document." in prompt.static_messages[1]["content"]


def test_build_compiled_prompt_with_assertions() -> None:
    """Test building a compiled prompt including matrix assertions."""
    matrix_assertions = [
        FlattenedAtom(
            atom_id="tda_11111111",
            question="Is it blue?",
            extraction_rule="Check for blue.",
            anchor_target="blue section",
            is_inverse=False,
        )
    ]
    matrix_context = MatrixEvaluationContext(matrix_assertions=matrix_assertions)

    node1 = LinkedAtomGraph(
        atom=ExtractedAtom(
            tda_id="tda_11111111",
            resolved_claim="This is not used because assertion exists.",
            reasoning="R",
            source_quote="Q",
            source_id="chk_1",
            source_sequence_index=1,
        ),
    )

    tda_id_to_alias = {"tda_11111111": "a0"}
    context_text = "Doc with blue text."

    prompt = MatrixSensorPromptBuilder.build_compiled_prompt(context_text, [node1], tda_id_to_alias, matrix_context)

    # Static prefix validation
    assert len(prompt.static_messages) == 2
    assert prompt.static_messages[1]["role"] == "user"

    # Dynamic message validation
    assert len(prompt.dynamic_messages) == 1
    assert prompt.dynamic_messages[0]["role"] == "user"
    content = prompt.dynamic_messages[0]["content"]

    # Should contain XML formatted elements mapped to alias a0
    assert "a0" in content
    assert "<question>" in content
    assert "Is it blue?" in content
    assert "<extraction_rule>" in content
    assert "Check for blue." in content
    assert "<anchor_target>" in content
    assert "blue section" in content


def test_build_compiled_prompt_fallback_claim() -> None:
    """Test fallback when no assertions are in the matrix context (happy path)."""
    node = LinkedAtomGraph(
        atom=ExtractedAtom(
            tda_id="tda_22222222",
            resolved_claim="Fallback claim text.",
            reasoning="R",
            source_quote="Q",
            source_id="chk_1",
            source_sequence_index=1,
        ),
    )

    prompt = MatrixSensorPromptBuilder.build_compiled_prompt("Context", [node], {"tda_22222222": "a1"}, None)

    assert len(prompt.dynamic_messages) == 1
    content = prompt.dynamic_messages[0]["content"]
    assert "a1" in content
    assert "Fallback claim text." in content
    assert "<question>" not in content


def test_ephemeral_block_creation_strictness() -> None:
    """Anti-happy path: Ensure creating an ephemeral block throws error on invalid parameters."""
    with pytest.raises(ValidationError):
        # Invalid block ID should trigger regex validation error
        MatrixSensorPromptBuilder._create_ephemeral_block(
            block_id="invalid_id",  # Needs to match ^[a-z]{2,5}_[a-fA-F0-9]{16,32}$
            category_id="NOT_AN_ENUM",  # type: ignore
            ai_desc="Something",
        )
