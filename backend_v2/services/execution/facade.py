"""Execution Service Facade (Strangler Fig Pattern) composing decomposed domain services."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from typing import Any
from warnings import deprecated

from arq import ArqRedis

from backend_v2.database.interfaces import (
    IComponentRepository,
    IExecutionRepository,
    IIdentityRepository,
    IOutputProfileRepository,
    IPromptBlockRepository,
    IReportArtifactRepository,
    ISystemRepository,
    IWorkflowRepository,
)
from backend_v2.models.auth import TokenData
from backend_v2.models.domain.execution import ExecutionCreate, ExecutionRecord
from backend_v2.models.dtos.matrix_scorecard import HumanOverrideRequest
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.services.document_extraction import DocumentExtractionService
from backend_v2.services.execution.context_service import ExecutionContextService
from backend_v2.services.execution.ingress_service import ExecutionIngressService, create_execution_record
from backend_v2.services.execution.legacy_render_service import ExecutionLegacyRenderService
from backend_v2.services.execution.lifecycle_service import ExecutionLifecycleService
from backend_v2.services.execution.override_service import ExecutionOverrideService
from backend_v2.services.execution.resumption_service import ExecutionResumptionService
from backend_v2.services.execution.stream_service import ExecutionStreamService
from backend_v2.services.export_service import ExportService
from backend_v2.services.file_driver import FileDriver
from backend_v2.services.storage import get_storage_driver
from backend_v2.services.usage_service import UsageService

logger = logging.getLogger(__name__)

__all__ = ["ExecutionService", "create_execution_record"]


class ExecutionService:
    """Unified facade for workflow execution operations."""

    def __init__(
        self,
        exec_repo: IExecutionRepository,
        workflow_repo: IWorkflowRepository,
        comp_repo: IComponentRepository | None = None,
        prompt_block_repo: IPromptBlockRepository | None = None,
        output_profile_repo: IOutputProfileRepository | None = None,
        identity_repo: IIdentityRepository | None = None,
        system_repo: ISystemRepository | None = None,
        usage_service: UsageService | None = None,
        executor: Any = None,
        export_service: ExportService | None = None,
        storage_driver: FileDriver | None = None,
        report_repo: IReportArtifactRepository | None = None,
    ) -> None:
        self.exec_repo, self.workflow_repo, self.comp_repo = exec_repo, workflow_repo, comp_repo
        self.prompt_block_repo, self.output_profile_repo = prompt_block_repo, output_profile_repo
        self.identity_repo, self.system_repo = identity_repo, system_repo
        self.usage_service = usage_service
        self.executor = executor
        self.export_service = export_service if export_service is not None else ExportService(comp_repo=comp_repo)
        self.storage: FileDriver = storage_driver if storage_driver is not None else get_storage_driver()

        self._resumption = ExecutionResumptionService(
            exec_repo,
            workflow_repo,
            self.usage_service,
            get_execution_fn=lambda *a, **k: self.get_execution(*a, **k),
            check_resumability_fn=lambda *a, **k: self.check_resumability(*a, **k),
        )
        self._lifecycle = ExecutionLifecycleService(
            exec_repo,
            self._resumption,
            self.storage,
            report_repo,
            check_resumability_fn=lambda *a, **k: self.check_resumability(*a, **k),
        )
        self._ingress = ExecutionIngressService(
            exec_repo, workflow_repo, prompt_block_repo, output_profile_repo, system_repo, self.usage_service
        )
        self._override = ExecutionOverrideService(
            exec_repo,
            workflow_repo,
            comp_repo,
            prompt_block_repo,
            output_profile_repo,
            identity_repo,
            system_repo,
            self.storage,
            get_execution_fn=lambda *a, **k: self.get_execution(*a, **k),
        )
        self._stream = ExecutionStreamService(exec_repo, get_execution_fn=lambda *a, **k: self.get_execution(*a, **k))
        self._context = ExecutionContextService(
            exec_repo, self.storage, get_execution_fn=lambda *a, **k: self.get_execution(*a, **k)
        )
        self._renderer = ExecutionLegacyRenderService(
            exec_repo,
            workflow_repo,
            comp_repo,
            prompt_block_repo,
            output_profile_repo,
            identity_repo,
            system_repo,
            self.export_service,
            self.storage,
            get_execution_fn=lambda *a, **k: self.get_execution(*a, **k),
            get_report_dto_fn=lambda *a, **k: self.get_report_dto(*a, **k),
        )

    async def list_executions(self, initiator: TokenData) -> list[ExecutionRecord]:
        return await self._lifecycle.list_executions(initiator)

    async def get_execution(
        self, initiator: TokenData, execution_id: str, hydrate: bool = True, skip_resumability: bool = False
    ) -> ExecutionRecord:
        return await self._lifecycle.get_execution(initiator, execution_id, hydrate, skip_resumability)

    async def delete_execution(self, initiator: TokenData, execution_id: str) -> bool:
        return await self._lifecycle.delete_execution(initiator, execution_id)

    async def start_execution(
        self,
        initiator: TokenData,
        payload: ExecutionCreate,
        arq_pool: ArqRedis,
        doc_service: DocumentExtractionService | None = None,
    ) -> ExecutionRecord:
        return await self._ingress.start_execution(initiator, payload, arq_pool, doc_service)

    async def get_workflow_ui_schema(self, workflow_id: str) -> dict[str, Any]:
        return await self._ingress.get_workflow_ui_schema(workflow_id)

    async def check_resumability(self, record: ExecutionRecord) -> bool:
        return await self._resumption.check_resumability(record)

    async def resume_execution(self, initiator: TokenData, execution_id: str, arq_pool: ArqRedis) -> ExecutionRecord:
        return await self._resumption.resume_execution(initiator, execution_id, arq_pool)

    async def override_atom(
        self, initiator: TokenData, execution_id: str, atom_id: str, payload: HumanOverrideRequest
    ) -> None:
        await self._override.override_atom(initiator, execution_id, atom_id, payload)

    async def reject_evidence_quote(self, initiator: TokenData, execution_id: str, evq_id: str, reason: str) -> None:
        await self._override.reject_evidence_quote(initiator, execution_id, evq_id, reason)

    async def clear_profile_synthesis(self, initiator: TokenData, execution_id: str, profile_id: str) -> None:
        await self._override.clear_profile_synthesis(initiator, execution_id, profile_id)

    async def stream_status(self, initiator: TokenData, execution_id: str) -> AsyncGenerator[str]:
        async for chunk in self._stream.stream_status(initiator, execution_id):
            yield chunk

    async def get_frozen_context_bytes(self, initiator: TokenData, execution_id: str) -> tuple[bytes, str]:
        return await self._context.get_frozen_context_bytes(initiator, execution_id)

    @deprecated("Use ExportService.export_excel directly or ReportService.get_report_excel_bytes.")
    async def get_execution_export_bytes(self, initiator: TokenData, execution_id: str) -> tuple[bytes, str]:
        return await self._renderer.get_execution_export_bytes(initiator, execution_id)

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
    ) -> tuple[bytes | list[Any] | dict[str, Any] | Any, str, str | None]:
        return await self._renderer.render_execution(
            initiator,
            execution_id,
            format_type,
            profile_id,
            accept_language,
            arq_pool,
            custom_preface_md,
            local_time_str,
        )

    async def get_report_dto(self, initiator: TokenData, execution_id: str) -> ReportDataDTO:
        return await self._renderer.get_report_dto(initiator, execution_id)

    async def get_sdui_view(self, initiator: TokenData, execution_id: str) -> dict[str, Any]:
        return await self._renderer.get_sdui_view(initiator, execution_id)

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
        await self._renderer.enqueue_pdf_generation(
            initiator, execution_id, accept_language, profile_id, arq_pool, custom_preface_md, local_time_str
        )
