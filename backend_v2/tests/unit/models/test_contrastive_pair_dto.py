"""Unit tests for ContrastivePairDTO and DAG transit invariants."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.dag_models import CausalEdge, ExtractedAtom, LinkedAtomGraph
from backend_v2.models.dtos.engine import FlattenedAtom, MatrixEvaluationContext
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.v2_core import (
    AcceptanceCriterion,
    AntiPattern,
    ContrastivePairDTO,
    TDAAssertion,
)
from backend_v2.services.orchestrator.prompts.matrix_sensor_prompt_builder import (
    MatrixSensorPromptBuilder,
)


def test_contrastive_pair_dto_positive() -> None:
    """Positive test: Valid pairs with length >= 10 instantiate cleanly and strip whitespace."""
    pair = ContrastivePairDTO(
        acceptable="  Valid acceptable exemplar with sufficient length  ",
        rejected="  Valid rejected counterpart demonstrating failure  ",
    )
    assert pair.acceptable == "Valid acceptable exemplar with sufficient length"
    assert pair.rejected == "Valid rejected counterpart demonstrating failure"

    # Invariant: Immutable frozen model
    with pytest.raises(ValidationError):
        pair.acceptable = "Mutating field should fail"  # type: ignore[misc]


def test_contrastive_pair_dto_negative_identical_exemplars() -> None:
    """Negative 1: acceptable == rejected raises ValidationError."""
    with pytest.raises(ValidationError, match="cannot be identical"):
        ContrastivePairDTO(
            acceptable="Identical exemplar text here",
            rejected="identical exemplar text here",
        )


def test_contrastive_pair_dto_negative_too_short_acceptable() -> None:
    """Negative 2: len(acceptable) < 10 raises ValidationError."""
    with pytest.raises(ValidationError, match="at least 10 characters"):
        ContrastivePairDTO(
            acceptable="Short",
            rejected="Valid rejected counterpart demonstrating failure",
        )


def test_contrastive_pair_dto_negative_too_short_rejected() -> None:
    """Negative 2b: len(rejected) < 10 raises ValidationError."""
    with pytest.raises(ValidationError, match="at least 10 characters"):
        ContrastivePairDTO(
            acceptable="Valid acceptable exemplar with sufficient length",
            rejected="Short",
        )


def test_contrastive_pair_dto_negative_whitespace_only() -> None:
    """Negative 3: Whitespace-only string raises ValidationError after stripping."""
    with pytest.raises(ValidationError, match="at least 10 characters"):
        ContrastivePairDTO(
            acceptable="          ",
            rejected="Valid rejected counterpart demonstrating failure",
        )


def test_contrastive_pair_dto_negative_missing_fields() -> None:
    """Negative 4: Missing required fields raises ValidationError."""
    with pytest.raises(ValidationError):
        ContrastivePairDTO.model_validate({"acceptable": "Valid acceptable exemplar with length"})

    with pytest.raises(ValidationError):
        ContrastivePairDTO.model_validate({"rejected": "Valid rejected counterpart demonstrating failure"})


def test_contrastive_pair_dto_extra_forbidden() -> None:
    """Negative 5: Extra fields are strictly forbidden."""
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ContrastivePairDTO(
            acceptable="Valid acceptable exemplar with sufficient length",
            rejected="Valid rejected counterpart demonstrating failure",
            unknown_extra="disallowed",  # type: ignore[call-arg]
        )


def test_tda_assertion_contrastive_example_schema() -> None:
    """Verify TDAAssertion schema validates ContrastivePairDTO cleanly."""
    valid_pair = ContrastivePairDTO(
        acceptable="Valid acceptable exemplar with sufficient length",
        rejected="Valid rejected counterpart demonstrating failure",
    )
    assertion = TDAAssertion(
        concept_description="Concept description testing contrastive pair integration",
        contrastive_example=valid_pair,
        inverse_evidence=False,
        aggregation_mode="ALL_MUST_COMPLY",
    )
    assert assertion.contrastive_example is not None
    assert assertion.contrastive_example.acceptable == "Valid acceptable exemplar with sufficient length"

    # Direct raw string should fail strict validation
    with pytest.raises(ValidationError):
        TDAAssertion(
            concept_description="Concept description testing contrastive pair integration",
            contrastive_example="ACCEPTABLE: something\nUNACCEPTABLE: something else",  # type: ignore[arg-type]
            inverse_evidence=False,
            aggregation_mode="ALL_MUST_COMPLY",
        )


def test_flattened_atom_rejects_raw_string_contrastive_example() -> None:
    """Verify FlattenedAtom strictly rejects raw string contrastive_example."""
    with pytest.raises(ValidationError):
        FlattenedAtom(
            atom_id="tda_1234567890abcdef",
            question="Valid test question",
            contrastive_example="Legacy string should fail",  # type: ignore[arg-type]
        )


def test_prompt_builder_omits_contrastive_grounding_when_none() -> None:
    """Verify MatrixSensorPromptBuilder completely omits <contrastive_grounding> when contrastive_example is None."""
    atom = FlattenedAtom(
        atom_id="tda_11111111",
        question="Is empirical evidence provided for the causal link?",
        contrastive_example=None,
    )
    node = LinkedAtomGraph(
        atom=ExtractedAtom(
            tda_id="tda_11111111",
            resolved_claim="Claim text",
            reasoning="R",
            source_quote="Q",
            source_id="chk_1",
            source_sequence_index=1,
        ),
    )
    context = MatrixEvaluationContext(matrix_assertions=[atom])

    prompt = MatrixSensorPromptBuilder.build_compiled_prompt(
        "Source document text",
        [node],
        {"tda_11111111": "a0"},
        target_locale="en",
        matrix_context=context,
    )
    dynamic_content = prompt.dynamic_messages[0].content
    assert "<contrastive_grounding>" not in dynamic_content
    assert "<acceptance_criteria>" not in dynamic_content
    assert "<anti_patterns>" not in dynamic_content
    assert "<syntactic_anchors>" not in dynamic_content


def test_prompt_builder_compiles_structured_fields_with_cdata() -> None:
    """Verify MatrixSensorPromptBuilder renders structured CDATA tags for contrastive, criteria, anti-patterns, and anchors."""
    atom = FlattenedAtom(
        atom_id="tda_22222222",
        question="Is empirical evidence provided for the causal link?",
        contrastive_example=ContrastivePairDTO(
            acceptable="The system latency improved by 14% across 50 iterations.",
            rejected="Our system is simply better and faster than existing tools.",
        ),
        acceptance_criteria=(
            AcceptanceCriterion(instruction="Verify statistical significance of claims."),
        ),
        anti_patterns=(
            AntiPattern(pattern="Vague references to unmeasured improvement."),
        ),
        syntactic_anchors=("latency", "iterations"),
    )
    node = LinkedAtomGraph(
        atom=ExtractedAtom(
            tda_id="tda_22222222",
            resolved_claim="Claim text",
            reasoning="R",
            source_quote="Q",
            source_id="chk_1",
            source_sequence_index=1,
        ),
    )
    context = MatrixEvaluationContext(matrix_assertions=[atom])

    prompt = MatrixSensorPromptBuilder.build_compiled_prompt(
        "Source document text",
        [node],
        {"tda_22222222": "a0"},
        target_locale="en",
        matrix_context=context,
    )
    dynamic_content = prompt.dynamic_messages[0].content
    assert "<contrastive_grounding>" in dynamic_content
    assert "<acceptable>" in dynamic_content
    assert "The system latency improved by 14% across 50 iterations." in dynamic_content
    assert "<rejected>" in dynamic_content
    assert "Our system is simply better and faster than existing tools." in dynamic_content
    assert "<acceptance_criteria>" in dynamic_content
    assert '<criterion index="1">' in dynamic_content
    assert "Verify statistical significance of claims." in dynamic_content
    assert "<anti_patterns>" in dynamic_content
    assert '<anti_pattern index="1">' in dynamic_content
    assert "Vague references to unmeasured improvement." in dynamic_content
    assert "<syntactic_anchors>" in dynamic_content
    assert "<anchor>" in dynamic_content
    assert "<![CDATA[latency" in dynamic_content


def test_transitive_causal_closure_three_deep_chain() -> None:
    """Verify transitive causal closure: A depends on B, B depends on C; sampling C retains A, B, C."""
    # Build a simulated dictionary of all matrix atoms
    atom_a = FlattenedAtom(
        atom_id="tda_aaaaaaaa",
        question="Assertion A",
        depends_on=(CausalEdge(tda_id="tda_bbbbbbbb", source_id="chk_1", expected_status=ExecutionStatus.PASSED, edge_reasoning="A requires B"),),
    )
    atom_b = FlattenedAtom(
        atom_id="tda_bbbbbbbb",
        question="Assertion B",
        depends_on=(CausalEdge(tda_id="tda_cccccccc", source_id="chk_1", expected_status=ExecutionStatus.PASSED, edge_reasoning="B requires C"),),
    )
    atom_c = FlattenedAtom(
        atom_id="tda_cccccccc",
        question="Assertion C",
        depends_on=(),
    )
    all_matrix_atoms: dict[str, FlattenedAtom] = {
        "tda_aaaaaaaa": atom_a,
        "tda_bbbbbbbb": atom_b,
        "tda_cccccccc": atom_c,
    }

    # If A is sampled into matrix_collected_atoms, transitive closure must pull B and C
    matrix_collected_atoms: list[FlattenedAtom] = [atom_a]
    closure_queue = list(matrix_collected_atoms)
    included_ids = {atom.atom_id for atom in matrix_collected_atoms}

    while closure_queue:
        current_atom = closure_queue.pop(0)
        causal_edges = current_atom.depends_on
        for edge in causal_edges:
            parent_id = edge.tda_id
            if parent_id in all_matrix_atoms and parent_id not in included_ids:
                parent_atom = all_matrix_atoms[parent_id]
                matrix_collected_atoms.append(parent_atom)
                included_ids.add(parent_id)
                closure_queue.append(parent_atom)

    collected_ids = [a.atom_id for a in matrix_collected_atoms]
    assert collected_ids == ["tda_aaaaaaaa", "tda_bbbbbbbb", "tda_cccccccc"]
