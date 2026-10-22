"""Excel workbook export service sub-module.

Extracts Excel binary streaming routines from monolithic ExportService under Epoch 1
(Pure Structural Lift-and-Shift) with zero behavioral changes.
"""

from __future__ import annotations

import io
import logging
from typing import TYPE_CHECKING

import pandas as pd

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.prompt_blocks import AnyPromptBlock
from backend_v2.models.dtos.export import ExportPayloadDTO
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import (
    ExecutionStatus,
    ReportAtomColumn,
    ReportMatrixColumn,
    ReportSheetKey,
)
from backend_v2.services.export.atom_row_builder import build_atom_rows
from backend_v2.services.export.excel_styler import apply_corporate_excel_styling
from backend_v2.services.export.metadata_resolver import extract_causal_result
from backend_v2.services.export.summary_builder import build_summary_dtos
from backend_v2.services.localization import ReportHeaderResolver

if TYPE_CHECKING:
    from backend_v2.database.interfaces import IPromptBlockRepository

__all__ = ["ExcelExporter"]

logger = logging.getLogger(__name__)


class ExcelExporter:
    """Service for generating corporate-styled Excel workbooks from execution records.

    Attributes:
        prompt_block_repo: Optional prompt block repository for resolving block definitions.
    """

    def __init__(self, prompt_block_repo: IPromptBlockRepository | None = None) -> None:
        """Initialize the Excel exporter.

        Args:
            prompt_block_repo: Optional repository for resolving prompt blocks.
        """
        self.prompt_block_repo = prompt_block_repo

    async def export_excel(
        self,
        execution: ExecutionRecord,
        report_dto: ReportDataDTO | None,
        matrices: list[MatrixScorecardRowDTO],
        locale: str = "fi",
        components: list[AnyPromptBlock] | None = None,
        execution_id: str | None = None,
        all_matrices: list[MatrixScorecardRowDTO] | None = None,
    ) -> ExportPayloadDTO:
        """Generate an Excel export for the execution including Summary and Raw Data tabs.

        Args:
            execution: ExecutionRecord containing evaluation data.
            report_dto: Optional ReportDataDTO containing presentation metrics.
            matrices: List of authoritative MatrixScorecardRowDTO instances to emit 1:1.
            locale: Target localization code ('fi' or 'en').
            components: Optional pre-fetched prompt blocks for rule text resolution.
            execution_id: Optional explicit execution ID for the export filename.
            all_matrices: Optional comprehensive list of all matrix scorecard rows.

        Returns:
            ExportPayloadDTO containing the Excel file bytes and canonical filename.

        Raises:
            AppException: If execution is not in PASSED state (400), has no scoreable atoms (400),
                matrices is empty (400), or Excel generation fails (500).
        """
        # Phase 3, Step 1: Enforce PASSED state validation
        if execution.status != ExecutionStatus.PASSED:
            msg = "Strict Fail-Fast: Execution must be in PASSED state to export Excel."
            logger.error(
                "[ExcelExporter] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        # Phase 3, Step 1: Enforce scoreable atoms validation
        if report_dto is None or not report_dto.results:
            msg = "Strict Fail-Fast: Execution has no scoreable atoms."
            logger.error(
                "[ExcelExporter] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        # Phase 3, Step 1: Enforce non-empty matrices validation
        if not matrices:
            msg = "Strict Fail-Fast: Execution has no evaluative matrices for Excel export."
            logger.error(
                "[ExcelExporter] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        effective_matrices = matrices
        if all_matrices is not None:
            effective_matrices = all_matrices

        target_id = execution.id
        if execution_id is not None:
            target_id = execution_id

        matrix_title_lookup: dict[str, str] = {}
        for m in effective_matrices:
            lbl = m.label_i18n.resolve(target_locale=locale)
            if not lbl:
                lbl = m.name
            matrix_title_lookup[m.block_id] = lbl

        summary_dtos = build_summary_dtos(effective_matrices, locale, target_id)

        tab1_headers = ReportHeaderResolver.get_all_matrix_headers(locale)
        tab1_rows = [
            {
                tab1_headers[ReportMatrixColumn.EXECUTION_ID]: s.execution_id,
                tab1_headers[ReportMatrixColumn.LABEL]: s.label,
                tab1_headers[ReportMatrixColumn.CONTEXT_TARGET]: s.context_target,
                tab1_headers[ReportMatrixColumn.DISTRIBUTION]: s.distribution,
                tab1_headers[ReportMatrixColumn.HITS]: s.hits,
                tab1_headers[ReportMatrixColumn.TOTAL_ATOMS]: s.total_atoms,
                tab1_headers[ReportMatrixColumn.HIT_RATIO]: s.hit_ratio,
                tab1_headers[ReportMatrixColumn.RAW_SCORE]: s.raw_score,
                tab1_headers[ReportMatrixColumn.SCALE_MAX]: s.scale_max,
                tab1_headers[ReportMatrixColumn.NORMALIZED_SCORE]: s.normalized_score,
                tab1_headers[ReportMatrixColumn.ROW_EXPLANATION]: s.row_explanation,
                tab1_headers[ReportMatrixColumn.CRITERIA]: s.criteria,
                tab1_headers[ReportMatrixColumn.SOURCE]: s.source,
            }
            for s in summary_dtos
        ]

        blocks_by_id: dict[str, AnyPromptBlock] = {}
        if components is not None:
            blocks_by_id = {b.id: b for b in components}
        elif self.prompt_block_repo is not None:
            comp_list = await self.prompt_block_repo.get_all_prompt_blocks()
            blocks_by_id = {b.id: b for b in comp_list}

        causal_result = extract_causal_result(execution)

        atom_dtos = build_atom_rows(
            report_dto=report_dto,
            matrices=matrices,
            locale=locale,
            blocks_by_id=blocks_by_id,
            matrix_title_lookup=matrix_title_lookup,
            all_matrices=all_matrices,
            causal_result=causal_result,
        )

        atom_headers = {col: ReportHeaderResolver.get_atom_column_header(col, locale) for col in ReportAtomColumn}
        tab2_rows = [
            {
                atom_headers[ReportAtomColumn.MATRIX]: a.matrix_label,
                atom_headers[ReportAtomColumn.CONTEXT_TARGET]: a.context_target,
                atom_headers[ReportAtomColumn.LEVEL]: a.level,
                atom_headers[ReportAtomColumn.LEVEL_NAME]: a.level_name,
                atom_headers[ReportAtomColumn.CRITERION]: a.criterion,
                atom_headers[ReportAtomColumn.CLAIM_TYPE]: a.claim_type,
                atom_headers[ReportAtomColumn.IS_INVERSE]: a.is_inverse,
                atom_headers[ReportAtomColumn.POINTS_AWARDED]: a.points_awarded,
                atom_headers[ReportAtomColumn.RESULT_STATUS]: a.result_status,
                atom_headers[ReportAtomColumn.QUOTES]: a.quotes,
                atom_headers[ReportAtomColumn.AI_REASONING]: a.ai_reasoning,
                atom_headers[ReportAtomColumn.CAUSAL_STATUS]: a.causal_status,
                atom_headers[ReportAtomColumn.BLAME_PARENT_ID]: a.blame_parent_id,
                atom_headers[ReportAtomColumn.DEPENDENT_COUNT]: a.dependent_count,
            }
            for a in atom_dtos
        ]

        sheet_summary = ReportHeaderResolver.get_sheet_name(ReportSheetKey.SUMMARY, locale)
        sheet_raw_data = ReportHeaderResolver.get_sheet_name(ReportSheetKey.RAW_DATA, locale)

        output = io.BytesIO()
        try:
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                pd.DataFrame(tab1_rows).to_excel(writer, sheet_name=sheet_summary, index=False)
                pd.DataFrame(tab2_rows).to_excel(writer, sheet_name=sheet_raw_data, index=False)
                apply_corporate_excel_styling(writer.book, [sheet_summary, sheet_raw_data])
        except Exception as e:
            logger.error(
                "[ExcelExporter] %s: Excel writing failed - %s",
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
        return ExportPayloadDTO(
            content_bytes=output.getvalue(),
            filename=f"execution_export_{target_id}.xlsx",
            mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
