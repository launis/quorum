"""Export domain service for generating forensic Excel and flat CSV reports.

Adheres strictly to Tripartite Pipeline Architecture and Dual-Axis Localization:
- Axis 1 (Flutter .arb) is segregated; backend export services use static SSOT mappings.
- Separates presentation export logic from core execution lifecycle.
"""

from __future__ import annotations

import csv
import io
import logging

import openpyxl
import pandas as pd

from backend_v2.database.interfaces import IPromptBlockRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.prompt_blocks import (
    AnyPromptBlock,
)
from backend_v2.models.dtos.causal_discovery import (
    CausalGraphPayloadDTO,
    CausalNodeDTO,
    CausalTdaFusionResultDTO,
)
from backend_v2.models.dtos.export import (
    AtomCausalMetadataDTO,
    AtomScaleMetadataDTO,
    ExportDenormalizedFlatRowDTO,
    ExportForensicAtomDTO,
    ExportMatrixSummaryRowDTO,
    ExportPayloadDTO,
)
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO, ScorecardAtomDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import (
    ExecutionStatus,
    ReportAtomColumn,
    ReportMatrixColumn,
    ReportSheetKey,
)
from backend_v2.services.export.atom_row_builder import (
    build_atom_rows,
    build_denormalized_rows,
)
from backend_v2.services.export.excel_styler import apply_corporate_excel_styling
from backend_v2.services.export.metadata_resolver import (
    build_matrix_atom_maps,
    build_scale_metadata,
    extract_causal_result,
    resolve_causal_meta,
    resolve_context_target,
    resolve_matrix_label,
)
from backend_v2.services.export.summary_builder import build_summary_dtos
from backend_v2.services.localization import ReportHeaderResolver

logger = logging.getLogger(__name__)

__all__ = ["ExportService"]


