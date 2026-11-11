"""Unit tests for UnifiedWorkflowRepository and sub-repository delegation."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import JsonValue

from backend_v2.database.repositories.base import AppendOnlyRepositoryBase
from backend_v2.database.repositories.execution import HydrationPayloadValue
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
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.base import AuditLogCreateDTO
from backend_v2.models.domain.knowledge import (
    ClaimCreateDTO,
    ConceptCreateDTO,
    ReferenceCreateDTO,
)
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import PersonaPromptBlock
from backend_v2.models.domain.system_config import (
    ModelProfile,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
)
from backend_v2.models.domain.task_brief import TaskBrief
from backend_v2.models.dtos.studio import (
    StepCreateDTO,
    StepUpdateDTO,
    WorkflowCreateDTO,
    WorkflowUpdateDTO,
)
from backend_v2.models.dtos.trace import ExecutionCreateDTO, ExecutionUpdateDTO
from backend_v2.models.enums import (
    BlockDataType,
    CognitiveTier,
    ExecutionStatus,
    LLMProvider,
    PromptBlockCategory,
    SystemLocale,
    TargetBlockType,
)
from backend_v2.tests.fakes.in_memory_uow import InMemoryUnitOfWork


@pytest.mark.asyncio
async def test_hydrate_payloads_fails_fast_on_empty_blob() -> None:
    """Test that an empty storage blob triggers a Fail-Fast DATA_CORRUPTION error."""
    mock_driver = AsyncMock()
    mock_driver.read.return_value = b"   "

    repo = UnifiedWorkflowRepository(driver=mock_driver)

    with patch("backend_v2.database.repositories.execution.get_storage_driver", return_value=mock_driver):
        data: dict[str, HydrationPayloadValue] = {
            "id": "exe_123",
            "execution_trace_storage_path": "executions/exe_123/execution_trace.json",
        }

        with pytest.raises(AppException) as exc_info:
            await repo._hydrate_payloads(data)

        assert exc_info.value.status_code == 500
        assert exc_info.value.details["error_code"] == ErrorCodes.DATA_CORRUPTION.value
        assert "Missing blob trace data for execution_trace" in exc_info.value.message


@pytest.mark.asyncio
async def test_persist_audit_trace_fails_fast() -> None:
    """Test that failing to persist an audit trace raises an AppException."""
    mock_driver = AsyncMock()
    mock_driver.upsert.side_effect = Exception("DB crash")

    repo = UnifiedWorkflowRepository(driver=mock_driver)
    data: dict[str, JsonValue] = {
        "frozen_context": {
            "mcp_tool_audit": [
                {
                    "id": "audit_123",
                    "tool_id": "tool_1",
                    "step_name": "step_1",
                    "query": "query_text",
                }
            ]
        }
    }

    with pytest.raises(AppException) as exc_info:
        await repo._offload_payloads("doc_123", data)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR.value
    assert "Failed to persist audit trace" in exc_info.value.message


@pytest.mark.asyncio
async def test_offload_payloads_fails_fast() -> None:
    """Test that failing to offload massive payloads to storage raises an AppException."""
    mock_driver = AsyncMock()
    repo = UnifiedWorkflowRepository(driver=mock_driver)

    mock_storage_driver = AsyncMock()
    mock_storage_driver.save.side_effect = Exception("Storage crash")

    data: dict[str, JsonValue] = {
        "execution_trace": ["large_data"] * 10000  # Will exceed 100KB
    }

    with patch("backend_v2.database.repositories.execution.get_storage_driver", return_value=mock_storage_driver):
        with pytest.raises(AppException) as exc_info:
            await repo._offload_payloads("doc_123", data)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR.value
    assert "Failed to offload execution_trace" in exc_info.value.message


@pytest.mark.asyncio
async def test_hydrate_audit_trails_fails_fast() -> None:
    """Test that failing to query audit trails from DB raises an AppException."""
    mock_driver = AsyncMock()
    mock_driver.query.side_effect = Exception("Query crash")

    repo = UnifiedWorkflowRepository(driver=mock_driver)
    data: dict[str, HydrationPayloadValue] = {"id": "doc_123"}

    with patch("backend_v2.database.repositories.execution.get_storage_driver"):
        with pytest.raises(AppException) as exc_info:
            await repo._hydrate_payloads(data)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.DATA_CORRUPTION.value
    assert "Failed to hydrate audit_trails" in exc_info.value.message


@pytest.mark.asyncio
async def test_workflow_fetching() -> None:
    """Test that get_workflow_by_id returns None when the workflow record does not exist."""
    mock_driver = AsyncMock()
    mock_driver.get.return_value = None
    repo = UnifiedWorkflowRepository(driver=mock_driver)

    workflow_id = "wor_0195f3a0000070008123456789abcdef"
    res = await repo.get_workflow_by_id(workflow_id)

    assert res is None
    mock_driver.get.assert_called_once_with("workflows", workflow_id)


@pytest.mark.asyncio
async def test_all_passthrough_methods() -> None:
    """Test delegation across UnifiedWorkflowRepository passthrough methods."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = []
    mock_driver.get.return_value = None
    mock_driver.upsert.return_value = "new_id"
    mock_driver.update.return_value = True
    mock_driver.delete.return_value = True

    repo = UnifiedWorkflowRepository(driver=mock_driver)

    await repo.get_execution("1")
    await repo.get_execution_status("1")
    await repo.create_execution(
        ExecutionCreateDTO(
            workflow_id="wor_0195f3a0000070008123456789abcdef",
            output_profile_id="pro_0195f3a0000070008123456789abcdef",
            raw_inputs=None,
        )
    )
    await repo.update_execution(
        "exe_0195f3a0000070008123456789abcdef", ExecutionUpdateDTO(status=ExecutionStatus.PASSED)
    )
    await repo.delete_execution("1")
    await repo.get_all_executions()
    await repo.get_recent_completed_executions()
    uow = InMemoryUnitOfWork()
    repo._uow_factory = lambda: uow
    await repo.log_audit_event(
        AuditLogCreateDTO(
            organization_id="org_0195f3a0000070008123456789abcdef",
            actor_id="usr_0195f3a0000070008123456789abcdef",
            event_type="WORKFLOW_TESTED",
            resource_type="workflow",
            resource_id="wor_0195f3a0000070008123456789abcdef",
            details={},
        )
    )
    await repo.get_audit_logs()
    await repo.get_all_workflows()
    await repo.get_workflow_by_id("1")
    await repo.create_workflow(
        WorkflowCreateDTO(
            slug="wf_slug",
            name="WF",
            description=None,
            expected_inputs=[],
            steps=[],
        )
    )
    mock_driver.get.return_value = {"id": "1", "version": 1, "slug": "s"}
    await repo.update_workflow("1", WorkflowUpdateDTO(name="WF New"))
    await repo.update_workflow_definition("1", WorkflowUpdateDTO(name="WF New"))
    await repo.delete_workflow("1")
    await repo.get_all_steps()
    mock_driver.get.return_value = None
    await repo.get_step_by_id("1")
    await repo.create_step(
        StepCreateDTO(
            slug="step_slug",
            name=I18nText(translations={"en": "Step"}),
            criteria_block_ids=[],
            pre_hooks=[],
            post_hooks=[],
            allowed_mcp_tools=[],
            mcp_tool_params={},
            expected_inputs=[],
        )
    )
    mock_driver.get.return_value = {"id": "1", "version": 1, "slug": "s"}
    await repo.update_step("1", StepUpdateDTO(name=I18nText(translations={"en": "Step"})))
    await repo.delete_step("1", force_delete=True)
    await repo.get_all_components()
    mock_driver.get.return_value = None
    await repo.get_component_by_id("1")
    persona_block = PersonaPromptBlock(
        id="blk_0195f3a0000070008123456789abcdef",
        slug="blk_1",
        label=I18nText(translations={"en": "Block"}),
        description=I18nText(translations={"en": "Desc"}),
        category_id=PromptBlockCategory.EXECUTION_PERSONA,
        type=BlockDataType.INSTRUCTION,
        organization_id="org_1234abcd",
        role_enforcement="Persona",
    )
    mock_driver.get.return_value = persona_block.model_dump(mode="json")
    await repo.update_component_metadata("1", "mod", "cls")
    await repo.register_component(persona_block)
    await repo.create_component(persona_block)
    mock_driver.get.return_value = None
    await repo.get_prompt_block_by_id("1")
    await repo.get_all_prompt_blocks()
    await repo.create_prompt_block(persona_block)
    mock_driver.get.return_value = {"id": "1", "version": 1, "slug": "s"}
    await repo.update_prompt_block("1", persona_block)
    await repo.delete_prompt_block("1", force_delete=True)
    mock_driver.get.return_value = None
    await repo.get_agent_by_id("1")
    await repo.get_all_agents()
    await repo.create_agent(persona_block)
    mock_driver.get.return_value = {"id": "1", "version": 1, "slug": "s"}
    await repo.update_agent("1", persona_block)
    await repo.delete_agent("1")
    mock_driver.get.return_value = None
    await repo.get_banned_phrases()
    await repo.add_banned_phrase("phrase")
    await repo.delete_banned_phrase("phrase")
    await repo.count_workflows()
    await repo.get_prompt_template("1")
    dummy_reg = SystemConfigModelRegistry(
        id="sys_0195f3a0000070018234567890abcdef",
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
    mock_driver.get.return_value = dummy_reg.model_dump(mode="json")
    await repo.get_model_registry("sys_0195f3a0000070018234567890abcdef")
    await repo.update_model_registry(dummy_reg)
    mock_driver.query.return_value = [
        {
            "id": "sys_0195f3a0000070018234567890abcdef",
            "name": "Gateway",
            "slug": "default_mcp_gateway",
            "type": "mcp_gateways",
            "tools": [],
        }
    ]
    await repo.get_mcp_gateways()
    await repo.update_mcp_gateways(
        SystemConfigMCPGateways(
            id="sys_0195f3a0000070018234567890abcdef",
            name="Gateway",
            slug="default_mcp_gateway",
            type="mcp_gateways",
            tools=[],
        )
    )
    mock_driver.query.return_value = []
    await repo.count_executions_by_matrix("1")
    await repo.get_matrices_using_dimension("1")
    await repo.list_organizations()
    mock_driver.get.return_value = None
    await repo.get_organization("1")
    await repo.create_organization(
        Organization(
            id="org_0195f3a0000070008123456789abcdef",
            name="Org",
            tier="enterprise",
            is_active=True,
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=500.0,
            tpm_limit=50000,
            rpm_limit=500,
            allowed_email_domains=[],
        )
    )
    await repo.update_organization("1", OrganizationUpdateDTO(name="Org New"))
    await repo.delete_organization("1")
    await repo.list_users()
    await repo.get_user("1")
    await repo.get_user_by_email("email")
    await repo.create_user(
        User(
            id="usr_0195f3a0000070008123456789abcdef",
            email="test@test.com",
            role=UserRole.MEMBER,
            is_active=True,
            language=SystemLocale.EN,
            theme_mode="system",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            organization_id="org_0195f3a0000070008123456789abcdef",
        )
    )
    await repo.update_user("1", UserUpdate(name="User New"))
    await repo.delete_user("1")
    await repo.delete_org_data("1")
    await repo.get_org_usage_total("1")
    await repo.add_concept(ConceptCreateDTO(name="concept_1"))
    await repo.add_reference(ReferenceCreateDTO(name="reference_1"))
    await repo.add_claim(ClaimCreateDTO(name="claim_1"))
    await repo.get_all_output_profiles()
    await repo.get_output_profile_by_id("1")
    await repo.create_output_profile(
        OutputProfile(
            id="prf_0195f3a0000070008123456789abcdef",
            slug="prf_1",
            workflow_id="wor_0195f3a0000070008123456789abcdef",
            name=I18nText(translations={"en": "Profile"}),
            target_block_order=[TargetBlockType.METADATA_BLOCK],
        )
    )
    await repo.update_output_profile(
        "1",
        OutputProfile(
            id="prf_0195f3a0000070008123456789abcdef",
            slug="prf_1",
            workflow_id="wor_0195f3a0000070008123456789abcdef",
            name=I18nText(translations={"en": "Profile"}),
            target_block_order=[TargetBlockType.METADATA_BLOCK],
        ),
    )
    await repo.delete_output_profile("1")
    sample_brief = TaskBrief(
        id="tbr_0195f3a0000070008123456789abcdef",
        slug="tbr_1",
        label=I18nText(translations={"en": "Brief", "fi": "Ohje"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        instruction_text="Instructions",
    )
    await repo.get_all_task_briefs()
    mock_driver.get.return_value = None
    await repo.get_task_brief_by_id("1")
    await repo.create_task_brief(sample_brief)
    mock_driver.get.return_value = sample_brief.model_dump(mode="json")
    await repo.update_task_brief("1", sample_brief)
    await repo.delete_task_brief("1")


@pytest.mark.asyncio
async def test_system_repo_get_mcp_gateways_with_id() -> None:
    """Positive: get_mcp_gateways with specific ID executes O(1) primary-key lookup via driver.get."""
    mock_driver = AsyncMock()
    gateway_id = "sys_0195f3a0000070018234567890abcdef"
    mock_driver.get.return_value = {
        "id": gateway_id,
        "name": "Test MCP Gateway",
        "slug": "test_mcp_gateway",
        "type": "mcp_gateways",
        "tools": [],
    }

    repo = UnifiedWorkflowRepository(driver=mock_driver)
    res = await repo.get_mcp_gateways(id=gateway_id)

    assert res.id == gateway_id
    mock_driver.get.assert_called_once_with("system_config", gateway_id)
    mock_driver.query.assert_not_called()


@pytest.mark.asyncio
async def test_system_repo_get_mcp_gateways_not_found_raises() -> None:
    """Negative: get_mcp_gateways with specific ID raises ResourceNotFoundError when driver.get returns None."""
    mock_driver = AsyncMock()
    mock_driver.get.return_value = None

    repo = UnifiedWorkflowRepository(driver=mock_driver)
    with pytest.raises(ResourceNotFoundError) as exc_info:
        await repo.get_mcp_gateways(id="sys_nonexistent")

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["resource_id"] == "sys_nonexistent"
    mock_driver.get.assert_called_once_with("system_config", "sys_nonexistent")
    mock_driver.query.assert_not_called()


@pytest.mark.asyncio
async def test_system_repo_get_mcp_gateways_default_not_found_raises() -> None:
    """Negative: get_mcp_gateways without ID raises ResourceNotFoundError when type query returns empty list."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = []

    repo = UnifiedWorkflowRepository(driver=mock_driver)
    with pytest.raises(ResourceNotFoundError) as exc_info:
        await repo.get_mcp_gateways()

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["resource_id"] == "mcp_gateways"
    mock_driver.query.assert_called_once()
    mock_driver.get.assert_not_called()


def test_append_only_repository_increment_version() -> None:
    """Positive: tests version incrementing on AppendOnlyRepositoryBase."""
    repo = AppendOnlyRepositoryBase(AsyncMock())
    res = repo._increment_version("wf_exec")
    assert res.base_id == "wf_exec"
    assert res.new_id == "wf_exec_v2"
    assert res.version == 2

    res2 = repo._increment_version("wf_exec_v2")
    assert res2.base_id == "wf_exec"
    assert res2.new_id == "wf_exec_v3"
    assert res2.version == 3

    res3 = repo._increment_version("wf_exec_v_invalid")
    assert res3.base_id == "wf_exec"
    assert res3.new_id == "wf_exec_v2"
    assert res3.version == 2
