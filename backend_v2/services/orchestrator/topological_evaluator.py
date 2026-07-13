"""Topological Evaluator.

Executes a Directed Acyclic Graph (DAG) of Enriched Atoms using a
TaskGroup-based asynchronous cascade, preventing deadlocks and enforcing
deterministic short-circuit logic for unmet dependencies.
"""

import asyncio
from collections.abc import Awaitable, Callable

import networkx as nx

from backend_v2.models.dtos.dag_models import AtomExecutionState, LinkedAtomGraph
from backend_v2.models.enums import ExecutionStatus


class TopologicalEvaluator:
    """Evaluates a DAG of LinkedAtomGraphs deterministically.

    Attributes:
        None
    """

    async def evaluate_graph(
        self,
        nodes: list[LinkedAtomGraph],
        evaluation_callback: Callable[[LinkedAtomGraph], Awaitable[ExecutionStatus]],
    ) -> dict[str, AtomExecutionState]:
        """Evaluates a graph of atoms deterministically.

        Args:
            nodes: The list of atom graph nodes to evaluate.
            evaluation_callback: An asynchronous callback that evaluates a single node
                and returns its ExecutionStatus (PASSED, FAILED, etc.). This is only
                called if the node is not short-circuited or blocked by its parents.

        Returns:
            A dictionary mapping tda_id to its final AtomExecutionState.
        """
        states: dict[str, AtomExecutionState] = {}
        events: dict[str, asyncio.Event] = {}
        node_map: dict[str, LinkedAtomGraph] = {n.atom.tda_id: n for n in nodes}

        # Initialize states and events
        for node in nodes:
            states[node.atom.tda_id] = AtomExecutionState(
                tda_id=node.atom.tda_id,
                status=ExecutionStatus.PENDING,
            )
            events[node.atom.tda_id] = asyncio.Event()

        # Step 1: Structural Integrity (Phantom Edges & Cycles)
        g = nx.DiGraph()

        for node in nodes:
            g.add_node(node.atom.tda_id)
            for edge in node.depends_on:
                if edge.tda_id not in node_map:
                    # Phantom edge detected: Isolate child node immediately
                    states[node.atom.tda_id] = states[node.atom.tda_id].model_copy(
                        update={
                            "status": ExecutionStatus.SYSTEM_ERROR,
                            "evaluation_reasoning": "UNRESOLVED_DEPENDENCY",
                        }
                    )
                    events[node.atom.tda_id].set()
                else:
                    # Directed edge from Parent -> Child
                    g.add_edge(edge.tda_id, node.atom.tda_id)

        # Detect cycles in thread pool to prevent Event Loop freezing
        cycles = await asyncio.to_thread(list, nx.simple_cycles(g))
        if cycles:
            for cycle in cycles:
                for node_id in cycle:
                    # Isolate cycle nodes
                    if states[node_id].status != ExecutionStatus.SYSTEM_ERROR:
                        states[node_id] = states[node_id].model_copy(
                            update={
                                "status": ExecutionStatus.SYSTEM_ERROR,
                                "evaluation_reasoning": "CYCLIC_DEPENDENCY_DETECTED",
                            }
                        )
                        events[node_id].set()

        # Step 2: TaskGroup Execution
        async def evaluate_node(node_id: str) -> None:
            """Evaluates a single node following priority cascade rules.

            Args:
                node_id: The TDA ID of the node to evaluate.
            """
            try:
                # If already resolved (phantom/cycle), short-circuit
                if events[node_id].is_set():
                    return

                node = node_map[node_id]

                # Wait for all parents deterministically
                for edge in node.depends_on:
                    if edge.tda_id in events:
                        await events[edge.tda_id].wait()

                # Re-check state just in case it was mutated
                if states[node_id].status != ExecutionStatus.PENDING:
                    return

                # Evaluate dependencies (Priority Matrix)
                is_blocked = False
                short_circuit_reasons: list[str] = []

                for edge in node.depends_on:
                    parent_state = states.get(edge.tda_id)
                    if not parent_state:
                        continue

                    if parent_state.status in (ExecutionStatus.SYSTEM_ERROR, ExecutionStatus.BLOCKED):
                        is_blocked = True
                        break

                    if parent_state.status != edge.expected_status:
                        short_circuit_reasons.append(edge.tda_id)

                if is_blocked:
                    states[node_id] = states[node_id].model_copy(update={"status": ExecutionStatus.BLOCKED})
                    return

                if short_circuit_reasons:
                    states[node_id] = states[node_id].model_copy(
                        update={
                            "status": ExecutionStatus.N_A,
                            "short_circuit_reason_tda_ids": short_circuit_reasons,
                        }
                    )
                    return

                # Perform actual evaluation
                try:
                    result_status = await evaluation_callback(node)
                    states[node_id] = states[node_id].model_copy(update={"status": result_status})
                except Exception as e:
                    states[node_id] = states[node_id].model_copy(
                        update={
                            "status": ExecutionStatus.SYSTEM_ERROR,
                            "evaluation_reasoning": f"EVALUATION_CRASH: {str(e)}",
                        }
                    )

            except Exception:
                # Catch-all DLQ equivalent for node to prevent TaskGroup failure
                states[node_id] = states[node_id].model_copy(
                    update={
                        "status": ExecutionStatus.SYSTEM_ERROR,
                        "evaluation_reasoning": "UNHANDLED_NODE_EXCEPTION",
                    }
                )
            finally:
                # Critical safety net: Always set the event to unlock children
                events[node_id].set()

        async with asyncio.TaskGroup() as tg:
            for node in nodes:
                if not events[node.atom.tda_id].is_set():
                    tg.create_task(evaluate_node(node.atom.tda_id))

        return states
