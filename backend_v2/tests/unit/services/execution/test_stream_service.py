"""Unit tests for ExecutionStreamService."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.domain.execution import ExecutionRecord, FrozenContext
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.enums import ExecutionStatus
from backend_v2.services.execution.ingress_service import create_execution_record
from backend_v2.services.execution.stream_service import ExecutionStreamService
from backend_v2.tests.fakes.in_memory_repositories import InMemoryExecutionRepository


def _make_record(
    execution_id: str = "exe_0123456789abcdef",
    org_id: str = "org_0123456789abcdef",
    user_id: str = "usr_0123456789abcdef",
    status: ExecutionStatus = ExecutionStatus.PENDING,
) -> ExecutionRecord:
    return create_execution_record(
        execution_id=execution_id,
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputs(),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        organization_id=org_id,
        created_by=user_id,
        status=status,
    )


@pytest.fixture
def member_token() -> TokenData:
    return TokenData(id="usr_0123456789abcdef", role=UserRole.MEMBER, organization_id="org_0123456789abcdef")


@pytest.fixture
def root_token() -> TokenData:
    return TokenData(id="usr_root000000000000", role=UserRole.ROOT, organization_id="org_root000000000000")


@pytest.mark.asyncio
async def test_default_get_execution_happy_path(member_token: TokenData) -> None:
    """Verify _default_get_execution fetches and returns record for valid tenant."""
    rec = _make_record()
    exec_repo = InMemoryExecutionRepository()
    exec_repo.get_execution = AsyncMock(return_value=rec)

    service = ExecutionStreamService(exec_repo=exec_repo)
    result = await service._default_get_execution(member_token, "exe_0123456789abcdef")
    assert result.id == "exe_0123456789abcdef"


@pytest.mark.asyncio
async def test_default_get_execution_not_found(member_token: TokenData) -> None:
    """Verify _default_get_execution raises ResourceNotFoundError when execution is missing."""
    exec_repo = InMemoryExecutionRepository()
    exec_repo.get_execution = AsyncMock(return_value=None)

    service = ExecutionStreamService(exec_repo=exec_repo)
    with pytest.raises(ResourceNotFoundError):
        await service._default_get_execution(member_token, "exe_missing00000000")


@pytest.mark.asyncio
async def test_default_get_execution_permission_denied(member_token: TokenData) -> None:
    """Verify _default_get_execution raises PermissionDeniedError when member accesses other tenant's execution."""
    rec = _make_record(org_id="org_other0000000000", user_id="usr_other0000000000")
    exec_repo = InMemoryExecutionRepository()
    exec_repo.get_execution = AsyncMock(return_value=rec)

    service = ExecutionStreamService(exec_repo=exec_repo)
    with pytest.raises(PermissionDeniedError):
        await service._default_get_execution(member_token, "exe_0123456789abcdef")


