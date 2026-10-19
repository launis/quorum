"""Tests for Topological Evaluator."""

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.dag_models import (
    AtomEvaluationResultDTO,
    AtomExecutionState,
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
        source_quotes=("quote",),
        tda_id=tda_id,
        source_id="src",
        source_sequence_index=0,
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
        current_states: dict[str, AtomExecutionState],
    ) -> dict[str, AtomEvaluationResultDTO]:
        return {
            node.atom.tda_id: AtomEvaluationResultDTO(
                status=ExecutionStatus.PASSED,
                reasoning="OK",
                source_quotes=("quote",),
                extensions={},
            )
            for node in batch_nodes
        }

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
        current_states: dict[str, AtomExecutionState],
    ) -> dict[str, AtomEvaluationResultDTO]:
        return {
            node.atom.tda_id: AtomEvaluationResultDTO(
                status=ExecutionStatus.PASSED,
                reasoning="OK",
                source_quotes=("quote",),
                extensions={},
            )
            for node in batch_nodes
        }

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
        current_states: dict[str, AtomExecutionState],
    ) -> dict[str, AtomEvaluationResultDTO]:
        return {
            node.atom.tda_id: AtomEvaluationResultDTO(
                status=ExecutionStatus.PASSED,
                reasoning="OK",
                source_quotes=("quote",),
                extensions={},
            )
            for node in batch_nodes
        }

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
        current_states: dict[str, AtomExecutionState],
    ) -> dict[str, AtomEvaluationResultDTO]:
        return {
            node.atom.tda_id: AtomEvaluationResultDTO(
                status=ExecutionStatus.PASSED,
                reasoning="OK",
                source_quotes=("quote",),
                extensions={},
            )
            for node in batch_nodes
        }

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

    dispatched_atom_ids: list[str] = []

    async def mock_callback(
        batch_nodes: list[LinkedAtomGraph],
        current_states: dict[str, AtomExecutionState],
    ) -> dict[str, AtomEvaluationResultDTO]:
        results = {}
        for node in batch_nodes:
            dispatched_atom_ids.append(node.atom.tda_id)
            # Parent fails, so child should short-circuit to N_A
            if node.atom.tda_id == "tda_1111111111111111":
                results[node.atom.tda_id] = AtomEvaluationResultDTO(
                    status=ExecutionStatus.FAILED,
                    reasoning="failed",
                    source_quotes=None,
                    extensions={},
                )
            else:
                results[node.atom.tda_id] = AtomEvaluationResultDTO(
                    status=ExecutionStatus.PASSED,
                    reasoning="passed",
                    source_quotes=("quote",),
                    extensions={},
                )
        return results

    states = await evaluator.evaluate_graph(nodes, mock_callback)

    assert states["tda_1111111111111111"].status == ExecutionStatus.FAILED

    # First child short-circuits because it expected PASSED but got FAILED
    assert states["tda_2222222222222222"].status == ExecutionStatus.N_A
    assert "tda_1111111111111111" in states["tda_2222222222222222"].short_circuit_reason_tda_ids

    # Second child short-circuits because it expected PASSED but got N_A
    assert states["tda_3333333333333333"].status == ExecutionStatus.N_A
    assert "tda_2222222222222222" in states["tda_3333333333333333"].short_circuit_reason_tda_ids

    # Causal Markov Gating Assertion: Short-circuited nodes must NEVER be dispatched to batch callback
    assert dispatched_atom_ids == ["tda_1111111111111111"]
    assert "tda_2222222222222222" not in dispatched_atom_ids
    assert "tda_3333333333333333" not in dispatched_atom_ids


@pytest.mark.asyncio
async def test_dlq_marking_on_app_exception() -> None:
    """Tests that when batch_evaluation_callback raises AppException, nodes are marked with SYSTEM_ERROR."""
    evaluator = TopologicalEvaluator()
    nodes = [
        LinkedAtomGraph(atom=create_atom("tda_1111111111111111")),
        LinkedAtomGraph(atom=create_atom("tda_2222222222222222")),
    ]

    async def failing_callback(
        batch_nodes: list[LinkedAtomGraph],
        current_states: dict[str, AtomExecutionState],
    ) -> dict[str, AtomEvaluationResultDTO]:
        raise AppException(
            message="Simulated callback failure",
            details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.value},
        )

    states = await evaluator.evaluate_graph(nodes, failing_callback)

    assert states["tda_1111111111111111"].status == ExecutionStatus.SYSTEM_ERROR
    assert "EVALUATION_CRASH: Simulated callback failure" in states["tda_1111111111111111"].evaluation_reasoning
    assert states["tda_2222222222222222"].status == ExecutionStatus.SYSTEM_ERROR
    assert "EVALUATION_CRASH: Simulated callback failure" in states["tda_2222222222222222"].evaluation_reasoning


