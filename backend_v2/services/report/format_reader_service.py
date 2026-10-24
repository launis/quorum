"""Report Artifact Format Reader Service managing storage retrieval, byte streaming, and tabular row projection."""

from __future__ import annotations

import logging

from backend_v2.database.interfaces import IUnifiedWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.dtos.report_artifact import ReportRowItemDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import ExecutionStatus, ReportStatus
from backend_v2.services.export_evidence_formatter import format_ai_reasoning
from backend_v2.services.file_driver import FileDriver
from backend_v2.services.storage import get_storage_driver

logger = logging.getLogger(__name__)

__all__ = ["ReportFormatReaderService"]


# Phase 3, Step 1: Extract artifact storage retrieval, byte streaming, and tabular rows parsing into ReportFormatReaderService
class ReportFormatReaderService:
    """Domain service managing report artifact storage retrieval, byte streaming, and tabular row parsing."""

    def __init__(
        self,
        repo: IUnifiedWorkflowRepository,
        storage_driver: FileDriver | None = None,
    ) -> None:
        """Initialize ReportFormatReaderService with repository and storage driver dependencies.

        Args:
            repo: Unified workflow repository for report persistence lookup.
            storage_driver: Optional storage driver for physical file reading.
        """
        self.repo = repo
        self.storage: FileDriver = storage_driver if storage_driver is not None else get_storage_driver()

    async def get_report(self, report_id: str) -> ReportArtifact:
        """Retrieves single report artifact model fail-fast.

        Args:
            report_id: Canonical ID of the report artifact to fetch.

        Returns:
            The fetched ReportArtifact domain model.

        Raises:
            ResourceNotFoundError: If report artifact does not exist in repository.
        """
        report = await self.repo.get_report_artifact(report_id)
        if not report:
            logger.error(
                "[ReportService] %s: Report artifact '%s' not found.",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                report_id,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "report_id": report_id},
            )
            raise ResourceNotFoundError(resource_type="report_artifact", resource_id=report_id)
        return report

    async def _read_artifact(self, report: ReportArtifact, path: str | None, artifact_type: str) -> bytes:
        """Read artifact binary payload from storage driver fail-fast.

        Args:
            report: Target report artifact model.
            path: Relative storage path to artifact file.
            artifact_type: Description of the artifact format (e.g. 'PDF', 'SDUI').

        Returns:
            Raw binary payload of the stored artifact.

        Raises:
            AppException: With ErrorCodes.REPORT_NOT_READY if artifact is not ready,
                or ErrorCodes.STORAGE_ACCESS_FAILED if storage driver read fails.
        """
        if report.status != ReportStatus.READY or not path:
            msg = f"{artifact_type} artifact for report '{report.id}' is not ready (status: {report.status.value})."
            logger.error(
                "[ReportService] %s: %s",
                ErrorCodes.REPORT_NOT_READY.name,
                msg,
                extra={"error_code": ErrorCodes.REPORT_NOT_READY.value, "report_id": report.id},
            )
            raise AppException(message=msg, status_code=409, details={"error_code": ErrorCodes.REPORT_NOT_READY.value})
        try:
            return await self.storage.read(path)
        except (OSError, UnicodeDecodeError, ValueError) as err:
            logger.error(
                "[ReportService] %s: Failed reading %s at %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                artifact_type,
                path,
                err,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "path": path},
            )
            raise AppException(
                message=f"Storage read error: {err}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from err

    async def get_report_sdui(self, report_id: str) -> ReportDataDTO:
        """Streams compiled SDUI ReportDataDTO from storage driver.

        Args:
            report_id: Canonical ID of the report artifact.

        Returns:
            Compiled ReportDataDTO deserialized from storage.

        Raises:
            ResourceNotFoundError: If report artifact does not exist.
            AppException: If report is not ready or storage read fails.
        """
        report = await self.get_report(report_id)
        path = report.storage_paths.sdui_json_path
        raw_bytes = await self._read_artifact(report, path, "SDUI")
        return ReportDataDTO.model_validate_json(raw_bytes.decode("utf-8"))

    async def get_report_pdf_bytes(self, report_id: str) -> tuple[bytes, str]:
        """Streams compiled PDF bytes from storage driver.

        Args:
            report_id: Canonical ID of the report artifact.

        Returns:
            Tuple of (raw PDF bytes, download filename).

        Raises:
            ResourceNotFoundError: If report artifact does not exist.
            AppException: If report is not ready or storage read fails.
        """
        report = await self.get_report(report_id)
        path = report.storage_paths.pdf_path
        return await self._read_artifact(report, path, "PDF"), f"report_{report_id}.pdf"

    async def get_report_excel_bytes(self, report_id: str) -> tuple[bytes, str]:
        """Streams compiled Excel workbook bytes from storage driver.

        Args:
            report_id: Canonical ID of the report artifact.

        Returns:
            Tuple of (raw Excel workbook bytes, download filename).

        Raises:
            ResourceNotFoundError: If report artifact does not exist.
            AppException: If report is not ready or storage read fails.
        """
        report = await self.get_report(report_id)
        path = report.storage_paths.excel_path
        return await self._read_artifact(report, path, "Excel"), f"report_{report_id}.xlsx"

    async def get_report_csv_bytes(self, report_id: str) -> tuple[bytes, str]:
        """Streams compiled flat CSV bytes from storage driver.

        Args:
            report_id: Canonical ID of the report artifact.

        Returns:
            Tuple of (raw CSV bytes, download filename).

        Raises:
            ResourceNotFoundError: If report artifact does not exist.
            AppException: If report is not ready or storage read fails.
        """
        report = await self.get_report(report_id)
        path = report.storage_paths.csv_path
        return await self._read_artifact(report, path, "CSV"), f"report_{report_id}.csv"

    async def get_report_rows(self, report_id: str) -> list[ReportRowItemDTO]:
        """Extracts tabular evaluated metric rows for B2B pipeline integration.

        Args:
            report_id: Canonical ID of the report artifact.

        Returns:
            List of ReportRowItemDTO items for tabular consumption.

        Raises:
            ResourceNotFoundError: If report artifact does not exist.
            AppException: If report is not ready or storage read fails.
        """
        report = await self.get_report(report_id)
        report_dto = await self.get_report_sdui(report_id)
        hydrated_refs = report_dto.hydrated_references

        rows: list[ReportRowItemDTO] = []
        for atom in report_dto.results:
            ref = None
            if atom.tda_id in hydrated_refs:
                ref = hydrated_refs[atom.tda_id]
            label = atom.tda_id
            if ref is not None:
                label = ref.resolved_claim
            score = 0.0
            if atom.status == ExecutionStatus.PASSED:
                score = 1.0
            reasoning_val = format_ai_reasoning(atom.evaluation_reasoning)
            quote_val: str | None = None
            if atom.source_quotes:
                quote_val = " [...] ".join(atom.source_quotes)
            rows.append(
                ReportRowItemDTO(
                    execution_id=report.execution_id,
                    report_id=report_id,
                    metric_key=atom.matrix_id or atom.tda_id,
                    metric_label=label,
                    score=score,
                    max_scale=1.0,
                    weight=1.0,
                    reasoning=reasoning_val,
                    quote=quote_val,
                    is_inverse_evidence=atom.is_inverse_evidence,
                )
            )
        return rows

    def _dlq_log_absent_storage_artifact(self, path: str) -> None:
        """Logs when a storage artifact being deleted is already absent.

        Args:
            path: Storage path of the artifact.
        """
        logger.debug("[ReportService] Storage artifact '%s' already absent during deletion.", path)
