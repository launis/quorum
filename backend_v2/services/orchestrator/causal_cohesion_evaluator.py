"""Pure stateless service for evaluating causal reasoning and argument cohesion BARS matrix.

Evaluates argument structural integrity, inferential cohesion, cycle avoidance,
and isolated claim absence from AntiFluffAuditDTO topological graph telemetry into
a deterministic BARS 1-5 scale and unified competence score.
"""

from __future__ import annotations

import logging
from collections import deque
from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase, generate_opaque_id
from backend_v2.models.domain.prompt_blocks import AnyPromptBlock, MatrixPromptBlock
from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
from backend_v2.models.dtos.causal_discovery import (
    AntiFluffAuditDTO,
    CausalEdgeDTO,
    CausalGraphPayloadDTO,
    CausalRootCauseDiagnosisDTO,
    CounterfactualSimulationResultDTO,
)
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO, ScoringResultDTO
from backend_v2.models.dtos.trace import TraceMatrixPayloadDTO
from backend_v2.models.enums import CausalRootCauseType, EntityPrefix, ExecutionStatus, SDUIComponentType
from backend_v2.settings import get_settings
from backend_v2.utils.scoring.unified_engine import UnifiedScoringEngine

logger = logging.getLogger(__name__)

__all__ = [
    "CausalCohesionEvaluationDTO",
    "CausalCohesionEvaluator",
]


