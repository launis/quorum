"""Matrix Summary Table SDUI Adapter.

Transforms parsed matrix data into a polymorphic Matrix Table block.
Visual rules are co-located as a module-level MATRIX_SUMMARY_RULES instance to enforce
separation of presentation from logic.
"""

from __future__ import annotations

import logging

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.dtos.causal_discovery import CausalTdaFusionResultDTO
from backend_v2.models.dtos.sdui_rules import MatrixSummaryAestheticsDTO, MatrixSummaryRuleItemDTO
from backend_v2.models.enums import ExecutionStatus, ReportMatrixColumn
from backend_v2.models.view.sdui import (
    AnySduiBlock,
    SduiMatrixTableBlock,
)
from backend_v2.services.localization import ReportHeaderResolver
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

__all__ = ["MATRIX_SUMMARY_RULES", "STANDARD_COLUMNS", "MatrixSummaryTableAdapter"]

logger = logging.getLogger(__name__)

# ============================================================================
# SECTION 1: AESTHETICS RULES
# ============================================================================

MATRIX_SUMMARY_RULES: MatrixSummaryAestheticsDTO = MatrixSummaryAestheticsDTO(
    rules={
        "matrix_summary": MatrixSummaryRuleItemDTO(min_axes=1),
    }
)

STANDARD_COLUMNS: list[str] = [c.value for c in ReportMatrixColumn]


# ============================================================================
# SECTION 2: ADAPTER CLASS
# ============================================================================
class MatrixSummaryTableAdapter:
    """Transforms parsed matrix data into SDUI matrix table blocks.

    Uses co-located MATRIX_SUMMARY_RULES for structural validation.
    Stateless: no instance state, no side effects.
    """

    @staticmethod
    def build(context: AdapterContext) -> list[AnySduiBlock]:
        """Build SDUI blocks from the adapter context.

        Args:
            context: Frozen, immutable adapter context containing all
                required data for block construction.

        Returns:
            Ordered list of polymorphic SDUI blocks ready for rendering.

        Raises:
            AppException: If an unmapped column is specified in matrix_visible_columns
                (ErrorCodes.VALIDATION_FAILED) or if column header translation fails
                (ErrorCodes.CONFIGURATION_ERROR).
        """
        blocks: list[AnySduiBlock] = []

        if context.is_data_starved or len(context.parsed_matrices) < MATRIX_SUMMARY_RULES["matrix_summary"].min_axes:
            return blocks

        axes = list(context.parsed_matrices.values())

        visible_columns = context.profile.matrix_visible_columns

        col_labels: dict[str, I18nText] = {}
        for col in visible_columns:
            try:
                col_enum = ReportMatrixColumn(col)
            except ValueError as e:
                logger.error(
                    "[MatrixSummaryTableAdapter] %s: Unknown matrix summary column '%s'.",
                    ErrorCodes.VALIDATION_FAILED.name,
                    col,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "column": col},
                    exc_info=True,
                )
                raise AppException(
                    message=f"Unknown matrix summary column: '{col}'",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e

            col_labels[col] = I18nText(
                translations={
                    "fi": ReportHeaderResolver.get_matrix_column_header(col_enum, "fi"),
                    "en": ReportHeaderResolver.get_matrix_column_header(col_enum, "en"),
                }
            )

        # Phase 3, Step 3.1: Populate topological short-circuit and Toulmin falsification lineage
        short_circuited_by_claims: list[str] = []
        falsified_warrant_claims: list[str] = []

        for axis in axes:
            for atom in axis.evaluated_atoms:
                if atom.status == ExecutionStatus.N_A:
                    claim_text = atom.claim_label.strip()
                    reasoning_text = atom.semantic_reasoning.strip()
                    if reasoning_text and reasoning_text not in claim_text:
                        entry = f"{claim_text}: {reasoning_text}"
                    else:
                        entry = claim_text
                    if entry and entry not in short_circuited_by_claims:
                        short_circuited_by_claims.append(entry)

        if isinstance(context.causal_result, CausalTdaFusionResultDTO):
            node_claim_by_id = {
                n.node_id: n.claim.strip() for n in context.causal_result.graph.nodes if n.claim.strip()
            }
            for diag in context.causal_result.root_cause_diagnoses:
                root_claim = diag.root_cause_claim.strip()
                if root_claim and root_claim not in short_circuited_by_claims:
                    short_circuited_by_claims.append(root_claim)
            for fc in context.causal_result.falsified_claims:
                rebuttal_label = fc.rebuttal_id
                if fc.rebuttal_id in node_claim_by_id:
                    rebuttal_label = node_claim_by_id[fc.rebuttal_id]
                warrant_label = fc.invalidated_warrant_id
                if fc.invalidated_warrant_id in node_claim_by_id:
                    warrant_label = node_claim_by_id[fc.invalidated_warrant_id]
                fc_entry = f"{rebuttal_label} -> {warrant_label} -> {fc.claim_statement}"
                if fc_entry not in falsified_warrant_claims:
                    falsified_warrant_claims.append(fc_entry)

        blocks.append(
            SduiMatrixTableBlock(
                title=None,
                axes=axes,
                matrix_column_labels=col_labels,
                matrix_visible_columns=visible_columns,
                extension_labels={},
                short_circuited_by_claims=short_circuited_by_claims,
                falsified_warrant_claims=falsified_warrant_claims,
            )
        )

        return blocks
