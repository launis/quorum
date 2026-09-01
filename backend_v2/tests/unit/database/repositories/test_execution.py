"""Unit tests for ExecutionRepositoryImpl."""

import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.execution import ExecutionRepositoryImpl
from backend_v2.exceptions import AppException
from backend_v2.models.dtos.trace import ExecutionCreateDTO, ExecutionUpdateDTO
from backend_v2.models.state import TraceEvent
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
async def test_repository_reconstitutes_typed_domain_models(
    repo: ExecutionRepositoryImpl, mock_driver: AsyncMock, valid_execution_doc: dict
) -> None:
    """Contract: Raw database record dictionary from driver reconstitutes into strict frozen Pydantic Domain model."""
    from backend_v2.models.v2_core import ExecutionRecord

    mock_driver.get.return_value = valid_execution_doc
    record = await repo.get_execution("exe_1234567890abcdef")
    assert record is not None
    assert isinstance(record, ExecutionRecord)
    assert record.id == "exe_1234567890abcdef"


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
    # 1. Valid executions return list
    mock_driver.query.return_value = [valid_execution_doc]

    all_execs = await repo.get_all_executions(organization_id="org_123", user_id="usr_123")
    assert len(all_execs) == 1
    assert all_execs[0].id == "exe_1234567890abcdef"

    recent = await repo.get_recent_completed_executions(limit=5)
    assert len(recent) == 1

    # 2. Corrupted execution in query fails fast with AppException (Fail-Fast Rule)
    mock_driver.query.return_value = [{"id": "corrupted_1"}]
    with pytest.raises(AppException) as exc_info:
        await repo.get_all_executions()
    assert exc_info.value.status_code == 500

    with pytest.raises(AppException) as exc_info_recent:
        await repo.get_recent_completed_executions()
    assert exc_info_recent.value.status_code == 500


