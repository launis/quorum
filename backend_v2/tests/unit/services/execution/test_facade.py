"""Unit tests for ExecutionService facade (Strangler Fig pattern)."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.exceptions import (
    AppException,
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
    TokenData,
    UserRole,
)
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionCreate, ExecutionRecord, FrozenContext
from backend_v2.models.domain.inputs import WorkflowInputs, WorkflowInputsIngress
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.step import Step, StepRule
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.matrix_scorecard import HumanOverrideRequest
from backend_v2.models.dtos.workflow_schema import WorkflowSchemaResponseDTO
from backend_v2.models.enums import AssignmentStatus, ExecutionStatus, HistoricalContextMode, StepType
from backend_v2.services.execution.facade import ExecutionService, create_execution_record
from backend_v2.tests.fakes.in_memory_repositories import (
    InMemoryExecutionRepository,
    InMemoryIdentityRepository,
    InMemorySystemRepository,
    InMemoryUnifiedWorkflowRepository,
    InMemoryWorkflowRepository,
)


@pytest.fixture
def initiator() -> TokenData:
    """Fixture providing standard user token data."""
    return TokenData(id="usr_123", role=UserRole.MEMBER, organization_id="org_123")


@pytest.fixture
def mock_execution_service() -> tuple[ExecutionService, dict[str, MagicMock]]:
    """Fixture providing ExecutionService facade with mocked sub-services."""
    exec_repo = InMemoryExecutionRepository()
    workflow_repo = InMemoryWorkflowRepository()

    service = ExecutionService(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
    )

    subservices = {
        "lifecycle": MagicMock(),
        "ingress": MagicMock(),
        "resumption": MagicMock(),
        "override": MagicMock(),
        "stream": MagicMock(),
        "context": MagicMock(),
    }

    service._lifecycle = subservices["lifecycle"]
    service._ingress = subservices["ingress"]
    service._resumption = subservices["resumption"]
    service._override = subservices["override"]
    service._stream = subservices["stream"]
    service._context = subservices["context"]

    return service, subservices


def test_execution_service_init_with_defaults() -> None:
    """Verify ExecutionService initializes correctly with default optional dependencies."""
    exec_repo = InMemoryExecutionRepository()
    workflow_repo = InMemoryWorkflowRepository()
    service = ExecutionService(exec_repo=exec_repo, workflow_repo=workflow_repo)
    assert service.exec_repo is exec_repo
    assert service.workflow_repo is workflow_repo
    assert service.comp_repo is None
    assert service.storage is not None
    assert callable(create_execution_record)


def test_execution_service_init_with_custom_deps() -> None:
    """Verify ExecutionService initializes correctly with custom injected dependencies."""
    exec_repo = InMemoryExecutionRepository()
    workflow_repo = InMemoryWorkflowRepository()
    custom_storage = MagicMock()
    custom_usage = MagicMock()
    custom_executor = MagicMock()

    service = ExecutionService(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
        usage_service=custom_usage,
        executor=custom_executor,
        storage_driver=custom_storage,
    )
    assert service.storage is custom_storage
    assert service.usage_service is custom_usage
    assert service.executor is custom_executor


@pytest.mark.asyncio
async def test_list_executions(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify list_executions delegates to _lifecycle.list_executions."""
    service, subs = mock_execution_service
    expected = [MagicMock(spec=ExecutionRecord)]
    subs["lifecycle"].list_executions = AsyncMock(return_value=expected)

    result = await service.list_executions(initiator)
    assert result == expected
    subs["lifecycle"].list_executions.assert_awaited_once_with(initiator)


