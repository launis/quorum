"""Pure stateless service for evaluating causal reasoning and argument cohesion BARS matrix.

Evaluates argument structural integrity, inferential cohesion, cycle avoidance,
and isolated claim absence from AntiFluffAuditDTO topological graph telemetry into
a deterministic BARS 1-5 scale and unified competence score.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
from backend_v2.models.dtos.causal_discovery import (
    AntiFluffAuditDTO,
    CausalGraphPayloadDTO,
    CausalRootCauseDiagnosisDTO,
)
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO, ScoringResultDTO
from backend_v2.models.dtos.trace import TraceMatrixPayloadDTO
from backend_v2.models.enums import CausalRootCauseType, ExecutionStatus, SDUIComponentType
from backend_v2.settings import get_settings
from backend_v2.utils.scoring.unified_engine import UnifiedScoringEngine

__all__ = [
    "CAUSAL_COHESION_CLAIMS",
    "CAUSAL_COHESION_TDA_IDS",
    "CausalCohesionEvaluationDTO",
    "CausalCohesionEvaluator",
]

CAUSAL_COHESION_TDA_IDS: tuple[str, ...] = (
    "tda_c0a1e500000000000000000000000001",
    "tda_c0a1e500000000000000000000000002",
    "tda_c0a1e500000000000000000000000003",
    "tda_c0a1e500000000000000000000000004",
    "tda_c0a1e500000000000000000000000005",
)

CAUSAL_COHESION_CLAIMS: tuple[str, ...] = (
    "Circular reasoning or under 40% logical cohesion",
    "Cohesion 40–59%, multiple orphan premise chains",
    "Cohesion 60–79%, core premises linked to conclusions, limited isolated nodes",
    "Cohesion 80–89%, deep and consistent argument structure",
    "Cohesion >= 90%, 0 cycles, under 5% isolated claims, extensive interconnectedness",
)


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

                    is_warrant_failure = edge_key in edge_failures or parent_is_passed
                    if is_warrant_failure:
                        rc_type = CausalRootCauseType.WARRANT_GROUNDING_FAILURE
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
    ) -> CausalCohesionEvaluationDTO:
        """Evaluate topological causal graph metrics into BARS 1-5 scale levels and unified score.

        Enforces the Cumulative Guttman Invariant (Level k requires Level k-1 to pass),
        zero-node Novice floor grounding, cycle defect grounding, and deterministic atom generation.

        Args:
            audit: AntiFluffAuditDTO containing topological metrics (cohesion, cycles, isolated nodes).
            total_nodes: Total count of nodes in the upstream causal graph.
            strictness_level: Continuous 0-100 workflow strictness level.
            matrix_block_id: Mandatory non-nullable Opaque Stripe ID of the matrix block.

        Returns:
            CausalCohesionEvaluationDTO containing atom results, level stats, and score result.
        """
        settings = get_settings()

        if total_nodes > 0:
            isolated_ratio = audit.isolated_concept_count / total_nodes
        else:
            isolated_ratio = 1.0

        # Cumulative Guttman Invariant: L1 subset L2 subset L3 subset L4 subset L5
        l1_passed = True  # Novice floor is unconditional
        l2_passed = (
            l1_passed
            and total_nodes > 0
            and not audit.cycle_detected
            and audit.logical_cohesion_score >= settings.causal_cohesion_l2_threshold
        )
        l3_passed = (
            l2_passed
            and audit.logical_cohesion_score >= settings.causal_cohesion_l3_threshold
            and isolated_ratio <= settings.causal_cohesion_l3_isolation_max
        )
        l4_passed = (
            l3_passed
            and audit.logical_cohesion_score >= settings.causal_cohesion_l4_threshold
            and isolated_ratio <= settings.causal_cohesion_l4_isolation_max
        )
        l5_passed = (
            l4_passed
            and audit.logical_cohesion_score >= settings.causal_cohesion_l5_threshold
            and isolated_ratio <= settings.causal_cohesion_l5_isolation_max
        )

        passed_flags = (l1_passed, l2_passed, l3_passed, l4_passed, l5_passed)

        atom_results: list[AtomResultDTO] = []
        for level, passed in enumerate(passed_flags, 1):
            tda_id = CAUSAL_COHESION_TDA_IDS[level - 1]
            if passed:
                atom = AtomResultDTO(
                    tda_id=tda_id,
                    matrix_id=matrix_block_id,
                    status=ExecutionStatus.PASSED,
                    contextual_override=True,
                    is_inverse_evidence=False,
                    source_quote=None,
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
                    source_quote=None,
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
                source_quote=None,
            )
            for tda_id, claim in zip(CAUSAL_COHESION_TDA_IDS, CAUSAL_COHESION_CLAIMS, strict=True)
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
