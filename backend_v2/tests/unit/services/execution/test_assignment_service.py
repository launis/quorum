"""Unit and ISTQB BVA tests for ExecutionAssignmentService and assignment endpoints."""

from __future__ import annotations

import base64
import logging
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest
from arq import ArqRedis

from backend_v2.api.routers.execution.executions import (
    activate_execution_assignment,
    create_execution_assignment,
    create_execution_assignment_batch,
    list_execution_assignments,
    onboard_execution_assignee,
    preview_execution_assignment,
    resend_execution_assignment_email,
    save_execution_assignment_draft,
    submit_execution_assignment,
)
from backend_v2.database.interfaces import EntityPersistencePort
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
    ExecutionAssignmentCreateDTO,
    ExecutionAssignmentDraftDTO,
    ExecutionAssignmentOnboardingRequestDTO,
    ExecutionAssignmentRecipientDTO,
    ExecutionAssignmentSubmitDTO,
    Organization,
    SubscriptionStatus,
    SystemOrganizations,
    TaskAssignmentBriefDTO,
    TokenData,
    User,
    UserRole,
)
from backend_v2.models.core_base import I18nText, generate_opaque_id
from backend_v2.models.domain.inputs import (
    Base64Attachment,
    WorkflowInputs,
    WorkflowInputsIngress,
)
from backend_v2.models.domain.step import ExpectedInput, Step, StepRule
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
from backend_v2.models.dtos.matrix_scorecard import ScorecardAtomDTO
from backend_v2.models.enums import (
    AssignmentResultVisibility,
    AssignmentStatus,
    EmailDeliveryStatus,
    EntityPrefix,
    ExecutionStatus,
    HistoricalContextMode,
    StepType,
    SystemLocale,
    VisualIntent,
)
from backend_v2.services.auth.email_service import EmailService
from backend_v2.services.auth.repositories import OrganizationRepository, UserRepository
from backend_v2.services.auth.token_service import TokenService
from backend_v2.services.document_extraction import DocumentExtractionService
from backend_v2.services.execution import (
    ExecutionAssignmentService,
    ExecutionIngressService,
    ExecutionService,
)
from backend_v2.services.execution.assignment_service import (
    AuditEventLoggerProtocol,
    mask_email_address,
)
from backend_v2.settings import get_settings
from backend_v2.tests.factories.model_factories import (
    ExecutionStepFactory,
    OutputProfileFactory,
    TaskBriefFactory,
    WorkflowFactory,
)
from backend_v2.tests.fakes.in_memory_repositories import (
    InMemoryIdentityRepository,
    InMemorySystemRepository,
    InMemoryUnifiedWorkflowRepository,
)
from backend_v2.tests.fakes.in_memory_uow import InMemoryUnitOfWork

ORG_ALPHA_ID = "org_0195f3a0000070008000000000000010"
ORG_BETA_ID = "org_0195f3a0000070008000000000000020"
WORKFLOW_ID = "wor_0195f3a0000070008123456789abcdef"
PROFILE_ID = "prf_0195f3a0000070008123456789abcdef"
STEP_ID = "stp_0195f3a0000070008123456789abcdef"
MANAGER_ID = "usr_0195f3a0000070008000000000000101"
ADMIN_ID = "usr_0195f3a0000070008000000000000102"
ASSIGNEE_ID = "usr_0195f3a0000070008000000000000201"
INTRUDER_ID = "usr_0195f3a0000070008000000000000202"


@dataclass
class RecordedAuditEvent:
    """In-memory captured audit event record for stateful verification."""

    actor_id: str
    action: str
    organization_id: str
    target_id: str
    details: Mapping[str, str | int | float | bool | None]


@dataclass
class InMemoryAuditEventLogger:
    """Hermetic in-memory AuditEventLoggerProtocol test double."""

    events: list[RecordedAuditEvent] = field(default_factory=list)

    async def log_event(
        self,
        *,
        actor_id: str,
        action: str,
        organization_id: str,
        target_id: str,
        details: Mapping[str, str | int | float | bool | None],
    ) -> None:
        """Append a structured audit event to the in-memory ledger."""
        self.events.append(
            RecordedAuditEvent(
                actor_id=actor_id,
                action=action,
                organization_id=organization_id,
                target_id=target_id,
                details=details,
            )
        )


def _build_workflow() -> Workflow:
    """Construct a valid test Workflow via WorkflowFactory with locked and assignee input slots.

    Returns:
        Validated Workflow domain model.
    """
    return WorkflowFactory.build(
        id=WORKFLOW_ID,
        slug="assignment-workflow",
        name=I18nText(translations={"en": "Assignment Workflow", "fi": "Tehtävätyönkulku"}),
        description=I18nText(translations={"en": "Assignment Workflow Description", "fi": "Kuvaus"}),
        status="active",
        version=1,
        default_strictness_level=50,
        model_registry_id="mrg_0195f3a00000700e826807f3bfa3454d",
        historical_context_mode=HistoricalContextMode.DISABLED,
        expected_inputs=[
            ExpectedInput(
                input_key="manager_context",
                label=I18nText(translations={"en": "Manager Context", "fi": "Esihenkilön konteksti"}),
                required=True,
                is_chat_history=False,
                input_modes=["paste"],
                description=I18nText(translations={"en": "Manager Context", "fi": "Konteksti"}),
                questionnaire_definition=[],
            ),
            ExpectedInput(
                input_key="candidate_answer",
                label=I18nText(translations={"en": "Candidate Answer", "fi": "Kandidaatin vastaus"}),
                required=True,
                is_chat_history=False,
                input_modes=["paste"],
                description=I18nText(translations={"en": "Candidate Answer", "fi": "Vastaus"}),
                questionnaire_definition=[],
            ),
        ],
        steps=[
            StepRule(
                id=STEP_ID,
                task_blueprint=STEP_ID,
                depends_on=[],
                input_mappings={},
            )
        ],
        default_profile_id=PROFILE_ID,
        organization_id=ORG_ALPHA_ID,
        is_public=False,
    )


async def _setup_assignment_harness(
    allowed_domains: list[str] | None = None,
) -> tuple[
    ExecutionAssignmentService,
    ExecutionService,
    InMemoryUnifiedWorkflowRepository,
    InMemoryIdentityRepository,
    EmailService,
    EntityPersistencePort,
]:
    """Create a complete hermetic in-memory harness for ExecutionAssignmentService tests.

    Args:
        allowed_domains: Optional list of allowed email domains for ORG_ALPHA_ID.

    Returns:
        Tuple of (assignment_service, execution_service, workflow_repo, identity_repo, email_service, entity_adapter).
    """
    wf_repo = InMemoryUnifiedWorkflowRepository()
    await wf_repo.save_workflow(_build_workflow())
    await wf_repo.save_step(
        Step(
            organization_id="org_0195f3a0000070008000000000000001",
            id=STEP_ID,
            slug="eval-step",
            name=I18nText(translations={"en": "Eval Step", "fi": "Arviointi"}),
            type=StepType.LOGIC,
            hook="my_hook",
            mcp_tool_params={},
            criteria_block_ids=[],
            pre_hooks=[],
            post_hooks=[],
            allowed_mcp_tools=[],
            expected_inputs=[],
        )
    )
    await wf_repo.save_output_profile(
        OutputProfileFactory.build(
            id=PROFILE_ID,
            slug="eval-profile",
            name=I18nText(translations={"en": "Eval Profile", "fi": "Profiili"}),
            workflow_id=WORKFLOW_ID,
            organization_id=ORG_ALPHA_ID,
            target_block_order=[],
            visible_block_extensions=[],
            visible_workflow_extensions=[],
            visible_metadata=[],
            matrix_visible_columns=[],
            matrix_synthesis_groups=[],
            content_blocks=[],
        )
    )
    system_repo = InMemorySystemRepository()
    identity_repo = InMemoryIdentityRepository()
    await identity_repo.create_organization(
        Organization(
            id=ORG_ALPHA_ID,
            name="Alpha Corp",
            created_at=datetime.now(UTC),
            is_active=True,
            tier="enterprise",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=500.0,
            tpm_limit=100000,
            rpm_limit=100,
            allowed_email_domains=allowed_domains if allowed_domains is not None else [],
        )
    )
    await identity_repo.create_organization(
        Organization(
            id=ORG_BETA_ID,
            name="Beta Corp",
            created_at=datetime.now(UTC),
            is_active=True,
            tier="enterprise",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=500.0,
            tpm_limit=100000,
            rpm_limit=100,
            allowed_email_domains=[],
        )
    )

    usage_service = AsyncMock()
    usage_service.check_quota = AsyncMock(return_value=True)

    ingress_service = ExecutionIngressService(
        exec_repo=wf_repo,
        workflow_repo=wf_repo,
        prompt_block_repo=wf_repo,
        output_profile_repo=wf_repo,
        system_repo=system_repo,
        usage_service=usage_service,
    )
    user_repo = UserRepository(identity_repo)
    org_repo = OrganizationRepository(identity_repo)
    email_service = EmailService()
    uow = InMemoryUnitOfWork()
    entity_adapter = uow.entities
    token_service = TokenService(repo=user_repo, use_firebase=False)

    assignment_service = ExecutionAssignmentService(
        ingress_service=ingress_service,
        org_repo=org_repo,
        user_repo=user_repo,
        workflow_repo=wf_repo,
        token_service=token_service,
        email_service=email_service,
        entity_adapter=entity_adapter,
        prompt_block_repo=wf_repo,
        task_brief_repo=wf_repo,
    )
    execution_service = ExecutionService(
        exec_repo=wf_repo,
        workflow_repo=wf_repo,
        prompt_block_repo=wf_repo,
        task_brief_repo=wf_repo,
        output_profile_repo=wf_repo,
        identity_repo=identity_repo,
        system_repo=system_repo,
        usage_service=usage_service,
        assignment_service=assignment_service,
        email_service=email_service,
        entity_adapter=entity_adapter,
    )
    return assignment_service, execution_service, wf_repo, identity_repo, email_service, entity_adapter


