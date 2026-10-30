"""Unit tests for ExecutionRepositoryImpl."""

import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.execution import ExecutionRepositoryImpl
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.execution import ExecutionRecord, FrozenContext
from backend_v2.models.dtos.trace import ExecutionCreateDTO, ExecutionUpdateDTO
from backend_v2.models.enums import ExecutionStatus, SystemLocale
from backend_v2.models.state import TraceEvent
from backend_v2.services.file_driver import FileDriver

_EXE_ID = "exe_0195f3a0000070018234567890abcdef"
_EXE_ID_2 = "exe_0195f3a0000070028234567890abcdef"
_WF_ID = "wf_0195f3a0000070018234567890abcdef"
_PRF_ID = "prf_0195f3a0000070018234567890abcdef"
_ORG_ID = "org_0195f3a0000070018234567890abcdef"
_USR_ID = "usr_0195f3a0000070018234567890abcdef"
_STP_ID = "stp_0195f3a0000070018234567890abcdef"
_STP_ID_2 = "stp_0195f3a0000070028234567890abcdef"
_BLK_ID = "blk_0195f3a0000070018234567890abcdef"
_TRC_ID_1 = "trc_0195f3a0000070018234567890abcdef"
_TRC_ID_2 = "trc_0195f3a0000070028234567890abcdef"


@pytest.fixture
def mock_driver() -> AsyncMock:
    """Mock storage driver."""
    driver = AsyncMock(spec=StorageDriver)
    driver.query.return_value = []
    driver.get.return_value = None
    driver.upsert.return_value = _EXE_ID
    driver.update.return_value = True
    driver.delete.return_value = True
    driver.count.return_value = 3
    return driver


@pytest.fixture
def repo(mock_driver: AsyncMock) -> ExecutionRepositoryImpl:
    """Execution repository fixture."""
    return ExecutionRepositoryImpl(mock_driver)


@pytest.fixture
def valid_execution_doc() -> ExecutionRecord:
    """Valid execution record fixture."""
    return ExecutionRecord(
        id=_EXE_ID,
        workflow_id=_WF_ID,
        output_profile_id=_PRF_ID,
        target_locale=SystemLocale.FI,
        status=ExecutionStatus.PASSED,
    )


