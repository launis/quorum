"""Abstract interface for projecting execution results into standardized DTOs."""

import graphlib
from abc import ABC, abstractmethod
from typing import Any

from backend_v2.models.dtos.dag_models import AtomExecutionState, LinkedAtomGraph
from backend_v2.models.dtos.report.atoms import AtomResultDTO, HydratedAtomDTO
from backend_v2.models.dtos.report.metrics import ExecutionMetricsDTO
from backend_v2.models.dtos.report.root import ReportDataDto
from backend_v2.models.enums import SDUIComponentType


class ResultProjector(ABC):
    """Abstract interface responsible for converting atom-level engine results
    to the new ReportDataDto.
    """

    @abstractmethod
    def project(self, engine_output: dict[str, Any]) -> ReportDataDto:
        """Project the raw engine output into a typed ReportDataDto.

        Args:
            engine_output: Raw output dict from the V1 or V2 engine.

        Returns:
            ReportDataDto: The strictly typed projection.
        """
        pass


class EnrichedResultProjector(ResultProjector):
    """Concrete projector for the Enriched Atom Graph.

    Transforms LinkedAtomGraph nodes and their AtomExecutionState results
    into a flat, topologically sorted ReportDataDto with strict referential integrity.
    """

    def project(self, engine_output: dict[str, Any]) -> ReportDataDto:
        """Projects DAG results into ReportDataDto.

        Args:
            engine_output: A dictionary containing:
                - 'execution_id' (str)
                - 'workflow_id' (str)
                - 'nodes' (list[LinkedAtomGraph])
                - 'results' (dict[str, AtomExecutionState]) mapping tda_id to its final state
                - 'global_synthesis' (dict | None) (optional)

        Returns:
            ReportDataDto: The strictly typed projection.
        """
        execution_id = engine_output["execution_id"]
        workflow_id = engine_output["workflow_id"]
        nodes: list[LinkedAtomGraph] = engine_output["nodes"]
        state_results: dict[str, AtomExecutionState] = engine_output["results"]
        global_synthesis = engine_output.get("global_synthesis")

        # 1. Topological Sort of tda_ids
        ts: graphlib.TopologicalSorter[str] = graphlib.TopologicalSorter()
        node_map = {node.atom.tda_id: node for node in nodes}

        for node in nodes:
            parent_ids = [edge.tda_id for edge in node.depends_on]
            ts.add(node.atom.tda_id, *parent_ids)

        sorted_tda_ids = list(ts.static_order())

        # 2. Map Status and Build DTOs
        results: list[AtomResultDTO] = []
        hydrated_references: dict[str, HydratedAtomDTO] = {}

        short_circuited_na_count = 0

        for tda_id in sorted_tda_ids:
            node = node_map[tda_id]
            state = state_results[tda_id]

            if state.status == "N_A" or state.status == "BLOCKED":
                if state.status == "N_A":
                    short_circuited_na_count += 1

            depends_on_tda_ids = [edge.tda_id for edge in node.depends_on]

            atom_result = AtomResultDTO(
                tda_id=tda_id,
                status=state.status,
                extracted_data=None,
                source_quote=node.atom.source_quote,
                contextual_override=False,
                evaluation_reasoning=state.evaluation_reasoning or "Evaluation completed without detailed reasoning.",
                error_details=None,
                depends_on_tda_ids=depends_on_tda_ids,
                short_circuit_reason_tda_ids=state.short_circuit_reason_tda_ids,
            )
            results.append(atom_result)

            hydrated_ref = HydratedAtomDTO(
                sdui_component=SDUIComponentType.BOOLEAN_CARD,
                resolved_claim=node.atom.resolved_claim,
                source_quote=node.atom.source_quote,
            )
            hydrated_references[tda_id] = hydrated_ref

        metrics = ExecutionMetricsDTO(
            total_atoms=len(nodes),
            evaluated=len(nodes) - short_circuited_na_count,
            short_circuited_na=short_circuited_na_count,
            duration_ms=0,
        )

        report_dto = ReportDataDto(
            execution_id=execution_id,
            workflow_id=workflow_id,
            global_metrics=metrics,
            global_synthesis=global_synthesis,
            results=results,
            hydrated_references=hydrated_references,
        )

        return report_dto
