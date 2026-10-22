"""CSV flat export service sub-module.

Extracts CSV streaming routines from monolithic ExportService under Epoch 1
(Pure Structural Lift-and-Shift) with zero behavioral changes.
"""

from __future__ import annotations

import csv
import io
import logging
from typing import TYPE_CHECKING

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.prompt_blocks import AnyPromptBlock
from backend_v2.models.dtos.export import ExportPayloadDTO
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.services.export.atom_row_builder import build_denormalized_rows
from backend_v2.services.export.metadata_resolver import extract_causal_result
from backend_v2.services.localization import ReportHeaderResolver

if TYPE_CHECKING:
    from backend_v2.database.interfaces import IPromptBlockRepository

__all__ = ["CsvExporter"]

logger = logging.getLogger(__name__)


class CsvExporter:
    """Service for generating flat 22-column CSV exports from execution records.

    Attributes:
        prompt_block_repo: Optional prompt block repository for resolving block definitions.
    """

    def __init__(self, prompt_block_repo: IPromptBlockRepository | None = None) -> None:
        """Initialize the CSV exporter.

        Args:
            prompt_block_repo: Optional repository for resolving prompt blocks.
        """
        self.prompt_block_repo = prompt_block_repo

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
            AppException: If execution is not in PASSED state or has no scoreable atoms (VALIDATION_FAILED).
        """
        # Phase 3, Step 2: Enforce PASSED state validation
        if execution.status != ExecutionStatus.PASSED:
            msg = "Strict Fail-Fast: Execution must be in PASSED state to export CSV."
            logger.error(
                "[CsvExporter] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        # Phase 3, Step 2: Enforce scoreable atoms validation
        if report_dto is None or not report_dto.results:
            msg = "Strict Fail-Fast: Execution has no scoreable atoms."
            logger.error(
                "[CsvExporter] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        effective_matrices: list[MatrixScorecardRowDTO] = []
        if matrices is not None:
            effective_matrices = matrices
        if all_matrices is not None:
            effective_matrices = all_matrices

        target_id = execution.id
        if execution_id is not None:
            target_id = execution_id

        matrix_title_lookup: dict[str, str] = {}
        for m in effective_matrices:
            title = m.label_i18n.resolve(target_locale=locale)
            matrix_title_lookup[m.block_id] = title

        blocks_by_id: dict[str, AnyPromptBlock] = {}
        if components is not None:
            blocks_by_id = {b.id: b for b in components}
        elif self.prompt_block_repo is not None:
            comp_list = await self.prompt_block_repo.get_all_prompt_blocks()
            blocks_by_id = {b.id: b for b in comp_list}

        causal_result = extract_causal_result(execution)

        # Phase 3, Step 2: Stream rectangular flat rows via atom_row_builder
        flat_dtos = build_denormalized_rows(
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