@pytest.mark.asyncio
async def test_get_execution_status(repo: ExecutionRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive & Negative: retrieves execution status when present and returns None when missing."""
    mock_driver.get.return_value = {"id": _EXE_ID, "status": "PASSED"}
    status = await repo.get_execution_status(_EXE_ID)
    assert status == "PASSED"

    mock_driver.get.return_value = None
    assert await repo.get_execution_status(_EXE_ID_2) is None


@pytest.mark.asyncio
async def test_get_execution_success(
    repo: ExecutionRepositoryImpl, mock_driver: AsyncMock, valid_execution_doc: ExecutionRecord
) -> None:
    """Positive: retrieves and hydrates valid ExecutionRecord."""
    mock_driver.get.return_value = valid_execution_doc.model_dump(mode="json")
    record = await repo.get_execution(_EXE_ID)
    assert record is not None
    assert record.id == _EXE_ID
    assert record.status == "PASSED"


@pytest.mark.asyncio
async def test_repository_reconstitutes_typed_domain_models(
    repo: ExecutionRepositoryImpl, mock_driver: AsyncMock, valid_execution_doc: ExecutionRecord
) -> None:
    """Contract: Raw database record dictionary from driver reconstitutes into strict frozen Pydantic Domain model."""
    mock_driver.get.return_value = valid_execution_doc.model_dump(mode="json")
    record = await repo.get_execution(_EXE_ID)
    assert record is not None
    assert isinstance(record, ExecutionRecord)
    assert record.id == _EXE_ID


@pytest.mark.asyncio
async def test_get_execution_not_found(repo: ExecutionRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: returns None if execution is not found."""
    mock_driver.get.return_value = None
    assert await repo.get_execution(_EXE_ID_2) is None


@pytest.mark.asyncio
async def test_get_execution_data_corruption(repo: ExecutionRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Negative: corrupted execution data raises AppException with DATA_CORRUPTION."""
    mock_driver.get.return_value = {"id": _EXE_ID, "status": "INVALID_STATUS"}
    with pytest.raises(AppException) as exc_info:
        await repo.get_execution(_EXE_ID)
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.DATA_CORRUPTION.value


@pytest.mark.asyncio
async def test_get_all_executions_and_recent(
    repo: ExecutionRepositoryImpl, mock_driver: AsyncMock, valid_execution_doc: ExecutionRecord
) -> None:
    """Positive & Negative: tests get_all_executions with filters and get_recent_completed_executions."""
    # 1. Valid executions return list
    mock_driver.query.return_value = [valid_execution_doc.model_dump(mode="json")]

    all_execs = await repo.get_all_executions(organization_id=_ORG_ID, user_id=_USR_ID)
    assert len(all_execs) == 1
    assert all_execs[0].id == _EXE_ID

    recent = await repo.get_recent_completed_executions(limit=5)
    assert len(recent) == 1

    # 2. Corrupted execution in query fails fast with AppException (Fail-Fast Rule)
    mock_driver.query.return_value = [{"id": _EXE_ID_2}]
    with pytest.raises(AppException) as exc_info:
        await repo.get_all_executions()
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.DATA_CORRUPTION.value

    with pytest.raises(AppException) as exc_info_recent:
        await repo.get_recent_completed_executions()
    assert exc_info_recent.value.status_code == 500
    assert exc_info_recent.value.details["error_code"] == ErrorCodes.DATA_CORRUPTION.value


@pytest.mark.asyncio
async def test_crud_and_query_operations(repo: ExecutionRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: tests create, update, append_trace_event, delete, and count operations."""
    create_dto = ExecutionCreateDTO(
        workflow_id=_WF_ID,
        output_profile_id=_PRF_ID,
        target_locale="fi",
        active_profile_id=_PRF_ID,
        organization_id=_ORG_ID,
        created_by=_USR_ID,
    )
    assert await repo.create_execution(create_dto) == _EXE_ID
    assert await repo.update_execution(_EXE_ID, ExecutionUpdateDTO(status="RUNNING")) is True
    mock_driver.get.return_value = {"id": _EXE_ID, "execution_trace": []}
    event = TraceEvent(step_name=_STP_ID, event_type="output", content={"type": "log"})
    assert await repo.append_trace_event(_EXE_ID, event) is True
    assert await repo.delete_execution(_EXE_ID) is True

    count = await repo.count_executions_by_matrix(_BLK_ID)
    assert count == 3


@pytest.mark.asyncio
async def test_offload_and_hydrate_payloads(repo: ExecutionRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive & Negative: tests payload offloading for large traces and hydration via storage driver."""
    await repo._hydrate_payloads(None)

    mock_storage = AsyncMock(spec=FileDriver)
    mock_storage.save.return_value = True
    mock_storage.read.return_value = json.dumps(
        [
            {
                "step_name": _STP_ID,
                "event_type": "output",
                "content": {"result": "ok"},
            }
        ]
    )

    with patch("backend_v2.database.repositories.execution.get_storage_driver", return_value=mock_storage):
        # 1. Test offload
        big_trace = [{"i": i, "content": "x" * 200} for i in range(600)]
        data = {
            "id": _EXE_ID,
            "execution_trace": big_trace,
            "frozen_context": {
                "mcp_tool_audit": [
                    {
                        "id": _TRC_ID_1,
                        "tool_id": "calc",
                        "step_name": _STP_ID,
                        "query": "2+2",
                        "reasoning": "math",
                    }
                ]
            },
        }
        await repo._offload_payloads(_EXE_ID, data)
        assert "execution_trace_storage_path" in data
        assert "execution_trace" not in data
        mock_storage.save.assert_called_once()

        # 2. Test hydrate
        await repo._hydrate_payloads(data)
        assert "execution_trace" in data

        # 3. Test empty payload handling for pending/running status
        pending_data = {
            "id": _EXE_ID,
            "status": "RUNNING",
            "execution_trace_storage_path": f"executions/{_EXE_ID}/trace.json",
        }
        mock_storage.read.return_value = ""
        await repo._hydrate_payloads(pending_data)
        assert pending_data["execution_trace"] == []

        # 4. Test empty payload on completed execution raises AppException (DATA_CORRUPTION)
        completed_empty_data = {
            "id": _EXE_ID,
            "status": "PASSED",
            "execution_trace_storage_path": f"executions/{_EXE_ID}/trace.json",
        }
        with pytest.raises(AppException) as exc_empty:
            await repo._hydrate_payloads(completed_empty_data)
        assert exc_empty.value.status_code == 500
        assert exc_empty.value.details["error_code"] == ErrorCodes.DATA_CORRUPTION.value

        # 5. Test error when blob data is corrupted / unparseable
        mock_storage.read.side_effect = Exception("Storage error")
        with pytest.raises(AppException) as exc_info:
            await repo._hydrate_payloads(
                {"id": _EXE_ID_2, "execution_trace_storage_path": f"executions/{_EXE_ID_2}/trace.json"}
            )
        assert exc_info.value.status_code == 500
        assert exc_info.value.details["error_code"] == ErrorCodes.DATA_CORRUPTION.value

        # 6. Test error when blob save fails during offload
        mock_storage.save.side_effect = Exception("Disk full")
        with pytest.raises(AppException) as exc_save:
            await repo._offload_payloads(_EXE_ID, {"id": _EXE_ID, "execution_trace": big_trace})
        assert exc_save.value.status_code == 500
        assert exc_save.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR.value


@pytest.mark.asyncio
async def test_offload_invalid_frozen_context_raises_validation_failed(repo: ExecutionRepositoryImpl) -> None:
    """Negative: invalid FrozenContext payload during offload raises AppException (VALIDATION_FAILED)."""
    invalid_data = {
        "id": _EXE_ID,
        "frozen_context": {"unexpected_invalid_key": "value"},
    }
    with pytest.raises(AppException) as exc_info:
        await repo._offload_payloads(_EXE_ID, invalid_data)
    assert exc_info.value.status_code == 422
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_audit_trails_offload_and_hydrate(repo: ExecutionRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive & Negative: tests subcollection audit trails offloading and hydration."""
    # Test offload audit trails
    data = {
        "id": _EXE_ID,
        "frozen_context": {
            "mcp_tool_audit": [
                {
                    "id": _TRC_ID_1,
                    "tool_id": "fetch",
                    "step_name": _STP_ID,
                    "query": "q1",
                    "reasoning": "r1",
                    "timestamp": "2026-08-31T01:00:00Z",
                },
                {
                    "id": _TRC_ID_2,
                    "tool_id": "calc",
                    "step_name": _STP_ID_2,
                    "query": "q2",
                    "reasoning": "r2",
                    "timestamp": "2026-08-31T00:00:00Z",
                },
            ]
        },
    }
    await repo._offload_payloads(_EXE_ID, data)
    assert mock_driver.upsert.call_count >= 2

    # Test audit trails failure on offload
    data_fail = {
        "id": _EXE_ID_2,
        "frozen_context": {
            "mcp_tool_audit": [
                {
                    "id": _TRC_ID_1,
                    "tool_id": "fetch",
                    "step_name": _STP_ID,
                    "query": "q_err",
                    "reasoning": "r_err",
                    "timestamp": "2026-08-31T01:00:00Z",
                },
            ]
        },
    }
    mock_driver.upsert.side_effect = Exception("DB error")
    with pytest.raises(AppException) as exc_info:
        await repo._offload_payloads(_EXE_ID_2, data_fail)
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR.value
    mock_driver.upsert.side_effect = None

    # Test hydrate audit trails (including existing FrozenContext merge and missing timestamp key)
    mock_driver.query.return_value = [
        {
            "id": _TRC_ID_2,
            "tool_id": "fetch",
            "step_name": _STP_ID_2,
            "query": "q2",
            "reasoning": "r2",
            "timestamp": datetime(2026, 8, 31, 1, 0, 0, tzinfo=timezone.utc),
        },
        {
            "id": _TRC_ID_1,
            "tool_id": "calc",
            "step_name": _STP_ID,
            "query": "q1",
            "reasoning": "r1",
        },
    ]
    hydrate_data = {
        "id": _EXE_ID,
        "frozen_context": FrozenContext(compiled_prompts={"p1": "prompt"}),
    }
    await repo._hydrate_payloads(hydrate_data)
    assert isinstance(hydrate_data["frozen_context"], FrozenContext)
    assert len(hydrate_data["frozen_context"].mcp_tool_audit) == 2
    assert hydrate_data["frozen_context"].mcp_tool_audit[0].id == _TRC_ID_1
    assert hydrate_data["frozen_context"].compiled_prompts == {"p1": "prompt"}

    # Test hydrate audit trails failure
    mock_driver.query.side_effect = Exception("Query error")
    with pytest.raises(AppException) as exc_audit_err:
        await repo._hydrate_payloads({"id": _EXE_ID_2})
    assert exc_audit_err.value.status_code == 500
    assert exc_audit_err.value.details["error_code"] == ErrorCodes.DATA_CORRUPTION.value


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
        json.dumps({"variables": {"var1": "val1"}}),
    ]

    with patch("backend_v2.database.repositories.execution.get_storage_driver", return_value=mock_storage):
        data = {
            "frozen_context_storage_path": f"executions/{_EXE_ID}/frozen_context.json",
            "context_variables_storage_path": f"executions/{_EXE_ID}/context_vars.json",
        }
        await repo._hydrate_payloads(data)
        assert "frozen_context" in data
        assert "context_variables" in data


@pytest.mark.asyncio
async def test_append_trace_event_errors(repo: ExecutionRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Negative: tests append_trace_event when execution is missing or hydration fails."""
    event = TraceEvent(step_name=_STP_ID, event_type="output", content={"type": "log"})
    # 1. Missing execution
    mock_driver.get.return_value = None
    assert await repo.append_trace_event(_EXE_ID_2, event) is False

    # 2. Hydration failure during append
    mock_driver.get.return_value = {
        "id": _EXE_ID,
        "execution_trace_storage_path": f"executions/{_EXE_ID}/trace.json",
    }
    mock_storage = AsyncMock(spec=FileDriver)
    mock_storage.read.side_effect = Exception("Read failure")
    with patch("backend_v2.database.repositories.execution.get_storage_driver", return_value=mock_storage):
        with pytest.raises(AppException):
            await repo.append_trace_event(_EXE_ID, event)


@pytest.mark.asyncio
async def test_get_all_executions_handles_offloaded_null_frozen_context(
    repo: ExecutionRepositoryImpl, mock_driver: AsyncMock, valid_execution_doc: ExecutionRecord
) -> None:
    """Regression: get_all_executions must successfully parse records with offloaded (null) frozen_context."""
    offloaded_doc = valid_execution_doc.model_dump(mode="json")
    offloaded_doc["frozen_context"] = None
    offloaded_doc["frozen_context_storage_path"] = f"executions/{_EXE_ID}/frozen_context.json"
    mock_driver.query.return_value = [offloaded_doc]

    results = await repo.get_all_executions()
    assert len(results) == 1
    assert results[0].id == _EXE_ID
    assert results[0].frozen_context is None


@pytest.mark.asyncio
async def test_get_execution_missing_offload_blob_data_corruption(
    repo: ExecutionRepositoryImpl, mock_driver: AsyncMock, valid_execution_doc: ExecutionRecord
) -> None:
    """Regression: Missing offloaded blob file on disk raises AppException with DATA_CORRUPTION code."""
    doc = valid_execution_doc.model_dump(mode="json")
    doc["execution_trace_storage_path"] = f"executions/{_EXE_ID}/execution_trace.json"
    mock_driver.get.return_value = doc

    mock_storage = AsyncMock(spec=FileDriver)
    mock_storage.read.side_effect = AppException(
        message=f"File not found: executions/{_EXE_ID}/execution_trace.json",
        status_code=404,
        details={"error_code": "FILE_NOT_FOUND"},
    )

    with patch("backend_v2.database.repositories.execution.get_storage_driver", return_value=mock_storage):
        with pytest.raises(AppException) as exc_info:
            await repo.get_execution(_EXE_ID)

        assert exc_info.value.status_code == 500
        assert exc_info.value.details["error_code"] == "DATA_CORRUPTION"
        assert "Missing blob trace data for execution_trace." in exc_info.value.message
