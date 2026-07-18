"""Result Projector for DAG execution.

Projects the Enriched Atom Graph and execution states into the strict V2 DTO format
required by the frontend (AtomResultDTO and HydratedAtomDTO).
"""

import logging

from backend_v2.exceptions import AppException
from backend_v2.models.dtos.dag_models import AtomExecutionState, LinkedAtomGraph
from backend_v2.models.enums import ExecutionStatus, SDUIComponentType
from backend_v2.models.v2_core import AtomResultDTO, ErrorDetailsDTO, HydratedAtomDTO

logger = logging.getLogger(__name__)


class ResultProjector:
    """Projects internal DAG state into presentation DTOs.

    Attributes:
        None
    """

    @staticmethod
    def project(
        nodes: list[LinkedAtomGraph], states: dict[str, AtomExecutionState]
    ) -> tuple[list[AtomResultDTO], dict[str, HydratedAtomDTO]]:
        """Project execution state to frontend DTOs.

        Args:
            nodes: The topological list of atom graphs.
            states: The dictionary of execution states keyed by tda_id.

        Returns:
            A tuple of (results list, hydrated_references dict).

        Raises:
            AppException: If a node has a PASSED or FAILED status but is missing mandatory reasoning.
        """
        results: list[AtomResultDTO] = []
        hydrated_references: dict[str, HydratedAtomDTO] = {}

        # 1. Topological Sort (Kahn's algorithm)
        graph: dict[str, list[str]] = {}
        in_degree: dict[str, int] = {}
        node_map = {n.atom.tda_id: n for n in nodes}

        for n in nodes:
            tda_id = n.atom.tda_id
            if tda_id not in graph:
                graph[tda_id] = []
            if tda_id not in in_degree:
                in_degree[tda_id] = 0

            for edge in n.depends_on:
                parent_id = edge.tda_id
                if parent_id not in graph:
                    graph[parent_id] = []
                if parent_id not in in_degree:
                    in_degree[parent_id] = 0
                graph[parent_id].append(tda_id)
                in_degree[tda_id] += 1

        queue = [nid for nid in in_degree if in_degree[nid] == 0]
        sorted_ids: list[str] = []
        while queue:
            current = queue.pop(0)
            sorted_ids.append(current)
            for child in graph[current]:
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        # Append any missing nodes
        missing = set(node_map.keys()) - set(sorted_ids)
        sorted_ids.extend(list(missing))

        # 2. Build DTOs
        for tda_id in sorted_ids:
            if tda_id not in node_map:
                continue

            node = node_map[tda_id]
            state = states.get(tda_id)

            status = state.status if state else ExecutionStatus.PENDING
            reasoning = state.evaluation_reasoning if state else "Pending evaluation."
            short_circuit = state.short_circuit_reason_tda_ids if state else []
            extensions = state.extensions if state else {}

            error_details = None
            if status == ExecutionStatus.SYSTEM_ERROR:
                error_details = ErrorDetailsDTO(
                    error_code="DAG_EXECUTION_ERROR", message="An error occurred during topological evaluation."
                )

            sdui_component = SDUIComponentType.BOOLEAN_CARD
            if status == ExecutionStatus.SYSTEM_ERROR:
                sdui_component = SDUIComponentType.ERROR_CARD
            elif status == ExecutionStatus.N_A:
                sdui_component = SDUIComponentType.N_A_CARD

            # For PASSED/FAILED, reasoning is mandatory. Make sure we never pass None.
            if status in (ExecutionStatus.PASSED, ExecutionStatus.FAILED) and not reasoning:
                raise AppException(
                    message=f"Node {tda_id} has status {status.value} but lacks mandatory evaluation_reasoning.",
                    details={"error_code": "MISSING_EVALUATION_REASONING"},
                )

            res = AtomResultDTO(
                tda_id=tda_id,
                status=status,
                extracted_data=None,
                source_quote=node.atom.source_quote,
                contextual_override=node.atom.is_logical_deduction,
                evaluation_reasoning=reasoning,
                extensions=extensions,
                error_details=error_details,
                depends_on_tda_ids=[e.tda_id for e in node.depends_on],
                short_circuit_reason_tda_ids=short_circuit,
            )
            results.append(res)

            hydrated_references[tda_id] = HydratedAtomDTO(
                sdui_component=sdui_component,
                resolved_claim=node.atom.resolved_claim,
                source_quote=node.atom.source_quote,
            )

        return results, hydrated_references
