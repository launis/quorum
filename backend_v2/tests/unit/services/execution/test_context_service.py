"""Unit tests for ExecutionContextService."""

from __future__ import annotations

import logging
from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.domain.execution import ExecutionRecord, FrozenContext
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.enums import ExecutionStatus
from backend_v2.services.execution.context_service import ExecutionContextService
from backend_v2.services.execution.ingress_service import create_execution_record
from backend_v2.tests.fakes.in_memory_repositories import InMemoryExecutionRepository


def _make_record(
    execution_id: str = "exe_0195f3a0000070008123456789abcdef",
    org_id: str = "org_0195f3a0000070008123456789abcdef",
    user_id: str = "usr_0195f3a0000070008123456789abcdef",
    status: ExecutionStatus = ExecutionStatus.PASSED,
    frozen_context: FrozenContext | None = None,
    frozen_context_storage_path: str | None = None,
) -> ExecutionRecord:
    record = create_execution_record(
        execution_id=execution_id,
        workflow_id="wor_0195f3a0000070008123456789abcdef",
        raw_inputs=WorkflowInputs(),
        frozen_context=frozen_context if frozen_context is not None else FrozenContext(),
        source_identity_manifest={},
        organization_id=org_id,
        created_by=user_id,
        status=status,
    )
    return record.model_copy(
        update={
            "frozen_context": frozen_context,
            "frozen_context_storage_path": frozen_context_storage_path,
        }
    )


@pytest.fixture
def member_token() -> TokenData:
    """Return a standard member token fixture."""
    return TokenData(
        id="usr_0195f3a0000070008123456789abcdef",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008123456789abcdef",
    )


@pytest.fixture
def root_token() -> TokenData:
    """Return a ROOT administrator token fixture."""
    return TokenData(id="usr_root000000000000", role=UserRole.ROOT, organization_id="org_root000000000000")


@pytest.mark.asyncio
async def test_default_get_execution_happy_path_same_org(member_token: TokenData) -> None:
    """Verify _default_get_execution returns record when member belongs to the execution organization."""
    rec = _make_record(user_id="usr_other0000000000")
    exec_repo = InMemoryExecutionRepository()
    await exec_repo.save_execution(rec)

    storage_mock = AsyncMock()
    service = ExecutionContextService(exec_repo=exec_repo, storage_driver=storage_mock)
    result = await service._default_get_execution(member_token, "exe_0195f3a0000070008123456789abcdef")
    assert result.id == "exe_0195f3a0000070008123456789abcdef"
    assert service.storage is storage_mock


@pytest.mark.asyncio
async def test_default_get_execution_happy_path_root_cross_org(root_token: TokenData) -> None:
    """Verify _default_get_execution allows ROOT user to access execution across organizations."""
    rec = _make_record(org_id="org_other0000000000", user_id="usr_other0000000000")
    exec_repo = InMemoryExecutionRepository()
    await exec_repo.save_execution(rec)

    service = ExecutionContextService(exec_repo=exec_repo)
    result = await service._default_get_execution(root_token, "exe_0195f3a0000070008123456789abcdef")
    assert result.id == "exe_0195f3a0000070008123456789abcdef"


@pytest.mark.asyncio
async def test_default_get_execution_not_found_logs_and_raises(
    member_token: TokenData, caplog: pytest.LogCaptureFixture
) -> None:
    """ISTQB Negative: _default_get_execution logs RFC 7807 error and raises ResourceNotFoundError when missing."""
    exec_repo = InMemoryExecutionRepository()
    service = ExecutionContextService(exec_repo=exec_repo)

    with caplog.at_level(logging.ERROR), pytest.raises(ResourceNotFoundError) as exc_info:
        await service._default_get_execution(member_token, "exe_missing00000000")

    assert exc_info.value.status_code == 404
    assert ErrorCodes.RESOURCE_NOT_FOUND.name in caplog.text


@pytest.mark.asyncio
async def test_default_get_execution_permission_denied_logs_and_raises(
    member_token: TokenData, caplog: pytest.LogCaptureFixture
) -> None:
    """ISTQB Negative: _default_get_execution logs RFC 7807 error and raises PermissionDeniedError on cross-tenant access."""
    rec = _make_record(org_id="org_other0000000000", user_id="usr_other0000000000")
    exec_repo = InMemoryExecutionRepository()
    await exec_repo.save_execution(rec)

    service = ExecutionContextService(exec_repo=exec_repo)
    with caplog.at_level(logging.ERROR), pytest.raises(PermissionDeniedError) as exc_info:
        await service._default_get_execution(member_token, "exe_0195f3a0000070008123456789abcdef")

    assert exc_info.value.status_code == 403
    assert ErrorCodes.PERMISSION_DENIED.name in caplog.text


