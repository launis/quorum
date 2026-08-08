from backend_v2.models.dtos.dag_models import AtomExecutionState, ExtractedAtom, LinkedAtomGraph
from backend_v2.models.enums import ExecutionStatus
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
