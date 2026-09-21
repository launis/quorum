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
        """Initialize ExecutionLegacyRenderService with repositories and delegation callables.

        Args:
            exec_repo: Repository for execution records.
            workflow_repo: Repository for workflows.
            comp_repo: Optional repository for components.
            prompt_block_repo: Optional repository for prompt blocks.
            output_profile_repo: Optional repository for output profiles.
            identity_repo: Optional repository for identity records.
            system_repo: Optional repository for system settings.
            export_service: Optional export service instance.
            storage_driver: Optional storage file driver.
            get_execution_fn: Optional callable to resolve execution records.
            get_report_dto_fn: Optional callable to resolve report data DTOs.
        """
        self.exec_repo, self.workflow_repo, self.comp_repo = exec_repo, workflow_repo, comp_repo
        self.prompt_block_repo, self.output_profile_repo = prompt_block_repo, output_profile_repo
        self.identity_repo, self.system_repo = identity_repo, system_repo

        if export_service is not None:
            self.export_service = export_service
        else:
            self.export_service = ExportService(comp_repo=comp_repo)

        if storage_driver is not None:
            self.storage = storage_driver
        else:
            self.storage = storage.get_storage_driver()

        if get_execution_fn is not None:
            self._get_execution = get_execution_fn
        else:
            self._get_execution = self._default_get_execution

        if get_report_dto_fn is not None:
            self._get_report_dto = get_report_dto_fn
        else:
            self._get_report_dto = self.get_report_dto

    async def _default_get_execution(self, initiator: TokenData, execution_id: str) -> ExecutionRecord:
        """Fetch execution record by ID with full hydration.

        Args:
            initiator: Auth token data of user requesting execution.
            execution_id: System execution identifier.

        Returns:
            Hydrated ExecutionRecord instance.

        Raises:
            ResourceNotFoundError: If execution record does not exist.
        """
        record = await self.exec_repo.get_execution(execution_id, hydrate=True)
        if not record:
            raise ResourceNotFoundError(resource_type="execution", resource_id=execution_id)
        return record

    def _transformer(self) -> BlueprintTransformer:
        """Build and return a BlueprintTransformer instance using registered repositories.

        Returns:
            Configured BlueprintTransformer instance.

        Raises:
            AppException: If required repositories for BlueprintTransformer are missing.
        """
        if (
            self.comp_repo is None
            or self.prompt_block_repo is None
            or self.output_profile_repo is None
            or self.identity_repo is None
            or self.system_repo is None
        ):
            logger.error(
                "[LegacyRenderService] %s: Repositories required for BlueprintTransformer are missing",
                ErrorCodes.CONFIGURATION_ERROR.name,
            )
            raise AppException(
                message="Repositories required for BlueprintTransformer are missing",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
            )
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
        """Generate an Excel export for the execution including Summary and Raw Data tabs.

        Args:
            initiator: Auth token data of user requesting export.
            execution_id: System execution identifier.

        Returns:
            Tuple of (raw_bytes, filename) for the generated export spreadsheet.

        Raises:
            AppException: If execution status is not PASSED, execution has no atoms, or report fetch fails.
        """
        record = await self._get_execution(initiator=initiator, execution_id=execution_id)
        if record.status != ExecutionStatus.PASSED:
            msg = "Execution must be in PASSED state to generate export."
            logger.error("[LegacyRenderService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED})

        if record.step_states:
            has_atoms = any(s.scorecard_atoms for s in record.step_states.values())
        else:
            has_atoms = False

        if not has_atoms:
            msg = "Execution has no scoreable atoms to export."
            logger.error("[LegacyRenderService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED})

        report_dto: ReportDataDTO | None = None
        try:
            report_dto = await self._get_report_dto(initiator, execution_id)
        except Exception as e:
            logger.error("[LegacyRenderService] Could not generate report_dto: %s", e)
            raise AppException(
                message=f"Report Fetch Error: {e}",
                status_code=500,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR},
            ) from e

        if self.comp_repo is not None:
            components = await self.comp_repo.get_all_components("prompt_block")
        else:
            components = None

        if record.target_locale:
            target_locale = record.target_locale
        else:
            target_locale = "fi"

        return await self.export_service.export_excel(
            execution=record,
            report_dto=report_dto,
            locale=target_locale,
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
        """Get the headless ReportDataDTO for an execution.

        Args:
            initiator: Auth token data of user requesting report.
            execution_id: System execution identifier.
            custom_preface_md: Optional preface markdown text override.
            local_time_str: Optional formatted local timestamp string.

        Returns:
            Headless ReportDataDTO instance for the execution.

        Raises:
            AppException: If execution status is not PASSED.
        """
        record = await self._get_execution(initiator=initiator, execution_id=execution_id)
        if record.status != ExecutionStatus.PASSED:
            msg = f"Execution is not in COMPLETED state. Current status: {record.status.value}"
            logger.error("[LegacyRenderService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return await self._transformer().build_report_dto(
            execution_id,
            profile_id=None,
            accept_language=record.target_locale,
            custom_preface_md=custom_preface_md,
            local_time_str=local_time_str,
        )

    async def get_sdui_view(self, initiator: TokenData, execution_id: str) -> ReportView:
        """Get the SDUI view components for an execution.

        Args:
            initiator: Auth token data of user requesting view.
            execution_id: System execution identifier.

        Returns:
            ReportView instance ready for client rendering.

        Raises:
            AppException: If report fetching fails or execution is not PASSED.
        """
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
        """Securely enqueue a PDF generation job and inject a Virtual Step into the trace.

        Args:
            initiator: Auth token data of user requesting PDF.
            execution_id: System execution identifier.
            accept_language: Target localization language code.
            profile_id: System profile identifier.
            arq_pool: Redis connection pool for background task dispatch.
            custom_preface_md: Optional preface markdown text override.
            local_time_str: Optional formatted local timestamp string.

        Returns:
            None.
        """
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
        """Render an execution record to requested format.

        Args:
            initiator: Auth token data of user requesting rendering.
            execution_id: System execution identifier.
            format_type: Output format string ("flat", "json", "html", "pdf").
            profile_id: System profile identifier or None.
            accept_language: Target localization language code.
            arq_pool: Redis connection pool for background task dispatch.
            custom_preface_md: Optional preface markdown text override.
            local_time_str: Optional formatted local timestamp string.

        Returns:
            RenderExecutionResultDTO with rendered payload and content type.

        Raises:
            AppException: If execution is not PASSED, format is unsupported, workflow not found, or storage fails.
        """
        record = await self._get_execution(initiator=initiator, execution_id=execution_id)
        if record.status != ExecutionStatus.PASSED:
            msg = f"Execution is not in COMPLETED state. Current status: {record.status.value}"
            logger.error("[LegacyRenderService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED})

        fmt = format_type.lower()
        if fmt not in ("flat", "json", "html", "pdf"):
            logger.error(
                "[LegacyRenderService] %s: Unsupported format: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                format_type,
            )
            raise AppException(
                message=f"Unsupported format: {format_type}",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED},
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
            logger.error(
                "[LegacyRenderService] %s: Workflow %s not found",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                record.workflow_id,
            )
            raise AppException(
                message="Workflow not found",
                status_code=500,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND},
            )

        workflow_obj = Workflow.model_validate(workflow_data)
        default_pid = workflow_obj.default_profile_id
        resolved_pid: str | None
        if profile_id and profile_id != "default":
            resolved_pid = profile_id
        else:
            resolved_pid = default_pid

        if resolved_pid not in record.profile_syntheses:
            updated_ts = "0"
            if record.updated_at:
                updated_ts = str(record.updated_at).replace(":", "").replace("-", "").replace(".", "").replace(" ", "_")

            if accept_language and accept_language.strip():
                resolved_lang = accept_language
            else:
                resolved_lang = record.target_locale

            job_id = f"render_{execution_id}_{resolved_pid}_{resolved_lang}_{updated_ts}"
            await arq_pool.enqueue_job(
                "render_profile_job",
                _job_id=job_id,
                execution_id=execution_id,
                profile_id=resolved_pid,
                accept_language=resolved_lang,
            )
            v_step_id = f"sys_render_{resolved_pid}"
            if v_step_id in record.step_states:
                active_message = record.step_states[v_step_id].label
            else:
                active_message = "Valmistellaan tulostusta..."

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

        if accept_language:
            target_locale = accept_language
        else:
            target_locale = record.target_locale

        if not target_locale:
            logger.error("[LegacyRenderService] %s: target_locale missing", ErrorCodes.VALIDATION_FAILED.name)
            raise AppException(
                message="target_locale missing",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED},
            )

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
                    logger.error(
                        "[LegacyRenderService] %s: Storage read failed: %s",
                        ErrorCodes.INTERNAL_SERVER_ERROR.name,
                        strg_err,
                    )
                    raise AppException(
                        message="Failed to read PDF from storage",
                        status_code=500,
                        details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR},
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
                    logger.error(
                        "[LegacyRenderService] %s: Storage save failed: %s",
                        ErrorCodes.INTERNAL_SERVER_ERROR.name,
                        heal_err,
                    )
                    raise AppException(
                        message="Failed to save PDF to storage",
                        status_code=500,
                        details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR},
                    ) from heal_err

            return RenderExecutionResultDTO(
                content=pdf_bytes,
                media_type="application/pdf",
                filename=f"execution_{execution_id}.pdf",
            )

        logger.error(
            "[LegacyRenderService] %s: Unsupported format: %s",
            ErrorCodes.VALIDATION_FAILED.name,
            format_type,
        )
        raise AppException(
            message=f"Unsupported format: {format_type}",
            status_code=400,
            details={"error_code": ErrorCodes.VALIDATION_FAILED},
        )
