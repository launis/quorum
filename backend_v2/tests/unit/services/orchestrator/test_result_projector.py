import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.dtos.dag_models import AtomExecutionState, CausalEdge, ExtractedAtom, LinkedAtomGraph
from backend_v2.models.enums import ExecutionStatus, SDUIComponentType
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

    # This should now succeed because contextual_override is mapped correctly.
    results, refs = ResultProjector.project([node], {"tda_12345678": state})

    assert len(results) == 1
    assert results[0].contextual_override is True
    assert results[0].source_quote is None


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

    results, refs = ResultProjector.project([node], {"tda_11111111": state}, matrix_id="blk_test123")

    assert len(results) == 1
    assert results[0].matrix_id == "blk_test123"


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

    # Pass child first in list; topological sort must order parent before child.
    # Also omit child from states to test pending state branch.
    parent_state = AtomExecutionState(
        tda_id="tda_11112222",
        status=ExecutionStatus.PASSED,
        evaluation_reasoning="Parent verified.",
    )
    results, refs = ResultProjector.project([child_node, parent_node], {"tda_11112222": parent_state})

    assert len(results) == 2
    assert results[0].tda_id == "tda_11112222"
    assert results[0].status == ExecutionStatus.PASSED
    assert results[1].tda_id == "tda_33334444"
    assert results[1].status == ExecutionStatus.PENDING
    assert results[1].evaluation_reasoning == "Pending evaluation."


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

    results, refs = ResultProjector.project([error_node, na_node], states)

    assert len(results) == 2
    err_res = next(r for r in results if r.tda_id == "tda_e0000001")
    assert refs["tda_e0000001"].sdui_component == SDUIComponentType.ERROR_CARD
    assert err_res.error_details is not None
    assert err_res.error_details.error_code == "DAG_EXECUTION_ERROR"

    assert refs["tda_a0000001"].sdui_component == SDUIComponentType.N_A_CARD


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
    # Empty string reasoning
    state = AtomExecutionState(
        tda_id="tda_f0000001",
        status=ExecutionStatus.PASSED,
        evaluation_reasoning="",
    )

    with pytest.raises(AppException) as exc_info:
        ResultProjector.project([node], {"tda_f0000001": state})

    assert exc_info.value.status_code == 400
