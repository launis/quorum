import pytest
from backend_v2.services.orchestrator.graph_validator import GraphValidatorService

from backend_v2.models.dtos.dag_models import CausalEdge, ExtractedAtom, LinkedAtomGraph
from backend_v2.models.enums import ExecutionStatus


@pytest.mark.asyncio
async def test_graph_validator_phantom_edge():
    atom1 = ExtractedAtom(reasoning="R", resolved_claim="C", source_quote="Q", tda_id="tda_1", source_id="s1")
    graph1 = LinkedAtomGraph(
        atom=atom1, depends_on=[CausalEdge(edge_reasoning="E", tda_id="tda_phantom", source_id="s1")]
    )

    states = await GraphValidatorService.validate([graph1])

    assert states["tda_1"].status == ExecutionStatus.SYSTEM_ERROR
    assert "Phantom edge" in states["tda_1"].evaluation_reasoning


@pytest.mark.asyncio
async def test_graph_validator_cycle_detection():
    atom1 = ExtractedAtom(reasoning="R1", resolved_claim="C1", source_quote="Q1", tda_id="tda_1", source_id="s1")
    atom2 = ExtractedAtom(reasoning="R2", resolved_claim="C2", source_quote="Q2", tda_id="tda_2", source_id="s2")

    # tda_1 depends on tda_2
    graph1 = LinkedAtomGraph(atom=atom1, depends_on=[CausalEdge(edge_reasoning="E1", tda_id="tda_2", source_id="s1")])
    # tda_2 depends on tda_1
    graph2 = LinkedAtomGraph(atom=atom2, depends_on=[CausalEdge(edge_reasoning="E2", tda_id="tda_1", source_id="s2")])

    states = await GraphValidatorService.validate([graph1, graph2])

    assert states["tda_1"].status == ExecutionStatus.SYSTEM_ERROR
    assert states["tda_2"].status == ExecutionStatus.SYSTEM_ERROR
    assert "causal cycle" in states["tda_1"].evaluation_reasoning


@pytest.mark.asyncio
async def test_graph_validator_valid_dag():
    atom1 = ExtractedAtom(reasoning="R1", resolved_claim="C1", source_quote="Q1", tda_id="tda_1", source_id="s1")
    atom2 = ExtractedAtom(reasoning="R2", resolved_claim="C2", source_quote="Q2", tda_id="tda_2", source_id="s2")

    # tda_2 depends on tda_1
    graph1 = LinkedAtomGraph(atom=atom1, depends_on=[])
    graph2 = LinkedAtomGraph(atom=atom2, depends_on=[CausalEdge(edge_reasoning="E", tda_id="tda_1", source_id="s2")])

    states = await GraphValidatorService.validate([graph1, graph2])

    assert states["tda_1"].status == ExecutionStatus.PENDING
    assert states["tda_2"].status == ExecutionStatus.PENDING