@pytest.mark.asyncio
async def test_stream_status_happy_path_completes(member_token: TokenData, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify stream_status yields execution records and completes when status reaches PASSED."""
    rec_pending = _make_record(status=ExecutionStatus.PENDING)
    rec_passed = _make_record(status=ExecutionStatus.PASSED)

    records = [rec_pending, rec_pending, rec_passed]

    async def mock_get(initiator: TokenData, execution_id: str, **kwargs: object) -> ExecutionRecord:
        if records:
            return records.pop(0)
        return rec_passed

    exec_repo = InMemoryExecutionRepository()
    service = ExecutionStreamService(exec_repo=exec_repo, get_execution_fn=mock_get)

    from backend_v2.settings import Settings

    test_settings = Settings(
        app_env="test",
        auth_jwt_secret="0123456789abcdef0123456789abcdef",
        redis_host="127.0.0.1",
        sse_polling_interval_seconds=0.01,
        sse_max_transient_retries=2,
    )
    monkeypatch.setattr("backend_v2.services.execution.stream_service.get_settings", lambda: test_settings)

    events: list[str] = []
    async for event in service.stream_status(member_token, "exe_0123456789abcdef"):
        events.append(event)

    assert len(events) == 2
    assert "data: " in events[0]
    assert "data: " in events[1]
    parsed_last = json.loads(events[1].replace("data: ", "").strip())
    assert parsed_last["status"] == ExecutionStatus.PASSED.value


@pytest.mark.asyncio
async def test_stream_status_failed_breaks(member_token: TokenData, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify stream_status terminates when execution status reaches FAILED."""
    rec_failed = _make_record(status=ExecutionStatus.FAILED)
    records = [rec_failed, rec_failed]

    async def mock_get(initiator: TokenData, execution_id: str, **kwargs: object) -> ExecutionRecord:
        if records:
            return records.pop(0)
        return rec_failed

    exec_repo = InMemoryExecutionRepository()
    service = ExecutionStreamService(exec_repo=exec_repo, get_execution_fn=mock_get)

    from backend_v2.settings import Settings

    test_settings = Settings(
        app_env="test",
        auth_jwt_secret="0123456789abcdef0123456789abcdef",
        redis_host="127.0.0.1",
        sse_polling_interval_seconds=0.01,
        sse_max_transient_retries=2,
    )
    monkeypatch.setattr("backend_v2.services.execution.stream_service.get_settings", lambda: test_settings)

    events: list[str] = []
    async for event in service.stream_status(member_token, "exe_0123456789abcdef"):
        events.append(event)

    assert len(events) == 1
    assert "data: " in events[0]
    parsed = json.loads(events[0].replace("data: ", "").strip())
    assert parsed["status"] == ExecutionStatus.FAILED.value


@pytest.mark.asyncio
async def test_stream_status_transient_retry_and_recovery(
    member_token: TokenData, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify stream_status tolerates transient ResourceNotFoundError and continues stream."""
    rec_passed = _make_record(status=ExecutionStatus.PASSED)
    call_count = 0

    async def mock_get(initiator: TokenData, execution_id: str, **kwargs: object) -> ExecutionRecord:
        nonlocal call_count
        call_count += 1
        # Call 1: initial preflight
        if call_count == 1:
            return rec_passed
        # Call 2: transient not found
        if call_count == 2:
            raise ResourceNotFoundError(resource_type="execution", resource_id=execution_id)
        # Call 3: recovered
        return rec_passed

    from backend_v2.settings import Settings

    test_settings = Settings(
        app_env="test",
        auth_jwt_secret="0123456789abcdef0123456789abcdef",
        redis_host="127.0.0.1",
        sse_polling_interval_seconds=0.01,
        sse_max_transient_retries=2,
    )
    monkeypatch.setattr("backend_v2.services.execution.stream_service.get_settings", lambda: test_settings)

    exec_repo = InMemoryExecutionRepository()
    service = ExecutionStreamService(exec_repo=exec_repo, get_execution_fn=mock_get)

    events: list[str] = []
    async for event in service.stream_status(member_token, "exe_0123456789abcdef"):
        events.append(event)

    assert len(events) == 1
    assert "data: " in events[0]


@pytest.mark.asyncio
async def test_stream_status_exceeded_retries_emits_error_event(
    member_token: TokenData, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify stream_status emits error event and breaks when transient retries exceed max."""
    rec = _make_record()
    call_count = 0

    async def mock_get(initiator: TokenData, execution_id: str, **kwargs: object) -> ExecutionRecord:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return rec  # Preflight passes
        raise ResourceNotFoundError(resource_type="execution", resource_id=execution_id)

    from backend_v2.settings import Settings

    test_settings = Settings(
        app_env="test",
        auth_jwt_secret="0123456789abcdef0123456789abcdef",
        redis_host="127.0.0.1",
        sse_polling_interval_seconds=0.01,
        sse_max_transient_retries=1,
    )
    monkeypatch.setattr("backend_v2.services.execution.stream_service.get_settings", lambda: test_settings)

    exec_repo = InMemoryExecutionRepository()
    service = ExecutionStreamService(exec_repo=exec_repo, get_execution_fn=mock_get)

    events: list[str] = []
    async for event in service.stream_status(member_token, "exe_0123456789abcdef"):
        events.append(event)

    assert len(events) == 1
    assert events[0].startswith("event: error\ndata: ")
    error_payload = json.loads(events[0].replace("event: error\ndata: ", "").strip())
    assert error_payload["error_code"] == "SSE_STREAM_INTERRUPTED"


@pytest.mark.asyncio
async def test_stream_status_generic_exception_emits_error_event(
    member_token: TokenData, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify stream_status emits error event and terminates on unexpected AppException or OSError."""
    rec = _make_record()
    call_count = 0

    async def mock_get(initiator: TokenData, execution_id: str, **kwargs: object) -> ExecutionRecord:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return rec  # Preflight passes
        raise AppException(
            "Fatal Redis failure",
            status_code=500,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        )

    from backend_v2.settings import Settings

    test_settings = Settings(
        app_env="test",
        auth_jwt_secret="0123456789abcdef0123456789abcdef",
        redis_host="127.0.0.1",
        sse_polling_interval_seconds=0.01,
        sse_max_transient_retries=1,
    )
    monkeypatch.setattr("backend_v2.services.execution.stream_service.get_settings", lambda: test_settings)

    exec_repo = InMemoryExecutionRepository()
    service = ExecutionStreamService(exec_repo=exec_repo, get_execution_fn=mock_get)

    events: list[str] = []
    async for event in service.stream_status(member_token, "exe_0123456789abcdef"):
        events.append(event)

    assert len(events) == 1
    assert events[0].startswith("event: error\ndata: ")
    error_payload = json.loads(events[0].replace("event: error\ndata: ", "").strip())
    assert error_payload["error_code"] == "SSE_STREAM_INTERRUPTED"
