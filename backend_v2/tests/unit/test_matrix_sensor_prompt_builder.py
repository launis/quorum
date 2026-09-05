import pytest
from polyfactory.factories.pydantic_factory import ModelFactory

from backend_v2.exceptions import AppException
from backend_v2.models.dtos.dag_models import CausalEdge, ExtractedAtom, LinkedAtomGraph
from backend_v2.models.dtos.engine import FlattenedAtom, MatrixEvaluationContext
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.services.orchestrator.prompts.matrix_sensor_prompt_builder import MatrixSensorPromptBuilder


class CausalEdgeFactory(ModelFactory[CausalEdge]):
    __model__ = CausalEdge


class FlattenedAtomFactory(ModelFactory[FlattenedAtom]):
    __model__ = FlattenedAtom


class ExtractedAtomFactory(ModelFactory[ExtractedAtom]):
    __model__ = ExtractedAtom


class LinkedAtomGraphFactory(ModelFactory[LinkedAtomGraph]):
    __model__ = LinkedAtomGraph


class MatrixEvaluationContextFactory(ModelFactory[MatrixEvaluationContext]):
    __model__ = MatrixEvaluationContext


def test_build_caching_prefix_success() -> None:
    """PROMISE: Prove static prefix is built correctly without dynamic content."""
    matrix_ctx = MatrixEvaluationContextFactory.build(
        matrix_objective="Test objective.",
        allow_contextual_override=False,
    )

    prompt = MatrixSensorPromptBuilder.build_caching_prefix("Massive Context Text", matrix_context=matrix_ctx)

    assert isinstance(prompt, CompiledPrompt)
    assert len(prompt.static_messages) == 2
    assert prompt.static_messages[0].role == "system"
    assert "Test objective." in prompt.static_messages[0].content

    assert prompt.static_messages[1].role == "user"
    assert "Massive Context Text" in prompt.static_messages[1].content
    assert len(prompt.dynamic_messages) == 0


def test_build_caching_prefix_with_theory_grounding_xml() -> None:
    """PROMISE: Prove theory_grounding is injected as pure <theory_context> XML."""
    from backend_v2.models.v2_core import TheoryGrounding

    tg = TheoryGrounding(
        source_url="https://example.com/test",
        citation_reference="Test Framework Citation (2026)",
    )
    matrix_ctx = MatrixEvaluationContextFactory.build(
        theory_grounding=tg,
        matrix_objective="Test objective.",
    )

    prompt = MatrixSensorPromptBuilder.build_caching_prefix("Massive Context Text", matrix_context=matrix_ctx)
    system_content = prompt.static_messages[0].content

    assert "<theory_context>" in system_content
    assert "Test Framework Citation (2026)" in system_content
    assert "https://example.com/test" not in system_content


def test_build_compiled_prompt_cdata_encapsulation() -> None:
    """PROMISE: Prove CDATA encapsulation for dynamic matrix assertions."""
    atom_id = "tda_abcdef1234567890"
    alias = "a0"

    flat_atom = FlattenedAtomFactory.build(
        atom_id=atom_id,
        question="Is this a test? <bad>tag</bad>",
        extraction_rule="Extract something",
        anchor_target="Anchor",
        is_inverse=True,
    )

    matrix_ctx = MatrixEvaluationContextFactory.build(matrix_assertions=[flat_atom])

    atom = ExtractedAtomFactory.build(
        tda_id=atom_id, resolved_claim="Resolved", is_logical_deduction=True, source_quote=None
    )
    node = LinkedAtomGraphFactory.build(atom=atom)

    prompt = MatrixSensorPromptBuilder.build_compiled_prompt(
        context_text="Source text",
        nodes=[node],
        tda_id_to_alias={atom_id: alias},
        target_locale="fi",
        matrix_context=matrix_ctx,
    )

    assert len(prompt.dynamic_messages) == 1
    dyn_content = prompt.dynamic_messages[0].content

    assert "<linguistic_context>" in dyn_content
    assert "<required_output_language>fi</required_output_language>" in dyn_content
    assert "<language_mandate>" in dyn_content
    assert f'alias="{alias}"' in dyn_content
    assert "Is this a test? <bad>tag</bad>" in dyn_content
    assert "Extract something" in dyn_content
    assert "Anchor" in dyn_content
    assert "True" in dyn_content


