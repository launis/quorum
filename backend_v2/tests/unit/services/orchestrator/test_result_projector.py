import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.matrix import MatrixClaim, MatrixScale, TDAAssertion
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.dtos.dag_models import AtomExecutionState, CausalEdge, ExtractedAtom, LinkedAtomGraph
from backend_v2.models.dtos.hook_delta import MatrixProjectionResultDTO, ProjectedResultsDTO
from backend_v2.models.enums import ExecutionStatus, SDUIComponentType, XaiExtensionType
from backend_v2.services.orchestrator.result_projector import ResultProjector


def test_result_projector_logical_deduction_crash():
    """Reproduces the bug where a logical deduction (None quote) crashes AtomResultDTO."""
    atom = ExtractedAtom(
        tda_id="tda_12345678",
        reasoning="Test",
        resolved_claim="Test Claim",
        is_logical_deduction=True,
        source_quote=None,
        source_id="chunk_0",
        source_sequence_index=0,
    )
    node = LinkedAtomGraph(atom=atom, depends_on=[])

    state = AtomExecutionState(
        tda_id="tda_12345678", status=ExecutionStatus.PASSED, evaluation_reasoning="Passed because of X"
    )

    projected = ResultProjector.project([node], {"tda_12345678": state})

    assert isinstance(projected, ProjectedResultsDTO)
    assert len(projected.results) == 1
    assert projected.results[0].contextual_override is True
    assert projected.results[0].source_quote is None


def test_result_projector_injects_matrix_id():
    """Verifies that matrix_id is injected correctly when provided."""
    atom = ExtractedAtom(
        tda_id="tda_11111111",
        reasoning="Test",
        resolved_claim="Claim",
        is_logical_deduction=False,
        source_quote="Quote",
        source_id="chunk_0",
        source_sequence_index=0,
    )
    node = LinkedAtomGraph(atom=atom, depends_on=[])
    state = AtomExecutionState(tda_id="tda_11111111", status=ExecutionStatus.PASSED, evaluation_reasoning="Reasoning")

    projected = ResultProjector.project([node], {"tda_11111111": state}, matrix_id="blk_test123")

    assert isinstance(projected, ProjectedResultsDTO)
    assert len(projected.results) == 1
    assert projected.results[0].matrix_id == "blk_test123"


def test_result_projector_topological_sort_with_dependencies():
    """Verifies topological sorting with causal dependency edges and pending states."""
    parent_atom = ExtractedAtom(
        tda_id="tda_11112222",
        reasoning="Parent reasoning",
        resolved_claim="Parent Claim",
        is_logical_deduction=False,
        source_quote="Parent quote",
        source_id="chunk_0",
        source_sequence_index=0,
    )
    child_atom = ExtractedAtom(
        tda_id="tda_33334444",
        reasoning="Child reasoning",
        resolved_claim="Child Claim",
        is_logical_deduction=False,
        source_quote="Child quote",
        source_id="chunk_0",
        source_sequence_index=1,
    )
    edge = CausalEdge(
        edge_reasoning="Causal connection",
        tda_id="tda_11112222",
        source_id="chunk_0",
        expected_status=ExecutionStatus.PASSED,
    )
    parent_node = LinkedAtomGraph(atom=parent_atom, depends_on=[])
    child_node = LinkedAtomGraph(atom=child_atom, depends_on=[edge])

    parent_state = AtomExecutionState(
        tda_id="tda_11112222",
        status=ExecutionStatus.PASSED,
        evaluation_reasoning="Parent verified.",
    )
    projected = ResultProjector.project([child_node, parent_node], {"tda_11112222": parent_state})

    assert isinstance(projected, ProjectedResultsDTO)
    assert len(projected.results) == 2
    assert projected.results[0].tda_id == "tda_11112222"
    assert projected.results[0].status == ExecutionStatus.PASSED
    assert projected.results[1].tda_id == "tda_33334444"
    assert projected.results[1].status == ExecutionStatus.PENDING
    assert projected.results[1].evaluation_reasoning == "Pending evaluation."


