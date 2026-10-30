"""Leaf Causal-TDA Fusion functions for DAG orchestration.

Provides pure depth-0 leaf functions transforming causal discovery proposition nodes
into immutable FlattenedAtom instances and computing composite CausalTdaFusionResultDTO
analytic outputs.
"""

from __future__ import annotations

import logging
from collections import deque

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.matrix import FlattenedAtom
from backend_v2.models.domain.step import ExpectedInput
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.causal_discovery import (
    AntiFluffAuditDTO,
    CausalGraphPayloadDTO,
    CausalNodeDTO,
    CausalRootCauseDiagnosisDTO,
    CausalTdaFusionResultDTO,
    FairScoringBreakdownDTO,
    PrescriptiveRemediationDTO,
)
from backend_v2.models.enums import ExecutionStatus
from backend_v2.services.orchestrator.causal_cohesion_evaluator import CausalCohesionEvaluator
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = [
    "compute_causal_tda_fusion_result",
    "transform_causal_nodes_to_atoms",
]


def transform_causal_nodes_to_atoms(nodes: list[CausalNodeDTO]) -> list[FlattenedAtom]:
    """Transform causal discovery proposition nodes into immutable FlattenedAtom instances.

    Args:
        nodes: List of CausalNodeDTO instances from upstream causal discovery.

    Returns:
        List of strictly typed FlattenedAtom instances for TDA evaluation.

    Raises:
        AppException: Triggered with VALIDATION_FAILED if any node has a blank node_id or claim.
    """
    atoms: list[FlattenedAtom] = []
    for node in nodes:
        if not node.node_id.strip() or not node.claim.strip():
            msg = "CausalNodeDTO requires non-blank node_id and claim for TDA atom transformation."
            logger.error(
                "[CausalTdaFusion] %s: %s (node_id=%r)",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                node.node_id,
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=422,
                details={
                    "error_code": ErrorCodes.VALIDATION_FAILED.value,
                    "node_id": node.node_id,
                },
            )
        anchor_target = ""
        if node.paragraph_ref is not None:
            anchor_target = node.paragraph_ref
        extraction_rule = ""
        if node.source_quotes:
            extraction_rule = " [...] ".join(node.source_quotes)
        atoms.append(
            FlattenedAtom(
                atom_id=node.node_id,
                question=node.claim,
                anchor_target=anchor_target,
                extraction_rule=extraction_rule,
                depends_on=(),
                acceptance_criteria=(),
                anti_patterns=(),
                syntactic_anchors=(),
            )
        )
    return atoms


def _compute_largest_component_ratio(
    deliverable_node_ids: set[str],
    graph: CausalGraphPayloadDTO,
) -> float:
    """Compute Largest Weakly Connected Component ratio (r_LCC) on the deliverable subgraph.

    Args:
        deliverable_node_ids: Set of node IDs belonging to the induced deliverable subgraph.
        graph: Projected CausalGraphPayloadDTO containing nodes and edges.

    Returns:
        Fraction of deliverable nodes in the largest weakly connected component in [0.0, 1.0].
    """
    total_deliverable = len(deliverable_node_ids)
    if total_deliverable <= 1:
        return 1.0

    adjacency: dict[str, set[str]] = {nid: set() for nid in deliverable_node_ids}
    for edge in graph.edges:
        if (
            edge.source_id in deliverable_node_ids
            and edge.target_id in deliverable_node_ids
            and edge.source_id != edge.target_id
        ):
            adjacency[edge.source_id].add(edge.target_id)
            adjacency[edge.target_id].add(edge.source_id)

    visited: set[str] = set()
    max_component_size = 0
    for start_id in deliverable_node_ids:
        if start_id in visited:
            continue
        comp_size = 0
        queue: deque[str] = deque([start_id])
        visited.add(start_id)
        while queue:
            curr = queue.popleft()
            comp_size += 1
            for neighbor in adjacency[curr]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        if comp_size > max_component_size:
            max_component_size = comp_size

    return round(max_component_size / total_deliverable, 4)