@pytest.mark.asyncio
async def test_get_frozen_context_bytes_inline_frozen_context(member_token: TokenData) -> None:
    """Verify get_frozen_context_bytes serializes inline FrozenContext when storage path is unset."""
    fc = FrozenContext()
    rec = _make_record(frozen_context=fc, frozen_context_storage_path=None)
    exec_repo = InMemoryExecutionRepository()
    await exec_repo.save_execution(rec)

    service = ExecutionContextService(exec_repo=exec_repo)
    payload_bytes, filename = await service.get_frozen_context_bytes(
        member_token, "exe_0195f3a0000070008123456789abcdef"
    )

    assert filename == "frozen_context_exe_0195f3a0000070008123456789abcdef.json"
    parsed = FrozenContext.model_validate_json(payload_bytes)
    assert parsed == fc


@pytest.mark.asyncio
async def test_get_frozen_context_bytes_none_frozen_context_defaults_empty(member_token: TokenData) -> None:
    """Verify get_frozen_context_bytes returns empty FrozenContext JSON when both storage path and inline context are None."""
    rec = _make_record(frozen_context=None, frozen_context_storage_path=None)

    async def custom_get_exec(initiator: TokenData, execution_id: str) -> ExecutionRecord:
        return rec

    exec_repo = InMemoryExecutionRepository()
    service = ExecutionContextService(exec_repo=exec_repo, get_execution_fn=custom_get_exec)
    payload_bytes, filename = await service.get_frozen_context_bytes(
        member_token, "exe_0195f3a0000070008123456789abcdef"
    )

    assert filename == "frozen_context_exe_0195f3a0000070008123456789abcdef.json"
    parsed = FrozenContext.model_validate_json(payload_bytes)
    assert parsed == FrozenContext()


@pytest.mark.asyncio
async def test_get_frozen_context_bytes_from_storage_success(member_token: TokenData) -> None:
    """Verify get_frozen_context_bytes reads and formats offloaded frozen context from storage."""
    rec = _make_record(
        frozen_context=None,
        frozen_context_storage_path="executions/exe_0195f3a0000070008123456789abcdef/frozen_context.json",
    )
    exec_repo = InMemoryExecutionRepository()
    await exec_repo.save_execution(rec)

    mock_driver = AsyncMock()
    mock_driver.read.return_value = FrozenContext().model_dump_json().encode("utf-8")

    with patch("backend_v2.services.execution.context_service.storage.get_storage_driver", return_value=mock_driver):
        service = ExecutionContextService(exec_repo=exec_repo, storage_driver=mock_driver)
        payload_bytes, filename = await service.get_frozen_context_bytes(
            member_token, "exe_0195f3a0000070008123456789abcdef"
        )

    assert filename == "frozen_context_exe_0195f3a0000070008123456789abcdef.json"
    mock_driver.read.assert_awaited_once_with("executions/exe_0195f3a0000070008123456789abcdef/frozen_context.json")
    assert FrozenContext.model_validate_json(payload_bytes) == FrozenContext()


@pytest.mark.asyncio
async def test_get_frozen_context_bytes_storage_read_failure_raises_404(
    member_token: TokenData, caplog: pytest.LogCaptureFixture
) -> None:
    """ISTQB Negative: get_frozen_context_bytes logs error and raises 404 AppException when storage read fails."""
    rec = _make_record(
        frozen_context=None,
        frozen_context_storage_path="executions/exe_0195f3a0000070008123456789abcdef/missing.json",
    )
    exec_repo = InMemoryExecutionRepository()
    await exec_repo.save_execution(rec)

    mock_driver = AsyncMock()
    mock_driver.read.side_effect = OSError("Blob not found on disk")

    with patch("backend_v2.services.execution.context_service.storage.get_storage_driver", return_value=mock_driver):
        service = ExecutionContextService(exec_repo=exec_repo, storage_driver=mock_driver)
        with caplog.at_level(logging.ERROR), pytest.raises(AppException) as exc_info:
            await service.get_frozen_context_bytes(member_token, "exe_0195f3a0000070008123456789abcdef")

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value
    assert "Failed to fetch frozen context from storage" in caplog.text


@pytest.mark.asyncio
async def test_get_frozen_context_bytes_corrupt_storage_json_raises_404(member_token: TokenData) -> None:
    """ISTQB Negative Boundary: get_frozen_context_bytes raises 404 AppException when offloaded JSON is malformed."""
    rec = _make_record(
        frozen_context=None,
        frozen_context_storage_path="executions/exe_0195f3a0000070008123456789abcdef/corrupt.json",
    )
    exec_repo = InMemoryExecutionRepository()
    await exec_repo.save_execution(rec)

    mock_driver = AsyncMock()
    mock_driver.read.return_value = b"{not-valid-json"

    with patch("backend_v2.services.execution.context_service.storage.get_storage_driver", return_value=mock_driver):
        service = ExecutionContextService(exec_repo=exec_repo, storage_driver=mock_driver)
        with pytest.raises(AppException) as exc_info:
            await service.get_frozen_context_bytes(member_token, "exe_0195f3a0000070008123456789abcdef")

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value
