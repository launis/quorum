from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories import (
    AuditRepositoryImpl,
    ComponentRepositoryImpl,
    ExecutionRepositoryImpl,
    IdentityRepositoryImpl,
    KnowledgeRepositoryImpl,
    SystemRepositoryImpl,
    WorkflowRepositoryImpl,
)
from backend_v2.database.tinydb_driver import TinyDBDriver
from backend_v2.database.wrapper import TinyDBClient
from backend_v2.exceptions import ResourceNotFoundError
from backend_v2.models.auth import Organization, SubscriptionStatus
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.base import (
    AuditLogCreateDTO,
    DetailedUsageDTO,
    UsageAggregateUpdateDTO,
    UsageRecord,
)
from backend_v2.models.domain.prompt_blocks import SystemRulePromptBlock
from backend_v2.models.domain.system_config import ModelProfile, SystemConfigModelRegistry
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.studio import StepCreateDTO, StepUpdateDTO
from backend_v2.models.dtos.trace import ExecutionCreateDTO
from backend_v2.models.enums import (
    BlockDataType,
    CognitiveTier,
    HistoricalContextMode,
    LLMProvider,
    PromptBlockCategory,
    StepType,
)


@pytest.fixture
def driver(tmp_path: Path) -> StorageDriver:
    """Provides a real TinyDBDriver over ephemeral tmp_path."""
    db_path = str(tmp_path / "test_repo_v2.json")
    return TinyDBDriver(TinyDBClient(db_path))


@pytest.mark.asyncio
async def test_execution_repo(driver: StorageDriver) -> None:
    repo = ExecutionRepositoryImpl(driver)
    status = await repo.get_execution_status("exe_123")
    assert status is None

    execution_dto = ExecutionCreateDTO(
        workflow_id="wor_0123456789abcdef",
        status="PENDING",
        organization_id="org1",
        target_locale="fi",
    )
    created_id = await repo.create_execution(execution_dto)
    assert created_id.startswith("exe_")

    status = await repo.get_execution_status(created_id)
    assert status == "PENDING"

    executions = await repo.get_all_executions(organization_id="org1")
    assert len(executions) == 1
    assert executions[0].id == created_id

    await repo.delete_execution(created_id)
    assert await repo.get_execution_status(created_id) is None
    assert len(await repo.get_all_executions(organization_id="org1")) == 0


@pytest.mark.asyncio
async def test_workflow_repo(driver: StorageDriver) -> None:
    repo = WorkflowRepositoryImpl(driver)
    res = await repo.get_all_workflows(organization_id="org1")
    assert res == []

    wf = Workflow(
        id="wor_0123456789abcdef",
        slug="test_wf",
        name=I18nText(translations={"en": "Test Workflow"}),
        description=I18nText(translations={"en": "Test Description"}),
        status="active",
        version=1,
        organization_id="org1",
        default_profile_id="prf_default",
        model_registry_id="cfg_model_registry_01",
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=[],
    )
    await repo.save_workflow(wf)
    persisted = await repo.get_workflow_by_id(wf.id)
    assert persisted is not None
    assert persisted.id == wf.id

    assert await repo.count_workflows() == 1
    workflows = await repo.get_all_workflows(organization_id="org1")
    assert len(workflows) == 1

    step_dto = StepCreateDTO(
        slug="s1",
        name=I18nText(translations={"en": "Step 1"}),
        type=StepType.LOGIC,
        hook="my_hook",
        criteria_block_ids=[],
        pre_hooks=[],
        post_hooks=[],
        allowed_mcp_tools=[],
        expected_inputs=[],
    )
    step_id = await repo.create_step(step_dto)
    assert step_id is not None
    steps = await repo.get_all_steps()
    assert len(steps) == 1
    assert steps[0].id == step_id

    await repo.update_step(step_id, StepUpdateDTO(name=I18nText(translations={"en": "Test"})))
    updated = await repo.get_step_by_id(step_id)
    assert updated is not None
    assert updated.name.translations["en"] == "Test"

    await repo.delete_step(step_id)
    assert await repo.get_step_by_id(step_id) is None

    await repo.delete_workflow(wf.id)
    assert await repo.get_workflow_by_id(wf.id) is None


