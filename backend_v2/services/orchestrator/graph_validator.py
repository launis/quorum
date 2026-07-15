"""Graph Validator Service.

Performs deterministic topological checks (phantom edge detection and cycle breaking)
before executing the DAG.
"""

import asyncio

import networkx as nx

from backend_v2.models.dtos.dag_models import AtomExecutionState, LinkedAtomGraph
from backend_v2.models.enums import ExecutionStatus


class GraphValidatorService:
    """Service to validate the causal topology of a LinkedAtomGraph."""

    @staticmethod
    async def validate(graphs: list[LinkedAtomGraph]) -> dict[str, AtomExecutionState]:
        """Validate the graph for phantom edges and cyclic dependencies.

        Nodes with invalid topology are deterministically isolated into SYSTEM_ERROR,
        preventing infinite loops or crashes during execution.

        Args:
            graphs: List of LinkedAtomGraphs representing the DAG.

        Returns:
            A dictionary mapping tda_id to its initial AtomExecutionState.
            Valid nodes start as PENDING. Invalid nodes start as SYSTEM_ERROR.
        """
        states: dict[str, AtomExecutionState] = {}
        valid_tda_ids = {g.atom.tda_id for g in graphs}

        # Initialize networkx directed graph
        # A depends on B -> B is parent, A is child -> Edge B -> A
        dg = nx.DiGraph()

        for g in graphs:
            states[g.atom.tda_id] = AtomExecutionState(
                tda_id=g.atom.tda_id,
                status=ExecutionStatus.PENDING,
            )
            dg.add_node(g.atom.tda_id)

        # 1. Phantom Edge Isolation
        for g in graphs:
            has_phantom = False
            for edge in g.depends_on:
                if edge.tda_id not in valid_tda_ids:
                    has_phantom = True
                else:
                    dg.add_edge(edge.tda_id, g.atom.tda_id)

            if has_phantom:
                states[g.atom.tda_id] = AtomExecutionState(
                    tda_id=g.atom.tda_id,
                    status=ExecutionStatus.SYSTEM_ERROR,
                    evaluation_reasoning="UNRESOLVED_DEPENDENCY: Phantom edge detected.",
                )

        # 2. Deterministic Cycle Isolation
        def get_cycles() -> list[list[str]]:
            """Detect all simple cycles in the directed graph.

            Returns:
                A list of cycles, where each cycle is a list of node IDs.
            """
            return list(nx.simple_cycles(dg))

        # Offload to thread to prevent blocking the async event loop for large graphs
        cycles = await asyncio.to_thread(get_cycles)

        for cycle in cycles:
            for node in cycle:
                states[node] = AtomExecutionState(
                    tda_id=node,
                    status=ExecutionStatus.SYSTEM_ERROR,
                    evaluation_reasoning="CYCLIC_DEPENDENCY_DETECTED: Node participates in a causal cycle.",
                )

        return states
