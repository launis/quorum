"""Report Artifact Compilation Service managing multi-format synthesis, rendering, and DLQ isolation."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arq.connections import ArqRedis

from backend_v2.database.interfaces import IUnifiedWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes, ExecutionNotReadyError, ResourceNotFoundError
from backend_v2.models.dtos.report_artifact import (
    ReportArtifactUpdateDTO,
    ReportMetadataDTO,
    ReportStoragePathsDTO,
)
from backend_v2.models.dtos.trace import ExecutionUpdateDTO
from backend_v2.models.enums import ExecutionStatus, ReportStatus
from backend_v2.services.blueprint import BlueprintTransformer
from backend_v2.services.export import ExportService
from backend_v2.services.file_driver import FileDriver
from backend_v2.services.localization import set_language
from backend_v2.services.pdf_generator import PdfReportService
from backend_v2.services.storage import get_storage_driver

logger = logging.getLogger(__name__)

__all__ = ["ReportCompilationService"]


# Phase 2, Step 1: Extract compilation and synthesis orchestration into ReportCompilationService
class ReportCompilationService:
    """Domain service orchestrating multi-format report artifact compilation, synthesis, and DLQ handling."""

    def __init__(
        self,
        repo: IUnifiedWorkflowRepository,
        storage_driver: FileDriver | None = None,
        export_service: ExportService | None = None,
        pdf_service: PdfReportService | None = None,
        synthesis_runner: Callable[..., Awaitable[None]] | None = None,
    ) -> None:
        """Initialize ReportCompilationService with repository, storage, export, PDF, and synthesis dependencies.

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

    async def compile_and_persist_artifact(
        self, report_id: str, arq_pool: ArqRedis, force_resynthesis: bool = False
    ) -> None:
        """Sets status to GENERATING and enqueues background artifact compilation.

        Args:
            report_id: Canonical ID of the report artifact.
            arq_pool: Redis worker connection pool for job enqueuing.
            force_resynthesis: Whether to invalidate synthesis cache and force re-running LLM Phase 2 synthesis.

        Raises:
            ResourceNotFoundError: If report artifact does not exist in repository.
            ExecutionNotReadyError: If associated execution record is not in PASSED state.
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

        execution = await self.repo.get_execution(report.execution_id)
        if execution is not None and execution.status != ExecutionStatus.PASSED:
            msg = f"Execution is not in PASSED state. Current status: {execution.status.value}"
            logger.error("[ReportService] %s: %s", ErrorCodes.EXECUTION_NOT_READY.name, msg)
            raise ExecutionNotReadyError(execution_id=execution.id, current_status=execution.status.value)

        job_key = f"compile_report_{report.id}"
        await arq_pool.delete(f"arq:result:{job_key}")
        await self.repo.update_report_artifact(report.id, ReportArtifactUpdateDTO(status=ReportStatus.GENERATING))
        job = await arq_pool.enqueue_job(
            "generate_report_artifact_job",
            report_id=report.id,
            force_resynthesis=force_resynthesis,
            _job_id=job_key,
        )
        if job is None:
            logger.warning(
                "[ReportService] Compilation job '%s' deduplicated by Arq for report '%s'",
                job_key,
                report.id,
                extra={"report_id": report.id, "job_key": job_key},
            )

    async def process_artifact_compilation(self, report_id: str, force_resynthesis: bool = False) -> None:
        """Executes Phase 2 synthesis and compiles Phase 3 presentation artifacts into storage.

        Args:
            report_id: Canonical ID of the report artifact to compile.
            force_resynthesis: Whether to invalidate synthesis cache and force re-running LLM Phase 2 synthesis.

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
        if not force_resynthesis and report.status == ReportStatus.READY and report.storage_paths is not None:
            pdf_path = report.storage_paths.pdf_path
            if pdf_path and await self.storage.exists(pdf_path):
                logger.info(
                    "[ReportService] Report artifact '%s' is already compiled and present in storage. Skipping.",
                    report_id,
                )
                return

        await self.repo.update_report_artifact(report.id, ReportArtifactUpdateDTO(status=ReportStatus.GENERATING))
        try:
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

            set_language(report.locale)

            if force_resynthesis and report.profile_id in execution.profile_syntheses:
                logger.info(
                    "[ReportService] Invalidating cached synthesis for profile '%s' in execution '%s' (force_resynthesis=True).",
                    report.profile_id,
                    execution.id,
                    extra={"profile_id": report.profile_id, "execution_id": execution.id},
                )
                execution = execution.without_profile_synthesis(report.profile_id)
                await self.repo.update_execution(
                    execution.id,
                    ExecutionUpdateDTO(profile_syntheses=execution.profile_syntheses),
                )

            if report.profile_id not in execution.profile_syntheses:
                if self.synthesis_runner is not None:
                    await self.synthesis_runner(
                        execution_id=report.execution_id,
                        accept_language=report.locale,
                        profile_id=report.profile_id,
                    )
                    refreshed = await self.repo.get_execution(report.execution_id)
                    if refreshed:
                        execution = refreshed
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

            all_matrices = (
                transformer.last_all_matrices if transformer.last_all_matrices else transformer.last_evaluative_matrices
            )
            excel_payload = await self.export_service.export_excel(
                execution=execution,
                report_dto=report_dto,
                matrices=all_matrices,
                locale=report.locale,
                execution_id=report.execution_id,
                all_matrices=all_matrices,
            )
            await self.storage.save(excel_path, excel_payload.content_bytes)
            csv_payload = await self.export_service.export_flat_csv(
                execution=execution,
                report_dto=report_dto,
                matrices=all_matrices,
                locale=report.locale,
                execution_id=report.execution_id,
                all_matrices=all_matrices,
            )
            await self.storage.save(csv_path, csv_payload.content_bytes)

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
                exec_obj = exec_refreshed.transition_step(
                    step_id=v_step_id,
                    status=ExecutionStatus.PASSED,
                    progress=100,
                    label="Report Render",
                )
                step_states = exec_obj.step_states
                steps = exec_obj.steps

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