class ExportService:
    """Domain service for generating forensic Excel and flat CSV exports."""

    def __init__(self, prompt_block_repo: IPromptBlockRepository | None = None) -> None:
        """Initialize the ExportService with an optional prompt block repository.

        Args:
            prompt_block_repo: Optional repository for resolving prompt blocks and matrix definitions.
        """
        self.prompt_block_repo = prompt_block_repo

    @staticmethod
    def _build_matrix_atom_maps(
        effective_matrices: list[MatrixScorecardRowDTO],
    ) -> tuple[dict[str, MatrixScorecardRowDTO], dict[str, ScorecardAtomDTO]]:
        """Maps atom IDs to their parent matrices and scorecard atom records.

        Args:
            effective_matrices: List of evaluated matrix scorecard rows.

        Returns:
            Tuple of atom-to-matrix and atom-to-scorecard-atom lookup dictionaries.
        """
        return build_matrix_atom_maps(effective_matrices)

    @staticmethod
    def _build_scale_metadata(
        blocks_by_id: dict[str, AnyPromptBlock],
        locale: str,
    ) -> dict[str, AtomScaleMetadataDTO]:
        """Indexes scale and claim metadata by TDA atom assertion ID.

        Args:
            blocks_by_id: Pre-indexed prompt blocks dictionary.
            locale: Target localization code ('fi' or 'en').

        Returns:
            Dictionary mapping TDA assertion IDs to scale metadata DTOs.
        """
        return build_scale_metadata(blocks_by_id, locale)

    @staticmethod
    def _resolve_matrix_label(
        atom_matrix_id: str | None,
        tda_id: str,
        parent_m: MatrixScorecardRowDTO | None,
        matrix_title_lookup: dict[str, str],
        blocks_by_id: dict[str, AnyPromptBlock],
        atom_scale_meta: dict[str, AtomScaleMetadataDTO],
        locale: str,
    ) -> str:
        """Resolves localized parent matrix label for an evaluated atom.

        Args:
            atom_matrix_id: Matrix block ID declared on the atom result.
            tda_id: TDA assertion identifier.
            parent_m: Parent matrix row DTO if matched.
            matrix_title_lookup: Pre-computed matrix titles by block ID.
            blocks_by_id: Pre-indexed prompt blocks dictionary.
            atom_scale_meta: Pre-indexed atom scale metadata dictionary.
            locale: Target localization code ('fi' or 'en').

        Returns:
            Resolved localized matrix title string.

        Raises:
            AppException: If matrix definition cannot be found in available lookups.
        """
        return resolve_matrix_label(
            atom_matrix_id=atom_matrix_id,
            tda_id=tda_id,
            parent_m=parent_m,
            matrix_title_lookup=matrix_title_lookup,
            blocks_by_id=blocks_by_id,
            atom_scale_meta=atom_scale_meta,
            locale=locale,
        )

    @staticmethod
    def _resolve_context_target(parent_m: MatrixScorecardRowDTO | None, locale: str) -> str:
        """Resolves localized context target string from parent matrix row.

        Args:
            parent_m: Parent matrix row DTO or None.
            locale: Target localization code ('fi' or 'en').

        Returns:
            Resolved context target string or empty string.
        """
        return resolve_context_target(parent_m, locale)

    @classmethod
    def _extract_causal_result(
        cls, execution: ExecutionRecord | None
    ) -> CausalTdaFusionResultDTO | CausalGraphPayloadDTO | None:
        """Extracts CausalTdaFusionResultDTO or CausalGraphPayloadDTO from execution trace or step states.

        Args:
            execution: Optional ExecutionRecord to extract causal data from.

        Returns:
            CausalTdaFusionResultDTO or CausalGraphPayloadDTO instance if present, else None.
        """
        return extract_causal_result(execution)

    @classmethod
    def _resolve_causal_meta(
        cls,
        c_node: CausalNodeDTO | None,
        root_cause_set: set[str],
        isolated_set: set[str],
    ) -> AtomCausalMetadataDTO:
        """Resolves topological causal metadata for a single argument node.

        Args:
            c_node: Optional CausalNodeDTO instance.
            root_cause_set: Set of node IDs identified as root causes.
            isolated_set: Set of node IDs identified as isolated/orphaned.

        Returns:
            AtomCausalMetadataDTO containing causal_status, blame_parent_id, and dependent_count.
        """
        return resolve_causal_meta(
            c_node=c_node,
            root_cause_set=root_cause_set,
            isolated_set=isolated_set,
        )

    @staticmethod
    def _apply_corporate_excel_styling(workbook: openpyxl.Workbook, sheet_names: list[str]) -> None:
        """Applies professional corporate styling across export sheets.

        Args:
            workbook: Active openpyxl Workbook instance.
            sheet_names: List of sheet names to style.
        """
        apply_corporate_excel_styling(workbook, sheet_names)

    def _build_summary_dtos(
        self,
        effective_matrices: list[MatrixScorecardRowDTO],
        locale: str,
        target_id: str,
    ) -> list[ExportMatrixSummaryRowDTO]:
        """Constructs 13-column summary DTOs for each matrix row in Tab 1.

        Args:
            effective_matrices: Authoritative list of matrix scorecard rows.
            locale: Target localization code ('fi' or 'en').
            target_id: Canonical execution identifier.

        Returns:
            List of strictly validated ExportMatrixSummaryRowDTO instances.
        """
        return build_summary_dtos(
            effective_matrices=effective_matrices,
            locale=locale,
            target_id=target_id,
        )

    def _build_atom_rows(
        self,
        report_dto: ReportDataDTO,
        matrices: list[MatrixScorecardRowDTO],
        locale: str,
        blocks_by_id: dict[str, AnyPromptBlock],
        matrix_title_lookup: dict[str, str],
        all_matrices: list[MatrixScorecardRowDTO] | None = None,
        causal_result: CausalTdaFusionResultDTO | CausalGraphPayloadDTO | None = None,
    ) -> list[ExportForensicAtomDTO]:
        """Constructs tabular raw data rows containing complete atom details with binary results.

        Args:
            report_dto: ReportDataDTO containing evaluated atom results and references.
            matrices: List of authoritative MatrixScorecardRowDTO instances.
            locale: Target localization code ('fi' or 'en').
            blocks_by_id: Pre-indexed prompt blocks dictionary.
            matrix_title_lookup: Pre-computed matrix titles by block ID.
            all_matrices: Optional comprehensive list of all matrix scorecard rows.
            causal_result: Optional composite fusion or causal graph payload.

        Returns:
            List of strictly validated ExportForensicAtomDTO instances.

        Raises:
            AppException: If matrix block for an atom is not found in matrices or blocks_by_id.
        """
        return build_atom_rows(
            report_dto=report_dto,
            matrices=matrices,
            locale=locale,
            blocks_by_id=blocks_by_id,
            matrix_title_lookup=matrix_title_lookup,
            all_matrices=all_matrices,
            causal_result=causal_result,
        )

    def _build_denormalized_rows(
        self,
        report_dto: ReportDataDTO,
        matrices: list[MatrixScorecardRowDTO],
        locale: str,
        blocks_by_id: dict[str, AnyPromptBlock],
        matrix_title_lookup: dict[str, str],
        execution_id: str,
        all_matrices: list[MatrixScorecardRowDTO] | None = None,
        causal_result: CausalTdaFusionResultDTO | CausalGraphPayloadDTO | None = None,
    ) -> list[ExportDenormalizedFlatRowDTO]:
        """Constructs denormalized rows combining parent matrix metrics and atom evaluations.

        Args:
            report_dto: ReportDataDTO containing evaluated atom results.
            matrices: List of authoritative MatrixScorecardRowDTO instances.
            locale: Target localization code ('fi' or 'en').
            blocks_by_id: Pre-indexed prompt blocks dictionary.
            matrix_title_lookup: Pre-computed matrix titles by block ID.
            execution_id: Unique execution identifier.
            all_matrices: Optional comprehensive list of all matrix scorecard rows.
            causal_result: Optional composite fusion or causal graph payload.

        Returns:
            List of strictly validated ExportDenormalizedFlatRowDTO instances.

        Raises:
            AppException: If matrix block for an atom is not found in matrices or blocks_by_id.
        """
        return build_denormalized_rows(
            report_dto=report_dto,
            matrices=matrices,
            locale=locale,
            blocks_by_id=blocks_by_id,
            matrix_title_lookup=matrix_title_lookup,
            execution_id=execution_id,
            all_matrices=all_matrices,
            causal_result=causal_result,
        )

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
            AppException: If execution is not in PASSED state, has no scoreable atoms,
                matrices is empty, matrix block is not found, or Excel generation fails.
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

        if not matrices:
            msg = "Strict Fail-Fast: Execution has no evaluative matrices for Excel export."
            logger.error(
                "[ExportService] %s: %s",
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

        summary_dtos = self._build_summary_dtos(effective_matrices, locale, target_id)

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

        causal_result = self._extract_causal_result(execution)

        atom_dtos = self._build_atom_rows(
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
                self._apply_corporate_excel_styling(writer.book, [sheet_summary, sheet_raw_data])
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
        return ExportPayloadDTO(
            content_bytes=output.getvalue(),
            filename=f"execution_export_{target_id}.xlsx",
            mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    async def export_flat_csv(
        self,
        execution: ExecutionRecord,
        report_dto: ReportDataDTO | None = None,
        matrices: list[MatrixScorecardRowDTO] | None = None,
        locale: str = "fi",
        components: list[AnyPromptBlock] | None = None,
        execution_id: str | None = None,
        all_matrices: list[MatrixScorecardRowDTO] | None = None,
    ) -> ExportPayloadDTO:
        """Generate a flat tabular CSV export streaming 22 denormalized columns.

        Args:
            execution: ExecutionRecord containing evaluation data.
            report_dto: Optional ReportDataDTO containing presentation metrics.
            matrices: Optional list of authoritative MatrixScorecardRowDTO instances.
            locale: Target localization code ('fi' or 'en').
            components: Optional pre-fetched prompt blocks for rule text resolution.
            execution_id: Optional explicit execution ID for the export filename.
            all_matrices: Optional comprehensive list of all matrix scorecard rows.

        Returns:
            ExportPayloadDTO containing CSV bytes and filename.

        Raises:
            AppException: If execution is not PASSED or has no scoreable atoms.
        """
        if execution.status != ExecutionStatus.PASSED:
            msg = "Strict Fail-Fast: Execution must be in PASSED state to export CSV."
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

        eval_matrices: list[MatrixScorecardRowDTO] = []
        if matrices is not None:
            eval_matrices = matrices
        effective_matrices = eval_matrices
        if all_matrices is not None:
            effective_matrices = all_matrices

        target_id = execution.id
        if execution_id is not None:
            target_id = execution_id

        matrix_title_lookup: dict[str, str] = {}
        for m in effective_matrices:
            title = m.label_i18n.resolve(target_locale=locale)
            if not title:
                title = m.name
            matrix_title_lookup[m.block_id] = title

        blocks_by_id: dict[str, AnyPromptBlock] = {}
        if components is not None:
            blocks_by_id = {b.id: b for b in components}
        elif self.prompt_block_repo is not None:
            comp_list = await self.prompt_block_repo.get_all_prompt_blocks()
            blocks_by_id = {b.id: b for b in comp_list}

        causal_result = self._extract_causal_result(execution)

        flat_dtos = self._build_denormalized_rows(
            report_dto=report_dto,
            matrices=effective_matrices,
            locale=locale,
            blocks_by_id=blocks_by_id,
            matrix_title_lookup=matrix_title_lookup,
            execution_id=target_id,
            all_matrices=all_matrices,
            causal_result=causal_result,
        )

        headers = ReportHeaderResolver.get_all_denormalized_csv_headers(locale)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        for row in flat_dtos:
            writer.writerow(
                [
                    row.execution_id,
                    row.matrix_label,
                    row.context_target,
                    row.distribution,
                    row.hits,
                    row.total_atoms,
                    row.hit_ratio,
                    row.raw_score,
                    row.scale_max,
                    row.normalized_score,
                    row.level,
                    row.level_name,
                    row.criterion,
                    row.claim_type,
                    row.is_inverse,
                    row.points_awarded,
                    row.result_status,
                    row.quotes,
                    row.ai_reasoning,
                    row.causal_status,
                    row.blame_parent_id,
                    row.dependent_count,
                ]
            )

        return ExportPayloadDTO(
            content_bytes=output.getvalue().encode("utf-8-sig"),
            filename=f"execution_export_{target_id}.csv",
            mime_type="text/csv",
        )
