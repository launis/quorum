from unittest.mock import AsyncMock
"""Tests for Topological Evaluator."""

import pytest

from backend_v2.models.dtos.dag_models import (
    CausalEdge,
    ExtractedAtom,
    LinkedAtomGraph,
)
from backend_v2.models.enums import ExecutionStatus
from backend_v2.services.orchestrator.topological_evaluator import TopologicalEvaluator


def create_atom(tda_id: str) -> ExtractedAtom:
    """Helper to create extracted atoms."""
    return ExtractedAtom(
        reasoning="reason",
        resolved_claim="claim",
        source_quote="quote",
        tda_id=tda_id,
        source_id="src",
    )


@pytest.mark.asyncio
async def test_successful_evaluation() -> None:
    """Tests successful parallel execution of a linear DAG."""
    evaluator = TopologicalEvaluator()

    nodes = [
        LinkedAtomGraph(atom=create_atom("tda_1111111111111111")),
        LinkedAtomGraph(
            atom=create_atom("tda_2222222222222222"),
            depends_on=[
                CausalEdge(
                    edge_reasoning="reason",
                    tda_id="tda_1111111111111111",
                    source_id="src",
                    expected_status=ExecutionStatus.PASSED,
                )
            ],
        ),
    ]

    async def mock_callback(
        batch_nodes: list[LinkedAtomGraph],
    ) -> dict[str, tuple[ExecutionStatus, str | None, dict[str, str]]]:
        return {node.atom.tda_id: (ExecutionStatus.PASSED, "OK", {}) for node in batch_nodes}

    states = await evaluator.evaluate_graph(nodes, mock_callback)

    assert states["tda_1111111111111111"].status == ExecutionStatus.PASSED
    assert states["tda_2222222222222222"].status == ExecutionStatus.PASSED


@pytest.mark.asyncio
async def test_phantom_edge_isolation() -> None:
    """Tests that missing dependencies trigger SYSTEM_ERROR for the child."""
    evaluator = TopologicalEvaluator()

    nodes = [
        LinkedAtomGraph(
            atom=create_atom("tda_1111111111111111"),
            depends_on=[
                CausalEdge(
                    edge_reasoning="reason",
                    tda_id="tda_9999999999999999",  # Does not exist
                    source_id="src",
                    expected_status=ExecutionStatus.PASSED,
                )
            ],
        ),
    ]

    async def mock_callback(
        batch_nodes: list[LinkedAtomGraph],
    ) -> dict[str, tuple[ExecutionStatus, str | None, dict[str, str]]]:
        return {node.atom.tda_id: (ExecutionStatus.PASSED, "OK", {}) for node in batch_nodes}

    states = await evaluator.evaluate_graph(nodes, mock_callback)

    assert states["tda_1111111111111111"].status == ExecutionStatus.SYSTEM_ERROR
    assert states["tda_1111111111111111"].evaluation_reasoning == "UNRESOLVED_DEPENDENCY"


@pytest.mark.asyncio
async def test_cyclic_dependency_detected() -> None:
    """Tests deterministic cycle breaking isolating involved nodes to SYSTEM_ERROR."""
    evaluator = TopologicalEvaluator()

    nodes = [
        LinkedAtomGraph(
            atom=create_atom("tda_1111111111111111"),
            depends_on=[
                CausalEdge(
                    edge_reasoning="reason",
                    tda_id="tda_2222222222222222",
                    source_id="src",
                    expected_status=ExecutionStatus.PASSED,
                )
            ],
        ),
        LinkedAtomGraph(
            atom=create_atom("tda_2222222222222222"),
            depends_on=[
                CausalEdge(
                    edge_reasoning="reason",
                    tda_id="tda_1111111111111111",
                    source_id="src",
                    expected_status=ExecutionStatus.PASSED,
                )
            ],
        ),
        LinkedAtomGraph(atom=create_atom("tda_3333333333333333")),  # Unrelated
    ]

    async def mock_callback(
        batch_nodes: list[LinkedAtomGraph],
    ) -> dict[str, tuple[ExecutionStatus, str | None, dict[str, str]]]:
        return {node.atom.tda_id: (ExecutionStatus.PASSED, "OK", {}) for node in batch_nodes}

    states = await evaluator.evaluate_graph(nodes, mock_callback)

    assert states["tda_1111111111111111"].status == ExecutionStatus.SYSTEM_ERROR
    assert states["tda_1111111111111111"].evaluation_reasoning == "CYCLIC_DEPENDENCY_DETECTED"

    assert states["tda_2222222222222222"].status == ExecutionStatus.SYSTEM_ERROR
    assert states["tda_2222222222222222"].evaluation_reasoning == "CYCLIC_DEPENDENCY_DETECTED"

    assert states["tda_3333333333333333"].status == ExecutionStatus.PASSED