@pytest.mark.asyncio
async def test_get_execution(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify get_execution delegates to _lifecycle.get_execution."""
    service, subs = mock_execution_service
    expected = MagicMock(spec=ExecutionRecord)
    subs["lifecycle"].get_execution = AsyncMock(return_value=expected)

    result = await service.get_execution(initiator, "exe_123", hydrate=True, skip_resumability=False)
    assert result == expected
    subs["lifecycle"].get_execution.assert_awaited_once_with(initiator, "exe_123", True, False)


@pytest.mark.asyncio
async def test_delete_execution(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify delete_execution delegates to _lifecycle.delete_execution."""
    service, subs = mock_execution_service
    subs["lifecycle"].delete_execution = AsyncMock(return_value=True)

    result = await service.delete_execution(initiator, "exe_123")
    assert result is True
    subs["lifecycle"].delete_execution.assert_awaited_once_with(initiator, "exe_123")


@pytest.mark.asyncio
async def test_start_execution(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify start_execution delegates to _ingress.start_execution."""
    service, subs = mock_execution_service
    expected = MagicMock(spec=ExecutionRecord)
    subs["ingress"].start_execution = AsyncMock(return_value=expected)

    payload = ExecutionCreate(
        workflow_id="wor_0195f3a0000070008123456789abcdef",
        target_locale="fi",
        raw_inputs=WorkflowInputsIngress(dynamic_inputs={"key": "val"}),
        matrix_sampling_strategy=10,
    )
    arq_pool = AsyncMock()

    result = await service.start_execution(initiator, payload, arq_pool)
    assert result == expected
    subs["ingress"].start_execution.assert_awaited_once_with(initiator, payload, arq_pool, None)


@pytest.mark.asyncio
async def test_get_workflow_ui_schema(mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]]) -> None:
    """Verify get_workflow_ui_schema delegates to _ingress.get_workflow_ui_schema."""
    service, subs = mock_execution_service
    expected = MagicMock(spec=WorkflowSchemaResponseDTO)
    subs["ingress"].get_workflow_ui_schema = AsyncMock(return_value=expected)

    result = await service.get_workflow_ui_schema("wf_123")
    assert result == expected
    subs["ingress"].get_workflow_ui_schema.assert_awaited_once_with("wf_123")


@pytest.mark.asyncio
async def test_check_resumability(mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]]) -> None:
    """Verify check_resumability delegates to _resumption.check_resumability."""
    service, subs = mock_execution_service
    subs["resumption"].check_resumability = AsyncMock(return_value=True)

    record = MagicMock(spec=ExecutionRecord)
    result = await service.check_resumability(record)
    assert result is True
    subs["resumption"].check_resumability.assert_awaited_once_with(record)


@pytest.mark.asyncio
async def test_resume_execution(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify resume_execution delegates to _resumption.resume_execution."""
    service, subs = mock_execution_service
    expected = MagicMock(spec=ExecutionRecord)
    subs["resumption"].resume_execution = AsyncMock(return_value=expected)

    arq_pool = AsyncMock()
    result = await service.resume_execution(initiator, "exe_123", arq_pool)
    assert result == expected
    subs["resumption"].resume_execution.assert_awaited_once_with(initiator, "exe_123", arq_pool)


@pytest.mark.asyncio
async def test_override_atom(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify override_atom delegates to _override.override_atom."""
    service, subs = mock_execution_service
    subs["override"].override_atom = AsyncMock()

    payload = HumanOverrideRequest(new_status=ExecutionStatus.PASSED, reason="Human override test", evidence_quotes=[])
    await service.override_atom(initiator, "exe_123", "atm_123", payload)
    subs["override"].override_atom.assert_awaited_once_with(initiator, "exe_123", "atm_123", payload)


@pytest.mark.asyncio
async def test_reject_evidence_quote(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify reject_evidence_quote delegates to _override.reject_evidence_quote."""
    service, subs = mock_execution_service
    subs["override"].reject_evidence_quote = AsyncMock()

    await service.reject_evidence_quote(initiator, "exe_123", "evq_123", "Hallucination")
    subs["override"].reject_evidence_quote.assert_awaited_once_with(initiator, "exe_123", "evq_123", "Hallucination")


@pytest.mark.asyncio
async def test_clear_profile_synthesis(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify clear_profile_synthesis delegates to _override.clear_profile_synthesis."""
    service, subs = mock_execution_service
    subs["override"].clear_profile_synthesis = AsyncMock()

    await service.clear_profile_synthesis(initiator, "exe_123", "prf_123")
    subs["override"].clear_profile_synthesis.assert_awaited_once_with(initiator, "exe_123", "prf_123")


@pytest.mark.asyncio
async def test_stream_status(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify stream_status delegates to _stream.stream_status."""
    service, subs = mock_execution_service

    async def sample_stream(init: TokenData, eid: str) -> AsyncGenerator[str]:
        yield "event: progress\ndata: {}\n\n"
        yield "event: done\ndata: {}\n\n"

    subs["stream"].stream_status = sample_stream

    chunks = [chunk async for chunk in service.stream_status(initiator, "exe_123")]
    assert len(chunks) == 2
    assert "progress" in chunks[0]
    assert "done" in chunks[1]


@pytest.mark.asyncio
async def test_get_frozen_context_bytes(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify get_frozen_context_bytes delegates to _context.get_frozen_context_bytes."""
    service, subs = mock_execution_service
    expected = (b'{"test": 1}', "frozen_context.json")
    subs["context"].get_frozen_context_bytes = AsyncMock(return_value=expected)

    result = await service.get_frozen_context_bytes(initiator, "exe_123")
    assert result == expected
    subs["context"].get_frozen_context_bytes.assert_awaited_once_with(initiator, "exe_123")


@pytest.mark.asyncio
async def test_facade_negative_missing_resources_raise_app_exception(initiator: TokenData) -> None:
    """ISTQB Negative: Verify facade raises ResourceNotFoundError (AppException) on missing execution or workflow."""
    repo = InMemoryUnifiedWorkflowRepository()
    service = ExecutionService(exec_repo=repo, workflow_repo=repo)

    with pytest.raises(ResourceNotFoundError) as exc_get:
        await service.get_execution(initiator, "exe_0195f3a0000070008000000000000000")
    assert exc_get.value.status_code == 404
    assert exc_get.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value

    with pytest.raises(ResourceNotFoundError) as exc_del:
        await service.delete_execution(initiator, "exe_0195f3a0000070008000000000000000")
    assert exc_del.value.status_code == 404

    with pytest.raises(ResourceNotFoundError) as exc_schema:
        await service.get_workflow_ui_schema("wor_0195f3a0000070008000000000000000")
    assert exc_schema.value.status_code == 404


@pytest.mark.asyncio
async def test_facade_negative_permission_denied_and_unresumable_state() -> None:
    """ISTQB Negative & Boundary: Verify cross-tenant access denial and unresumable execution state via real callbacks."""
    repo = InMemoryUnifiedWorkflowRepository()
    service = ExecutionService(exec_repo=repo, workflow_repo=repo)

    record = create_execution_record(
        execution_id="exe_0195f3a0000070008123456789abcdef",
        workflow_id="wor_0195f3a0000070008123456789abcdef",
        raw_inputs=WorkflowInputs(),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        created_by="usr_owner0000000000",
        organization_id="org_owner0000000000",
        status=ExecutionStatus.PENDING,
    )
    repo.set_execution(record)

    outsider = TokenData(id="usr_outsider0000000", role=UserRole.MEMBER, organization_id="org_outsider0000000")
    with pytest.raises(PermissionDeniedError) as exc_perm:
        await service.get_execution(outsider, "exe_0195f3a0000070008123456789abcdef")
    assert exc_perm.value.status_code == 403
    assert exc_perm.value.details["error_code"] == ErrorCodes.PERMISSION_DENIED.value

    owner = TokenData(id="usr_owner0000000000", role=UserRole.MEMBER, organization_id="org_owner0000000000")
    with pytest.raises(AppException) as exc_resume:
        await service.resume_execution(owner, "exe_0195f3a0000070008123456789abcdef", AsyncMock())
    assert exc_resume.value.status_code == 400
    assert exc_resume.value.details["error_code"] == ErrorCodes.UNRESUMABLE_STATE_ERROR.value

    override_payload = HumanOverrideRequest(
        new_status=ExecutionStatus.PASSED, reason="Missing target atom test", evidence_quotes=[]
    )
    with pytest.raises(AppException) as exc_override:
        await service.override_atom(
            owner, "exe_0195f3a0000070008123456789abcdef", "atm_missing00000000", override_payload
        )
    assert exc_override.value.status_code == 404
    assert exc_override.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


def test_create_execution_record_negative_invalid_id_raises_app_exception() -> None:
    """ISTQB Boundary/Negative: Verify create_execution_record fails fast on malformed execution_id."""
    with pytest.raises(AppException) as exc_info:
        create_execution_record(
            execution_id="invalid id with spaces",
            workflow_id="wor_0195f3a0000070008123456789abcdef",
            raw_inputs=WorkflowInputs(),
            frozen_context=FrozenContext(),
            source_identity_manifest={},
        )
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_facade_assignment_lifecycle_and_missing_dependency_negative() -> None:
    """Verify ExecutionService assignment lifecycle methods and SERVICE_DEPENDENCY_MISSING negative guard."""
    repo = InMemoryUnifiedWorkflowRepository()
    unconfigured_service = ExecutionService(exec_repo=repo, workflow_repo=repo)
    manager = TokenData(
        id="usr_0195f3a0000070008000000000000101",
        role=UserRole.MANAGER,
        organization_id="org_0195f3a0000070008000000000000010",
        email="mgr@alpha.fi",
    )
    deadline = datetime.now(UTC) + timedelta(hours=6)
    create_dto = ExecutionAssignmentCreateDTO(
        assigned_email="cand@alpha.fi",
        workflow_id="wor_0195f3a0000070008123456789abcdef",
        output_profile_id="prf_0195f3a0000070008123456789abcdef",
        locked_inputs=WorkflowInputs(),
        assignee_input_keys=[],
        hard_deadline_at=deadline,
    )

    with pytest.raises(AppException) as missing_exc:
        await unconfigured_service.create_assignment(manager, create_dto)
    assert missing_exc.value.details["error_code"] == ErrorCodes.SERVICE_DEPENDENCY_MISSING.value

    await repo.save_workflow(
        Workflow(
            id="wor_0195f3a0000070008123456789abcdef",
            slug="wf-slug",
            name="WF",
            description="Desc",
            status="active",
            version=1,
            default_strictness_level=50,
            model_registry_id="sys_0195f3a00000700e826807f3bfa3454d",
            historical_context_mode=HistoricalContextMode.DISABLED,
            expected_inputs=[],
            steps=[
                StepRule(
                    id="stp_0195f3a0000070008123456789abcdef",
                    task_blueprint="stp_0195f3a0000070008123456789abcdef",
                )
            ],
            default_profile_id="prf_0195f3a0000070008123456789abcdef",
            organization_id="org_0195f3a0000070008000000000000010",
            is_public=False,
        )
    )
    await repo.save_step(
        Step(
            id="stp_0195f3a0000070008123456789abcdef",
            slug="stp-slug",
            name=I18nText(translations={"en": "Step", "fi": "Vaihe"}),
            type=StepType.LOGIC,
            hook="my_hook",
            mcp_tool_params={},
        )
    )
    await repo.save_output_profile(
        OutputProfile(
            id="prf_0195f3a0000070008123456789abcdef",
            slug="prf-slug",
            name=I18nText(translations={"en": "Profile", "fi": "Profiili"}),
            workflow_id="wor_0195f3a0000070008123456789abcdef",
            target_block_order=[],
            visible_block_extensions=[],
            visible_workflow_extensions=[],
        )
    )
    identity_repo = InMemoryIdentityRepository()
    await identity_repo.create_organization(
        Organization(
            id="org_0195f3a0000070008000000000000010",
            name="Alpha",
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
    configured = ExecutionService(
        exec_repo=repo,
        workflow_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=identity_repo,
        system_repo=InMemorySystemRepository(),
        usage_service=usage_service,
    )

    created = await configured.create_assignment(manager, create_dto)
    batch = await configured.create_assignment_batch(
        manager,
        ExecutionAssignmentBatchCreateDTO(
            recipients=[ExecutionAssignmentRecipientDTO(email="batch@alpha.fi")],
            workflow_id="wor_0195f3a0000070008123456789abcdef",
            locked_inputs=WorkflowInputs(),
            assignee_input_keys=[],
            hard_deadline_at=deadline,
        ),
    )
    assert batch.created_count == 1
    listed = await configured.list_assignments(manager)
    assert len(listed) == 2

    resent = await configured.resend_assignment_email(manager, created.id)
    assert configured._assignment is not None
    raw_token = configured._assignment.get_last_generated_token(resent.id)
    assert raw_token is not None

    preview = await configured.preview_assignment(raw_token)
    assert preview.id == created.id

    onboarded = await configured.onboard_assignee(
        raw_token,
        ExecutionAssignmentOnboardingRequestDTO(name="Candidate"),
    )
    cand_token = TokenData(
        id=onboarded.user.id,
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000010",
        email="cand@alpha.fi",
    )
    activated = await configured.activate_assignment(cand_token, created.id)
    assert activated.status == AssignmentStatus.ACTIVATED

    draft = await configured.save_draft_inputs(
        cand_token,
        created.id,
        ExecutionAssignmentDraftDTO(draft_inputs=WorkflowInputs(dynamic_inputs={"note": "draft"})),
    )
    assert draft.draft_inputs.dynamic_inputs["note"] == "draft"

    submitted = await configured.submit_assignment(
        cand_token,
        created.id,
        ExecutionAssignmentSubmitDTO(submitted_inputs=WorkflowInputs()),
        AsyncMock(),
    )
    assert submitted.id.startswith("exe_")