def test_result_projector_system_error_and_na_cards():
    """Verifies SDUI component card mapping for SYSTEM_ERROR and N_A statuses."""
    error_atom = ExtractedAtom(
        tda_id="tda_e0000001",
        reasoning="Error node",
        resolved_claim="Error Claim",
        is_logical_deduction=False,
        source_quote="Error quote",
        source_id="chunk_0",
        source_sequence_index=0,
    )
    na_atom = ExtractedAtom(
        tda_id="tda_a0000001",
        reasoning="NA node",
        resolved_claim="NA Claim",
        is_logical_deduction=False,
        source_quote="NA quote",
        source_id="chunk_0",
        source_sequence_index=1,
    )
    error_node = LinkedAtomGraph(atom=error_atom, depends_on=[])
    na_node = LinkedAtomGraph(atom=na_atom, depends_on=[])

    states = {
        "tda_e0000001": AtomExecutionState(
            tda_id="tda_e0000001",
            status=ExecutionStatus.SYSTEM_ERROR,
            evaluation_reasoning="Failed fatally.",
        ),
        "tda_a0000001": AtomExecutionState(
            tda_id="tda_a0000001",
            status=ExecutionStatus.N_A,
            evaluation_reasoning="Not applicable.",
        ),
    }

    projected = ResultProjector.project([error_node, na_node], states)

    assert isinstance(projected, ProjectedResultsDTO)
    assert len(projected.results) == 2
    err_res = next(r for r in projected.results if r.tda_id == "tda_e0000001")
    assert projected.hydrated_references["tda_e0000001"].sdui_component == SDUIComponentType.ERROR_CARD
    assert err_res.error_details is not None
    assert err_res.error_details.error_code == "DAG_EXECUTION_ERROR"

    assert projected.hydrated_references["tda_a0000001"].sdui_component == SDUIComponentType.N_A_CARD


def test_result_projector_missing_reasoning_fails_fast():
    """Verifies that PASSED status without evaluation_reasoning raises AppException."""
    atom = ExtractedAtom(
        tda_id="tda_f0000001",
        reasoning="Reason",
        resolved_claim="Claim",
        is_logical_deduction=False,
        source_quote="Quote",
        source_id="chunk_0",
        source_sequence_index=0,
    )
    node = LinkedAtomGraph(atom=atom, depends_on=[])
    state = AtomExecutionState(
        tda_id="tda_f0000001",
        status=ExecutionStatus.PASSED,
        evaluation_reasoning="",
    )

    with pytest.raises(AppException) as exc_info:
        ResultProjector.project([node], {"tda_f0000001": state})

    assert exc_info.value.status_code == 400
    assert exc_info.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED.value}


def test_result_projector_inverse_evidence_passed():
    """Positive: assert projecting a passed inverse atom yields source_quote=None, contextual_override=False, and is_inverse_evidence=True."""
    atom = ExtractedAtom(
        tda_id="tda_1111aaaa",
        reasoning="Testing inverse pass",
        resolved_claim="Candidate does not display hostility",
        is_logical_deduction=False,
        is_inverse=True,
        source_quote=None,
        source_id="chunk_0",
        source_sequence_index=0,
    )
    node = LinkedAtomGraph(atom=atom, depends_on=[])
    state = AtomExecutionState(
        tda_id="tda_1111aaaa",
        status=ExecutionStatus.PASSED,
        evaluation_reasoning="No hostile statements observed in text.",
    )

    projected = ResultProjector.project([node], {"tda_1111aaaa": state})

    assert isinstance(projected, ProjectedResultsDTO)
    assert len(projected.results) == 1
    assert projected.results[0].status == ExecutionStatus.PASSED
    assert projected.results[0].source_quote is None
    assert projected.results[0].contextual_override is False
    assert projected.results[0].is_inverse_evidence is True


