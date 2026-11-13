"""Unit and integration roundtrip tests for active V2 domain repositories over EntityPersistencePort."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from backend_v2.database.repositories import (
    AuditRepositoryImpl,
    ExecutionRepositoryImpl,
    IdentityRepositoryImpl,
    ReportArtifactRepositoryImpl,
    SystemRepositoryImpl,
    WorkflowRepositoryImpl,
)
from backend_v2.database.repositories.components import (
    OutputProfileRepositoryImpl,
    PromptBlockRepositoryImpl,
    TaskBriefRepositoryImpl,
)
from backend_v2.database.repository import UnifiedWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.auth import Organization, SubscriptionStatus
from backend_v2.models.domain.base import AuditLogCreateDTO, DetailedUsageDTO
from backend_v2.models.domain.system_config import (
    ModelProfile,
    ProviderExtraParamsDTO,
    SystemConfigModelRegistry,
)
from backend_v2.models.dtos.studio import StepCreateDTO, StepUpdateDTO
from backend_v2.models.dtos.trace import ExecutionCreateDTO, ExecutionUpdateDTO
from backend_v2.models.enums import (
    CognitiveTier,
    ExecutionStatus,
    HistoricalContextMode,
    LLMProvider,
    StepType,
)
from backend_v2.tests.factories.model_factories import (
    I18nTextFactory,
    OutputProfileFactory,
    ReportArtifactFactory,
    SystemRulePromptBlockFactory,
    TaskBriefFactory,
    UsageRecordFactory,
    WorkflowFactory,
)
from backend_v2.tests.fakes.in_memory_uow import InMemoryUnitOfWork

_WF_ID = "wf_0195f3a0000070008000000000000001"
_PRF_ID = "prf_0195f3a0000070008000000000000001"
_ORG_ID = "org_0195f3a0000070008000000000000001"
_USR_ID = "usr_0195f3a0000070008000000000000001"
_BLK_ID = "blk_0195f3a0000070008000000000000001"
_TBR_ID = "tbr_0195f3a0000070008000000000000001"
_REP_ID = "rep_0195f3a0000070008000000000000001"
_SYS_ID = "mrg_0195f3a00000700e826807f3bfa3454d"
_SYS_MISSING_ID = "mrg_0195f3a0000070008000000000000099"
_EXE_MISSING_ID = "exe_0195f3a0000070008000000000000099"
_USG_ID = "usg_0195f3a0000070008000000000000001"


@pytest.mark.asyncio
async def test_execution_repo() -> None:
    """Verify ExecutionRepositoryImpl stateful roundtrip over InMemoryUnitOfWork."""
    base_uow = InMemoryUnitOfWork()
    repo = ExecutionRepositoryImpl(uow_factory=lambda: InMemoryUnitOfWork(base_uow.store))
    assert await repo.get_execution_status(_EXE_MISSING_ID) is None

    execution_dto = ExecutionCreateDTO(
        workflow_id=_WF_ID,
        status="PENDING",
        organization_id=_ORG_ID,
        created_by=_USR_ID,
        target_locale="fi",
    )
    created_id = await repo.create_execution(execution_dto)
    assert created_id.startswith("exe_")

    status = await repo.get_execution_status(created_id)
    assert status == "PENDING"

    executions = await repo.get_all_executions(organization_id=_ORG_ID, user_id=_USR_ID)
    assert len(executions) == 1
    assert executions[0].id == created_id

    await repo.delete_execution(created_id)
    assert await repo.get_execution_status(created_id) is None
    assert len(await repo.get_all_executions(organization_id=_ORG_ID)) == 0


@pytest.mark.asyncio
async def test_workflow_repo() -> None:
    """Verify WorkflowRepositoryImpl workflow and step CRUD roundtrips over InMemoryUnitOfWork."""
    base_uow = InMemoryUnitOfWork()
    repo = WorkflowRepositoryImpl(uow_factory=lambda: InMemoryUnitOfWork(base_uow.store))
    assert await repo.get_all_workflows(organization_id=_ORG_ID) == []

    wf = WorkflowFactory.build(
        id=_WF_ID,
        slug="test_wf",
        organization_id=_ORG_ID,
        default_profile_id=_PRF_ID,
        model_registry_id=_SYS_ID,
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=[],
    )
    await repo.save_workflow(wf)
    persisted = await repo.get_workflow_by_id(wf.id)
    assert persisted is not None
    assert persisted.id == wf.id

    assert await repo.count_workflows() == 1
    workflows = await repo.get_all_workflows(organization_id=_ORG_ID)
    assert len(workflows) == 1

    step_dto = StepCreateDTO(
        slug="s1",
        name=I18nTextFactory.build(translations={"en": "Step 1", "fi": "Vaihe 1"}),
        type=StepType.LOGIC,
        hook="my_hook",
        criteria_block_ids=[],
        pre_hooks=[],
        post_hooks=[],
        allowed_mcp_tools=[],
        mcp_tool_params={},
        expected_inputs=[],
    )
    step_id = await repo.create_step(step_dto)
    steps = await repo.get_all_steps()
    assert len(steps) == 1
    assert steps[0].id == step_id

    await repo.update_step(
        step_id,
        StepUpdateDTO(name=I18nTextFactory.build(translations={"en": "Test", "fi": "Testi"})),
    )
    updated = await repo.get_step_by_id(step_id)
    assert updated is not None
    assert updated.name.translations["en"] == "Test"

    await repo.delete_step(step_id)
    assert await repo.get_step_by_id(step_id) is None

    await repo.delete_workflow(wf.id)
    assert await repo.get_workflow_by_id(wf.id) is None


@pytest.mark.asyncio
async def test_identity_repo() -> None:
    """Verify IdentityRepositoryImpl organization roundtrips over InMemoryUnitOfWork."""
    base_uow = InMemoryUnitOfWork()
    repo = IdentityRepositoryImpl(uow_factory=lambda: InMemoryUnitOfWork(base_uow.store))
    assert await repo.list_organizations() == []

    org = Organization(
        id=_ORG_ID,
        name="Test Org",
        is_active=True,
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=1000.0,
        tpm_limit=100000,
        rpm_limit=1000,
        allowed_email_domains=[],
    )
    org_id = await repo.create_organization(org)
    persisted = await repo.get_organization(org_id)
    assert persisted is not None
    assert persisted.name == "Test Org"

    all_orgs = await repo.list_organizations()
    assert len(all_orgs) == 1
    assert all_orgs[0].id == org_id

    await repo.delete_organization(org_id)
    assert await repo.get_organization(org_id) is None
    assert len(await repo.list_organizations()) == 0


@pytest.mark.asyncio
async def test_prompt_block_task_brief_output_profile_and_report_repos() -> None:
    """Verify PromptBlock, TaskBrief, OutputProfile, and ReportArtifact repository roundtrips."""
    base_uow = InMemoryUnitOfWork()

    def _uow_factory() -> InMemoryUnitOfWork:
        return InMemoryUnitOfWork(base_uow.store)

    pb_repo = PromptBlockRepositoryImpl(uow_factory=_uow_factory)
    block = SystemRulePromptBlockFactory.build(id=_BLK_ID, slug="comp2")
    await pb_repo.create_prompt_block(block)
    assert await pb_repo.get_prompt_block_by_id(block.id) == block
    assert len(await pb_repo.get_all_prompt_blocks()) == 1
    assert await pb_repo.delete_prompt_block(block.id) is True
    assert await pb_repo.get_prompt_block_by_id(block.id) is None

    tb_repo = TaskBriefRepositoryImpl(uow_factory=_uow_factory)
    brief = TaskBriefFactory.build(id=_TBR_ID, slug="brief_1")
    await tb_repo.create_task_brief(brief)
    assert await tb_repo.get_task_brief_by_id(brief.id) == brief
    assert len(await tb_repo.get_all_task_briefs()) == 1
    assert await tb_repo.delete_task_brief(brief.id) is True

    op_repo = OutputProfileRepositoryImpl(uow_factory=_uow_factory)
    profile = OutputProfileFactory.build(id=_PRF_ID, workflow_id=_WF_ID, content_blocks=[])
    await op_repo.create_output_profile(profile)
    assert await op_repo.get_output_profile_by_id(profile.id) == profile
    assert len(await op_repo.get_all_output_profiles()) == 1
    assert await op_repo.delete_output_profile(profile.id) is True

    exec_repo = ExecutionRepositoryImpl(uow_factory=_uow_factory)
    exe_id = await exec_repo.create_execution(
        ExecutionCreateDTO(workflow_id=_WF_ID, status="PENDING", organization_id=_ORG_ID, target_locale="en")
    )
    rep_repo = ReportArtifactRepositoryImpl(uow_factory=_uow_factory)
    report = ReportArtifactFactory.build(id=_REP_ID, execution_id=exe_id, workflow_id=_WF_ID, profile_id=_PRF_ID)
    await rep_repo.create_report_artifact(report)
    assert await rep_repo.get_report_artifact(report.id) == report
    assert len(await rep_repo.list_report_artifacts_by_execution(exe_id)) == 1
    assert await rep_repo.delete_report_artifact(report.id) is True


@pytest.mark.asyncio
async def test_system_repo() -> None:
    """Verify SystemRepositoryImpl model registry CRUD over InMemoryUnitOfWork."""
    base_uow = InMemoryUnitOfWork()
    repo = SystemRepositoryImpl(uow_factory=lambda: InMemoryUnitOfWork(base_uow.store))

    with pytest.raises(ResourceNotFoundError):
        await repo.get_model_registry(_SYS_MISSING_ID)

    profile = ModelProfile(
        provider="ai_studio",
        model_name="gemini-2.5-flash",
        allowed_tools=[],
        additional_params=ProviderExtraParamsDTO(),
    )
    reg = SystemConfigModelRegistry(
        id=_SYS_ID,
        name="Default Model Registry",
        default_provider=LLMProvider.AI_STUDIO,
        tier_definitions={tier: profile for tier in CognitiveTier},
    )
    await repo.update_model_registry(reg)

    fetched = await repo.get_model_registry(reg.id)
    assert fetched.id == reg.id
    assert fetched.name == "Default Model Registry"
    assert len(await repo.get_all_model_registries()) == 1


@pytest.mark.asyncio
async def test_audit_repo() -> None:
    """Verify AuditRepositoryImpl append-only audit and usage rollups over InMemoryUnitOfWork."""
    base_uow = InMemoryUnitOfWork()
    repo = AuditRepositoryImpl(uow_factory=lambda: InMemoryUnitOfWork(base_uow.store))
    assert await repo.get_audit_logs(organization_id=_ORG_ID, actor_id=_USR_ID, event_type="run") == []

    await repo.log_audit_event(
        AuditLogCreateDTO(
            event_type="test",
            actor_id=_USR_ID,
            organization_id=_ORG_ID,
            resource_type="workflow",
            resource_id=_WF_ID,
            details={},
        )
    )
    stored_logs = await repo.get_audit_logs(organization_id=_ORG_ID, event_type="test")
    assert len(stored_logs) == 1

    record = UsageRecordFactory.build(
        id=_USG_ID,
        org_id=_ORG_ID,
        user_id=_USR_ID,
        model="gemini-2.5-pro",
        input_tokens=10,
        output_tokens=0,
        cached_tokens=0,
        cost_usd=0.0,
        timestamp=datetime.now(UTC),
    )
    await repo.log_usage(record)
    usage_records = await repo.get_usage_records("organization", _ORG_ID)
    assert len(usage_records) == 1
    assert usage_records[0].model == "gemini-2.5-pro"

    rep = await repo.get_detailed_usage("organization", _ORG_ID)
    assert isinstance(rep, DetailedUsageDTO)


@pytest.mark.asyncio
async def test_repositories_v2_occ_conflict_and_invalid_payload_failure() -> None:
    """Verify stale expected_state_version raises HTTP 409 CONFLICT and malformed entity IDs raise VALIDATION_FAILED."""
    base_uow = InMemoryUnitOfWork()
    unified = UnifiedWorkflowRepository(uow_factory=lambda: InMemoryUnitOfWork(base_uow.store))

    created_id = await unified.create_execution(
        ExecutionCreateDTO(
            workflow_id=_WF_ID,
            output_profile_id=_PRF_ID,
            organization_id=_ORG_ID,
            created_by=_USR_ID,
            status="PENDING",
            target_locale="en",
        )
    )
    assert await unified.update_execution(
        created_id,
        ExecutionUpdateDTO(status=ExecutionStatus.RUNNING, expected_state_version=1),
    )

    with pytest.raises(AppException) as occ_exc:
        await unified.update_execution(
            created_id,
            ExecutionUpdateDTO(status=ExecutionStatus.PASSED, expected_state_version=1),
        )
    assert occ_exc.value.status_code == 409
    assert occ_exc.value.details["error_code"] == ErrorCodes.CONFLICT.value

    with pytest.raises(AppException) as bad_id_exc:
        await unified.get_workflow("usr_0195f3a0000070008000000000000001")
    assert bad_id_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
