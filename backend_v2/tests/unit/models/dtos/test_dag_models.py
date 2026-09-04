"""Unit tests for DAG Data Transfer Objects."""

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.dag_models import (
    AtomEvaluationResultDTO,
    AtomExecutionState,
    CausalEdge,
    ExtractedAtom,
    GlobalOntologyMap,
    LinkedAtomGraph,
    OntologyEntity,
)
from backend_v2.models.enums import ExecutionStatus


def test_causal_edge_valid():
    """Test CausalEdge with valid data."""
    edge = CausalEdge(
        edge_reasoning="Reasoning test",
        tda_id="tda_1234567890123456",
        source_id="src_1",
        expected_status=ExecutionStatus.PASSED,
    )
    assert edge.edge_reasoning == "Reasoning test"
    assert edge.tda_id == "tda_1234567890123456"
    assert edge.expected_status == ExecutionStatus.PASSED


def test_causal_edge_forbids_extra():
    """Test CausalEdge forbids extra fields."""
    with pytest.raises(ValidationError):
        CausalEdge(
            edge_reasoning="Reasoning test",
            tda_id="tda_1234567890123456",
            source_id="src_1",
            expected_status=ExecutionStatus.PASSED,
            extra_field="invalid",
        )


def test_extracted_atom_valid():
    """Test ExtractedAtom with valid data."""
    atom = ExtractedAtom(
        reasoning="Testing reasoning",
        resolved_claim="The claim",
        source_quote="The quote",
        tda_id="tda_1234567890abcdef",
        source_id="src_1",
        source_sequence_index=0,
    )
    assert atom.resolved_claim == "The claim"
    assert atom.tda_id == "tda_1234567890abcdef"


def test_extracted_atom_invalid_tda_id():
    """Test ExtractedAtom with invalid tda_id format."""
    with pytest.raises(ValidationError):
        ExtractedAtom(
            reasoning="Reasoning",
            resolved_claim="Claim",
            source_quote="Quote",
            tda_id="invalid_id_format",
            source_id="src_1",
            source_sequence_index=0,
        )


def test_extracted_atom_missing_quote_not_logical():
    """Test ExtractedAtom fails if quote is missing and not logical deduction."""
    with pytest.raises(ValidationError, match="source_quote is mandatory unless is_logical_deduction is True"):
        ExtractedAtom(
            reasoning="Reasoning",
            resolved_claim="Claim",
            is_logical_deduction=False,
            source_quote=None,
            tda_id="tda_1234567890abcdef",
            source_id="src_1",
            source_sequence_index=0,
        )


def test_extracted_atom_quote_with_logical_deduction():
    """Test ExtractedAtom fails if quote is present when logical deduction."""
    with pytest.raises(ValidationError, match="source_quote must be None if is_logical_deduction is True"):
        ExtractedAtom(
            reasoning="Reasoning",
            resolved_claim="Claim",
            is_logical_deduction=True,
            source_quote="Should be None",
            tda_id="tda_1234567890abcdef",
            source_id="src_1",
            source_sequence_index=0,
        )


def test_linked_atom_graph_valid():
    """Test LinkedAtomGraph with valid data."""
    atom = ExtractedAtom(
        reasoning="Testing reasoning",
        resolved_claim="The claim",
        source_quote="The quote",
        tda_id="tda_1234567890abcdef",
        source_id="src_1",
        source_sequence_index=0,
    )
    graph = LinkedAtomGraph(atom=atom)
    assert graph.atom == atom
    assert graph.depends_on == []


def test_atom_execution_state_valid():
    """Test AtomExecutionState with valid data."""
    state = AtomExecutionState(
        tda_id="tda_1234567890abcdef",
        status=ExecutionStatus.PENDING,
    )
    assert state.tda_id == "tda_1234567890abcdef"
    assert state.status == ExecutionStatus.PENDING
    assert state.short_circuit_reason_tda_ids == []


def test_ontology_entity_valid():
    """Test OntologyEntity with valid data."""
    entity = OntologyEntity(name="Entity1", description="Desc")
    assert entity.name == "Entity1"


def test_global_ontology_map_valid():
    """Test GlobalOntologyMap with valid data."""
    entity = OntologyEntity(name="Entity1", description="Desc")
    gmap = GlobalOntologyMap(entities=[entity], macro_rules=["Rule 1"])
    assert len(gmap.entities) == 1
    assert gmap.entities[0].name == "Entity1"
    assert gmap.macro_rules == ["Rule 1"]


def test_atom_execution_state_source_quote_valid() -> None:
    """Test AtomExecutionState with valid source_quote."""
    state = AtomExecutionState(
        tda_id="tda_1234567890abcdef",
        status=ExecutionStatus.PASSED,
        source_quote="Valid verbatim quote.",
    )
    assert state.source_quote == "Valid verbatim quote."


def test_atom_execution_state_source_quote_max_length_exceeded() -> None:
    """Test AtomExecutionState enforces max_length=500 on source_quote."""
    oversized_quote = "A" * 501
    with pytest.raises(ValidationError):
        AtomExecutionState(
            tda_id="tda_1234567890abcdef",
            status=ExecutionStatus.PASSED,
            source_quote=oversized_quote,
        )


def test_atom_evaluation_result_dto_valid() -> None:
    """Test AtomEvaluationResultDTO with valid fields."""
    dto = AtomEvaluationResultDTO(
        status=ExecutionStatus.PASSED,
        reasoning="Valid justification",
        source_quote="Exact quote",
        extensions={"coaching": "Tip"},
    )
    assert dto.status == ExecutionStatus.PASSED
    assert dto.reasoning == "Valid justification"
    assert dto.source_quote == "Exact quote"
    assert dto.extensions == {"coaching": "Tip"}


def test_atom_evaluation_result_dto_frozen_immutability() -> None:
    """Test AtomEvaluationResultDTO is immutable (frozen=True)."""
    dto = AtomEvaluationResultDTO(
        status=ExecutionStatus.PASSED,
        reasoning="Reasoning",
    )
    with pytest.raises(ValidationError):
        dto.status = ExecutionStatus.FAILED  # type: ignore[misc]


def test_atom_evaluation_result_dto_forbids_extra_fields() -> None:
    """Test AtomEvaluationResultDTO forbids extra fields."""
    with pytest.raises(ValidationError):
        AtomEvaluationResultDTO(
            status=ExecutionStatus.PASSED,
            extra_field="disallowed",  # type: ignore[call-arg]
        )


def test_atom_evaluation_result_dto_missing_status_fails() -> None:
    """Test AtomEvaluationResultDTO fails if mandatory status is omitted."""
    with pytest.raises(ValidationError):
        AtomEvaluationResultDTO()  # type: ignore[call-arg]


def test_atom_evaluation_result_dto_source_quote_max_length() -> None:
    """Test AtomEvaluationResultDTO enforces max_length=500 on source_quote."""
    oversized_quote = "Q" * 501
    with pytest.raises(ValidationError):
        AtomEvaluationResultDTO(
            status=ExecutionStatus.PASSED,
            source_quote=oversized_quote,
        )
