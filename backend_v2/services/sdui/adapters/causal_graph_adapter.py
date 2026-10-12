"""Causal Graph SDUI Adapter.

Transforms causal discovery and TDA fusion results into a SduiCausalGraphBlock
Unified Causal Action Card for Server-Driven UI rendering.
"""

from __future__ import annotations

import logging

from fastapi import status

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.dtos.causal_discovery import (
    AntiFluffAuditDTO,
    CausalTdaFusionResultDTO,
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

        if isinstance(causal, CausalTdaFusionResultDTO):
            graph = causal.graph
            root_cause_diagnoses = list(causal.root_cause_diagnoses)
            anti_fluff_audit = causal.anti_fluff_audit
            prescriptive_remediations = list(causal.prescriptive_remediations)
            fair_scoring = causal.fair_scoring
        else:
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

        # Critical path nodes: root cause nodes, nodes with blame parents, failing nodes, or all if none
        critical_node_ids: set[str] = set(graph.root_cause_node_ids)
        for node in graph.nodes:
            if node.blame_parent_ids or node.status == ExecutionStatus.FAILED:
                critical_node_ids.add(node.node_id)
                critical_node_ids.update(node.blame_parent_ids)

        if not critical_node_ids:
            critical_path_nodes = list(graph.nodes)
        else:
            critical_path_nodes = [n for n in graph.nodes if n.node_id in critical_node_ids]

        critical_node_id_set = {n.node_id for n in critical_path_nodes}
        critical_edges = [
            e for e in graph.edges if e.source_id in critical_node_id_set and e.target_id in critical_node_id_set
        ]

        total_claims_count = len(graph.nodes)
        intact_claims_count = sum(1 for n in graph.nodes if n.status == ExecutionStatus.PASSED)

        en_summary = (
            f"{intact_claims_count}/{total_claims_count} propositions intact. "
            f"{len(root_cause_diagnoses)} root cause fault chains identified."
        )
        fi_summary = (
            f"{intact_claims_count}/{total_claims_count} väitettä ehjänä. "
            f"{len(root_cause_diagnoses)} juurisyyn ketjua tunnistettu."
        )
        summary = I18nText(translations={"en": en_summary, "fi": fi_summary})

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
        )
