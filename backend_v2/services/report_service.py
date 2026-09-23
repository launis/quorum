"""Materialized Report Artifact domain service coordinates compilation, storage, and retrieval."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arq.connections import ArqRedis

from backend_v2.database.interfaces import IUnifiedWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes, ExecutionNotReadyError, ResourceNotFoundError
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.domain.execution import ExecutionRecord, ExecutionStep
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.report_artifact import (
    PublicReportDTO,
    ReportArtifactCreateDTO,
    ReportArtifactSummaryDTO,
    ReportArtifactUpdateDTO,
    ReportMetadataDTO,
    ReportRowItemDTO,
    ReportStoragePathsDTO,
)
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.dtos.trace import ExecutionUpdateDTO
from backend_v2.models.enums import EntityPrefix, ExecutionStatus, ReportStatus
from backend_v2.services.blueprint import BlueprintTransformer
from backend_v2.services.export_service import ExportService
from backend_v2.services.file_driver import FileDriver
from backend_v2.services.localization import set_language
from backend_v2.services.pdf_generator import PdfReportService
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
            export_service if export_service is not None else ExportService(comp_repo=repo)
        )
        self.pdf_service: PdfReportService = pdf_service if pdf_service is not None else PdfReportService()
        self.synthesis_runner = synthesis_runner

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

    async def list_reports_for_execution(self, execution_id: str) -> list[ReportArtifactSummaryDTO]:
        """Lists all report artifacts for an execution as lightweight summaries.

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
        exec_dict = await self.repo.get_execution(payload.execution_id)
        if not exec_dict:
            logger.error(
                "[ReportService] %s: Execution '%s' not found.",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                payload.execution_id,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "execution_id": payload.execution_id},
            )
            raise ResourceNotFoundError(resource_type="execution", resource_id=payload.execution_id)

        execution = ExecutionRecord.model_validate(exec_dict, strict=False)
        if execution.status != ExecutionStatus.PASSED:
            msg = f"Execution is not in PASSED state. Current status: {execution.status.value}"
            logger.error("[ReportService] %s: %s", ErrorCodes.EXECUTION_NOT_READY.name, msg)
            raise ExecutionNotReadyError(execution_id=execution.id, current_status=execution.status.value)

        profile_dict = await self.repo.get_output_profile_by_id(payload.profile_id)
        if not profile_dict:
            logger.error(
                "[ReportService] %s: Output profile '%s' not found.",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                payload.profile_id,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "profile_id": payload.profile_id},
            )
            raise ResourceNotFoundError(resource_type="output_profile", resource_id=payload.profile_id)

        profile = OutputProfile.model_validate(profile_dict, strict=False)
        if profile.workflow_id != execution.workflow_id:
            logger.error(
                "[ReportService] %s: Profile '%s' belongs to workflow '%s', not execution workflow '%s'.",
                ErrorCodes.VALIDATION_FAILED.name,
                payload.profile_id,
                profile.workflow_id,
                execution.workflow_id,
                extra={
                    "error_code": ErrorCodes.VALIDATION_FAILED.value,
                    "profile_id": payload.profile_id,
                    "workflow_id": execution.workflow_id,
                },
            )
            raise AppException(
                message=f"Output profile '{payload.profile_id}' does not belong to workflow '{execution.workflow_id}'.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        report_id = generate_opaque_id(EntityPrefix.REPORT)
        resolved_title = profile.name.resolve(payload.locale)
        now = datetime.now(timezone.utc)

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
        exec_dict = await self.repo.get_execution(execution_id)
        if not exec_dict:
            logger.error(
                "[ReportService] %s: Execution '%s' not found.",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                execution_id,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "execution_id": execution_id},
            )
            raise ResourceNotFoundError(resource_type="execution", resource_id=execution_id)

        execution = ExecutionRecord.model_validate(exec_dict, strict=False)
        resolved_locale = locale.strip() if locale and locale.strip() else execution.target_locale

        target_profile_id: str | None = profile_id
        if not target_profile_id:
            if execution.output_profile_id:
                target_profile_id = execution.output_profile_id
            elif execution.active_profile_id:
                target_profile_id = execution.active_profile_id
            else:
                wf_dict = await self.repo.get_workflow(execution.workflow_id)
                if not wf_dict:
                    logger.error(
                        "[ReportService] %s: Workflow '%s' not found for execution '%s'.",
                        ErrorCodes.RESOURCE_NOT_FOUND.name,
                        execution.workflow_id,
                        execution_id,
                        extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "workflow_id": execution.workflow_id},
                    )
                    raise ResourceNotFoundError(resource_type="workflow", resource_id=execution.workflow_id)
                workflow = Workflow.model_validate(wf_dict, strict=False)
                if workflow.default_profile_id:
                    target_profile_id = workflow.default_profile_id
                else:
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
                    target_profile_id = matching_profiles[0].id

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

    async def compile_and_persist_artifact(self, report_id: str, arq_pool: ArqRedis) -> None:
        """Sets status to GENERATING and enqueues background artifact compilation.

        Args:
            report_id: Canonical ID of the report artifact.
            arq_pool: Redis worker connection pool for job enqueuing.
        """
        report = await self.get_report(report_id)
        job_key = f"compile_report_{report.id}"
        await arq_pool.delete(f"arq:result:{job_key}")
        await self.repo.update_report_artifact(report.id, ReportArtifactUpdateDTO(status=ReportStatus.GENERATING))
        job = await arq_pool.enqueue_job("generate_report_artifact_job", report_id=report.id, _job_id=job_key)
        if job is None:
            logger.warning(
                "[ReportService] Compilation job '%s' deduplicated by Arq for report '%s'",
                job_key,
                report.id,
                extra={"report_id": report.id, "job_key": job_key},
            )

    async def process_artifact_compilation(self, report_id: str) -> None:
        """Executes Phase 2 synthesis and compiles Phase 3 presentation artifacts into storage.

        Args:
            report_id: Canonical ID of the report artifact to compile.

        Raises:
            ResourceNotFoundError: If report or execution does not exist.
        """
        report = await self.repo.get_report_artifact(report_id)
        if not report:
            logger.error(
                "[ReportService] %s: Report '%s' not found for compilation.",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                report_id,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "report_id": report_id},
            )
            raise ResourceNotFoundError(resource_type="report_artifact", resource_id=report_id)

        # Idempotency check: If already ready and files exist, skip redundant compilation
        if report.status == ReportStatus.READY and report.storage_paths is not None:
            pdf_path = report.storage_paths.pdf_path
            if pdf_path and await self.storage.exists(pdf_path):
                logger.info(
                    "[ReportService] Report artifact '%s' is already compiled and present in storage. Skipping.",
                    report_id,
                )
                return

        await self.repo.update_report_artifact(report.id, ReportArtifactUpdateDTO(status=ReportStatus.GENERATING))
        try:
            exec_dict = await self.repo.get_execution(report.execution_id)
            if not exec_dict:
                logger.error(
                    "[ReportService] %s: Execution '%s' not found for report '%s'.",
                    ErrorCodes.RESOURCE_NOT_FOUND.name,
                    report.execution_id,
                    report_id,
                    extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "execution_id": report.execution_id},
                )
                raise ResourceNotFoundError(resource_type="execution", resource_id=report.execution_id)

            execution = ExecutionRecord.model_validate(exec_dict, strict=False)
            set_language(report.locale)

            if report.profile_id not in execution.profile_syntheses:
                if self.synthesis_runner is not None:
                    await self.synthesis_runner(
                        execution_id=report.execution_id,
                        accept_language=report.locale,
                        profile_id=report.profile_id,
                    )
                    refreshed = await self.repo.get_execution(report.execution_id)
                    if refreshed:
                        execution = ExecutionRecord.model_validate(refreshed, strict=False)
                else:
                    msg = (
                        f"Profile '{report.profile_id}' has not been synthesized for execution '{report.execution_id}'."
                    )
                    logger.error(
                        "[ReportService] %s: %s",
                        ErrorCodes.VALIDATION_FAILED.name,
                        msg,
                        extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )
                    raise AppException(
                        message=msg,
                        status_code=400,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )

            transformer = BlueprintTransformer(
                self.repo, self.repo, self.repo, self.repo, self.repo, self.repo, self.repo
            )
            report_dto = await transformer.build_report_dto(
                report.execution_id, report.profile_id, report.locale, report.custom_preface_md
            )

            sdui_path = f"artifacts/reports/{report_id}/report.sdui.json"
            pdf_path = f"artifacts/reports/{report_id}/report.pdf"
            excel_path, csv_path = (
                f"artifacts/reports/{report_id}/report.xlsx",
                f"artifacts/reports/{report_id}/report.csv",
            )

            await self.storage.save(sdui_path, report_dto.model_dump_json())
            pdf_bytes = await self.pdf_service.generate_execution_pdf(
                report.execution_id, report_dto=report_dto, locale=report.locale
            )
            await self.storage.save(pdf_path, pdf_bytes)

            excel_bytes, _ = await self.export_service.export_excel(
                execution=execution, report_dto=report_dto, locale=report.locale, execution_id=report.execution_id
            )
            await self.storage.save(excel_path, excel_bytes)
            csv_bytes, _ = self.export_service.export_flat_csv(
                execution=execution, report_dto=report_dto, execution_id=report.execution_id
            )
            await self.storage.save(csv_path, csv_bytes)

            paths = ReportStoragePathsDTO(
                pdf_path=pdf_path, sdui_json_path=sdui_path, excel_path=excel_path, csv_path=csv_path
            )
            total_tok = execution.prompt_tokens + execution.completion_tokens + execution.cumulative_synthesis_tokens
            prov = None
            if execution.metadata is not None and execution.metadata.provider_override is not None:
                prov = execution.metadata.provider_override.value
            model_reg_id = None
            if execution.metadata is not None:
                model_reg_id = execution.metadata.model_registry_id
            meta = ReportMetadataDTO(
                cost_usd=execution.dag_cost_usd + execution.cumulative_synthesis_cost,
                duration_ms=execution.duration_ms,
                tokens_used=total_tok,
                llm_model=None,
                provider=prov,
                model_registry_id=model_reg_id,
            )
            await self.repo.update_report_artifact(
                report_id,
                ReportArtifactUpdateDTO(status=ReportStatus.READY, storage_paths=paths, metadata=meta),
            )

            v_step_id = f"sys_render_{report.profile_id}"
            exec_refreshed = await self.repo.get_execution(report.execution_id, hydrate=False)
            step_states = None
            steps = None
            if exec_refreshed:
                exec_obj = ExecutionRecord.model_validate(exec_refreshed, strict=False)
                new_states = dict(exec_obj.step_states)
                if v_step_id in new_states:
                    old_step = new_states[v_step_id]
                    new_states[v_step_id] = old_step.model_copy(
                        update={"status": ExecutionStatus.PASSED, "progress": 100}
                    )
                else:
                    new_states[v_step_id] = ExecutionStep(
                        id=v_step_id,
                        label="Report Render",
                        status=ExecutionStatus.PASSED,
                        progress=100,
                        has_warning=False,
                    )
                new_steps = [
                    s.model_copy(update={"status": ExecutionStatus.PASSED, "progress": 100}) if s.id == v_step_id else s
                    for s in exec_obj.steps
                ]
                if not any(s.id == v_step_id for s in exec_obj.steps):
                    new_steps.append(new_states[v_step_id])
                step_states = new_states
                steps = new_steps

            await self.repo.update_execution(
                report.execution_id,
                ExecutionUpdateDTO(
                    pdf_report_path=pdf_path,
                    steps=steps,
                    step_states=step_states,
                ),
            )
            logger.info("[ReportService] Successfully compiled report artifact: %s", report_id)
        except Exception as exc:
            await self._dispatch_report_compilation_dlq(report_id, exc)

    async def _dispatch_report_compilation_dlq(self, report_id: str, exc: Exception) -> None:
        """Dispatches compilation failure to artifact failure state.

        Args:
            report_id: Canonical ID of the report artifact.
            exc: Caught exception causing the compilation failure.
        """
        msg = f"Artifact compilation failed for report {report_id}: {exc}"
        logger.error(
            "[ReportService] %s: %s",
            ErrorCodes.INTERNAL_SERVER_ERROR.name,
            msg,
            exc_info=True,
            extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value, "report_id": report_id},
        )
        await self.repo.update_report_artifact(
            report_id,
            ReportArtifactUpdateDTO(status=ReportStatus.FAILED, error_message=str(exc)),
        )

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
            rows.append(
                ReportRowItemDTO(
                    execution_id=report.execution_id,
                    report_id=report_id,
                    metric_key=atom.matrix_id or atom.tda_id,
                    metric_label=label,
                    score=score,
                    max_scale=1.0,
                    weight=1.0,
                    reasoning=atom.evaluation_reasoning,
                    quote=atom.source_quote,
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
                            extra={"report_id": report_id, "path": p},
                            exc_info=True,
                        )
                        raise AppException(
                            message=msg,
                            status_code=500,
                            details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "report_id": report_id},
                        ) from err
        await self.repo.delete_report_artifact(report_id)

    async def regenerate_report_artifact(self, report_id: str, arq_pool: ArqRedis) -> None:
        """Resets status to GENERATING and triggers background compilation re-run.

        Args:
            report_id: Canonical ID of the report artifact to regenerate.
            arq_pool: Redis worker connection pool for job enqueuing.
        """
        await self.compile_and_persist_artifact(report_id, arq_pool)

    async def get_public_report(self, report_id: str) -> PublicReportDTO:
        """Produces a sanitized public read-only B2B report DTO.

        Args:
            report_id: Canonical ID of the report artifact.

        Returns:
            PublicReportDTO sanitized for external read-only access.

        Raises:
            ResourceNotFoundError: If execution does not exist.
        """
        report = await self.get_report(report_id)
        exec_dict = await self.repo.get_execution(report.execution_id)
        if not exec_dict:
            logger.error(
                "[ReportService] %s: Execution '%s' not found for report '%s'.",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                report.execution_id,
                report_id,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "execution_id": report.execution_id},
            )
            raise ResourceNotFoundError(resource_type="execution", resource_id=report.execution_id)

        execution = ExecutionRecord.model_validate(exec_dict, strict=False)
        report_dto = await self.get_report_sdui(report_id)
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
            summary_md = synth.variance_explanation or synth.authenticity_explanation

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
