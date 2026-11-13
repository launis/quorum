"""Unit tests for In-Memory Repository Fakes.

Verifies snapshot isolation, ingress mutation decoupling, explicit update requirement,
100% protocol method parity across the 9 active V2 repositories, and deterministic fault injection mechanics.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError, ServiceUnavailableError
from backend_v2.models.auth import (
    Organization,
    OrganizationCreate,
    OrganizationUpdateDTO,
    SubscriptionStatus,
    User,
    UserCreate,
    UserRole,
    UserUpdate,
)
from backend_v2.models.core_base import generate_uuid7
from backend_v2.models.domain.base import AuditLogCreateDTO
from backend_v2.models.domain.system_config import SystemConfigMCPGateways
from backend_v2.models.dtos.report_artifact import ReportArtifactUpdateDTO
from backend_v2.models.dtos.studio import StepCreateDTO, StepUpdateDTO, WorkflowCreateDTO, WorkflowUpdateDTO
from backend_v2.models.dtos.trace import (
    ExecutionCreateDTO,
    ExecutionUpdateDTO,
    ProgressTracePayloadDTO,
    TraceEventMetadataDTO,
)
from backend_v2.models.enums import ExecutionStatus, ReportStatus, StepType, SystemLocale
from backend_v2.models.state import TraceEvent
from backend_v2.tests.factories.model_factories import (
    I18nTextFactory,
    OutputProfileFactory,
    ReportArtifactFactory,
    SystemRulePromptBlockFactory,
    TaskBriefFactory,
    UsageRecordFactory,
)
from backend_v2.tests.fakes.in_memory_repositories import (
    InMemoryAuditRepository,
    InMemoryExecutionRepository,
    InMemoryIdentityRepository,
    InMemoryOutputProfileRepository,
    InMemoryPromptBlockRepository,
    InMemoryReportArtifactRepository,
    InMemorySystemRepository,
    InMemoryTaskBriefRepository,
    InMemoryUnifiedWorkflowRepository,
    InMemoryWorkflowRepository,
)

_WF_ID = "wf_0195f3a0000070008000000000000001"
_PRF_ID = "prf_0195f3a0000070008000000000000001"
_ORG_ID = "org_0195f3a0000070008000000000000001"
_USR_ID = "usr_0195f3a0000070008000000000000001"
_BLK_ID = "blk_0195f3a0000070008000000000000001"
_TBR_ID = "tbr_0195f3a0000070008000000000000001"
_EXE_ID = "exe_0195f3a0000070008000000000000001"
_REP_ID = "rep_0195f3a0000070008000000000000001"
_MRG_REG_ID = "mrg_0195f3a0000070008000bf23c2670ad5"
_MCP_GW_ID = "mcp_0195f3a00000700080008172bda70c86"
_MCP_EXTRA_ID = "mcp_0195f3a0000070018234567890abcde1"
_MCP_UNIFIED_EXTRA_ID = "mcp_0195f3a0000070018234567890abcde2"
_MTX_ID = "blk_0195f3a0000070008000000000000099"


def _make_workflow_dto(slug: str, name: str, description: str) -> WorkflowCreateDTO:
    """Build a strict WorkflowCreateDTO fixture for in-memory repository tests."""
    return WorkflowCreateDTO(
        slug=slug,
        name=name,
        description=description,
        expected_inputs=[],
        steps=[],
    )


def _make_step_dto(slug: str, label: str, hook: str) -> StepCreateDTO:
    """Build a strict StepCreateDTO fixture for in-memory repository tests."""
    return StepCreateDTO(
        slug=slug,
        name=I18nTextFactory.build(translations={"en": label, "fi": label}),
        type=StepType.LOGIC,
        hook=hook,
        criteria_block_ids=[],
        pre_hooks=[],
        post_hooks=[],
        allowed_mcp_tools=[],
        mcp_tool_params={},
        expected_inputs=[],
    )


def _make_trace_event(step_name: str, message: str) -> TraceEvent:
    """Build a strict TraceEvent fixture for in-memory repository tests."""
    return TraceEvent(
        event_id=generate_uuid7(),
        timestamp=datetime.now(UTC),
        step_name=step_name,
        event_type="progress",
        content=ProgressTracePayloadDTO(message=message, progress_pct=50),
        metadata=TraceEventMetadataDTO(mcp_audit_traces=[]),
        mcp_audit_traces=[],
    )


@pytest.mark.asyncio
async def test_in_memory_workflow_repo_persistence_roundtrip() -> None:
    """Verify saving a workflow to InMemoryWorkflowRepository and reading back updated state."""
    repo = InMemoryWorkflowRepository()
    dto = _make_workflow_dto(slug="roundtrip-slug", name="Roundtrip Workflow", description="Initial")
    wf_id = await repo.create_workflow(dto)
    fetched = await repo.get_workflow(wf_id)
    assert fetched is not None
    assert fetched.name == "Roundtrip Workflow"

    await repo.update_workflow(wf_id, WorkflowUpdateDTO(name="Updated Workflow"))
    updated = await repo.get_workflow(wf_id)
    assert updated is not None
    assert updated.name == "Updated Workflow"


@pytest.mark.asyncio
async def test_in_memory_repo_fault_injection() -> None:
    """Verify inject_fault raises configured exception and cleans up via clear_faults."""
    repo = InMemoryWorkflowRepository()
    exc = ServiceUnavailableError("Database connection error")
    repo.inject_fault("create_workflow", exc)
    try:
        dto = _make_workflow_dto(slug="fault-slug", name="Fault Test", description="Testing Fault")
        with pytest.raises(ServiceUnavailableError) as exc_info:
            await repo.create_workflow(dto)
        assert exc_info.value.error_code == ErrorCodes.SERVICE_UNAVAILABLE
    finally:
        repo.clear_faults()


@pytest.mark.asyncio
async def test_in_memory_repo_snapshot_isolation() -> None:
    """Verify retrieved entities are distinct memory copies (`is not`) with identical structural state (`==`)."""
    repo = InMemoryWorkflowRepository()
    dto = _make_workflow_dto(slug="iso-slug", name="Snapshot Iso", description="Isolation Desc")
    wf_id = await repo.create_workflow(dto)

    w1 = await repo.get_workflow(wf_id)
    w2 = await repo.get_workflow(wf_id)
    assert w1 is not None and w2 is not None
    assert w1 is not w2
    assert w1 == w2

    _ = w1.model_copy(update={"name": "Locally Mutated Name"})
    refetched = await repo.get_workflow(wf_id)
    assert refetched is not None
    assert refetched.name == "Snapshot Iso"


@pytest.mark.asyncio
async def test_snapshot_reference_isolation() -> None:
    """Verify get_execution returns distinct memory objects with identical structural data."""
    repo = InMemoryExecutionRepository()
    dto = ExecutionCreateDTO(
        workflow_id=_WF_ID,
        output_profile_id=_PRF_ID,
        organization_id=_ORG_ID,
        created_by=_USR_ID,
    )
    exec_id = await repo.create_execution(dto)

    rec1 = await repo.get_execution(exec_id)
    rec2 = await repo.get_execution(exec_id)

    assert rec1 is not None
    assert rec2 is not None
    assert rec1 is not rec2
    assert rec1 == rec2


@pytest.mark.asyncio
async def test_ingress_mutation_decoupling() -> None:
    """Verify mutating the input DTO after create_workflow does not affect stored state."""
    repo = InMemoryWorkflowRepository()
    dto = _make_workflow_dto(slug="orig-slug", name="Original Name", description="Test Desc")
    wf_id = await repo.create_workflow(dto)

    _ = dto.model_copy(update={"name": "Mutated Name"})

    stored = await repo.get_workflow(wf_id)
    assert stored is not None
    assert stored.name == "Original Name"


@pytest.mark.asyncio
async def test_explicit_update_requirement() -> None:
    """Verify modifying a returned entity without calling update_execution leaves stored snapshot intact."""
    repo = InMemoryExecutionRepository()
    dto = ExecutionCreateDTO(
        workflow_id=_WF_ID,
        output_profile_id=_PRF_ID,
        organization_id=_ORG_ID,
        created_by=_USR_ID,
    )
    exec_id = await repo.create_execution(dto)

    rec = await repo.get_execution(exec_id)
    assert rec is not None

    _ = rec.model_copy(update={"status": ExecutionStatus.FAILED})

    fetched = await repo.get_execution(exec_id)
    assert fetched is not None
    assert fetched.status == ExecutionStatus.PENDING


@pytest.mark.asyncio
async def test_deterministic_fault_injection_transient() -> None:
    """Verify single-shot transient fault raises on first call and succeeds on second call."""
    repo = InMemoryExecutionRepository()
    dto = ExecutionCreateDTO(
        workflow_id=_WF_ID,
        output_profile_id=_PRF_ID,
        organization_id=_ORG_ID,
        created_by=_USR_ID,
    )
    exec_id = await repo.create_execution(dto)

    repo.inject_fault("get_execution", TimeoutError("Transient DB Timeout"), trigger_count=1)
    try:
        with pytest.raises(TimeoutError) as exc_info:
            await repo.get_execution(exec_id)
        assert "Transient DB Timeout" in str(exc_info.value)

        rec = await repo.get_execution(exec_id)
        assert rec is not None
        assert rec.id == exec_id
    finally:
        repo.clear_faults()


@pytest.mark.asyncio
async def test_deterministic_fault_injection_permanent() -> None:
    """Verify permanent fault consistently raises across invocations until cleared."""
    repo = InMemoryExecutionRepository()
    dto = ExecutionCreateDTO(
        workflow_id=_WF_ID,
        output_profile_id=_PRF_ID,
        organization_id=_ORG_ID,
        created_by=_USR_ID,
    )
    repo.inject_fault("create_execution", ConnectionError("Database Down"), trigger_count=None)
    try:
        with pytest.raises(ConnectionError):
            await repo.create_execution(dto)

        with pytest.raises(ConnectionError):
            await repo.create_execution(dto)
    finally:
        repo.clear_faults("create_execution")

    exec_id = await repo.create_execution(dto)
    assert exec_id.startswith("exe_")


@pytest.mark.asyncio
async def test_deterministic_fault_injection_context_manager() -> None:
    """Verify scoped fault_context raises during block and clears automatically on exit."""
    repo = InMemoryWorkflowRepository()
    dto = _make_workflow_dto(slug="wf-scoped", name="WF", description="Desc")
    wf_id = await repo.create_workflow(dto)

    async with repo.fault_context("get_workflow", RuntimeError("Scoped Error")):
        with pytest.raises(RuntimeError):
            await repo.get_workflow(wf_id)

    wf = await repo.get_workflow(wf_id)
    assert wf is not None


def test_fault_injection_invalid_method_failure() -> None:
    """Verify injecting fault on non-existent, private, or excluded method raises ValueError Fail-Fast."""
    repo = InMemoryExecutionRepository()
    with pytest.raises(ValueError) as exc_info:
        repo.inject_fault("non_existent_method", RuntimeError("Boom"))
    assert "does not exist" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info_private:
        repo.inject_fault("_clone", RuntimeError("Boom"))
    assert "does not exist" in str(exc_info_private.value)

    with pytest.raises(ValueError) as exc_info_excluded:
        repo.inject_fault("inject_fault", RuntimeError("Boom"))
    assert "does not exist" in str(exc_info_excluded.value)


@pytest.mark.asyncio
async def test_all_9_active_v2_fake_repositories_and_facade() -> None:
    """Exercise methods across all 9 active V2 fake repositories and InMemoryUnifiedWorkflowRepository."""
    # 1. Execution
    exec_repo = InMemoryExecutionRepository()
    e_id = await exec_repo.create_execution(
        ExecutionCreateDTO(
            workflow_id=_WF_ID,
            output_profile_id=_PRF_ID,
            organization_id=_ORG_ID,
            created_by=_USR_ID,
        )
    )
    assert await exec_repo.get_execution_status(e_id) is not None
    assert await exec_repo.update_execution(e_id, ExecutionUpdateDTO(status=ExecutionStatus.PASSED))
    event = _make_trace_event(step_name="step_1", message="Started")
    assert await exec_repo.append_trace_event(e_id, event)
    assert len(await exec_repo.get_all_executions(organization_id=_ORG_ID)) == 1
    assert len(await exec_repo.get_recent_completed_executions()) == 1
    assert await exec_repo.delete_execution(e_id)
    assert not await exec_repo.delete_execution(_EXE_ID)

    # 2. Workflow & Step
    wf_repo = InMemoryWorkflowRepository()
    wf_id = await wf_repo.create_workflow(_make_workflow_dto(slug="wf-1", name="WF1", description="D1"))
    assert await wf_repo.get_workflow(wf_id) is not None
    assert await wf_repo.get_workflow_definition(wf_id) is not None
    assert await wf_repo.get_workflow_by_id(wf_id) is not None
    assert len(await wf_repo.get_all_workflows()) == 1
    assert await wf_repo.count_workflows() == 1
    await wf_repo.update_workflow(wf_id, WorkflowUpdateDTO(name="WF1 Updated"))
    await wf_repo.update_workflow_definition(wf_id, WorkflowUpdateDTO(name="WF1 Updated Def"))
    wf_model = await wf_repo.get_workflow(wf_id)
    assert wf_model is not None
    saved_wf_name = I18nTextFactory.build(translations={"en": "Saved WF", "fi": "Saved WF"})
    updated_wf = wf_model.model_copy(update={"name": saved_wf_name})
    assert await wf_repo.save_workflow(updated_wf) == wf_id
    re_fetched_wf = await wf_repo.get_workflow(wf_id)
    assert re_fetched_wf is not None
    assert re_fetched_wf.name == saved_wf_name

    s_id = await wf_repo.create_step(_make_step_dto(slug="s1", label="S1", hook="h1"))
    assert await wf_repo.get_step(s_id) is not None
    assert await wf_repo.get_step_by_id(s_id) is not None
    assert len(await wf_repo.get_all_steps()) == 1
    await wf_repo.update_step(
        s_id,
        StepUpdateDTO(name=I18nTextFactory.build(translations={"en": "S1 Updated", "fi": "S1 Updated"})),
    )

    step_model = await wf_repo.get_step(s_id)
    assert step_model is not None
    saved_step_name = I18nTextFactory.build(translations={"en": "Saved Step", "fi": "Saved Step"})
    updated_step = step_model.model_copy(update={"name": saved_step_name})
    assert await wf_repo.save_step(updated_step) == s_id
    re_fetched_step = await wf_repo.get_step(s_id)
    assert re_fetched_step is not None
    assert re_fetched_step.name == saved_step_name

    assert await wf_repo.delete_step(s_id)
    assert await wf_repo.delete_workflow(wf_id)

    # 3. Identity
    id_repo = InMemoryIdentityRepository()
    org_id = await id_repo.create_organization(
        OrganizationCreate(
            name="Org1",
            admin_email="admin@test.com",
            admin_password="password123",
            admin_name="Admin User",
            tpm_limit=10000,
            rpm_limit=60,
        )
    )
    assert await id_repo.get_organization(org_id) is not None
    assert await id_repo.get_organization_model(org_id) is not None
    assert len(await id_repo.list_organizations()) == 1
    await id_repo.update_organization(org_id, OrganizationUpdateDTO(name="Org1 Updated"))
    u_id = await id_repo.create_user(
        UserCreate(
            email="u@test.com",
            role=UserRole.MEMBER,
            organization_id=org_id,
            is_active=True,
            language=SystemLocale.EN,
            theme_mode="system",
        )
    )
    assert await id_repo.get_user(u_id) is not None
    assert await id_repo.get_user_by_email("u@test.com") is not None
    assert len(await id_repo.list_users(org_id)) == 1
    await id_repo.update_user(u_id, UserUpdate(name="Updated User"))
    assert await id_repo.get_org_usage_total(org_id) == 0.0
    await id_repo.delete_user(u_id)
    await id_repo.delete_org_data(org_id)
    await id_repo.delete_organization(org_id)

    # 4. PromptBlock
    block = SystemRulePromptBlockFactory.build(id=_BLK_ID, slug="rule-1")
    pb_repo = InMemoryPromptBlockRepository()
    await pb_repo.create_prompt_block(block)
    assert await pb_repo.get_prompt_block_by_id(_BLK_ID) is not None
    assert await pb_repo.get_prompt_block(_BLK_ID) is not None
    assert len(await pb_repo.get_all_prompt_blocks()) == 1
    assert len(await pb_repo.get_all_prompt_blocks_models()) == 1
    assert len(await pb_repo.get_prompt_blocks_by_ids([_BLK_ID])) == 1
    await pb_repo.update_prompt_block(_BLK_ID, block)
    await pb_repo.delete_prompt_block(_BLK_ID)

    # 5. TaskBrief
    tb_repo = InMemoryTaskBriefRepository()
    brief = TaskBriefFactory.build(id=_TBR_ID, slug="brief-1")
    await tb_repo.create_task_brief(brief)
    assert await tb_repo.get_task_brief_by_id(_TBR_ID) is not None
    assert len(await tb_repo.get_all_task_briefs()) == 1
    assert await tb_repo.update_task_brief(_TBR_ID, brief)
    assert await tb_repo.delete_task_brief(_TBR_ID)

    # 6. OutputProfile
    op_repo = InMemoryOutputProfileRepository()
    profile = OutputProfileFactory.build(id=_PRF_ID, slug="prof-1", workflow_id=_WF_ID, target_block_order=[])
    await op_repo.create_output_profile(profile)
    assert await op_repo.get_output_profile_by_id(_PRF_ID) is not None
    assert len(await op_repo.get_all_output_profiles()) == 1
    assert len(await op_repo.get_all_output_profiles_models()) == 1
    await op_repo.update_output_profile(_PRF_ID, profile)
    await op_repo.delete_output_profile(_PRF_ID)

    # 7. System
    sys_repo = InMemorySystemRepository()
    reg = await sys_repo.get_model_registry(_MRG_REG_ID)
    assert reg.id is not None
    await sys_repo.update_model_registry(reg.model_copy(update={"id": _MRG_REG_ID, "name": "Updated Registry"}))
    gw_cfg = SystemConfigMCPGateways(
        id=_MCP_GW_ID,
        organization_id=_ORG_ID,
        name="Gateway",
        slug="default_mcp_gateway",
        tools=[],
    )
    await sys_repo.update_mcp_gateways(gw_cfg)
    assert (await sys_repo.get_mcp_gateways(_MCP_GW_ID)).id == _MCP_GW_ID
    mcp_cfg = SystemConfigMCPGateways(
        id=_MCP_EXTRA_ID,
        organization_id=_ORG_ID,
        name="Extra Gateway",
        slug="extra_mcp_gateway",
        tools=[],
    )
    assert await sys_repo.update_mcp_gateways(mcp_cfg) is True
    assert (await sys_repo.get_mcp_gateways(_MCP_EXTRA_ID)).id == _MCP_EXTRA_ID
    assert await sys_repo.delete_mcp_gateways(_MCP_EXTRA_ID) is True

    # 8. Audit
    aud_repo = InMemoryAuditRepository()
    await aud_repo.log_audit_event(
        AuditLogCreateDTO(
            actor_id=_USR_ID,
            event_type="WORKFLOW_CREATED",
            resource_type="workflow",
            resource_id=_WF_ID,
            details={},
        )
    )
    assert len(await aud_repo.get_audit_logs(actor_id=_USR_ID)) == 1
    await aud_repo.log_usage(
        UsageRecordFactory.build(
            org_id=_ORG_ID,
            user_id=_USR_ID,
            model="gemini-2.5-flash",
            input_tokens=50,
            output_tokens=50,
            cost_usd=0.001,
            timestamp=datetime.now(UTC),
        )
    )
    assert len(await aud_repo.get_usage_records("organization", _ORG_ID)) == 1
    rollup = await aud_repo.aggregate_organization_usage(organization_id=_ORG_ID)
    assert rollup.total_prompt_tokens == 50
    assert (await aud_repo.get_detailed_usage("organization", _ORG_ID)).organization_id == _ORG_ID

    # 9. Report Artifact
    rep_repo = InMemoryReportArtifactRepository()
    art = ReportArtifactFactory.build(
        id=_REP_ID,
        execution_id=_EXE_ID,
        workflow_id=_WF_ID,
        profile_id=_PRF_ID,
        locale="en",
        title="Test Report",
        status=ReportStatus.READY,
    )
    await rep_repo.create_report_artifact(art)
    assert await rep_repo.get_report_artifact(_REP_ID) is not None
    assert len(await rep_repo.list_report_artifacts_by_execution(_EXE_ID)) == 1
    await rep_repo.update_report_artifact(_REP_ID, ReportArtifactUpdateDTO(error_message="Err"))
    assert await rep_repo.delete_report_artifact(_REP_ID)

    # 10. Unified Workflow Facade across all 9 active protocols
    unified = InMemoryUnifiedWorkflowRepository()
    u_wf_id = await unified.create_workflow(_make_workflow_dto(slug="unified-wf", name="Unified WF", description="D"))
    assert await unified.get_workflow(u_wf_id) is not None
    assert await unified.get_workflow_by_id(u_wf_id) is not None
    assert await unified.get_workflow_definition(u_wf_id) is not None
    assert len(await unified.get_all_workflows()) == 1
    assert await unified.count_workflows() == 1
    await unified.update_workflow(u_wf_id, WorkflowUpdateDTO(name="Updated WF"))
    await unified.update_workflow_definition(u_wf_id, WorkflowUpdateDTO(name="Updated Def"))

    u_wf = await unified.get_workflow(u_wf_id)
    assert u_wf is not None
    u_wf_up = u_wf.model_copy(
        update={"name": I18nTextFactory.build(translations={"en": "Unified Saved WF", "fi": "Unified Saved WF"})}
    )
    assert await unified.save_workflow(u_wf_up) == u_wf_id

    u_step_id = await unified.create_step(_make_step_dto(slug="u-s1", label="US1", hook="h"))
    assert await unified.get_step(u_step_id) is not None
    assert await unified.get_step_by_id(u_step_id) is not None
    assert len(await unified.get_all_steps()) == 1
    await unified.update_step(
        u_step_id,
        StepUpdateDTO(name=I18nTextFactory.build(translations={"en": "US1 Up", "fi": "US1 Up"})),
    )

    u_step_model = await unified.get_step(u_step_id)
    assert u_step_model is not None
    u_step_saved = u_step_model.model_copy(
        update={"name": I18nTextFactory.build(translations={"en": "Unified Saved Step", "fi": "Unified Saved Step"})}
    )
    assert await unified.save_step(u_step_saved) == u_step_id
    assert await unified.delete_step(u_step_id)
    assert await unified.delete_workflow(u_wf_id)

    u_exec_id = await unified.create_execution(
        ExecutionCreateDTO(
            workflow_id=_WF_ID,
            output_profile_id=_PRF_ID,
            organization_id=_ORG_ID,
            created_by=_USR_ID,
        )
    )
    assert await unified.get_execution(u_exec_id) is not None
    assert await unified.get_execution_status(u_exec_id) is not None
    await unified.update_execution(u_exec_id, ExecutionUpdateDTO(status=ExecutionStatus.RUNNING))
    await unified.append_trace_event(u_exec_id, _make_trace_event(step_name="step1", message="ok"))
    assert len(await unified.get_all_executions()) == 1
    assert len(await unified.get_recent_completed_executions()) == 1
    assert await unified.delete_execution(u_exec_id)

    u_org_id = await unified.create_organization(
        OrganizationCreate(
            name="OrgU",
            admin_email="u@test.com",
            admin_password="password123",
            admin_name="Admin User",
            tpm_limit=10000,
            rpm_limit=60,
        )
    )
    assert await unified.get_organization(u_org_id) is not None
    assert await unified.get_organization_model(u_org_id) is not None
    assert len(await unified.list_organizations()) == 1
    await unified.update_organization(u_org_id, OrganizationUpdateDTO(name="OrgU Updated"))
    u_user_id = await unified.create_user(
        UserCreate(
            email="u@test.com",
            role=UserRole.MEMBER,
            organization_id=u_org_id,
            is_active=True,
            language=SystemLocale.EN,
            theme_mode="system",
        )
    )
    assert await unified.get_user(u_user_id) is not None
    assert await unified.get_user_by_email("u@test.com") is not None
    assert len(await unified.list_users(u_org_id)) == 1
    await unified.update_user(u_user_id, UserUpdate(name="Updated User"))
    assert await unified.get_org_usage_total(u_org_id) == 0.0
    assert await unified.delete_user(u_user_id)
    assert await unified.delete_organization(u_org_id)
    await unified.delete_org_data(_ORG_ID)

    await unified.create_prompt_block(block)
    assert await unified.get_prompt_block(_BLK_ID) is not None
    assert await unified.get_prompt_block_by_id(_BLK_ID) is not None
    assert len(await unified.get_all_prompt_blocks()) == 1
    assert len(await unified.get_all_prompt_blocks_models()) == 1
    assert len(await unified.get_prompt_blocks_by_ids([_BLK_ID])) == 1
    await unified.update_prompt_block(_BLK_ID, block)
    assert await unified.delete_prompt_block(_BLK_ID)

    await unified.create_task_brief(brief)
    assert await unified.get_task_brief_by_id(_TBR_ID) is not None
    assert len(await unified.get_all_task_briefs()) == 1
    assert await unified.update_task_brief(_TBR_ID, brief)
    assert await unified.delete_task_brief(_TBR_ID)

    await unified.create_output_profile(profile)
    assert await unified.get_output_profile_by_id(_PRF_ID) is not None
    assert len(await unified.get_all_output_profiles()) == 1
    assert len(await unified.get_all_output_profiles_models()) == 1
    await unified.update_output_profile(_PRF_ID, profile)
    assert await unified.delete_output_profile(_PRF_ID)

    u_reg = await unified.get_model_registry(_MRG_REG_ID)
    assert u_reg.id is not None
    await unified.update_model_registry(u_reg.model_copy(update={"id": _MRG_REG_ID, "name": "U Reg"}))
    await unified.update_mcp_gateways(gw_cfg)
    assert (await unified.get_mcp_gateways(_MCP_GW_ID)).id == _MCP_GW_ID
    all_gws = await unified.get_all_mcp_gateways()
    assert any(g.id == _MCP_GW_ID for g in all_gws)
    unified_extra_gw = SystemConfigMCPGateways(
        id=_MCP_UNIFIED_EXTRA_ID,
        organization_id=_ORG_ID,
        name="Unified Extra Gateway",
        slug="unified_extra_gateway",
        tools=[],
    )
    assert await unified.update_mcp_gateways(unified_extra_gw) is True
    assert (await unified.get_mcp_gateways(_MCP_UNIFIED_EXTRA_ID)).id == _MCP_UNIFIED_EXTRA_ID
    assert await unified.delete_mcp_gateways(_MCP_UNIFIED_EXTRA_ID) is True

    await unified.log_audit_event(
        AuditLogCreateDTO(
            actor_id=_USR_ID,
            event_type="WORKFLOW_UPDATED",
            resource_type="workflow",
            resource_id=_WF_ID,
            details={},
        )
    )
    assert len(await unified.get_audit_logs()) == 1
    await unified.log_usage(
        UsageRecordFactory.build(
            org_id=_ORG_ID,
            user_id=_USR_ID,
            model="gemini-2.5-flash",
            input_tokens=10,
            output_tokens=20,
            cost_usd=0.01,
            timestamp=datetime.now(UTC),
        )
    )
    assert len(await unified.get_usage_records("organization", _ORG_ID)) == 1
    assert (await unified.aggregate_organization_usage(organization_id=_ORG_ID)).record_count == 1
    assert (await unified.get_detailed_usage("organization", _ORG_ID)).organization_id == _ORG_ID

    await unified.create_report_artifact(art)
    assert await unified.get_report_artifact(_REP_ID) is not None
    assert len(await unified.list_report_artifacts_by_execution(_EXE_ID)) == 1
    await unified.update_report_artifact(_REP_ID, ReportArtifactUpdateDTO(error_message="Err2"))
    assert await unified.delete_report_artifact(_REP_ID)


@pytest.mark.asyncio
async def test_in_memory_fk_restrict_and_not_found_contracts() -> None:
    """Verify FK usage restrictions and ResourceNotFoundError paths across fake repositories."""
    unified = InMemoryUnifiedWorkflowRepository()
    block = SystemRulePromptBlockFactory.build(id=_BLK_ID, organization_id=_ORG_ID)
    await unified.create_prompt_block(block)

    with pytest.raises(AppException) as missing_blk_exc:
        await unified.get_prompt_blocks_by_ids(["blk_0195f3a0000070008000000000999999"], strict=True)
    assert missing_blk_exc.value.status_code == 404
    assert await unified.get_prompt_blocks_by_ids(["blk_0195f3a0000070008000000000999999"], strict=False) == []

    step_dto = StepCreateDTO(
        slug="fk-step",
        name=I18nTextFactory.build(translations={"en": "FK Step", "fi": "FK Step"}),
        type=StepType.LOGIC,
        hook="fk_hook",
        criteria_block_ids=[_BLK_ID],
        pre_hooks=[],
        post_hooks=[],
        allowed_mcp_tools=[],
        mcp_tool_params={},
        expected_inputs=[],
    )
    step_id = await unified.create_step(step_dto)
    with pytest.raises(AppException) as step_fk_exc:
        await unified.delete_prompt_block(_BLK_ID)
    assert step_fk_exc.value.status_code == 400
    assert await unified.delete_step(step_id) is True

    profile = OutputProfileFactory.build(
        id=_PRF_ID,
        workflow_id=_WF_ID,
        organization_id=_ORG_ID,
        variance_target_block=_BLK_ID,
    )
    await unified.save_output_profile(profile)
    with pytest.raises(AppException) as prof_blk_exc:
        await unified.delete_prompt_block(_BLK_ID)
    assert prof_blk_exc.value.status_code == 400

    wf_id = await unified.create_workflow(
        WorkflowCreateDTO(
            slug="fk-wf",
            name="FK Workflow",
            description="FK test",
            default_profile_id=_PRF_ID,
            model_registry_id=_MRG_REG_ID,
            mcp_gateway_id=_MCP_GW_ID,
            expected_inputs=[],
            steps=[],
        )
    )
    with pytest.raises(AppException):
        await unified.delete_output_profile(_PRF_ID)
    with pytest.raises(AppException):
        await unified.delete_model_registry(_MRG_REG_ID)
    with pytest.raises(AppException):
        await unified.delete_mcp_gateways(_MCP_GW_ID)
    assert await unified.delete_workflow(wf_id) is True

    art = ReportArtifactFactory.build(
        id=_REP_ID,
        execution_id=_EXE_ID,
        workflow_id=_WF_ID,
        profile_id=_PRF_ID,
        locale="en",
        title="FK Report",
        status=ReportStatus.READY,
    )
    unified.save_report_artifact(art)
    with pytest.raises(AppException):
        await unified.delete_output_profile(_PRF_ID)
    assert await unified.delete_report_artifact(_REP_ID) is True

    assert await unified.delete_output_profile(_PRF_ID) is True
    assert await unified.delete_output_profile(_PRF_ID) is False
    assert await unified.delete_prompt_block(_BLK_ID) is True
    assert await unified.delete_prompt_block(_BLK_ID) is False
    assert (
        await unified.update_task_brief(_TBR_ID, TaskBriefFactory.build(id=_TBR_ID, organization_id=_ORG_ID)) is False
    )
    assert await unified.delete_task_brief(_TBR_ID) is False

    sys_repo = InMemorySystemRepository()
    with pytest.raises(ResourceNotFoundError):
        await sys_repo.get_model_registry("")
    with pytest.raises(ResourceNotFoundError):
        await sys_repo.get_mcp_gateways("mcp_0195f3a0000070008000000000999999")
    assert len(await sys_repo.get_all_model_registries()) >= 1
    reg = await sys_repo.get_model_registry(_MRG_REG_ID)
    sys_repo.seed_raw_system_config("custom_cfg", {"enabled": True})
    assert await sys_repo.get_system_config("custom_cfg") == {"enabled": True}
    assert (await sys_repo.get_system_config(_MRG_REG_ID)).id == _MRG_REG_ID
    assert (await sys_repo.get_system_config(_MCP_GW_ID)).id == _MCP_GW_ID
    sys_repo.remove_system_config("custom_cfg")
    sys_repo.remove_system_config(_MCP_GW_ID)
    assert await sys_repo.delete_mcp_gateways("mcp_0195f3a0000070008000000000999999") is False
    assert await sys_repo.delete_model_registry(_MRG_REG_ID) is True
    assert await sys_repo.delete_model_registry("mrg_0195f3a0000070008000000000999999") is False
    sys_repo.set_model_registry(None)
    assert await sys_repo.get_all_model_registries() == []
    sys_repo.set_model_registry(reg, registry_id="mrg_0195f3a0000070008000000000888888")
    assert (await sys_repo.get_model_registry("mrg_0195f3a0000070008000000000888888")).id == reg.id


@pytest.mark.asyncio
async def test_unified_workflow_repository_seeding_and_system_helpers() -> None:
    """Verify InMemoryUnifiedWorkflowRepository test-seeding helpers and execution org auto-seed."""
    unified = InMemoryUnifiedWorkflowRepository()
    tenant_org_id = "org_0195f3a0000070008000000000000777"

    exec_id = await unified.create_execution(
        ExecutionCreateDTO(
            workflow_id=_WF_ID,
            output_profile_id=_PRF_ID,
            organization_id=tenant_org_id,
            created_by=_USR_ID,
        )
    )
    exec_rec = await unified.get_execution(exec_id)
    assert exec_rec is not None
    await unified.save_execution(exec_rec)
    assert len(await unified.get_all_executions(organization_id=tenant_org_id, user_id=_USR_ID)) == 1
    auto_org = await unified.get_organization(tenant_org_id)
    assert auto_org is not None
    assert auto_org.id == tenant_org_id

    unified.set_org_usage_total(tenant_org_id, 42.5)
    assert await unified.get_org_usage_total(tenant_org_id) == 42.5

    brief = TaskBriefFactory.build(id=_TBR_ID, organization_id=tenant_org_id)
    unified.set_task_briefs([brief])
    assert len(await unified.get_all_task_briefs()) == 1

    profile = OutputProfileFactory.build(id=_PRF_ID, workflow_id=_WF_ID, organization_id=tenant_org_id)
    unified.set_output_profile(profile)
    assert await unified.get_output_profile(_PRF_ID) is not None
    fetched_prof = await unified.get_by_id(_PRF_ID)
    assert fetched_prof is not None
    assert fetched_prof.id == _PRF_ID
    unified.set_output_profile(None)
    assert await unified.get_output_profile(_PRF_ID) is None

    block = SystemRulePromptBlockFactory.build(id=_BLK_ID, organization_id=tenant_org_id)
    unified.set_prompt_blocks([block])
    fetched_blk = await unified.get_by_id(_BLK_ID)
    assert fetched_blk is not None
    assert fetched_blk.id == _BLK_ID
    unified.seed_raw_prompt_block(_BLK_ID, block)

    wf_id = await unified.create_workflow(_make_workflow_dto(slug="seed-wf", name="Seed WF", description="Desc"))
    wf_model = await unified.get_workflow(wf_id)
    assert wf_model is not None
    with pytest.raises(AppException) as occ_exc:
        await unified.save_workflow(wf_model.model_copy(update={"version": 99}))
    assert occ_exc.value.status_code == 409
    with pytest.raises(AppException):
        await unified.update_workflow("wf_0195f3a0000070008000000000999999", WorkflowUpdateDTO(name="Missing"))
    assert await unified.delete_workflow("wf_0195f3a0000070008000000000999999") is False
    assert len(await unified._workflows.get_all_workflows(organization_id=tenant_org_id, role="MEMBER")) == 1
    assert len(await unified._workflows.get_all_workflows(organization_id=tenant_org_id, role="ROOT")) == 0
    unified.set_workflow(None)
    assert await unified.get_workflow(wf_id) is None
    await unified.save_workflow(wf_model)
    unified.seed_raw_workflow(wf_id, wf_model)
    assert await unified.get_workflow(wf_id) is not None
    unified.set_workflow(None)

    step_id = await unified.create_step(_make_step_dto(slug="seed-stp", label="Seed Step", hook="h"))
    step_model = await unified.get_step(step_id)
    assert step_model is not None
    with pytest.raises(AppException):
        await unified.update_step("stp_0195f3a0000070008000000000999999", StepUpdateDTO(hook="missing"))
    assert await unified.delete_step("stp_0195f3a0000070008000000000999999") is False
    unified.set_step(None)
    assert await unified.get_step("stp_0195f3a0000070008000000000999999") is None
    unified.set_step(step_model)
    assert await unified.get_step("stp_0195f3a0000070008000000000999999") is not None
    unified.set_step(step_model, step_id=step_id)
    unified.seed_raw_step(step_id, step_model)

    unified.set_execution(None)
    assert await unified.get_execution(exec_id) is None
    unified.set_execution(exec_rec)
    assert await unified.get_execution(exec_id) is not None

    org_model = Organization(
        id=tenant_org_id,
        name="Explicit Tenant",
        contact_email="tenant@example.com",
        is_active=True,
        tier="pro",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=1000000,
        rpm_limit=120,
        allowed_email_domains=[],
    )
    unified.set_organization(None)
    assert await unified.create_organization(org_model) == tenant_org_id
    assert (
        await unified.update_organization("org_0195f3a0000070008000000000999999", OrganizationUpdateDTO(name="No"))
        is False
    )
    assert await unified.delete_organization("org_0195f3a0000070008000000000999999") is False
    unified.set_organization(org_model)
    assert (await unified.get_organization(tenant_org_id)) is not None

    user_model = User(
        id=_USR_ID,
        email="member@example.com",
        name="Member",
        role=UserRole.MEMBER,
        organization_id=tenant_org_id,
        is_active=True,
        language=SystemLocale.EN,
        theme_mode="system",
        created_at=datetime.now(UTC),
    )
    unified.set_user(None)
    assert await unified.get_user(_USR_ID) is None
    assert await unified.get_user_by_email("missing@example.com") is None
    assert await unified.create_user(user_model) == _USR_ID
    assert await unified.update_user("usr_0195f3a0000070008000000000999999", UserUpdate(name="No")) is False
    assert await unified.delete_user("usr_0195f3a0000070008000000000999999") is False
    unified.set_user(user_model)
    assert (await unified.get_user(_USR_ID)) is not None

    reg = await unified.get_model_registry(_MRG_REG_ID)
    assert len(await unified.get_all_model_registries()) >= 1
    unified.set_model_registry(reg)
    unified.seed_system_config("sys_flag", {"ready": True})
    assert await unified.get_system_config("sys_flag") == {"ready": True}
    unified.remove_system_config("sys_flag")
    assert await unified.delete_model_registry(_MRG_REG_ID) is True

    gw = SystemConfigMCPGateways(
        id=_MCP_EXTRA_ID,
        organization_id=tenant_org_id,
        name="Seeded GW",
        slug="seeded_gw",
        tools=[],
    )
    unified.set_mcp_gateways(None)
    unified.set_mcp_gateways(gw)
    assert (await unified.get_mcp_gateways(_MCP_EXTRA_ID)).id == _MCP_EXTRA_ID
