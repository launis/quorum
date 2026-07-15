"""Unit tests for GraphValidatorService."""

import pytest

from backend_v2.models.dtos.dag_models import LinkedAtomGraph, CausalEdge, ExtractedAtom
from backend_v2.models.enums import ExecutionStatus
from backend_v2.services.orchestrator.graph_validator import GraphValidatorService


@pytest.fixture
def sample_atom() -> ExtractedAtom:
    """Fixture for creating a basic atom."""
    return ExtractedAtom(
        tda_id="tda_11111111111111111111111111111111",
        reasoning="test",
        resolved_claim="Claim",
        source_quote="Quote from text",
    )


@pytest.mark.asyncio
async def test_validate_valid_graph(sample_atom: ExtractedAtom) -> None:
    """Test validation of a valid acyclic graph without phantom edges."""
    atom_2 = sample_atom.model_copy(update={"tda_id": "tda_22222222222222222222222222222222"})

    graph_1 = LinkedAtomGraph(atom=sample_atom, depends_on=[])
    graph_2 = LinkedAtomGraph(atom=atom_2, depends_on=[CausalEdge(tda_id="tda_11111111111111111111111111111111", edge_reasoning="test", source_id="src_1")])

    states = await GraphValidatorService.validate([graph_1, graph_2])

    assert len(states) == 2
    assert states["tda_11111111111111111111111111111111"].status == ExecutionStatus.PENDING
    assert states["tda_22222222222222222222222222222222"].status == ExecutionStatus.PENDING


@pytest.mark.asyncio
async def test_validate_phantom_edge(sample_atom: ExtractedAtom) -> None:
    """Test validation detects phantom edges and sets SYSTEM_ERROR."""
    graph_1 = LinkedAtomGraph(atom=sample_atom, depends_on=[CausalEdge(tda_id="tda_99999999999999999999999999999999", edge_reasoning="test", source_id="src_1")])

    states = await GraphValidatorService.validate([graph_1])

    assert len(states) == 1
    assert states["tda_11111111111111111111111111111111"].status == ExecutionStatus.SYSTEM_ERROR
    assert states["tda_11111111111111111111111111111111"].evaluation_reasoning is not None
    assert "Phantom edge detected" in states["tda_11111111111111111111111111111111"].evaluation_reasoning


@pytest.mark.asyncio
async def test_validate_cyclic_dependency(sample_atom: ExtractedAtom) -> None:
    """Test validation detects cyclic dependencies."""
    atom_2 = sample_atom.model_copy(update={"tda_id": "tda_22222222222222222222222222222222"})

    # A depends on B, B depends on A
    graph_1 = LinkedAtomGraph(atom=sample_atom, depends_on=[CausalEdge(tda_id="tda_22222222222222222222222222222222", edge_reasoning="test", source_id="src_1")])
    graph_2 = LinkedAtomGraph(atom=atom_2, depends_on=[CausalEdge(tda_id="tda_11111111111111111111111111111111", edge_reasoning="test", source_id="src_1")])

    states = await GraphValidatorService.validate([graph_1, graph_2])

    assert len(states) == 2
    assert states["tda_11111111111111111111111111111111"].status == ExecutionStatus.SYSTEM_ERROR
    assert states["tda_11111111111111111111111111111111"].evaluation_reasoning is not None
    assert "CYCLIC_DEPENDENCY_DETECTED" in states["tda_11111111111111111111111111111111"].evaluation_reasoning
    assert states["tda_22222222222222222222222222222222"].status == ExecutionStatus.SYSTEM_ERROR
    assert states["tda_22222222222222222222222222222222"].evaluation_reasoning is not None
    assert "CYCLIC_DEPENDENCY_DETECTED" in states["tda_22222222222222222222222222222222"].evaluation_reasoning