def test_build_compiled_prompt_negative_empty_nodes() -> None:
    """PROMISE: Prove empty node lists crash the prompt builder (anti-happy-path)."""
    with pytest.raises(AppException) as exc_info:
        MatrixSensorPromptBuilder.build_compiled_prompt(
            context_text="Source text", nodes=[], tda_id_to_alias={}, target_locale="fi", matrix_context=None
        )
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"


def test_build_compiled_prompt_negative_missing_aliases() -> None:
    """PROMISE: Prove missing aliases crash the builder (anti-happy-path)."""
    atom_id = "tda_0987654321fedcba"
    atom = ExtractedAtomFactory.build(
        tda_id=atom_id, resolved_claim="Claim", is_logical_deduction=True, source_quote=None
    )
    node = LinkedAtomGraphFactory.build(atom=atom)

    with pytest.raises(AppException) as exc_info:
        MatrixSensorPromptBuilder.build_compiled_prompt(
            context_text="Context",
            nodes=[node],
            tda_id_to_alias={},  # Empty alias mapping
            target_locale="fi",
            matrix_context=None,
        )

    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"


def test_build_compiled_prompt_dependency_injection() -> None:
    """PROMISE: Prove that causal dependencies are injected accurately into the prompt."""
    parent_id = "tda_bbbbbbbbbbbbbbbb"
    child_id = "tda_cccccccccccccccc"

    parent_alias = "a0"
    child_alias = "a1"

    edge = CausalEdgeFactory.build(
        tda_id=parent_id, expected_status=ExecutionStatus.PASSED, edge_reasoning="Because A causes B."
    )

    child_atom = ExtractedAtomFactory.build(
        tda_id=child_id, resolved_claim="Child Claim", is_logical_deduction=True, source_quote=None
    )

    child_node = LinkedAtomGraphFactory.build(atom=child_atom, depends_on=[edge])

    atom_status_map = {parent_id: ExecutionStatus.FAILED}

    tda_id_to_alias = {
        parent_id: parent_alias,
        child_id: child_alias,
    }

    prompt = MatrixSensorPromptBuilder.build_compiled_prompt(
        context_text="Context",
        nodes=[child_node],
        tda_id_to_alias=tda_id_to_alias,
        target_locale="fi",
        matrix_context=None,
        atom_status_map=atom_status_map,
    )

    assert len(prompt.dynamic_messages) == 1
    dyn_content = prompt.dynamic_messages[0].content

    assert "<causal_dependencies>" in dyn_content
    assert f'<dependency parent_alias="{parent_alias}">' in dyn_content
    assert "<expected_status>" in dyn_content
    assert ExecutionStatus.PASSED.value in dyn_content
    assert "<actual_status>" in dyn_content
    assert ExecutionStatus.FAILED.value in dyn_content
    assert "<reasoning>" in dyn_content
    assert "Because A causes B." in dyn_content


@pytest.mark.parametrize("invalid_locale", ["", "   ", None])
def test_build_compiled_prompt_negative_invalid_locale(invalid_locale: str | None) -> None:
    """PROMISE: Prove that missing or blank target_locale triggers Fail-Fast validation."""
    atom_id = "tda_0987654321fedcba"
    atom = ExtractedAtomFactory.build(
        tda_id=atom_id, resolved_claim="Claim", is_logical_deduction=True, source_quote=None
    )
    node = LinkedAtomGraphFactory.build(atom=atom)

    with pytest.raises(AppException) as exc_info:
        MatrixSensorPromptBuilder.build_compiled_prompt(
            context_text="Context",
            nodes=[node],
            tda_id_to_alias={atom_id: "a0"},
            target_locale=invalid_locale,  # type: ignore[arg-type]
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert "target_locale must be a non-empty string" in exc_info.value.message