def _manager_token() -> TokenData:
    """Return a TokenData fixture for an Alpha Corp MANAGER."""
    return TokenData(
        id=MANAGER_ID,
        role=UserRole.MANAGER,
        organization_id=ORG_ALPHA_ID,
        email="manager@alpha.fi",
    )


def _assignee_token(email: str = "participant@alpha.fi") -> TokenData:
    """Return a TokenData fixture for an Alpha Corp MEMBER assignee."""
    return TokenData(
        id=ASSIGNEE_ID,
        role=UserRole.MEMBER,
        organization_id=ORG_ALPHA_ID,
        email=email,
    )


@pytest.mark.asyncio
async def test_assignment_preview_safelinks_idempotent_positive() -> None:
    """Verify repeated GET preview calls are 100% side-effect-free and never start countdown."""
    assignment_service, _, _, _, email_service, _ = await _setup_assignment_harness()
    deadline = datetime.now(UTC) + timedelta(hours=24)

    created = await assignment_service.create_assignment(
        initiator=_manager_token(),
        payload=ExecutionAssignmentCreateDTO(
            assigned_email="participant@alpha.fi",
            invited_role=UserRole.MEMBER,
            workflow_id=WORKFLOW_ID,
            output_profile_id=PROFILE_ID,
            target_locale=SystemLocale.FI,
            locked_inputs=WorkflowInputs(dynamic_inputs={"manager_context": "Locked brief"}),
            assignee_input_keys=["candidate_answer"],
            result_visibility=AssignmentResultVisibility.CONFIRMATION_ONLY,
            hard_deadline_at=deadline,
            relative_duration_seconds=1800,
        ),
    )
    assert created.status == AssignmentStatus.PENDING
    assert created.activated_at is None
    assert created.email_delivery_status == EmailDeliveryStatus.SENT
    assert len(email_service.console_outbox) == 1

    raw_token = assignment_service.get_last_generated_token(created.id)
    assert raw_token is not None

    # Simulate 3 consecutive SafeLinks / Proofpoint email scanner GET prefetches
    for _ in range(3):
        preview = await assignment_service.preview_assignment(raw_token)
        assert preview.id == created.id
        assert preview.organization_id == ORG_ALPHA_ID
        assert preview.organization_name == "Alpha Corp"
        assert preview.assigned_email_masked == "p***@alpha.fi"
        assert preview.status == AssignmentStatus.PENDING
        assert preview.relative_duration_seconds == 1800

    # Verify stored assignment remains PENDING with activated_at=None
    listed = await assignment_service.list_assignments(_manager_token())
    assert len(listed) == 1
    assert listed[0].status == AssignmentStatus.PENDING
    assert listed[0].activated_at is None


