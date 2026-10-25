"""Report Artifact Lifecycle Service managing CRUD, default resolution, regeneration, and public summaries."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arq.connections import ArqRedis

from backend_v2.database.interfaces import IUnifiedWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes, ExecutionNotReadyError, ResourceNotFoundError
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.dtos.report_artifact import (
    PublicReportDTO,
    ReportArtifactCreateDTO,
    ReportArtifactSummaryDTO,
    ReportArtifactUpdateDTO,
    ReportMetadataDTO,
    ReportStoragePathsDTO,
)
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import EntityPrefix, ExecutionStatus, ReportStatus
from backend_v2.services.file_driver import FileDriver
from backend_v2.services.storage import get_storage_driver

logger = logging.getLogger(__name__)

__all__ = ["ReportLifecycleService"]


class ReportLifecycleService:
    """Domain service managing report artifact CRUD, lifecycle state transitions, and public summaries."""

    def __init__(
        self,
        repo: IUnifiedWorkflowRepository,
        storage_driver: FileDriver | None = None,
    ) -> None:
        """Initialize ReportLifecycleService with repository and storage dependencies.

        Args:
            repo: Unified workflow repository for report persistence.
            storage_driver: Optional storage driver for file storage.
        """
        self.repo = repo
        self.storage: FileDriver = storage_driver if storage_driver is not None else get_storage_driver()

    async def get_report(self, report_id: str) -> ReportArtifact:
        """Retrieve a single report artifact model fail-fast.

        Args:
            report_id: Canonical ID of the report artifact to fetch.

        Returns:
            The fetched ReportArtifact domain model.

        Raises:
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if report artifact does not exist in repository.
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

    async def list_reports_for_execution(self, execution_id: str) -> list[ReportArtifactSummaryDTO]:
        """List all report artifacts for an execution as lightweight summaries.

        Args:
            execution_id: Canonical execution ID to query reports for.

        Returns:
            List of ReportArtifactSummaryDTO objects.
        """
        reports = await self.repo.list_report_artifacts_by_execution(execution_id)
        return [
            ReportArtifactSummaryDTO(
                id=r.id,
                execution_id=r.execution_id,
                profile_id=r.profile_id,
                locale=r.locale,
                title=r.title,
                status=r.status,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
            for r in reports
        ]

    async def _get_validated_profile(self, execution: ExecutionRecord, profile_id: str) -> OutputProfile:
        """Fetch output profile and verify it belongs to the execution workflow.

        Args:
            execution: Validated ExecutionRecord instance.
            profile_id: Target output profile identifier.

        Returns:
            Validated OutputProfile domain model.

        Raises:
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if output profile does not exist.
            AppException: With ErrorCodes.VALIDATION_FAILED if output profile does not belong to execution workflow.
        """
        profile = await self.repo.get_output_profile_by_id(profile_id)
        if not profile:
            logger.error(
                "[ReportService] %s: Output profile '%s' not found.",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                profile_id,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "profile_id": profile_id},
            )
            raise ResourceNotFoundError(resource_type="output_profile", resource_id=profile_id)
        if profile.workflow_id != execution.workflow_id:
            logger.error(
                "[ReportService] %s: Profile '%s' belongs to workflow '%s', not execution workflow '%s'.",
                ErrorCodes.VALIDATION_FAILED.name,
                profile_id,
                profile.workflow_id,
                execution.workflow_id,
                extra={
                    "error_code": ErrorCodes.VALIDATION_FAILED.value,
                    "profile_id": profile_id,
                    "workflow_id": execution.workflow_id,
                },
            )
            raise AppException(
                message=f"Output profile '{profile_id}' does not belong to workflow '{execution.workflow_id}'.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        return profile

    async def create_report_artifact(self, payload: ReportArtifactCreateDTO) -> ReportArtifact:
        """Validate execution and profile preconditions, then persist a new PENDING report artifact.

        Args:
            payload: Creation DTO containing execution, profile, and locale parameters.

        Returns:
            The newly created and persisted ReportArtifact model.

        Raises:
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if execution or profile does not exist.
            ExecutionNotReadyError: With ErrorCodes.EXECUTION_NOT_READY if execution is not in PASSED state.
            AppException: With ErrorCodes.VALIDATION_FAILED if output profile does not belong to execution workflow.
        """
        execution = await self.repo.get_execution(payload.execution_id)
        if not execution:
            logger.error(
                "[ReportService] %s: Execution '%s' not found.",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                payload.execution_id,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "execution_id": payload.execution_id},
            )
            raise ResourceNotFoundError(resource_type="execution", resource_id=payload.execution_id)

        if execution.status != ExecutionStatus.PASSED:
            msg = f"Execution is not in PASSED state. Current status: {execution.status.value}"
            logger.error(
                "[ReportService] %s: %s",
                ErrorCodes.EXECUTION_NOT_READY.name,
                msg,
                extra={
                    "error_code": ErrorCodes.EXECUTION_NOT_READY.value,
                    "execution_id": execution.id,
                    "current_status": execution.status.value,
                },
            )
            raise ExecutionNotReadyError(execution_id=execution.id, current_status=execution.status.value)

        profile = await self._get_validated_profile(execution=execution, profile_id=payload.profile_id)
        report_id = generate_opaque_id(EntityPrefix.REPORT)
        resolved_title = profile.name.resolve(payload.locale)
        now = datetime.now(UTC)

        report = ReportArtifact(
            id=report_id,
            execution_id=payload.execution_id,
            workflow_id=execution.workflow_id,
            profile_id=payload.profile_id,
            locale=payload.locale,
            title=resolved_title,
            status=ReportStatus.PENDING,
            storage_paths=ReportStoragePathsDTO(),
            metadata=ReportMetadataDTO(),
            custom_preface_md=payload.custom_preface_md,
            created_at=now,
            updated_at=now,
        )
        return await self.repo.create_report_artifact(report)

    async def _resolve_default_profile_id(self, execution: ExecutionRecord) -> str:
        """Resolve default output profile ID from execution or parent workflow configuration.

        Args:
            execution: Target ExecutionRecord instance.

        Returns:
            Resolved canonical output profile ID.

        Raises:
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if workflow or matching output profile is missing.
        """
        if execution.output_profile_id:
            return execution.output_profile_id
        if execution.active_profile_id:
            return execution.active_profile_id

        workflow = await self.repo.get_workflow(execution.workflow_id)
        if not workflow:
            logger.error(
                "[ReportService] %s: Workflow '%s' not found for execution '%s'.",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                execution.workflow_id,
                execution.id,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "workflow_id": execution.workflow_id},
            )
            raise ResourceNotFoundError(resource_type="workflow", resource_id=execution.workflow_id)
        if workflow.default_profile_id:
            return workflow.default_profile_id

        all_profiles = await self.repo.get_all_output_profiles()
        matching_profiles = [p for p in all_profiles if p.workflow_id == execution.workflow_id]
        if not matching_profiles:
            logger.error(
                "[ReportService] %s: No output profiles found for workflow '%s'.",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                execution.workflow_id,
                extra={
                    "error_code": ErrorCodes.RESOURCE_NOT_FOUND.value,
                    "workflow_id": execution.workflow_id,
                },
            )
            raise ResourceNotFoundError(resource_type="output_profile", resource_id=execution.workflow_id)
        return matching_profiles[0].id

    async def get_or_create_default_artifact(
        self,
        execution_id: str,
        profile_id: str | None = None,
        locale: str | None = None,
    ) -> ReportArtifact:
        """Retrieve an existing matching report artifact or create and persist a default pending artifact.

        Args:
            execution_id: Target execution identifier.
            profile_id: Optional output profile identifier.
            locale: Optional target locale code.

        Returns:
            The existing or newly created ReportArtifact model.

        Raises:
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if execution, workflow, or profile does not exist.
            ExecutionNotReadyError: With ErrorCodes.EXECUTION_NOT_READY if execution is not in PASSED state.
            AppException: With ErrorCodes.VALIDATION_FAILED if output profile does not belong to execution workflow.
        """
        execution = await self.repo.get_execution(execution_id)
        if not execution:
            logger.error(
                "[ReportService] %s: Execution '%s' not found.",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                execution_id,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "execution_id": execution_id},
            )
            raise ResourceNotFoundError(resource_type="execution", resource_id=execution_id)

        resolved_locale = locale.strip() if locale and locale.strip() else execution.target_locale
        target_profile_id = profile_id if profile_id else await self._resolve_default_profile_id(execution)

        existing_reports = await self.repo.list_report_artifacts_by_execution(execution_id)
        for r in existing_reports:
            if r.profile_id == target_profile_id and r.locale == resolved_locale:
                return r

        create_dto = ReportArtifactCreateDTO(
            execution_id=execution_id,
            profile_id=target_profile_id,
            locale=resolved_locale,
        )
        return await self.create_report_artifact(create_dto)

    def _dlq_log_absent_storage_artifact(self, path: str) -> None:
        """Log when a storage artifact being deleted is already absent.

        Args:
            path: Storage path of the artifact.
        """
        logger.debug("[ReportService] Storage artifact '%s' already absent during deletion.", path)

    async def delete_report_artifact(self, report_id: str) -> None:
        """Delete database record and associated physical files from storage.

        Args:
            report_id: Canonical ID of the report artifact to delete.

        Raises:
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if report artifact does not exist.
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED if physical file deletion fails.
        """
        report = await self.get_report(report_id)
        if report.storage_paths:
            paths = (
                report.storage_paths.pdf_path,
                report.storage_paths.sdui_json_path,
                report.storage_paths.excel_path,
                report.storage_paths.csv_path,
            )
            for p in paths:
                if p:
                    try:
                        await self.storage.delete(p)
                    except FileNotFoundError:
                        self._dlq_log_absent_storage_artifact(p)
                    except OSError as err:
                        msg = f"Failed deleting storage artifact '{p}' for report '{report_id}': {err}"
                        logger.error(
                            "[ReportService] %s: %s",
                            ErrorCodes.STORAGE_ACCESS_FAILED.name,
                            msg,
                            extra={
                                "error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value,
                                "report_id": report_id,
                                "path": p,
                            },
                            exc_info=True,
                        )
                        raise AppException(
                            message=msg,
                            status_code=500,
                            details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "report_id": report_id},
                        ) from err
        await self.repo.delete_report_artifact(report_id)

    async def regenerate_report_artifact(self, report_id: str, arq_pool: ArqRedis) -> None:
        """Reset status to GENERATING and trigger background compilation re-run.

        Args:
            report_id: Canonical ID of the report artifact to regenerate.
            arq_pool: Redis worker connection pool for job enqueuing.

        Raises:
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if report artifact does not exist in repository.
        """
        report = await self.get_report(report_id)
        job_key = f"compile_report_{report.id}"
        await arq_pool.delete(f"arq:result:{job_key}")
        await self.repo.update_report_artifact(report.id, ReportArtifactUpdateDTO(status=ReportStatus.GENERATING))
        job = await arq_pool.enqueue_job(
            "generate_report_artifact_job",
            report_id=report.id,
            force_resynthesis=True,
            _job_id=job_key,
        )
        if job is None:
            logger.warning(
                "[ReportService] Compilation job '%s' deduplicated by Arq for report '%s'",
                job_key,
                report.id,
                extra={"report_id": report.id, "job_key": job_key},
            )

    async def _read_sdui_artifact(self, report: ReportArtifact) -> ReportDataDTO:
        """Read and deserialize compiled SDUI ReportDataDTO from storage driver.

        Args:
            report: Target ReportArtifact domain model.

        Returns:
            Hydrated ReportDataDTO instance.

        Raises:
            AppException: With ErrorCodes.REPORT_NOT_READY if report is not ready, or ErrorCodes.STORAGE_ACCESS_FAILED if storage read fails.
        """
        path = report.storage_paths.sdui_json_path
        if report.status != ReportStatus.READY or not path:
            msg = f"SDUI artifact for report '{report.id}' is not ready (status: {report.status.value})."
            logger.error(
                "[ReportService] %s: %s",
                ErrorCodes.REPORT_NOT_READY.name,
                msg,
                extra={"error_code": ErrorCodes.REPORT_NOT_READY.value, "report_id": report.id},
            )
            raise AppException(message=msg, status_code=409, details={"error_code": ErrorCodes.REPORT_NOT_READY.value})
        try:
            raw_bytes = await self.storage.read(path)
        except (OSError, UnicodeDecodeError, ValueError) as err:
            logger.error(
                "[ReportService] %s: Failed reading SDUI at %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                path,
                err,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "path": path},
                exc_info=True,
            )
            raise AppException(
                message=f"Storage read error: {err}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from err
        return ReportDataDTO.model_validate_json(raw_bytes.decode("utf-8"))

    async def get_public_report(self, report_id: str) -> PublicReportDTO:
        """Produce a sanitized public read-only B2B report DTO.

        Args:
            report_id: Canonical ID of the report artifact.

        Returns:
            PublicReportDTO sanitized for external read-only access.

        Raises:
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if report or execution does not exist.
            AppException: With ErrorCodes.REPORT_NOT_READY or ErrorCodes.STORAGE_ACCESS_FAILED if SDUI report artifact is not ready or cannot be read.
        """
        report = await self.get_report(report_id)
        execution = await self.repo.get_execution(report.execution_id)
        if not execution:
            logger.error(
                "[ReportService] %s: Execution '%s' not found for report '%s'.",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                report.execution_id,
                report_id,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "execution_id": report.execution_id},
            )
            raise ResourceNotFoundError(resource_type="execution", resource_id=report.execution_id)

        report_dto = await self._read_sdui_artifact(report)
        hydrated_refs = report_dto.hydrated_references
        metrics: dict[str, float] = {}
        for atom in report_dto.results:
            metric_label = atom.tda_id
            if atom.tda_id in hydrated_refs:
                metric_label = hydrated_refs[atom.tda_id].resolved_claim
            status_val = 1.0 if atom.status == ExecutionStatus.PASSED else 0.0
            metrics[metric_label] = status_val
        summary_md: str | None = None
        if report.profile_id in execution.profile_syntheses:
            synth = execution.profile_syntheses[report.profile_id]
            summary_md = (
                synth.variance_explanation if synth.variance_explanation is not None else synth.authenticity_explanation
            )

        downloads = {fmt: f"/api/v2/reports/{report.id}/{fmt}" for fmt in ("pdf", "excel", "csv", "sdui")}
        return PublicReportDTO(
            report_id=report.id,
            created_at=report.created_at,
            title=report.title,
            target_audience="stakeholder",
            overall_score=report_dto.global_score,
            metrics=metrics,
            executive_summary_markdown=summary_md,
            downloads=downloads,
        )
