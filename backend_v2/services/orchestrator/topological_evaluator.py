"""Topological Evaluator.

Executes a Directed Acyclic Graph (DAG) of Enriched Atoms using a
deterministic wave-based topological sort (Kahn's Algorithm),
preventing deadlocks and enabling bulk micro-prompt batching.
"""

import asyncio
from collections.abc import Awaitable, Callable

import networkx as nx

from backend_v2.exceptions import AppException
from backend_v2.models.dtos.dag_models import AtomExecutionState, CausalEdge, LinkedAtomGraph
from backend_v2.models.enums import ExecutionStatus


class TopologicalEvaluator:
    """Evaluates a DAG of LinkedAtomGraphs deterministically via Kahn's Algorithm.

    Attributes:
        None
    """

    async def evaluate_graph(
        self,
        nodes: list[LinkedAtomGraph],
        batch_evaluation_callback: Callable[
            [list[LinkedAtomGraph], dict[str, AtomExecutionState]],
            Awaitable[dict[str, tuple[ExecutionStatus, str | None, dict[str, str]]]],
        ],
    ) -> dict[str, AtomExecutionState]:
        """Evaluates a graph of atoms deterministically using Kahn's Algorithm.

        Args:
            nodes: The list of atom graph nodes to evaluate.
            batch_evaluation_callback: An asynchronous callback that evaluates a batch
                of nodes simultaneously and returns a dictionary mapping tda_id to a
                tuple of (ExecutionStatus, reasoning, extensions).

        Returns:
            A dictionary mapping tda_id to its final AtomExecutionState.
        """
        states: dict[str, AtomExecutionState] = {}
        node_map: dict[str, LinkedAtomGraph] = {n.atom.tda_id: n for n in nodes}

        in_degree: dict[str, int] = {}
        adj: dict[str, list[str]] = {}

        # Initialize states, in-degree, and adjacency list
        for node in nodes:
            tda_id = node.atom.tda_id
            states[tda_id] = AtomExecutionState(
                tda_id=tda_id,
                status=ExecutionStatus.PENDING,
            )
            in_degree[tda_id] = 0
            adj[tda_id] = []

        # Step 1: Structural Integrity (Phantom Edges & Cycles)
        g = nx.DiGraph()

        for node in nodes:
            child_id = node.atom.tda_id
            g.add_node(child_id)
            for edge in node.depends_on:
                parent_id = edge.tda_id
                if parent_id not in node_map:
                    # Phantom edge detected: Isolate child node immediately
                    states[child_id] = states[child_id].model_copy(
                        update={
                            "status": ExecutionStatus.SYSTEM_ERROR,
                            "evaluation_reasoning": "UNRESOLVED_DEPENDENCY",
                        }
                    )
                else:
                    # Directed edge from Parent -> Child
                    g.add_edge(parent_id, child_id)
                    adj[parent_id].append(child_id)
                    in_degree[child_id] += 1

        # Detect cycles in thread pool to prevent Event Loop freezing
        cycles = await asyncio.to_thread(list, nx.simple_cycles(g))
        if cycles:
            for cycle in cycles:
                for cycle_node_id in cycle:
                    # Isolate cycle nodes
                    if states[cycle_node_id].status != ExecutionStatus.SYSTEM_ERROR:
                        states[cycle_node_id] = states[cycle_node_id].model_copy(
                            update={
                                "status": ExecutionStatus.SYSTEM_ERROR,
                                "evaluation_reasoning": "CYCLIC_DEPENDENCY_DETECTED",
                            }
                        )

        # Step 2: Kahn's Algorithm (Wave-Based Evaluation)
        # Seed the initial queue with all nodes having in-degree 0
        queue = [tda_id for tda_id, deg in in_degree.items() if deg == 0]

        while queue:
            # Filter the current wave for nodes that are strictly PENDING
            pending_nodes = [node_map[tda_id] for tda_id in queue if states[tda_id].status == ExecutionStatus.PENDING]

            if pending_nodes:
                try:
                    results = await batch_evaluation_callback(pending_nodes, states)
                    for node in pending_nodes:
                        if node.atom.tda_id in results:
                            res = results[node.atom.tda_id]
                            status, reasoning, extensions = res
                            states[node.atom.tda_id] = states[node.atom.tda_id].model_copy(
                                update={
                                    "status": status,
                                    "evaluation_reasoning": reasoning,
                                    "extensions": extensions,
                                }
                            )
                        else:
                            states[node.atom.tda_id] = states[node.atom.tda_id].model_copy(
                                update={
                                    "status": ExecutionStatus.SYSTEM_ERROR,
                                    "evaluation_reasoning": "Missing from batch response",
                                }
                            )
                except AppException as e:
                    for node in pending_nodes:
                        states[node.atom.tda_id] = states[node.atom.tda_id].model_copy(
                            update={
                                "status": ExecutionStatus.SYSTEM_ERROR,
                                "evaluation_reasoning": f"EVALUATION_CRASH: {str(e)}",
                            }
                        )

            next_queue = []

            # Propagate state to children and populate next wave
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
                        # Short-circuit logic
                        reasons = list(states[child_id].short_circuit_reason_tda_ids)
                        if parent_id not in reasons:
                            reasons.append(parent_id)
                        states[child_id] = states[child_id].model_copy(
                            update={
                                "status": ExecutionStatus.N_A,
                                "short_circuit_reason_tda_ids": reasons,
                            }
                        )

                    in_degree[child_id] -= 1
                    if in_degree[child_id] == 0:
                        next_queue.append(child_id)

            queue = next_queue

        # Safety net: Any nodes remaining PENDING after wave evaluation must be
        # blocked by unresolved cycles.
        for tda_id, state in states.items():
            if state.status == ExecutionStatus.PENDING:
                states[tda_id] = state.model_copy(
                    update={
                        "status": ExecutionStatus.BLOCKED,
                        "evaluation_reasoning": "BLOCKED_BY_CYCLE_OR_UNRESOLVED_PARENT",
                    }
                )

        return states
