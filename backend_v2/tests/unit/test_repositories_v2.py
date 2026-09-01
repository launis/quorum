from datetime import UTC, datetime
from unittest.mock import AsyncMock

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
from backend_v2.models.domain.base import (
    AuditLogCreateDTO,
    DetailedUsageDTO,
    UsageAggregateUpdateDTO,
    UsageRecord,
)
from backend_v2.models.domain.prompt_blocks import SystemRulePromptBlock
from backend_v2.models.dtos.studio import StepCreateDTO, StepUpdateDTO
from backend_v2.models.enums import BlockDataType, PromptBlockCategory, StepType
from backend_v2.models.v2_core import I18nText


@pytest.fixture
def mock_driver() -> AsyncMock:
    driver = AsyncMock(spec=StorageDriver)
    driver.query.return_value = []
    driver.get.return_value = None
    driver.upsert.return_value = "upserted_id"
    driver.update.return_value = True
    driver.delete.return_value = True
    return driver


@pytest.mark.asyncio
async def test_execution_repo(mock_driver: AsyncMock) -> None:
    repo = ExecutionRepositoryImpl(mock_driver)
    status = await repo.get_execution_status("exec_123")
    assert status is None

    await repo.delete_execution("exec_123")
    mock_driver.delete.assert_called_with("executions", "exec_123")

    mock_driver.get.return_value = {"id": "exec_123", "status": "PENDING"}
    from backend_v2.exceptions import AppException

    with pytest.raises(AppException):
        await repo.get_execution("exec_123")

    mock_driver.query.return_value = []
    executions = await repo.get_all_executions(organization_id="org1")
    assert executions == []
    recent = await repo.get_recent_completed_executions()
    assert recent == []
    mock_driver.count.return_value = 5
    assert await repo.count_executions_by_matrix("m1") == 5


@pytest.mark.asyncio
async def test_workflow_repo(mock_driver: AsyncMock) -> None:
    repo = WorkflowRepositoryImpl(mock_driver)
    mock_driver.query.return_value = []
    res = await repo.get_all_workflows(organization_id="org1")
    assert res == []

    await repo.delete_workflow("wf_1")
    mock_driver.delete.assert_called_with("workflows", "wf_1")

    await repo.get_workflow_by_id("wf_1")
    mock_driver.count.return_value = 10
    await repo.count_workflows()

    await repo.get_all_steps()
    step_dto = StepCreateDTO(
        slug="s1",
        name=I18nText(translations={"en": "Step 1"}),
        type=StepType.LLM,
    )
    await repo.create_step(step_dto)
    await repo.update_step("s1", StepUpdateDTO(name=I18nText(translations={"en": "Test"})))


@pytest.mark.asyncio
async def test_identity_repo(mock_driver: AsyncMock) -> None:
    repo = IdentityRepositoryImpl(mock_driver)
    res = await repo.list_organizations()
    assert res == []

    await repo.delete_organization("org_1")
    mock_driver.delete.assert_called_with("organizations", "org_1")


@pytest.mark.asyncio
async def test_component_repo(mock_driver: AsyncMock) -> None:
    repo = ComponentRepositoryImpl(mock_driver)
    res = await repo.get_all_components(type="agent")
    assert res == []

    await repo.delete_component("comp_1")
    assert mock_driver.delete.call_count == 0

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


@pytest.mark.asyncio
async def test_knowledge_repo(mock_driver: AsyncMock) -> None:
    repo = KnowledgeRepositoryImpl(mock_driver)
    res = await repo.get_banned_phrases()
    assert res == []


@pytest.mark.asyncio
async def test_system_repo(mock_driver: AsyncMock) -> None:
    repo = SystemRepositoryImpl(mock_driver)
    from backend_v2.exceptions import ResourceNotFoundError

    with pytest.raises(ResourceNotFoundError):
        await repo.get_model_registry()


@pytest.mark.asyncio
async def test_audit_repo(mock_driver: AsyncMock) -> None:
    repo = AuditRepositoryImpl(mock_driver)
    res = await repo.get_audit_logs(organization_id="org1", actor_id="user1", action="run")
    assert res == []

    await repo.log_audit_event(
        AuditLogCreateDTO(
            action="test",
            actor_id="user1",
            organization_id="org1",
        )
    )
    await repo.log_usage(
        UsageRecord(
            org_id="org1",
            user_id="user1",
            model="gpt-4o",
            input_tokens=10,
            output_tokens=0,
            cached_tokens=0,
            cost_usd=0.0,
            timestamp=datetime.now(UTC),
        )
    )
    await repo.get_usage_records("organization", "org1")
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
