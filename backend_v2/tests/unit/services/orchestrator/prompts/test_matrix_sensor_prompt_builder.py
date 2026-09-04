import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.dtos.dag_models import CausalEdge, ExtractedAtom, LinkedAtomGraph
from backend_v2.models.dtos.engine import FlattenedAtom, MatrixEvaluationContext
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.v2_core import TheoryGrounding
from backend_v2.services.orchestrator.prompts.matrix_sensor_prompt_builder import MatrixSensorPromptBuilder


def test_build_caching_prefix_with_context() -> None:
    """Test building a caching prefix when full matrix context is provided."""
    theory_grounding = TheoryGrounding(
        source_url="https://arma.org/guidelines",
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
    assert prompt.static_messages[0].role == "system"
    assert "<global_system_mandates>" in prompt.static_messages[0].content
    assert "Evaluate matrix rules." in prompt.static_messages[0].content
    assert "<theory_context>" in prompt.static_messages[0].content
    assert "Test Citation" in prompt.static_messages[0].content
    assert "https://arma.org/guidelines" not in prompt.static_messages[0].content

    assert prompt.static_messages[1].role == "user"
    assert "Here is a massive document." in prompt.static_messages[1].content

    assert len(prompt.dynamic_messages) == 0


def test_build_caching_prefix_theory_grounding_none_citation() -> None:
    """Boundary test: theory_grounding with None citation_reference does not add ephemeral block."""
    theory_grounding = TheoryGrounding(
        source_url="https://arma.org/guidelines",
        citation_reference=None,
    )
    matrix_context = MatrixEvaluationContext(
        theory_grounding=theory_grounding,
        matrix_objective="Evaluate matrix rules.",
    )
    prompt = MatrixSensorPromptBuilder.build_caching_prefix("Doc text", matrix_context)
    assert "<theory_context>" not in prompt.static_messages[0].content


def test_build_caching_prefix_theory_grounding_empty_citation() -> None:
    """Boundary test: theory_grounding with empty string citation_reference does not add ephemeral block."""
    theory_grounding = TheoryGrounding(
        source_url="https://arma.org/guidelines",
        citation_reference="",
    )
    matrix_context = MatrixEvaluationContext(
        theory_grounding=theory_grounding,
        matrix_objective="Evaluate matrix rules.",
    )
    prompt = MatrixSensorPromptBuilder.build_caching_prefix("Doc text", matrix_context)
    assert "<theory_context>" not in prompt.static_messages[0].content


def test_build_caching_prefix_theory_grounding_whitespace_only() -> None:
    """Boundary test: theory_grounding with whitespace-only citation_reference does not add ephemeral block."""
    theory_grounding = TheoryGrounding(
        source_url="https://arma.org/guidelines",
        citation_reference="   \n\t  ",
    )
    matrix_context = MatrixEvaluationContext(
        theory_grounding=theory_grounding,
        matrix_objective="Evaluate matrix rules.",
    )
    prompt = MatrixSensorPromptBuilder.build_caching_prefix("Doc text", matrix_context)
    assert "<theory_context>" not in prompt.static_messages[0].content


def test_build_caching_prefix_theory_grounding_omits_raw_urls() -> None:
    """Security/Optimization test: raw source_url is never leaked or injected into system prompt."""
    theory_grounding = TheoryGrounding(
        source_url="https://secret-internal-domain.org/doc",
        citation_reference="Valid Scientific Citation",
    )
    matrix_context = MatrixEvaluationContext(
        theory_grounding=theory_grounding,
    )
    prompt = MatrixSensorPromptBuilder.build_caching_prefix("Doc text", matrix_context)
    assert "<theory_context>" in prompt.static_messages[0].content
    assert "Valid Scientific Citation" in prompt.static_messages[0].content
    assert "https://secret-internal-domain.org" not in prompt.static_messages[0].content


def test_build_caching_prefix_theory_grounding_xml_injection_shield() -> None:
    """Security/Error-path test: citation containing XML tags and CDATA breakout sequences is shielded."""
    theory_grounding = TheoryGrounding(
        source_url="https://secret-domain.org/doc",
        citation_reference="Author (2020) <tag> & ]]> </theory_context><injected>",
    )
    matrix_context = MatrixEvaluationContext(
        theory_grounding=theory_grounding,
    )
    prompt = MatrixSensorPromptBuilder.build_caching_prefix("Doc text", matrix_context)
    system_content = prompt.static_messages[0].content

    assert "<theory_context>" in system_content
    assert "<![CDATA[Author (2020) <tag> & ]]]]><![CDATA[> </theory_context><injected>]]>" in system_content
    assert "https://secret-domain.org" not in system_content


def test_build_caching_prefix_without_context() -> None:
    """Test building a caching prefix without an optional matrix context."""
    context_text = "Some small document."
    prompt = MatrixSensorPromptBuilder.build_caching_prefix(context_text, None)

    assert len(prompt.static_messages) == 2
    assert prompt.static_messages[0].role == "system"
    assert "Evaluate" in prompt.static_messages[0].content

    assert prompt.static_messages[1].role == "user"
    assert "Some small document." in prompt.static_messages[1].content


def test_build_compiled_prompt_with_assertions() -> None:
    """Test building a compiled prompt including matrix assertions."""
    matrix_assertions = [
        FlattenedAtom(
            atom_id="tda_11111111",
            question="Is it blue?",
            extraction_rule="Check for blue.",
            anchor_target="blue section",
            is_inverse=False,
            depends_on=(),
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

    prompt = MatrixSensorPromptBuilder.build_compiled_prompt(
        context_text, [node1], tda_id_to_alias, target_locale="fi", matrix_context=matrix_context
    )

    # Static prefix validation
    assert len(prompt.static_messages) == 2
    assert prompt.static_messages[1].role == "user"

    # Dynamic message validation
    assert len(prompt.dynamic_messages) == 1
    assert prompt.dynamic_messages[0].role == "user"
    content = prompt.dynamic_messages[0].content

    # Linguistic context injection validation
    assert "<linguistic_context>" in content
    assert "<required_output_language>fi</required_output_language>" in content

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

    prompt = MatrixSensorPromptBuilder.build_compiled_prompt(
        "Context", [node], {"tda_22222222": "a1"}, target_locale="fi", matrix_context=None
    )

    assert len(prompt.dynamic_messages) == 1
    content = prompt.dynamic_messages[0].content
    assert "a1" in content
    assert "Fallback claim text." in content
    assert "<question>" not in content


def test_build_caching_prefix_contains_evaluation_directives() -> None:
    """Regression test (RED): Ensure static system prompt includes anti-repetition and concise reasoning directives."""
    prompt = MatrixSensorPromptBuilder.build_caching_prefix("Sample document", None)
    system_text = prompt.static_messages[0].content

    # Verify that the system prompt explicitly bans repetitive keyword iteration and mandates concise reasoning
    assert "repetitive" in system_text.lower()
    assert "concise" in system_text.lower()


def test_build_compiled_prompt_empty_nodes_raises_app_exception() -> None:
    """Anti-happy path: Ensure building prompt with empty nodes raises AppException."""
    with pytest.raises(AppException) as exc_info:
        MatrixSensorPromptBuilder.build_compiled_prompt(
            "Context", [], {}, target_locale="fi", matrix_context=None
        )
    assert exc_info.value.status_code == 400
    assert "Cannot build prompt with empty nodes" in exc_info.value.message


def test_build_compiled_prompt_missing_alias_raises_app_exception() -> None:
    """Anti-happy path: Ensure missing alias for node raises AppException."""
    node = LinkedAtomGraph(
        atom=ExtractedAtom(
            tda_id="tda_11111111",
            resolved_claim="Claim text.",
            reasoning="R",
            source_quote="Q",
            source_id="chk_1",
            source_sequence_index=1,
        ),
    )
    with pytest.raises(AppException) as exc_info:
        MatrixSensorPromptBuilder.build_compiled_prompt(
            "Context", [node], {}, target_locale="fi", matrix_context=None
        )
    assert exc_info.value.status_code == 400
    assert "Missing alias for tda_id" in exc_info.value.message


def test_build_compiled_prompt_with_inverse_assertion() -> None:
    """Test building compiled prompt with is_inverse=True assertion."""
    matrix_assertions = [
        FlattenedAtom(
            atom_id="tda_33333333",
            question="Is it absent?",
            extraction_rule="Check absence.",
            anchor_target="target",
            is_inverse=True,
            depends_on=(),
        )
    ]
    matrix_context = MatrixEvaluationContext(matrix_assertions=matrix_assertions)
    node = LinkedAtomGraph(
        atom=ExtractedAtom(
            tda_id="tda_33333333",
            resolved_claim="Claim",
            reasoning="R",
            source_quote="Q",
            source_id="chk_1",
            source_sequence_index=1,
        ),
    )

    prompt = MatrixSensorPromptBuilder.build_compiled_prompt(
        "Context", [node], {"tda_33333333": "a3"}, target_locale="fi", matrix_context=matrix_context
    )
    content = prompt.dynamic_messages[0].content
    assert "<is_inverse>" in content
    assert "True" in content


def test_build_compiled_prompt_with_dependencies_and_status_map() -> None:
    """Test building compiled prompt with causal dependencies and status map."""
    dep1 = CausalEdge(
        tda_id="tda_11111111",
        source_id="chk_1",
        expected_status=ExecutionStatus.PASSED,
        edge_reasoning="Parent must be satisfied first.",
    )
    dep2 = CausalEdge(
        tda_id="tda_22222222",
        source_id="chk_2",
        expected_status=ExecutionStatus.FAILED,
        edge_reasoning="Alternative condition.",
    )
    node = LinkedAtomGraph(
        atom=ExtractedAtom(
            tda_id="tda_33333333",
            resolved_claim="Child claim.",
            reasoning="R",
            source_quote="Q",
            source_id="chk_1",
            source_sequence_index=1,
        ),
        depends_on=[dep1, dep2],
    )

    tda_id_to_alias = {
        "tda_33333333": "a_child",
        "tda_11111111": "a_p1",
    }
    atom_status_map = {
        "tda_11111111": ExecutionStatus.PASSED,
    }

    prompt = MatrixSensorPromptBuilder.build_compiled_prompt(
        context_text="Context text",
        nodes=[node],
        tda_id_to_alias=tda_id_to_alias,
        target_locale="fi",
        matrix_context=None,
        atom_status_map=atom_status_map,
    )
    content = prompt.dynamic_messages[0].content
    assert "<causal_dependencies>" in content
    assert 'parent_alias="a_p1"' in content
    assert "<actual_status>" in content
    assert "PASSED" in content
    assert 'parent_alias="tda_22222222"' in content
    assert "PENDING" in content
    assert "Parent must be satisfied first." in content


def test_build_compiled_prompt_empty_assertion_question_raises_app_exception() -> None:
    """Anti-happy path: matrix assertion with empty question raises AppException(VALIDATION_FAILED)."""
    tda_id = "tda_00000000000000000000000000000000"
    matrix_assertions = [
        FlattenedAtom(
            atom_id=tda_id,
            question="   ",
            extraction_rule="Extract rule",
            anchor_target="Anchor",
            is_inverse=False,
            depends_on=(),
        )
    ]
    matrix_context = MatrixEvaluationContext(matrix_assertions=matrix_assertions)
    node = LinkedAtomGraph(
        atom=ExtractedAtom(
            tda_id=tda_id,
            resolved_claim="Claim",
            reasoning="Reasoning",
            source_quote="Quote",
            source_id="chk_1",
            source_sequence_index=1,
        ),
    )

    with pytest.raises(AppException) as exc_info:
        MatrixSensorPromptBuilder.build_compiled_prompt(
            context_text="Some context",
            nodes=[node],
            tda_id_to_alias={tda_id: "a0"},
            target_locale="fi",
            matrix_context=matrix_context,
        )

    assert exc_info.value.status_code == 400
    assert "empty question" in exc_info.value.message


@pytest.mark.parametrize("invalid_locale", ["", "   ", None])
def test_build_compiled_prompt_invalid_locale_raises_app_exception(invalid_locale: str | None) -> None:
    """Anti-happy path: missing, empty, or whitespace target_locale raises AppException(VALIDATION_FAILED)."""
    node = LinkedAtomGraph(
        atom=ExtractedAtom(
            tda_id="tda_11111111",
            resolved_claim="Claim",
            reasoning="R",
            source_quote="Q",
            source_id="chk_1",
            source_sequence_index=1,
        ),
    )
    with pytest.raises(AppException) as exc_info:
        MatrixSensorPromptBuilder.build_compiled_prompt(
            context_text="Some context",
            nodes=[node],
            tda_id_to_alias={"tda_11111111": "a0"},
            target_locale=invalid_locale,  # type: ignore[arg-type]
        )

    assert exc_info.value.status_code == 400
    assert "target_locale must be a non-empty string" in exc_info.value.message
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
