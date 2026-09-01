from unittest.mock import AsyncMock, patch

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
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.base import AuditLogCreateDTO
from backend_v2.models.domain.knowledge import (
    ClaimCreateDTO,
    ConceptCreateDTO,
    ReferenceCreateDTO,
)
from backend_v2.models.domain.prompt_blocks import PersonaPromptBlock
from backend_v2.models.dtos.studio import (
    StepCreateDTO,
    StepUpdateDTO,
    WorkflowCreateDTO,
    WorkflowUpdateDTO,
)
from backend_v2.models.dtos.system import SystemConfigMCPGateways, SystemConfigModelRegistry
from backend_v2.models.dtos.trace import ExecutionCreateDTO, ExecutionUpdateDTO
from backend_v2.models.enums import BlockDataType, ExecutionStatus, PromptBlockCategory, TargetBlockType
from backend_v2.models.v2_core import OutputProfile


@pytest.mark.asyncio
async def test_hydrate_payloads_fails_fast_on_empty_blob() -> None:
    """Epic 32: Test that an empty storage blob triggers a Fail-Fast DATA_CORRUPTION error."""
    mock_driver = AsyncMock()
    mock_driver.read.return_value = b"   "

    repo = UnifiedWorkflowRepository(driver=mock_driver)

    with patch("backend_v2.database.repositories.execution.get_storage_driver", return_value=mock_driver):
        data = {"id": "exe_123", "execution_trace_storage_path": "executions/exe_123/execution_trace.json"}

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
    data = {
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

    data = {
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
    data = {"id": "doc_123"}

    with patch("backend_v2.database.repositories.execution.get_storage_driver"):
        with pytest.raises(AppException) as exc_info:
            await repo._hydrate_payloads(data)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.DATA_CORRUPTION.value
    assert "Failed to hydrate audit_trails" in exc_info.value.message


@pytest.mark.asyncio
async def test_workflow_fetching() -> None:
    mock_driver = AsyncMock()
    mock_driver.get.return_value = {"id": "test_wf"}
    pass


@pytest.mark.asyncio
async def test_all_passthrough_methods() -> None:
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
        ExecutionCreateDTO(id="exe_0123456789abcdef", workflow_id="wor_0123456789abcdef", raw_inputs=None)
    )
    await repo.update_execution("exe_0123456789abcdef", ExecutionUpdateDTO(status=ExecutionStatus.PASSED))
    await repo.delete_execution("1")
    await repo.get_all_executions()
    await repo.get_recent_completed_executions()
    await repo.log_audit_event(
        AuditLogCreateDTO(
            organization_id="org_1234abcd",
            actor_id="usr_1234abcd",
            action="test",
            details={"resource_type": "workflow", "resource_id": "wor_1234"},
        )
    )
    await repo.get_audit_logs()
    await repo.get_all_workflows()
    await repo.get_workflow_by_id("1")
    await repo.create_workflow(WorkflowCreateDTO(slug="wf_slug", name="WF"))
    mock_driver.get.return_value = {"id": "1", "version": 1, "slug": "s"}
    await repo.update_workflow("1", WorkflowUpdateDTO(name="WF New"))
    await repo.update_workflow_definition("1", WorkflowUpdateDTO(name="WF New"))
    await repo.delete_workflow("1")
    await repo.get_all_steps()
    mock_driver.get.return_value = None
    await repo.get_step_by_id("1")
    await repo.create_step(StepCreateDTO(slug="step_slug", name=I18nText(translations={"en": "Step"})))
    mock_driver.get.return_value = {"id": "1", "version": 1, "slug": "s"}
    await repo.update_step("1", StepUpdateDTO(name=I18nText(translations={"en": "Step"})))
    await repo.delete_step("1", force_delete=True)
    await repo.get_all_components()
    mock_driver.get.return_value = None
    await repo.get_component_by_id("1")
    persona_block = PersonaPromptBlock(
        id="blk_0123456789abcdef",
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
    mock_driver.query.return_value = [{"id": "sys_1234567890abcdef", "type": "model_registry", "models": {}}]
    await repo.get_model_registry()
    await repo.update_model_registry(
        SystemConfigModelRegistry(id="sys_1234567890abcdef", type="model_registry", models={})
    )
    mock_driver.query.return_value = [{"id": "sys_1234567890abcdef", "type": "mcp_gateways", "tools": []}]
    await repo.get_mcp_gateways()
    await repo.update_mcp_gateways(SystemConfigMCPGateways(id="sys_1234567890abcdef", type="mcp_gateways", tools=[]))
    mock_driver.query.return_value = []
    await repo.count_executions_by_matrix("1")
    await repo.get_matrices_using_dimension("1")
    await repo.list_organizations()
    mock_driver.get.return_value = None
    await repo.get_organization("1")
    await repo.create_organization(
        Organization(
            id="org_0123456789abcdef",
            name="Org",
            tier="enterprise",
            is_active=True,
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=500.0,
            tpm_limit=50000,
            rpm_limit=500,
        )
    )
    await repo.update_organization("1", OrganizationUpdateDTO(name="Org New"))
    await repo.delete_organization("1")
    await repo.list_users()
    await repo.get_user("1")
    await repo.get_user_by_email("email")
    await repo.create_user(
        User(
            id="usr_0123456789abcdef",
            email="test@test.com",
            role=UserRole.MEMBER,
            is_active=True,
            language="en",
            theme_mode="system",
            created_at="2026-01-01T00:00:00Z",
            organization_id="org_0123456789abcdef",
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
            id="prf_0123456789abcdef",
            slug="prf_1",
            workflow_id="wor_0123456789abcdef",
            name=I18nText(translations={"en": "Profile"}),
            target_block_order=[TargetBlockType.METADATA_BLOCK],
        )
    )
    await repo.update_output_profile(
        "1",
        OutputProfile(
            id="prf_0123456789abcdef",
            slug="prf_1",
            workflow_id="wor_0123456789abcdef",
            name=I18nText(translations={"en": "Profile"}),
            target_block_order=[TargetBlockType.METADATA_BLOCK],
        ),
    )
    await repo.delete_output_profile("1")


@pytest.mark.asyncio
async def test_system_repo_get_mcp_gateways_with_id() -> None:
    """Positive: get_mcp_gateways with specific ID filters by id."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = [{"id": "sys_1234567890abcdef", "type": "mcp_gateways", "tools": []}]

    repo = UnifiedWorkflowRepository(driver=mock_driver)
    res = await repo.get_mcp_gateways(id="sys_1234567890abcdef")

    assert res.id == "sys_1234567890abcdef"
    mock_driver.query.assert_called_once()
    filters = mock_driver.query.call_args[0][1]
    assert len(filters) == 1
    assert filters[0].field == "id"
    assert filters[0].value == "sys_1234567890abcdef"


@pytest.mark.asyncio
async def test_system_repo_get_mcp_gateways_not_found_raises() -> None:
    """Negative: get_mcp_gateways raises ResourceNotFoundError when config document is missing."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = []

    repo = UnifiedWorkflowRepository(driver=mock_driver)
    with pytest.raises(ResourceNotFoundError) as exc_info:
        await repo.get_mcp_gateways(id="sys_nonexistent")

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["resource_id"] == "sys_nonexistent"


def test_append_only_repository_increment_version() -> None:
    """Positive: tests version incrementing on AppendOnlyRepositoryBase."""
    from backend_v2.database.repositories.base import AppendOnlyRepositoryBase

    repo = AppendOnlyRepositoryBase(AsyncMock())
    base, new_id, ver = repo._increment_version("wf_exec")
    assert base == "wf_exec"
    assert new_id == "wf_exec_v2"
    assert ver == 2

    base2, new_id2, ver2 = repo._increment_version("wf_exec_v2")
    assert base2 == "wf_exec"
    assert new_id2 == "wf_exec_v3"
    assert ver2 == 3

    base3, new_id3, ver3 = repo._increment_version("wf_exec_v_invalid")
    assert base3 == "wf_exec"
    assert new_id3 == "wf_exec_v2"
    assert ver3 == 2
