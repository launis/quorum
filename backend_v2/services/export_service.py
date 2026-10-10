"""Export domain service for generating forensic Excel and flat CSV reports.

Adheres strictly to Tripartite Pipeline Architecture and Dual-Axis Localization:
- Axis 1 (Flutter .arb) is segregated; backend export services use static SSOT mappings.
- Separates presentation export logic from core execution lifecycle.
"""

from __future__ import annotations

import csv
import io
import logging

from backend_v2.database.interfaces import IPromptBlockRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.prompt_blocks import (
    AnyPromptBlock,
    MatrixPromptBlock,
)
from backend_v2.models.dtos.export import (
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
from backend_v2.services.localization import LocalizationService, ReportHeaderResolver

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

    def _build_atom_rows(
        self,
        report_dto: ReportDataDTO,
        matrices: list[MatrixScorecardRowDTO],
        locale: str,
        blocks_by_id: dict[str, AnyPromptBlock],
        matrix_title_lookup: dict[str, str],
    ) -> list[ExportForensicAtomDTO]:
        """Constructs tabular raw data rows containing complete atom details with binary results.

        Args:
            report_dto: ReportDataDTO containing evaluated atom results and references.
            matrices: List of authoritative MatrixScorecardRowDTO instances.
            locale: Target localization code ('fi' or 'en').
            blocks_by_id: Pre-indexed prompt blocks dictionary.
            matrix_title_lookup: Pre-computed matrix titles by block ID.

        Returns:
            List of strictly validated ExportForensicAtomDTO instances.

        Raises:
            AppException: If matrix block for an atom is not found in matrices or blocks_by_id.
        """
        atom_to_matrix: dict[str, MatrixScorecardRowDTO] = {}
        atom_to_scorecard: dict[str, ScorecardAtomDTO] = {}
        for m in matrices:
            for s_atom in m.evaluated_atoms:
                atom_to_matrix[s_atom.atom_id] = m
                atom_to_scorecard[s_atom.atom_id] = s_atom

        atom_is_inverse: dict[str, bool] = {}
        for b in blocks_by_id.values():
            if isinstance(b, MatrixPromptBlock) and b.scales:
                for scale in b.scales:
                    for claim in scale.claims:
                        for tda in claim.tda_assertions:
                            atom_is_inverse[tda.tda_id] = bool(tda.inverse_evidence)

        atom_rows: list[ExportForensicAtomDTO] = []
        hydrated_refs = report_dto.hydrated_references
        for atom in report_dto.results:
            parent_m = None
            if atom.tda_id in atom_to_matrix:
                parent_m = atom_to_matrix[atom.tda_id]

            matrix_label = ""
            if atom.matrix_id:
                if atom.matrix_id in matrix_title_lookup:
                    matrix_label = matrix_title_lookup[atom.matrix_id]
                elif atom.matrix_id in blocks_by_id:
                    blk = blocks_by_id[atom.matrix_id]
                    matrix_label = blk.label.resolve(target_locale=locale)
                elif parent_m is not None:
                    matrix_label = parent_m.label_i18n.resolve(target_locale=locale)
                    if not matrix_label:
                        matrix_label = parent_m.name
                else:
                    msg = (
                        f"Strict Fail-Fast: Matrix block '{atom.matrix_id}' for atom '{atom.tda_id}' "
                        "not found in matrices or prompt block repository."
                    )
                    logger.error(
                        "[ExportService] %s: %s",
                        ErrorCodes.RESOURCE_NOT_FOUND.name,
                        msg,
                        extra={
                            "error_code": ErrorCodes.RESOURCE_NOT_FOUND.value,
                            "matrix_id": atom.matrix_id,
                            "tda_id": atom.tda_id,
                        },
                    )
                    raise AppException(
                        message=msg,
                        status_code=404,
                        details={
                            "error_code": ErrorCodes.RESOURCE_NOT_FOUND.value,
                            "matrix_id": atom.matrix_id,
                            "tda_id": atom.tda_id,
                        },
                    )
            elif parent_m is not None:
                matrix_label = parent_m.label_i18n.resolve(target_locale=locale)
                if not matrix_label:
                    matrix_label = parent_m.name
            else:
                msg = (
                    f"Strict Fail-Fast: Matrix block for atom '{atom.tda_id}' "
                    "not found in matrices or prompt block repository."
                )
                logger.error(
                    "[ExportService] %s: %s",
                    ErrorCodes.RESOURCE_NOT_FOUND.name,
                    msg,
                    extra={
                        "error_code": ErrorCodes.RESOURCE_NOT_FOUND.value,
                        "tda_id": atom.tda_id,
                    },
                )
                raise AppException(
                    message=msg,
                    status_code=404,
                    details={
                        "error_code": ErrorCodes.RESOURCE_NOT_FOUND.value,
                        "tda_id": atom.tda_id,
                    },
                )

            context_target = ""
            if parent_m is not None:
                if parent_m.context_target_label is not None:
                    context_target = parent_m.context_target_label.resolve(target_locale=locale)
                elif parent_m.context_target:
                    context_target = parent_m.context_target

            scorecard_atom = None
            if atom.tda_id in atom_to_scorecard:
                scorecard_atom = atom_to_scorecard[atom.tda_id]

            level = 0
            level_name = ""
            if scorecard_atom is not None:
                level = scorecard_atom.level
                level_name = scorecard_atom.level_name

            ref = None
            if hydrated_refs and atom.tda_id in hydrated_refs:
                ref = hydrated_refs[atom.tda_id]

            criterion = ""
            if ref and ref.resolved_claim:
                criterion = ref.resolved_claim
            elif scorecard_atom and scorecard_atom.claim_label:
                criterion = scorecard_atom.claim_label

            is_inverse_claim = atom.is_inverse_evidence or (
                atom.tda_id in atom_is_inverse and atom_is_inverse[atom.tda_id]
            )
            claim_type = (
                LocalizationService.translate("export_claim_inverse", locale)
                if is_inverse_claim
                else LocalizationService.translate("export_claim_positive", locale)
            )

            result_status: int = 1 if atom.status == ExecutionStatus.PASSED else 0

            quote_str = ""
            if atom.source_quote is not None:
                quote_str = atom.source_quote
            elif ref is not None and ref.source_quote is not None:
                quote_str = ref.source_quote

            reasoning = ""
            if atom.evaluation_reasoning is not None:
                reasoning = atom.evaluation_reasoning

            atom_rows.append(
                ExportForensicAtomDTO(
                    matrix_label=matrix_label,
                    context_target=context_target,
                    level=level,
                    level_name=level_name,
                    criterion=criterion,
                    claim_type=claim_type,
                    result_status=result_status,
                    quotes=quote_str,
                    ai_reasoning=reasoning,
                )
            )
        return atom_rows

    async def export_excel(
        self,
        execution: ExecutionRecord,
        report_dto: ReportDataDTO | None,
        matrices: list[MatrixScorecardRowDTO],
        locale: str = "fi",
        components: list[AnyPromptBlock] | None = None,
        execution_id: str | None = None,
    ) -> ExportPayloadDTO:
        """Generate an Excel export for the execution including Summary and Raw Data tabs.

        Args:
            execution: ExecutionRecord containing evaluation data.
            report_dto: Optional ReportDataDTO containing presentation metrics.
            matrices: List of authoritative MatrixScorecardRowDTO instances to emit 1:1.
            locale: Target localization code ('fi' or 'en').
            components: Optional pre-fetched prompt blocks for rule text resolution.
            execution_id: Optional explicit execution ID for the export filename.

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

        matrix_title_lookup: dict[str, str] = {}
        summary_dtos: list[ExportMatrixSummaryRowDTO] = []
        for m in matrices:
            lbl = m.label_i18n.resolve(target_locale=locale)
            if not lbl:
                lbl = m.name
            matrix_title_lookup[m.block_id] = lbl

            ctx_target = ""
            if m.context_target_label is not None:
                ctx_target = m.context_target_label.resolve(target_locale=locale)
            elif m.context_target:
                ctx_target = m.context_target

            dist = ""
            if m.level_breakdown:
                dist = ", ".join(f"{lvl}: {val}" for lvl, val in m.level_breakdown.items())

            score_str = ""
            if m.score is not None and m.scale_max is not None:
                score_str = f"{m.score} / {m.scale_max}"
            elif m.score is not None:
                score_str = f"{m.score}"

            norm_score: float | str = ""
            if m.normalized_score is not None:
                norm_score = m.normalized_score

            row_expl = ""
            if m.row_explanation:
                row_expl = m.row_explanation

            true_atoms_val = 0
            if m.true_atoms is not None:
                true_atoms_val = m.true_atoms

            total_atoms_val = 0
            if m.total_atoms is not None:
                total_atoms_val = m.total_atoms

            quote_val = ""
            if m.cited_text_quote:
                quote_val = m.cited_text_quote

            source_val = ""
            if m.cited_source_title:
                source_val = m.cited_source_title
            elif m.cited_source_id:
                source_val = m.cited_source_id

            summary_dtos.append(
                ExportMatrixSummaryRowDTO(
                    label=lbl,
                    context_target=ctx_target,
                    distribution=dist,
                    row_explanation=row_expl,
                    criteria=f"{true_atoms_val}/{total_atoms_val}",
                    quotes=quote_val,
                    source=source_val,
                    normalized_score=norm_score,
                    score=score_str,
                )
            )

        tab1_headers = ReportHeaderResolver.get_all_matrix_headers(locale)
        tab1_rows = [
            {
                tab1_headers[ReportMatrixColumn.LABEL]: s.label,
                tab1_headers[ReportMatrixColumn.CONTEXT_TARGET]: s.context_target,
                tab1_headers[ReportMatrixColumn.DISTRIBUTION]: s.distribution,
                tab1_headers[ReportMatrixColumn.ROW_EXPLANATION]: s.row_explanation,
                tab1_headers[ReportMatrixColumn.CRITERIA]: s.criteria,
                tab1_headers[ReportMatrixColumn.QUOTES]: s.quotes,
                tab1_headers[ReportMatrixColumn.SOURCE]: s.source,
                tab1_headers[ReportMatrixColumn.NORMALIZED_SCORE]: s.normalized_score,
                tab1_headers[ReportMatrixColumn.SCORE]: s.score,
            }
            for s in summary_dtos
        ]

        blocks_by_id: dict[str, AnyPromptBlock] = {}
        if components is not None:
            blocks_by_id = {b.id: b for b in components}
        elif self.prompt_block_repo is not None:
            comp_list = await self.prompt_block_repo.get_all_prompt_blocks()
            blocks_by_id = {b.id: b for b in comp_list}

        atom_dtos = self._build_atom_rows(
            report_dto=report_dto,
            matrices=matrices,
            locale=locale,
            blocks_by_id=blocks_by_id,
            matrix_title_lookup=matrix_title_lookup,
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
                atom_headers[ReportAtomColumn.RESULT_STATUS]: a.result_status,
                atom_headers[ReportAtomColumn.QUOTES]: a.quotes,
                atom_headers[ReportAtomColumn.AI_REASONING]: a.ai_reasoning,
            }
            for a in atom_dtos
        ]

        sheet_summary = ReportHeaderResolver.get_sheet_name(ReportSheetKey.SUMMARY, locale)
        sheet_raw_data = ReportHeaderResolver.get_sheet_name(ReportSheetKey.RAW_DATA, locale)

        output = io.BytesIO()
        try:
            import pandas as pd

            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                pd.DataFrame(tab1_rows).to_excel(writer, sheet_name=sheet_summary, index=False)
                pd.DataFrame(tab2_rows).to_excel(writer, sheet_name=sheet_raw_data, index=False)
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
        target_id = execution_id if execution_id is not None else execution.id
        return ExportPayloadDTO(
            content_bytes=output.getvalue(),
            filename=f"execution_export_{target_id}.xlsx",
            mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def export_flat_csv(
        self,
        execution: ExecutionRecord,
        report_dto: ReportDataDTO | None = None,
        matrices: list[MatrixScorecardRowDTO] | None = None,
        locale: str = "fi",
        execution_id: str | None = None,
    ) -> ExportPayloadDTO:
        """Generate a flat tabular CSV export for the execution raw atoms.

        Args:
            execution: ExecutionRecord containing evaluation data.
            report_dto: Optional ReportDataDTO containing presentation metrics.
            matrices: Optional list of authoritative MatrixScorecardRowDTO instances.
            locale: Target localization code ('fi' or 'en').
            execution_id: Optional explicit execution ID for the export filename.

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

        matrix_title_lookup: dict[str, str] = {}
        for m in eval_matrices:
            title = m.label_i18n.resolve(target_locale=locale)
            if not title:
                title = m.name
            matrix_title_lookup[m.block_id] = title

        atom_dtos = self._build_atom_rows(
            report_dto=report_dto,
            matrices=eval_matrices,
            locale=locale,
            blocks_by_id={},
            matrix_title_lookup=matrix_title_lookup,
        )

        atom_headers = ReportHeaderResolver.get_all_atom_headers(locale)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(atom_headers)
        for a in atom_dtos:
            writer.writerow(
                [
                    a.matrix_label,
                    a.context_target,
                    a.level,
                    a.level_name,
                    a.criterion,
                    a.claim_type,
                    a.result_status,
                    a.quotes,
                    a.ai_reasoning,
                ]
            )

        target_id = execution_id if execution_id is not None else execution.id
        return ExportPayloadDTO(
            content_bytes=output.getvalue().encode("utf-8-sig"),
            filename=f"execution_export_{target_id}.csv",
            mime_type="text/csv",
        )