@pytest.mark.asyncio
async def test_crud_and_query_operations(repo: ExecutionRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: tests create, update, append_trace_event, delete, and count operations."""
    create_dto = ExecutionCreateDTO(
        id="exe_1234567890abcdef",
        workflow_id="wf_1234567890abcdef",
        target_locale="fi",
        active_profile_id="prof_1",
        organization_id="org_1",
        created_by="usr_1",
    )
    assert await repo.create_execution(create_dto) == "exec_1234567890abcdef"
    assert await repo.update_execution("exe_1234567890abcdef", ExecutionUpdateDTO(status="RUNNING")) is True
    mock_driver.get.return_value = {"id": "exe_1234567890abcdef"}
    event = TraceEvent(step_name="stp_1", event_type="output", content={"type": "log"})
    assert await repo.append_trace_event("exe_1234567890abcdef", event) is True
    assert await repo.delete_execution("exe_1234567890abcdef") is True

    count = await repo.count_executions_by_matrix("mat_1234567890abcdef")
    assert count == 3


@pytest.mark.asyncio
async def test_offload_and_hydrate_payloads(repo: ExecutionRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: tests payload offloading for large traces and hydration via storage driver."""
    mock_storage = AsyncMock(spec=FileDriver)
    mock_storage.save.return_value = True
    mock_storage.read.return_value = json.dumps(
        [
            {
                "step_name": "stp_1",
                "event_type": "output",
                "content": {"result": "ok"},
            }
        ]
    )

    with patch("backend_v2.database.repositories.execution.get_storage_driver", return_value=mock_storage):
        # 1. Test offload
        big_trace = [{"i": i, "content": "x" * 200} for i in range(600)]
        data = {
            "id": "exe_big",
            "execution_trace": big_trace,
            "frozen_context": {
                "mcp_tool_audit": [
                    {
                        "id": "audit_1",
                        "tool_id": "calc",
                        "step_name": "stp_1",
                        "query": "2+2",
                        "reasoning": "math",
                    }
                ]
            },
        }
        await repo._offload_payloads("exe_big", data)
        assert "execution_trace_storage_path" in data
        assert "execution_trace" not in data
        mock_storage.save.assert_called_once()

        # 2. Test hydrate
        await repo._hydrate_payloads(data)
        assert "execution_trace" in data

        # 3. Test empty payload handling for pending/running status
        pending_data = {
            "id": "exe_pending",
            "status": "RUNNING",
            "execution_trace_storage_path": "executions/exe_pending/trace.json",
        }
        mock_storage.read.return_value = ""
        await repo._hydrate_payloads(pending_data)
        assert pending_data["execution_trace"] == []

        # 4. Test error when blob data is corrupted / unparseable
        mock_storage.read.side_effect = Exception("Storage error")
        with pytest.raises(AppException) as exc_info:
            await repo._hydrate_payloads(
                {"id": "exe_err", "execution_trace_storage_path": "executions/exe_err/trace.json"}
            )
        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_audit_trails_offload_and_hydrate(repo: ExecutionRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive & Negative: tests subcollection audit trails offloading and hydration."""
    # Test offload audit trails
    data = {
        "id": "exe_audit",
        "frozen_context": {
            "mcp_tool_audit": [
                {
                    "id": "audit_1",
                    "tool_id": "fetch",
                    "step_name": "stp_1",
                    "query": "q1",
                    "reasoning": "r1",
                    "timestamp": "2026-08-31T01:00:00Z",
                },
                {
                    "id": "audit_custom",
                    "tool_id": "calc",
                    "step_name": "stp_2",
                    "query": "q2",
                    "reasoning": "r2",
                    "timestamp": "2026-08-31T00:00:00Z",
                },
            ]
        },
    }
    await repo._offload_payloads("exe_audit", data)
    assert mock_driver.upsert.call_count >= 2

    # Test audit trails failure on offload
    data_fail = {
        "id": "exe_audit_fail",
        "frozen_context": {
            "mcp_tool_audit": [
                {
                    "id": "audit_err",
                    "tool_id": "fetch",
                    "step_name": "stp_err",
                    "query": "q_err",
                    "reasoning": "r_err",
                    "timestamp": "2026-08-31T01:00:00Z",
                },
            ]
        },
    }
    mock_driver.upsert.side_effect = Exception("DB error")
    with pytest.raises(AppException) as exc_info:
        await repo._offload_payloads("exe_audit_fail", data_fail)
    assert exc_info.value.status_code == 500
    mock_driver.upsert.side_effect = None

    # Test hydrate audit trails
    mock_driver.query.return_value = [
        {
            "id": "a2",
            "tool_id": "fetch",
            "step_name": "stp_2",
            "query": "q2",
            "reasoning": "r2",
            "timestamp": datetime(2026, 8, 31, 1, 0, 0, tzinfo=timezone.utc),
        },
        {
            "id": "a1",
            "tool_id": "calc",
            "step_name": "stp_1",
            "query": "q1",
            "reasoning": "r1",
            "timestamp": datetime(2026, 8, 31, 0, 0, 0, tzinfo=timezone.utc),
        },
    ]
    hydrate_data = {"id": "exe_audit"}
    await repo._hydrate_payloads(hydrate_data)
    assert "frozen_context" in hydrate_data
    assert len(hydrate_data["frozen_context"].mcp_tool_audit) == 2
    # Check sorting
    assert hydrate_data["frozen_context"].mcp_tool_audit[0].id == "a1"

    # Test hydrate audit trails failure
    mock_driver.query.side_effect = Exception("Query error")
    with pytest.raises(AppException):
        await repo._hydrate_payloads({"id": "exe_fail_audit"})


@pytest.mark.asyncio
async def test_hydrate_frozen_context_and_context_vars(repo: ExecutionRepositoryImpl) -> None:
    """Positive: tests hydration of frozen_context and context_variables blobs."""
    mock_storage = AsyncMock(spec=FileDriver)
    mock_storage.read.side_effect = [
        json.dumps(
            {
                "compiled_prompts": {"p1": "prompt"},
                "injected_theory": {},
                "generated_schemas": {},
                "ui_hints_snapshot": {},
                "mcp_tool_audit": [],
            }
        ),
        json.dumps({"var1": "val1"}),
    ]

    with patch("backend_v2.database.repositories.execution.get_storage_driver", return_value=mock_storage):
        data = {
            "frozen_context_storage_path": "executions/exe_1/frozen_context.json",
            "context_variables_storage_path": "executions/exe_1/context_vars.json",
        }
        await repo._hydrate_payloads(data)
        assert "frozen_context" in data
        assert "context_variables" in data


@pytest.mark.asyncio
async def test_append_trace_event_errors(repo: ExecutionRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Negative: tests append_trace_event when execution is missing or hydration fails."""
    event = TraceEvent(step_name="stp_1", event_type="output", content={"type": "log"})
    # 1. Missing execution
    mock_driver.get.return_value = None
    assert await repo.append_trace_event("exe_nonexistent", event) is False

    # 2. Hydration failure during append
    mock_driver.get.return_value = {
        "id": "exe_corrupt",
        "execution_trace_storage_path": "executions/exe_corrupt/trace.json",
    }
    mock_storage = AsyncMock(spec=FileDriver)
    mock_storage.read.side_effect = Exception("Read failure")
    with patch("backend_v2.database.repositories.execution.get_storage_driver", return_value=mock_storage):
        with pytest.raises(AppException):
            await repo.append_trace_event("exe_corrupt", event)