@pytest.mark.asyncio
async def test_identity_repo(driver: StorageDriver) -> None:
    repo = IdentityRepositoryImpl(driver)
    res = await repo.list_organizations()
    assert res == []

    org = Organization(
        id="org_0123456789abcdef",
        name="Test Org",
        is_active=True,
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=1000.0,
        tpm_limit=100000,
        rpm_limit=1000,
    )
    org_id = await repo.create_organization(org)
    assert org_id is not None

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
async def test_component_repo(driver: StorageDriver) -> None:
    repo = ComponentRepositoryImpl(driver)
    res = await repo.get_all_components(type="agent")
    assert res == []

    block = SystemRulePromptBlock(
        id="blk_0000000000000001",
        slug="comp2",
        label=I18nText(translations={"en": "Component 2"}),
        description=I18nText(translations={"en": "Description"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
        type=BlockDataType.INSTRUCTION,
        instruction_text="Test instruction",
    )
    await repo.create_component(block)
    persisted = await repo.get_component_by_id(block.id)
    assert persisted is not None
    assert persisted.id == block.id

    all_components = await repo.get_all_components()
    assert len(all_components) == 1

    await repo.delete_component(block.id)
    assert await repo.get_component_by_id(block.id) is None
    assert len(await repo.get_all_components()) == 0


@pytest.mark.asyncio
async def test_knowledge_repo(driver: StorageDriver) -> None:
    repo = KnowledgeRepositoryImpl(driver)
    res = await repo.get_banned_phrases()
    assert res == []

    await repo.add_banned_phrase("bad_phrase", language="en")
    phrases = await repo.get_banned_phrases()
    assert len(phrases) == 1
    assert phrases[0].phrase == "bad_phrase"

    assert await repo.delete_banned_phrase("bad_phrase") is True
    assert len(await repo.get_banned_phrases()) == 0


@pytest.mark.asyncio
async def test_system_repo(driver: StorageDriver) -> None:
    repo = SystemRepositoryImpl(driver)

    with pytest.raises(ResourceNotFoundError):
        await repo.get_model_registry("cfg_missing")

    reg = SystemConfigModelRegistry(
        id="sys_1234567890abcdef1234567890abcdef",
        name="Default Model Registry",
        type="model_registry",
        default_provider=LLMProvider.AI_STUDIO,
        tier_definitions={
            CognitiveTier.FAST: ModelProfile(provider="ai_studio", model_name="gemini-2.5-flash"),
            CognitiveTier.BALANCED: ModelProfile(provider="ai_studio", model_name="gemini-2.5-flash"),
            CognitiveTier.DEEP: ModelProfile(provider="ai_studio", model_name="gemini-2.5-pro"),
            CognitiveTier.REASONING: ModelProfile(provider="ai_studio", model_name="gemini-2.5-pro"),
        },
    )
    await repo.update_model_registry(reg)

    fetched = await repo.get_model_registry(reg.id)
    assert fetched is not None
    assert fetched.id == reg.id
    assert fetched.name == "Default Model Registry"

    all_registries = await repo.get_all_model_registries()
    assert len(all_registries) == 1


@pytest.mark.asyncio
async def test_audit_repo(driver: StorageDriver) -> None:
    repo = AuditRepositoryImpl(driver)
    res = await repo.get_audit_logs(organization_id="org1", actor_id="user1", action="run")
    assert res == []

    await repo.log_audit_event(
        AuditLogCreateDTO(
            action="test",
            actor_id="user1",
            organization_id="org1",
        )
    )
    raw_logs = await driver.query("audit_logs")
    assert any("action" in r and r["action"] == "test" for r in raw_logs)

    record = UsageRecord(
        id="usg_0123456789abcdef",
        org_id="org1",
        user_id="user1",
        model="gpt-4o",
        input_tokens=10,
        output_tokens=0,
        cached_tokens=0,
        cost_usd=0.0,
        timestamp=datetime.now(UTC),
    )
    await repo.log_usage(record)
    usage_records = await repo.get_usage_records("organization", "org1")
    assert len(usage_records) == 1
    assert usage_records[0].model == "gpt-4o"

    rep = await repo.get_detailed_usage("org", "org1")
    assert isinstance(rep, DetailedUsageDTO)

    agg = UsageAggregateUpdateDTO(
        input_tokens=10,
        output_tokens=0,
        cached_tokens=0,
        cost_usd=0.0,
        execution_count=1,
    )
    await repo.upsert_usage_aggregate("org", "org1", "2026-04", agg)
