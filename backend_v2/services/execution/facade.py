"""Execution Service Facade (Strangler Fig Pattern) composing decomposed domain services."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING
from warnings import deprecated

from arq import ArqRedis

if TYPE_CHECKING:
    from backend_v2.services.orchestrator.dag_executor import DAGExecutor

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
from backend_v2.models.dtos.render import RenderExecutionResultDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.dtos.workflow_schema import WorkflowSchemaResponseDTO
from backend_v2.models.view.sdui import ReportView
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
    """Consolidated facade delegating execution operations to decomposed domain services."""

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
        executor: DAGExecutor | None = None,
        export_service: ExportService | None = None,
        storage_driver: FileDriver | None = None,
        report_repo: IReportArtifactRepository | None = None,
    ) -> None:
        """Initialize ExecutionService facade with required repositories and sub-services.

        Args:
            exec_repo: Repository for execution records.
            workflow_repo: Repository for workflows.
            comp_repo: Optional repository for components.
            prompt_block_repo: Optional repository for prompt blocks.
            output_profile_repo: Optional repository for output profiles.
            identity_repo: Optional repository for identities.
            system_repo: Optional repository for system settings.
            usage_service: Optional service for token usage telemetry.
            executor: Optional DAGExecutor instance.
            export_service: Optional ExportService instance.
            storage_driver: Optional FileDriver storage backend.
            report_repo: Optional repository for report artifacts.
        """
        self.exec_repo, self.workflow_repo, self.comp_repo = exec_repo, workflow_repo, comp_repo
        self.prompt_block_repo, self.output_profile_repo = prompt_block_repo, output_profile_repo
        self.identity_repo, self.system_repo = identity_repo, system_repo
        self.usage_service = usage_service
        self.executor = executor
        if export_service is not None:
            self.export_service = export_service
        else:
            self.export_service = ExportService(comp_repo=comp_repo)

        if storage_driver is not None:
            self.storage: FileDriver = storage_driver
        else:
            self.storage = get_storage_driver()

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
        """List all execution records accessible to the initiator.

        Args:
            initiator: Authentication token data of requesting user.

        Returns:
            List of execution records belonging to user's organization.
        """
        return await self._lifecycle.list_executions(initiator)

    async def get_execution(
        self, initiator: TokenData, execution_id: str, hydrate: bool = True, skip_resumability: bool = False
    ) -> ExecutionRecord:
        """Retrieve a specific execution record by ID.

        Args:
            initiator: Authentication token data of requesting user.
            execution_id: Canonical Opaque Stripe ID of target execution.
            hydrate: Whether to hydrate related workflow and step metadata.
            skip_resumability: Whether to bypass checking resumable state.

        Returns:
            Retrieved execution record.
        """
        return await self._lifecycle.get_execution(initiator, execution_id, hydrate, skip_resumability)

    async def delete_execution(self, initiator: TokenData, execution_id: str) -> bool:
        """Delete an execution record and associated storage artifacts.

        Args:
            initiator: Authentication token data of requesting user.
            execution_id: Canonical Opaque Stripe ID of target execution.

        Returns:
            True if execution was successfully deleted.
        """
        return await self._lifecycle.delete_execution(initiator, execution_id)

    async def start_execution(
        self,
        initiator: TokenData,
        payload: ExecutionCreate,
        arq_pool: ArqRedis,
        doc_service: DocumentExtractionService | None = None,
    ) -> ExecutionRecord:
        """Validate ingress payload and schedule a new execution run.

        Args:
            initiator: Authentication token data of requesting user.
            payload: Input parameters and target workflow for execution.
            arq_pool: Redis worker connection pool for job queueing.
            doc_service: Optional service for document text extraction.

        Returns:
            Newly initialized execution record.
        """
        return await self._ingress.start_execution(initiator, payload, arq_pool, doc_service)

    async def get_workflow_ui_schema(self, workflow_id: str) -> WorkflowSchemaResponseDTO:
        """Retrieve the dynamic UI schema for a specific workflow.

        Args:
            workflow_id: Canonical Opaque Stripe ID of target workflow.

        Returns:
            Workflow schema response containing input definitions and rules.
        """
        return await self._ingress.get_workflow_ui_schema(workflow_id)

    async def check_resumability(self, record: ExecutionRecord) -> bool:
        """Check if an interrupted execution record can be resumed.

        Args:
            record: Target execution record to evaluate.

        Returns:
            True if execution state permits resumption.
        """
        return await self._resumption.check_resumability(record)

    async def resume_execution(self, initiator: TokenData, execution_id: str, arq_pool: ArqRedis) -> ExecutionRecord:
        """Resume an interrupted or paused execution run.

        Args:
            initiator: Authentication token data of requesting user.
            execution_id: Canonical Opaque Stripe ID of target execution.
            arq_pool: Redis worker connection pool for job queueing.

        Returns:
            Updated execution record scheduled for resumption.
        """
        return await self._resumption.resume_execution(initiator, execution_id, arq_pool)

    async def override_atom(
        self, initiator: TokenData, execution_id: str, atom_id: str, payload: HumanOverrideRequest
    ) -> None:
        """Apply a human override decision to an evaluated atom.

        Args:
            initiator: Authentication token data of requesting user.
            execution_id: Canonical Opaque Stripe ID of target execution.
            atom_id: Target atom identifier to override.
            payload: Override parameters including verdict and explanation.
        """
        await self._override.override_atom(initiator, execution_id, atom_id, payload)

    async def reject_evidence_quote(self, initiator: TokenData, execution_id: str, evq_id: str, reason: str) -> None:
        """Reject a specific evidence quote on an execution record.

        Args:
            initiator: Authentication token data of requesting user.
            execution_id: Canonical Opaque Stripe ID of target execution.
            evq_id: Unique quote evidence identifier to reject.
            reason: Text explanation for quote rejection.
        """
        await self._override.reject_evidence_quote(initiator, execution_id, evq_id, reason)

    async def clear_profile_synthesis(self, initiator: TokenData, execution_id: str, profile_id: str) -> None:
        """Clear cached profile synthesis blocks for an execution.

        Args:
            initiator: Authentication token data of requesting user.
            execution_id: Canonical Opaque Stripe ID of target execution.
            profile_id: Canonical Opaque Stripe ID of output profile.
        """
        await self._override.clear_profile_synthesis(initiator, execution_id, profile_id)

    async def stream_status(self, initiator: TokenData, execution_id: str) -> AsyncGenerator[str]:
        """Yield Server-Sent Events streaming the real-time status of an execution.

        Args:
            initiator: Authentication token data of requesting user.
            execution_id: Canonical Opaque Stripe ID of target execution.

        Yields:
            Serialized Server-Sent Events chunks reporting status updates.
        """
        async for chunk in self._stream.stream_status(initiator, execution_id):
            yield chunk

    async def get_frozen_context_bytes(self, initiator: TokenData, execution_id: str) -> tuple[bytes, str]:
        """Retrieve the raw frozen context JSON payload for an execution.

        Args:
            initiator: Authentication token data of requesting user.
            execution_id: Canonical Opaque Stripe ID of target execution.

        Returns:
            Tuple of (raw bytes of frozen context JSON, suggested filename).
        """
        return await self._context.get_frozen_context_bytes(initiator, execution_id)

    @deprecated("Use ExportService.export_excel directly or ReportService.get_report_excel_bytes.")
    async def get_execution_export_bytes(self, initiator: TokenData, execution_id: str) -> tuple[bytes, str]:
        """Retrieve legacy export bytes for an execution.

        Args:
            initiator: Authentication token data of requesting user.
            execution_id: Canonical Opaque Stripe ID of target execution.

        Returns:
            Tuple of (raw bytes of exported file, suggested filename).
        """
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
    ) -> RenderExecutionResultDTO:
        """Render an execution into requested format (PDF, SDUI, HTML, etc.).

        Args:
            initiator: Authentication token data of requesting user.
            execution_id: Canonical Opaque Stripe ID of target execution.
            format_type: Desired output format representation.
            profile_id: Optional output profile identifier.
            accept_language: Optional user locale preference.
            arq_pool: Redis worker connection pool for job queueing.
            custom_preface_md: Optional custom Markdown preface for rendering.
            local_time_str: Optional client local timestamp string.

        Returns:
            Render result DTO containing rendered payload and metadata.
        """
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
        """Compile and return the complete ReportDataDTO for an execution.

        Args:
            initiator: Authentication token data of requesting user.
            execution_id: Canonical Opaque Stripe ID of target execution.

        Returns:
            Fully compiled ReportDataDTO object.
        """
        return await self._renderer.get_report_dto(initiator, execution_id)

    async def get_sdui_view(self, initiator: TokenData, execution_id: str) -> ReportView:
        """Generate and return the Server-Driven UI ReportView model.

        Args:
            initiator: Authentication token data of requesting user.
            execution_id: Canonical Opaque Stripe ID of target execution.

        Returns:
            Structured ReportView containing SDUI sections and blocks.
        """
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
        """Enqueue an asynchronous background task to render execution PDF.

        Args:
            initiator: Authentication token data of requesting user.
            execution_id: Canonical Opaque Stripe ID of target execution.
            accept_language: Optional user locale preference.
            profile_id: Output profile identifier for report layout.
            arq_pool: Redis worker connection pool for job queueing.
            custom_preface_md: Optional custom Markdown preface for report.
            local_time_str: Optional client local timestamp string.
        """
        await self._renderer.enqueue_pdf_generation(
            initiator, execution_id, accept_language, profile_id, arq_pool, custom_preface_md, local_time_str
        )
