from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.database.repositories.execution import ExecutionRepositoryImpl
from backend_v2.database.repositories.knowledge import KnowledgeRepositoryImpl
from backend_v2.exceptions import AppException, ErrorCodes


@pytest.mark.asyncio
async def test_hydrate_payloads_fails_fast_on_empty_blob() -> None:
    """Epic 32: Test that an empty storage blob triggers a Fail-Fast DATA_CORRUPTION error."""
    mock_driver = AsyncMock()
    # Mock read to return empty bytes
    mock_driver.read.return_value = b"   "

    repo = ExecutionRepositoryImpl(driver=mock_driver)

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

    repo = ExecutionRepositoryImpl(driver=mock_driver)
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
    repo = ExecutionRepositoryImpl(driver=mock_driver)

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

    repo = ExecutionRepositoryImpl(driver=mock_driver)
    data = {"id": "doc_123"}

    with patch("backend_v2.database.repositories.execution.get_storage_driver"):
        with pytest.raises(AppException) as exc_info:
            await repo._hydrate_payloads(data)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.DATA_CORRUPTION.value
    assert "Failed to hydrate audit_trails" in exc_info.value.message


@pytest.mark.asyncio
async def test_knowledge_base_delegates() -> None:
    mock_driver = AsyncMock()
    mock_driver.query.return_value = []
    mock_driver.upsert.return_value = "id_1"
    repo = KnowledgeRepositoryImpl(driver=mock_driver)

    assert await repo.get_concepts() == []
    assert await repo.get_references() == []
    assert await repo.get_claims() == []
    assert await repo.add_concept({"id": "id_1"}) == "id_1"
    assert await repo.add_reference({"id": "id_1"}) == "id_1"
    assert await repo.add_claim({"id": "id_1"}) == "id_1"
    await repo.clear_knowledge_base()
    assert mock_driver.clear.call_count == 3
