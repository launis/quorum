"""Unit tests for DAG Data Transfer Objects."""

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.dag_models import (
    AtomEvaluationResultDTO,
    AtomExecutionState,
    CausalEdge,
    ChunkPacketDTO,
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
        tda_id="tda_0195f3a0000070018234567890123456",
        source_id="src_1",
        expected_status=ExecutionStatus.PASSED,
    )
    assert edge.edge_reasoning == "Reasoning test"
    assert edge.tda_id == "tda_0195f3a0000070018234567890123456"
    assert edge.expected_status == ExecutionStatus.PASSED


def test_causal_edge_forbids_extra():
    """Test CausalEdge forbids extra fields."""
    with pytest.raises(ValidationError):
        CausalEdge(
            edge_reasoning="Reasoning test",
            tda_id="tda_0195f3a0000070018234567890123456",
            source_id="src_1",
            expected_status=ExecutionStatus.PASSED,
            extra_field="invalid",
        )


def test_extracted_atom_valid():
    """Test ExtractedAtom with valid data."""
    atom = ExtractedAtom(
        reasoning="Testing reasoning",
        resolved_claim="The claim",
        source_quotes=("The quote",),
        tda_id="tda_0195f3a0000070018234567890abcdef",
        source_id="src_1",
        source_sequence_index=0,
    )
    assert atom.resolved_claim == "The claim"
    assert atom.tda_id == "tda_0195f3a0000070018234567890abcdef"


def test_extracted_atom_invalid_tda_id():
    """Test ExtractedAtom with invalid tda_id format."""
    with pytest.raises(ValidationError):
        ExtractedAtom(
            reasoning="Reasoning",
            resolved_claim="Claim",
            source_quotes=("Quote",),
            tda_id="invalid_id_format",
            source_id="src_1",
            source_sequence_index=0,
        )


def test_extracted_atom_missing_quote_not_logical():
    """Test ExtractedAtom fails if quote is missing and not logical deduction."""
    with pytest.raises(
        ValidationError, match="source_quotes is mandatory unless is_logical_deduction or is_inverse is True"
    ):
        ExtractedAtom(
            reasoning="Reasoning",
            resolved_claim="Claim",
            is_logical_deduction=False,
            source_quotes=None,
            tda_id="tda_0195f3a0000070018234567890abcdef",
            source_id="src_1",
            source_sequence_index=0,
        )


def test_extracted_atom_quote_with_logical_deduction():
    """Test ExtractedAtom fails if quote is present when logical deduction."""
    with pytest.raises(
        ValidationError, match="source_quotes must be None if is_logical_deduction or is_inverse is True"
    ):
        ExtractedAtom(
            reasoning="Reasoning",
            resolved_claim="Claim",
            is_logical_deduction=True,
            source_quotes=("Should be None",),
            tda_id="tda_0195f3a0000070018234567890abcdef",
            source_id="src_1",
            source_sequence_index=0,
        )


def test_extracted_atom_segment_under_30_chars_when_m_greater_than_1_raises_error():
    """Test ExtractedAtom raises ValidationError if any segment is < 30 chars when m > 1."""
    with pytest.raises(
        ValidationError,
        match="source_quotes segment floor is at least 30 characters when m > 1",
    ):
        ExtractedAtom(
            reasoning="Valid premise reasoning.",
            resolved_claim="Valid claim statement.",
            is_logical_deduction=False,
            source_quotes=("Valid premise sentence here with enough characters.", "Short."),
            tda_id="tda_0195f3a0000070018234567890abcdef",
            source_id="src_1",
            source_sequence_index=0,
        )


def test_extracted_atom_allows_segment_up_to_1000_chars_gate2_ceiling():
    """Prove Gate 2 safety ceiling: ExtractedAtom must accept quotes up to 1,000 characters."""
    valid_long_quote = "A" * 602  # Exact length from Sitra block B4
    atom = ExtractedAtom(
        reasoning="Extracted premise from multi-sentence paragraph.",
        resolved_claim="Resolved empirical claim.",
        is_logical_deduction=False,
        source_quotes=(valid_long_quote,),
        tda_id="tda_0195f3a0000070018234567890abcdef",
        source_id="src_1",
        source_sequence_index=0,
    )
    assert atom.source_quotes == (valid_long_quote,)


def test_linked_atom_graph_valid():
    """Test LinkedAtomGraph with valid data."""
    atom = ExtractedAtom(
        reasoning="Testing reasoning",
        resolved_claim="The claim",
        source_quotes=("The quote",),
        tda_id="tda_0195f3a0000070018234567890abcdef",
        source_id="src_1",
        source_sequence_index=0,
    )
    graph = LinkedAtomGraph(atom=atom)
    assert graph.atom == atom
    assert graph.depends_on == []


def test_atom_execution_state_valid():
    """Test AtomExecutionState with valid data."""
    state = AtomExecutionState(
        tda_id="tda_0195f3a0000070018234567890abcdef",
        status=ExecutionStatus.PENDING,
    )
    assert state.tda_id == "tda_0195f3a0000070018234567890abcdef"
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
    """Test AtomExecutionState with valid source_quotes."""
    state = AtomExecutionState(
        tda_id="tda_0195f3a0000070018234567890abcdef",
        status=ExecutionStatus.PASSED,
        source_quotes=("Valid verbatim quote.",),
    )
    assert state.source_quotes == ("Valid verbatim quote.",)


