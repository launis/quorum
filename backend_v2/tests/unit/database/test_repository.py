from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.database.repository import UnifiedWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError


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
    data = {"frozen_context": {"mcp_tool_audit": [{"id": "audit_123"}]}}

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
    await repo.create_execution({"id": "1"})
    await repo.update_execution("1", {"status": "ok"})
    await repo.delete_execution("1")
    await repo.get_all_executions()
    await repo.get_recent_completed_executions()
    await repo.log_audit_event({"data": "test"})
    await repo.get_audit_logs()
    await repo.get_all_workflows()
    await repo.get_workflow_by_id("1")
    await repo.create_workflow({"id": "1"})
    mock_driver.get.return_value = {"id": "1", "version": 1, "slug": "s"}
    await repo.update_workflow("1", {})
    await repo.update_workflow_definition("1", {})
    await repo.delete_workflow("1")
    await repo.get_all_steps()
    mock_driver.get.return_value = None
    await repo.get_step_by_id("1")
    await repo.create_step({"id": "1"})
    mock_driver.get.return_value = {"id": "1", "version": 1, "slug": "s"}
    await repo.update_step("1", {})
    await repo.delete_step("1", force_delete=True)
    await repo.get_all_components()
    mock_driver.get.return_value = None
    await repo.get_component_by_id("1")
    await repo.get_component_by_name("name")
    mock_driver.get.return_value = {"id": "1", "type": "agent"}
    await repo.update_component_metadata("1", "mod", "cls")
    await repo.register_component({"id": "1"})
    await repo.create_component({"id": "1"})
    mock_driver.get.return_value = None
    await repo.get_prompt_block_by_id("1")
    await repo.get_all_prompt_blocks()
    await repo.create_prompt_block({"id": "1"})
    mock_driver.get.return_value = {"id": "1", "version": 1, "slug": "s"}
    await repo.update_prompt_block("1", {})
    await repo.delete_prompt_block("1", force_delete=True)
    mock_driver.get.return_value = None
    await repo.get_agent_by_id("1")
    await repo.get_all_agents()
    await repo.create_agent({"id": "1"})
    mock_driver.get.return_value = {"id": "1", "version": 1, "slug": "s"}
    await repo.update_agent("1", {})
    await repo.delete_agent("1")
    mock_driver.get.return_value = None
    await repo.get_banned_phrases()
    await repo.add_banned_phrase("phrase")
    await repo.delete_banned_phrase("phrase")
    await repo.count_workflows()
    await repo.get_prompt_template("1")
    mock_driver.query.return_value = [{"id": "sys_1234567890abcdef", "type": "model_registry", "models": {}}]
    await repo.get_model_registry()
    await repo.update_model_registry({})
    mock_driver.query.return_value = [{"id": "sys_1234567890abcdef", "type": "mcp_gateways", "tools": []}]
    await repo.get_mcp_gateways()
    await repo.update_mcp_gateways({})
    mock_driver.query.return_value = []
    await repo.count_executions_by_matrix("1")
    await repo.get_matrices_using_dimension("1")
    await repo.list_organizations()
    mock_driver.get.return_value = None
    await repo.get_organization("1")
    await repo.create_organization({"id": "1"})
    await repo.update_organization("1", {})
    await repo.delete_organization("1")
    await repo.list_users()
    await repo.get_user("1")
    await repo.get_user_by_email("email")
    await repo.create_user({"id": "1"})
    await repo.update_user("1", {})
    await repo.delete_user("1")
    await repo.delete_org_data("1")
    await repo.get_org_usage_total("1")
    await repo.add_concept({"id": "1"})
    await repo.add_reference({"id": "1"})
    await repo.add_claim({"id": "1"})
    await repo.get_all_output_profiles()
    await repo.get_output_profile_by_id("1")
    await repo.create_output_profile({"id": "1"})
    await repo.update_output_profile("1", {})
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
