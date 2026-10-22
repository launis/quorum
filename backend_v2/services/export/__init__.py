"""Export package facade providing Excel and CSV export capabilities.

Decomposed from monolithic export_service.py into focused sub-modules:
- metadata_resolver: Prompt block metadata, scales, and causal graph extraction.
- excel_styler: Openpyxl styling and corporate theme application.
- summary_builder: 13-column summary row builder for Excel Tab 1.
- atom_row_builder: Tabular atom and denormalized dataset builders.
- excel_exporter: Workbook generation and Excel serialization.
- csv_exporter: Flat CSV tabular streaming.
"""

from __future__ import annotations

import openpyxl

from backend_v2.database.interfaces import IPromptBlockRepository
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.prompt_blocks import AnyPromptBlock
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
from backend_v2.services.export.atom_row_builder import (
    build_atom_rows as build_atom_rows,
)
from backend_v2.services.export.atom_row_builder import (
    build_denormalized_rows as build_denormalized_rows,
)
from backend_v2.services.export.csv_exporter import CsvExporter as CsvExporter
from backend_v2.services.export.excel_exporter import ExcelExporter as ExcelExporter
from backend_v2.services.export.excel_styler import (
    apply_corporate_excel_styling as apply_corporate_excel_styling,
)
from backend_v2.services.export.metadata_resolver import (
    build_matrix_atom_maps as build_matrix_atom_maps,
)
from backend_v2.services.export.metadata_resolver import (
    build_scale_metadata as build_scale_metadata,
)
from backend_v2.services.export.metadata_resolver import (
    extract_causal_result as extract_causal_result,
)
from backend_v2.services.export.metadata_resolver import (
    resolve_causal_meta as resolve_causal_meta,
)
from backend_v2.services.export.metadata_resolver import (
    resolve_context_target as resolve_context_target,
)
from backend_v2.services.export.metadata_resolver import (
    resolve_matrix_label as resolve_matrix_label,
)
from backend_v2.services.export.summary_builder import build_summary_dtos as build_summary_dtos

__all__ = [
    "CsvExporter",
    "ExcelExporter",
    "ExportService",
    "apply_corporate_excel_styling",
    "build_atom_rows",
    "build_denormalized_rows",
    "build_matrix_atom_maps",
    "build_scale_metadata",
    "build_summary_dtos",
    "extract_causal_result",
    "resolve_causal_meta",
    "resolve_context_target",
    "resolve_matrix_label",
]


class ExportService:
    """Domain package facade for generating forensic Excel and flat CSV exports."""

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
        return await ExcelExporter(self.prompt_block_repo).export_excel(
            execution=execution,
            report_dto=report_dto,
            matrices=matrices,
            locale=locale,
            components=components,
            execution_id=execution_id,
            all_matrices=all_matrices,
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
        return await CsvExporter(self.prompt_block_repo).export_flat_csv(
            execution=execution,
            report_dto=report_dto,
            matrices=matrices,
            locale=locale,
            components=components,
            execution_id=execution_id,
            all_matrices=all_matrices,
        )
