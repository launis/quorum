"""Time-Bound Execution Assignment Service for SafeLinks-immune task links and JIT onboarding."""

from __future__ import annotations

import asyncio
import hashlib
import inspect
import logging
import secrets
import time
from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from typing import Never, Protocol, runtime_checkable

import jwt
from arq import ArqRedis
from pydantic import SecretStr

from backend_v2.database.interfaces import (
    EntityPersistencePort,
    IPromptBlockRepository,
    IWorkflowRepository,
    UnitOfWorkFactory,
    get_registered_uow_factory,
)
from backend_v2.exceptions import (
    AppException,
    AuthenticationError,
    ConfigurationError,
    ConflictError,
    ErrorCodes,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from backend_v2.models.auth import (
    ExecutionAssignmentBatchCreateDTO,
    ExecutionAssignmentBatchResponseDTO,
    ExecutionAssignmentCreateDTO,
    ExecutionAssignmentDraftDTO,
    ExecutionAssignmentOnboardingRequestDTO,
    ExecutionAssignmentPreviewDTO,
    ExecutionAssignmentRecipientDTO,
    ExecutionAssignmentResponseDTO,
    ExecutionAssignmentSubmitDTO,
    Organization,
    SystemOrganizations,
    TaskAssignmentBriefDTO,
    TokenData,
    TokenExchangeResponseDTO,
    TransactionalEmailItemDTO,
    User,
    UserRole,
    UserUpdate,
)
from backend_v2.models.core_base import (
    PrefixedUUID7,
    generate_opaque_id,
    generate_uuid7,
    generate_uuid7_opaque_id,
)
from backend_v2.models.domain.execution import (
    ExecutionAssignment,
    ExecutionCreate,
    ExecutionRecord,
    FrozenContext,
)
from backend_v2.models.domain.inputs import Base64Attachment, WorkflowInputs, WorkflowInputsIngress
from backend_v2.models.domain.prompt_blocks import SystemRulePromptBlock
from backend_v2.models.dtos.schema_manifest import GeneratedSchemaManifestDTO
from backend_v2.models.dtos.theory_manifest import InjectedTheoryManifestDTO
from backend_v2.models.enums import (
    AssignmentResultVisibility,
    AssignmentStatus,
    EmailDeliveryStatus,
    EntityPrefix,
    PromptBlockCategory,
    SystemLocale,
)
from backend_v2.services.auth.email_service import EmailService
from backend_v2.services.auth.repositories import OrganizationRepository, UserRepository
from backend_v2.services.auth.token_service import TokenService
from backend_v2.services.document_extraction import DocumentExtractionService
from backend_v2.services.execution.ingress_service import (
    ExecutionIngressService,
    merge_assignment_inputs,
)
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = [
    "AuditEventLoggerProtocol",
    "ExecutionAssignmentService",
    "mask_email_address",
    "redact_execution_for_confirmation_only",
]


@runtime_checkable
class AuditEventLoggerProtocol(Protocol):
    """Protocol for structured task assignment audit event logging across bounded contexts."""

    async def log_event(
        self,
        *,
        actor_id: str,
        action: str,
        organization_id: str,
        target_id: str,
        details: Mapping[str, str | int | float | bool | None],
    ) -> None: ...


def mask_email_address(email: str) -> str:
    """Mask an email address for public preview responses (e.g. 'j***@example.com').

    Args:
        email: Raw email address string.

    Returns:
        Redacted email hint preserving first character and domain.
    """
    normalized = email.strip()
    if "@" not in normalized:
        return "***"
    local_part, domain = normalized.split("@", 1)
    if not local_part:
        return f"***@{domain}"
    return f"{local_part[0]}***@{domain}"


def redact_execution_for_confirmation_only(record: ExecutionRecord) -> ExecutionRecord:
    """Strip forensic SDUI, synthesis, and PDF report payloads for CONFIRMATION_ONLY visibility.

    Args:
        record: Full ExecutionRecord model.

    Returns:
        Redacted ExecutionRecord containing only submission confirmation and status metadata.
    """
    redacted_steps = [step.model_copy(update={"scorecard_atoms": {}}) for step in record.steps]
    redacted_step_states = {
        step_id: state.model_copy(update={"scorecard_atoms": {}}) for step_id, state in record.step_states.items()
    }
    return record.model_copy(
        update={
            "profile_syntheses": {},
            "pdf_report_path": None,
            "frozen_context": FrozenContext(
                compiled_prompts={},
                injected_theory=InjectedTheoryManifestDTO(theories={}),
                generated_schemas=GeneratedSchemaManifestDTO(schemas={}),
                ui_hints_snapshot={},
                mcp_tool_audit=[],
            ),
            "frozen_context_storage_path": None,
            "steps": redacted_steps,
            "step_states": redacted_step_states,
        }
    )


class ExecutionAssignmentService:
    """Service managing Time-Bound Execution Assignments, SafeLinks preview, and JIT onboarding.

    Attributes:
        ingress_service: ExecutionIngressService for single-pipeline execution startup.
        org_repo: Organization repository wrapper.
        user_repo: User repository wrapper.
        workflow_repo: Optional workflow repository for workflow verification.
        prompt_block_repo: Optional prompt block repository for Task Brief lookup.
        token_service: Optional TokenService for Firebase 2FA verification and JWT issuance.
        email_service: Transactional email dispatch service.
        audit_service: Optional audit event logging service.
    """

    def __init__(
        self,
        ingress_service: ExecutionIngressService,
        org_repo: OrganizationRepository,
        user_repo: UserRepository,
        workflow_repo: IWorkflowRepository | None = None,
        prompt_block_repo: IPromptBlockRepository | None = None,
        token_service: TokenService | None = None,
        email_service: EmailService | None = None,
        audit_service: AuditEventLoggerProtocol | None = None,
        entity_adapter: EntityPersistencePort | None = None,
        uow_factory: UnitOfWorkFactory | None = None,
    ) -> None:
        """Initialize the ExecutionAssignmentService.

        Args:
            ingress_service: ExecutionIngressService instance.
            org_repo: OrganizationRepository wrapper.
            user_repo: UserRepository wrapper.
            workflow_repo: Optional IWorkflowRepository instance.
            prompt_block_repo: Optional IPromptBlockRepository instance.
            token_service: Optional TokenService instance.
            email_service: Optional EmailService instance.
            audit_service: Optional structured audit event logger implementing AuditEventLoggerProtocol.
            entity_adapter: Optional hexagonal EntityPersistencePort for assignments.
            uow_factory: Optional UnitOfWork factory for transactional assignment persistence.
        """
        self.ingress_service = ingress_service
        self.org_repo = org_repo
        self.user_repo = user_repo
        self.workflow_repo = workflow_repo
        self.prompt_block_repo: IPromptBlockRepository | None = (
            prompt_block_repo if prompt_block_repo is not None else ingress_service.prompt_block_repo
        )
        self.token_service = token_service
        self.email_service: EmailService = email_service if email_service is not None else EmailService()
        self.audit_service: AuditEventLoggerProtocol | None = audit_service
        self._entity_adapter: EntityPersistencePort | None = entity_adapter
        self._uow_factory: UnitOfWorkFactory | None = uow_factory
        self._last_generated_tokens: dict[str, str] = {}

    def _resolve_uow_factory(self) -> UnitOfWorkFactory | None:
        """Resolve explicit or globally registered UnitOfWork factory.

        Returns:
            Configured UnitOfWorkFactory callable or None.
        """
        return self._uow_factory if self._uow_factory is not None else get_registered_uow_factory()

    @staticmethod
    def _raise_unconfigured_persistence_error() -> Never:
        """Raise Fail-Fast ConfigurationError when no persistence port or UoW is configured.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR.
        """
        logger.error(
            "[ExecutionAssignmentService] %s: ExecutionAssignmentService requires an entity_adapter or uow_factory.",
            ErrorCodes.CONFIGURATION_ERROR.name,
            exc_info=True,
            extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )
        raise ConfigurationError(
            message="ExecutionAssignmentService requires an entity_adapter or uow_factory for assignment persistence.",
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )

    @asynccontextmanager
    async def _acquire_entity_port(
        self,
        *,
        commit: bool = False,
    ) -> AsyncIterator[EntityPersistencePort]:
        """Yield the active EntityPersistencePort from entity_adapter or a UnitOfWork transaction.

        Args:
            commit: Whether to commit the UnitOfWork transaction upon successful exit.

        Yields:
            Configured EntityPersistencePort instance.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
        """
        if self._entity_adapter is not None:
            yield self._entity_adapter
            return
        uow_factory = self._resolve_uow_factory()
        if uow_factory is not None:
            async with uow_factory() as uow:
                yield uow.entities
                if commit:
                    await uow.commit()
            return
        self._raise_unconfigured_persistence_error()

    @staticmethod
    def _ensure_utc(dt: datetime) -> datetime:
        """Normalize a datetime value to timezone-aware UTC.

        Args:
            dt: Input datetime instance.

        Returns:
            Timezone-aware UTC datetime instance.
        """
        return dt.replace(tzinfo=UTC) if dt.tzinfo is None else dt

    @staticmethod
    def _assert_not_submitted(
        assignment: ExecutionAssignment,
        *,
        operation: str,
    ) -> None:
        """Raise ConflictError if the assignment has already been submitted.

        Args:
            assignment: Target ExecutionAssignment domain model.
            operation: Human-readable operation description for structured diagnostics.

        Raises:
            ConflictError: With ErrorCodes.ASSIGNMENT_ALREADY_SUBMITTED if already submitted.
        """
        if assignment.status == AssignmentStatus.SUBMITTED or assignment.execution_id is not None:
            logger.error(
                "[ExecutionAssignmentService] %s: Cannot %s already submitted assignment '%s'.",
                ErrorCodes.ASSIGNMENT_ALREADY_SUBMITTED.name,
                operation,
                assignment.id,
                exc_info=True,
                extra={"error_code": ErrorCodes.ASSIGNMENT_ALREADY_SUBMITTED.value},
            )
            raise ConflictError(
                message="Assignment has already been submitted.",
                details={
                    "error_code": ErrorCodes.ASSIGNMENT_ALREADY_SUBMITTED.value,
                    "assignment_id": assignment.id,
                },
            )

    def get_last_generated_token(self, assignment_id: str) -> str | None:
        """Return the raw token generated for an assignment ID in test/local workflows.

        Args:
            assignment_id: Canonical Task Assignment ID (tsk_<hex32>).

        Returns:
            Raw URL-safe assignment token if generated in this service instance, else None.
        """
        if assignment_id in self._last_generated_tokens:
            return self._last_generated_tokens[assignment_id]
        return None

    async def create_assignment(
        self,
        initiator: TokenData,
        payload: ExecutionAssignmentCreateDTO,
    ) -> ExecutionAssignmentResponseDTO:
        """Create a single time-bound workflow execution assignment and dispatch email.

        Args:
            initiator: Authenticated caller token data (ROOT, ADMIN, or MANAGER).
            payload: Validated ExecutionAssignmentCreateDTO.

        Returns:
            Redacted ExecutionAssignmentResponseDTO without token_hash.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED on role or domain violation.
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if organization is missing.
            ConflictError: With ErrorCodes.USER_ALREADY_ASSIGNED on cross-tenant identity collision.
            AppException: With ErrorCodes.VALIDATION_FAILED if hard_deadline_at is in the past.
        """
        org = await self._authorize_and_load_assignment_org(
            initiator=initiator,
            invited_role=payload.invited_role,
        )
        now = datetime.now(UTC)
        self._validate_deadline(hard_deadline_at=payload.hard_deadline_at, now=now)
        normalized_email = await self._validate_assignment_recipient(
            org=org,
            raw_email=str(payload.assigned_email),
        )
        task_brief = await self._validate_and_resolve_task_brief(
            payload.task_brief_id,
            org.id,
            strict=True,
        )

        raw_token = secrets.token_urlsafe(32)
        assignment = self._build_assignment(
            initiator=initiator,
            org=org,
            normalized_email=normalized_email,
            invited_role=payload.invited_role,
            workflow_id=payload.workflow_id,
            output_profile_id=payload.output_profile_id,
            task_brief_id=payload.task_brief_id,
            target_locale=payload.target_locale,
            locked_inputs=payload.locked_inputs,
            assignee_input_keys=payload.assignee_input_keys,
            result_visibility=payload.result_visibility,
            hard_deadline_at=payload.hard_deadline_at,
            relative_duration_seconds=payload.relative_duration_seconds,
            raw_token=raw_token,
            batch_id=None,
            now=now,
        )
        persisted = await self._dispatch_and_persist_single_assignment(
            org=org,
            assignment=assignment,
            raw_token=raw_token,
        )
        await self._log_audit(
            actor_id=initiator.id,
            action="ASSIGNMENT_CREATED",
            organization_id=org.id,
            target_id=persisted.id,
            assignment_id=persisted.id,
            workflow_id=persisted.workflow_id,
        )
        return self._to_assignment_response(persisted, task_brief=task_brief)

    async def create_assignment_batch(
        self,
        initiator: TokenData,
        payload: ExecutionAssignmentBatchCreateDTO,
    ) -> ExecutionAssignmentBatchResponseDTO:
        """Create a cohort batch of time-bound execution assignments with all-or-nothing preflight.

        Args:
            initiator: Authenticated caller token data (ROOT, ADMIN, or MANAGER).
            payload: Validated ExecutionAssignmentBatchCreateDTO (1 to 500 recipients).

        Returns:
            ExecutionAssignmentBatchResponseDTO with shared batch_id and created assignments.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED on role or domain violation.
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if organization is missing.
            ConflictError: With ErrorCodes.USER_ALREADY_ASSIGNED on cross-tenant identity collision.
            AppException: With ErrorCodes.VALIDATION_FAILED if hard_deadline_at is in the past.
        """
        org = await self._authorize_and_load_assignment_org(
            initiator=initiator,
            invited_role=payload.invited_role,
        )
        now = datetime.now(UTC)
        self._validate_deadline(hard_deadline_at=payload.hard_deadline_at, now=now)
        task_brief = await self._validate_and_resolve_task_brief(
            payload.task_brief_id,
            org.id,
            strict=True,
        )
        deduplicated = await self._preflight_validate_batch_recipients(
            org=org,
            recipients=payload.recipients,
        )
        batch_id = generate_uuid7_opaque_id(EntityPrefix.ASSIGNMENT)
        persisted_dtos = await self._materialize_and_dispatch_batch(
            initiator=initiator,
            org=org,
            payload=payload,
            deduplicated=deduplicated,
            batch_id=batch_id,
            task_brief=task_brief,
            now=now,
        )
        await self._log_audit(
            actor_id=initiator.id,
            action="ASSIGNMENT_BATCH_CREATED",
            organization_id=org.id,
            target_id=batch_id,
            batch_id=batch_id,
            created_count=len(persisted_dtos),
        )
        return ExecutionAssignmentBatchResponseDTO(
            batch_id=batch_id,
            created_count=len(persisted_dtos),
            assignments=persisted_dtos,
        )

    async def list_assignments(
        self,
        initiator: TokenData,
    ) -> list[ExecutionAssignmentResponseDTO]:
        """List execution assignments scoped by the 4-Tier RBAC Governance Matrix.

        Args:
            initiator: Authenticated caller token data.

        Returns:
            List of ExecutionAssignmentResponseDTO accessible to the caller.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
        """
        all_records = await self._list_all_assignments(
            organization_id=None if initiator.role == UserRole.ROOT else initiator.organization_id
        )
        if initiator.role == UserRole.ROOT:
            visible = all_records
        elif initiator.role in (UserRole.ADMIN, UserRole.MANAGER):
            visible = [a for a in all_records if a.organization_id == initiator.organization_id]
        else:
            visible = [
                a
                for a in all_records
                if a.assigned_user_id == initiator.id
                or (initiator.email is not None and a.assigned_email.lower() == initiator.email.lower())
            ]
        return [await self._to_hydrated_assignment_response(a) for a in visible]

    async def resend_assignment_email(
        self,
        initiator: TokenData,
        assignment_id: str,
    ) -> ExecutionAssignmentResponseDTO:
        """Rotate the 256-bit assignment token and re-dispatch the magic-link email.

        Args:
            initiator: Authenticated caller token data (ROOT, ADMIN, or MANAGER).
            assignment_id: Canonical Task Assignment ID (tsk_<hex32>).

        Returns:
            Updated ExecutionAssignmentResponseDTO with refreshed email_delivery_status.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if caller lacks privileges.
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if assignment is missing.
            ConflictError: With ErrorCodes.ASSIGNMENT_ALREADY_SUBMITTED if already submitted.
        """
        assignment = await self._get_assignment_or_raise(assignment_id)
        self._verify_manager_or_admin_for_org(initiator=initiator, org_id=assignment.organization_id)
        self._assert_not_submitted(assignment, operation="resend")
        org = await self._fetch_org_or_raise(assignment.organization_id)
        raw_token = secrets.token_urlsafe(32)
        new_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        rotated = assignment.model_copy(update={"token_hash": new_hash})
        persisted = await self._dispatch_and_persist_single_assignment(
            org=org,
            assignment=rotated,
            raw_token=raw_token,
        )
        return await self._to_hydrated_assignment_response(persisted)

    async def preview_assignment(self, raw_token: str) -> ExecutionAssignmentPreviewDTO:
        """Perform a 100% side-effect-free SafeLinks-immune preview lookup by token digest.

        Never mutates status or sets activated_at on GET, neutralizing premature countdown
        triggers from email security scanners (Microsoft Defender SafeLinks, Proofpoint, Mimecast).

        Args:
            raw_token: Raw single-use URL-safe assignment token from query string.

        Returns:
            ExecutionAssignmentPreviewDTO with masked email and deadline metadata.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if token digest is unknown.
        """
        assignment = await self._resolve_assignment_by_raw_token_or_raise(
            raw_token,
            context_label="Assignment preview",
        )
        org = await self._fetch_org_or_raise(assignment.organization_id)
        task_brief = await self._validate_and_resolve_task_brief(
            assignment.task_brief_id,
            assignment.organization_id,
            strict=False,
        )
        return ExecutionAssignmentPreviewDTO(
            id=assignment.id,
            organization_id=assignment.organization_id,
            organization_name=org.name,
            assigned_email_masked=mask_email_address(str(assignment.assigned_email)),
            workflow_id=assignment.workflow_id,
            task_brief_id=assignment.task_brief_id,
            task_brief=task_brief,
            target_locale=assignment.target_locale,
            status=assignment.status,
            hard_deadline_at=assignment.hard_deadline_at,
            relative_duration_seconds=assignment.relative_duration_seconds,
        )

    async def onboard_assignee(
        self,
        raw_token: str,
        payload: ExecutionAssignmentOnboardingRequestDTO,
    ) -> TokenExchangeResponseDTO:
        """Execute combined Just-In-Time (JIT) user onboarding + 2FA verification for a task assignee.

        Args:
            raw_token: Raw URL-safe assignment token.
            payload: ExecutionAssignmentOnboardingRequestDTO with Firebase token and display name.

        Returns:
            TokenExchangeResponseDTO containing a signed 15-minute Quorum Local JWT and User profile.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if token digest is unknown.
            AppException: With ErrorCodes.ASSIGNMENT_EXPIRED if hard_deadline_at has passed.
            AuthenticationError: With ErrorCodes.MFA_REQUIRED or AUTHENTICATION_FAILED on invalid token.
            PermissionDeniedError: With ErrorCodes.IDENTITY_MISMATCH if Firebase email mismatches assignment.
            ConflictError: With ErrorCodes.USER_ALREADY_ASSIGNED if user belongs to another organization.
        """
        assignment = await self._resolve_assignment_by_raw_token_or_raise(
            raw_token,
            context_label="Onboarding",
        )
        now = datetime.now(UTC)
        await self._assert_not_hard_expired(assignment=assignment, now=now)
        firebase_uid = await self._verify_onboarding_firebase_token(
            firebase_token=payload.firebase_token,
            expected_email=str(assignment.assigned_email),
        )
        user = await self._provision_or_bind_assignee_user(
            assignment=assignment,
            display_name=payload.name,
            firebase_uid=firebase_uid,
            now=now,
        )
        updated_assignment = assignment.model_copy(update={"assigned_user_id": user.id})
        await self._save_assignment(updated_assignment)
        return self._issue_local_jwt_for_user(user)

    async def activate_assignment(
        self,
        initiator: TokenData,
        assignment_id: str,
    ) -> ExecutionAssignmentResponseDTO:
        """Explicitly activate a task assignment and start the relative countdown window.

        Args:
            initiator: Authenticated user token data matching assignment.assigned_email.
            assignment_id: Canonical Task Assignment ID (tsk_<hex32>).

        Returns:
            ExecutionAssignmentResponseDTO with status='activated' and populated activated_at.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if assignment does not exist.
            PermissionDeniedError: With ErrorCodes.IDENTITY_MISMATCH if caller email mismatches.
            ConflictError: With ErrorCodes.USER_ALREADY_ASSIGNED on cross-org collision or
                ErrorCodes.ASSIGNMENT_ALREADY_SUBMITTED if already submitted.
            AppException: With ErrorCodes.ASSIGNMENT_EXPIRED if hard_deadline_at has passed.
        """
        assignment = await self._get_assignment_or_raise(assignment_id)
        await self._verify_assignee_identity(initiator=initiator, assignment=assignment)
        self._assert_not_submitted(assignment, operation="activate")
        now = datetime.now(UTC)
        await self._assert_not_hard_expired(assignment=assignment, now=now)
        if assignment.status == AssignmentStatus.ACTIVATED and assignment.activated_at is not None:
            await self._assert_within_dual_clock_deadline(assignment=assignment, now=now, include_grace=False)
            return await self._to_hydrated_assignment_response(assignment)

        activated = assignment.model_copy(
            update={
                "status": AssignmentStatus.ACTIVATED,
                "activated_at": now,
                "assigned_user_id": initiator.id,
            }
        )
        await self._save_assignment(activated)
        return await self._to_hydrated_assignment_response(activated)

    async def save_draft_inputs(
        self,
        initiator: TokenData,
        assignment_id: str,
        payload: ExecutionAssignmentDraftDTO,
        doc_service: DocumentExtractionService | None = None,
    ) -> ExecutionAssignmentResponseDTO:
        """Persist auto-saved assignee draft inputs while the assignment is active.

        Args:
            initiator: Authenticated assignee token data.
            assignment_id: Canonical Task Assignment ID (tsk_<hex32>).
            payload: Validated ExecutionAssignmentDraftDTO.
            doc_service: Optional DocumentExtractionService for eager Base64 extraction.

        Returns:
            Updated ExecutionAssignmentResponseDTO with saved draft_inputs.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if assignment is missing.
            PermissionDeniedError: With ErrorCodes.IDENTITY_MISMATCH if caller email mismatches.
            ConflictError: With ErrorCodes.ASSIGNMENT_ALREADY_SUBMITTED if already submitted.
            AppException: With ErrorCodes.ASSIGNMENT_EXPIRED if deadline has passed,
                ErrorCodes.SERVICE_DEPENDENCY_MISSING if Base64Attachment is sent without doc_service,
                or ErrorCodes.VALIDATION_FAILED if assignment is not yet activated.
        """
        assignment = await self._get_assignment_or_raise(assignment_id)
        await self._verify_assignee_identity(initiator=initiator, assignment=assignment)
        self._assert_not_submitted(assignment, operation="save draft on")
        now = datetime.now(UTC)
        await self._assert_within_dual_clock_deadline(assignment=assignment, now=now, include_grace=False)
        if assignment.status != AssignmentStatus.ACTIVATED:
            logger.error(
                "[ExecutionAssignmentService] %s: Assignment '%s' must be activated before saving draft.",
                ErrorCodes.VALIDATION_FAILED.name,
                assignment.id,
                exc_info=True,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(
                message="Assignment must be activated before saving draft inputs.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        normalized_draft = await self._normalize_assignee_ingress_inputs(payload.draft_inputs, doc_service)
        updated = assignment.model_copy(update={"draft_inputs": normalized_draft})
        await self._save_assignment(updated)
        return await self._to_hydrated_assignment_response(updated)

    async def submit_assignment(
        self,
        initiator: TokenData,
        assignment_id: str,
        payload: ExecutionAssignmentSubmitDTO,
        arq_pool: ArqRedis,
        doc_service: DocumentExtractionService | None = None,
        now_override: datetime | None = None,
    ) -> ExecutionRecord:
        """Atomically validate Dual-Clock expiration, merge locked inputs, and trigger execution.

        Args:
            initiator: Authenticated assignee token data.
            assignment_id: Canonical Task Assignment ID (tsk_<hex32>).
            payload: Validated ExecutionAssignmentSubmitDTO.
            arq_pool: Arq Redis connection pool for job dispatch.
            doc_service: Optional document extraction service.
            now_override: Optional UTC timestamp override for deterministic BVA testing.

        Returns:
            Initialized ExecutionRecord (redacted if result_visibility is CONFIRMATION_ONLY).

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if assignment is missing.
            PermissionDeniedError: With ErrorCodes.IDENTITY_MISMATCH if caller email mismatches.
            ConflictError: With ErrorCodes.ASSIGNMENT_ALREADY_SUBMITTED on replay submission.
            AppException: With ErrorCodes.ASSIGNMENT_EXPIRED if Dual-Clock deadline + grace has passed,
                or ErrorCodes.SERVICE_DEPENDENCY_MISSING if Base64Attachment is sent without doc_service.
        """
        assignment = await self._get_assignment_or_raise(assignment_id)
        await self._verify_assignee_identity(initiator=initiator, assignment=assignment)
        self._assert_not_submitted(assignment, operation="submit")
        now = now_override if now_override is not None else datetime.now(UTC)
        await self._assert_within_dual_clock_deadline(assignment=assignment, now=now, include_grace=True)
        normalized_submitted = await self._normalize_assignee_ingress_inputs(
            payload.submitted_inputs,
            doc_service,
        )

        record = await self._trigger_assignment_execution(
            initiator=initiator,
            assignment=assignment,
            submitted_inputs=normalized_submitted,
            arq_pool=arq_pool,
            doc_service=doc_service,
        )
        submitted = assignment.model_copy(
            update={
                "status": AssignmentStatus.SUBMITTED,
                "submitted_at": now,
                "execution_id": record.id,
                "assigned_user_id": initiator.id,
                "draft_inputs": normalized_submitted,
            }
        )
        await self._save_assignment(submitted)
        await self._log_audit(
            actor_id=initiator.id,
            action="ASSIGNMENT_SUBMITTED",
            organization_id=assignment.organization_id,
            target_id=assignment.id,
            assignment_id=assignment.id,
            execution_id=record.id,
        )
        if assignment.result_visibility == AssignmentResultVisibility.CONFIRMATION_ONLY and initiator.role in (
            UserRole.MEMBER,
            UserRole.VIEWER,
        ):
            return redact_execution_for_confirmation_only(record)
        return record

    async def get_assignment_by_execution_id(self, execution_id: str) -> ExecutionAssignment | None:
        """Look up the ExecutionAssignment that triggered a specific execution_id, if any.

        Args:
            execution_id: Canonical ExecutionRecord ID (exe_<hex32>).

        Returns:
            Matching ExecutionAssignment or None.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
        """
        persisted = await self._list_all_assignments()
        for item in persisted:
            if item.execution_id == execution_id:
                return item
        return None

    async def _authorize_and_load_assignment_org(
        self,
        *,
        initiator: TokenData,
        invited_role: UserRole,
    ) -> Organization:
        """Verify caller RBAC role and invited_role scope, then load the caller's Organization.

        Args:
            initiator: Caller TokenData.
            invited_role: Target role to grant upon assignee onboarding.

        Returns:
            Validated Organization domain model.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED on unauthorized role or scope.
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if organization is missing.
        """
        if initiator.role not in (UserRole.ROOT, UserRole.ADMIN, UserRole.MANAGER):
            logger.error(
                "[ExecutionAssignmentService] %s: Role '%s' cannot create task assignments.",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.role.value,
                exc_info=True,
                extra={"error_code": ErrorCodes.PERMISSION_DENIED.value},
            )
            raise PermissionDeniedError("Only MANAGER, ADMIN, or ROOT can create task assignments.")

        if initiator.role == UserRole.MANAGER and invited_role != UserRole.MEMBER:
            logger.error(
                "[ExecutionAssignmentService] %s: MANAGER '%s' attempted to assign invited_role='%s'.",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                invited_role.value,
                exc_info=True,
                extra={"error_code": ErrorCodes.PERMISSION_DENIED.value},
            )
            raise PermissionDeniedError("MANAGER can only assign tasks with MEMBER role.")

        if initiator.role != UserRole.ROOT and invited_role == UserRole.ROOT:
            logger.error(
                "[ExecutionAssignmentService] %s: Non-ROOT '%s' attempted to assign ROOT role.",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                exc_info=True,
                extra={"error_code": ErrorCodes.PERMISSION_DENIED.value},
            )
            raise PermissionDeniedError("Only ROOT can assign tasks with ROOT role.")

        if initiator.organization_id:
            org_id: str = initiator.organization_id
        elif initiator.role == UserRole.ROOT:
            org_id = SystemOrganizations.ROOT_SYSTEM
        else:
            logger.error(
                "[ExecutionAssignmentService] %s: Caller '%s' has no organization_id.",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                exc_info=True,
                extra={"error_code": ErrorCodes.PERMISSION_DENIED.value},
            )
            raise PermissionDeniedError("Caller must belong to an organization to create task assignments.")
        return await self._fetch_org_or_raise(org_id)

    @staticmethod
    def _validate_deadline(*, hard_deadline_at: datetime, now: datetime) -> None:
        """Ensure hard_deadline_at is strictly in the future relative to server UTC clock.

        Args:
            hard_deadline_at: Requested absolute deadline timestamp.
            now: Current server UTC timestamp.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if hard_deadline_at <= now.
        """
        deadline_utc = ExecutionAssignmentService._ensure_utc(hard_deadline_at)
        if deadline_utc <= now:
            logger.error(
                "[ExecutionAssignmentService] %s: hard_deadline_at '%s' must be in the future.",
                ErrorCodes.VALIDATION_FAILED.name,
                deadline_utc.isoformat(),
                exc_info=True,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(
                message="Assignment hard_deadline_at must be in the future.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

    async def _validate_assignment_recipient(
        self,
        *,
        org: Organization,
        raw_email: str,
    ) -> str:
        """Validate recipient email domain allowlist and 1:1 Flat Identity Collision Guard.

        Args:
            org: Issuing Organization model.
            raw_email: Recipient email string.

        Returns:
            Normalized lowercase email address.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if email domain is not allowed.
            ConflictError: With ErrorCodes.USER_ALREADY_ASSIGNED if recipient belongs to another org.
        """
        normalized_email = raw_email.strip().lower()
        email_domain = normalized_email.split("@")[-1].lower()
        if org.allowed_email_domains:
            allowed_domains = {d.strip().lower() for d in org.allowed_email_domains if d.strip()}
            if allowed_domains and email_domain not in allowed_domains:
                logger.error(
                    "[ExecutionAssignmentService] %s: Domain '%s' not in allowed_email_domains for org '%s'.",
                    ErrorCodes.PERMISSION_DENIED.name,
                    email_domain,
                    org.id,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.PERMISSION_DENIED.value},
                )
                raise PermissionDeniedError(
                    f"Recipient domain '{email_domain}' is not permitted for organization '{org.id}'."
                )

        existing_user = await self.user_repo.get_by_email(normalized_email)
        if (
            existing_user is not None
            and existing_user.deleted_at is None
            and existing_user.organization_id is not None
            and existing_user.organization_id != org.id
        ):
            logger.error(
                "[ExecutionAssignmentService] %s: User '%s' already belongs to org '%s' (target='%s').",
                ErrorCodes.USER_ALREADY_ASSIGNED.name,
                existing_user.id,
                existing_user.organization_id,
                org.id,
                exc_info=True,
                extra={"error_code": ErrorCodes.USER_ALREADY_ASSIGNED.value},
            )
            raise ConflictError(
                message=f"Recipient already belongs to another organization ('{existing_user.organization_id}').",
                details={
                    "error_code": ErrorCodes.USER_ALREADY_ASSIGNED.value,
                    "user_id": existing_user.id,
                    "current_organization_id": existing_user.organization_id,
                    "target_organization_id": org.id,
                },
            )
        return normalized_email

    async def _preflight_validate_batch_recipients(
        self,
        *,
        org: Organization,
        recipients: list[ExecutionAssignmentRecipientDTO],
    ) -> list[tuple[str, ExecutionAssignmentRecipientDTO]]:
        """Execute all-or-nothing pre-flight validation and deduplication across batch recipients.

        Args:
            org: Issuing Organization model.
            recipients: Batch recipient descriptors.

        Returns:
            Deduplicated list of (normalized_email, ExecutionAssignmentRecipientDTO) pairs.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if any email domain is disallowed.
            ConflictError: With ErrorCodes.USER_ALREADY_ASSIGNED if any recipient belongs to another org.
        """
        deduplicated: list[tuple[str, ExecutionAssignmentRecipientDTO]] = []
        seen_emails: set[str] = set()
        for item in recipients:
            normalized_email = await self._validate_assignment_recipient(
                org=org,
                raw_email=str(item.email),
            )
            if normalized_email in seen_emails:
                continue
            seen_emails.add(normalized_email)
            deduplicated.append((normalized_email, item))
        return deduplicated

    async def _materialize_and_dispatch_batch(
        self,
        *,
        initiator: TokenData,
        org: Organization,
        payload: ExecutionAssignmentBatchCreateDTO,
        deduplicated: list[tuple[str, ExecutionAssignmentRecipientDTO]],
        batch_id: PrefixedUUID7,
        task_brief: TaskAssignmentBriefDTO | None,
        now: datetime,
    ) -> list[ExecutionAssignmentResponseDTO]:
        """Construct, dispatch emails for, and persist a validated cohort batch of assignments.

        Args:
            initiator: Caller TokenData.
            org: Issuing Organization model.
            payload: Batch creation DTO.
            deduplicated: Validated and deduplicated recipient list.
            batch_id: Shared cohort batch UUIDv7 identifier.
            task_brief: Optional hydrated TaskAssignmentBriefDTO.
            now: Current UTC timestamp.

        Returns:
            List of persisted ExecutionAssignmentResponseDTO models.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
        """
        drafts: list[ExecutionAssignment] = []
        email_items: list[TransactionalEmailItemDTO] = []
        raw_tokens_by_id: dict[str, str] = {}

        for normalized_email, recipient_dto in deduplicated:
            raw_token = secrets.token_urlsafe(32)
            effective_locale = (
                recipient_dto.target_locale if recipient_dto.target_locale is not None else payload.target_locale
            )
            assignment = self._build_assignment(
                initiator=initiator,
                org=org,
                normalized_email=normalized_email,
                invited_role=payload.invited_role,
                workflow_id=payload.workflow_id,
                output_profile_id=payload.output_profile_id,
                task_brief_id=payload.task_brief_id,
                target_locale=effective_locale,
                locked_inputs=payload.locked_inputs,
                assignee_input_keys=payload.assignee_input_keys,
                result_visibility=payload.result_visibility,
                hard_deadline_at=payload.hard_deadline_at,
                relative_duration_seconds=payload.relative_duration_seconds,
                raw_token=raw_token,
                batch_id=batch_id,
                now=now,
            )
            email_item = self._build_assignment_email(
                org=org,
                assignment=assignment,
                raw_token=raw_token,
                recipient_name=recipient_dto.name,
            )
            drafts.append(assignment)
            email_items.append(email_item)
            raw_tokens_by_id[assignment.id] = raw_token

        batch_result = await self.email_service.send_assignment_emails(email_items)
        persisted_dtos: list[ExecutionAssignmentResponseDTO] = []
        for draft in drafts:
            status_val = (
                batch_result.delivery_statuses[draft.id]
                if draft.id in batch_result.delivery_statuses
                else EmailDeliveryStatus.FAILED
            )
            final_assignment = draft.model_copy(update={"email_delivery_status": status_val})
            await self._save_assignment(final_assignment)
            self._last_generated_tokens[final_assignment.id] = raw_tokens_by_id[final_assignment.id]
            persisted_dtos.append(self._to_assignment_response(final_assignment, task_brief=task_brief))
        return persisted_dtos

    @staticmethod
    def _build_assignment(
        *,
        initiator: TokenData,
        org: Organization,
        normalized_email: str,
        invited_role: UserRole,
        workflow_id: PrefixedUUID7,
        output_profile_id: PrefixedUUID7 | None,
        task_brief_id: PrefixedUUID7 | None,
        target_locale: SystemLocale,
        locked_inputs: WorkflowInputs,
        assignee_input_keys: list[str],
        result_visibility: AssignmentResultVisibility,
        hard_deadline_at: datetime,
        relative_duration_seconds: int | None,
        raw_token: str,
        batch_id: PrefixedUUID7 | None,
        now: datetime,
    ) -> ExecutionAssignment:
        """Instantiate an ExecutionAssignment domain model with SHA-256 token_hash.

        Args:
            initiator: Caller TokenData.
            org: Issuing Organization.
            normalized_email: Lowercase recipient email.
            invited_role: Role granted upon onboarding.
            workflow_id: Target Workflow ID.
            output_profile_id: Optional Output Profile ID.
            task_brief_id: Optional Task Definition PromptBlock ID.
            target_locale: Target locale enum.
            locked_inputs: Manager-locked WorkflowInputs.
            assignee_input_keys: Unlocked input keys for assignee.
            result_visibility: Post-submission visibility policy.
            hard_deadline_at: Absolute UTC deadline.
            relative_duration_seconds: Optional relative countdown seconds.
            raw_token: 256-bit raw URL-safe token.
            batch_id: Optional cohort batch ID.
            now: Creation UTC timestamp.

        Returns:
            Validated ExecutionAssignment domain model.
        """
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        deadline_utc = ExecutionAssignmentService._ensure_utc(hard_deadline_at)
        return ExecutionAssignment(
            id=generate_uuid7_opaque_id(EntityPrefix.ASSIGNMENT),
            batch_id=batch_id,
            organization_id=org.id,
            assigned_email=normalized_email,
            assigned_user_id=None,
            invited_role=invited_role,
            workflow_id=workflow_id,
            output_profile_id=output_profile_id,
            task_brief_id=task_brief_id,
            target_locale=target_locale,
            locked_inputs=locked_inputs,
            assignee_input_keys=list(assignee_input_keys),
            draft_inputs=WorkflowInputs(dynamic_inputs={}),
            token_hash=token_hash,
            status=AssignmentStatus.PENDING,
            email_delivery_status=EmailDeliveryStatus.PENDING,
            result_visibility=result_visibility,
            hard_deadline_at=deadline_utc,
            relative_duration_seconds=relative_duration_seconds,
            activated_at=None,
            submitted_at=None,
            execution_id=None,
            created_by=initiator.id,
            created_at=now,
        )

    @staticmethod
    def _build_assignment_email(
        *,
        org: Organization,
        assignment: ExecutionAssignment,
        raw_token: str,
        recipient_name: str | None = None,
    ) -> TransactionalEmailItemDTO:
        """Construct a localized TransactionalEmailItemDTO for a task assignment.

        Args:
            org: Issuing Organization model.
            assignment: ExecutionAssignment model.
            raw_token: Raw single-use token for the /task/<token> URL.
            recipient_name: Optional recipient display name.

        Returns:
            TransactionalEmailItemDTO with SecretStr-wrapped action_url.
        """
        base_url = get_settings().frontend_app_base_url.rstrip("/")
        action_url = f"{base_url}/task/{raw_token}"
        deadline_str = assignment.hard_deadline_at.isoformat()
        if assignment.relative_duration_seconds is not None:
            minutes = assignment.relative_duration_seconds // 60
            schedule_label_fi = f"määräaika: {deadline_str} ({minutes} min)"
            schedule_label_en = f"deadline: {deadline_str} ({minutes} min)"
        else:
            schedule_label_fi = f"määräaika: {deadline_str}"
            schedule_label_en = f"deadline: {deadline_str}"
        if assignment.target_locale == SystemLocale.FI:
            subject = f"Tehtäväkutsu organisaatiolta {org.name}"
            html_body = (
                f"<p>Organisaatio <strong>{org.name}</strong> on osoittanut sinulle tehtävän ({schedule_label_fi}).</p>"
            )
        else:
            subject = f"Task assignment from {org.name}"
            html_body = f"<p><strong>{org.name}</strong> has assigned you a workflow task ({schedule_label_en}).</p>"
        return TransactionalEmailItemDTO(
            entity_id=assignment.id,
            recipient_email=assignment.assigned_email,
            recipient_name=recipient_name,
            locale=assignment.target_locale,
            subject=subject,
            html_body=html_body,
            action_url=SecretStr(action_url),
        )

    async def _dispatch_and_persist_single_assignment(
        self,
        *,
        org: Organization,
        assignment: ExecutionAssignment,
        raw_token: str,
    ) -> ExecutionAssignment:
        """Send the transactional assignment email and persist the updated assignment record.

        Args:
            org: Issuing Organization model.
            assignment: Draft or rotated ExecutionAssignment model.
            raw_token: Raw 256-bit assignment token.

        Returns:
            Persisted ExecutionAssignment with updated email_delivery_status.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
        """
        email_item = self._build_assignment_email(
            org=org,
            assignment=assignment,
            raw_token=raw_token,
        )
        email_result = await self.email_service.send_assignment_emails([email_item])
        delivery_status = (
            email_result.delivery_statuses[assignment.id]
            if assignment.id in email_result.delivery_statuses
            else EmailDeliveryStatus.FAILED
        )
        persisted = assignment.model_copy(update={"email_delivery_status": delivery_status})
        await self._save_assignment(persisted)
        self._last_generated_tokens[persisted.id] = raw_token
        return persisted

    async def _verify_onboarding_firebase_token(
        self,
        *,
        firebase_token: str | None,
        expected_email: str,
    ) -> str | None:
        """Verify Firebase ID token + mandatory 2FA claim during JIT assignee onboarding.

        Args:
            firebase_token: Optional Firebase ID token string from onboarding payload.
            expected_email: Assigned recipient email on the task assignment.

        Returns:
            Verified Firebase UID string if Firebase verification ran, else None.

        Raises:
            AuthenticationError: With ErrorCodes.MFA_REQUIRED or AUTHENTICATION_FAILED if invalid.
            PermissionDeniedError: With ErrorCodes.IDENTITY_MISMATCH if token email mismatches.
        """
        settings = get_settings()
        if self.token_service is not None and self.token_service.use_firebase:
            if not firebase_token:
                logger.error(
                    "[ExecutionAssignmentService] %s: Missing firebase_token during onboarding.",
                    ErrorCodes.AUTHENTICATION_FAILED.name,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value},
                )
                raise AuthenticationError(
                    message="Firebase ID token is required for assignee onboarding.",
                    details={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value},
                )
            fb_auth = self.token_service.firebase_auth
            try:
                async with asyncio.timeout(settings.email_http_timeout_seconds):
                    decoded = await asyncio.to_thread(fb_auth.verify_id_token, firebase_token)
            except AppException:
                raise
            except Exception as exc:
                logger.error(
                    "[ExecutionAssignmentService] %s: Firebase token verification failed: %s",
                    ErrorCodes.AUTHENTICATION_FAILED.name,
                    exc,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value},
                )
                raise AuthenticationError(
                    message="Invalid Firebase ID token.",
                    details={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value},
                ) from exc
            if "email" in decoded and decoded["email"]:
                token_email = str(decoded["email"]).strip().lower()
                if token_email != expected_email.lower():
                    logger.error(
                        "[ExecutionAssignmentService] %s: Onboarding token email '%s' != '%s'.",
                        ErrorCodes.IDENTITY_MISMATCH.name,
                        mask_email_address(token_email),
                        mask_email_address(expected_email),
                        exc_info=True,
                        extra={"error_code": ErrorCodes.IDENTITY_MISMATCH.value},
                    )
                    raise PermissionDeniedError(
                        message="Authenticated Firebase email does not match assignment recipient.",
                        details={"error_code": ErrorCodes.IDENTITY_MISMATCH.value},
                    )
            uid_str: str | None = None
            if "uid" in decoded and decoded["uid"]:
                uid_str = str(decoded["uid"]).strip()
            if uid_str and ("email_verified" not in decoded or not bool(decoded["email_verified"])):
                async with asyncio.timeout(settings.email_http_timeout_seconds):
                    update_res = await asyncio.to_thread(fb_auth.update_user, uid_str, email_verified=True)
                    if inspect.iscoroutine(update_res):
                        await update_res
            self.token_service._enforce_firebase_mfa_claim(decoded, settings)
            return uid_str
        return None

    async def _provision_or_bind_assignee_user(
        self,
        *,
        assignment: ExecutionAssignment,
        display_name: str | None,
        firebase_uid: str | None,
        now: datetime,
    ) -> User:
        """Provision a new MEMBER user or bind an unassigned existing user for the assignment.

        Args:
            assignment: Target ExecutionAssignment model.
            display_name: Optional user display name.
            firebase_uid: Optional verified Firebase UID.
            now: Current UTC timestamp.

        Returns:
            Persisted User model bound to assignment.organization_id.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
            ConflictError: With ErrorCodes.USER_ALREADY_ASSIGNED if user belongs to another org.
        """
        existing = await self.user_repo.get_by_email(str(assignment.assigned_email))
        if existing is not None and existing.deleted_at is None:
            if existing.organization_id is not None and existing.organization_id != assignment.organization_id:
                logger.error(
                    "[ExecutionAssignmentService] %s: Onboarding collision for user '%s' (org='%s').",
                    ErrorCodes.USER_ALREADY_ASSIGNED.name,
                    existing.id,
                    existing.organization_id,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.USER_ALREADY_ASSIGNED.value},
                )
                raise ConflictError(
                    message="User already belongs to another organization.",
                    details={"error_code": ErrorCodes.USER_ALREADY_ASSIGNED.value, "user_id": existing.id},
                )
            updated_name = display_name if display_name is not None else existing.name
            await self.user_repo.update(
                existing.id,
                UserUpdate(
                    organization_id=assignment.organization_id,
                    role=assignment.invited_role,
                    name=updated_name,
                    is_active=True,
                ),
            )
            bound = existing.model_copy(
                update={
                    "organization_id": assignment.organization_id,
                    "role": assignment.invited_role,
                    "name": updated_name,
                    "is_active": True,
                    "firebase_uid": firebase_uid if firebase_uid is not None else existing.firebase_uid,
                }
            )
            async with self._acquire_entity_port(commit=True) as port:
                await port.upsert_user(bound)
            return bound

        resolved_name = display_name if display_name is not None else str(assignment.assigned_email).split("@")[0]
        new_user = User(
            id=generate_opaque_id(EntityPrefix.USER),
            email=assignment.assigned_email,
            name=resolved_name,
            role=assignment.invited_role,
            organization_id=assignment.organization_id,
            firebase_uid=firebase_uid,
            is_active=True,
            created_at=now,
            language=assignment.target_locale,
            theme_mode="system",
        )
        await self.user_repo.create(new_user)
        async with self._acquire_entity_port(commit=True) as port:
            await port.upsert_user(new_user)
        return new_user

    @staticmethod
    def _issue_local_jwt_for_user(user: User) -> TokenExchangeResponseDTO:
        """Issue a signed 15-minute Quorum Local JWT for an onboarded assignee.

        Args:
            user: Provisioned or bound User model.

        Returns:
            TokenExchangeResponseDTO with signed access_token and user profile.
        """
        settings = get_settings()
        expire_seconds = settings.jwt_access_token_expire_minutes * 60
        now_epoch = int(time.time())
        signed_jwt = jwt.encode(
            {
                "sub": user.id,
                "org": user.organization_id,
                "role": user.role.value,
                "email": str(user.email),
                "mfa": True,
                "jti": str(generate_uuid7()),
                "iat": now_epoch,
                "exp": now_epoch + expire_seconds,
                "type": "access",
            },
            settings.jwt_secret_key.get_secret_value(),
            algorithm=settings.jwt_algorithm,
        )
        return TokenExchangeResponseDTO(
            access_token=signed_jwt,
            token_type="bearer",
            expires_in_seconds=expire_seconds,
            user=user,
        )

    async def _verify_assignee_identity(
        self,
        *,
        initiator: TokenData,
        assignment: ExecutionAssignment,
    ) -> None:
        """Verify that the authenticated caller's email and organization match the assignment.

        Args:
            initiator: Caller TokenData.
            assignment: Target ExecutionAssignment model.

        Raises:
            PermissionDeniedError: With ErrorCodes.IDENTITY_MISMATCH if caller email does not match.
            ConflictError: With ErrorCodes.USER_ALREADY_ASSIGNED if caller belongs to a different org.
        """
        caller_email: str | None = initiator.email
        if caller_email is None:
            user = await self.user_repo.get_by_id(initiator.id)
            if user is not None:
                caller_email = str(user.email)

        if caller_email is None or caller_email.strip().lower() != str(assignment.assigned_email).strip().lower():
            masked_caller = "***"
            if caller_email is not None:
                masked_caller = mask_email_address(caller_email)
            logger.error(
                "[ExecutionAssignmentService] %s: Caller '%s' (email='%s') mismatched assignment '%s' ('%s').",
                ErrorCodes.IDENTITY_MISMATCH.name,
                initiator.id,
                masked_caller,
                assignment.id,
                mask_email_address(str(assignment.assigned_email)),
                exc_info=True,
                extra={"error_code": ErrorCodes.IDENTITY_MISMATCH.value},
            )
            raise PermissionDeniedError(
                message="Authenticated user identity does not match the assigned recipient email.",
                details={
                    "error_code": ErrorCodes.IDENTITY_MISMATCH.value,
                    "assignment_id": assignment.id,
                },
            )

        if initiator.organization_id is not None and initiator.organization_id != assignment.organization_id:
            logger.error(
                "[ExecutionAssignmentService] %s: Caller '%s' belongs to org '%s' != assignment org '%s'.",
                ErrorCodes.USER_ALREADY_ASSIGNED.name,
                initiator.id,
                initiator.organization_id,
                assignment.organization_id,
                exc_info=True,
                extra={"error_code": ErrorCodes.USER_ALREADY_ASSIGNED.value},
            )
            raise ConflictError(
                message="Authenticated user belongs to a different organization.",
                details={
                    "error_code": ErrorCodes.USER_ALREADY_ASSIGNED.value,
                    "assignment_id": assignment.id,
                },
            )

    async def _assert_not_hard_expired(
        self,
        *,
        assignment: ExecutionAssignment,
        now: datetime,
    ) -> None:
        """Verify the assignment has not passed its absolute hard_deadline_at or been revoked.

        Args:
            assignment: Target ExecutionAssignment model.
            now: Current server UTC timestamp.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
            AppException: With ErrorCodes.ASSIGNMENT_EXPIRED if expired or revoked.
        """
        hard_deadline = self._ensure_utc(assignment.hard_deadline_at)
        if assignment.status in (AssignmentStatus.EXPIRED, AssignmentStatus.REVOKED) or now > hard_deadline:
            if assignment.status not in (AssignmentStatus.EXPIRED, AssignmentStatus.REVOKED) and now > hard_deadline:
                await self._save_assignment(assignment.model_copy(update={"status": AssignmentStatus.EXPIRED}))
            logger.error(
                "[ExecutionAssignmentService] %s: Assignment '%s' expired (hard_deadline_at=%s, now=%s).",
                ErrorCodes.ASSIGNMENT_EXPIRED.name,
                assignment.id,
                hard_deadline.isoformat(),
                now.isoformat(),
                exc_info=True,
                extra={"error_code": ErrorCodes.ASSIGNMENT_EXPIRED.value},
            )
            raise AppException(
                message="Task assignment has expired.",
                status_code=410,
                details={
                    "error_code": ErrorCodes.ASSIGNMENT_EXPIRED.value,
                    "assignment_id": assignment.id,
                },
            )

    async def _assert_within_dual_clock_deadline(
        self,
        *,
        assignment: ExecutionAssignment,
        now: datetime,
        include_grace: bool,
    ) -> None:
        """Enforce Dual-Clock Expiration: min(hard_deadline_at, activated_at + relative_duration_seconds).

        Args:
            assignment: Target ExecutionAssignment model.
            now: Current server UTC timestamp.
            include_grace: Whether to add assignment_submission_grace_seconds to effective_expires_at.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
            AppException: With ErrorCodes.ASSIGNMENT_EXPIRED if current time exceeds deadline.
        """
        effective_expires_at = self.compute_effective_expires_at(assignment)
        cutoff = effective_expires_at
        if include_grace:
            cutoff = effective_expires_at + timedelta(seconds=get_settings().assignment_submission_grace_seconds)

        if assignment.status in (AssignmentStatus.EXPIRED, AssignmentStatus.REVOKED) or now > cutoff:
            if assignment.status not in (AssignmentStatus.EXPIRED, AssignmentStatus.REVOKED):
                await self._save_assignment(assignment.model_copy(update={"status": AssignmentStatus.EXPIRED}))
            logger.error(
                "[ExecutionAssignmentService] %s: Assignment '%s' exceeded dual-clock cutoff (%s > %s).",
                ErrorCodes.ASSIGNMENT_EXPIRED.name,
                assignment.id,
                now.isoformat(),
                cutoff.isoformat(),
                exc_info=True,
                extra={"error_code": ErrorCodes.ASSIGNMENT_EXPIRED.value},
            )
            raise AppException(
                message="Task assignment deadline has expired.",
                status_code=410,
                details={
                    "error_code": ErrorCodes.ASSIGNMENT_EXPIRED.value,
                    "assignment_id": assignment.id,
                },
            )

    @staticmethod
    def compute_effective_expires_at(assignment: ExecutionAssignment) -> datetime:
        """Compute server-authoritative Dual-Clock expiration timestamp.

        Formula: min(hard_deadline_at, activated_at + relative_duration_seconds)
        when both activated_at and relative_duration_seconds are present, else hard_deadline_at.

        Args:
            assignment: ExecutionAssignment domain model.

        Returns:
            Timezone-aware UTC effective expiration timestamp.
        """
        hard_deadline = ExecutionAssignmentService._ensure_utc(assignment.hard_deadline_at)
        if assignment.relative_duration_seconds is not None and assignment.activated_at is not None:
            activated_utc = ExecutionAssignmentService._ensure_utc(assignment.activated_at)
            relative_deadline = activated_utc + timedelta(seconds=assignment.relative_duration_seconds)
            return min(hard_deadline, relative_deadline)
        return hard_deadline

    async def _trigger_assignment_execution(
        self,
        *,
        initiator: TokenData,
        assignment: ExecutionAssignment,
        submitted_inputs: WorkflowInputs,
        arq_pool: ArqRedis,
        doc_service: DocumentExtractionService | None,
    ) -> ExecutionRecord:
        """Merge manager locked_inputs over submitted_inputs and invoke ExecutionIngressService.

        Args:
            initiator: Authenticated assignee TokenData.
            assignment: Validated ExecutionAssignment model.
            submitted_inputs: Assignee-submitted WorkflowInputs.
            arq_pool: Arq Redis pool.
            doc_service: Optional DocumentExtractionService.

        Returns:
            Created ExecutionRecord from ExecutionIngressService.start_execution.

        Raises:
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if workflow or profile is missing.
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if workflow access is denied.
            AppException: With ErrorCodes.VALIDATION_FAILED or RATE_LIMIT_EXCEEDED on ingress validation failure.
        """
        merged_inputs = merge_assignment_inputs(
            locked_inputs=assignment.locked_inputs,
            submitted_inputs=submitted_inputs,
            assignee_input_keys=assignment.assignee_input_keys,
            organization_id=assignment.organization_id,
            user_id=initiator.id,
            language=assignment.target_locale.value,
        )
        effective_initiator = initiator.model_copy(update={"organization_id": assignment.organization_id})
        exec_create = ExecutionCreate(
            workflow_id=assignment.workflow_id,
            target_locale=assignment.target_locale.value,
            profile_id=assignment.output_profile_id,
            matrix_sampling_strategy=get_settings().matrix_sampling_limit,
            raw_inputs=merged_inputs,
        )
        return await self.ingress_service.start_execution(
            initiator=effective_initiator,
            payload=exec_create,
            arq_pool=arq_pool,
            doc_service=doc_service,
        )

    @staticmethod
    def _verify_manager_or_admin_for_org(*, initiator: TokenData, org_id: str) -> None:
        """Verify caller is ROOT or an ADMIN/MANAGER belonging to org_id.

        Args:
            initiator: Caller TokenData.
            org_id: Target organization ID.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if unauthorized.
        """
        if initiator.role == UserRole.ROOT:
            return
        if initiator.role in (UserRole.ADMIN, UserRole.MANAGER) and initiator.organization_id == org_id:
            return
        logger.error(
            "[ExecutionAssignmentService] %s: Caller '%s' denied management access to org '%s'.",
            ErrorCodes.PERMISSION_DENIED.name,
            initiator.id,
            org_id,
            exc_info=True,
            extra={"error_code": ErrorCodes.PERMISSION_DENIED.value},
        )
        raise PermissionDeniedError("Insufficient permissions to manage assignments for this organization.")

    async def _fetch_org_or_raise(self, org_id: str) -> Organization:
        """Fetch an Organization by ID or raise ResourceNotFoundError.

        Args:
            org_id: Organization identifier (org_<hex32>).

        Returns:
            Organization domain model.

        Raises:
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if organization is missing.
        """
        org = await self.org_repo.get_by_id(org_id)
        if org is None:
            logger.error(
                "[ExecutionAssignmentService] %s: Organization '%s' not found.",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                org_id,
                exc_info=True,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )
            raise ResourceNotFoundError(resource_type="organization", resource_id=org_id)
        return org

    async def _get_assignment_or_raise(self, assignment_id: str) -> ExecutionAssignment:
        """Fetch an ExecutionAssignment by ID or raise ResourceNotFoundError.

        Args:
            assignment_id: Canonical Task Assignment ID (tsk_<hex32>).

        Returns:
            ExecutionAssignment domain model.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if assignment does not exist.
        """
        async with self._acquire_entity_port() as port:
            persisted = await port.get_execution_assignment(assignment_id)
        if persisted is not None:
            return persisted
        logger.error(
            "[ExecutionAssignmentService] %s: Assignment '%s' not found.",
            ErrorCodes.RESOURCE_NOT_FOUND.name,
            assignment_id,
            exc_info=True,
            extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
        )
        raise ResourceNotFoundError(resource_type="execution_assignment", resource_id=assignment_id)

    async def _save_assignment(self, assignment: ExecutionAssignment) -> None:
        """Persist an ExecutionAssignment via the acquired EntityPersistencePort.

        Args:
            assignment: Validated ExecutionAssignment domain model.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
        """
        async with self._acquire_entity_port(commit=True) as port:
            await port.upsert_execution_assignment(assignment)

    async def _list_all_assignments(self, organization_id: str | None = None) -> list[ExecutionAssignment]:
        """List all persisted execution assignments via the acquired EntityPersistencePort.

        Args:
            organization_id: Optional organization filter.

        Returns:
            List of ExecutionAssignment models.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
        """
        async with self._acquire_entity_port() as port:
            return await port.list_execution_assignments(organization_id=organization_id)

    async def _find_assignment_by_token_hash(self, token_hash: str) -> ExecutionAssignment | None:
        """Locate an ExecutionAssignment matching the SHA-256 token digest in constant time.

        Args:
            token_hash: 64-character hex SHA-256 digest of the raw assignment token.

        Returns:
            Matching ExecutionAssignment or None.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
        """
        persisted = await self._list_all_assignments()
        for item in persisted:
            if secrets.compare_digest(item.token_hash, token_hash):
                return item
        return None

    async def _resolve_assignment_by_raw_token_or_raise(
        self,
        raw_token: str,
        *,
        context_label: str,
    ) -> ExecutionAssignment:
        """Hash a raw assignment token with SHA-256 and resolve the matching assignment or fail fast.

        Args:
            raw_token: Raw URL-safe assignment token string.
            context_label: Diagnostic operation label for structured RFC 7807 error logging.

        Returns:
            Matching ExecutionAssignment domain model.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if no persistence backend is configured.
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if token digest is unknown.
        """
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        assignment = await self._find_assignment_by_token_hash(token_hash)
        if assignment is None:
            logger.error(
                "[ExecutionAssignmentService] %s: %s token digest not found.",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                context_label,
                exc_info=True,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )
            raise ResourceNotFoundError(resource_type="execution_assignment", resource_id="token")
        return assignment

    async def _log_audit(
        self,
        *,
        actor_id: str,
        action: str,
        organization_id: str,
        target_id: str,
        **details: str | int | float | bool | None,
    ) -> None:
        """Record an audit log event if audit_service is configured.

        Args:
            actor_id: User ID performing the action.
            action: Audit action identifier.
            organization_id: Organization ID scope.
            target_id: Target entity ID.
            **details: Structured primitive audit metadata keyword arguments.
        """
        if self.audit_service is not None:
            await self.audit_service.log_event(
                actor_id=actor_id,
                action=action,
                organization_id=organization_id,
                target_id=target_id,
                details=details,
            )

    async def _validate_and_resolve_task_brief(
        self,
        task_brief_id: str | None,
        organization_id: str,
        *,
        strict: bool = True,
    ) -> TaskAssignmentBriefDTO | None:
        """Validate and resolve a Task Definition PromptBlock into a TaskAssignmentBriefDTO.

        Args:
            task_brief_id: Optional PromptBlock identifier (blk_<hex32>).
            organization_id: Owning organization identifier of the assignment.
            strict: Whether to fail fast with AppException if the block is missing or invalid.

        Returns:
            Hydrated TaskAssignmentBriefDTO or None.

        Raises:
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if block is missing and strict is True.
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if block belongs to another tenant.
            AppException: With ErrorCodes.SERVICE_DEPENDENCY_MISSING if repository is missing or
                ErrorCodes.VALIDATION_FAILED if category_id is not TASK_DEFINITION.
        """
        if task_brief_id is None:
            return None
        if self.prompt_block_repo is None:
            if not strict:
                return None
            logger.error(
                "[ExecutionAssignmentService] %s: PromptBlock repository is required to resolve task_brief_id '%s'.",
                ErrorCodes.SERVICE_DEPENDENCY_MISSING.name,
                task_brief_id,
                exc_info=True,
                extra={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.value},
            )
            raise AppException(
                message="PromptBlock repository is required to resolve task_brief_id.",
                status_code=500,
                details={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.value},
            )

        block = await self.prompt_block_repo.get_prompt_block_by_id(task_brief_id)
        if block is None:
            if not strict:
                return None
            logger.error(
                "[ExecutionAssignmentService] %s: Task brief PromptBlock '%s' not found.",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                task_brief_id,
                exc_info=True,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )
            raise ResourceNotFoundError(resource_type="prompt_block", resource_id=task_brief_id)

        allowed_orgs = {None, SystemOrganizations.ROOT_SYSTEM.value, organization_id}
        if block.organization_id not in allowed_orgs:
            if not strict:
                return None
            logger.error(
                "[ExecutionAssignmentService] %s: Task brief '%s' org '%s' not accessible to org '%s'.",
                ErrorCodes.PERMISSION_DENIED.name,
                task_brief_id,
                block.organization_id,
                organization_id,
                exc_info=True,
                extra={"error_code": ErrorCodes.PERMISSION_DENIED.value},
            )
            raise PermissionDeniedError(
                f"Task brief '{task_brief_id}' does not belong to organization '{organization_id}'."
            )

        if not isinstance(block, SystemRulePromptBlock) or block.category_id != PromptBlockCategory.TASK_DEFINITION:
            if not strict:
                return None
            logger.error(
                "[ExecutionAssignmentService] %s: PromptBlock '%s' category '%s' != TASK_DEFINITION.",
                ErrorCodes.VALIDATION_FAILED.name,
                task_brief_id,
                block.category_id,
                exc_info=True,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(
                message=f"PromptBlock '{task_brief_id}' must have category 'task_definition'.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        source_url: str | None = None
        if block.theory_grounding is not None:
            source_url = block.theory_grounding.source_url
        return TaskAssignmentBriefDTO(
            id=block.id,
            label=block.label,
            instruction_text=block.instruction_text,
            source_url=source_url,
        )

    @staticmethod
    async def _normalize_assignee_ingress_inputs(
        raw_inputs: WorkflowInputsIngress | WorkflowInputs,
        doc_service: DocumentExtractionService | None,
    ) -> WorkflowInputs:
        """Extract any Base64Attachment items from assignee ingress inputs into domain WorkflowInputs.

        Args:
            raw_inputs: Assignee draft or submitted workflow inputs (ingress or domain).
            doc_service: Optional DocumentExtractionService for binary decoding and text extraction.

        Returns:
            Validated WorkflowInputs with zero Base64Attachment payloads.

        Raises:
            AppException: With ErrorCodes.SERVICE_DEPENDENCY_MISSING if Base64Attachment is present
                without doc_service, or ErrorCodes.VALIDATION_FAILED on extraction failure.
        """
        if isinstance(raw_inputs, WorkflowInputs):
            return raw_inputs

        has_attachments = any(isinstance(v, Base64Attachment) for v in raw_inputs.dynamic_inputs.values())
        if has_attachments:
            if doc_service is None:
                logger.error(
                    "[ExecutionAssignmentService] %s: DocumentExtractionService required for Base64Attachment inputs.",
                    ErrorCodes.SERVICE_DEPENDENCY_MISSING.name,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.value},
                )
                raise AppException(
                    message="DocumentExtractionService is required to extract Base64Attachment inputs.",
                    status_code=500,
                    details={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.value},
                )
            processed = await doc_service.process_ingress_payload(raw_inputs)
        else:
            processed = raw_inputs

        return WorkflowInputs.model_validate(processed.model_dump(exclude_unset=True))

    async def _to_hydrated_assignment_response(
        self,
        assignment: ExecutionAssignment,
    ) -> ExecutionAssignmentResponseDTO:
        """Resolve optional TaskAssignmentBriefDTO and project an ExecutionAssignment into a response DTO.

        Args:
            assignment: ExecutionAssignment domain model.

        Returns:
            Hydrated ExecutionAssignmentResponseDTO.
        """
        task_brief = await self._validate_and_resolve_task_brief(
            assignment.task_brief_id,
            assignment.organization_id,
            strict=False,
        )
        return self._to_assignment_response(assignment, task_brief=task_brief)

    @staticmethod
    def _to_assignment_response(
        assignment: ExecutionAssignment,
        *,
        task_brief: TaskAssignmentBriefDTO | None = None,
    ) -> ExecutionAssignmentResponseDTO:
        """Project an ExecutionAssignment domain model into a redacted ExecutionAssignmentResponseDTO.

        Args:
            assignment: ExecutionAssignment domain model.
            task_brief: Optional hydrated TaskAssignmentBriefDTO.

        Returns:
            ExecutionAssignmentResponseDTO excluding token_hash.
        """
        return ExecutionAssignmentResponseDTO(
            id=assignment.id,
            batch_id=assignment.batch_id,
            organization_id=assignment.organization_id,
            assigned_email=assignment.assigned_email,
            assigned_user_id=assignment.assigned_user_id,
            invited_role=assignment.invited_role,
            workflow_id=assignment.workflow_id,
            output_profile_id=assignment.output_profile_id,
            task_brief_id=assignment.task_brief_id,
            task_brief=task_brief,
            target_locale=assignment.target_locale,
            locked_inputs=assignment.locked_inputs,
            assignee_input_keys=list(assignment.assignee_input_keys),
            draft_inputs=assignment.draft_inputs,
            status=assignment.status,
            email_delivery_status=assignment.email_delivery_status,
            result_visibility=assignment.result_visibility,
            hard_deadline_at=assignment.hard_deadline_at,
            relative_duration_seconds=assignment.relative_duration_seconds,
            activated_at=assignment.activated_at,
            submitted_at=assignment.submitted_at,
            execution_id=assignment.execution_id,
            created_by=assignment.created_by,
            created_at=assignment.created_at,
        )
