"""Integration tests for TopologicalEvaluator (Epic 92: DAG Determinismi)."""

import asyncio

import pytest

from backend_v2.models.dtos.dag_models import CausalEdge, ExtractedAtom, LinkedAtomGraph
from backend_v2.models.enums import ExecutionStatus
from backend_v2.services.orchestrator.topological_evaluator import TopologicalEvaluator


@pytest.fixture
def evaluator() -> TopologicalEvaluator:
    return TopologicalEvaluator()


def create_mock_atom(tda_id: str) -> ExtractedAtom:
    return ExtractedAtom(
        tda_id=tda_id,
        reasoning="Test reasoning",
        resolved_claim="Test claim",
        source_quote="Test quote",
        source_id="chunk_1",
    )


@pytest.mark.asyncio
async def test_topological_evaluator_successful_run(evaluator: TopologicalEvaluator) -> None:
    """Test a basic DAG execution without short circuits or errors."""
    nodes = [
        LinkedAtomGraph(atom=create_mock_atom("tda_11111111111111111111111111111111"), depends_on=[]),
        LinkedAtomGraph(
            atom=create_mock_atom("tda_22222222222222222222222222222222"),
            depends_on=[
                CausalEdge(
                    tda_id="tda_11111111111111111111111111111111",
                    source_id="chunk_1",
                    edge_reasoning="Depends on 1",
                    expected_status=ExecutionStatus.PASSED,
                )
            ],
        ),
    ]

    async def mock_callback(node: LinkedAtomGraph) -> ExecutionStatus:
        await asyncio.sleep(0.01)
        return ExecutionStatus.PASSED

    results = await evaluator.evaluate_graph(nodes, mock_callback)

    assert len(results) == 2
    assert results["tda_11111111111111111111111111111111"].status == ExecutionStatus.PASSED
    assert results["tda_22222222222222222222222222222222"].status == ExecutionStatus.PASSED


@pytest.mark.asyncio
async def test_topological_evaluator_short_circuit(evaluator: TopologicalEvaluator) -> None:
    """Test N_A cascade when parent fails to meet expected status."""
    nodes = [
        LinkedAtomGraph(atom=create_mock_atom("tda_11111111111111111111111111111111"), depends_on=[]),
        LinkedAtomGraph(
            atom=create_mock_atom("tda_22222222222222222222222222222222"),
            depends_on=[
                CausalEdge(
                    tda_id="tda_11111111111111111111111111111111",
                    source_id="chunk_1",
                    edge_reasoning="Depends on 1 to be PASSED",
                    expected_status=ExecutionStatus.PASSED,
                )
            ],
        ),
    ]

    async def mock_callback(node: LinkedAtomGraph) -> ExecutionStatus:
        if node.atom.tda_id == "tda_11111111111111111111111111111111":
            return ExecutionStatus.FAILED
        return ExecutionStatus.PASSED

    results = await evaluator.evaluate_graph(nodes, mock_callback)

    assert results["tda_11111111111111111111111111111111"].status == ExecutionStatus.FAILED
    assert results["tda_22222222222222222222222222222222"].status == ExecutionStatus.N_A
    assert (
        "tda_11111111111111111111111111111111"
        in results["tda_22222222222222222222222222222222"].short_circuit_reason_tda_ids
    )


@pytest.mark.asyncio
async def test_topological_evaluator_blocked_cascade(evaluator: TopologicalEvaluator) -> None:
    """Test BLOCKED cascade when parent is BLOCKED or SYSTEM_ERROR."""
    nodes = [
        LinkedAtomGraph(atom=create_mock_atom("tda_11111111111111111111111111111111"), depends_on=[]),
        LinkedAtomGraph(
            atom=create_mock_atom("tda_22222222222222222222222222222222"),
            depends_on=[
                CausalEdge(
                    tda_id="tda_11111111111111111111111111111111",
                    source_id="chunk_1",
                    edge_reasoning="Depends on 1",
                    expected_status=ExecutionStatus.PASSED,
                )
            ],
        ),
    ]

    async def mock_callback(node: LinkedAtomGraph) -> ExecutionStatus:
        if node.atom.tda_id == "tda_11111111111111111111111111111111":
            return ExecutionStatus.SYSTEM_ERROR
        return ExecutionStatus.PASSED

    results = await evaluator.evaluate_graph(nodes, mock_callback)

    assert results["tda_11111111111111111111111111111111"].status == ExecutionStatus.SYSTEM_ERROR
    assert results["tda_22222222222222222222222222222222"].status == ExecutionStatus.BLOCKED


@pytest.mark.asyncio
async def test_topological_evaluator_cycle_breaker(evaluator: TopologicalEvaluator) -> None:
    """Test Cycle Breaker isolates cycles with SYSTEM_ERROR without deadlock."""
    nodes = [
        LinkedAtomGraph(
            atom=create_mock_atom("tda_11111111111111111111111111111111"),
            depends_on=[
                CausalEdge(
                    tda_id="tda_22222222222222222222222222222222",
                    source_id="chunk_1",
                    edge_reasoning="Cycle 1->2",
                    expected_status=ExecutionStatus.PASSED,
                )
            ],
        ),
        LinkedAtomGraph(
            atom=create_mock_atom("tda_22222222222222222222222222222222"),
            depends_on=[
                CausalEdge(
                    tda_id="tda_11111111111111111111111111111111",
                    source_id="chunk_1",
                    edge_reasoning="Cycle 2->1",
                    expected_status=ExecutionStatus.PASSED,
                )
            ],
        ),
    ]

    async def mock_callback(node: LinkedAtomGraph) -> ExecutionStatus:
        # Should not be called due to cycle isolation
        return ExecutionStatus.PASSED

    results = await evaluator.evaluate_graph(nodes, mock_callback)

    assert results["tda_11111111111111111111111111111111"].status == ExecutionStatus.SYSTEM_ERROR
    assert "CYCLIC_DEPENDENCY_DETECTED" in (results["tda_11111111111111111111111111111111"].evaluation_reasoning or "")
    assert results["tda_22222222222222222222222222222222"].status == ExecutionStatus.SYSTEM_ERROR
