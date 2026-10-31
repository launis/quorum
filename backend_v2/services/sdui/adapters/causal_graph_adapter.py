"""Causal Graph SDUI Adapter.

Transforms causal discovery and TDA fusion results into a SduiCausalGraphBlock
Unified Causal Action Card for Server-Driven UI rendering.
"""

from __future__ import annotations

import logging

from fastapi import status

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.proposition_graph import FalsifiedClaimMatch
from backend_v2.models.dtos.causal_discovery import (
    AntiFluffAuditDTO,
    CausalEdgeDTO,
    CausalGraphPayloadDTO,
    CausalNodeDTO,
    CausalRootCauseDiagnosisDTO,
    CausalTdaFusionResultDTO,
    FairScoringBreakdownDTO,
)
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.view.sdui import AnySduiBlock, SduiCausalGraphBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

__all__ = ["CausalGraphAdapter"]

logger = logging.getLogger(__name__)


class CausalGraphAdapter:
    """Transforms causal discovery graph and fusion results into an SDUI visual block.

    Stateless: no instance state, no side effects.
    """

    @staticmethod
    def build(context: AdapterContext) -> list[AnySduiBlock]:
        """Build SDUI blocks from the adapter context.

        Args:
            context: Frozen, immutable adapter context containing all
                required data for block construction.

        Returns:
            Ordered list containing SduiCausalGraphBlock if causal results exist and not data starved.

        Raises:
            AppException: If causal action card construction fails (VALIDATION_FAILED).
        """
        blocks: list[AnySduiBlock] = []
        if context.is_data_starved or context.causal_result is None:
            return blocks

        action_card = CausalGraphAdapter.build_action_card(context)
        blocks.append(action_card)
        return blocks

    @staticmethod
    def build_action_card(ctx: AdapterContext) -> SduiCausalGraphBlock:
        """Constructs the Unified Causal Action Card block.

        Args:
            ctx: Adapter context with non-null causal_result.

        Returns:
            SduiCausalGraphBlock configured for Dumb Painter rendering.

        Raises:
            AppException: If ctx.causal_result is None (VALIDATION_FAILED).
        """
        causal = ctx.causal_result
        if causal is None:
            msg = "Cannot build causal action card when causal_result is None."
            logger.error("[CausalGraphAdapter] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        fair_scoring: FairScoringBreakdownDTO | None
        falsified_claims_list: list[FalsifiedClaimMatch] = []
        match causal:
            case CausalTdaFusionResultDTO():
                graph = causal.graph
                root_cause_diagnoses = list(causal.root_cause_diagnoses)
                anti_fluff_audit = causal.anti_fluff_audit
                prescriptive_remediations = list(causal.prescriptive_remediations)
                fair_scoring = causal.fair_scoring
                falsified_claims_list = list(causal.falsified_claims)
            case CausalGraphPayloadDTO():
                graph = causal
                root_cause_diagnoses = []
                anti_fluff_audit = AntiFluffAuditDTO(
                    isolated_concept_count=len(graph.isolated_node_ids),
                    cycle_detected=graph.cycle_detected,
                    unsupported_claims_count=0,
                    logical_cohesion_score=1.0 if not graph.cycle_detected else 0.5,
                    detected_hollow_terms=[],
                )
                prescriptive_remediations = []
                fair_scoring = None

        raw_critical_nodes = CausalGraphAdapter._resolve_critical_nodes(
            graph,
            extra_node_ids={fc.falsified_claim_id for fc in falsified_claims_list if fc.falsified_claim_id},
        )
        node_by_id = {n.node_id: n for n in graph.nodes}
        critical_path_nodes = CausalGraphAdapter._enrich_critical_nodes(
            raw_critical_nodes=raw_critical_nodes,
            node_by_id=node_by_id,
            root_cause_diagnoses=root_cause_diagnoses,
            falsified_claims_list=falsified_claims_list,
        )
        block_short_circuited_claims = CausalGraphAdapter._collect_block_short_circuited_claims(
            critical_path_nodes=critical_path_nodes,
            root_cause_diagnoses=root_cause_diagnoses,
        )
        block_falsified_warrant_claims = CausalGraphAdapter._collect_block_falsified_warrant_claims(
            critical_path_nodes=critical_path_nodes,
            falsified_claims_list=falsified_claims_list,
            node_by_id=node_by_id,
        )
        critical_edges = CausalGraphAdapter._resolve_critical_edges(graph, critical_path_nodes)

        total_claims_count = len(graph.nodes)
        intact_claims_count = sum(1 for n in graph.nodes if n.status == ExecutionStatus.PASSED)
        summary = CausalGraphAdapter._build_summary_text(
            intact_claims_count=intact_claims_count,
            total_claims_count=total_claims_count,
            diagnoses_count=len(root_cause_diagnoses),
        )

        return SduiCausalGraphBlock(
            critical_path_nodes=critical_path_nodes,
            critical_edges=critical_edges,
            root_cause_diagnoses=root_cause_diagnoses,
            anti_fluff_audit=anti_fluff_audit,
            prescriptive_remediations=prescriptive_remediations,
            fair_scoring=fair_scoring,
            intact_claims_count=intact_claims_count,
            total_claims_count=total_claims_count,
            summary=summary,
            short_circuited_by_claims=block_short_circuited_claims,
            falsified_warrant_claims=block_falsified_warrant_claims,
        )

    @staticmethod
    def _format_falsified_claim(fc: FalsifiedClaimMatch, node_by_id: dict[str, CausalNodeDTO]) -> str:
        """Formats a single Toulmin falsified claim match into a lineage string.

        Args:
            fc: Falsified claim match DTO.
            node_by_id: Lookup dictionary mapping node_id to CausalNodeDTO.

        Returns:
            Formatted string 'rebuttal -> warrant -> claim_statement'.
        """
        rebuttal_label = node_by_id[fc.rebuttal_id].claim.strip() if fc.rebuttal_id in node_by_id else fc.rebuttal_id
        warrant_label = (
            node_by_id[fc.invalidated_warrant_id].claim.strip()
            if fc.invalidated_warrant_id in node_by_id
            else fc.invalidated_warrant_id
        )
        return f"{rebuttal_label} -> {warrant_label} -> {fc.claim_statement}"

    @staticmethod
    def _enrich_critical_nodes(
        raw_critical_nodes: list[CausalNodeDTO],
        node_by_id: dict[str, CausalNodeDTO],
        root_cause_diagnoses: list[CausalRootCauseDiagnosisDTO],
        falsified_claims_list: list[FalsifiedClaimMatch],
    ) -> list[CausalNodeDTO]:
        """Enriches critical path nodes with short-circuited and falsified warrant claims.

        Args:
            raw_critical_nodes: Unenriched critical path nodes.
            node_by_id: Lookup mapping from node_id to CausalNodeDTO.
            root_cause_diagnoses: Evaluated root cause diagnoses.
            falsified_claims_list: Toulmin falsified claim matches.

        Returns:
            List of enriched CausalNodeDTO instances.
        """
        critical_path_nodes: list[CausalNodeDTO] = []
        for node in raw_critical_nodes:
            parent_claims = {
                node_by_id[pid].claim.strip()
                for pid in node.blame_parent_ids
                if pid in node_by_id and node_by_id[pid].claim.strip()
            }
            diag_claims = {
                diag.root_cause_claim.strip()
                for diag in root_cause_diagnoses
                if diag.failing_node_id == node.node_id and diag.root_cause_claim.strip()
            }
            node_sc_set: set[str] = set(node.short_circuited_by_claims) | parent_claims | diag_claims

            matched_fc_claims = {
                CausalGraphAdapter._format_falsified_claim(fc, node_by_id)
                for fc in falsified_claims_list
                if fc.falsified_claim_id == node.node_id or fc.claim_statement == node.claim
            }
            node_fw_set: set[str] = set(node.falsified_warrant_claims) | matched_fc_claims

            critical_path_nodes.append(
                node.model_copy(
                    update={
                        "short_circuited_by_claims": sorted(list(node_sc_set)),
                        "falsified_warrant_claims": sorted(list(node_fw_set)),
                    }
                )
            )
        return critical_path_nodes

    @staticmethod
    def _collect_block_short_circuited_claims(
        critical_path_nodes: list[CausalNodeDTO],
        root_cause_diagnoses: list[CausalRootCauseDiagnosisDTO],
    ) -> list[str]:
        """Collects deduplicated short-circuited claims for the block header.

        Args:
            critical_path_nodes: Enriched critical path nodes.
            root_cause_diagnoses: Evaluated root cause diagnoses.

        Returns:
            Sorted list of unique short-circuited claim strings.
        """
        block_sc_set: set[str] = {
            diag.root_cause_claim.strip() for diag in root_cause_diagnoses if diag.root_cause_claim.strip()
        }
        for node in critical_path_nodes:
            block_sc_set.update(node.short_circuited_by_claims)
        return sorted(list(block_sc_set))

    @staticmethod
    def _collect_block_falsified_warrant_claims(
        critical_path_nodes: list[CausalNodeDTO],
        falsified_claims_list: list[FalsifiedClaimMatch],
        node_by_id: dict[str, CausalNodeDTO],
    ) -> list[str]:
        """Collects deduplicated falsified warrant lineage strings for the block header.

        Args:
            critical_path_nodes: Enriched critical path nodes.
            falsified_claims_list: Toulmin falsified claim matches.
            node_by_id: Lookup mapping from node_id to CausalNodeDTO.

        Returns:
            Sorted list of unique falsified warrant lineage strings.
        """
        block_fw_set: set[str] = {
            CausalGraphAdapter._format_falsified_claim(fc, node_by_id) for fc in falsified_claims_list
        }
        for node in critical_path_nodes:
            block_fw_set.update(node.falsified_warrant_claims)
        return sorted(list(block_fw_set))

    @staticmethod
    def _resolve_critical_nodes(
        graph: CausalGraphPayloadDTO,
        extra_node_ids: set[str] | None = None,
    ) -> list[CausalNodeDTO]:
        """Selects critical path nodes from the causal graph.

        Args:
            graph: Evaluated causal graph payload.
            extra_node_ids: Optional additional node IDs (such as falsified claim nodes) to include.

        Returns:
            Ordered list of critical path nodes, or all graph nodes if no faults exist.
        """
        critical_node_ids: set[str] = set(graph.root_cause_node_ids)
        if extra_node_ids:
            critical_node_ids.update(extra_node_ids)
        for node in graph.nodes:
            if node.blame_parent_ids or node.status == ExecutionStatus.FAILED:
                critical_node_ids.add(node.node_id)
                critical_node_ids.update(node.blame_parent_ids)

        if not critical_node_ids:
            return list(graph.nodes)
        return [n for n in graph.nodes if n.node_id in critical_node_ids]

    @staticmethod
    def _resolve_critical_edges(
        graph: CausalGraphPayloadDTO,
        critical_nodes: list[CausalNodeDTO],
    ) -> list[CausalEdgeDTO]:
        """Filters graph edges to those connecting critical path nodes.

        Args:
            graph: Evaluated causal graph payload.
            critical_nodes: Resolved critical path nodes.

        Returns:
            List of edges whose source and target both belong to the critical path.
        """
        critical_node_id_set = {n.node_id for n in critical_nodes}
        return [e for e in graph.edges if e.source_id in critical_node_id_set and e.target_id in critical_node_id_set]

    @staticmethod
    def _build_summary_text(
        intact_claims_count: int,
        total_claims_count: int,
        diagnoses_count: int,
    ) -> I18nText:
        """Builds localized summary text for the Unified Causal Action Card.

        Args:
            intact_claims_count: Count of propositions with PASSED status.
            total_claims_count: Total count of propositions in the graph.
            diagnoses_count: Count of identified root cause fault chains.

        Returns:
            I18nText containing English and Finnish summary strings.
        """
        en_summary = (
            f"{intact_claims_count}/{total_claims_count} propositions intact. "
            f"{diagnoses_count} root cause fault chains identified."
        )
        fi_summary = (
            f"{intact_claims_count}/{total_claims_count} väitettä ehjänä. "
            f"{diagnoses_count} juurisyyn ketjua tunnistettu."
        )
        return I18nText(translations={"en": en_summary, "fi": fi_summary})