@pytest.mark.asyncio
async def test_missing_node_from_batch_response() -> None:
    """Tests that nodes omitted from callback results dict are isolated with SYSTEM_ERROR."""
    evaluator = TopologicalEvaluator()
    nodes = [
        LinkedAtomGraph(atom=create_atom("tda_1111111111111111")),
        LinkedAtomGraph(atom=create_atom("tda_2222222222222222")),
    ]

    async def partial_callback(
        batch_nodes: list[LinkedAtomGraph],
        current_states: dict[str, AtomExecutionState],
    ) -> dict[str, AtomEvaluationResultDTO]:
        # Only return result for the first node; omit the second
        return {
            "tda_1111111111111111": AtomEvaluationResultDTO(
                status=ExecutionStatus.PASSED,
                reasoning="OK",
                source_quotes=("quote",),
                extensions={},
            )
        }

    states = await evaluator.evaluate_graph(nodes, partial_callback)

    assert states["tda_1111111111111111"].status == ExecutionStatus.PASSED
    assert states["tda_2222222222222222"].status == ExecutionStatus.SYSTEM_ERROR
    assert states["tda_2222222222222222"].evaluation_reasoning == "Missing from batch response"


@pytest.mark.asyncio
async def test_dlq_marking_on_unexpected_runtime_error_and_downstream_blocked() -> None:
    """Verify Scenario NEG-06: RuntimeError in callback transitions wave nodes to SYSTEM_ERROR and children to BLOCKED."""
    evaluator = TopologicalEvaluator()
    node1 = LinkedAtomGraph(atom=create_atom("tda_1111111111111111"))
    node2 = LinkedAtomGraph(
        atom=create_atom("tda_2222222222222222"),
        depends_on=[
            CausalEdge(
                edge_reasoning="reason",
                tda_id="tda_1111111111111111",
                source_id="src",
                expected_status=ExecutionStatus.PASSED,
            )
        ],
    )
    nodes = [node1, node2]

    async def crashing_callback(
        batch_nodes: list[LinkedAtomGraph],
        current_states: dict[str, AtomExecutionState],
    ) -> dict[str, AtomEvaluationResultDTO]:
        raise RuntimeError("Unexpected LLM cluster crash")

    states = await evaluator.evaluate_graph(nodes, crashing_callback)

    # Wave 0 node must be SYSTEM_ERROR
    assert states["tda_1111111111111111"].status == ExecutionStatus.SYSTEM_ERROR
    assert "EVALUATION_CRASH: Unexpected LLM cluster crash" in states["tda_1111111111111111"].evaluation_reasoning

    # Downstream child must be BLOCKED
    assert states["tda_2222222222222222"].status == ExecutionStatus.BLOCKED

    # Zero nodes may remain PENDING
    for tda_id, state in states.items():
        assert state.status != ExecutionStatus.PENDING, f"Node {tda_id} remained PENDING"


@pytest.mark.asyncio
async def test_dlq_marking_on_exception_group() -> None:
    """Tests that ExceptionGroup in callback transitions nodes to SYSTEM_ERROR."""
    evaluator = TopologicalEvaluator()
    nodes = [
        LinkedAtomGraph(atom=create_atom("tda_1111111111111111")),
        LinkedAtomGraph(atom=create_atom("tda_2222222222222222")),
    ]

    async def eg_callback(
        batch_nodes: list[LinkedAtomGraph],
        current_states: dict[str, AtomExecutionState],
    ) -> dict[str, AtomEvaluationResultDTO]:
        raise ExceptionGroup("Batch evaluation errors", [ValueError("Err 1"), TimeoutError("Err 2")])

    states = await evaluator.evaluate_graph(nodes, eg_callback)

    assert states["tda_1111111111111111"].status == ExecutionStatus.SYSTEM_ERROR
    assert "EVALUATION_CRASH: Batch evaluation errors" in states["tda_1111111111111111"].evaluation_reasoning
    assert states["tda_2222222222222222"].status == ExecutionStatus.SYSTEM_ERROR
    assert "EVALUATION_CRASH: Batch evaluation errors" in states["tda_2222222222222222"].evaluation_reasoning