def test_result_projector_non_inverse_missing_quote_override():
    """Negative Partition 1: assert positive non-inverse atom without quote triggers contextual_override=True and is_inverse_evidence=False."""
    atom = ExtractedAtom(
        tda_id="tda_2222bbbb",
        reasoning="Testing logical deduction bypass",
        resolved_claim="Logical deduction claim",
        is_logical_deduction=True,
        is_inverse=False,
        source_quote=None,
        source_id="chunk_0",
        source_sequence_index=0,
    )
    node = LinkedAtomGraph(atom=atom, depends_on=[])
    state = AtomExecutionState(
        tda_id="tda_2222bbbb",
        status=ExecutionStatus.PASSED,
        evaluation_reasoning="Deduction verified.",
    )

    projected = ResultProjector.project([node], {"tda_2222bbbb": state})

    assert isinstance(projected, ProjectedResultsDTO)
    assert len(projected.results) == 1
    assert projected.results[0].status == ExecutionStatus.PASSED
    assert projected.results[0].source_quote is None
    assert projected.results[0].contextual_override is True
    assert projected.results[0].is_inverse_evidence is False


def test_result_projector_inverse_evidence_failed():
    """Negative Partition 2: assert failed atom projection yields source_quote=None, contextual_override=False, and is_inverse_evidence=False regardless of whether claim was inverse."""
    atom = ExtractedAtom(
        tda_id="tda_3333cccc",
        reasoning="Testing inverse failure",
        resolved_claim="Candidate does not display hostility",
        is_logical_deduction=False,
        is_inverse=True,
        source_quote=None,
        source_id="chunk_0",
        source_sequence_index=0,
    )
    node = LinkedAtomGraph(atom=atom, depends_on=[])
    state = AtomExecutionState(
        tda_id="tda_3333cccc",
        status=ExecutionStatus.FAILED,
        evaluation_reasoning="Hostile statements were observed.",
    )

    projected = ResultProjector.project([node], {"tda_3333cccc": state})

    assert isinstance(projected, ProjectedResultsDTO)
    assert len(projected.results) == 1
    assert projected.results[0].status == ExecutionStatus.FAILED
    assert projected.results[0].source_quote is None
    assert projected.results[0].contextual_override is False
    assert projected.results[0].is_inverse_evidence is False


def test_result_projector_project_matrix_results():
    """Verifies project_matrix_results returns MatrixProjectionResultDTO with clean domain output."""
    tda_id = "tda_44444444444444444444444444444444"
    atom = ExtractedAtom(
        tda_id=tda_id,
        reasoning="Valid claim reasoning",
        resolved_claim="Active listening displayed",
        is_logical_deduction=False,
        source_quote="I hear you clearly",
        source_id="chunk_0",
        source_sequence_index=0,
    )
    node = LinkedAtomGraph(atom=atom, depends_on=[])
    state = AtomExecutionState(
        tda_id=tda_id,
        status=ExecutionStatus.PASSED,
        evaluation_reasoning="Verified in chunk 0.",
        source_quote="I hear you clearly",
        extensions={XaiExtensionType.COACHING: "Good pacing."},
    )

    matrix_block = MatrixPromptBlock(
        id="blk_0123456789abcdef",
        slug="matrix_test",
        label=I18nText(translations={"en": "Test Matrix"}),
        description=I18nText(translations={"en": "Description"}),
        scales=[
            MatrixScale(
                score=5,
                ai_label="EXCELLENT",
                claims=[
                    MatrixClaim(
                        label=I18nText(translations={"en": "Active listening displayed"}),
                        tda_assertions=[
                            TDAAssertion(
                                tda_id=tda_id,
                                inverse_evidence=False,
                                aggregation_mode="EXISTS",
                                concept_description="Active listening displayed clearly",
                            )
                        ],
                    )
                ],
            )
        ],
    )

    proj_matrix = ResultProjector.project_matrix_results(
        nodes=[node],
        states={tda_id: state},
        matrix_id="blk_0123456789abcdef",
        matrix_block=matrix_block,
        raw_score=5.0,
        justification="Strong performance.",
    )

    assert isinstance(proj_matrix, MatrixProjectionResultDTO)
    assert len(proj_matrix.results) == 1
    assert proj_matrix.results[0].status == ExecutionStatus.PASSED
    assert proj_matrix.matrix_output.raw_score == 5.0
    assert proj_matrix.matrix_output.justification == "Strong performance."
    assert proj_matrix.matrix_output.evaluated_atoms[tda_id] == ExecutionStatus.PASSED
    assert proj_matrix.missing_context is None
    assert XaiExtensionType.COACHING in proj_matrix.matrix_output.extensions
    assert proj_matrix.matrix_output.extensions[XaiExtensionType.COACHING] == "Good pacing."
    assert proj_matrix.missing_context is None


