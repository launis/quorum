"""Unit tests for ExecutionRepositoryImpl."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.execution import ExecutionRepositoryImpl
from backend_v2.exceptions import AppException
from backend_v2.services.file_driver import FileDriver


@pytest.fixture
def mock_driver() -> AsyncMock:
    """Mock storage driver."""
    driver = AsyncMock(spec=StorageDriver)
    driver.query.return_value = []
    driver.get.return_value = None
    driver.upsert.return_value = "exec_1234567890abcdef"
    driver.update.return_value = True
    driver.delete.return_value = True
    driver.count.return_value = 3
    return driver


@pytest.fixture
def repo(mock_driver: AsyncMock) -> ExecutionRepositoryImpl:
    """Execution repository fixture."""
    return ExecutionRepositoryImpl(mock_driver)


@pytest.fixture
def valid_execution_doc() -> dict:
    """Valid execution document fixture."""
    return {
        "id": "exe_1234567890abcdef",
        "workflow_id": "wf_1234567890abcdef",
        "target_locale": "fi",
        "status": "PASSED",
        "metadata": {
            "target_locale": "fi",
            "organization_id": "org_1234567890abcdef",
            "user_id": "usr_1234567890abcdef",
        },
    }


@pytest.mark.asyncio
async def test_get_execution_status(repo: ExecutionRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: retrieves execution status."""
    mock_driver.get.return_value = {"id": "exe_1234567890abcdef", "status": "PASSED"}
    status = await repo.get_execution_status("exe_1234567890abcdef")
    assert status == "PASSED"


@pytest.mark.asyncio
async def test_get_execution_success(
    repo: ExecutionRepositoryImpl, mock_driver: AsyncMock, valid_execution_doc: dict
) -> None:
    """Positive: retrieves and hydrates valid ExecutionRecord."""
    mock_driver.get.return_value = valid_execution_doc
    record = await repo.get_execution("exe_1234567890abcdef")
    assert record is not None
    assert record.id == "exe_1234567890abcdef"
    assert record.status == "PASSED"


@pytest.mark.asyncio
async def test_get_execution_not_found(repo: ExecutionRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: returns None if execution is not found."""
    mock_driver.get.return_value = None
    assert await repo.get_execution("exe_missing") is None


@pytest.mark.asyncio
async def test_get_execution_data_corruption(repo: ExecutionRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Negative: corrupted execution data raises AppException with DATA_CORRUPTION."""
    mock_driver.get.return_value = {"id": "invalid_id", "status": "INVALID_STATUS"}
    with pytest.raises(AppException) as exc_info:
        await repo.get_execution("invalid_id")
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_get_all_executions_and_recent(
    repo: ExecutionRepositoryImpl, mock_driver: AsyncMock, valid_execution_doc: dict
) -> None:
    """Positive: tests get_all_executions with filters and get_recent_completed_executions."""
    mock_driver.query.return_value = [{"id": "corrupted_1"}, valid_execution_doc]

    all_execs = await repo.get_all_executions(organization_id="org_123", user_id="usr_123")
    assert len(all_execs) == 1
    assert all_execs[0].id == "exe_1234567890abcdef"

    recent = await repo.get_recent_completed_executions(limit=5)
    assert len(recent) == 1


@pytest.mark.asyncio
async def test_crud_and_query_operations(repo: ExecutionRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: tests create, update, append_trace_event, delete, and count operations."""
    assert await repo.create_execution({"id": "exe_1234567890abcdef"}) == "exec_1234567890abcdef"
    assert await repo.update_execution("exe_1234567890abcdef", {"status": "RUNNING"}) is True
    mock_driver.get.return_value = {"id": "exe_1234567890abcdef"}
    assert await repo.append_trace_event("exe_1234567890abcdef", {"type": "log"}) is True
    assert await repo.delete_execution("exe_1234567890abcdef") is True

    count = await repo.count_executions_by_matrix("mat_1234567890abcdef")
    assert count == 3


@pytest.mark.asyncio
async def test_offload_and_hydrate_payloads(repo: ExecutionRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: tests payload offloading for large traces and hydration via storage driver."""
    mock_storage = AsyncMock(spec=FileDriver)
    mock_storage.save.return_value = True
    mock_storage.read.return_value = json.dumps(
        [{"step_id": "stp_1", "block_id": "blk_1", "data_type": "text", "payload": "ok"}]
    )

    with patch("backend_v2.database.repositories.execution.get_storage_driver", return_value=mock_storage):
        # 1. Test offload
        big_trace = [{"i": i, "content": "x" * 200} for i in range(600)]
        data = {
            "id": "exe_big",
            "execution_trace": big_trace,
            "frozen_context": {"mcp_tool_audit": [{"id": "audit_1", "tool": "calc"}]},
        }
        await repo._offload_payloads("exe_big", data)
        assert "execution_trace_storage_path" in data
        assert "execution_trace" not in data
        mock_storage.save.assert_called_once()

        # 2. Test hydrate
        await repo._hydrate_payloads(data)
        assert "execution_trace" in data