class CausalCohesionEvaluationDTO(V2CoreBase):
    """Typed evaluation result for the causal cohesion BARS matrix.

    Attributes:
        matrix_block_id: Opaque Stripe ID of the matrix.
        atom_results: Atoms evaluated for BARS Levels 1-5.
        level_stats: Level statistics mapping scale level string to LevelStatsDTO.
        score_result: Unified score calculation result.
        hydrated_references: Hydrated atom references for BARS levels.
        matrix_output: Matrix scorecard payload for domain parsing.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    matrix_block_id: Annotated[str, Field(description="Opaque Stripe ID of the matrix.")]
    atom_results: Annotated[list[AtomResultDTO], Field(description="Atoms for Levels 1-5.")]
    level_stats: Annotated[dict[str, LevelStatsDTO], Field(description="Level statistics.")]
    score_result: Annotated[ScoringResultDTO, Field(description="Unified score calculation.")]
    hydrated_references: Annotated[
        dict[str, HydratedAtomDTO],
        Field(description="Hydrated atom references for BARS levels."),
    ]
    matrix_output: Annotated[
        TraceMatrixPayloadDTO,
        Field(description="Matrix scorecard payload for domain parsing."),
    ]


class CausalCohesionEvaluator:
    """Pure, stateless evaluator for argument causal cohesion BARS matrix.

    Attributes:
        _scoring_engine: UnifiedScoringEngine instance used for score calculations.
    """

    def __init__(self, scoring_engine: UnifiedScoringEngine | None = None) -> None:
        """Initialize the causal cohesion evaluator.

        Args:
            scoring_engine: Optional UnifiedScoringEngine instance.
        """
        self._scoring_engine = scoring_engine or UnifiedScoringEngine()

    def diagnose_root_causes(
        self,
        graph: CausalGraphPayloadDTO,
    ) -> list[CausalRootCauseDiagnosisDTO]:
        """Diagnose root cause faults attributing node failures vs warrant grounding failures (Algorithm 1).

        Separates independent node intrinsic failures (RC_node) from inferential warrant/edge
        grounding failures (RC_edge). When a parent premise is valid (PASSED) but the child is failed,
        or the edge key is explicitly registered in edge_root_causes, the fault is attributed as
        WARRANT_GROUNDING_FAILURE. Otherwise, cascading failures are attributed as NODE_FAILURE.

        Args:
            graph: CausalGraphPayloadDTO containing argument nodes, edges, and edge root causes.

        Returns:
            List of CausalRootCauseDiagnosisDTO entries with typed root_cause_type.
        """
        diagnoses: list[CausalRootCauseDiagnosisDTO] = []
        node_map = {n.node_id: n for n in graph.nodes}
        edge_map = {(e.source_id, e.target_id): e for e in graph.edges}
        edge_failures = set(graph.edge_root_causes)

        for node in graph.nodes:
            if node.blame_parent_ids:
                paragraph_ref = ""
                if node.paragraph_ref is not None:
                    paragraph_ref = node.paragraph_ref

                for parent_id in node.blame_parent_ids:
                    edge_key = f"{parent_id}->{node.node_id}"
                    parent_is_passed = False
                    if parent_id in node_map:
                        parent_node = node_map[parent_id]
                        if parent_node.status == ExecutionStatus.PASSED:
                            parent_is_passed = True

                    edge: CausalEdgeDTO | None = None
                    if (parent_id, node.node_id) in edge_map:
                        edge = edge_map[(parent_id, node.node_id)]
                    is_warrant_failure = edge_key in edge_failures or parent_is_passed
                    if is_warrant_failure:
                        rc_type = CausalRootCauseType.WARRANT_GROUNDING_FAILURE
                        if edge is not None and edge.warrant_quotes:
                            warrant_text = " [...] ".join(edge.warrant_quotes)
                            explanation = (
                                f"Inferential warrant failure on dependency from '{parent_id}' to '{node.node_id}' "
                                f"(grounding quotes: '{warrant_text}')."
                            )
                        else:
                            explanation = (
                                f"Inferential warrant failure on dependency from '{parent_id}' to '{node.node_id}'."
                            )
                    else:
                        rc_type = CausalRootCauseType.NODE_FAILURE
                        explanation = f"Cascading failure caused by root issue in parent '{parent_id}'."

                    diagnoses.append(
                        CausalRootCauseDiagnosisDTO(
                            failing_node_id=node.node_id,
                            root_cause_parent_id=parent_id,
                            paragraph_ref=paragraph_ref,
                            explanation=explanation,
                            penalty_points=1.0,
                            root_cause_type=rc_type,
                        )
                    )
        return diagnoses

    def evaluate_causal_cohesion(
        self,
        audit: AntiFluffAuditDTO,
        total_nodes: int,
        strictness_level: int,
        matrix_block_id: str,
        bars_claims: dict[str, str] | None = None,
        matrix_block: AnyPromptBlock | None = None,
    ) -> CausalCohesionEvaluationDTO:
        """Evaluate topological causal graph metrics into BARS 1-5 scale levels and unified score.

        Enforces the Cumulative Guttman Invariant (Level k requires Level k-1 to pass),
        zero-node Novice floor grounding, cycle defect grounding, and deterministic atom generation.

        Args:
            audit: AntiFluffAuditDTO containing topological metrics (cohesion, cycles, isolated nodes).
            total_nodes: Total count of nodes in the upstream causal graph.
            strictness_level: Continuous 0-100 workflow strictness level.
            matrix_block_id: Mandatory non-nullable Opaque Stripe ID of the matrix block.
            bars_claims: Optional insertion-ordered mapping of tda_id to claim text for BARS Levels 1-5.
            matrix_block: Optional hydrated MatrixPromptBlock providing BARS TDAAssertion rows.

        Returns:
            CausalCohesionEvaluationDTO containing atom results, level stats, and score result.
        """
        settings = get_settings()
        resolved_claims = bars_claims
        if resolved_claims is None and isinstance(matrix_block, MatrixPromptBlock):
            resolved_claims = {
                a.tda_id: c.label.resolve("en")
                for sc in matrix_block.scales
                for c in sc.claims
                for a in c.tda_assertions
            }
        if resolved_claims and len(resolved_claims) >= 5:
            tda_ids = tuple(resolved_claims.keys())[:5]
            claims = tuple(resolved_claims.values())[:5]
        else:
            tda_ids = tuple(generate_opaque_id(EntityPrefix.TDA) for _ in range(5))
            claims = tuple(f"Causal cohesion BARS level {lvl}" for lvl in range(1, 6))

        if total_nodes > 0:
            isolated_ratio = audit.isolated_concept_count / total_nodes
        else:
            isolated_ratio = 1.0

        # Phase 5, Step 5: Enforce Equation (13) Cumulative Guttman Invariant (L1 subset L2 subset L3 subset L4 subset L5)
        l1_passed = total_nodes >= 1
        l2_passed = (
            l1_passed
            and total_nodes >= settings.causal_cohesion_l2_min_nodes
            and not audit.cycle_detected
            and audit.logical_cohesion_score >= settings.causal_cohesion_l2_threshold
            and isolated_ratio <= (1.0 - settings.causal_cohesion_l2_threshold)
            and audit.largest_component_ratio >= settings.causal_cohesion_l2_lcc_min
        )
        l3_passed = (
            l2_passed
            and total_nodes >= settings.causal_cohesion_l3_min_nodes
            and audit.logical_cohesion_score >= settings.causal_cohesion_l3_threshold
            and isolated_ratio <= settings.causal_cohesion_l3_isolation_max
            and audit.largest_component_ratio >= settings.causal_cohesion_l3_lcc_min
        )
        l4_passed = (
            l3_passed
            and total_nodes >= settings.causal_cohesion_l4_min_nodes
            and audit.logical_cohesion_score >= settings.causal_cohesion_l4_threshold
            and isolated_ratio <= settings.causal_cohesion_l4_isolation_max
            and audit.largest_component_ratio >= settings.causal_cohesion_l4_lcc_min
            and audit.branch_convergence_ratio >= settings.causal_cohesion_l4_convergence_min
        )
        l5_passed = (
            l4_passed
            and total_nodes >= settings.causal_cohesion_l5_min_nodes
            and audit.logical_cohesion_score >= settings.causal_cohesion_l5_threshold
            and isolated_ratio <= settings.causal_cohesion_l5_isolation_max
            and audit.largest_component_ratio >= settings.causal_cohesion_l5_lcc_min
        )

        passed_flags = (l1_passed, l2_passed, l3_passed, l4_passed, l5_passed)

        atom_results: list[AtomResultDTO] = []
        for level, passed in enumerate(passed_flags, 1):
            tda_id = tda_ids[level - 1]
            if passed:
                atom = AtomResultDTO(
                    tda_id=tda_id,
                    matrix_id=matrix_block_id,
                    status=ExecutionStatus.PASSED,
                    contextual_override=True,
                    is_inverse_evidence=False,
                    source_quotes=None,
                    evaluation_reasoning=(
                        f"Topological causal cohesion score {audit.logical_cohesion_score:.2f} "
                        f"satisfies Level {level} threshold."
                    ),
                    extensions={},
                    depends_on_tda_ids=[],
                    short_circuit_reason_tda_ids=[],
                )
            else:
                atom = AtomResultDTO(
                    tda_id=tda_id,
                    matrix_id=matrix_block_id,
                    status=ExecutionStatus.FAILED,
                    contextual_override=False,
                    is_inverse_evidence=False,
                    source_quotes=None,
                    evaluation_reasoning=(
                        f"Topological causal cohesion score {audit.logical_cohesion_score:.2f} "
                        f"does not satisfy Level {level} threshold."
                    ),
                    extensions={},
                    depends_on_tda_ids=[],
                    short_circuit_reason_tda_ids=[],
                )
            atom_results.append(atom)

        level_stats: dict[str, LevelStatsDTO] = {
            str(lvl): LevelStatsDTO(
                hits=1 if passed else 0,
                total=1,
                dlqs=0,
                pos_hits=1 if passed else 0,
                pos_total=1,
                inv_clean=0,
                inv_total=0,
            )
            for lvl, passed in enumerate(passed_flags, 1)
        }

        score_result = self._scoring_engine.calculate(
            stats={float(k): v for k, v in level_stats.items()},
            math_min=1.0,
            math_max=5.0,
            strictness_level=strictness_level,
        )

        hydrated_references: dict[str, HydratedAtomDTO] = {
            tda_id: HydratedAtomDTO(
                sdui_component=SDUIComponentType.BOOLEAN_CARD,
                resolved_claim=claim,
                source_quotes=None,
            )
            for tda_id, claim in zip(tda_ids, claims, strict=True)
        }

        matrix_output = TraceMatrixPayloadDTO(
            raw_score=score_result.score,
            normalized_score=score_result.score,
            level_breakdown=level_stats,
            justification=(
                f"Topological argument cohesion: score {audit.logical_cohesion_score:.2f}, "
                f"{audit.isolated_concept_count} isolated concepts, cycle_detected={audit.cycle_detected}."
            ),
            evaluated_atoms={a.tda_id: a.status for a in atom_results},
            allowed_extensions=[],
        )

        return CausalCohesionEvaluationDTO(
            matrix_block_id=matrix_block_id,
            atom_results=atom_results,
            level_stats=level_stats,
            score_result=score_result,
            hydrated_references=hydrated_references,
            matrix_output=matrix_output,
        )

    def simulate_counterfactual_retraction(
        self,
        graph: CausalGraphPayloadDTO,
        retracted_node_id: str,
        conjunctive: bool = True,
    ) -> CounterfactualSimulationResultDTO:
        """Simulate discrete ATMS counterfactual premise retraction over a compiled causal graph (Algorithm 1).

        Clamps retracted_node_id to BLOCKED and propagates reachability cascades forward in O(|V| + |E|)
        deterministic linear time under either conjunctive (all antecedents required) or disjunctive
        (corroborative warrant redundancy) gate semantics.

        Args:
            graph: Compiled CausalGraphPayloadDTO instance.
            retracted_node_id: Identifier of the proposition node to retract.
            conjunctive: True for conjunctive deductive gating; False for disjunctive corroborative gating.

        Returns:
            CounterfactualSimulationResultDTO detailing collapsed nodes, surviving nodes, ratio, and depth.

        Raises:
            AppException: If retracted_node_id does not exist in graph.nodes (VALIDATION_FAILED).
        """
        # Phase 5, Step 5: Implement Algorithm 1 discrete ATMS counterfactual retraction simulation
        node_map = {n.node_id: n for n in graph.nodes}
        if retracted_node_id not in node_map:
            logger.error(
                "Fail-Fast: Counterfactual retraction target does not exist in causal graph.",
                extra={
                    "error_code": ErrorCodes.VALIDATION_FAILED.value,
                    "retracted_node_id": retracted_node_id,
                },
            )
            raise AppException(
                message=f"Retracted node '{retracted_node_id}' does not exist in causal graph.",
                status_code=422,
                details={
                    "error_code": ErrorCodes.VALIDATION_FAILED.value,
                    "retracted_node_id": retracted_node_id,
                },
            )

        state_map: dict[str, ExecutionStatus] = {n.node_id: n.status for n in graph.nodes}
        state_map[retracted_node_id] = ExecutionStatus.BLOCKED

        children_by_parent: dict[str, list[str]] = {n.node_id: [] for n in graph.nodes}
        parents_by_child: dict[str, list[str]] = {n.node_id: [] for n in graph.nodes}
        edge_failures = set(graph.edge_root_causes)

        for edge in graph.edges:
            if edge.source_id != edge.target_id:
                children_by_parent[edge.source_id].append(edge.target_id)
                parents_by_child[edge.target_id].append(edge.source_id)

        queue: deque[tuple[str, int]] = deque([(retracted_node_id, 0)])
        visited: set[str] = {retracted_node_id}
        collapsed_node_ids: list[str] = []
        max_cascade_depth = 0

        while queue:
            curr_id, curr_depth = queue.popleft()
            for child_id in children_by_parent[curr_id]:
                if child_id in visited:
                    continue
                parents = parents_by_child[child_id]
                if conjunctive:
                    survives_gate = all(
                        state_map[p_id] == ExecutionStatus.PASSED and f"{p_id}->{child_id}" not in edge_failures
                        for p_id in parents
                    )
                else:
                    survives_gate = any(
                        state_map[p_id] == ExecutionStatus.PASSED and f"{p_id}->{child_id}" not in edge_failures
                        for p_id in parents
                    )
                if not survives_gate:
                    state_map[child_id] = ExecutionStatus.BLOCKED
                    visited.add(child_id)
                    collapsed_node_ids.append(child_id)
                    next_depth = curr_depth + 1
                    if next_depth > max_cascade_depth:
                        max_cascade_depth = next_depth
                    queue.append((child_id, next_depth))

        invalidated_ids = set(collapsed_node_ids) | {retracted_node_id}
        surviving_node_ids = [
            n.node_id
            for n in graph.nodes
            if n.node_id not in invalidated_ids and state_map[n.node_id] == ExecutionStatus.PASSED
        ]
        collapse_ratio = round(len(invalidated_ids) / len(graph.nodes), 4)

        return CounterfactualSimulationResultDTO(
            retracted_root_id=retracted_node_id,
            collapsed_node_ids=collapsed_node_ids,
            surviving_node_ids=surviving_node_ids,
            collapse_ratio=collapse_ratio,
            max_cascade_depth=max_cascade_depth,
        )
