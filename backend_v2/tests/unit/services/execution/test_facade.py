"""Unit tests for ExecutionService facade (Strangler Fig pattern)."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator, Awaitable, Callable
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
from backend_v2.models.core_base import I18nText, generate_opaque_id
from backend_v2.models.domain.execution import ExecutionCreate, ExecutionRecord, FrozenContext
from backend_v2.models.domain.inputs import WorkflowInputs, WorkflowInputsIngress
from backend_v2.models.domain.step import Step, StepRule
from backend_v2.models.dtos.matrix_scorecard import HumanOverrideRequest
from backend_v2.models.dtos.workflow_schema import WorkflowSchemaResponseDTO
from backend_v2.models.enums import AssignmentStatus, EntityPrefix, ExecutionStatus, HistoricalContextMode, StepType
from backend_v2.services.execution.assignment_service import ExecutionAssignmentService
from backend_v2.services.execution.facade import ExecutionService, create_execution_record
from backend_v2.tests.factories.model_factories import (
    ExecutionStepFactory,
    OutputProfileFactory,
    SystemRulePromptBlockFactory,
    WorkflowFactory,
)
from backend_v2.tests.fakes.in_memory_repositories import (
    InMemoryExecutionRepository,
    InMemoryIdentityRepository,
    InMemoryPromptBlockRepository,
    InMemoryUnifiedWorkflowRepository,
    InMemoryWorkflowRepository,
)


@pytest.fixture
def initiator() -> TokenData:
    """Provide standard authenticated user token data with canonical Opaque Stripe IDs.

    Returns:
        Validated TokenData fixture for MEMBER caller.
    """
    return TokenData(
        id=generate_opaque_id(EntityPrefix.USER),
        role=UserRole.MEMBER,
        organization_id=generate_opaque_id(EntityPrefix.ORGANIZATION),
    )


@pytest.fixture
def mock_execution_service() -> tuple[ExecutionService, dict[str, MagicMock]]:
    """Provide ExecutionService facade with isolated mocked sub-services for delegation verification.

    Returns:
        Tuple of (ExecutionService instance, dictionary of sub-service mocks).
    """
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
    """Verify ExecutionService initializes cleanly with default optional dependencies."""
    exec_repo = InMemoryExecutionRepository()
    workflow_repo = InMemoryWorkflowRepository()
    service = ExecutionService(exec_repo=exec_repo, workflow_repo=workflow_repo)
    assert service.exec_repo is exec_repo
    assert service.workflow_repo is workflow_repo
    assert service.prompt_block_repo is None
    assert service.storage is not None
    assert service._assignment is None
    assert callable(create_execution_record)


def test_execution_service_init_with_custom_deps() -> None:
    """Verify ExecutionService binds custom storage, usage, executor, and assignment dependencies."""
    exec_repo = InMemoryExecutionRepository()
    workflow_repo = InMemoryWorkflowRepository()
    custom_storage = MagicMock()
    custom_usage = MagicMock()
    custom_executor = MagicMock()
    custom_assignment = MagicMock(spec=ExecutionAssignmentService)

    service = ExecutionService(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
        usage_service=custom_usage,
        executor=custom_executor,
        storage_driver=custom_storage,
        assignment_service=custom_assignment,
    )
    assert service.storage is custom_storage
    assert service.usage_service is custom_usage
    assert service.executor is custom_executor
    assert service._assignment is custom_assignment


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
    execution_id = generate_opaque_id(EntityPrefix.EXECUTION)

    result = await service.get_execution(initiator, execution_id, hydrate=True, skip_resumability=False)
    assert result == expected
    subs["lifecycle"].get_execution.assert_awaited_once_with(initiator, execution_id, True, False)


@pytest.mark.asyncio
async def test_delete_execution(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify delete_execution delegates to _lifecycle.delete_execution."""
    service, subs = mock_execution_service
    subs["lifecycle"].delete_execution = AsyncMock(return_value=True)
    execution_id = generate_opaque_id(EntityPrefix.EXECUTION)

    result = await service.delete_execution(initiator, execution_id)
    assert result is True
    subs["lifecycle"].delete_execution.assert_awaited_once_with(initiator, execution_id)


