"""Legacy presentation rendering shim for ExecutionService backward compatibility."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from warnings import deprecated

from arq import ArqRedis

from backend_v2.database.interfaces import (
    IComponentRepository,
    IExecutionRepository,
    IIdentityRepository,
    IOutputProfileRepository,
    IPromptBlockRepository,
    ISystemRepository,
    IWorkflowRepository,
)
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.auth import TokenData
from backend_v2.models.domain.execution import ExecutionRecord, ExecutionStep, JobAcceptedDTO
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.render import RenderExecutionResultDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.dtos.trace import ExecutionUpdateDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.view.sdui import AlertBlock, MarkdownBlock, ParagraphBlock, ReportView
from backend_v2.services import blueprint, flattener, pdf_generator, sdui_mapper_service, storage
from backend_v2.services.blueprint import BlueprintTransformer
from backend_v2.services.export_service import ExportService
from backend_v2.services.file_driver import FileDriver

logger = logging.getLogger(__name__)

__all__ = ["ExecutionLegacyRenderService"]


class ExecutionLegacyRenderService:
    """Provides backward-compatible rendering methods for ExecutionService."""

    def __init__(
        self,
        exec_repo: IExecutionRepository,
        workflow_repo: IWorkflowRepository,
        comp_repo: IComponentRepository | None = None,
        prompt_block_repo: IPromptBlockRepository | None = None,
        output_profile_repo: IOutputProfileRepository | None = None,
        identity_repo: IIdentityRepository | None = None,
        system_repo: ISystemRepository | None = None,
        export_service: ExportService | None = None,
        storage_driver: FileDriver | None = None,
        get_execution_fn: Callable[..., Awaitable[ExecutionRecord]] | None = None,
        get_report_dto_fn: Callable[..., Awaitable[ReportDataDTO]] | None = None,
    ) -> None:
        self.exec_repo, self.workflow_repo, self.comp_repo = exec_repo, workflow_repo, comp_repo
        self.prompt_block_repo, self.output_profile_repo = prompt_block_repo, output_profile_repo
        self.identity_repo, self.system_repo = identity_repo, system_repo
        self.export_service = export_service if export_service is not None else ExportService(comp_repo=comp_repo)
        self.storage: FileDriver = storage_driver if storage_driver is not None else storage.get_storage_driver()
        self._get_execution = get_execution_fn or self._default_get_execution
        self._get_report_dto = get_report_dto_fn or self.get_report_dto

    async def _default_get_execution(self, initiator: TokenData, execution_id: str) -> ExecutionRecord:
        record = await self.exec_repo.get_execution(execution_id, hydrate=True)
        if not record:
            raise ResourceNotFoundError(resource_type="execution", resource_id=execution_id)
        return record

    def _transformer(self) -> BlueprintTransformer:
        if (
            self.comp_repo is None
            or self.prompt_block_repo is None
            or self.output_profile_repo is None
            or self.identity_repo is None
            or self.system_repo is None
        ):
            raise AppException("Repositories required for BlueprintTransformer are missing", 500)
        return blueprint.BlueprintTransformer(
            self.exec_repo,
            self.workflow_repo,
            self.comp_repo,
            self.prompt_block_repo,
            self.output_profile_repo,
            self.identity_repo,
            self.system_repo,
        )

    @deprecated("Use ExportService.export_excel directly or ReportService.get_report_excel_bytes.")
    async def get_execution_export_bytes(self, initiator: TokenData, execution_id: str) -> tuple[bytes, str]:
        """Generates an Excel export for the execution including Summary and Raw Data tabs."""
        record = await self._get_execution(initiator=initiator, execution_id=execution_id)
        if record.status != ExecutionStatus.PASSED:
            msg = "Execution must be in PASSED state to generate export."
            logger.error("[LegacyRenderService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        has_atoms = any(s.scorecard_atoms for s in record.step_states.values()) if record.step_states else False
        if not has_atoms:
            msg = "Execution has no scoreable atoms to export."
            logger.error("[LegacyRenderService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        report_dto: ReportDataDTO | None = None
        try:
            report_dto = await self._get_report_dto(initiator, execution_id)
        except Exception as e:
            logger.error("[LegacyRenderService] Could not generate report_dto: %s", e)
            raise AppException(
                f"Report Fetch Error: {e}", 500, {"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
            ) from e

        components = await self.comp_repo.get_all_components("prompt_block") if self.comp_repo else None
        return await self.export_service.export_excel(
            execution=record,
            report_dto=report_dto,
            locale=record.target_locale or "fi",
            components=components,
            execution_id=execution_id,
        )

    async def get_report_dto(
        self,
        initiator: TokenData,
        execution_id: str,
        custom_preface_md: str | None = None,
        local_time_str: str | None = None,
    ) -> ReportDataDTO:
        """Get the headless ReportDataDTO for an execution."""
        record = await self._get_execution(initiator=initiator, execution_id=execution_id)
        if record.status != ExecutionStatus.PASSED:
            msg = f"Execution is not in COMPLETED state. Current status: {record.status.value}"
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return await self._transformer().build_report_dto(
            execution_id,
            profile_id=None,
            accept_language=record.target_locale,
            custom_preface_md=custom_preface_md,
            local_time_str=local_time_str,
        )

    async def get_sdui_view(self, initiator: TokenData, execution_id: str) -> ReportView:
        """Get the SDUI view components for an execution."""
        dto = await self._get_report_dto(initiator, execution_id)
        mapper = sdui_mapper_service.SduiMapperService()
        view = mapper.map_report_to_sdui(dto, execution_id=execution_id)
        title_summary = ""
        if dto.inner_sdui_blocks:
            for block in dto.inner_sdui_blocks:
                match block:
                    case MarkdownBlock(text=txt) | ParagraphBlock(text=txt) | AlertBlock(text=txt) if txt:
                        title_summary += txt + " "
                    case _:
                        pass
        if title_summary:
            view = view.model_copy(update={"title": title_summary.strip()[:100]})
        return view

    async def enqueue_pdf_generation(
        self,
        initiator: TokenData,
        execution_id: str,
        accept_language: str | None,
        profile_id: str,
        arq_pool: ArqRedis,
        custom_preface_md: str | None = None,
        local_time_str: str | None = None,
    ) -> None:
        """Securely enqueue a PDF generation job and inject a Virtual Step into the trace."""
        await self._get_execution(initiator=initiator, execution_id=execution_id)
        v_step_id = f"sys_render_{profile_id}"
        v_step = ExecutionStep(id=v_step_id, label=v_step_id, status=ExecutionStatus.RUNNING)

        exec_local = await self.exec_repo.get_execution(execution_id, hydrate=False)
        if exec_local:
            new_states = dict(exec_local.step_states)
            new_states[v_step_id] = v_step
            new_steps = [s for s in exec_local.steps if s.id != v_step_id] + [v_step]
            await self.exec_repo.update_execution(
                execution_id,
                ExecutionUpdateDTO(status=ExecutionStatus.RUNNING, steps=new_steps, step_states=new_states),
            )

        await arq_pool.enqueue_job(
            "generate_pdf_job",
            execution_id=execution_id,
            accept_language=accept_language,
            profile_id=profile_id,
            custom_preface_md=custom_preface_md,
            local_time_str=local_time_str,
        )

    async def render_execution(
        self,
        initiator: TokenData,
        execution_id: str,
        format_type: str,
        profile_id: str | None,
        accept_language: str | None,
        arq_pool: ArqRedis,
        custom_preface_md: str | None = None,
        local_time_str: str | None = None,
    ) -> RenderExecutionResultDTO:
        """Render an execution record to requested format."""
        record = await self._get_execution(initiator=initiator, execution_id=execution_id)
        if record.status != ExecutionStatus.PASSED:
            msg = f"Execution is not in COMPLETED state. Current status: {record.status.value}"
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        fmt = format_type.lower()
        if fmt not in ("flat", "json", "html", "pdf"):
            raise AppException(
                f"Unsupported format: {format_type}", 400, {"error_code": ErrorCodes.VALIDATION_FAILED.value}
            )

        transformer = self._transformer()

        if fmt == "flat":
            rep_dto = await transformer.build_report_dto(
                execution_id, profile_id, accept_language, custom_preface_md, local_time_str
            )
            flat_rec = flattener.FlatFileService.flatten_results(record, rep_dto)
            return RenderExecutionResultDTO(
                content=flat_rec,
                media_type="application/json",
                filename=None,
            )

        workflow_data = await self.workflow_repo.get_workflow_by_id(record.workflow_id)
        if not workflow_data:
            raise AppException("Workflow not found", 500, {"error_code": ErrorCodes.VALIDATION_FAILED.value})

        workflow_obj = Workflow.model_validate(workflow_data)
        default_pid = workflow_obj.default_profile_id
        resolved_pid = profile_id if profile_id and profile_id != "default" else default_pid

        if resolved_pid not in record.profile_syntheses:
            updated_ts = "0"
            if record.updated_at:
                updated_ts = str(record.updated_at).replace(":", "").replace("-", "").replace(".", "").replace(" ", "_")
            lang_key = accept_language if accept_language else "default"
            job_id = f"render_{execution_id}_{resolved_pid}_{lang_key}_{updated_ts}"
            await arq_pool.enqueue_job(
                "render_profile_job",
                _job_id=job_id,
                execution_id=execution_id,
                profile_id=resolved_pid,
                accept_language=accept_language,
            )
            v_step_id = f"sys_render_{resolved_pid}"
            active_message = (
                record.step_states[v_step_id].label
                if v_step_id in record.step_states
                else "Valmistellaan tulostusta..."
            )
            return RenderExecutionResultDTO(
                content=JobAcceptedDTO(
                    status=ExecutionStatus.PENDING, message=active_message, execution_id=execution_id
                ),
                media_type="application/json",
                filename=None,
            )

        if fmt == "json":
            dto = await self.get_report_dto(
                initiator,
                execution_id,
                custom_preface_md=custom_preface_md,
                local_time_str=local_time_str,
            )
            return RenderExecutionResultDTO(
                content=dto,
                media_type="application/json",
                filename=None,
            )

        target_locale = accept_language if accept_language else record.target_locale
        if not target_locale:
            raise AppException("target_locale missing", 500, {"error_code": ErrorCodes.VALIDATION_FAILED.value})

        storage_drv = storage.get_storage_driver()
        if fmt == "pdf":
            if resolved_pid == default_pid and record.pdf_report_path and not custom_preface_md and not local_time_str:
                try:
                    pdf_bytes = await storage_drv.read(record.pdf_report_path)
                    return RenderExecutionResultDTO(
                        content=pdf_bytes,
                        media_type="application/pdf",
                        filename=f"execution_{execution_id}.pdf",
                    )
                except Exception as strg_err:
                    logger.error("[LegacyRenderService] Storage read failed: %s", strg_err)
                    raise AppException(
                        "Failed to read PDF from storage", 500, {"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
                    ) from strg_err

        rep_dto = await transformer.build_report_dto(
            execution_id, resolved_pid, target_locale, custom_preface_md, local_time_str
        )
        pdf_service = pdf_generator.PdfReportService()

        if fmt == "html":
            html_string = await pdf_service.generate_execution_html(execution_id, rep_dto, target_locale)
            return RenderExecutionResultDTO(
                content=html_string.encode("utf-8"),
                media_type="text/html",
                filename=f"execution_{execution_id}.html",
            )

        if fmt == "pdf":
            pdf_bytes = await pdf_service.generate_execution_pdf(execution_id, rep_dto, target_locale)
            if resolved_pid == default_pid:
                try:
                    output_path_rel = f"executions/{execution_id}/report.pdf"
                    saved_path = await storage_drv.save(output_path_rel, pdf_bytes)
                    if not record.pdf_report_path or record.pdf_report_path != saved_path:
                        await self.exec_repo.update_execution(
                            execution_id, ExecutionUpdateDTO(pdf_report_path=saved_path)
                        )
                except Exception as heal_err:
                    logger.error("[LegacyRenderService] Storage save failed: %s", heal_err)
                    raise AppException(
                        "Failed to save PDF to storage", 500, {"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
                    ) from heal_err

            return RenderExecutionResultDTO(
                content=pdf_bytes,
                media_type="application/pdf",
                filename=f"execution_{execution_id}.pdf",
            )

        raise AppException(
            f"Unsupported format: {format_type}", 400, {"error_code": ErrorCodes.VALIDATION_FAILED.value}
        )
