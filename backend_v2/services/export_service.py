"""Export domain service for generating forensic Excel and flat CSV reports.

Adheres strictly to Tripartite Pipeline Architecture and Dual-Axis Localization:
- Axis 1 (Flutter .arb) is segregated; backend export services use static SSOT mappings.
- Separates presentation export logic from core execution lifecycle.
"""

from __future__ import annotations

import csv
import io
import logging
from typing import Any

from backend_v2.database.interfaces import IComponentRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.prompt_blocks import (
    AnyPromptBlock,
    MatrixPromptBlock,
    PersonaPromptBlock,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.view.sdui import (
    SduiMatrixTableBlock,
    SduiMetrics1DBlock,
    SduiRadarChartBlock,
    SduiScatterPlotBlock,
)
from backend_v2.services.flattener import FlatFileService

logger = logging.getLogger(__name__)

__all__ = ["ExportService"]

_EXCEL_KEYS = (
    ("excelHeaderMatrix", "Matriisi", "Matrix"),
    ("excelHeaderGrade", "Arvosana", "Grade"),
    ("excelHeaderMaxScore", "Maksimi", "Max Score"),
    ("excelHeaderCriterion", "Kriteeri (UI)", "Criterion Name (UI)"),
    ("excelHeaderAiRule", "AI-s\u00e4\u00e4nt\u00f6", "AI Rule"),
    ("excelHeaderInternalizedRule", "Sis\u00e4istetty s\u00e4\u00e4nt\u00f6", "Internalized Rule"),
    ("excelHeaderResultStatus", "Tulos (Status)", "Result (Status)"),
    ("excelHeaderConfidence", "Luottamusarvio", "Confidence Estimate"),
    ("excelHeaderReasoningLength", "Perustelun pituus", "Reasoning Length"),
    ("excelHeaderFoundQuotes", "L\u00f6ydetyt sitaatit", "Found Quotes"),
    ("excelHeaderUsedSources", "K\u00e4ytetyt l\u00e4hteet", "Used Sources"),
    ("excelHeaderAiReasoning", "AI-perustelu", "AI Reasoning"),
    ("excelHeaderFalsification", "Falsifiointi", "Falsification"),
    ("excelSheetSummary", "Yhteenveto", "Summary"),
    ("excelSheetRawData", "Raakadata", "Raw Data"),
)
_EXCEL_HEADERS_FI: dict[str, str] = {k: fi for k, fi, _ in _EXCEL_KEYS}
_EXCEL_HEADERS_EN: dict[str, str] = {k: en for k, _, en in _EXCEL_KEYS}


def _extract_claim_rule(block: AnyPromptBlock | None) -> str:
    """Extract operational rule description from a prompt block.

    Args:
        block: Prompt block to extract operational rule from.

    Returns:
        Extracted operational rule description or empty string.
    """
    match block:
        case MatrixPromptBlock(ai_description=desc) if desc:
            return desc
        case SystemRulePromptBlock(instruction_text=text) if text:
            return text
        case PersonaPromptBlock(role_enforcement=text) if text:
            return text
        case ProtocolPromptBlock(protocol_instructions=text) if text:
            return text
        case _:
            return ""


class ExportService:
    """Domain service for generating forensic Excel and flat CSV exports."""

    def __init__(self, comp_repo: IComponentRepository | None = None) -> None:
        """Initialize the ExportService with an optional component repository.

        Args:
            comp_repo: Optional repository for resolving prompt block component descriptions.
        """
        self.comp_repo = comp_repo

    async def export_excel(
        self,
        execution: ExecutionRecord,
        report_dto: ReportDataDTO | None,
        locale: str = "fi",
        components: list[AnyPromptBlock] | None = None,
        execution_id: str | None = None,
    ) -> tuple[bytes, str]:
        """Generate an Excel export for the execution including Summary and Raw Data tabs.

        Args:
            execution: ExecutionRecord containing evaluation data.
            report_dto: Optional ReportDataDTO containing presentation metrics.
            locale: Target localization code ('fi' or 'en').
            components: Optional pre-fetched prompt blocks for rule text resolution.
            execution_id: Optional explicit execution ID for the export filename.

        Returns:
            Tuple of the Excel file bytes and the suggested filename.

        Raises:
            AppException: If execution is not in PASSED state, has no scoreable atoms, or Excel generation fails (ErrorCodes.VALIDATION_FAILED, ErrorCodes.INTERNAL_SERVER_ERROR).
        """
        if execution.status != ExecutionStatus.PASSED:
            msg = "Strict Fail-Fast: Execution must be in PASSED state to export Excel."
            logger.error(
                "[ExportService] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        if report_dto is None or not report_dto.results:
            msg = "Strict Fail-Fast: Execution has no scoreable atoms."
            logger.error(
                "[ExportService] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        if locale.lower().startswith("fi"):
            h = _EXCEL_HEADERS_FI
        else:
            h = _EXCEL_HEADERS_EN

        summary_rows = []
        matrix_title_lookup: dict[str, str] = {}
        if report_dto.inner_sdui_blocks is not None:
            matrices: list[Any] = []
            for block in report_dto.inner_sdui_blocks:
                match block:
                    case (
                        SduiRadarChartBlock(axes=axes)
                        | SduiScatterPlotBlock(axes=axes)
                        | SduiMatrixTableBlock(axes=axes)
                        | SduiMetrics1DBlock(axes=axes)
                    ):
                        matrices.extend(axes)
                    case _:
                        pass
            for m in matrices:
                lbl = m.label_i18n.resolve()
                matrix_title_lookup[m.block_id] = lbl
                summary_rows.append(
                    {
                        h["excelHeaderMatrix"]: lbl,
                        h["excelHeaderGrade"]: m.score,
                        h["excelHeaderMaxScore"]: m.scale_max,
                    }
                )

        blocks_by_id: dict[str, AnyPromptBlock] = {}
        if components is not None:
            blocks_by_id = {b.id: b for b in components}
        elif self.comp_repo is not None:
            comp_list = await self.comp_repo.get_all_components("prompt_block")
            blocks_by_id = {b.id: b for b in comp_list}

        rows = []
        hydrated_refs = report_dto.hydrated_references
        for atom in report_dto.results:
            matrix_label = ""
            if atom.matrix_id:
                if atom.matrix_id in matrix_title_lookup:
                    matrix_label = matrix_title_lookup[atom.matrix_id]
                elif atom.matrix_id in blocks_by_id:
                    blk = blocks_by_id[atom.matrix_id]
                    matrix_label = blk.label.resolve()
                else:
                    matrix_label = atom.matrix_id

            ref = hydrated_refs[atom.tda_id]
            criterion = ref.resolved_claim

            target_block: AnyPromptBlock | None = None
            if atom.matrix_id and atom.matrix_id in blocks_by_id:
                target_block = blocks_by_id[atom.matrix_id]
            elif atom.tda_id in blocks_by_id:
                target_block = blocks_by_id[atom.tda_id]
            rule_text = _extract_claim_rule(target_block)

            reasoning = atom.evaluation_reasoning
            if reasoning is None:
                reasoning = ""
            w_count = 0
            if reasoning:
                w_count = len(reasoning.split())

            quote_str = ""
            if atom.source_quote is not None:
                quote_str = atom.source_quote
            elif ref.source_quote is not None:
                quote_str = ref.source_quote

            internalized_rule_val = ""
            if "internalized_rule" in atom.extensions:
                internalized_rule_val = atom.extensions["internalized_rule"]

            confidence_val = None
            if "confidence" in atom.extensions:
                confidence_val = atom.extensions["confidence"]

            source_id_val = ""
            if "source_id" in atom.extensions:
                source_id_val = atom.extensions["source_id"]

            falsification_val = ""
            if "falsification" in atom.extensions:
                falsification_val = atom.extensions["falsification"]

            if atom.status == ExecutionStatus.PASSED:
                result_status = 1
            else:
                result_status = 0

            rows.append(
                {
                    h["excelHeaderMatrix"]: matrix_label,
                    h["excelHeaderCriterion"]: criterion,
                    h["excelHeaderAiRule"]: rule_text,
                    h["excelHeaderInternalizedRule"]: internalized_rule_val,
                    h["excelHeaderResultStatus"]: result_status,
                    h["excelHeaderConfidence"]: confidence_val,
                    h["excelHeaderReasoningLength"]: w_count,
                    h["excelHeaderFoundQuotes"]: quote_str,
                    h["excelHeaderUsedSources"]: source_id_val,
                    h["excelHeaderAiReasoning"]: reasoning,
                    h["excelHeaderFalsification"]: falsification_val,
                }
            )

        output = io.BytesIO()
        try:
            import pandas as pd

            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                pd.DataFrame(summary_rows).to_excel(writer, sheet_name=h["excelSheetSummary"], index=False)
                pd.DataFrame(rows).to_excel(writer, sheet_name=h["excelSheetRawData"], index=False)
        except Exception as e:
            logger.error(
                "[ExportService] %s: Excel writing failed - %s",
                ErrorCodes.INTERNAL_SERVER_ERROR.name,
                e,
                exc_info=True,
                extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
            )
            raise AppException(
                message="Failed to generate Excel export",
                status_code=500,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
            ) from e

        output.seek(0)
        if execution_id is not None:
            target_id = execution_id
        else:
            target_id = execution.id
        return output.getvalue(), f"execution_export_{target_id}.xlsx"

    def export_flat_csv(
        self,
        execution: ExecutionRecord,
        report_dto: ReportDataDTO | None = None,
        execution_id: str | None = None,
    ) -> tuple[bytes, str]:
        """Generate a flat CSV export for the execution using FlatFileService.

        Args:
            execution: ExecutionRecord containing evaluation data.
            report_dto: Optional ReportDataDTO containing presentation metrics.
            execution_id: Optional explicit execution ID for the export filename.

        Returns:
            Tuple of the CSV file bytes and the suggested filename.
        """
        flat_data = FlatFileService.flatten_results(execution, report_dto)
        csv_dict = flat_data.to_csv_dict()
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(csv_dict.keys()))
        writer.writeheader()
        writer.writerow(csv_dict)
        if execution_id is not None:
            target_id = execution_id
        else:
            target_id = execution.id
        return output.getvalue().encode("utf-8"), f"execution_export_{target_id}.csv"
