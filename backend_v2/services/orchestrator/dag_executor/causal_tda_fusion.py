"""Leaf Causal-TDA Fusion functions for DAG orchestration.

Provides pure depth-0 leaf functions transforming causal discovery proposition nodes
into immutable FlattenedAtom instances and computing composite CausalTdaFusionResultDTO
analytic outputs.
"""

from __future__ import annotations

from backend_v2.models.domain.matrix import FlattenedAtom
from backend_v2.models.domain.step import ExpectedInput
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.causal_discovery import (
    AntiFluffAuditDTO,
    CausalGraphPayloadDTO,
    CausalNodeDTO,
    CausalTdaFusionResultDTO,
    FairScoringBreakdownDTO,
    PrescriptiveRemediationDTO,
)
from backend_v2.models.enums import ExecutionStatus
from backend_v2.services.orchestrator.causal_cohesion_evaluator import CausalCohesionEvaluator
from backend_v2.settings import get_settings

__all__ = [
    "compute_causal_tda_fusion_result",
    "transform_causal_nodes_to_atoms",
]


# Phase 1, Step 1: Extract leaf causal TDA fusion functions
def transform_causal_nodes_to_atoms(nodes: list[CausalNodeDTO]) -> list[FlattenedAtom]:
    """Transform causal discovery proposition nodes into immutable FlattenedAtom instances.

    Args:
        nodes: List of CausalNodeDTO instances from upstream causal discovery.

    Returns:
        List of strictly typed FlattenedAtom instances for TDA evaluation.
    """
    atoms: list[FlattenedAtom] = []
    for node in nodes:
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


def compute_causal_tda_fusion_result(
    graph: CausalGraphPayloadDTO,
    evaluative_matrices: dict[str, float] | None = None,
    evaluated_atoms: list[AtomResultDTO] | None = None,
    dampening_factor: float | None = None,
    expected_inputs: list[ExpectedInput] | None = None,
) -> CausalTdaFusionResultDTO:
    """Computes composite fusion result executing five stakeholder benefit pipelines.

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
        dampening_factor: Optional penalty dampening factor (defaults to settings value).
        expected_inputs: Optional list of ExpectedInput configurations to induce deliverable subgraph.

    Returns:
        CausalTdaFusionResultDTO combining graph and all five analytical facets.
    """
    # 1. Visual XAI Data Projection: Overlay evaluated statuses/scores
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

    projected_graph = graph.model_copy(update={"nodes": updated_nodes})

    # 2. Root Cause Attribution: Diagnoses cascading failures via Algorithm 1
    root_cause_diagnoses = CausalCohesionEvaluator().diagnose_root_causes(projected_graph)

    # 3. Anti-Fluff Shield: Induce Deliverable Subgraph and evaluate Exogenous Boundary Axiom
    deliverable_keys: set[str] = set()
    if expected_inputs:
        deliverable_keys = {ei.input_key for ei in expected_inputs if ei.is_endorsed_deliverable}
        if not deliverable_keys:
            deliverable_keys = {
                ei.input_key
                for ei in expected_inputs
                if not ei.is_chat_history and not ei.is_assignment and "questionnaire" not in ei.input_modes
            }

    deliverable_nodes: list[CausalNodeDTO]
    if deliverable_keys:
        deliverable_nodes = [n for n in projected_graph.nodes if n.source_input_key in deliverable_keys]
    else:
        deliverable_nodes = list(projected_graph.nodes)

    deliverable_node_ids = {n.node_id for n in deliverable_nodes}

    # Exogenous Boundary Axiom: incoming cross-document edges prevent isolated status
    deliverable_isolated_count = 0
    for node in deliverable_nodes:
        nid = node.node_id
        has_internal_link = any(
            (e.source_id == nid and e.target_id in deliverable_node_ids and e.target_id != nid)
            or (e.target_id == nid and e.source_id in deliverable_node_ids and e.source_id != nid)
            for e in projected_graph.edges
        )
        has_exogenous_support = any(
            e.target_id == nid and e.source_id not in deliverable_node_ids for e in projected_graph.edges
        )
        if not has_internal_link and not has_exogenous_support:
            deliverable_isolated_count += 1

    cycle = projected_graph.cycle_detected
    unsupported_count = sum(1 for n in deliverable_nodes if not n.source_quotes)
    total_deliverable_nodes = len(deliverable_nodes)
    if total_deliverable_nodes == 0:
        cohesion = 1.0
    else:
        connected_ratio = max(0.0, 1.0 - (deliverable_isolated_count / total_deliverable_nodes))
        if cycle:
            connected_ratio *= 0.5
        cohesion = round(connected_ratio, 4)

    anti_fluff_audit = AntiFluffAuditDTO(
        isolated_concept_count=deliverable_isolated_count,
        cycle_detected=cycle,
        unsupported_claims_count=unsupported_count,
        logical_cohesion_score=cohesion,
        detected_hollow_terms=[],
    )

    # 4. Prescriptive Remediation
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

    # 5. Fair Scoring Deduplication
    effective_dampening = get_settings().causal_secondary_fault_dampening
    if dampening_factor is not None:
        effective_dampening = dampening_factor

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

    fair_scoring = FairScoringBreakdownDTO(
        independent_error_count=independent_error_count,
        cascading_fault_count=cascading_fault_count,
        raw_penalty_points=raw_penalty,
        deduplicated_penalty_points=deduplicated_penalty,
        dampened_savings_points=dampened_savings,
    )

    return CausalTdaFusionResultDTO(
        graph=projected_graph,
        root_cause_diagnoses=root_cause_diagnoses,
        anti_fluff_audit=anti_fluff_audit,
        prescriptive_remediations=prescriptive_remediations,
        fair_scoring=fair_scoring,
        total_deliverable_nodes=total_deliverable_nodes,
    )
