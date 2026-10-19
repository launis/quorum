"""Topological Evaluator.

Executes a Directed Acyclic Graph (DAG) of Enriched Atoms using a
deterministic wave-based topological sort (Kahn's Algorithm),
preventing deadlocks and enabling bulk micro-prompt batching.
"""

import asyncio
import logging
from collections.abc import Awaitable, Callable

import networkx as nx

logger = logging.getLogger(__name__)
from backend_v2.models.dtos.dag_models import AtomEvaluationResultDTO, AtomExecutionState, CausalEdge, LinkedAtomGraph
from backend_v2.models.enums import ExecutionStatus

__all__ = ["TopologicalEvaluator"]


class TopologicalEvaluator:
    """Evaluates a DAG of LinkedAtomGraphs deterministically via Kahn's Algorithm.

    Enforces the Local Causal Markov Condition via Kahn's wave-based topological evaluation:
        P(A_1, ..., A_n | D) = prod_{k=1}^W prod_{A_i in Wave_k} P(A_i | Parents_G(A_i), D)

    Within each topological wave k, every node possesses in_degree == 0 relative to remaining
    un-evaluated nodes, guaranteeing that all causal antecedents Parents_G(A_i) have already been
    deterministically evaluated. Nodes within the same wave are conditionally independent given the
    fixed conditioning set of resolved parent outcomes and document context, enabling sound,
    safe concurrent batch evaluation.

    If any parent fails to satisfy its required expected_status, downstream child nodes deterministically
    short-circuit with P(A_i = BLOCKED | Parent != expected) = 1.0, assigning ExecutionStatus.N_A
    without invoking the LLM batch evaluation callback.

    Attributes:
        None
    """

    @staticmethod
    def _dlq_mark_node_error(state: AtomExecutionState, exc: BaseException) -> AtomExecutionState:
        """Dead-letter error recording for failed atom evaluations within wave.

        Args:
            state: The current atom execution state to update.
            exc: The caught exception to record.

        Returns:
            Updated atom execution state with SYSTEM_ERROR status.
        """
        return state.model_copy(
            update={"status": ExecutionStatus.SYSTEM_ERROR, "evaluation_reasoning": f"EVALUATION_CRASH: {str(exc)}"}
        )

    async def evaluate_graph(
        self,
        nodes: list[LinkedAtomGraph],
        batch_evaluation_callback: Callable[
            [list[LinkedAtomGraph], dict[str, AtomExecutionState]], Awaitable[dict[str, AtomEvaluationResultDTO]]
        ],
    ) -> dict[str, AtomExecutionState]:
        """Evaluates a graph of atoms deterministically using Kahn's Algorithm.

        Executes wave-by-wave topological evaluation:
        1. Identifies all nodes with in_degree == 0 (Wave 0).
        2. Checks causal preconditions against resolved parent states. If any precondition
           fails, short-circuits the node to ExecutionStatus.N_A and prunes child dispatch.
        3. Dispatches satisfying in-degree 0 nodes concurrently to batch_evaluation_callback
           under conditional Markov isolation.
        4. Decrements in-degree of downstream children and iterates until all waves complete.

        Args:
            nodes: The list of atom graph nodes to evaluate.
            batch_evaluation_callback: An asynchronous callback that evaluates a batch
                of nodes simultaneously and returns a dictionary mapping tda_id to an
                AtomEvaluationResultDTO.

        Returns:
            A dictionary mapping tda_id to its final AtomExecutionState.
        """
        states: dict[str, AtomExecutionState] = {}
        node_map: dict[str, LinkedAtomGraph] = {n.atom.tda_id: n for n in nodes}
        in_degree: dict[str, int] = {}
        adj: dict[str, list[str]] = {}
        for node in nodes:
            tda_id = node.atom.tda_id
            states[tda_id] = AtomExecutionState(
                tda_id=tda_id, status=ExecutionStatus.PENDING, short_circuit_reason_tda_ids=[], extensions={}
            )
            in_degree[tda_id] = 0
            adj[tda_id] = []
        g = nx.DiGraph()
        for node in nodes:
            child_id = node.atom.tda_id
            g.add_node(child_id)
            for edge in node.depends_on:
                parent_id = edge.tda_id
                if parent_id not in node_map:
                    states[child_id] = states[child_id].model_copy(
                        update={"status": ExecutionStatus.SYSTEM_ERROR, "evaluation_reasoning": "UNRESOLVED_DEPENDENCY"}
                    )
                else:
                    g.add_edge(parent_id, child_id)
                    adj[parent_id].append(child_id)
                    in_degree[child_id] += 1
        cycles = await asyncio.to_thread(list, nx.simple_cycles(g))
        if cycles:
            for cycle in cycles:
                for cycle_node_id in cycle:
                    if states[cycle_node_id].status != ExecutionStatus.SYSTEM_ERROR:
                        states[cycle_node_id] = states[cycle_node_id].model_copy(
                            update={
                                "status": ExecutionStatus.SYSTEM_ERROR,
                                "evaluation_reasoning": "CYCLIC_DEPENDENCY_DETECTED",
                            }
                        )
        queue = [tda_id for tda_id, deg in in_degree.items() if deg == 0]
        while queue:
            pending_nodes = [node_map[tda_id] for tda_id in queue if states[tda_id].status == ExecutionStatus.PENDING]
            if pending_nodes:
                try:
                    results = await batch_evaluation_callback(pending_nodes, states)
                    for node in pending_nodes:
                        if node.atom.tda_id in results:
                            res = results[node.atom.tda_id]
                            states[node.atom.tda_id] = states[node.atom.tda_id].model_copy(
                                update={
                                    "status": res.status,
                                    "evaluation_reasoning": res.reasoning,
                                    "source_quotes": res.source_quotes,
                                    "extensions": res.extensions,
                                }
                            )
                        else:
                            states[node.atom.tda_id] = states[node.atom.tda_id].model_copy(
                                update={
                                    "status": ExecutionStatus.SYSTEM_ERROR,
                                    "evaluation_reasoning": "Missing from batch response",
                                }
                            )
                except BaseException as e:
                    logger.error("[TopologicalEvaluator] Wave evaluation failed: %s", e, exc_info=True)
                    for node in pending_nodes:
                        states[node.atom.tda_id] = self._dlq_mark_node_error(states[node.atom.tda_id], e)
            next_queue = []
            for parent_id in queue:
                parent_state = states[parent_id]
                for child_id in adj[parent_id]:
                    child_node = node_map[child_id]
                    parent_edge: CausalEdge | None = next(
                        (e for e in child_node.depends_on if e.tda_id == parent_id), None
                    )
                    if parent_state.status in (ExecutionStatus.SYSTEM_ERROR, ExecutionStatus.BLOCKED):
                        states[child_id] = states[child_id].model_copy(update={"status": ExecutionStatus.BLOCKED})
                    elif parent_edge and parent_state.status != parent_edge.expected_status:
                        reasons = list(states[child_id].short_circuit_reason_tda_ids)
                        if parent_id not in reasons:
                            reasons.append(parent_id)
                        states[child_id] = states[child_id].model_copy(
                            update={"status": ExecutionStatus.N_A, "short_circuit_reason_tda_ids": reasons}
                        )
                    in_degree[child_id] -= 1
                    if in_degree[child_id] == 0:
                        next_queue.append(child_id)
            queue = next_queue
        for tda_id, state in states.items():
            if state.status == ExecutionStatus.PENDING:
                states[tda_id] = state.model_copy(
                    update={
                        "status": ExecutionStatus.BLOCKED,
                        "evaluation_reasoning": "BLOCKED_BY_CYCLE_OR_UNRESOLVED_PARENT",
                    }
                )
        return states
