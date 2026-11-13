"""Unit tests for UnifiedWorkflowRepository delegation over UnitOfWorkFactory."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from backend_v2.database.repository import UnifiedWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.auth import (
    Organization,
    OrganizationUpdateDTO,
    SubscriptionStatus,
    User,
    UserRole,
    UserUpdate,
)
from backend_v2.models.core_base import generate_uuid7
from backend_v2.models.domain.base import AuditLogCreateDTO
from backend_v2.models.domain.system_config import (
    ModelProfile,
    ProviderExtraParamsDTO,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
)
from backend_v2.models.dtos.report_artifact import ReportArtifactUpdateDTO
from backend_v2.models.dtos.studio import (
    StepCreateDTO,
    StepUpdateDTO,
    WorkflowCreateDTO,
    WorkflowUpdateDTO,
)
from backend_v2.models.dtos.trace import (
    ExecutionCreateDTO,
    ExecutionUpdateDTO,
    ProgressTracePayloadDTO,
    TraceEventMetadataDTO,
)
from backend_v2.models.enums import (
    CognitiveTier,
    ExecutionStatus,
    LLMProvider,
    StepType,
    SystemLocale,
    TargetBlockType,
)
from backend_v2.models.state import TraceEvent
from backend_v2.tests.factories.model_factories import (
    ExecutionRecordFactory,
    I18nTextFactory,
    OutputProfileFactory,
    ReportArtifactFactory,
    SystemRulePromptBlockFactory,
    TaskBriefFactory,
    UsageRecordFactory,
)
from backend_v2.tests.fakes.in_memory_uow import InMemoryUnitOfWork

_WF_ID = "wf_0195f3a0000070008123456789abcdef"
_PRF_ID = "prf_0195f3a0000070008123456789abcdef"
_EXE_ID = "exe_0195f3a0000070008123456789abcdef"
_ORG_ID = "org_0195f3a0000070008123456789abcdef"
_USR_ID = "usr_0195f3a0000070008123456789abcdef"
_BLK_ID = "blk_0195f3a0000070008123456789abcdef"
_TBR_ID = "tbr_0195f3a0000070008123456789abcdef"
_REP_ID = "rep_0195f3a0000070008123456789abcdef"
_MRG_ID = "mrg_0195f3a0000070018234567890abcdef"
_MCP_GW_ID = "mcp_0195f3a0000070018234567890abcde1"
_MCP_MISSING_ID = "mcp_0195f3a0000070018234567890abcde9"


@pytest.mark.asyncio
async def test_get_execution_fails_fast_on_corrupt_sidecar_payload_failure() -> None:
    """Verify corrupt JSONB in execution_payloads triggers Fail-Fast VALIDATION_FAILED on get_execution."""
    base_uow = InMemoryUnitOfWork()
    repo = UnifiedWorkflowRepository(uow_factory=lambda: InMemoryUnitOfWork(base_uow.store))

    valid_record = ExecutionRecordFactory.build(
        id=_EXE_ID,
        organization_id=_ORG_ID,
        workflow_id=_WF_ID,
        execution_trace=[],
    )
    async with InMemoryUnitOfWork(base_uow.store) as uow:
        await uow.entities.save_execution(valid_record)

    existing_sidecar = base_uow.store.execution_payloads[_EXE_ID]
    base_uow.store.execution_payloads[_EXE_ID] = existing_sidecar.model_copy(
        update={"context_variables": '{"invalid_cv_key": 1}'}
    )

    with pytest.raises(AppException) as exc_info:
        await repo.get_execution(_EXE_ID, hydrate=True)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_large_execution_trace_roundtrip_uses_sidecar_and_missing_update_raises_not_found() -> None:
    """Verify >100KB execution_trace persists in execution_payloads sidecar and missing update raises 404."""
    base_uow = InMemoryUnitOfWork()
    repo = UnifiedWorkflowRepository(uow_factory=lambda: InMemoryUnitOfWork(base_uow.store))

    large_events = [
        TraceEvent(
            event_id=generate_uuid7(),
            timestamp=datetime.now(UTC),
            step_name=_BLK_ID,
            event_type="progress",
            content=ProgressTracePayloadDTO(message="x" * 2048, progress_pct=50),
            metadata=TraceEventMetadataDTO(mcp_audit_traces=[]),
            mcp_audit_traces=[],
        )
        for _ in range(60)
    ]
    initial_record = ExecutionRecordFactory.build(
        id=_EXE_ID,
        organization_id=_ORG_ID,
        workflow_id=_WF_ID,
        execution_trace=[],
    )
    async with InMemoryUnitOfWork(base_uow.store) as uow:
        await uow.entities.save_execution(initial_record)

    assert await repo.update_execution(_EXE_ID, ExecutionUpdateDTO(execution_trace=large_events)) is True
    hydrated = await repo.get_execution(_EXE_ID)
    assert hydrated is not None
    assert len(hydrated.execution_trace) == 60

    with pytest.raises(ResourceNotFoundError):
        await repo.update_execution(
            "exe_0195f3a0000070008123456789abcde9",
            ExecutionUpdateDTO(execution_trace=large_events),
        )


@pytest.mark.asyncio
async def test_all_9_active_protocol_delegations_roundtrip() -> None:
    """Verify delegation across all 9 active V2 repository protocols on UnifiedWorkflowRepository."""
    base_uow = InMemoryUnitOfWork()
    repo = UnifiedWorkflowRepository(uow_factory=lambda: InMemoryUnitOfWork(base_uow.store))

    profile_tier = ModelProfile(
        provider="ai_studio",
        model_name="gemini-2.5-flash",
        allowed_tools=[],
        additional_params=ProviderExtraParamsDTO(),
    )
    reg = SystemConfigModelRegistry(
        id=_MRG_ID,
        name="Default Model Registry",
        default_provider=LLMProvider.AI_STUDIO,
        tier_definitions={tier: profile_tier for tier in CognitiveTier},
    )
    assert await repo.update_model_registry(reg) is True
    assert (await repo.get_model_registry(_MRG_ID)).id == _MRG_ID
    assert len(await repo.get_all_model_registries()) == 1

    gw = SystemConfigMCPGateways(
        id=_MCP_GW_ID,
        organization_id=_ORG_ID,
        name="Gateway",
        slug="default_mcp_gateway",
        tools=[],
    )
    assert await repo.update_mcp_gateways(gw) is True
    assert (await repo.get_mcp_gateways(_MCP_GW_ID)).id == _MCP_GW_ID
    assert (await repo.get_mcp_gateways()).id == _MCP_GW_ID
    assert len(await repo.get_all_mcp_gateways()) == 1
    extra_gw = SystemConfigMCPGateways(
        id="mcp_0195f3a0000070018234567890abcde2",
        organization_id=_ORG_ID,
        name="Extra Gateway",
        slug="extra_mcp_gateway",
        tools=[],
    )
    assert await repo.update_mcp_gateways(extra_gw) is True
    assert (await repo.get_mcp_gateways(extra_gw.id)).id == extra_gw.id
    assert await repo.delete_mcp_gateways(extra_gw.id) is True

    wf_id = await repo.create_workflow(
        WorkflowCreateDTO(
            slug="wf_slug",
            name="WF",
            description="Desc",
            model_registry_id=_MRG_ID,
            organization_id=_ORG_ID,
            expected_inputs=[],
            steps=[],
        )
    )
    assert await repo.get_workflow(wf_id) is not None
    assert await repo.get_workflow_by_id(wf_id) is not None
    assert await repo.get_workflow_definition(wf_id) is not None
    assert await repo.count_workflows() == 1
    assert len(await repo.get_all_workflows(organization_id=_ORG_ID)) == 1
    await repo.update_workflow(wf_id, WorkflowUpdateDTO(name="WF New"))
    await repo.update_workflow_definition(wf_id, WorkflowUpdateDTO(name="WF Def"))
    persisted_wf = await repo.get_workflow(wf_id)
    assert persisted_wf is not None
    assert await repo.save_workflow(persisted_wf) == wf_id

    step_id = await repo.create_step(
        StepCreateDTO(
            slug="step_slug",
            name=I18nTextFactory.build(translations={"en": "Step", "fi": "Vaihe"}),
            type=StepType.LOGIC,
            hook="h1",
            criteria_block_ids=[],
            pre_hooks=[],
            post_hooks=[],
            allowed_mcp_tools=[],
            mcp_tool_params={},
            expected_inputs=[],
        )
    )
    assert await repo.get_step(step_id) is not None
    assert await repo.get_step_by_id(step_id) is not None
    assert len(await repo.get_all_steps()) == 1
    await repo.update_step(
        step_id,
        StepUpdateDTO(name=I18nTextFactory.build(translations={"en": "Step Updated", "fi": "Vaihe"})),
    )
    persisted_step = await repo.get_step(step_id)
    assert persisted_step is not None
    assert await repo.save_step(persisted_step) == step_id
    assert await repo.delete_step(step_id, force_delete=True) is True

    exe_id = await repo.create_execution(
        ExecutionCreateDTO(
            workflow_id=wf_id,
            output_profile_id=_PRF_ID,
            organization_id=_ORG_ID,
            created_by=_USR_ID,
            raw_inputs=None,
        )
    )
    assert await repo.get_execution(exe_id) is not None
    assert await repo.get_execution_status(exe_id) == "PENDING"
    assert await repo.update_execution(exe_id, ExecutionUpdateDTO(status=ExecutionStatus.PASSED)) is True
    event = TraceEvent(
        event_id=generate_uuid7(),
        timestamp=datetime.now(UTC),
        step_name="step_1",
        event_type="progress",
        content=ProgressTracePayloadDTO(message="ok", progress_pct=100),
        metadata=TraceEventMetadataDTO(mcp_audit_traces=[]),
        mcp_audit_traces=[],
    )
    assert await repo.append_trace_event(exe_id, event) is True
    assert len(await repo.get_all_executions(organization_id=_ORG_ID)) == 1
    assert len(await repo.get_recent_completed_executions()) == 1

    art = ReportArtifactFactory.build(id=_REP_ID, execution_id=exe_id, workflow_id=wf_id, profile_id=_PRF_ID)
    await repo.create_report_artifact(art)
    assert await repo.get_report_artifact(_REP_ID) is not None
    assert len(await repo.list_report_artifacts_by_execution(exe_id)) == 1
    await repo.update_report_artifact(_REP_ID, ReportArtifactUpdateDTO(error_message="Updated"))
    assert await repo.delete_report_artifact(_REP_ID) is True
    assert await repo.delete_execution(exe_id) is True

    block = SystemRulePromptBlockFactory.build(id=_BLK_ID, slug="blk_1", organization_id=_ORG_ID)
    await repo.create_prompt_block(block)
    assert await repo.get_prompt_block(_BLK_ID) is not None
    assert await repo.get_prompt_block_by_id(_BLK_ID) is not None
    assert len(await repo.get_all_prompt_blocks()) == 1
    assert len(await repo.get_all_prompt_blocks_models()) == 1
    assert len(await repo.get_prompt_blocks_by_ids([_BLK_ID])) == 1
    assert await repo.update_prompt_block(_BLK_ID, block) is True
    assert await repo.delete_prompt_block(_BLK_ID, force_delete=True) is True

    brief = TaskBriefFactory.build(id=_TBR_ID, slug="tbr_1")
    await repo.create_task_brief(brief)
    assert await repo.get_task_brief_by_id(_TBR_ID) is not None
    assert len(await repo.get_all_task_briefs()) == 1
    assert await repo.update_task_brief(_TBR_ID, brief) is True
    assert await repo.delete_task_brief(_TBR_ID) is True

    profile = OutputProfileFactory.build(
        id=_PRF_ID,
        slug="prf_1",
        workflow_id=wf_id,
        target_block_order=[TargetBlockType.METADATA_BLOCK],
        content_blocks=[],
    )
    await repo.create_output_profile(profile)
    assert await repo.get_output_profile_by_id(_PRF_ID) is not None
    assert len(await repo.get_all_output_profiles()) == 1
    assert len(await repo.get_all_output_profiles_models()) == 1
    assert await repo.update_output_profile(_PRF_ID, profile) is True
    assert await repo.delete_output_profile(_PRF_ID) is True
    assert await repo.delete_workflow(wf_id) is True

    org = Organization(
        id=_ORG_ID,
        name="Org",
        tier="enterprise",
        is_active=True,
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    await repo.create_organization(org)
    assert await repo.get_organization(_ORG_ID) is not None
    assert await repo.get_organization_model(_ORG_ID) is not None
    assert len(await repo.list_organizations()) == 1
    assert await repo.update_organization(_ORG_ID, OrganizationUpdateDTO(name="Org New")) is True

    user = User(
        id=_USR_ID,
        email="test@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        language=SystemLocale.EN,
        theme_mode="system",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        organization_id=_ORG_ID,
    )
    await repo.create_user(user)
    assert await repo.get_user(_USR_ID) is not None
    assert await repo.get_user_by_email("test@test.com") is not None
    assert len(await repo.list_users(_ORG_ID)) == 1
    assert await repo.update_user(_USR_ID, UserUpdate(name="User New")) is True

    await repo.log_audit_event(
        AuditLogCreateDTO(
            organization_id=_ORG_ID,
            actor_id=_USR_ID,
            event_type="WORKFLOW_TESTED",
            resource_type="workflow",
            resource_id=_WF_ID,
            details={},
        )
    )
    assert len(await repo.get_audit_logs(organization_id=_ORG_ID)) == 1
    usage_rec = UsageRecordFactory.build(
        org_id=_ORG_ID,
        user_id=_USR_ID,
        model="gemini-2.5-flash",
        input_tokens=20,
        output_tokens=10,
        cost_usd=0.25,
        timestamp=datetime.now(UTC),
    )
    await repo.log_usage(usage_rec)
    assert len(await repo.get_usage_records("organization", _ORG_ID)) == 1
    assert (await repo.aggregate_organization_usage(organization_id=_ORG_ID)).total_cost_usd == pytest.approx(0.25)
    assert await repo.get_org_usage_total(_ORG_ID) == pytest.approx(0.25)
    assert (await repo.get_detailed_usage("organization", _ORG_ID)).total_tokens >= 30

    assert await repo.delete_user(_USR_ID) is True
    await repo.delete_org_data(_ORG_ID)
    assert await repo.get_organization(_ORG_ID) is None


@pytest.mark.asyncio
async def test_system_repo_get_mcp_gateways_not_found_raises_failure() -> None:
    """Verify get_mcp_gateways raises ResourceNotFoundError when missing by ID or when none exist."""
    base_uow = InMemoryUnitOfWork()
    repo = UnifiedWorkflowRepository(uow_factory=lambda: InMemoryUnitOfWork(base_uow.store))

    with pytest.raises(ResourceNotFoundError) as empty_exc:
        await repo.get_mcp_gateways()
    assert empty_exc.value.status_code == 404

    with pytest.raises(ResourceNotFoundError) as id_exc:
        await repo.get_mcp_gateways(id=_MCP_MISSING_ID)
    assert id_exc.value.status_code == 404
    assert id_exc.value.details["resource_id"] == _MCP_MISSING_ID
