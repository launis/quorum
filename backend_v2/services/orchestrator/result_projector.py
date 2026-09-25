"""Result Projector for DAG execution.

Projects the Enriched Atom Graph and execution states into the strict V2 DTO format
required by the frontend (AtomResultDTO and HydratedAtomDTO) and aggregates matrix
results into MatrixProjectionResultDTO.
"""

from __future__ import annotations

import logging

from pydantic import JsonValue

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.dtos.atom_result import AtomResultDTO, ErrorDetailsDTO, HydratedAtomDTO
from backend_v2.models.dtos.dag_models import AtomExecutionState, LinkedAtomGraph
from backend_v2.models.dtos.hook_delta import (
    MatrixProjectionResultDTO,
    MissingContextDTO,
    ProjectedResultsDTO,
)
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.enums import ExecutionStatus, SDUIComponentType, XaiExtensionType

__all__ = ["ResultProjector"]

logger = logging.getLogger(__name__)


class ResultProjector:
    """Projects internal DAG state into presentation DTOs."""

    @staticmethod
    def project(
        nodes: list[LinkedAtomGraph], states: dict[str, AtomExecutionState], matrix_id: str | None = None
    ) -> ProjectedResultsDTO:
        """Project execution state to frontend DTOs.

        Args:
            nodes: The topological list of atom graphs.
            states: The dictionary of execution states keyed by tda_id.
            matrix_id: Optional parent matrix ID for scoping the projected results.

        Returns:
            ProjectedResultsDTO encapsulating results list and hydrated_references dict.

        Raises:
            AppException: ErrorCodes.VALIDATION_FAILED if a node has PASSED or FAILED
                status but lacks mandatory evaluation_reasoning.
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
            state = None
            if tda_id in states:
                state = states[tda_id]

            if state is not None:
                status = state.status
                reasoning = state.evaluation_reasoning
                short_circuit = state.short_circuit_reason_tda_ids
                extensions = state.extensions
            else:
                status = ExecutionStatus.PENDING
                reasoning = "Pending evaluation."
                short_circuit = []
                extensions = {}

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
                msg = f"Node {tda_id} has status {status.value} but lacks mandatory evaluation_reasoning."
                logger.error(
                    "[ResultProjector] %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    msg,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
                raise AppException(
                    message=msg,
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

            # Resolve quote and contextual_override according to status and cognitive strictness
            quote_val = None
            if state is not None and state.source_quote and state.source_quote.strip():
                quote_val = state.source_quote.strip()
            elif node.atom.source_quote and node.atom.source_quote.strip():
                quote_val = node.atom.source_quote.strip()

            if status == ExecutionStatus.FAILED:
                source_quote_for_dto = None
                contextual_override = False
                is_inverse_evidence = False
            elif status == ExecutionStatus.PASSED:
                if quote_val:
                    source_quote_for_dto = quote_val
                    contextual_override = False
                    is_inverse_evidence = False
                elif node.atom.is_inverse:
                    source_quote_for_dto = None
                    contextual_override = False
                    is_inverse_evidence = True
                else:
                    source_quote_for_dto = None
                    contextual_override = True
                    is_inverse_evidence = False
            else:
                source_quote_for_dto = quote_val
                contextual_override = node.atom.is_logical_deduction
                is_inverse_evidence = False

            res = AtomResultDTO(
                tda_id=tda_id,
                matrix_id=matrix_id,
                status=status,
                extracted_data=None,
                source_quote=source_quote_for_dto,
                contextual_override=contextual_override,
                is_inverse_evidence=is_inverse_evidence,
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
                source_quote=source_quote_for_dto,
            )

        return ProjectedResultsDTO(results=results, hydrated_references=hydrated_references)

    @staticmethod
    def project_matrix_results(
        nodes: list[LinkedAtomGraph],
        states: dict[str, AtomExecutionState],
        matrix_id: str,
        matrix_block: MatrixPromptBlock,
        raw_score: float = 0.0,
        justification: str = "",
    ) -> MatrixProjectionResultDTO:
        """Project atom states to domain matrix results and missing context.

        Args:
            nodes: The topological list of atom graphs.
            states: The dictionary of execution states keyed by tda_id.
            matrix_id: Identifier of the matrix prompt block.
            matrix_block: Domain model of the matrix block with scale definitions.
            raw_score: Preliminary or computed unnormalized score.
            justification: Clean domain justification string.

        Returns:
            MatrixProjectionResultDTO with projected results, LightweightMatrixOutput, and MissingContextDTO.
        """
        projected = ResultProjector.project(nodes, states, matrix_id=matrix_id)

        evaluated_atoms: dict[str, ExecutionStatus] = {}
        extensions_by_type: dict[str, list[str]] = {}
        missing_atoms: list[str] = []

        atom_results_map = {r.tda_id: r for r in projected.results}

        for scale in matrix_block.scales:
            for claim in scale.claims:
                if claim.tda_assertions is None:
                    continue
                for tda in claim.tda_assertions:
                    aid = str(tda.tda_id)
                    if aid in atom_results_map:
                        res = atom_results_map[aid]
                        evaluated_atoms[aid] = res.status
                        if res.status == ExecutionStatus.FAILED:
                            missing_atoms.append(tda.concept_description)
                        elif res.status == ExecutionStatus.SYSTEM_ERROR:
                            missing_atoms.append(f"{tda.concept_description} (DLQ - Unscorable)")

                        if res.extensions:
                            for ext_k, ext_v in res.extensions.items():
                                ext_str = ext_k if isinstance(ext_k, str) else str(ext_k)
                                if ext_v:
                                    if ext_str not in extensions_by_type:
                                        extensions_by_type[ext_str] = []
                                    extensions_by_type[ext_str].append(str(ext_v))
                    else:
                        evaluated_atoms[aid] = ExecutionStatus.PENDING
                        missing_atoms.append(tda.concept_description)

        final_extensions: dict[XaiExtensionType, JsonValue] = {
            XaiExtensionType(k): "\n\n".join(v)
            for k, v in extensions_by_type.items()
            if k in {e.value for e in XaiExtensionType}
        }

        matrix_output = LightweightMatrixOutput(
            raw_score=raw_score,
            normalized_score=None,
            level_breakdown=None,
            justification=justification,
            evaluated_atoms=evaluated_atoms,
            extensions=final_extensions,
        )

        missing_context = None
        if missing_atoms:
            missing_context = MissingContextDTO(
                missing_atoms=missing_atoms,
                missing_context_text="\n".join(missing_atoms),
            )

        return MatrixProjectionResultDTO(
            results=projected.results,
            matrix_output=matrix_output,
            missing_context=missing_context,
        )