def test_result_projector_external_edge_and_missing_context() -> None:
    """Test handling of external causal dependencies and missing context aggregation for failed/pending/system_error atoms."""
    tda_child = "tda_" + "c" * 32
    tda_edge = "tda_" + "e" * 32
    tda_sys = "tda_" + "d" * 32
    tda_unprojected = "tda_" + "f" * 32

    atom_child = ExtractedAtom(
        tda_id=tda_child,
        reasoning="Child reasoning",
        resolved_claim="Child Claim",
        is_logical_deduction=False,
        source_quote="Quote",
        source_id="chunk_0",
        source_sequence_index=0,
    )
    edge_ext = CausalEdge(
        edge_reasoning="External dependency",
        tda_id=tda_edge,
        source_id="chunk_0",
        expected_status=ExecutionStatus.PASSED,
    )
    node_child = LinkedAtomGraph(atom=atom_child, depends_on=[edge_ext])
    state_child = AtomExecutionState(
        tda_id=tda_child,
        status=ExecutionStatus.FAILED,
        evaluation_reasoning="Failed evaluation.",
    )

    atom_sys = ExtractedAtom(
        tda_id=tda_sys,
        reasoning="Sys error",
        resolved_claim="Sys Claim",
        is_logical_deduction=False,
        source_quote="Error quote",
        source_id="chunk_0",
        source_sequence_index=1,
    )
    node_sys = LinkedAtomGraph(atom=atom_sys, depends_on=[])
    state_sys = AtomExecutionState(
        tda_id=tda_sys,
        status=ExecutionStatus.SYSTEM_ERROR,
        evaluation_reasoning="System crashed.",
    )

    matrix_block = MatrixPromptBlock(
        id="blk_0123456789abcdef",
        slug="matrix_test",
        label=I18nText(translations={"en": "Test Matrix"}),
        description=I18nText(translations={"en": "Description"}),
        scales=[
            MatrixScale(
                score=1,
                ai_label="POOR",
                claims=[
                    MatrixClaim(
                        label=I18nText(translations={"en": "Claims"}),
                        tda_assertions=[
                            TDAAssertion(
                                tda_id=tda_child,
                                inverse_evidence=False,
                                aggregation_mode="EXISTS",
                                concept_description="Child concept",
                            ),
                            TDAAssertion(
                                tda_id=tda_sys,
                                inverse_evidence=False,
                                aggregation_mode="EXISTS",
                                concept_description="System concept",
                            ),
                            TDAAssertion(
                                tda_id=tda_unprojected,
                                inverse_evidence=False,
                                aggregation_mode="EXISTS",
                                concept_description="Unprojected concept",
                            ),
                        ],
                    )
                ],
            )
        ],
    )

    proj_matrix = ResultProjector.project_matrix_results(
        nodes=[node_child, node_sys],
        states={tda_child: state_child, tda_sys: state_sys},
        matrix_id="blk_0123456789abcdef",
        matrix_block=matrix_block,
        raw_score=1.0,
        justification="Poor performance.",
    )

    assert proj_matrix.missing_context is not None
    assert len(proj_matrix.missing_context.missing_atoms) == 3
    assert "Child concept" in proj_matrix.missing_context.missing_atoms
    assert "System concept (DLQ - Unscorable)" in proj_matrix.missing_context.missing_atoms
    assert "Unprojected concept" in proj_matrix.missing_context.missing_atoms

