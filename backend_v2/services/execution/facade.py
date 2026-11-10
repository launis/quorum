"""Execution Service Facade composing decomposed execution domain services."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

from arq import ArqRedis

if TYPE_CHECKING:
    from backend_v2.services.orchestrator.dag_executor import DAGExecutor

from backend_v2.database.interfaces import (
    EntityPersistencePort,
    IComponentRepository,
    IExecutionRepository,
    IIdentityRepository,
    IOutputProfileRepository,
    IPromptBlockRepository,
    IReportArtifactRepository,
    ISystemRepository,
    IWorkflowRepository,
)
from backend_v2.exceptions import (
    AppException,
    ErrorCodes,
)
from backend_v2.models.auth import (
    ExecutionAssignmentBatchCreateDTO,
    ExecutionAssignmentBatchResponseDTO,
    ExecutionAssignmentCreateDTO,
    ExecutionAssignmentDraftDTO,
    ExecutionAssignmentOnboardingRequestDTO,
    ExecutionAssignmentPreviewDTO,
    ExecutionAssignmentResponseDTO,
    ExecutionAssignmentSubmitDTO,
    TokenData,
    TokenExchangeResponseDTO,
)
from backend_v2.models.domain.execution import ExecutionCreate, ExecutionRecord
from backend_v2.models.dtos.matrix_scorecard import HumanOverrideRequest
from backend_v2.models.dtos.workflow_schema import WorkflowSchemaResponseDTO
from backend_v2.services.auth.email_service import EmailService
from backend_v2.services.auth.repositories import OrganizationRepository, UserRepository
from backend_v2.services.auth.token_service import TokenService
from backend_v2.services.document_extraction import DocumentExtractionService
from backend_v2.services.execution.assignment_service import ExecutionAssignmentService
from backend_v2.services.execution.context_service import ExecutionContextService
from backend_v2.services.execution.ingress_service import (
    ExecutionIngressService,
)
from backend_v2.services.execution.ingress_service import (
    create_execution_record as create_execution_record,
)
from backend_v2.services.execution.lifecycle_service import ExecutionLifecycleService
from backend_v2.services.execution.override_service import ExecutionOverrideService
from backend_v2.services.execution.resumption_service import ExecutionResumptionService
from backend_v2.services.execution.stream_service import ExecutionStreamService
from backend_v2.services.file_driver import FileDriver
from backend_v2.services.storage import get_storage_driver
from backend_v2.services.usage_service import UsageService

logger = logging.getLogger(__name__)

__all__ = ["ExecutionService", "create_execution_record"]


class ExecutionService:
    """Consolidated facade delegating execution operations to decomposed domain services.

    Attributes:
        exec_repo: Repository for execution records.
        workflow_repo: Repository for workflow blueprints.
        comp_repo: Optional repository for workflow components.
        prompt_block_repo: Optional repository for prompt blocks.
        output_profile_repo: Optional repository for output profiles.
        identity_repo: Optional repository for user and organization identities.
        system_repo: Optional repository for system configuration and model registries.
        usage_service: Optional service for organization token usage and quota telemetry.
        executor: Optional DAGExecutor instance.
        storage: FileDriver storage backend for execution artifacts.
    """

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
        storage_driver: FileDriver | None = None,
        report_repo: IReportArtifactRepository | None = None,
        assignment_service: ExecutionAssignmentService | None = None,
        email_service: EmailService | None = None,
        entity_adapter: EntityPersistencePort | None = None,
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
            storage_driver: Optional FileDriver storage backend.
            report_repo: Optional repository for report artifacts.
            assignment_service: Optional ExecutionAssignmentService instance.
            email_service: Optional EmailService instance.
            entity_adapter: Optional hexagonal EntityPersistencePort for assignments.

        Raises:
            AppException: If resolving the default FileDriver fails due to an unsupported
                storage backend (ErrorCodes.CONFIGURATION_ERROR).
        """
        self.exec_repo, self.workflow_repo, self.comp_repo = exec_repo, workflow_repo, comp_repo
        self.prompt_block_repo, self.output_profile_repo = prompt_block_repo, output_profile_repo
        self.identity_repo, self.system_repo = identity_repo, system_repo
        self.usage_service = usage_service
        self.executor = executor
        self.storage: FileDriver = storage_driver if storage_driver is not None else get_storage_driver()

        self._ingress = ExecutionIngressService(
            exec_repo, workflow_repo, prompt_block_repo, output_profile_repo, system_repo, self.usage_service
        )
        self._assignment: ExecutionAssignmentService | None = self._build_assignment_service(
            assignment_service=assignment_service,
            identity_repo=identity_repo,
            workflow_repo=workflow_repo,
            prompt_block_repo=prompt_block_repo,
            email_service=email_service,
            entity_adapter=entity_adapter,
        )
        self._resumption = ExecutionResumptionService(
            exec_repo,
            workflow_repo,
            self.usage_service,
            get_execution_fn=self._delegate_get_execution,
            check_resumability_fn=self._delegate_check_resumability,
            prompt_block_repo=prompt_block_repo,
        )
        assignment_lookup_fn = None
        if self._assignment is not None:
            assignment_lookup_fn = self._assignment.get_assignment_by_execution_id
        self._lifecycle = ExecutionLifecycleService(
            exec_repo,
            self._resumption,
            self.storage,
            report_repo,
            check_resumability_fn=self._delegate_check_resumability,
            assignment_lookup_fn=assignment_lookup_fn,
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
            get_execution_fn=self._delegate_get_execution,
        )
        self._stream = ExecutionStreamService(exec_repo, get_execution_fn=self._delegate_get_execution)
        self._context = ExecutionContextService(exec_repo, self.storage, get_execution_fn=self._delegate_get_execution)

    def _build_assignment_service(
        self,
        *,
        assignment_service: ExecutionAssignmentService | None,
        identity_repo: IIdentityRepository | None,
        workflow_repo: IWorkflowRepository,
        prompt_block_repo: IPromptBlockRepository | None,
        email_service: EmailService | None,
        entity_adapter: EntityPersistencePort | None,
    ) -> ExecutionAssignmentService | None:
        """Resolve or instantiate the optional ExecutionAssignmentService sub-service.

        Args:
            assignment_service: Explicit ExecutionAssignmentService override if injected.
            identity_repo: Optional identity repository backing user and organization lookups.
            workflow_repo: Workflow repository passed to assignment orchestration.
            prompt_block_repo: Optional prompt block repository for Task Brief resolution.
            email_service: Optional transactional email dispatch service.
            entity_adapter: Optional hexagonal EntityPersistencePort for assignments.

        Returns:
            Configured ExecutionAssignmentService instance or None if identity dependencies are absent.
        """
        if assignment_service is not None:
            return assignment_service
        if identity_repo is not None:
            user_repo = UserRepository(identity_repo)
            org_repo = OrganizationRepository(identity_repo)
            return ExecutionAssignmentService(
                ingress_service=self._ingress,
                org_repo=org_repo,
                user_repo=user_repo,
                workflow_repo=workflow_repo,
                prompt_block_repo=prompt_block_repo,
                token_service=TokenService(repo=user_repo),
                email_service=email_service,
                entity_adapter=entity_adapter,
            )
        return None

    async def _delegate_get_execution(
        self,
        initiator: TokenData,
        execution_id: str,
        hydrate: bool = True,
        skip_resumability: bool = False,
    ) -> ExecutionRecord:
        """Forward execution lookup dynamically through the facade's get_execution entrypoint.

        Args:
            initiator: Authentication token data of requesting user.
            execution_id: Canonical Opaque Stripe ID of target execution.
            hydrate: Whether to hydrate related workflow and step metadata.
            skip_resumability: Whether to bypass checking resumable state.

        Returns:
            Retrieved execution record.

        Raises:
            ResourceNotFoundError: If the execution record does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
            PermissionDeniedError: If the initiator lacks access to the execution (ErrorCodes.PERMISSION_DENIED).
        """
        return await self.get_execution(
            initiator,
            execution_id,
            hydrate=hydrate,
            skip_resumability=skip_resumability,
        )

    async def _delegate_check_resumability(self, record: ExecutionRecord) -> bool:
        """Forward resumability evaluation dynamically through the facade's check_resumability entrypoint.

        Args:
            record: Target execution record to evaluate.

        Returns:
            True if execution state permits resumption, False otherwise.
        """
        return await self.check_resumability(record)

    async def list_executions(self, initiator: TokenData) -> list[ExecutionRecord]:
        """List all execution records accessible to the initiator.

        Args:
            initiator: Authentication token data of requesting user.

        Returns:
            List of execution records belonging to user's organization.

        Raises:
            AppException: If repository lookup or resumability evaluation fails (ErrorCodes.INTERNAL_SERVER_ERROR).
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

        Raises:
            ResourceNotFoundError: If the execution record does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
            PermissionDeniedError: If the initiator lacks access to the execution (ErrorCodes.PERMISSION_DENIED).
        """
        return await self._lifecycle.get_execution(initiator, execution_id, hydrate, skip_resumability)

    async def delete_execution(self, initiator: TokenData, execution_id: str) -> bool:
        """Delete an execution record and associated storage artifacts.

        Args:
            initiator: Authentication token data of requesting user.
            execution_id: Canonical Opaque Stripe ID of target execution.

        Returns:
            True if execution was successfully deleted.

        Raises:
            ResourceNotFoundError: If the execution record does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
            PermissionDeniedError: If the initiator lacks deletion rights (ErrorCodes.PERMISSION_DENIED).
            AppException: If cascading storage or repository deletion fails (ErrorCodes.INTERNAL_SERVER_ERROR).
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

        Raises:
            ResourceNotFoundError: If workflow, profile, or model registry does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
            PermissionDeniedError: If the initiator lacks access to the workflow (ErrorCodes.PERMISSION_DENIED).
            ConfigurationError: If a referenced step or prompt block blueprint is missing (ErrorCodes.CONFIGURATION_ERROR).
            AppException: If quota is exceeded (ErrorCodes.RATE_LIMIT_EXCEEDED), input or profile validation fails
                (ErrorCodes.VALIDATION_FAILED), or a required repository dependency is missing
                (ErrorCodes.SERVICE_DEPENDENCY_MISSING).
        """
        return await self._ingress.start_execution(initiator, payload, arq_pool, doc_service)

    async def get_workflow_ui_schema(self, workflow_id: str) -> WorkflowSchemaResponseDTO:
        """Retrieve the dynamic UI schema for a specific workflow.

        Args:
            workflow_id: Canonical Opaque Stripe ID of target workflow.

        Returns:
            Workflow schema response containing input definitions and rules.

        Raises:
            ResourceNotFoundError: If the target workflow does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
        """
        return await self._ingress.get_workflow_ui_schema(workflow_id)

    async def check_resumability(self, record: ExecutionRecord) -> bool:
        """Check if an interrupted execution record can be resumed.

        Args:
            record: Target execution record to evaluate.

        Returns:
            True if execution state permits resumption, False otherwise.
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

        Raises:
            ResourceNotFoundError: If the execution record does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
            PermissionDeniedError: If the initiator lacks access to the execution (ErrorCodes.PERMISSION_DENIED).
            AppException: If the execution state is unresumable (ErrorCodes.UNRESUMABLE_STATE_ERROR) or organization
                quota is exceeded (ErrorCodes.RATE_LIMIT_EXCEEDED).
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

        Raises:
            ResourceNotFoundError: If the execution record does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
            PermissionDeniedError: If the initiator lacks permission to modify the execution (ErrorCodes.PERMISSION_DENIED).
            AppException: If the target atom is not found (ErrorCodes.RESOURCE_NOT_FOUND), required repositories are
                missing (ErrorCodes.CONFIGURATION_ERROR), or an optimistic concurrency conflict occurs
                (ErrorCodes.CONFLICT).
        """
        await self._override.override_atom(initiator, execution_id, atom_id, payload)

    async def reject_evidence_quote(self, initiator: TokenData, execution_id: str, evq_id: str, reason: str) -> None:
        """Reject a specific evidence quote on an execution record.

        Args:
            initiator: Authentication token data of requesting user.
            execution_id: Canonical Opaque Stripe ID of target execution.
            evq_id: Unique quote evidence identifier to reject.
            reason: Text explanation for quote rejection.

        Raises:
            ResourceNotFoundError: If the execution record does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
            PermissionDeniedError: If the initiator lacks permission to modify the execution (ErrorCodes.PERMISSION_DENIED).
            AppException: If an optimistic concurrency conflict occurs (ErrorCodes.CONFLICT).
        """
        await self._override.reject_evidence_quote(initiator, execution_id, evq_id, reason)

    async def clear_profile_synthesis(self, initiator: TokenData, execution_id: str, profile_id: str) -> None:
        """Clear cached profile synthesis blocks for an execution.

        Args:
            initiator: Authentication token data of requesting user.
            execution_id: Canonical Opaque Stripe ID of target execution.
            profile_id: Canonical Opaque Stripe ID of output profile.

        Raises:
            ResourceNotFoundError: If the execution or workflow record does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
            PermissionDeniedError: If the initiator lacks access to the execution (ErrorCodes.PERMISSION_DENIED).
            AppException: If deleting the cached PDF report blob fails (ErrorCodes.INTERNAL_SERVER_ERROR) or an
                optimistic concurrency conflict occurs (ErrorCodes.CONFLICT).
        """
        await self._override.clear_profile_synthesis(initiator, execution_id, profile_id)

    async def stream_status(self, initiator: TokenData, execution_id: str) -> AsyncGenerator[str]:
        """Yield Server-Sent Events streaming the real-time status of an execution.

        Args:
            initiator: Authentication token data of requesting user.
            execution_id: Canonical Opaque Stripe ID of target execution.

        Yields:
            Serialized Server-Sent Events chunks reporting status updates.

        Raises:
            ResourceNotFoundError: If the execution record does not exist on preflight check (ErrorCodes.RESOURCE_NOT_FOUND).
            PermissionDeniedError: If the initiator lacks access to the execution on preflight check
                (ErrorCodes.PERMISSION_DENIED).
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

        Raises:
            ResourceNotFoundError: If the execution record does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
            PermissionDeniedError: If the initiator lacks access to the execution (ErrorCodes.PERMISSION_DENIED).
            AppException: If reading the offloaded frozen context blob from storage fails (ErrorCodes.RESOURCE_NOT_FOUND).
        """
        return await self._context.get_frozen_context_bytes(initiator, execution_id)

    def _require_assignment_service(self) -> ExecutionAssignmentService:
        """Return the configured ExecutionAssignmentService or raise AppException.

        Returns:
            Configured ExecutionAssignmentService instance.

        Raises:
            AppException: With ErrorCodes.SERVICE_DEPENDENCY_MISSING if _assignment is None.
        """
        if self._assignment is None:
            logger.error(
                "[ExecutionService] %s: ExecutionAssignmentService is not configured.",
                ErrorCodes.SERVICE_DEPENDENCY_MISSING.name,
                exc_info=True,
                extra={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.value},
            )
            raise AppException(
                message="ExecutionAssignmentService is not configured.",
                status_code=500,
                details={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.value},
            )
        return self._assignment

    async def create_assignment(
        self,
        initiator: TokenData,
        payload: ExecutionAssignmentCreateDTO,
    ) -> ExecutionAssignmentResponseDTO:
        """Create a single time-bound workflow execution assignment.

        Args:
            initiator: Authenticated caller token data.
            payload: Validated ExecutionAssignmentCreateDTO.

        Returns:
            Redacted ExecutionAssignmentResponseDTO.

        Raises:
            ConfigurationError: If no assignment persistence backend is configured (ErrorCodes.CONFIGURATION_ERROR).
            PermissionDeniedError: If caller role or email domain violates policy (ErrorCodes.PERMISSION_DENIED).
            ResourceNotFoundError: If the caller's organization does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
            ConflictError: If recipient belongs to a different organization (ErrorCodes.USER_ALREADY_ASSIGNED).
            AppException: If ExecutionAssignmentService is missing (ErrorCodes.SERVICE_DEPENDENCY_MISSING) or
                hard_deadline_at is in the past (ErrorCodes.VALIDATION_FAILED).
        """
        return await self._require_assignment_service().create_assignment(initiator, payload)

    async def create_assignment_batch(
        self,
        initiator: TokenData,
        payload: ExecutionAssignmentBatchCreateDTO,
    ) -> ExecutionAssignmentBatchResponseDTO:
        """Create a cohort batch of time-bound execution assignments.

        Args:
            initiator: Authenticated caller token data.
            payload: Validated ExecutionAssignmentBatchCreateDTO.

        Returns:
            ExecutionAssignmentBatchResponseDTO with batch_id and created assignments.

        Raises:
            ConfigurationError: If no assignment persistence backend is configured (ErrorCodes.CONFIGURATION_ERROR).
            PermissionDeniedError: If caller role or email domain violates policy (ErrorCodes.PERMISSION_DENIED).
            ResourceNotFoundError: If the caller's organization does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
            ConflictError: If any recipient belongs to a different organization (ErrorCodes.USER_ALREADY_ASSIGNED).
            AppException: If ExecutionAssignmentService is missing (ErrorCodes.SERVICE_DEPENDENCY_MISSING) or
                hard_deadline_at is in the past (ErrorCodes.VALIDATION_FAILED).
        """
        return await self._require_assignment_service().create_assignment_batch(initiator, payload)

    async def list_assignments(self, initiator: TokenData) -> list[ExecutionAssignmentResponseDTO]:
        """List execution assignments accessible to the initiator.

        Args:
            initiator: Authenticated caller token data.

        Returns:
            List of ExecutionAssignmentResponseDTO records.

        Raises:
            ConfigurationError: If no assignment persistence backend is configured (ErrorCodes.CONFIGURATION_ERROR).
            AppException: If ExecutionAssignmentService is missing (ErrorCodes.SERVICE_DEPENDENCY_MISSING).
        """
        return await self._require_assignment_service().list_assignments(initiator)

    async def resend_assignment_email(
        self,
        initiator: TokenData,
        assignment_id: str,
    ) -> ExecutionAssignmentResponseDTO:
        """Rotate token and resend magic-link email for a task assignment.

        Args:
            initiator: Authenticated caller token data.
            assignment_id: Canonical Task Assignment ID.

        Returns:
            Updated ExecutionAssignmentResponseDTO.

        Raises:
            ConfigurationError: If no assignment persistence backend is configured (ErrorCodes.CONFIGURATION_ERROR).
            PermissionDeniedError: If the caller lacks organization privileges (ErrorCodes.PERMISSION_DENIED).
            ResourceNotFoundError: If the assignment or organization does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
            ConflictError: If the assignment was already submitted (ErrorCodes.ASSIGNMENT_ALREADY_SUBMITTED).
            AppException: If ExecutionAssignmentService is missing (ErrorCodes.SERVICE_DEPENDENCY_MISSING).
        """
        return await self._require_assignment_service().resend_assignment_email(initiator, assignment_id)

    async def preview_assignment(self, raw_token: str) -> ExecutionAssignmentPreviewDTO:
        """Perform a side-effect-free preview of a task assignment by raw token.

        Args:
            raw_token: Raw single-use assignment token.

        Returns:
            ExecutionAssignmentPreviewDTO.

        Raises:
            ConfigurationError: If no assignment persistence backend is configured (ErrorCodes.CONFIGURATION_ERROR).
            ResourceNotFoundError: If the token digest or organization does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
            AppException: If ExecutionAssignmentService is missing (ErrorCodes.SERVICE_DEPENDENCY_MISSING).
        """
        return await self._require_assignment_service().preview_assignment(raw_token)

    async def onboard_assignee(
        self,
        raw_token: str,
        payload: ExecutionAssignmentOnboardingRequestDTO,
    ) -> TokenExchangeResponseDTO:
        """Execute combined JIT user onboarding and 2FA verification for a task assignee.

        Args:
            raw_token: Raw single-use assignment token.
            payload: Onboarding request DTO.

        Returns:
            TokenExchangeResponseDTO with signed 15-minute Quorum Local JWT.

        Raises:
            ConfigurationError: If no assignment persistence backend is configured (ErrorCodes.CONFIGURATION_ERROR).
            ResourceNotFoundError: If the token digest does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
            AuthenticationError: If Firebase token or MFA verification fails
                (ErrorCodes.MFA_REQUIRED, ErrorCodes.AUTHENTICATION_FAILED).
            PermissionDeniedError: If Firebase email mismatches assigned_email (ErrorCodes.IDENTITY_MISMATCH).
            ConflictError: If the user belongs to another organization (ErrorCodes.USER_ALREADY_ASSIGNED).
            AppException: If ExecutionAssignmentService is missing (ErrorCodes.SERVICE_DEPENDENCY_MISSING) or
                hard_deadline_at has passed (ErrorCodes.ASSIGNMENT_EXPIRED).
        """
        return await self._require_assignment_service().onboard_assignee(raw_token, payload)

    async def activate_assignment(
        self,
        initiator: TokenData,
        assignment_id: str,
    ) -> ExecutionAssignmentResponseDTO:
        """Explicitly activate a task assignment and start its countdown timer.

        Args:
            initiator: Authenticated assignee token data.
            assignment_id: Canonical Task Assignment ID.

        Returns:
            Activated ExecutionAssignmentResponseDTO.

        Raises:
            ConfigurationError: If no assignment persistence backend is configured (ErrorCodes.CONFIGURATION_ERROR).
            ResourceNotFoundError: If the assignment does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
            PermissionDeniedError: If caller identity mismatches assigned_email (ErrorCodes.IDENTITY_MISMATCH).
            ConflictError: If a cross-organization collision occurs (ErrorCodes.USER_ALREADY_ASSIGNED) or the
                assignment was already submitted (ErrorCodes.ASSIGNMENT_ALREADY_SUBMITTED).
            AppException: If ExecutionAssignmentService is missing (ErrorCodes.SERVICE_DEPENDENCY_MISSING) or
                deadline has passed (ErrorCodes.ASSIGNMENT_EXPIRED).
        """
        return await self._require_assignment_service().activate_assignment(initiator, assignment_id)

    async def save_draft_inputs(
        self,
        initiator: TokenData,
        assignment_id: str,
        payload: ExecutionAssignmentDraftDTO,
        doc_service: DocumentExtractionService | None = None,
    ) -> ExecutionAssignmentResponseDTO:
        """Persist auto-saved assignee draft inputs on an active assignment.

        Args:
            initiator: Authenticated assignee token data.
            assignment_id: Canonical Task Assignment ID.
            payload: Draft inputs DTO.
            doc_service: Optional document extraction service for Base64 attachments.

        Returns:
            Updated ExecutionAssignmentResponseDTO.

        Raises:
            ConfigurationError: If no assignment persistence backend is configured (ErrorCodes.CONFIGURATION_ERROR).
            ResourceNotFoundError: If the assignment does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
            PermissionDeniedError: If caller identity mismatches assigned_email (ErrorCodes.IDENTITY_MISMATCH).
            ConflictError: If the assignment was already submitted (ErrorCodes.ASSIGNMENT_ALREADY_SUBMITTED).
            AppException: If ExecutionAssignmentService is missing (ErrorCodes.SERVICE_DEPENDENCY_MISSING),
                deadline has passed (ErrorCodes.ASSIGNMENT_EXPIRED), or assignment is not yet activated
                (ErrorCodes.VALIDATION_FAILED).
        """
        return await self._require_assignment_service().save_draft_inputs(
            initiator,
            assignment_id,
            payload,
            doc_service=doc_service,
        )

    async def submit_assignment(
        self,
        initiator: TokenData,
        assignment_id: str,
        payload: ExecutionAssignmentSubmitDTO,
        arq_pool: ArqRedis,
        doc_service: DocumentExtractionService | None = None,
    ) -> ExecutionRecord:
        """Validate Dual-Clock expiration, merge locked inputs, and trigger execution.

        Args:
            initiator: Authenticated assignee token data.
            assignment_id: Canonical Task Assignment ID.
            payload: Submitted inputs DTO.
            arq_pool: Arq Redis connection pool.
            doc_service: Optional document extraction service.

        Returns:
            Initialized ExecutionRecord.

        Raises:
            ConfigurationError: If no assignment persistence backend is configured (ErrorCodes.CONFIGURATION_ERROR).
            ResourceNotFoundError: If the assignment or workflow does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
            PermissionDeniedError: If caller identity mismatches assigned_email (ErrorCodes.IDENTITY_MISMATCH) or
                workflow access is denied (ErrorCodes.PERMISSION_DENIED).
            ConflictError: If the assignment was already submitted (ErrorCodes.ASSIGNMENT_ALREADY_SUBMITTED).
            AppException: If ExecutionAssignmentService is missing (ErrorCodes.SERVICE_DEPENDENCY_MISSING) or
                Dual-Clock deadline plus grace window has passed (ErrorCodes.ASSIGNMENT_EXPIRED).
        """
        return await self._require_assignment_service().submit_assignment(
            initiator=initiator,
            assignment_id=assignment_id,
            payload=payload,
            arq_pool=arq_pool,
            doc_service=doc_service,
        )