def _resolve_deliverable_nodes(
    projected_graph: CausalGraphPayloadDTO,
    expected_inputs: list[ExpectedInput] | None,
) -> list[CausalNodeDTO]:
    """Filter projected graph nodes belonging to the induced deliverable subgraph.

    Args:
        projected_graph: CausalGraphPayloadDTO with overlaid TDA evaluation statuses.
        expected_inputs: Optional ExpectedInput definitions classifying deliverable inputs.

    Returns:
        List of CausalNodeDTO instances belonging to the deliverable subgraph.
    """
    deliverable_keys: set[str] = set()
    if expected_inputs:
        deliverable_keys = {ei.input_key for ei in expected_inputs if ei.is_endorsed_deliverable}
        if not deliverable_keys:
            deliverable_keys = {
                ei.input_key
                for ei in expected_inputs
                if not ei.is_chat_history and not ei.is_assignment and "questionnaire" not in ei.input_modes
            }

    if deliverable_keys:
        return [n for n in projected_graph.nodes if n.source_input_key in deliverable_keys]
    return list(projected_graph.nodes)


def _resolve_dialogue_node_ids(
    projected_graph: CausalGraphPayloadDTO,
    expected_inputs: list[ExpectedInput] | None,
    deliverable_node_ids: set[str],
) -> set[str]:
    """Resolve the set of node IDs originating from dialogue history inputs.

    Args:
        projected_graph: CausalGraphPayloadDTO with overlaid TDA evaluation statuses.
        expected_inputs: Optional ExpectedInput definitions classifying dialogue inputs.
        deliverable_node_ids: Set of node IDs belonging to the induced deliverable subgraph.

    Returns:
        Set of node IDs belonging to dialogue inputs.
    """
    dialogue_keys: set[str] = set()
    if expected_inputs:
        dialogue_keys = {ei.input_key for ei in expected_inputs if ei.is_chat_history}
    if dialogue_keys:
        return {n.node_id for n in projected_graph.nodes if n.source_input_key in dialogue_keys}
    return {n.node_id for n in projected_graph.nodes if n.node_id not in deliverable_node_ids}


def _compute_anti_fluff_audit(
    projected_graph: CausalGraphPayloadDTO,
    expected_inputs: list[ExpectedInput] | None,
) -> tuple[AntiFluffAuditDTO, int]:
    """Compute 0-token topological AntiFluffAuditDTO metrics over the induced deliverable subgraph.

    Args:
        projected_graph: CausalGraphPayloadDTO with overlaid TDA evaluation statuses.
        expected_inputs: Optional ExpectedInput definitions classifying deliverable and dialogue inputs.

    Returns:
        2-tuple of (AntiFluffAuditDTO, total_deliverable_nodes).
    """
    deliverable_nodes = _resolve_deliverable_nodes(projected_graph, expected_inputs)
    deliverable_node_ids = {n.node_id for n in deliverable_nodes}
    dialogue_node_ids = _resolve_dialogue_node_ids(projected_graph, expected_inputs, deliverable_node_ids)

    deliverable_isolated_count = 0
    convergent_count = 0
    deliverable_root_ids: list[str] = []

    for node in deliverable_nodes:
        nid = node.node_id
        internal_parents = {
            e.source_id
            for e in projected_graph.edges
            if e.target_id == nid and e.source_id in deliverable_node_ids and e.source_id != nid
        }
        internal_children = {
            e.target_id
            for e in projected_graph.edges
            if e.source_id == nid and e.target_id in deliverable_node_ids and e.target_id != nid
        }
        exogenous_parents = {
            e.source_id for e in projected_graph.edges if e.target_id == nid and e.source_id not in deliverable_node_ids
        }
        all_incoming_parents = internal_parents | exogenous_parents
        if len(all_incoming_parents) >= 2:
            convergent_count += 1
        if not internal_parents:
            deliverable_root_ids.append(nid)
        if not internal_parents and not internal_children and not exogenous_parents:
            deliverable_isolated_count += 1

    cycle = projected_graph.cycle_detected
    unsupported_count = sum(1 for n in deliverable_nodes if not n.source_quotes)
    total_deliverable_nodes = len(deliverable_nodes)
    if total_deliverable_nodes == 0:
        cohesion = 1.0
        lcc_ratio = 1.0
        conv_ratio = 0.0
    else:
        connected_ratio = max(0.0, 1.0 - (deliverable_isolated_count / total_deliverable_nodes))
        if cycle:
            connected_ratio *= 0.5
        cohesion = round(connected_ratio, 4)
        lcc_ratio = _compute_largest_component_ratio(deliverable_node_ids, projected_graph)
        conv_ratio = round(convergent_count / total_deliverable_nodes, 4)

    if not deliverable_root_ids:
        steering_ratio = 0.0
    else:
        steered_roots = sum(
            1
            for root_id in deliverable_root_ids
            if any(e.target_id == root_id and e.source_id in dialogue_node_ids for e in projected_graph.edges)
        )
        steering_ratio = round(steered_roots / len(deliverable_root_ids), 4)

    audit = AntiFluffAuditDTO(
        isolated_concept_count=deliverable_isolated_count,
        cycle_detected=cycle,
        unsupported_claims_count=unsupported_count,
        logical_cohesion_score=cohesion,
        largest_component_ratio=lcc_ratio,
        branch_convergence_ratio=conv_ratio,
        steering_coupling_ratio=steering_ratio,
        detected_hollow_terms=[],
    )
    return audit, total_deliverable_nodes


