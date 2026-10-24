"""Materialized Report Artifact domain service coordinates compilation, storage, and retrieval."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arq.connections import ArqRedis

from backend_v2.database.interfaces import IUnifiedWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.dtos.report_artifact import (
    PublicReportDTO,
    ReportArtifactCreateDTO,
    ReportArtifactSummaryDTO,
    ReportRowItemDTO,
)
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import ExecutionStatus, ReportStatus
from backend_v2.services.export import ExportService
from backend_v2.services.export_evidence_formatter import format_ai_reasoning
from backend_v2.services.file_driver import FileDriver
from backend_v2.services.pdf_generator import PdfReportService
from backend_v2.services.report.compilation_service import ReportCompilationService
from backend_v2.services.report.lifecycle_service import ReportLifecycleService
from backend_v2.services.storage import get_storage_driver

logger = logging.getLogger(__name__)

__all__ = ["ReportService"]


class ReportService:
    """Domain service managing materialized report artifacts across all formats."""

    def __init__(
        self,
        repo: IUnifiedWorkflowRepository,
        storage_driver: FileDriver | None = None,
        export_service: ExportService | None = None,
        pdf_service: PdfReportService | None = None,
        synthesis_runner: Callable[..., Awaitable[None]] | None = None,
    ) -> None:
        """Initialize ReportService with repository and presentation services.

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
        # Phase 1, Step 2: Instantiate ReportLifecycleService for CRUD and lifecycle delegation
        self._lifecycle = ReportLifecycleService(repo=self.repo, storage_driver=self.storage)
        # Phase 2, Step 2: Instantiate ReportCompilationService for compilation and DLQ delegation
        self._compilation = ReportCompilationService(
            repo=self.repo,
            storage_driver=self.storage,
            export_service=self.export_service,
            pdf_service=self.pdf_service,
            synthesis_runner=self.synthesis_runner,
        )

    async def get_report(self, report_id: str) -> ReportArtifact:
        """Retrieves single report artifact model fail-fast.

        Args:
            report_id: Canonical ID of the report artifact to fetch.

        Returns:
            The fetched ReportArtifact domain model.

        Raises:
            ResourceNotFoundError: If report artifact does not exist in repository.
        """
        # Phase 1, Step 2: Delegate to ReportLifecycleService
        return await self._lifecycle.get_report(report_id)

    async def list_reports_for_execution(self, execution_id: str) -> list[ReportArtifactSummaryDTO]:
        """Lists all report artifacts for an execution as lightweight summaries.

        Args:
            execution_id: Canonical execution ID to query reports for.

        Returns:
            List of ReportArtifactSummaryDTO objects.
        """
        # Phase 1, Step 2: Delegate to ReportLifecycleService
        return await self._lifecycle.list_reports_for_execution(execution_id)

    async def create_report_artifact(self, payload: ReportArtifactCreateDTO) -> ReportArtifact:
        """Validates execution and profile preconditions, then persists a new PENDING report artifact.

        Args:
            payload: Creation DTO containing execution, profile, and locale parameters.

        Returns:
            The newly created and persisted ReportArtifact model.

        Raises:
            ResourceNotFoundError: If execution or profile does not exist.
            ExecutionNotReadyError: If execution is not in PASSED state.
        """
        # Phase 1, Step 2: Delegate to ReportLifecycleService
        return await self._lifecycle.create_report_artifact(payload)

    async def get_or_create_default_artifact(
        self,
        execution_id: str,
        profile_id: str | None = None,
        locale: str | None = None,
    ) -> ReportArtifact:
        """Retrieves an existing matching report artifact or creates and persists a default pending artifact.

        Args:
            execution_id: Target execution identifier.
            profile_id: Optional output profile identifier.
            locale: Optional target locale code.

        Returns:
            The existing or newly created ReportArtifact model.

        Raises:
            ResourceNotFoundError: If execution or target workflow/profile does not exist.
            AppException: If execution is not ready or profile mismatch occurs.
        """
        # Phase 1, Step 2: Delegate to ReportLifecycleService
        return await self._lifecycle.get_or_create_default_artifact(execution_id, profile_id, locale)

    async def compile_and_persist_artifact(
        self, report_id: str, arq_pool: ArqRedis, force_resynthesis: bool = False
    ) -> None:
        """Sets status to GENERATING and enqueues background artifact compilation.

        Args:
            report_id: Canonical ID of the report artifact.
            arq_pool: Redis worker connection pool for job enqueuing.
            force_resynthesis: Whether to invalidate synthesis cache and force re-running LLM Phase 2 synthesis.
        """
        # Phase 2, Step 2: Delegate to ReportCompilationService
        await self._compilation.compile_and_persist_artifact(report_id, arq_pool, force_resynthesis=force_resynthesis)

    async def process_artifact_compilation(self, report_id: str, force_resynthesis: bool = False) -> None:
        """Executes Phase 2 synthesis and compiles Phase 3 presentation artifacts into storage.

        Args:
            report_id: Canonical ID of the report artifact to compile.
            force_resynthesis: Whether to invalidate synthesis cache and force re-running LLM Phase 2 synthesis.

        Raises:
            ResourceNotFoundError: If report or execution does not exist.
        """
        # Phase 2, Step 2: Delegate to ReportCompilationService
        await self._compilation.process_artifact_compilation(report_id, force_resynthesis=force_resynthesis)

    async def _dispatch_report_compilation_dlq(self, report_id: str, exc: Exception) -> None:
        """Dispatches compilation failure to artifact failure state.

        Args:
            report_id: Canonical ID of the report artifact.
            exc: Caught exception causing the compilation failure.
        """
        # Phase 2, Step 2: Delegate to ReportCompilationService
        await self._compilation._dispatch_report_compilation_dlq(report_id, exc)

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

    async def delete_report_artifact(self, report_id: str) -> None:
        """Deletes database record and associated physical files from storage.

        Args:
            report_id: Canonical ID of the report artifact to delete.

        Raises:
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED if physical file deletion fails.
        """
        # Phase 1, Step 2: Delegate to ReportLifecycleService
        await self._lifecycle.delete_report_artifact(report_id)

    async def regenerate_report_artifact(self, report_id: str, arq_pool: ArqRedis) -> None:
        """Resets status to GENERATING and triggers background compilation re-run.

        Args:
            report_id: Canonical ID of the report artifact to regenerate.
            arq_pool: Redis worker connection pool for job enqueuing.
        """
        # Phase 1, Step 2: Delegate to ReportLifecycleService
        await self._lifecycle.regenerate_report_artifact(report_id, arq_pool)

    async def get_public_report(self, report_id: str) -> PublicReportDTO:
        """Produces a sanitized public read-only B2B report DTO.

        Args:
            report_id: Canonical ID of the report artifact.

        Returns:
            PublicReportDTO sanitized for external read-only access.

        Raises:
            ResourceNotFoundError: If execution does not exist.
        """
        # Phase 1, Step 2: Delegate to ReportLifecycleService
        return await self._lifecycle.get_public_report(report_id)