def test_atom_execution_state_source_quote_long_allowed() -> None:
    """Test AtomExecutionState allows long verbatim source_quotes."""
    long_quote = "A" * 850
    state = AtomExecutionState(
        tda_id="tda_0195f3a0000070018234567890abcdef",
        status=ExecutionStatus.PASSED,
        source_quotes=(long_quote,),
    )
    assert state.source_quotes == (long_quote,)


def test_atom_evaluation_result_dto_valid() -> None:
    """Test AtomEvaluationResultDTO with valid fields."""
    dto = AtomEvaluationResultDTO(
        status=ExecutionStatus.PASSED,
        reasoning="Valid justification",
        source_quotes=("Exact quote",),
        extensions={"coaching": "Tip"},
    )
    assert dto.status == ExecutionStatus.PASSED
    assert dto.reasoning == "Valid justification"
    assert dto.source_quotes == ("Exact quote",)
    assert dto.extensions == {"coaching": "Tip"}


def test_atom_evaluation_result_dto_coerces_list_to_tuple() -> None:
    """Test AtomEvaluationResultDTO coerces list of quotes to tuple."""
    dto = AtomEvaluationResultDTO(
        status=ExecutionStatus.PASSED,
        source_quotes=["Segment 1 with sufficient length.", "Segment 2 with sufficient length."],
    )
    assert dto.source_quotes == ("Segment 1 with sufficient length.", "Segment 2 with sufficient length.")


def test_atom_evaluation_result_dto_frozen_immutability() -> None:
    """Test AtomEvaluationResultDTO is immutable (frozen=True)."""
    dto = AtomEvaluationResultDTO(
        status=ExecutionStatus.PASSED,
        reasoning="Reasoning",
    )
    with pytest.raises(ValidationError):
        dto.status = ExecutionStatus.FAILED


def test_atom_evaluation_result_dto_forbids_extra_fields() -> None:
    """Test AtomEvaluationResultDTO forbids extra fields."""
    with pytest.raises(ValidationError):
        AtomEvaluationResultDTO.model_validate(
            {
                "status": ExecutionStatus.PASSED,
                "extra_field": "disallowed",
            }
        )


def test_atom_evaluation_result_dto_missing_status_fails() -> None:
    """Test AtomEvaluationResultDTO fails if mandatory status is omitted."""
    with pytest.raises(ValidationError):
        AtomEvaluationResultDTO.model_validate({})


def test_atom_evaluation_result_dto_source_quote_long_allowed() -> None:
    """Test AtomEvaluationResultDTO accepts long verbatim source_quotes."""
    long_quote = "Q" * 850
    dto = AtomEvaluationResultDTO(
        status=ExecutionStatus.PASSED,
        source_quotes=(long_quote,),
    )
    assert dto.source_quotes == (long_quote,)


def test_chunk_packet_dto_valid() -> None:
    """Test ChunkPacketDTO with valid data."""
    packet = ChunkPacketDTO(
        start_block="blk_start",
        end_block="blk_end",
        packet_keys=["k1", "k2"],
    )
    assert packet.start_block == "blk_start"
    assert packet.end_block == "blk_end"
    assert packet.packet_keys == ["k1", "k2"]


def test_chunk_packet_dto_forbids_extra() -> None:
    """Test ChunkPacketDTO strictly forbids extra fields."""
    with pytest.raises(ValidationError):
        ChunkPacketDTO.model_validate(
            {
                "start_block": "blk_start",
                "end_block": "blk_end",
                "packet_keys": ["k1"],
                "extra_field": "disallowed",
            }
        )


def test_extracted_atom_more_than_3_segments_raises_error() -> None:
    """Test ExtractedAtom raises ValidationError if source_quotes has > 3 segments."""
    with pytest.raises(ValidationError, match="source_quotes cannot contain more than 3 segments"):
        ExtractedAtom(
            reasoning="Valid reasoning text.",
            resolved_claim="Valid claim text.",
            source_quotes=(
                "Valid quote segment 1 with at least thirty chars.",
                "Valid quote segment 2 with at least thirty chars.",
                "Valid quote segment 3 with at least thirty chars.",
                "Valid quote segment 4 with at least thirty chars.",
            ),
            tda_id="tda_0195f3a0000070018234567890abcdef",
            source_sequence_index=0,
        )


def test_extracted_atom_segment_over_1000_chars_raises_error() -> None:
    """Test ExtractedAtom raises ValidationError if any segment exceeds 1,000 chars."""
    with pytest.raises(ValidationError, match="source_quotes segment exceeds maximum allowed length"):
        ExtractedAtom(
            reasoning="Valid reasoning text.",
            resolved_claim="Valid claim text.",
            source_quotes=("A" * 1001,),
            tda_id="tda_0195f3a0000070018234567890abcdef",
            source_sequence_index=0,
        )
