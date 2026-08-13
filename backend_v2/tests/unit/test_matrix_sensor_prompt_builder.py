from polyfactory.factories.pydantic_factory import ModelFactory

from backend_v2.models.dtos.dag_models import ExtractedAtom, LinkedAtomGraph
from backend_v2.models.dtos.engine import FlattenedAtom, MatrixEvaluationContext
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.services.orchestrator.prompts.matrix_sensor_prompt_builder import MatrixSensorPromptBuilder


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
    assert prompt.static_messages[0]["role"] == "system"
    assert "Test objective." in prompt.static_messages[0]["content"]

    assert prompt.static_messages[1]["role"] == "user"
    assert "Massive Context Text" in prompt.static_messages[1]["content"]
    assert len(prompt.dynamic_messages) == 0


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
        context_text="Source text", nodes=[node], tda_id_to_alias={atom_id: alias}, matrix_context=matrix_ctx
    )

    assert len(prompt.dynamic_messages) == 1
    dyn_content = prompt.dynamic_messages[0]["content"]

    assert f'alias="{alias}"' in dyn_content
    assert "Is this a test? <bad>tag</bad>" in dyn_content
    assert "Extract something" in dyn_content
    assert "Anchor" in dyn_content
    assert "True" in dyn_content


def test_build_compiled_prompt_negative_empty_nodes() -> None:
    """PROMISE: Prove empty node lists are handled safely (anti-happy-path)."""
    prompt = MatrixSensorPromptBuilder.build_compiled_prompt(
        context_text="Source text", nodes=[], tda_id_to_alias={}, matrix_context=None
    )

    assert len(prompt.dynamic_messages) == 1
    assert "<execution_parameters>" in prompt.dynamic_messages[0]["content"]


def test_build_compiled_prompt_negative_missing_aliases() -> None:
    """PROMISE: Prove fallback to tda_id when alias is missing (anti-happy-path)."""
    atom_id = "tda_0987654321fedcba"
    atom = ExtractedAtomFactory.build(
        tda_id=atom_id, resolved_claim="Claim", is_logical_deduction=True, source_quote=None
    )
    node = LinkedAtomGraphFactory.build(atom=atom)

    prompt = MatrixSensorPromptBuilder.build_compiled_prompt(
        context_text="Context",
        nodes=[node],
        tda_id_to_alias={},  # Empty alias mapping
        matrix_context=None,
    )

    dyn_content = prompt.dynamic_messages[0]["content"]
    assert f'alias="{atom_id}"' in dyn_content  # Falls back to the raw ID
