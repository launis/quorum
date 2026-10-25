"""Canonical package facade for Materialized Report Artifact domain services."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arq.connections import ArqRedis

from backend_v2.database.interfaces import IUnifiedWorkflowRepository
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.dtos.report_artifact import (
    PublicReportDTO,
    ReportArtifactCreateDTO,
    ReportArtifactSummaryDTO,
    ReportRowItemDTO,
)
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.services.export import ExportService
from backend_v2.services.file_driver import FileDriver
from backend_v2.services.pdf_generator import PdfReportService
from backend_v2.services.report.compilation_service import (
    ReportCompilationService as ReportCompilationService,
)
from backend_v2.services.report.format_reader_service import (
    ReportFormatReaderService as ReportFormatReaderService,
)
from backend_v2.services.report.lifecycle_service import (
    ReportLifecycleService as ReportLifecycleService,
)
from backend_v2.services.storage import get_storage_driver

# Phase 4, Step 2: Expose ReportService package aggregator facade with explicit __all__
__all__ = [
    "ReportCompilationService",
    "ReportFormatReaderService",
    "ReportLifecycleService",
    "ReportService",
]


class ReportService:
    """Domain package facade managing materialized report artifacts across all formats."""

    def __init__(
        self,
        repo: IUnifiedWorkflowRepository,
        storage_driver: FileDriver | None = None,
        export_service: ExportService | None = None,
        pdf_service: PdfReportService | None = None,
        synthesis_runner: Callable[..., Awaitable[None]] | None = None,
    ) -> None:
        """Initialize ReportService facade with repository and presentation sub-services.

        Args:
            repo: Unified workflow repository for report persistence.
            storage_driver: Optional storage driver for file storage.
            export_service: Optional export service for data conversion.
            pdf_service: Optional PDF rendering service.
            synthesis_runner: Optional async callable for triggering on-demand text synthesis.
        """
        self.repo = repo
        self.storage: FileDriver = storage_driver if storage_driver is not None else get_storage_driver()
        self.export_service: ExportService = (
            export_service if export_service is not None else ExportService(prompt_block_repo=repo)
        )
        self.pdf_service: PdfReportService = pdf_service if pdf_service is not None else PdfReportService()
        self.synthesis_runner = synthesis_runner
        # Phase 4, Step 2: Route lifecycle, compilation, and format reader sub-services
        self._lifecycle = ReportLifecycleService(repo=self.repo, storage_driver=self.storage)
        self._compilation = ReportCompilationService(
            repo=self.repo,
            storage_driver=self.storage,
            export_service=self.export_service,
            pdf_service=self.pdf_service,
            synthesis_runner=self.synthesis_runner,
        )
        self._format_reader = ReportFormatReaderService(repo=self.repo, storage_driver=self.storage)

    async def get_report(self, report_id: str) -> ReportArtifact:
        """Retrieve single report artifact model fail-fast.

        Args:
            report_id: Canonical ID of the report artifact to fetch.

        Returns:
            Fetched ReportArtifact domain model.

        Raises:
            ResourceNotFoundError: If report artifact does not exist in repository.
        """
        return await self._lifecycle.get_report(report_id)

    async def list_reports_for_execution(self, execution_id: str) -> list[ReportArtifactSummaryDTO]:
        """List all report artifacts for an execution as lightweight summaries.

        Args:
            execution_id: Canonical execution ID to query reports for.

        Returns:
            List of ReportArtifactSummaryDTO objects.
        """
        return await self._lifecycle.list_reports_for_execution(execution_id)

    async def create_report_artifact(self, payload: ReportArtifactCreateDTO) -> ReportArtifact:
        """Validate execution and profile preconditions, then persist a new PENDING report artifact.

        Args:
            payload: Creation DTO containing execution, profile, and locale parameters.

        Returns:
            Newly created and persisted ReportArtifact model.

        Raises:
            ResourceNotFoundError: If execution or profile does not exist.
            ExecutionNotReadyError: If execution is not in PASSED state.
        """
        return await self._lifecycle.create_report_artifact(payload)

    async def get_or_create_default_artifact(
        self,
        execution_id: str,
        profile_id: str | None = None,
        locale: str | None = None,
    ) -> ReportArtifact:
        """Retrieve an existing matching report artifact or create a default pending artifact.

        Args:
            execution_id: Target execution identifier.
            profile_id: Optional output profile identifier.
            locale: Optional target locale code.

        Returns:
            Existing or newly created ReportArtifact model.

        Raises:
            ResourceNotFoundError: If execution or target workflow/profile does not exist.
            AppException: If execution is not ready or profile mismatch occurs.
        """
        return await self._lifecycle.get_or_create_default_artifact(execution_id, profile_id, locale)

    async def compile_and_persist_artifact(
        self, report_id: str, arq_pool: ArqRedis, force_resynthesis: bool = False
    ) -> None:
        """Set status to GENERATING and enqueue background artifact compilation.

        Args:
            report_id: Canonical ID of the report artifact.
            arq_pool: Redis worker connection pool for job enqueuing.
            force_resynthesis: Whether to invalidate synthesis cache and force re-running LLM Phase 2 synthesis.
        """
        await self._compilation.compile_and_persist_artifact(report_id, arq_pool, force_resynthesis=force_resynthesis)

    async def process_artifact_compilation(self, report_id: str, force_resynthesis: bool = False) -> None:
        """Execute Phase 2 synthesis and compile Phase 3 presentation artifacts into storage.

        Args:
            report_id: Canonical ID of the report artifact to compile.
            force_resynthesis: Whether to invalidate synthesis cache and force re-running LLM Phase 2 synthesis.

        Raises:
            ResourceNotFoundError: If report or execution does not exist.
        """
        await self._compilation.process_artifact_compilation(report_id, force_resynthesis=force_resynthesis)

    async def _dispatch_report_compilation_dlq(self, report_id: str, exc: Exception) -> None:
        """Dispatch compilation failure to artifact failure state.

        Args:
            report_id: Canonical ID of the report artifact.
            exc: Caught exception causing the compilation failure.
        """
        await self._compilation._dispatch_report_compilation_dlq(report_id, exc)

    async def _read_artifact(self, report: ReportArtifact, path: str | None, artifact_type: str) -> bytes:
        """Read artifact binary payload from storage driver fail-fast.

        Args:
            report: Target report artifact model.
            path: Relative storage path to artifact file.
            artifact_type: Description of the artifact format.

        Returns:
            Raw binary payload of the stored artifact.

        Raises:
            AppException: With ErrorCodes.REPORT_NOT_READY or ErrorCodes.STORAGE_ACCESS_FAILED.
        """
        return await self._format_reader._read_artifact(report, path, artifact_type)

    async def get_report_sdui(self, report_id: str) -> ReportDataDTO:
        """Stream compiled SDUI ReportDataDTO from storage driver.

        Args:
            report_id: Canonical ID of the report artifact.

        Returns:
            Compiled ReportDataDTO deserialized from storage.

        Raises:
            AppException: If report is not ready or storage read fails.
        """
        return await self._format_reader.get_report_sdui(report_id)

    async def get_report_pdf_bytes(self, report_id: str) -> tuple[bytes, str]:
        """Stream compiled PDF bytes from storage driver.

        Args:
            report_id: Canonical ID of the report artifact.

        Returns:
            Tuple of raw PDF bytes and download filename.

        Raises:
            AppException: If report is not ready or storage read fails.
        """
        return await self._format_reader.get_report_pdf_bytes(report_id)

    async def get_report_excel_bytes(self, report_id: str) -> tuple[bytes, str]:
        """Stream compiled Excel workbook bytes from storage driver.

        Args:
            report_id: Canonical ID of the report artifact.

        Returns:
            Tuple of raw Excel workbook bytes and download filename.

        Raises:
            AppException: If report is not ready or storage read fails.
        """
        return await self._format_reader.get_report_excel_bytes(report_id)

    async def get_report_csv_bytes(self, report_id: str) -> tuple[bytes, str]:
        """Stream compiled flat CSV bytes from storage driver.

        Args:
            report_id: Canonical ID of the report artifact.

        Returns:
            Tuple of raw CSV bytes and download filename.

        Raises:
            AppException: If report is not ready or storage read fails.
        """
        return await self._format_reader.get_report_csv_bytes(report_id)

    async def get_report_rows(self, report_id: str) -> list[ReportRowItemDTO]:
        """Extract tabular evaluated metric rows for B2B pipeline integration.

        Args:
            report_id: Canonical ID of the report artifact.

        Returns:
            List of ReportRowItemDTO items for tabular consumption.
        """
        return await self._format_reader.get_report_rows(report_id)

    def _dlq_log_absent_storage_artifact(self, path: str) -> None:
        """Log when a storage artifact being deleted is already absent.

        Args:
            path: Storage path of the artifact.
        """
        self._format_reader._dlq_log_absent_storage_artifact(path)

    async def delete_report_artifact(self, report_id: str) -> None:
        """Delete database record and associated physical files from storage.

        Args:
            report_id: Canonical ID of the report artifact to delete.

        Raises:
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED if physical file deletion fails.
        """
        await self._lifecycle.delete_report_artifact(report_id)

    async def regenerate_report_artifact(self, report_id: str, arq_pool: ArqRedis) -> None:
        """Reset status to GENERATING and trigger background compilation re-run.

        Args:
            report_id: Canonical ID of the report artifact to regenerate.
            arq_pool: Redis worker connection pool for job enqueuing.
        """
        await self._lifecycle.regenerate_report_artifact(report_id, arq_pool)

    async def get_public_report(self, report_id: str) -> PublicReportDTO:
        """Produce a sanitized public read-only B2B report DTO.

        Args:
            report_id: Canonical ID of the report artifact.

        Returns:
            PublicReportDTO sanitized for external read-only access.

        Raises:
            ResourceNotFoundError: If execution does not exist.
        """
        return await self._lifecycle.get_public_report(report_id)
