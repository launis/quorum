from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.database.repository import UnifiedWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes


@pytest.mark.asyncio
async def test_hydrate_payloads_fails_fast_on_empty_blob() -> None:
    """Epic 32: Test that an empty storage blob triggers a Fail-Fast DATA_CORRUPTION error."""
    mock_driver = AsyncMock()
    # Mock read to return empty bytes
    mock_driver.read.return_value = b"   "

    repo = UnifiedWorkflowRepository(driver=mock_driver)

    with patch("backend_v2.database.repository.get_storage_driver", return_value=mock_driver):
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

    with patch("backend_v2.database.repository.get_storage_driver", return_value=mock_storage_driver):
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

    with patch("backend_v2.database.repository.get_storage_driver"):
        with pytest.raises(AppException) as exc_info:
            await repo._hydrate_payloads(data)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.DATA_CORRUPTION.value
    assert "Failed to hydrate audit_trails" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_all_delegates_to_driver() -> None:
    """Test that get_all delegates to driver.query."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = [{"id": "123"}]
    repo = UnifiedWorkflowRepository(driver=mock_driver)
    
    result = await repo.get_all("workflows")
    
    mock_driver.query.assert_called_once_with("workflows")
    assert result == [{"id": "123"}]


@pytest.mark.asyncio
async def test_get_delegates_to_driver() -> None:
    """Test that get delegates to driver.get."""
    mock_driver = AsyncMock()
    mock_driver.get.return_value = {"id": "123"}
    repo = UnifiedWorkflowRepository(driver=mock_driver)
    
    result = await repo.get("workflows", "123")
    
    mock_driver.get.assert_called_once_with("workflows", "123")
    assert result == {"id": "123"}


@pytest.mark.asyncio
async def test_create_raw_delegates_to_driver() -> None:
    """Test that create_raw generates UUID if missing and delegates to driver.upsert."""
    mock_driver = AsyncMock()
    mock_driver.upsert.return_value = "new_123"
    repo = UnifiedWorkflowRepository(driver=mock_driver)
    
    # Without ID
    result = await repo.create_raw("workflows", {"name": "Test"})
    assert mock_driver.upsert.call_count == 1
    args, _ = mock_driver.upsert.call_args
    assert args[0] == "workflows"
    assert "id" in args[1]
    assert result == "new_123"
    
    # With ID
    mock_driver.upsert.reset_mock()
    result = await repo.create_raw("workflows", {"id": "existing_id", "name": "Test"})
    mock_driver.upsert.assert_called_once_with("workflows", {"id": "existing_id", "name": "Test"}, "existing_id")


@pytest.mark.asyncio
async def test_delete_delegates_to_driver() -> None:
    """Test that delete delegates to driver.delete."""
    mock_driver = AsyncMock()
    mock_driver.delete.return_value = True
    repo = UnifiedWorkflowRepository(driver=mock_driver)
    
    result = await repo.delete("workflows", "123")
    
    mock_driver.delete.assert_called_once_with("workflows", "123")
    assert result is True


@pytest.mark.asyncio
async def test_agent_delegates() -> None:
    mock_driver = AsyncMock()
    mock_driver.get.return_value = {"id": "agent_1"}
    mock_driver.query.return_value = [{"id": "agent_1"}]
    mock_driver.upsert.return_value = "agent_1"
    mock_driver.update.return_value = True
    mock_driver.delete.return_value = True
    repo = UnifiedWorkflowRepository(driver=mock_driver)

    assert await repo.get_agent_by_id("agent_1") == {"id": "agent_1"}
    assert await repo.get_all_agents() == [{"id": "agent_1"}]
    assert await repo.create_agent({"id": "agent_1"}) == "agent_1"
    assert await repo.update_agent("agent_1", {}) is True
    assert await repo.delete_agent("agent_1") is True


@pytest.mark.asyncio
async def test_output_profile_delegates() -> None:
    mock_driver = AsyncMock()
    mock_driver.get.return_value = {"id": "profile_1"}
    mock_driver.query.return_value = [{"id": "profile_1"}]
    mock_driver.upsert.return_value = "profile_1"
    mock_driver.update.return_value = True
    mock_driver.delete.return_value = True
    repo = UnifiedWorkflowRepository(driver=mock_driver)

    assert await repo.get_all_output_profiles() == [{"id": "profile_1"}]
    assert await repo.get_output_profile_by_id("profile_1") == {"id": "profile_1"}
    assert await repo.create_output_profile({"id": "profile_1"}) == "profile_1"
    assert await repo.update_output_profile("profile_1", {}) is True
    assert await repo.delete_output_profile("profile_1") is True


@pytest.mark.asyncio
async def test_knowledge_base_delegates() -> None:
    mock_driver = AsyncMock()
    mock_driver.query.return_value = []
    mock_driver.upsert.return_value = "id_1"
    repo = UnifiedWorkflowRepository(driver=mock_driver)

    assert await repo.get_concepts() == []
    assert await repo.get_references() == []
    assert await repo.get_claims() == []
    assert await repo.add_concept({"id": "id_1"}) == "id_1"
    assert await repo.add_reference({"id": "id_1"}) == "id_1"
    assert await repo.add_claim({"id": "id_1"}) == "id_1"
    await repo.clear_knowledge_base()
    assert mock_driver.clear.call_count == 3


@pytest.mark.asyncio
async def test_banned_phrases_delegates() -> None:
    mock_driver = AsyncMock()
    mock_driver.query.return_value = []
    repo = UnifiedWorkflowRepository(driver=mock_driver)

    assert await repo.get_banned_phrases() == []
    await repo.add_banned_phrase("bad")
    mock_driver.upsert.assert_called_once()
    
    mock_driver.query.return_value = [{"id": "123"}]
    assert await repo.delete_banned_phrase("bad") is mock_driver.delete.return_value


