import pytest

from backend_v2.models.dtos.dag_models import (
    AtomExecutionState,
    CausalEdge,
    ExtractedAtom,
    LinkedAtomGraph,
)
from backend_v2.models.dtos.report.root import ReportDataDto
from backend_v2.models.enums import ExecutionStatus, SDUIComponentType
from backend_v2.services.orchestrator.result_projector import EnrichedResultProjector


@pytest.fixture
def sample_engine_output() -> dict:
    """Fixture providing a sample engine output matching the Phase 4 and 5 structure."""
    # Create atoms
    atom_1 = ExtractedAtom(
        reasoning="Reasoning 1",
        resolved_claim="Claim 1",
        source_quote="Quote 1",
        tda_id="tda_1111111111111111",
        source_id="chunk_1",
    )
    atom_2 = ExtractedAtom(
        reasoning="Reasoning 2",
        resolved_claim="Claim 2",
        source_quote="Quote 2",
        tda_id="tda_2222222222222222",
        source_id="chunk_2",
    )

    # Create graph
    node_1 = LinkedAtomGraph(atom=atom_1, depends_on=[])
    node_2 = LinkedAtomGraph(
        atom=atom_2,
        depends_on=[
            CausalEdge(
                edge_reasoning="Because of 1",
                tda_id="tda_1111111111111111",
                source_id="chunk_2",
            )
        ],
    )

    # Create states
    state_1 = AtomExecutionState(
        tda_id="tda_1111111111111111",
        status=ExecutionStatus.FAILED,
        evaluation_reasoning="Failed reason",
    )
    state_2 = AtomExecutionState(
        tda_id="tda_2222222222222222",
        status=ExecutionStatus.N_A,
        short_circuit_reason_tda_ids=["tda_1111111111111111"],
    )

    return {
        "execution_id": "exec_abc123",
        "workflow_id": "wf_123",
        "nodes": [node_1, node_2],
        "results": {
            "tda_1111111111111111": state_1,
            "tda_2222222222222222": state_2,
        },
        "global_synthesis": None,
    }


def test_enriched_result_projector_projects_correctly(sample_engine_output: dict):
    """Test that EnrichedResultProjector maps DAG output to ReportDataDto accurately."""
    projector = EnrichedResultProjector()

    report: ReportDataDto = projector.project(sample_engine_output)

    assert report.execution_id == "exec_abc123"
    assert report.workflow_id == "wf_123"
    assert report.global_metrics.total_atoms == 2
    assert report.global_metrics.short_circuited_na == 1
    assert report.global_metrics.evaluated == 1

    # Topological sort means tda_1 should be before tda_2
    assert len(report.results) == 2
    assert report.results[0].tda_id == "tda_1111111111111111"
    assert report.results[1].tda_id == "tda_2222222222222222"

    assert report.results[0].status == ExecutionStatus.FAILED
    assert report.results[0].evaluation_reasoning == "Failed reason"

    assert report.results[1].status == ExecutionStatus.N_A
    assert report.results[1].short_circuit_reason_tda_ids == ["tda_1111111111111111"]

    # Test hydrated_references
    assert len(report.hydrated_references) == 2
    assert report.hydrated_references["tda_1111111111111111"].sdui_component == SDUIComponentType.BOOLEAN_CARD
    assert report.hydrated_references["tda_1111111111111111"].resolved_claim == "Claim 1"
    assert report.hydrated_references["tda_2222222222222222"].source_quote == "Quote 2"