@pytest.mark.asyncio
async def test_start_execution(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify start_execution delegates to _ingress.start_execution."""
    service, subs = mock_execution_service
    expected = MagicMock(spec=ExecutionRecord)
    subs["ingress"].start_execution = AsyncMock(return_value=expected)

    payload = ExecutionCreate(
        workflow_id=generate_opaque_id(EntityPrefix.WORKFLOW),
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
    workflow_id = generate_opaque_id(EntityPrefix.WORKFLOW)

    result = await service.get_workflow_ui_schema(workflow_id)
    assert result == expected
    subs["ingress"].get_workflow_ui_schema.assert_awaited_once_with(workflow_id)


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
    execution_id = generate_opaque_id(EntityPrefix.EXECUTION)

    arq_pool = AsyncMock()
    result = await service.resume_execution(initiator, execution_id, arq_pool)
    assert result == expected
    subs["resumption"].resume_execution.assert_awaited_once_with(initiator, execution_id, arq_pool)


@pytest.mark.asyncio
async def test_override_atom(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify override_atom delegates to _override.override_atom."""
    service, subs = mock_execution_service
    subs["override"].override_atom = AsyncMock()
    execution_id = generate_opaque_id(EntityPrefix.EXECUTION)
    atom_id = generate_opaque_id(EntityPrefix.TDA)

    payload = HumanOverrideRequest(new_status=ExecutionStatus.PASSED, reason="Human override test", evidence_quotes=[])
    await service.override_atom(initiator, execution_id, atom_id, payload)
    subs["override"].override_atom.assert_awaited_once_with(initiator, execution_id, atom_id, payload)


@pytest.mark.asyncio
async def test_reject_evidence_quote(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify reject_evidence_quote delegates to _override.reject_evidence_quote."""
    service, subs = mock_execution_service
    subs["override"].reject_evidence_quote = AsyncMock()
    execution_id = generate_opaque_id(EntityPrefix.EXECUTION)
    evq_id = generate_opaque_id(EntityPrefix.NODE)

    await service.reject_evidence_quote(initiator, execution_id, evq_id, "Hallucination")
    subs["override"].reject_evidence_quote.assert_awaited_once_with(initiator, execution_id, evq_id, "Hallucination")


@pytest.mark.asyncio
async def test_clear_profile_synthesis(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify clear_profile_synthesis delegates to _override.clear_profile_synthesis."""
    service, subs = mock_execution_service
    subs["override"].clear_profile_synthesis = AsyncMock()
    execution_id = generate_opaque_id(EntityPrefix.EXECUTION)
    profile_id = generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)

    await service.clear_profile_synthesis(initiator, execution_id, profile_id)
    subs["override"].clear_profile_synthesis.assert_awaited_once_with(initiator, execution_id, profile_id)


@pytest.mark.asyncio
async def test_stream_status(
    mock_execution_service: tuple[ExecutionService, dict[str, MagicMock]], initiator: TokenData
) -> None:
    """Verify stream_status delegates to _stream.stream_status."""
    service, subs = mock_execution_service
    execution_id = generate_opaque_id(EntityPrefix.EXECUTION)

    async def sample_stream(init: TokenData, eid: str) -> AsyncGenerator[str]:
        yield "event: progress\ndata: {}\n\n"
        yield "event: done\ndata: {}\n\n"

    subs["stream"].stream_status = sample_stream

    chunks = [chunk async for chunk in service.stream_status(initiator, execution_id)]
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
    execution_id = generate_opaque_id(EntityPrefix.EXECUTION)

    result = await service.get_frozen_context_bytes(initiator, execution_id)
    assert result == expected
    subs["context"].get_frozen_context_bytes.assert_awaited_once_with(initiator, execution_id)


@pytest.mark.asyncio
async def test_facade_negative_missing_resources_raise_app_exception(initiator: TokenData) -> None:
    """ISTQB Negative: Verify facade raises ResourceNotFoundError on missing execution or workflow."""
    repo = InMemoryUnifiedWorkflowRepository()
    service = ExecutionService(exec_repo=repo, workflow_repo=repo)
    missing_exe_id = generate_opaque_id(EntityPrefix.EXECUTION)
    missing_wf_id = generate_opaque_id(EntityPrefix.WORKFLOW)

    with pytest.raises(ResourceNotFoundError) as exc_get:
        await service.get_execution(initiator, missing_exe_id)
    assert exc_get.value.status_code == 404
    assert exc_get.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value

    with pytest.raises(ResourceNotFoundError) as exc_del:
        await service.delete_execution(initiator, missing_exe_id)
    assert exc_del.value.status_code == 404

    with pytest.raises(ResourceNotFoundError) as exc_schema:
        await service.get_workflow_ui_schema(missing_wf_id)
    assert exc_schema.value.status_code == 404


@pytest.mark.asyncio
async def test_facade_negative_permission_denied_and_unresumable_state() -> None:
    """ISTQB Negative & Boundary: Verify cross-tenant access denial and unresumable execution state via real callbacks."""
    repo = InMemoryUnifiedWorkflowRepository()
    service = ExecutionService(exec_repo=repo, workflow_repo=repo)

    owner_id = generate_opaque_id(EntityPrefix.USER)
    owner_org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
    outsider_id = generate_opaque_id(EntityPrefix.USER)
    outsider_org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
    execution_id = generate_opaque_id(EntityPrefix.EXECUTION)
    workflow_id = generate_opaque_id(EntityPrefix.WORKFLOW)

    record = create_execution_record(
        execution_id=execution_id,
        workflow_id=workflow_id,
        raw_inputs=WorkflowInputs(dynamic_inputs={}),
        frozen_context=FrozenContext.model_validate_json("{}"),
        source_identity_manifest={},
        created_by=owner_id,
        organization_id=owner_org_id,
        status=ExecutionStatus.PENDING,
    )
    repo.set_execution(record)

    outsider = TokenData(id=outsider_id, role=UserRole.MEMBER, organization_id=outsider_org_id)
    with pytest.raises(PermissionDeniedError) as exc_perm:
        await service.get_execution(outsider, execution_id)
    assert exc_perm.value.status_code == 403
    assert exc_perm.value.details["error_code"] == ErrorCodes.PERMISSION_DENIED.value

    owner = TokenData(id=owner_id, role=UserRole.MEMBER, organization_id=owner_org_id)
    with pytest.raises(AppException) as exc_resume:
        await service.resume_execution(owner, execution_id, AsyncMock())
    assert exc_resume.value.status_code == 400
    assert exc_resume.value.details["error_code"] == ErrorCodes.UNRESUMABLE_STATE_ERROR.value

    override_payload = HumanOverrideRequest(
        new_status=ExecutionStatus.PASSED, reason="Missing target atom test", evidence_quotes=[]
    )
    with pytest.raises(AppException) as exc_override:
        await service.override_atom(owner, execution_id, generate_opaque_id(EntityPrefix.TDA), override_payload)
    assert exc_override.value.status_code == 404
    assert exc_override.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


def test_create_execution_record_negative_invalid_id_raises_app_exception() -> None:
    """ISTQB Boundary/Negative: Verify create_execution_record fails fast on malformed execution_id."""
    with pytest.raises(AppException) as exc_info:
        create_execution_record(
            execution_id="invalid id with spaces",
            workflow_id=generate_opaque_id(EntityPrefix.WORKFLOW),
            raw_inputs=WorkflowInputs(dynamic_inputs={}),
            frozen_context=FrozenContext.model_validate_json("{}"),
            source_identity_manifest={},
        )
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_resume_execution_forwards_prompt_block_repo_for_merkle_invalidation() -> None:
    """Verify ExecutionService wires prompt_block_repo into ExecutionResumptionService for Merkle drift checks."""
    exec_repo = InMemoryExecutionRepository()
    workflow_repo = InMemoryWorkflowRepository()
    prompt_block_repo = InMemoryPromptBlockRepository()
    usage_service = AsyncMock()
    usage_service.check_quota = AsyncMock(return_value=True)

    org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
    user_id = generate_opaque_id(EntityPrefix.USER)
    block = SystemRulePromptBlockFactory.build(organization_id=org_id)
    await prompt_block_repo.create_prompt_block(block)

    step_blueprint_id = generate_opaque_id(EntityPrefix.STEP)
    step_rule_id = generate_opaque_id(EntityPrefix.STEP_REFERENCE)
    step = Step(
        id=step_blueprint_id,
        slug="merkle-step",
        name=I18nText(translations={"en": "Step", "fi": "Vaihe"}),
        type=StepType.LOGIC,
        hook="my_hook",
        criteria_block_ids=[block.id],
        mcp_tool_params={},
        pre_hooks=[],
        post_hooks=[],
        allowed_mcp_tools=[],
        expected_inputs=[],
    )
    await workflow_repo.save_step(step)

    workflow = WorkflowFactory.build(
        organization_id=org_id,
        version=1,
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=[
            StepRule(
                id=step_rule_id,
                task_blueprint=step_blueprint_id,
                depends_on=[],
                input_mappings={},
            )
        ],
    )
    await workflow_repo.save_workflow(workflow)

    drifted_step_state = ExecutionStepFactory.build(
        id=step_rule_id,
        status=ExecutionStatus.PASSED,
        input_merkle_hash="stale_hash_value",
    )
    execution_id = generate_opaque_id(EntityPrefix.EXECUTION)
    record = create_execution_record(
        execution_id=execution_id,
        workflow_id=workflow.id,
        raw_inputs=WorkflowInputs(dynamic_inputs={}),
        frozen_context=FrozenContext.model_validate_json("{}"),
        source_identity_manifest={},
        created_by=user_id,
        organization_id=org_id,
        status=ExecutionStatus.FAILED,
        steps=[drifted_step_state],
        step_states={step_rule_id: drifted_step_state},
    )
    await exec_repo.save_execution(record)

    service = ExecutionService(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
        prompt_block_repo=prompt_block_repo,
        usage_service=usage_service,
    )
    owner = TokenData(id=user_id, role=UserRole.MEMBER, organization_id=org_id)
    arq_pool = AsyncMock()

    resumed = await service.resume_execution(owner, execution_id, arq_pool)
    assert resumed.status == ExecutionStatus.RUNNING
    assert resumed.step_states[step_rule_id].status == ExecutionStatus.PENDING
    arq_pool.enqueue_job.assert_awaited_once()

    persisted = await exec_repo.get_execution(execution_id)
    assert persisted is not None
    assert persisted.status == ExecutionStatus.RUNNING
    assert persisted.step_states[step_rule_id].status == ExecutionStatus.PENDING


@pytest.mark.asyncio
async def test_facade_all_assignment_methods_negative_missing_dependency(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """ISTQB Negative: Verify all 9 assignment methods fail fast and dual-log SERVICE_DEPENDENCY_MISSING."""
    repo = InMemoryUnifiedWorkflowRepository()
    unconfigured = ExecutionService(exec_repo=repo, workflow_repo=repo)
    caller = TokenData(
        id=generate_opaque_id(EntityPrefix.USER),
        role=UserRole.MANAGER,
        organization_id=generate_opaque_id(EntityPrefix.ORGANIZATION),
        email="mgr@alpha.fi",
    )
    deadline = datetime.now(UTC) + timedelta(hours=6)
    assignment_id = generate_opaque_id(EntityPrefix.ASSIGNMENT)
    wf_id = generate_opaque_id(EntityPrefix.WORKFLOW)

    calls: list[Callable[[], Awaitable[object]]] = [
        lambda: unconfigured.create_assignment(
            caller,
            ExecutionAssignmentCreateDTO(
                assigned_email="cand@alpha.fi",
                workflow_id=wf_id,
                locked_inputs=WorkflowInputs(dynamic_inputs={}),
                assignee_input_keys=[],
                hard_deadline_at=deadline,
            ),
        ),
        lambda: unconfigured.create_assignment_batch(
            caller,
            ExecutionAssignmentBatchCreateDTO(
                recipients=[ExecutionAssignmentRecipientDTO(email="batch@alpha.fi")],
                workflow_id=wf_id,
                locked_inputs=WorkflowInputs(dynamic_inputs={}),
                assignee_input_keys=[],
                hard_deadline_at=deadline,
            ),
        ),
        lambda: unconfigured.list_assignments(caller),
        lambda: unconfigured.resend_assignment_email(caller, assignment_id),
        lambda: unconfigured.preview_assignment("raw-token"),
        lambda: unconfigured.onboard_assignee("raw-token", ExecutionAssignmentOnboardingRequestDTO(name="Cand")),
        lambda: unconfigured.activate_assignment(caller, assignment_id),
        lambda: unconfigured.save_draft_inputs(
            caller,
            assignment_id,
            ExecutionAssignmentDraftDTO(draft_inputs=WorkflowInputs(dynamic_inputs={})),
        ),
        lambda: unconfigured.submit_assignment(
            caller,
            assignment_id,
            ExecutionAssignmentSubmitDTO(submitted_inputs=WorkflowInputs(dynamic_inputs={})),
            AsyncMock(),
        ),
    ]

    with caplog.at_level(logging.ERROR):
        for call in calls:
            with pytest.raises(AppException) as exc_info:
                await call()
            assert exc_info.value.status_code == 500
            assert exc_info.value.details["error_code"] == ErrorCodes.SERVICE_DEPENDENCY_MISSING.value

    assert ErrorCodes.SERVICE_DEPENDENCY_MISSING.name in caplog.text


@pytest.mark.asyncio
async def test_facade_assignment_lifecycle_end_to_end() -> None:
    """Verify ExecutionService end-to-end assignment lifecycle with hermetic repositories and factories."""
    repo = InMemoryUnifiedWorkflowRepository()
    org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
    wf_id = generate_opaque_id(EntityPrefix.WORKFLOW)
    prf_id = generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)
    stp_id = generate_opaque_id(EntityPrefix.STEP)
    sr_id = generate_opaque_id(EntityPrefix.STEP_REFERENCE)

    manager = TokenData(
        id=generate_opaque_id(EntityPrefix.USER),
        role=UserRole.MANAGER,
        organization_id=org_id,
        email="mgr@alpha.fi",
    )
    deadline = datetime.now(UTC) + timedelta(hours=6)

    await repo.save_workflow(
        WorkflowFactory.build(
            id=wf_id,
            status="active",
            version=1,
            default_strictness_level=50,
            model_registry_id="mrg_0195f3a00000700e826807f3bfa3454d",
            historical_context_mode=HistoricalContextMode.DISABLED,
            expected_inputs=[],
            steps=[StepRule(id=sr_id, task_blueprint=stp_id, depends_on=[], input_mappings={})],
            default_profile_id=prf_id,
            organization_id=org_id,
            is_public=False,
        )
    )
    await repo.save_step(
        Step(
            id=stp_id,
            slug="stp-slug",
            name=I18nText(translations={"en": "Step", "fi": "Vaihe"}),
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
    await repo.save_output_profile(
        OutputProfileFactory.build(
            id=prf_id,
            workflow_id=wf_id,
            organization_id=org_id,
            target_block_order=[],
            visible_block_extensions=[],
            visible_workflow_extensions=[],
        )
    )
    identity_repo = InMemoryIdentityRepository()
    await identity_repo.create_organization(
        Organization(
            id=org_id,
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
        system_repo=repo,
        usage_service=usage_service,
    )

    create_dto = ExecutionAssignmentCreateDTO(
        assigned_email="cand@alpha.fi",
        workflow_id=wf_id,
        output_profile_id=prf_id,
        locked_inputs=WorkflowInputs(dynamic_inputs={}),
        assignee_input_keys=[],
        hard_deadline_at=deadline,
    )
    created = await configured.create_assignment(manager, create_dto)
    batch = await configured.create_assignment_batch(
        manager,
        ExecutionAssignmentBatchCreateDTO(
            recipients=[ExecutionAssignmentRecipientDTO(email="batch@alpha.fi")],
            workflow_id=wf_id,
            locked_inputs=WorkflowInputs(dynamic_inputs={}),
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
        organization_id=org_id,
        email="cand@alpha.fi",
    )
    activated = await configured.activate_assignment(cand_token, created.id)
    assert activated.status == AssignmentStatus.ACTIVATED

    draft = await configured.save_draft_inputs(
        cand_token,
        created.id,
        ExecutionAssignmentDraftDTO(draft_inputs=WorkflowInputs(dynamic_inputs={"note": "draft"})),
        doc_service=None,
    )
    assert draft.draft_inputs.dynamic_inputs["note"] == "draft"

    submitted = await configured.submit_assignment(
        cand_token,
        created.id,
        ExecutionAssignmentSubmitDTO(submitted_inputs=WorkflowInputs(dynamic_inputs={})),
        AsyncMock(),
    )
    assert submitted.id.startswith("exe_")