def _project_evaluated_atoms_onto_graph(
    graph: CausalGraphPayloadDTO,
    evaluative_matrices: dict[str, float] | None,
    evaluated_atoms: list[AtomResultDTO] | None,
) -> CausalGraphPayloadDTO:
    """Overlay evaluated TDA atom statuses and scores onto the causal graph nodes.

    Args:
        graph: Upstream CausalGraphPayloadDTO discovered from source propositions.
        evaluative_matrices: Optional mapping of matrix IDs to evaluated scores.
        evaluated_atoms: Optional list of evaluated AtomResultDTO instances.

    Returns:
        Projected CausalGraphPayloadDTO with updated node statuses and scores.
    """
    updated_nodes: list[CausalNodeDTO] = []
    atom_by_id: dict[str, AtomResultDTO] = {}
    if evaluated_atoms is not None:
        for atom in evaluated_atoms:
            atom_by_id[atom.tda_id] = atom

    for node in graph.nodes:
        if node.node_id in atom_by_id:
            atom = atom_by_id[node.node_id]
            node_status = ExecutionStatus.FAILED
            if atom.status == ExecutionStatus.PASSED:
                node_status = ExecutionStatus.PASSED
            score_val = node.tda_score
            if evaluative_matrices and atom.matrix_id and atom.matrix_id in evaluative_matrices:
                score_val = evaluative_matrices[atom.matrix_id]
            elif atom.extracted_data and isinstance(atom.extracted_data.value, (int, float)):
                score_val = float(atom.extracted_data.value)

            updated_nodes.append(
                node.model_copy(
                    update={
                        "status": node_status,
                        "tda_score": score_val,
                    }
                )
            )
        else:
            updated_nodes.append(node)

    return graph.model_copy(update={"nodes": updated_nodes})


def _build_prescriptive_remediations(projected_graph: CausalGraphPayloadDTO) -> list[PrescriptiveRemediationDTO]:
    """Identify unlock paths and score impact for root cause failure nodes.

    Args:
        projected_graph: CausalGraphPayloadDTO with overlaid TDA evaluation statuses.

    Returns:
        List of PrescriptiveRemediationDTO instances for root cause nodes with downstream dependents.
    """
    prescriptive_remediations: list[PrescriptiveRemediationDTO] = []
    node_by_id = {n.node_id: n for n in projected_graph.nodes}
    for root_id in projected_graph.root_cause_node_ids:
        root_node = None
        if root_id in node_by_id:
            root_node = node_by_id[root_id]
        dependent_children: set[str] = set()
        if root_node is not None:
            dependent_children = set(root_node.dependent_child_ids)
        blaming_nodes = {n.node_id for n in projected_graph.nodes if root_id in n.blame_parent_ids}
        unlocked = sorted(list((dependent_children | blaming_nodes) - {root_id}))
        if unlocked:
            prescriptive_remediations.append(
                PrescriptiveRemediationDTO(
                    target_node_id=root_id,
                    required_action=(
                        f"Remediate foundational claim in node '{root_id}' to restore downstream validity."
                    ),
                    unlocks_node_ids=unlocked,
                    potential_score_impact=float(len(unlocked) + 1),
                )
            )
    return prescriptive_remediations


