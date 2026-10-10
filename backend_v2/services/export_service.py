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
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from backend_v2.database.interfaces import IPromptBlockRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.prompt_blocks import (
    AnyPromptBlock,
    MatrixPromptBlock,
)
from backend_v2.models.dtos.export import (
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
from backend_v2.services.export_evidence_formatter import (
    clean_citation_brackets,
    format_ai_reasoning,
    format_text_observations,
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
        atom_to_matrix: dict[str, MatrixScorecardRowDTO] = {}
        atom_to_scorecard: dict[str, ScorecardAtomDTO] = {}
        for m in effective_matrices:
            for s_atom in m.evaluated_atoms:
                atom_to_matrix[s_atom.atom_id] = m
                atom_to_scorecard[s_atom.atom_id] = s_atom
        return atom_to_matrix, atom_to_scorecard

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
        atom_scale_meta: dict[str, AtomScaleMetadataDTO] = {}
        for b in blocks_by_id.values():
            if isinstance(b, MatrixPromptBlock) and b.scales:
                for scale in b.scales:
                    scale_lvl = scale.score
                    scale_name = scale.ai_label
                    if scale.name is not None:
                        scale_name = scale.name.resolve(target_locale=locale)
                    for claim in scale.claims:
                        claim_desc = claim.label.resolve(target_locale=locale)
                        for tda in claim.tda_assertions:
                            atom_scale_meta[tda.tda_id] = AtomScaleMetadataDTO(
                                matrix_id=b.id,
                                level=scale_lvl,
                                level_name=scale_name,
                                criterion=claim_desc,
                                is_inverse=bool(tda.inverse_evidence),
                            )
        return atom_scale_meta

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
        if atom_matrix_id:
            if atom_matrix_id in matrix_title_lookup:
                return matrix_title_lookup[atom_matrix_id]
            if atom_matrix_id in blocks_by_id:
                return blocks_by_id[atom_matrix_id].label.resolve(target_locale=locale)
            if parent_m is not None:
                lbl = parent_m.label_i18n.resolve(target_locale=locale)
                if lbl:
                    return lbl
                return parent_m.name
        elif parent_m is not None:
            lbl = parent_m.label_i18n.resolve(target_locale=locale)
            if lbl:
                return lbl
            return parent_m.name
        elif tda_id in atom_scale_meta:
            meta = atom_scale_meta[tda_id]
            if meta.matrix_id in matrix_title_lookup:
                return matrix_title_lookup[meta.matrix_id]
            if meta.matrix_id in blocks_by_id:
                return blocks_by_id[meta.matrix_id].label.resolve(target_locale=locale)

        if atom_matrix_id is not None:
            msg = (
                f"Strict Fail-Fast: Matrix block '{atom_matrix_id}' for atom '{tda_id}' "
                "not found in matrices or prompt block repository."
            )
        else:
            msg = (
                f"Strict Fail-Fast: Matrix block for atom '{tda_id}' not found in matrices or prompt block repository."
            )
        logger.error(
            "[ExportService] %s: %s",
            ErrorCodes.RESOURCE_NOT_FOUND.name,
            msg,
            extra={
                "error_code": ErrorCodes.RESOURCE_NOT_FOUND.value,
                "matrix_id": atom_matrix_id,
                "tda_id": tda_id,
            },
        )
        raise AppException(
            message=msg,
            status_code=404,
            details={
                "error_code": ErrorCodes.RESOURCE_NOT_FOUND.value,
                "matrix_id": atom_matrix_id,
                "tda_id": tda_id,
            },
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
        if parent_m is None:
            return ""
        if parent_m.context_target_label is not None:
            return parent_m.context_target_label.resolve(target_locale=locale)
        if parent_m.context_target:
            return parent_m.context_target
        return ""

    @staticmethod
    def _apply_corporate_excel_styling(workbook: openpyxl.Workbook, sheet_names: list[str]) -> None:
        """Applies professional corporate styling across export sheets.

        Args:
            workbook: Active openpyxl Workbook instance.
            sheet_names: List of sheet names to style.
        """
        header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        zebra_fill = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid")
        white_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
        thin_border_side = Side(border_style="thin", color="D9D9D9")
        grid_border = Border(
            left=thin_border_side,
            right=thin_border_side,
            top=thin_border_side,
            bottom=thin_border_side,
        )
        header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        data_alignment = Alignment(vertical="top", wrap_text=True)

        for name in sheet_names:
            if name not in workbook.sheetnames:
                continue
            ws = workbook[name]
            if ws.views.sheetView:
                ws.views.sheetView[0].showGridLines = True
            ws.freeze_panes = "A2"

            ws.row_dimensions[1].height = 28
            for col_idx in range(1, ws.max_column + 1):
                cell = ws.cell(row=1, column=col_idx)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = header_alignment
                cell.border = grid_border

            for row_idx in range(2, ws.max_row + 1):
                fill = white_fill
                if row_idx % 2 == 0:
                    fill = zebra_fill
                for col_idx in range(1, ws.max_column + 1):
                    cell = ws.cell(row=row_idx, column=col_idx)
                    cell.fill = fill
                    cell.border = grid_border
                    cell.alignment = data_alignment

            for col_idx in range(1, ws.max_column + 1):
                col_letter = get_column_letter(col_idx)
                max_len = 0
                for row_idx in range(1, ws.max_row + 1):
                    val = ws.cell(row=row_idx, column=col_idx).value
                    if val is not None:
                        val_str = str(val)
                        line_len = max((len(line) for line in val_str.split("\n")), default=0)
                        max_len = max(max_len, line_len)
                calculated_width = max(max_len + 4, 12)
                ws.column_dimensions[col_letter].width = min(calculated_width, 50)

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
        summary_dtos: list[ExportMatrixSummaryRowDTO] = []
        for m in effective_matrices:
            lbl = m.label_i18n.resolve(target_locale=locale)
            if not lbl:
                lbl = m.name
            ctx_target = self._resolve_context_target(m, locale)
            dist = ""
            if m.level_breakdown:
                dist = ", ".join(f"{lvl}: {val}" for lvl, val in m.level_breakdown.items())

            true_atoms_val = 0
            if m.true_atoms is not None:
                true_atoms_val = m.true_atoms

            total_atoms_val = 0
            if m.total_atoms is not None:
                total_atoms_val = m.total_atoms

            hit_ratio_val = 0.0
            if total_atoms_val > 0:
                hit_ratio_val = float(true_atoms_val / total_atoms_val)

            raw_score_val = 0.0
            if m.raw_score is not None:
                raw_score_val = m.raw_score
            elif m.score is not None:
                raw_score_val = m.score

            scale_max_val = 0.0
            if m.scale_max is not None:
                scale_max_val = m.scale_max

            norm_score_val = 0.0
            if m.normalized_score is not None:
                norm_score_val = m.normalized_score

            row_expl = format_ai_reasoning(m.row_explanation)
            criteria_val = f"{true_atoms_val}/{total_atoms_val}"

            source_val = ""
            if m.cited_source_title:
                source_val = clean_citation_brackets(m.cited_source_title)
            elif m.cited_source_id:
                source_val = clean_citation_brackets(m.cited_source_id)

            summary_dtos.append(
                ExportMatrixSummaryRowDTO(
                    execution_id=target_id,
                    label=lbl,
                    context_target=ctx_target,
                    distribution=dist,
                    hits=true_atoms_val,
                    total_atoms=total_atoms_val,
                    hit_ratio=hit_ratio_val,
                    raw_score=raw_score_val,
                    scale_max=scale_max_val,
                    normalized_score=norm_score_val,
                    row_explanation=row_expl,
                    criteria=criteria_val,
                    source=source_val,
                )
            )
        return summary_dtos

    def _build_atom_rows(
        self,
        report_dto: ReportDataDTO,
        matrices: list[MatrixScorecardRowDTO],
        locale: str,
        blocks_by_id: dict[str, AnyPromptBlock],
        matrix_title_lookup: dict[str, str],
        all_matrices: list[MatrixScorecardRowDTO] | None = None,
    ) -> list[ExportForensicAtomDTO]:
        """Constructs tabular raw data rows containing complete atom details with binary results.

        Args:
            report_dto: ReportDataDTO containing evaluated atom results and references.
            matrices: List of authoritative MatrixScorecardRowDTO instances.
            locale: Target localization code ('fi' or 'en').
            blocks_by_id: Pre-indexed prompt blocks dictionary.
            matrix_title_lookup: Pre-computed matrix titles by block ID.
            all_matrices: Optional comprehensive list of all matrix scorecard rows.

        Returns:
            List of strictly validated ExportForensicAtomDTO instances.

        Raises:
            AppException: If matrix block for an atom is not found in matrices or blocks_by_id.
        """
        effective_matrices = matrices
        if all_matrices is not None:
            effective_matrices = all_matrices

        atom_to_matrix, atom_to_scorecard = self._build_matrix_atom_maps(effective_matrices)
        atom_scale_meta = self._build_scale_metadata(blocks_by_id, locale)

        atom_rows: list[ExportForensicAtomDTO] = []
        hydrated_refs = report_dto.hydrated_references

        for atom in report_dto.results:
            parent_m: MatrixScorecardRowDTO | None = None
            if atom.tda_id in atom_to_matrix:
                parent_m = atom_to_matrix[atom.tda_id]

            matrix_label = self._resolve_matrix_label(
                atom_matrix_id=atom.matrix_id,
                tda_id=atom.tda_id,
                parent_m=parent_m,
                matrix_title_lookup=matrix_title_lookup,
                blocks_by_id=blocks_by_id,
                atom_scale_meta=atom_scale_meta,
                locale=locale,
            )
            context_target = self._resolve_context_target(parent_m, locale)

            scorecard_atom: ScorecardAtomDTO | None = None
            if atom.tda_id in atom_to_scorecard:
                scorecard_atom = atom_to_scorecard[atom.tda_id]

            meta: AtomScaleMetadataDTO | None = None
            if atom.tda_id in atom_scale_meta:
                meta = atom_scale_meta[atom.tda_id]

            level = 0
            level_name = ""
            if scorecard_atom is not None:
                level = scorecard_atom.level
                level_name = scorecard_atom.level_name
            elif meta is not None:
                level = meta.level
                level_name = meta.level_name

            ref = None
            if hydrated_refs and atom.tda_id in hydrated_refs:
                ref = hydrated_refs[atom.tda_id]

            criterion = ""
            if ref is not None and ref.resolved_claim:
                criterion = ref.resolved_claim
            elif scorecard_atom is not None and scorecard_atom.claim_label:
                criterion = scorecard_atom.claim_label
            elif meta is not None:
                criterion = meta.criterion

            is_inverse_claim = False
            if atom.is_inverse_evidence:
                is_inverse_claim = True
            elif meta is not None and meta.is_inverse:
                is_inverse_claim = True

            claim_type = LocalizationService.translate("export_claim_positive", locale)
            if is_inverse_claim:
                claim_type = LocalizationService.translate("export_claim_inverse", locale)

            result_status: int = 0
            if atom.status == ExecutionStatus.PASSED:
                result_status = 1

            quote_raw: list[str] | str | None = atom.source_quote
            if quote_raw is None and ref is not None:
                quote_raw = ref.source_quote
            formatted_quotes = format_text_observations(quote_raw)
            formatted_reasoning = format_ai_reasoning(atom.evaluation_reasoning)

            atom_rows.append(
                ExportForensicAtomDTO(
                    matrix_label=matrix_label,
                    context_target=context_target,
                    level=level,
                    level_name=level_name,
                    criterion=criterion,
                    claim_type=claim_type,
                    result_status=result_status,
                    quotes=formatted_quotes,
                    ai_reasoning=formatted_reasoning,
                )
            )
        return atom_rows

    def _build_denormalized_rows(
        self,
        report_dto: ReportDataDTO,
        matrices: list[MatrixScorecardRowDTO],
        locale: str,
        blocks_by_id: dict[str, AnyPromptBlock],
        matrix_title_lookup: dict[str, str],
        execution_id: str,
        all_matrices: list[MatrixScorecardRowDTO] | None = None,
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

        Returns:
            List of strictly validated ExportDenormalizedFlatRowDTO instances.

        Raises:
            AppException: If matrix block for an atom is not found in matrices or blocks_by_id.
        """
        effective_matrices = matrices
        if all_matrices is not None:
            effective_matrices = all_matrices

        atom_to_matrix, atom_to_scorecard = self._build_matrix_atom_maps(effective_matrices)
        atom_scale_meta = self._build_scale_metadata(blocks_by_id, locale)

        denormalized_rows: list[ExportDenormalizedFlatRowDTO] = []
        hydrated_refs = report_dto.hydrated_references

        for atom in report_dto.results:
            parent_m: MatrixScorecardRowDTO | None = None
            if atom.tda_id in atom_to_matrix:
                parent_m = atom_to_matrix[atom.tda_id]

            matrix_label = self._resolve_matrix_label(
                atom_matrix_id=atom.matrix_id,
                tda_id=atom.tda_id,
                parent_m=parent_m,
                matrix_title_lookup=matrix_title_lookup,
                blocks_by_id=blocks_by_id,
                atom_scale_meta=atom_scale_meta,
                locale=locale,
            )
            context_target = self._resolve_context_target(parent_m, locale)

            dist = ""
            hits_val = 0
            total_atoms_val = 0
            hit_ratio_val = 0.0
            raw_score_val = 0.0
            scale_max_val = 0.0
            normalized_score_val = 0.0

            if parent_m is not None:
                if parent_m.level_breakdown:
                    dist = ", ".join(f"{lvl}: {val}" for lvl, val in parent_m.level_breakdown.items())
                if parent_m.true_atoms is not None:
                    hits_val = parent_m.true_atoms
                if parent_m.total_atoms is not None:
                    total_atoms_val = parent_m.total_atoms
                if total_atoms_val > 0:
                    hit_ratio_val = float(hits_val / total_atoms_val)
                if parent_m.raw_score is not None:
                    raw_score_val = parent_m.raw_score
                elif parent_m.score is not None:
                    raw_score_val = parent_m.score
                if parent_m.scale_max is not None:
                    scale_max_val = parent_m.scale_max
                if parent_m.normalized_score is not None:
                    normalized_score_val = parent_m.normalized_score

            scorecard_atom: ScorecardAtomDTO | None = None
            if atom.tda_id in atom_to_scorecard:
                scorecard_atom = atom_to_scorecard[atom.tda_id]

            meta: AtomScaleMetadataDTO | None = None
            if atom.tda_id in atom_scale_meta:
                meta = atom_scale_meta[atom.tda_id]

            level = 0
            level_name = ""
            if scorecard_atom is not None:
                level = scorecard_atom.level
                level_name = scorecard_atom.level_name
            elif meta is not None:
                level = meta.level
                level_name = meta.level_name

            ref = None
            if hydrated_refs and atom.tda_id in hydrated_refs:
                ref = hydrated_refs[atom.tda_id]

            criterion = ""
            if ref is not None and ref.resolved_claim:
                criterion = ref.resolved_claim
            elif scorecard_atom is not None and scorecard_atom.claim_label:
                criterion = scorecard_atom.claim_label
            elif meta is not None:
                criterion = meta.criterion

            is_inverse_claim = False
            if atom.is_inverse_evidence:
                is_inverse_claim = True
            elif meta is not None and meta.is_inverse:
                is_inverse_claim = True

            claim_type = LocalizationService.translate("export_claim_positive", locale)
            if is_inverse_claim:
                claim_type = LocalizationService.translate("export_claim_inverse", locale)

            result_status: int = 0
            if atom.status == ExecutionStatus.PASSED:
                result_status = 1

            quote_raw: list[str] | str | None = atom.source_quote
            if quote_raw is None and ref is not None:
                quote_raw = ref.source_quote
            formatted_quotes = format_text_observations(quote_raw)
            formatted_reasoning = format_ai_reasoning(atom.evaluation_reasoning)

            denormalized_rows.append(
                ExportDenormalizedFlatRowDTO(
                    execution_id=execution_id,
                    matrix_label=matrix_label,
                    context_target=context_target,
                    distribution=dist,
                    hits=hits_val,
                    total_atoms=total_atoms_val,
                    hit_ratio=hit_ratio_val,
                    raw_score=raw_score_val,
                    scale_max=scale_max_val,
                    normalized_score=normalized_score_val,
                    level=level,
                    level_name=level_name,
                    criterion=criterion,
                    claim_type=claim_type,
                    result_status=result_status,
                    quotes=formatted_quotes,
                    ai_reasoning=formatted_reasoning,
                )
            )
        return denormalized_rows

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

        atom_dtos = self._build_atom_rows(
            report_dto=report_dto,
            matrices=matrices,
            locale=locale,
            blocks_by_id=blocks_by_id,
            matrix_title_lookup=matrix_title_lookup,
            all_matrices=all_matrices,
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
        """Generate a flat tabular CSV export streaming 17 denormalized columns.

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

        flat_dtos = self._build_denormalized_rows(
            report_dto=report_dto,
            matrices=effective_matrices,
            locale=locale,
            blocks_by_id=blocks_by_id,
            matrix_title_lookup=matrix_title_lookup,
            execution_id=target_id,
            all_matrices=all_matrices,
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
                    row.result_status,
                    row.quotes,
                    row.ai_reasoning,
                ]
            )

        return ExportPayloadDTO(
            content_bytes=output.getvalue().encode("utf-8-sig"),
            filename=f"execution_export_{target_id}.csv",
            mime_type="text/csv",
        )