@pytest.mark.asyncio
async def test_assignment_activate_identity_mismatch_negative(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify POST .../activate by a user with mismatched email logs IDENTITY_MISMATCH and raises 403."""
    assignment_service, _, _, _, _, _ = await _setup_assignment_harness()
    created = await assignment_service.create_assignment(
        initiator=_manager_token(),
        payload=ExecutionAssignmentCreateDTO(
            assigned_email="participant@alpha.fi",
            workflow_id=WORKFLOW_ID,
            locked_inputs=WorkflowInputs(dynamic_inputs={}),
            assignee_input_keys=[],
            hard_deadline_at=datetime.now(UTC) + timedelta(hours=24),
        ),
    )

    intruder = TokenData(
        id=INTRUDER_ID,
        role=UserRole.MEMBER,
        organization_id=ORG_ALPHA_ID,
        email="wrong.person@alpha.fi",
    )
    caplog.clear()
    with caplog.at_level(logging.ERROR), pytest.raises(PermissionDeniedError) as exc_info:
        await assignment_service.activate_assignment(initiator=intruder, assignment_id=created.id)

    assert exc_info.value.status_code == 403
    assert ErrorCodes.IDENTITY_MISMATCH.name in caplog.text
    assert "wrong.person@alpha.fi" not in caplog.text
    assert "participant@alpha.fi" not in caplog.text
    assert "w***@alpha.fi" in caplog.text
    assert "p***@alpha.fi" in caplog.text


@pytest.mark.asyncio
async def test_assignment_submit_dual_clock_expiration_bva_boundary(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify Dual-Clock BVA at effective_expires_at - 1s, +0s, +grace, and +grace + 1s."""
    assignment_service, _, _, _, _, _ = await _setup_assignment_harness()
    grace_seconds = 60
    relative_seconds = 600
    hard_deadline = datetime.now(UTC) + timedelta(hours=12)

    offsets_and_outcomes: list[tuple[int, bool]] = [
        (-1, True),
        (0, True),
        (grace_seconds, True),
        (grace_seconds + 1, False),
    ]

    for idx, (offset_sec, should_succeed) in enumerate(offsets_and_outcomes):
        email = f"bva{idx}@alpha.fi"
        created = await assignment_service.create_assignment(
            initiator=_manager_token(),
            payload=ExecutionAssignmentCreateDTO(
                assigned_email=email,
                workflow_id=WORKFLOW_ID,
                output_profile_id=PROFILE_ID,
                locked_inputs=WorkflowInputs(dynamic_inputs={"manager_context": "Brief"}),
                assignee_input_keys=["candidate_answer"],
                hard_deadline_at=hard_deadline,
                relative_duration_seconds=relative_seconds,
            ),
        )
        assignee = _assignee_token(email=email)
        activated = await assignment_service.activate_assignment(
            initiator=assignee,
            assignment_id=created.id,
        )
        assert activated.activated_at is not None
        effective_expires_at = activated.activated_at + timedelta(seconds=relative_seconds)
        simulated_now = effective_expires_at + timedelta(seconds=offset_sec)

        submit_dto = ExecutionAssignmentSubmitDTO(
            submitted_inputs=WorkflowInputs(dynamic_inputs={"candidate_answer": f"Response {idx}"})
        )
        if should_succeed:
            record = await assignment_service.submit_assignment(
                initiator=assignee,
                assignment_id=created.id,
                payload=submit_dto,
                arq_pool=AsyncMock(spec=ArqRedis),
                now_override=simulated_now,
            )
            assert record.id.startswith("exe_")
        else:
            with caplog.at_level(logging.ERROR), pytest.raises(AppException) as exc_info:
                await assignment_service.submit_assignment(
                    initiator=assignee,
                    assignment_id=created.id,
                    payload=submit_dto,
                    arq_pool=AsyncMock(spec=ArqRedis),
                    now_override=simulated_now,
                )
            assert exc_info.value.status_code == 410
            assert ErrorCodes.ASSIGNMENT_EXPIRED.name in caplog.text


@pytest.mark.asyncio
async def test_assignment_submit_replay_already_submitted_negative(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify a second submit call logs ASSIGNMENT_ALREADY_SUBMITTED and raises 409 ConflictError."""
    assignment_service, _, _, _, _, _ = await _setup_assignment_harness()
    created = await assignment_service.create_assignment(
        initiator=_manager_token(),
        payload=ExecutionAssignmentCreateDTO(
            assigned_email="participant@alpha.fi",
            workflow_id=WORKFLOW_ID,
            output_profile_id=PROFILE_ID,
            locked_inputs=WorkflowInputs(dynamic_inputs={"manager_context": "Immutable brief"}),
            assignee_input_keys=["candidate_answer"],
            hard_deadline_at=datetime.now(UTC) + timedelta(hours=4),
        ),
    )
    assignee = _assignee_token()
    await assignment_service.activate_assignment(initiator=assignee, assignment_id=created.id)

    submit_dto = ExecutionAssignmentSubmitDTO(
        submitted_inputs=WorkflowInputs(
            dynamic_inputs={
                "candidate_answer": "My first submission",
                "manager_context": "Attempted tampering",
            }
        )
    )
    first_record = await assignment_service.submit_assignment(
        initiator=assignee,
        assignment_id=created.id,
        payload=submit_dto,
        arq_pool=AsyncMock(spec=ArqRedis),
    )
    # Verify locked_inputs cannot be overridden by assignee
    assert first_record.raw_inputs.dynamic_inputs["manager_context"] == "Immutable brief"
    assert first_record.raw_inputs.dynamic_inputs["candidate_answer"] == "My first submission"

    # Replay attempt must fail with 409 ConflictError
    with caplog.at_level(logging.ERROR), pytest.raises(ConflictError) as exc_info:
        await assignment_service.submit_assignment(
            initiator=assignee,
            assignment_id=created.id,
            payload=submit_dto,
            arq_pool=AsyncMock(spec=ArqRedis),
        )
    assert exc_info.value.status_code == 409
    assert ErrorCodes.ASSIGNMENT_ALREADY_SUBMITTED.name in caplog.text


@pytest.mark.asyncio
async def test_assignment_batch_creation_and_collision_guards(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify cohort batch creation, deduplication, domain allowlist, and 1:1 collision guard."""
    assignment_service, _, _, identity_repo, email_service, _ = await _setup_assignment_harness(
        allowed_domains=["alpha.fi"]
    )
    deadline = datetime.now(UTC) + timedelta(hours=24)

    # 1. Domain allowlist violation rejects entire batch before persisting any row
    with pytest.raises(PermissionDeniedError):
        await assignment_service.create_assignment_batch(
            initiator=_manager_token(),
            payload=ExecutionAssignmentBatchCreateDTO(
                recipients=[
                    ExecutionAssignmentRecipientDTO(email="valid@alpha.fi"),
                    ExecutionAssignmentRecipientDTO(email="outside@rogue.com"),
                ],
                workflow_id=WORKFLOW_ID,
                locked_inputs=WorkflowInputs(dynamic_inputs={}),
                assignee_input_keys=[],
                hard_deadline_at=deadline,
            ),
        )
    assert len(await assignment_service.list_assignments(_manager_token())) == 0

    # 2. Cross-tenant 1:1 Identity Collision Guard rejects batch if user belongs to ORG_BETA_ID
    await identity_repo.create_user(
        User(
            id="usr_0195f3a0000070008000000000000999",
            email="taken@alpha.fi",
            name="Beta Member",
            role=UserRole.MEMBER,
            organization_id=ORG_BETA_ID,
            is_active=True,
            created_at=datetime.now(UTC),
            language=SystemLocale.FI,
            theme_mode="system",
        )
    )
    with caplog.at_level(logging.ERROR), pytest.raises(ConflictError) as exc_info:
        await assignment_service.create_assignment_batch(
            initiator=_manager_token(),
            payload=ExecutionAssignmentBatchCreateDTO(
                recipients=[
                    ExecutionAssignmentRecipientDTO(email="valid@alpha.fi"),
                    ExecutionAssignmentRecipientDTO(email="taken@alpha.fi"),
                ],
                workflow_id=WORKFLOW_ID,
                locked_inputs=WorkflowInputs(dynamic_inputs={}),
                assignee_input_keys=[],
                hard_deadline_at=deadline,
            ),
        )
    assert exc_info.value.status_code == 409
    assert ErrorCodes.USER_ALREADY_ASSIGNED.name in caplog.text
    assert len(await assignment_service.list_assignments(_manager_token())) == 0

    # 3. Valid batch deduplicates emails, assigns shared batch_id, and dispatches emails
    batch_res = await assignment_service.create_assignment_batch(
        initiator=_manager_token(),
        payload=ExecutionAssignmentBatchCreateDTO(
            recipients=[
                ExecutionAssignmentRecipientDTO(email="one@alpha.fi", name="User One"),
                ExecutionAssignmentRecipientDTO(email="ONE@alpha.fi", name="Duplicate One"),
                ExecutionAssignmentRecipientDTO(
                    email="two@alpha.fi",
                    name="User Two",
                    target_locale=SystemLocale.EN,
                ),
            ],
            workflow_id=WORKFLOW_ID,
            locked_inputs=WorkflowInputs(dynamic_inputs={}),
            assignee_input_keys=[],
            hard_deadline_at=deadline,
            relative_duration_seconds=900,
        ),
    )
    assert batch_res.created_count == 2
    assert batch_res.batch_id.startswith("tsk_")
    assert all(a.batch_id == batch_res.batch_id for a in batch_res.assignments)
    assert batch_res.assignments[0].id != batch_res.assignments[1].id
    assert len(email_service.console_outbox) == 2


@pytest.mark.asyncio
async def test_assignment_role_scope_and_deadline_validation_negative() -> None:
    """Verify MANAGER cannot assign ADMIN role, MEMBER cannot create assignments, and past deadline fails."""
    assignment_service, _, _, _, _, _ = await _setup_assignment_harness()
    future_deadline = datetime.now(UTC) + timedelta(hours=12)

    # MANAGER cannot assign ADMIN
    with pytest.raises(PermissionDeniedError):
        await assignment_service.create_assignment(
            initiator=_manager_token(),
            payload=ExecutionAssignmentCreateDTO(
                assigned_email="cand@alpha.fi",
                invited_role=UserRole.ADMIN,
                workflow_id=WORKFLOW_ID,
                locked_inputs=WorkflowInputs(dynamic_inputs={}),
                assignee_input_keys=[],
                hard_deadline_at=future_deadline,
            ),
        )

    # Non-ROOT ADMIN cannot assign ROOT
    admin_token = TokenData(
        id=ADMIN_ID,
        role=UserRole.ADMIN,
        organization_id=ORG_ALPHA_ID,
        email="admin@alpha.fi",
    )
    with pytest.raises(PermissionDeniedError):
        await assignment_service.create_assignment(
            initiator=admin_token,
            payload=ExecutionAssignmentCreateDTO(
                assigned_email="cand@alpha.fi",
                invited_role=UserRole.ROOT,
                workflow_id=WORKFLOW_ID,
                locked_inputs=WorkflowInputs(dynamic_inputs={}),
                assignee_input_keys=[],
                hard_deadline_at=future_deadline,
            ),
        )

    # MEMBER cannot create assignments
    with pytest.raises(PermissionDeniedError):
        await assignment_service.create_assignment(
            initiator=_assignee_token(),
            payload=ExecutionAssignmentCreateDTO(
                assigned_email="cand@alpha.fi",
                workflow_id=WORKFLOW_ID,
                locked_inputs=WorkflowInputs(dynamic_inputs={}),
                assignee_input_keys=[],
                hard_deadline_at=future_deadline,
            ),
        )

    # Past hard_deadline_at rejected with 400 VALIDATION_FAILED
    with pytest.raises(AppException) as exc_info:
        await assignment_service.create_assignment(
            initiator=_manager_token(),
            payload=ExecutionAssignmentCreateDTO(
                assigned_email="cand@alpha.fi",
                workflow_id=WORKFLOW_ID,
                locked_inputs=WorkflowInputs(dynamic_inputs={}),
                assignee_input_keys=[],
                hard_deadline_at=datetime.now(UTC) - timedelta(minutes=5),
            ),
        )
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_assignment_jit_onboarding_draft_and_confirmation_only_visibility() -> None:
    """Verify JIT onboarding + 2FA, draft checkpointing, resend, and CONFIRMATION_ONLY report redaction."""
    assignment_service, execution_service, wf_repo, _, _, _ = await _setup_assignment_harness()
    deadline = datetime.now(UTC) + timedelta(hours=12)

    created = await execution_service.create_assignment(
        initiator=_manager_token(),
        payload=ExecutionAssignmentCreateDTO(
            assigned_email="newhire@alpha.fi",
            workflow_id=WORKFLOW_ID,
            output_profile_id=PROFILE_ID,
            locked_inputs=WorkflowInputs(dynamic_inputs={"manager_context": "Confidential Context"}),
            assignee_input_keys=["candidate_answer"],
            result_visibility=AssignmentResultVisibility.CONFIRMATION_ONLY,
            hard_deadline_at=deadline,
            relative_duration_seconds=1200,
        ),
    )

    # Resend rotates token
    first_token = assignment_service.get_last_generated_token(created.id)
    resent = await execution_service.resend_assignment_email(
        initiator=_manager_token(),
        assignment_id=created.id,
    )
    second_token = assignment_service.get_last_generated_token(resent.id)
    assert second_token is not None
    assert second_token != first_token

    # Saving draft before activation is rejected
    onboard_res = await execution_service.onboard_assignee(
        raw_token=second_token,
        payload=ExecutionAssignmentOnboardingRequestDTO(name="New Hire"),
    )
    assert onboard_res.user.email == "newhire@alpha.fi"
    assert onboard_res.user.organization_id == ORG_ALPHA_ID
    assert onboard_res.user.role == UserRole.MEMBER
    assert len(onboard_res.access_token) > 20

    assignee_tok = TokenData(
        id=onboard_res.user.id,
        role=UserRole.MEMBER,
        organization_id=ORG_ALPHA_ID,
        email="newhire@alpha.fi",
    )

    with pytest.raises(AppException) as draft_err:
        await execution_service.save_draft_inputs(
            initiator=assignee_tok,
            assignment_id=created.id,
            payload=ExecutionAssignmentDraftDTO(
                draft_inputs=WorkflowInputs(dynamic_inputs={"candidate_answer": "Draft 1"})
            ),
        )
    assert draft_err.value.status_code == 400

    # Activate assignment (idempotent on second call)
    act1 = await execution_service.activate_assignment(initiator=assignee_tok, assignment_id=created.id)
    act2 = await execution_service.activate_assignment(initiator=assignee_tok, assignment_id=created.id)
    assert act1.status == AssignmentStatus.ACTIVATED
    assert act1.activated_at == act2.activated_at

    # Save draft checkpoint
    saved_draft = await execution_service.save_draft_inputs(
        initiator=assignee_tok,
        assignment_id=created.id,
        payload=ExecutionAssignmentDraftDTO(
            draft_inputs=WorkflowInputs(dynamic_inputs={"candidate_answer": "Checkpoint text"})
        ),
    )
    assert saved_draft.draft_inputs.dynamic_inputs["candidate_answer"] == "Checkpoint text"

    # Submit assignment
    submitted_record = await execution_service.submit_assignment(
        initiator=assignee_tok,
        assignment_id=created.id,
        payload=ExecutionAssignmentSubmitDTO(
            submitted_inputs=WorkflowInputs(dynamic_inputs={"candidate_answer": "Final answer"})
        ),
        arq_pool=AsyncMock(spec=ArqRedis),
    )

    # Simulate completed execution with forensic synthesis and scorecard atoms in repository
    populated_step = ExecutionStepFactory.build(
        id=STEP_ID,
        label="Eval Step",
        status=ExecutionStatus.PASSED,
        scorecard_atoms={
            "tda_0195f3a0000070008123456789abcdef": ScorecardAtomDTO(
                atom_id="tda_0195f3a0000070008123456789abcdef",
                level=1,
                level_name="Foundation",
                claim_label="Clarity",
                extracted_facts={},
                exact_quotes=[],
                internal_logic_en=ReasoningStepDTO(
                    step_1_identify_premise="Premise",
                    step_2_scan_source="Scan",
                    step_3_evaluate_anti_patterns="None",
                    step_4_final_conclusion="Passed",
                ),
                status=ExecutionStatus.PASSED,
                semantic_reasoning="Strong analytical structure.",
                contextual_override=False,
                structural_location=None,
                chart_display_label="Clarity",
                visual_intent=VisualIntent.NEUTRAL,
            )
        },
    )
    enriched_record = submitted_record.model_copy(
        update={
            "pdf_report_path": "reports/confidential.pdf",
            "profile_syntheses": {
                PROFILE_ID: RenderedSynthesisCache(
                    section_syntheses={},
                    row_explanations={"blk_0195f3a0000070008123456789abcdef": "Confidential Manager Synthesis"},
                    row_curated_quotes={},
                    cited_sources=[],
                    xai_highlights=[],
                    created_at=datetime.now(UTC),
                )
            },
            "steps": [populated_step],
            "step_states": {STEP_ID: populated_step},
        }
    )
    await wf_repo.save_execution(enriched_record)

    # MEMBER assignee sees redacted confirmation-only record
    member_view = await execution_service.get_execution(
        initiator=assignee_tok,
        execution_id=submitted_record.id,
    )
    assert member_view.pdf_report_path is None
    assert member_view.profile_syntheses == {}
    assert member_view.steps[0].scorecard_atoms == {}

    # MANAGER sees full forensic report
    manager_view = await execution_service.get_execution(
        initiator=_manager_token(),
        execution_id=submitted_record.id,
    )
    assert manager_view.pdf_report_path == "reports/confidential.pdf"
    assert PROFILE_ID in manager_view.profile_syntheses
    assert len(manager_view.steps[0].scorecard_atoms) == 1


@pytest.mark.asyncio
async def test_assignment_firebase_onboarding_mfa_and_router_endpoints(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify Firebase 2FA enforcement during onboarding and router endpoint delegation."""
    mfa_settings = get_settings().model_copy(update={"require_mfa": True})
    monkeypatch.setattr(
        "backend_v2.services.execution.assignment_service.get_settings",
        lambda: mfa_settings,
    )
    assignment_service, execution_service, _, _, _, _ = await _setup_assignment_harness()
    deadline = datetime.now(UTC) + timedelta(hours=8)

    # Exercise router endpoints directly
    created = await create_execution_assignment(
        payload=ExecutionAssignmentCreateDTO(
            assigned_email="router.user@alpha.fi",
            workflow_id=WORKFLOW_ID,
            output_profile_id=PROFILE_ID,
            locked_inputs=WorkflowInputs(dynamic_inputs={"manager_context": "Router context"}),
            assignee_input_keys=["candidate_answer"],
            hard_deadline_at=deadline,
        ),
        current_user=_manager_token(),
        execution_service=execution_service,
    )
    batch = await create_execution_assignment_batch(
        payload=ExecutionAssignmentBatchCreateDTO(
            recipients=[ExecutionAssignmentRecipientDTO(email="batch.router@alpha.fi")],
            workflow_id=WORKFLOW_ID,
            locked_inputs=WorkflowInputs(dynamic_inputs={}),
            assignee_input_keys=[],
            hard_deadline_at=deadline,
        ),
        current_user=_manager_token(),
        execution_service=execution_service,
    )
    assert batch.created_count == 1

    all_listed = await list_execution_assignments(
        current_user=_manager_token(),
        execution_service=execution_service,
    )
    assert len(all_listed) == 2

    resent = await resend_execution_assignment_email(
        assignment_id=created.id,
        current_user=_manager_token(),
        execution_service=execution_service,
    )
    raw_token = assignment_service.get_last_generated_token(resent.id)
    assert raw_token is not None

    preview = await preview_execution_assignment(
        token=raw_token,
        execution_service=execution_service,
    )
    assert preview.id == created.id

    # Enable Firebase mode on token_service to test MFA_REQUIRED and IDENTITY_MISMATCH on onboarding
    assert assignment_service.token_service is not None
    mock_fb = AsyncMock()
    assignment_service.token_service.use_firebase = True
    assignment_service.token_service.firebase_auth = mock_fb

    # Missing 2FA claim raises MFA_REQUIRED
    mock_fb.verify_id_token = lambda tok: {
        "uid": "fb_uid_1",
        "email": "router.user@alpha.fi",
        "firebase": {},
    }
    with pytest.raises(AuthenticationError) as mfa_exc:
        await onboard_execution_assignee(
            token=raw_token,
            payload=ExecutionAssignmentOnboardingRequestDTO(
                firebase_token="valid_length_firebase_token",
                name="Router User",
            ),
            execution_service=execution_service,
        )
    assert mfa_exc.value.details["error_code"] == ErrorCodes.MFA_REQUIRED.value

    # Mismatched Firebase email raises PermissionDeniedError (IDENTITY_MISMATCH)
    mock_fb.verify_id_token = lambda tok: {
        "uid": "fb_uid_1",
        "email": "other.email@alpha.fi",
        "firebase": {"sign_in_second_factor": "totp"},
    }
    with pytest.raises(PermissionDeniedError):
        await onboard_execution_assignee(
            token=raw_token,
            payload=ExecutionAssignmentOnboardingRequestDTO(
                firebase_token="valid_length_firebase_token",
                name="Router User",
            ),
            execution_service=execution_service,
        )

    # Valid 2FA claim succeeds
    mock_fb.verify_id_token = lambda tok: {
        "uid": "fb_uid_1",
        "email": "router.user@alpha.fi",
        "firebase": {"sign_in_second_factor": "totp"},
    }
    onboarded = await onboard_execution_assignee(
        token=raw_token,
        payload=ExecutionAssignmentOnboardingRequestDTO(
            firebase_token="valid_length_firebase_token",
            name="Router User",
        ),
        execution_service=execution_service,
    )
    router_user_token = TokenData(
        id=onboarded.user.id,
        role=UserRole.MEMBER,
        organization_id=ORG_ALPHA_ID,
        email="router.user@alpha.fi",
    )

    activated = await activate_execution_assignment(
        assignment_id=created.id,
        current_user=router_user_token,
        execution_service=execution_service,
    )
    assert activated.status == AssignmentStatus.ACTIVATED

    draft_res = await save_execution_assignment_draft(
        assignment_id=created.id,
        payload=ExecutionAssignmentDraftDTO(
            draft_inputs=WorkflowInputs(dynamic_inputs={"candidate_answer": "Draft via router"})
        ),
        current_user=router_user_token,
        execution_service=execution_service,
        doc_service=AsyncMock(),
    )
    assert draft_res.draft_inputs.dynamic_inputs["candidate_answer"] == "Draft via router"

    exec_rec = await submit_execution_assignment(
        assignment_id=created.id,
        payload=ExecutionAssignmentSubmitDTO(
            submitted_inputs=WorkflowInputs(dynamic_inputs={"candidate_answer": "Submitted via router"})
        ),
        arq_pool=AsyncMock(spec=ArqRedis),
        current_user=router_user_token,
        execution_service=execution_service,
        doc_service=AsyncMock(),
    )
    assert exec_rec.id.startswith("exe_")
    assert mask_email_address("invalid_email") == "***"
    assert mask_email_address("@alpha.fi") == "***@alpha.fi"


@pytest.mark.asyncio
async def test_assignment_edge_and_negative_branches() -> None:
    """Exercise remaining negative, RBAC, persistence fallback, and audit branches."""
    assignment_service, _, _, identity_repo, _, _ = await _setup_assignment_harness()
    audit_logger = InMemoryAuditEventLogger()
    assert isinstance(audit_logger, AuditEventLoggerProtocol)
    assignment_service.audit_service = audit_logger

    assert assignment_service.get_last_generated_token("tsk_0195f3a0000070008000000000000000") is None

    # Unknown preview & onboarding tokens raise ResourceNotFoundError
    with pytest.raises(ResourceNotFoundError):
        await assignment_service.preview_assignment("unknown_raw_token_value_12345")
    with pytest.raises(ResourceNotFoundError):
        await assignment_service.onboard_assignee(
            "unknown_raw_token_value_12345",
            ExecutionAssignmentOnboardingRequestDTO(name="Nobody"),
        )
    with pytest.raises(ResourceNotFoundError):
        await assignment_service.activate_assignment(
            initiator=_assignee_token(),
            assignment_id="tsk_0195f3a0000070008000000000000999",
        )

    # Manager without organization_id raises PermissionDeniedError
    no_org_manager = TokenData(id=MANAGER_ID, role=UserRole.MANAGER, organization_id=None, email="m@alpha.fi")
    with pytest.raises(PermissionDeniedError):
        await assignment_service.create_assignment(
            initiator=no_org_manager,
            payload=ExecutionAssignmentCreateDTO(
                assigned_email="participant@alpha.fi",
                workflow_id=WORKFLOW_ID,
                locked_inputs=WorkflowInputs(dynamic_inputs={}),
                assignee_input_keys=[],
                hard_deadline_at=datetime.now(UTC) + timedelta(hours=4),
            ),
        )

    # Create a valid assignment
    created = await assignment_service.create_assignment(
        initiator=_manager_token(),
        payload=ExecutionAssignmentCreateDTO(
            assigned_email="participant@alpha.fi",
            workflow_id=WORKFLOW_ID,
            output_profile_id=PROFILE_ID,
            locked_inputs=WorkflowInputs(dynamic_inputs={"manager_context": "Context"}),
            assignee_input_keys=["candidate_answer"],
            hard_deadline_at=datetime.now(UTC) + timedelta(hours=4),
        ),
    )
    assert len(audit_logger.events) == 1
    assert audit_logger.events[0].action == "ASSIGNMENT_CREATED"
    assert audit_logger.events[0].target_id == created.id
    raw_token = assignment_service.get_last_generated_token(created.id)
    assert raw_token is not None

    # Exercise entity_adapter persistence lookup branches
    preview = await assignment_service.preview_assignment(raw_token)
    assert preview.id == created.id

    fetched_list_root = await assignment_service.list_assignments(
        TokenData(id="usr_0195f3a0000070008000000000000001", role=UserRole.ROOT, organization_id=None)
    )
    assert len(fetched_list_root) == 1

    fetched_list_member = await assignment_service.list_assignments(_assignee_token())
    assert len(fetched_list_member) == 1

    # Unauthorized org manager cannot resend
    beta_manager = TokenData(id=MANAGER_ID, role=UserRole.MANAGER, organization_id=ORG_BETA_ID)
    with pytest.raises(PermissionDeniedError):
        await assignment_service.resend_assignment_email(beta_manager, created.id)

    # Root can resend
    await assignment_service.resend_assignment_email(
        TokenData(id="usr_0195f3a0000070008000000000000001", role=UserRole.ROOT, organization_id=None),
        created.id,
    )
    rotated_token = assignment_service.get_last_generated_token(created.id)
    assert rotated_token is not None

    # Pre-create existing user in same org to exercise existing-user bind path in _provision_or_bind_assignee_user
    await identity_repo.create_user(
        User(
            id=ASSIGNEE_ID,
            email="participant@alpha.fi",
            name="Existing Participant",
            role=UserRole.MEMBER,
            organization_id=ORG_ALPHA_ID,
            is_active=True,
            created_at=datetime.now(UTC),
            language=SystemLocale.FI,
            theme_mode="system",
        )
    )
    onboarded = await assignment_service.onboard_assignee(
        rotated_token,
        ExecutionAssignmentOnboardingRequestDTO(name="Updated Participant"),
    )
    assert onboarded.user.name == "Updated Participant"

    # Caller with email=None resolves email via user_repo.get_by_id
    token_without_email = TokenData(id=ASSIGNEE_ID, role=UserRole.MEMBER, organization_id=ORG_ALPHA_ID, email=None)
    await assignment_service.activate_assignment(token_without_email, created.id)

    # Caller from wrong org with matching email raises ConflictError (USER_ALREADY_ASSIGNED)
    wrong_org_token = TokenData(
        id=ASSIGNEE_ID,
        role=UserRole.MEMBER,
        organization_id=ORG_BETA_ID,
        email="participant@alpha.fi",
    )
    with pytest.raises(ConflictError):
        await assignment_service.activate_assignment(wrong_org_token, created.id)

    # Submit the assignment
    record = await assignment_service.submit_assignment(
        initiator=_assignee_token(),
        assignment_id=created.id,
        payload=ExecutionAssignmentSubmitDTO(
            submitted_inputs=WorkflowInputs(dynamic_inputs={"candidate_answer": "Done"})
        ),
        arq_pool=AsyncMock(spec=ArqRedis),
    )

    # Exercise get_assignment_by_execution_id from entity_adapter (hit + miss)
    by_exec = await assignment_service.get_assignment_by_execution_id(record.id)
    assert by_exec is not None
    assert by_exec.id == created.id
    assert await assignment_service.get_assignment_by_execution_id("exe_0195f3a0000070008000000000009999") is None

    # Resend, activate, and save_draft on already-submitted assignment raise 409 ConflictError
    with pytest.raises(ConflictError):
        await assignment_service.resend_assignment_email(_manager_token(), created.id)
    with pytest.raises(ConflictError):
        await assignment_service.activate_assignment(_assignee_token(), created.id)
    with pytest.raises(ConflictError):
        await assignment_service.save_draft_inputs(
            _assignee_token(),
            created.id,
            ExecutionAssignmentDraftDTO(draft_inputs=WorkflowInputs(dynamic_inputs={})),
        )

    # Firebase onboarding missing token and invalid token branches
    assert assignment_service.token_service is not None
    assignment_service.token_service.use_firebase = True
    mock_fb = AsyncMock()
    assignment_service.token_service.firebase_auth = mock_fb

    created2 = await assignment_service.create_assignment(
        initiator=_manager_token(),
        payload=ExecutionAssignmentCreateDTO(
            assigned_email="fb.edge@alpha.fi",
            workflow_id=WORKFLOW_ID,
            locked_inputs=WorkflowInputs(dynamic_inputs={}),
            assignee_input_keys=[],
            hard_deadline_at=datetime.now(UTC) + timedelta(hours=2),
        ),
    )
    tok2 = assignment_service.get_last_generated_token(created2.id)
    assert tok2 is not None

    with pytest.raises(AuthenticationError):
        await assignment_service.onboard_assignee(
            tok2,
            ExecutionAssignmentOnboardingRequestDTO(firebase_token=None, name="FB Edge"),
        )

    def _raise_fb(_t: str) -> dict[str, str]:
        raise RuntimeError("Invalid token")

    mock_fb.verify_id_token = _raise_fb
    with pytest.raises(AuthenticationError):
        await assignment_service.onboard_assignee(
            tok2,
            ExecutionAssignmentOnboardingRequestDTO(firebase_token="bad_firebase_token_value", name="FB Edge"),
        )


@pytest.mark.asyncio
async def test_assignment_uow_factory_roundtrip_and_unconfigured_persistence_negative(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify transactional uow_factory persistence roundtrip and Fail-Fast ConfigurationError when unconfigured."""
    base_service, _, _, identity_repo, email_service, _ = await _setup_assignment_harness()
    monkeypatch.setattr(
        "backend_v2.services.execution.assignment_service.get_registered_uow_factory",
        lambda: None,
    )

    # 1. Negative: Unconfigured persistence fails fast with ConfigurationError + RFC 7807 log
    unconfigured = ExecutionAssignmentService(
        ingress_service=base_service.ingress_service,
        org_repo=base_service.org_repo,
        user_repo=base_service.user_repo,
        workflow_repo=base_service.workflow_repo,
        token_service=base_service.token_service,
        email_service=email_service,
        entity_adapter=None,
        uow_factory=None,
    )
    with caplog.at_level(logging.ERROR), pytest.raises(ConfigurationError) as cfg_err:
        await unconfigured.list_assignments(_manager_token())
    assert cfg_err.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value
    assert ErrorCodes.CONFIGURATION_ERROR.name in caplog.text

    # 2. Positive: Transactional uow_factory stateful roundtrip + FULL_PORTAL visibility
    uow = InMemoryUnitOfWork()
    uow_service = ExecutionAssignmentService(
        ingress_service=base_service.ingress_service,
        org_repo=base_service.org_repo,
        user_repo=base_service.user_repo,
        workflow_repo=base_service.workflow_repo,
        token_service=base_service.token_service,
        email_service=email_service,
        entity_adapter=None,
        uow_factory=lambda: uow,
    )
    created = await uow_service.create_assignment(
        initiator=_manager_token(),
        payload=ExecutionAssignmentCreateDTO(
            assigned_email="uow.user@alpha.fi",
            workflow_id=WORKFLOW_ID,
            output_profile_id=PROFILE_ID,
            locked_inputs=WorkflowInputs(dynamic_inputs={"manager_context": "UoW Brief"}),
            assignee_input_keys=["candidate_answer"],
            result_visibility=AssignmentResultVisibility.FULL_REPORT_ACCESS,
            hard_deadline_at=datetime.now(UTC) + timedelta(hours=6),
        ),
    )
    raw_token = uow_service.get_last_generated_token(created.id)
    assert raw_token is not None

    onboarded = await uow_service.onboard_assignee(
        raw_token,
        ExecutionAssignmentOnboardingRequestDTO(name="UoW Assignee"),
    )
    assert onboarded.user.email == "uow.user@alpha.fi"
    persisted_uow_user = await uow.entities.get_user(onboarded.user.id)
    assert persisted_uow_user is not None
    assert persisted_uow_user.organization_id == ORG_ALPHA_ID

    uow_assignee_tok = TokenData(
        id=onboarded.user.id,
        role=UserRole.MEMBER,
        organization_id=ORG_ALPHA_ID,
        email="uow.user@alpha.fi",
    )
    activated = await uow_service.activate_assignment(uow_assignee_tok, created.id)
    assert activated.status == AssignmentStatus.ACTIVATED

    full_record = await uow_service.submit_assignment(
        initiator=uow_assignee_tok,
        assignment_id=created.id,
        payload=ExecutionAssignmentSubmitDTO(
            submitted_inputs=WorkflowInputs(dynamic_inputs={"candidate_answer": "UoW Submission"})
        ),
        arq_pool=AsyncMock(spec=ArqRedis),
    )
    assert full_record.frozen_context is not None
    fetched_list = await uow_service.list_assignments(_manager_token())
    assert len(fetched_list) == 1
    assert fetched_list[0].status == AssignmentStatus.SUBMITTED
    assert fetched_list[0].execution_id == full_record.id


@pytest.mark.asyncio
async def test_assignment_hard_deadline_bva_cross_org_onboarding_and_root_org_resolution(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify hard_deadline_at expiration state transition, cross-org onboarding collision, and missing org errors."""
    assignment_service, _, _, identity_repo, _, entity_adapter = await _setup_assignment_harness()

    # 1. ROOT without organization_id resolves SystemOrganizations.ROOT_SYSTEM; missing org raises ResourceNotFoundError
    root_token = TokenData(id="usr_0195f3a0000070008000000000000001", role=UserRole.ROOT, organization_id=None)
    with caplog.at_level(logging.ERROR), pytest.raises(ResourceNotFoundError) as not_found_exc:
        await assignment_service.create_assignment(
            initiator=root_token,
            payload=ExecutionAssignmentCreateDTO(
                assigned_email="root.target@alpha.fi",
                workflow_id=WORKFLOW_ID,
                locked_inputs=WorkflowInputs(dynamic_inputs={}),
                assignee_input_keys=[],
                hard_deadline_at=datetime.now(UTC) + timedelta(hours=2),
            ),
        )
    assert not_found_exc.value.status_code == 404
    assert ErrorCodes.RESOURCE_NOT_FOUND.name in caplog.text

    # Seed ROOT_SYSTEM org and verify ROOT with organization_id=None creates assignment cleanly
    await identity_repo.create_organization(
        Organization(
            id=SystemOrganizations.ROOT_SYSTEM,
            name="System Root",
            created_at=datetime.now(UTC),
            is_active=True,
            tier="enterprise",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=500.0,
            tpm_limit=100000,
            rpm_limit=100,
            allowed_email_domains=[],
        )
    )
    root_created = await assignment_service.create_assignment(
        initiator=root_token,
        payload=ExecutionAssignmentCreateDTO(
            assigned_email="root.target@alpha.fi",
            workflow_id=WORKFLOW_ID,
            locked_inputs=WorkflowInputs(dynamic_inputs={}),
            assignee_input_keys=[],
            hard_deadline_at=datetime.now(UTC) + timedelta(hours=2),
        ),
    )
    assert root_created.organization_id == SystemOrganizations.ROOT_SYSTEM

    # 2. Cross-org collision during onboard_assignee when user joins ORG_BETA_ID after assignment creation
    collision_assignment = await assignment_service.create_assignment(
        initiator=_manager_token(),
        payload=ExecutionAssignmentCreateDTO(
            assigned_email="late.collision@alpha.fi",
            workflow_id=WORKFLOW_ID,
            locked_inputs=WorkflowInputs(dynamic_inputs={}),
            assignee_input_keys=[],
            hard_deadline_at=datetime.now(UTC) + timedelta(hours=2),
        ),
    )
    collision_tok = assignment_service.get_last_generated_token(collision_assignment.id)
    assert collision_tok is not None
    await identity_repo.create_user(
        User(
            id="usr_0195f3a0000070008000000000000888",
            email="late.collision@alpha.fi",
            name="Moved To Beta",
            role=UserRole.MEMBER,
            organization_id=ORG_BETA_ID,
            is_active=True,
            created_at=datetime.now(UTC),
            language=SystemLocale.FI,
            theme_mode="system",
        )
    )
    with caplog.at_level(logging.ERROR), pytest.raises(ConflictError) as col_exc:
        await assignment_service.onboard_assignee(
            collision_tok,
            ExecutionAssignmentOnboardingRequestDTO(name="Collision User"),
        )
    assert col_exc.value.details["error_code"] == ErrorCodes.USER_ALREADY_ASSIGNED.value

    # 3. Hard deadline expiration during onboard_assignee transitions stored status to EXPIRED and raises 410
    expiring = await assignment_service.create_assignment(
        initiator=_manager_token(),
        payload=ExecutionAssignmentCreateDTO(
            assigned_email="expiring@alpha.fi",
            workflow_id=WORKFLOW_ID,
            locked_inputs=WorkflowInputs(dynamic_inputs={}),
            assignee_input_keys=[],
            hard_deadline_at=datetime.now(UTC) + timedelta(hours=1),
        ),
    )
    expiring_tok = assignment_service.get_last_generated_token(expiring.id)
    assert expiring_tok is not None
    stored_expiring = await entity_adapter.get_execution_assignment(expiring.id)
    assert stored_expiring is not None
    await entity_adapter.upsert_execution_assignment(
        stored_expiring.model_copy(update={"hard_deadline_at": datetime.now(UTC) - timedelta(seconds=1)})
    )
    with caplog.at_level(logging.ERROR), pytest.raises(AppException) as exp_exc:
        await assignment_service.onboard_assignee(
            expiring_tok,
            ExecutionAssignmentOnboardingRequestDTO(name="Late User"),
        )
    assert exp_exc.value.status_code == 410
    assert exp_exc.value.details["error_code"] == ErrorCodes.ASSIGNMENT_EXPIRED.value
    refreshed_expiring = await entity_adapter.get_execution_assignment(expiring.id)
    assert refreshed_expiring is not None
    assert refreshed_expiring.status == AssignmentStatus.EXPIRED


@pytest.mark.asyncio
async def test_assignment_task_brief_lifecycle_and_rbac_validation(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify task_brief_id persistence, TaskAssignmentBriefDTO projection, and negative RBAC guards."""
    assignment_service, _, wf_repo, identity_repo, _, _ = await _setup_assignment_harness()

    alpha_brief_id = generate_opaque_id(EntityPrefix.TASK_BRIEF)
    await wf_repo.create_task_brief(
        TaskBriefFactory.build(
            id=alpha_brief_id,
            slug="alpha-task-brief",
            label=I18nText(translations={"en": "Alpha Case Study", "fi": "Alpha-tapaustutkimus"}),
            description=I18nText(translations={"en": "Case description", "fi": "Tapauksen kuvaus"}),
            instruction_text="Review section 4 and summarize key risks.",
            source_url="https://docs.qrum.ai/cases/alpha-4",
            organization_id=ORG_ALPHA_ID,
        )
    )

    # 1. Positive: Create single and batch assignments with task_brief_id and verify TaskAssignmentBriefDTO hydration
    created = await assignment_service.create_assignment(
        initiator=_manager_token(),
        payload=ExecutionAssignmentCreateDTO(
            assigned_email="brief.user@alpha.fi",
            workflow_id=WORKFLOW_ID,
            output_profile_id=PROFILE_ID,
            task_brief_id=alpha_brief_id,
            locked_inputs=WorkflowInputs(dynamic_inputs={"manager_context": "Context"}),
            assignee_input_keys=["candidate_answer"],
            hard_deadline_at=datetime.now(UTC) + timedelta(hours=6),
        ),
    )
    assert created.task_brief_id == alpha_brief_id
    assert isinstance(created.task_brief, TaskAssignmentBriefDTO)
    assert created.task_brief.id == alpha_brief_id
    assert created.task_brief.label.translations["en"] == "Alpha Case Study"
    assert created.task_brief.instruction_text == "Review section 4 and summarize key risks."
    assert created.task_brief.source_url == "https://docs.qrum.ai/cases/alpha-4"

    batch_created = await assignment_service.create_assignment_batch(
        initiator=_manager_token(),
        payload=ExecutionAssignmentBatchCreateDTO(
            recipients=[ExecutionAssignmentRecipientDTO(email="batch.brief@alpha.fi", name="Batch Brief")],
            workflow_id=WORKFLOW_ID,
            output_profile_id=PROFILE_ID,
            task_brief_id=alpha_brief_id,
            locked_inputs=WorkflowInputs(dynamic_inputs={"manager_context": "Batch Context"}),
            assignee_input_keys=["candidate_answer"],
            hard_deadline_at=datetime.now(UTC) + timedelta(hours=6),
        ),
    )
    assert batch_created.assignments[0].task_brief_id == alpha_brief_id
    assert batch_created.assignments[0].task_brief is not None
    assert batch_created.assignments[0].task_brief.source_url == "https://docs.qrum.ai/cases/alpha-4"

    raw_tok = assignment_service.get_last_generated_token(created.id)
    assert raw_tok is not None
    preview = await assignment_service.preview_assignment(raw_tok)
    assert preview.task_brief_id == alpha_brief_id
    assert preview.task_brief is not None
    assert preview.task_brief.instruction_text == "Review section 4 and summarize key risks."

    resent = await assignment_service.resend_assignment_email(_manager_token(), created.id)
    assert resent.task_brief is not None
    assert resent.task_brief.id == alpha_brief_id
    rotated_tok = assignment_service.get_last_generated_token(created.id)
    assert rotated_tok is not None

    onboarded = await assignment_service.onboard_assignee(
        rotated_tok,
        ExecutionAssignmentOnboardingRequestDTO(name="Brief User"),
    )
    brief_user_tok = TokenData(
        id=onboarded.user.id,
        role=UserRole.MEMBER,
        organization_id=ORG_ALPHA_ID,
        email="brief.user@alpha.fi",
    )
    activated = await assignment_service.activate_assignment(brief_user_tok, created.id)
    assert activated.task_brief is not None
    assert activated.task_brief.id == alpha_brief_id

    drafted = await assignment_service.save_draft_inputs(
        brief_user_tok,
        created.id,
        ExecutionAssignmentDraftDTO(draft_inputs=WorkflowInputs(dynamic_inputs={"candidate_answer": "Initial draft"})),
    )
    assert drafted.task_brief is not None
    assert drafted.task_brief.id == alpha_brief_id

    listed = await assignment_service.list_assignments(_manager_token())
    assert len(listed) == 2
    assert all(item.task_brief is not None and item.task_brief.id == alpha_brief_id for item in listed)

    # 2. Snapshot immutability: Read paths retain frozen publication-time task_brief_snapshot even if task_brief_repo is detached
    assignment_service.task_brief_repo = None
    listed_without_repo = await assignment_service.list_assignments(_manager_token())
    assert all(
        item.task_brief_id == alpha_brief_id
        and item.task_brief is not None
        and item.task_brief.instruction_text == "Review section 4 and summarize key risks."
        for item in listed_without_repo
    )

    # 3. Negative 1: Missing task_brief_repo on create_assignment with task_brief_id raises SERVICE_DEPENDENCY_MISSING
    with caplog.at_level(logging.ERROR), pytest.raises(AppException) as missing_repo_exc:
        await assignment_service.create_assignment(
            initiator=_manager_token(),
            payload=ExecutionAssignmentCreateDTO(
                assigned_email="norepo@alpha.fi",
                workflow_id=WORKFLOW_ID,
                task_brief_id=alpha_brief_id,
                locked_inputs=WorkflowInputs(dynamic_inputs={"manager_context": "Context"}),
                assignee_input_keys=["candidate_answer"],
                hard_deadline_at=datetime.now(UTC) + timedelta(hours=4),
            ),
        )
    assert missing_repo_exc.value.details["error_code"] == ErrorCodes.SERVICE_DEPENDENCY_MISSING.value
    assignment_service.task_brief_repo = wf_repo

    # 4. Negative 2: Unknown task_brief_id raises ResourceNotFoundError
    unknown_brief_id = generate_opaque_id(EntityPrefix.TASK_BRIEF)
    with caplog.at_level(logging.ERROR), pytest.raises(ResourceNotFoundError) as not_found_exc:
        await assignment_service.create_assignment(
            initiator=_manager_token(),
            payload=ExecutionAssignmentCreateDTO(
                assigned_email="unknown.brief@alpha.fi",
                workflow_id=WORKFLOW_ID,
                task_brief_id=unknown_brief_id,
                locked_inputs=WorkflowInputs(dynamic_inputs={"manager_context": "Context"}),
                assignee_input_keys=["candidate_answer"],
                hard_deadline_at=datetime.now(UTC) + timedelta(hours=4),
            ),
        )
    assert not_found_exc.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value

    # 5. Negative 3: Another tenant's private TaskBrief raises PermissionDeniedError
    beta_brief_id = generate_opaque_id(EntityPrefix.TASK_BRIEF)
    await wf_repo.create_task_brief(
        TaskBriefFactory.build(
            id=beta_brief_id,
            slug="beta-private-brief",
            label=I18nText(translations={"en": "Beta Brief", "fi": "Beta-ohje"}),
            description=I18nText(translations={"en": "Beta Desc", "fi": "Beta-kuvaus"}),
            instruction_text="Confidential Beta brief.",
            source_url=None,
            organization_id=ORG_BETA_ID,
        )
    )
    with caplog.at_level(logging.ERROR), pytest.raises(PermissionDeniedError) as cross_org_exc:
        await assignment_service.create_assignment(
            initiator=_manager_token(),
            payload=ExecutionAssignmentCreateDTO(
                assigned_email="cross.org@alpha.fi",
                workflow_id=WORKFLOW_ID,
                task_brief_id=beta_brief_id,
                locked_inputs=WorkflowInputs(dynamic_inputs={"manager_context": "Context"}),
                assignee_input_keys=["candidate_answer"],
                hard_deadline_at=datetime.now(UTC) + timedelta(hours=4),
            ),
        )
    assert cross_org_exc.value.details["error_code"] == ErrorCodes.PERMISSION_DENIED.value
    assert identity_repo is not None


@pytest.mark.asyncio
async def test_assignment_eager_base64_extraction_and_firebase_email_verified_bootstrap(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify eager Base64Attachment extraction on draft/submit and Firebase email_verified bootstrap ordering."""
    mfa_settings = get_settings().model_copy(update={"require_mfa": True})
    monkeypatch.setattr(
        "backend_v2.services.execution.assignment_service.get_settings",
        lambda: mfa_settings,
    )
    assignment_service, _, _, _, _, _ = await _setup_assignment_harness()
    doc_service = DocumentExtractionService()

    created = await assignment_service.create_assignment(
        initiator=_manager_token(),
        payload=ExecutionAssignmentCreateDTO(
            assigned_email="upload.user@alpha.fi",
            workflow_id=WORKFLOW_ID,
            output_profile_id=PROFILE_ID,
            locked_inputs=WorkflowInputs(dynamic_inputs={"manager_context": "Context"}),
            assignee_input_keys=["candidate_answer"],
            hard_deadline_at=datetime.now(UTC) + timedelta(hours=6),
        ),
    )
    raw_token = assignment_service.get_last_generated_token(created.id)
    assert raw_token is not None

    onboarded = await assignment_service.onboard_assignee(
        raw_token,
        ExecutionAssignmentOnboardingRequestDTO(name="Upload User"),
    )
    assignee_tok = TokenData(
        id=onboarded.user.id,
        role=UserRole.MEMBER,
        organization_id=ORG_ALPHA_ID,
        email="upload.user@alpha.fi",
    )
    await assignment_service.activate_assignment(assignee_tok, created.id)

    attachment_b64 = base64.b64encode(b"Extracted candidate case response from uploaded TXT.").decode("ascii")
    ingress_payload = WorkflowInputsIngress(
        dynamic_inputs={
            "candidate_answer": Base64Attachment(
                filename="response.txt",
                content_base64=attachment_b64,
            )
        }
    )

    # 1. Negative: Base64Attachment without doc_service raises AppException(SERVICE_DEPENDENCY_MISSING)
    with caplog.at_level(logging.ERROR), pytest.raises(AppException) as missing_doc_exc:
        await assignment_service.save_draft_inputs(
            assignee_tok,
            created.id,
            ExecutionAssignmentDraftDTO(draft_inputs=ingress_payload),
            doc_service=None,
        )
    assert missing_doc_exc.value.details["error_code"] == ErrorCodes.SERVICE_DEPENDENCY_MISSING.value

    # 2. Positive: save_draft_inputs eagerly extracts Base64Attachment into plain text WorkflowInputs
    drafted = await assignment_service.save_draft_inputs(
        assignee_tok,
        created.id,
        ExecutionAssignmentDraftDTO(draft_inputs=ingress_payload),
        doc_service=doc_service,
    )
    assert (
        drafted.draft_inputs.dynamic_inputs["candidate_answer"]
        == "Extracted candidate case response from uploaded TXT."
    )

    # 3. Positive: submit_assignment eagerly extracts Base64Attachment into plain text WorkflowInputs
    submit_b64 = base64.b64encode(b"Final submitted attachment text.").decode("ascii")
    submitted_rec = await assignment_service.submit_assignment(
        initiator=assignee_tok,
        assignment_id=created.id,
        payload=ExecutionAssignmentSubmitDTO(
            submitted_inputs=WorkflowInputsIngress(
                dynamic_inputs={
                    "candidate_answer": Base64Attachment(
                        filename="final.txt",
                        content_base64=submit_b64,
                    )
                }
            )
        ),
        arq_pool=AsyncMock(spec=ArqRedis),
        doc_service=doc_service,
    )
    assert submitted_rec.raw_inputs.dynamic_inputs["candidate_answer"] == "Final submitted attachment text."

    # 4. Firebase onboarding: IDENTITY_MISMATCH checked before update_user, and email_verified=True marked before MFA_REQUIRED
    assert assignment_service.token_service is not None
    assignment_service.token_service.use_firebase = True
    mock_fb = AsyncMock()
    assignment_service.token_service.firebase_auth = mock_fb

    mfa_assignment = await assignment_service.create_assignment(
        initiator=_manager_token(),
        payload=ExecutionAssignmentCreateDTO(
            assigned_email="mfa.onboard@alpha.fi",
            workflow_id=WORKFLOW_ID,
            locked_inputs=WorkflowInputs(dynamic_inputs={"manager_context": "Context"}),
            assignee_input_keys=["candidate_answer"],
            hard_deadline_at=datetime.now(UTC) + timedelta(hours=4),
        ),
    )
    mfa_tok = assignment_service.get_last_generated_token(mfa_assignment.id)
    assert mfa_tok is not None

    # 4a. Mismatched Firebase email raises IDENTITY_MISMATCH without calling update_user
    def _verify_mismatched(_jwt: str) -> dict[str, str]:
        return {"uid": "fb_uid_mismatch", "email": "intruder@alpha.fi"}

    mock_fb.verify_id_token = _verify_mismatched
    mock_fb.update_user = AsyncMock()
    with pytest.raises(PermissionDeniedError) as mismatch_exc:
        await assignment_service.onboard_assignee(
            mfa_tok,
            ExecutionAssignmentOnboardingRequestDTO(
                firebase_token="valid_firebase_jwt_token_string",
                name="Intruder",
            ),
        )
    assert mismatch_exc.value.details["error_code"] == ErrorCodes.IDENTITY_MISMATCH.value
    mock_fb.update_user.assert_not_called()

    # 4b. Matching Firebase email without email_verified marks email_verified=True BEFORE _enforce_firebase_mfa_claim raises MFA_REQUIRED
    def _verify_unverified_no_mfa(_jwt: str) -> dict[str, str]:
        return {"uid": "fb_uid_new_user", "email": "mfa.onboard@alpha.fi"}

    mock_fb.verify_id_token = _verify_unverified_no_mfa
    mock_fb.update_user = AsyncMock(return_value=None)
    with pytest.raises(AuthenticationError) as mfa_exc:
        await assignment_service.onboard_assignee(
            mfa_tok,
            ExecutionAssignmentOnboardingRequestDTO(
                firebase_token="valid_firebase_jwt_token_string",
                name="New MFA User",
            ),
        )
    assert mfa_exc.value.details["error_code"] == ErrorCodes.MFA_REQUIRED.value
    mock_fb.update_user.assert_called_once_with("fb_uid_new_user", email_verified=True)


@pytest.mark.asyncio
async def test_published_assignment_task_brief_snapshot_immune_to_subsequent_studio_edits() -> None:
    """Verify published ExecutionAssignment retains frozen task_brief_snapshot after Studio edits."""
    assignment_service, _, wf_repo, _, _, _ = await _setup_assignment_harness()
    brief_id = generate_opaque_id(EntityPrefix.TASK_BRIEF)
    original_brief = TaskBriefFactory.build(
        id=brief_id,
        slug="immutable-snapshot-brief",
        label=I18nText(translations={"en": "Original Title", "fi": "Alkuperäinen otsikko"}),
        description=I18nText(translations={"en": "Original Desc", "fi": "Alkuperäinen kuvaus"}),
        instruction_text="Original publication instructions v1.",
        source_url="https://docs.qrum.ai/v1",
        organization_id=ORG_ALPHA_ID,
    )
    await wf_repo.create_task_brief(original_brief)

    created = await assignment_service.create_assignment(
        initiator=_manager_token(),
        payload=ExecutionAssignmentCreateDTO(
            assigned_email="snapshot.user@alpha.fi",
            workflow_id=WORKFLOW_ID,
            output_profile_id=PROFILE_ID,
            task_brief_id=brief_id,
            locked_inputs=WorkflowInputs(dynamic_inputs={"manager_context": "Context"}),
            assignee_input_keys=["candidate_answer"],
            hard_deadline_at=datetime.now(UTC) + timedelta(hours=6),
        ),
    )
    raw_token = assignment_service.get_last_generated_token(created.id)
    assert raw_token is not None

    onboarded = await assignment_service.onboard_assignee(
        raw_token,
        ExecutionAssignmentOnboardingRequestDTO(name="Snapshot User"),
    )
    assignee_tok = TokenData(
        id=onboarded.user.id,
        role=UserRole.MEMBER,
        organization_id=ORG_ALPHA_ID,
        email="snapshot.user@alpha.fi",
    )
    await assignment_service.activate_assignment(assignee_tok, created.id)
    exec_rec = await assignment_service.submit_assignment(
        initiator=assignee_tok,
        assignment_id=created.id,
        payload=ExecutionAssignmentSubmitDTO(
            submitted_inputs=WorkflowInputs(dynamic_inputs={"candidate_answer": "Submitted answer"})
        ),
        arq_pool=AsyncMock(spec=ArqRedis),
    )

    edited_brief = original_brief.model_copy(
        update={
            "label": I18nText(translations={"en": "Mutated Title v2", "fi": "Muokattu otsikko v2"}),
            "instruction_text": "Retroactively mutated instructions v2.",
            "source_url": "https://docs.qrum.ai/v2",
        }
    )
    await wf_repo.update_task_brief(brief_id, edited_brief)

    preview = await assignment_service.preview_assignment(raw_token)
    assert preview.task_brief is not None
    assert preview.task_brief.label.translations["en"] == "Original Title"
    assert preview.task_brief.instruction_text == "Original publication instructions v1."
    assert preview.task_brief.source_url == "https://docs.qrum.ai/v1"

    listed = await assignment_service.list_assignments(_manager_token())
    assert len(listed) == 1
    assert listed[0].task_brief is not None
    assert listed[0].task_brief.instruction_text == "Original publication instructions v1."

    by_exec = await assignment_service.get_assignment_by_execution_id(exec_rec.id)
    assert by_exec is not None
    assert by_exec.task_brief_snapshot is not None
    assert by_exec.task_brief_snapshot.instruction_text == "Original publication instructions v1."


@pytest.mark.asyncio
async def test_create_assignment_with_missing_or_cross_tenant_task_brief_fails_fast(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify create_assignment and create_assignment_batch fail fast on missing or cross-tenant TaskBrief."""
    assignment_service, _, wf_repo, _, _, _ = await _setup_assignment_harness()
    missing_brief_id = generate_opaque_id(EntityPrefix.TASK_BRIEF)
    beta_brief_id = generate_opaque_id(EntityPrefix.TASK_BRIEF)
    await wf_repo.create_task_brief(
        TaskBriefFactory.build(
            id=beta_brief_id,
            slug="beta-only-brief",
            organization_id=ORG_BETA_ID,
            instruction_text="Beta private instructions.",
        )
    )
    deadline = datetime.now(UTC) + timedelta(hours=6)

    with caplog.at_level(logging.ERROR), pytest.raises(ResourceNotFoundError) as nf_single:
        await assignment_service.create_assignment(
            initiator=_manager_token(),
            payload=ExecutionAssignmentCreateDTO(
                assigned_email="missing1@alpha.fi",
                workflow_id=WORKFLOW_ID,
                task_brief_id=missing_brief_id,
                locked_inputs=WorkflowInputs(dynamic_inputs={}),
                assignee_input_keys=[],
                hard_deadline_at=deadline,
            ),
        )
    assert nf_single.value.status_code == 404
    assert nf_single.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value

    with caplog.at_level(logging.ERROR), pytest.raises(ResourceNotFoundError) as nf_batch:
        await assignment_service.create_assignment_batch(
            initiator=_manager_token(),
            payload=ExecutionAssignmentBatchCreateDTO(
                recipients=[ExecutionAssignmentRecipientDTO(email="missing2@alpha.fi")],
                workflow_id=WORKFLOW_ID,
                task_brief_id=missing_brief_id,
                locked_inputs=WorkflowInputs(dynamic_inputs={}),
                assignee_input_keys=[],
                hard_deadline_at=deadline,
            ),
        )
    assert nf_batch.value.status_code == 404
    assert nf_batch.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value

    with caplog.at_level(logging.ERROR), pytest.raises(PermissionDeniedError) as fb_single:
        await assignment_service.create_assignment(
            initiator=_manager_token(),
            payload=ExecutionAssignmentCreateDTO(
                assigned_email="cross1@alpha.fi",
                workflow_id=WORKFLOW_ID,
                task_brief_id=beta_brief_id,
                locked_inputs=WorkflowInputs(dynamic_inputs={}),
                assignee_input_keys=[],
                hard_deadline_at=deadline,
            ),
        )
    assert fb_single.value.status_code == 403
    assert fb_single.value.details["error_code"] == ErrorCodes.PERMISSION_DENIED.value

    with caplog.at_level(logging.ERROR), pytest.raises(PermissionDeniedError) as fb_batch:
        await assignment_service.create_assignment_batch(
            initiator=_manager_token(),
            payload=ExecutionAssignmentBatchCreateDTO(
                recipients=[ExecutionAssignmentRecipientDTO(email="cross2@alpha.fi")],
                workflow_id=WORKFLOW_ID,
                task_brief_id=beta_brief_id,
                locked_inputs=WorkflowInputs(dynamic_inputs={}),
                assignee_input_keys=[],
                hard_deadline_at=deadline,
            ),
        )
    assert fb_batch.value.status_code == 403
    assert fb_batch.value.details["error_code"] == ErrorCodes.PERMISSION_DENIED.value