def _compute_fair_scoring_breakdown(
    projected_graph: CausalGraphPayloadDTO,
    root_cause_diagnoses: list[CausalRootCauseDiagnosisDTO],
    effective_dampening: float,
) -> FairScoringBreakdownDTO:
    """Compute fair scoring breakdown deduplicating cascading faults with dampening.

    Args:
        projected_graph: CausalGraphPayloadDTO with overlaid TDA evaluation statuses.
        root_cause_diagnoses: Diagnosed cascading failure attributions.
        effective_dampening: Secondary fault dampening factor in [0.0, 1.0].

    Returns:
        Validated FairScoringBreakdownDTO satisfying the scoring identity.
    """
    failing_nodes = [
        n
        for n in projected_graph.nodes
        if n.status in (ExecutionStatus.FAILED, ExecutionStatus.SYSTEM_ERROR, ExecutionStatus.BLOCKED)
    ]
    if not failing_nodes and (projected_graph.root_cause_node_ids or root_cause_diagnoses):
        cascading_fault_count = len({d.failing_node_id for d in root_cause_diagnoses})
        independent_error_count = len(projected_graph.root_cause_node_ids)
    else:
        cascading_fault_count = sum(1 for n in failing_nodes if n.blame_parent_ids)
        independent_error_count = sum(1 for n in failing_nodes if not n.blame_parent_ids)

    raw_penalty = float(independent_error_count + cascading_fault_count) * 1.0
    dampened_savings = round(float(cascading_fault_count) * 1.0 * effective_dampening, 4)
    deduplicated_penalty = round(raw_penalty - dampened_savings, 4)

    return FairScoringBreakdownDTO(
        independent_error_count=independent_error_count,
        cascading_fault_count=cascading_fault_count,
        raw_penalty_points=raw_penalty,
        deduplicated_penalty_points=deduplicated_penalty,
        dampened_savings_points=dampened_savings,
    )


def compute_causal_tda_fusion_result(
    graph: CausalGraphPayloadDTO,
    evaluative_matrices: dict[str, float] | None = None,
    evaluated_atoms: list[AtomResultDTO] | None = None,
    dampening_factor: float | None = None,
    expected_inputs: list[ExpectedInput] | None = None,
) -> CausalTdaFusionResultDTO:
    """Compute composite fusion result executing five stakeholder benefit pipelines.

    Executes:
    1. Root Cause Attribution: Diagnoses cascading failures via blame_parent_ids.
    2. Anti-Fluff Shield: Quantifies isolated concepts, unsupported claims, and logical cohesion.
    3. Prescriptive Remediation: Identifies unlock paths for root cause failure nodes.
    4. Visual XAI Data Projection: Overlays evaluated statuses and scores on graph nodes.
    5. Fair Scoring Deduplication: Deduplicates cascading penalties with power-curve dampening.

    Args:
        graph: Causal graph payload discovered from source propositions.
        evaluative_matrices: Optional mapping of matrix IDs to evaluated scores.
        evaluated_atoms: Optional list of evaluated AtomResultDTO instances.
        dampening_factor: Optional penalty dampening factor in [0.0, 1.0] (defaults to settings value).
        expected_inputs: Optional list of ExpectedInput configurations to induce deliverable subgraph.

    Returns:
        CausalTdaFusionResultDTO combining graph and all five analytical facets.

    Raises:
        AppException: Triggered with VALIDATION_FAILED if dampening_factor is outside [0.0, 1.0].
    """
    effective_dampening = get_settings().causal_secondary_fault_dampening
    if dampening_factor is not None:
        if not 0.0 <= dampening_factor <= 1.0:
            msg = f"dampening_factor must reside within [0.0, 1.0], got {dampening_factor}."
            logger.error(
                "[CausalTdaFusion] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=422,
                details={
                    "error_code": ErrorCodes.VALIDATION_FAILED.value,
                    "dampening_factor": dampening_factor,
                },
            )
        effective_dampening = dampening_factor

    projected_graph = _project_evaluated_atoms_onto_graph(
        graph=graph,
        evaluative_matrices=evaluative_matrices,
        evaluated_atoms=evaluated_atoms,
    )
    root_cause_diagnoses = CausalCohesionEvaluator().diagnose_root_causes(projected_graph)
    anti_fluff_audit, total_deliverable_nodes = _compute_anti_fluff_audit(
        projected_graph=projected_graph,
        expected_inputs=expected_inputs,
    )
    prescriptive_remediations = _build_prescriptive_remediations(projected_graph)
    fair_scoring = _compute_fair_scoring_breakdown(
        projected_graph=projected_graph,
        root_cause_diagnoses=root_cause_diagnoses,
        effective_dampening=effective_dampening,
    )

    return CausalTdaFusionResultDTO(
        graph=projected_graph,
        root_cause_diagnoses=root_cause_diagnoses,
        anti_fluff_audit=anti_fluff_audit,
        prescriptive_remediations=prescriptive_remediations,
        fair_scoring=fair_scoring,
        total_deliverable_nodes=total_deliverable_nodes,
    )