@pytest.mark.asyncio
async def test_blocked_cascade() -> None:
    """Tests that a SYSTEM_ERROR parent blocks its children."""
    evaluator = TopologicalEvaluator()

    nodes = [
        LinkedAtomGraph(
            atom=create_atom("tda_1111111111111111"),
            depends_on=[
                CausalEdge(
                    edge_reasoning="reason",
                    tda_id="tda_9999999999999999",  # Phantom -> SYSTEM_ERROR
                    source_id="src",
                    expected_status=ExecutionStatus.PASSED,
                )
            ],
        ),
        LinkedAtomGraph(
            atom=create_atom("tda_2222222222222222"),
            depends_on=[
                CausalEdge(
                    edge_reasoning="reason",
                    tda_id="tda_1111111111111111",
                    source_id="src",
                    expected_status=ExecutionStatus.PASSED,
                )
            ],
        ),
    ]

    async def mock_callback(
        batch_nodes: list[LinkedAtomGraph],
    ) -> dict[str, tuple[ExecutionStatus, str | None, dict[str, str]]]:
        return {node.atom.tda_id: (ExecutionStatus.PASSED, "OK", {}) for node in batch_nodes}

    states = await evaluator.evaluate_graph(nodes, mock_callback)

    assert states["tda_1111111111111111"].status == ExecutionStatus.SYSTEM_ERROR
    assert states["tda_2222222222222222"].status == ExecutionStatus.BLOCKED


@pytest.mark.asyncio
async def test_na_short_circuit_cascade() -> None:
    """Tests N/A propagation if parent status does not match expected_status."""
    evaluator = TopologicalEvaluator()

    nodes = [
        LinkedAtomGraph(atom=create_atom("tda_1111111111111111")),
        LinkedAtomGraph(
            atom=create_atom("tda_2222222222222222"),
            depends_on=[
                CausalEdge(
                    edge_reasoning="reason",
                    tda_id="tda_1111111111111111",
                    source_id="src",
                    expected_status=ExecutionStatus.PASSED,
                )
            ],
        ),
        LinkedAtomGraph(
            atom=create_atom("tda_3333333333333333"),
            depends_on=[
                CausalEdge(
                    edge_reasoning="reason",
                    tda_id="tda_2222222222222222",
                    source_id="src",
                    expected_status=ExecutionStatus.PASSED,
                )
            ],
        ),
    ]

    async def mock_callback(
        batch_nodes: list[LinkedAtomGraph],
    ) -> dict[str, tuple[ExecutionStatus, str | None, dict[str, str]]]:
        results = {}
        for node in batch_nodes:
            # Parent fails, so child should short-circuit to N_A
            if node.atom.tda_id == "tda_1111111111111111":
                results[node.atom.tda_id] = (ExecutionStatus.FAILED, "failed", {})
            else:
                results[node.atom.tda_id] = (ExecutionStatus.PASSED, "passed", {})
        return results

    states = await evaluator.evaluate_graph(nodes, mock_callback)

    assert states["tda_1111111111111111"].status == ExecutionStatus.FAILED

    # First child short-circuits because it expected PASSED but got FAILED
    assert states["tda_2222222222222222"].status == ExecutionStatus.N_A
    assert "tda_1111111111111111" in states["tda_2222222222222222"].short_circuit_reason_tda_ids

    # Second child short-circuits because it expected PASSED but got N_A
    assert states["tda_3333333333333333"].status == ExecutionStatus.N_A
    assert "tda_2222222222222222" in states["tda_3333333333333333"].short_circuit_reason_tda_ids
