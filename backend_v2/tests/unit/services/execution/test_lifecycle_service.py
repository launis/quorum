"""Unit tests for ExecutionLifecycleService."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.exceptions import AppException, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.domain.execution import ExecutionRecord, FrozenContext
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.dtos.report_artifact import ReportMetadataDTO, ReportStatus, ReportStoragePathsDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.services.execution.ingress_service import create_execution_record
from backend_v2.services.execution.lifecycle_service import ExecutionLifecycleService
from backend_v2.tests.fakes.in_memory_repositories import (
    InMemoryExecutionRepository,
    InMemoryReportArtifactRepository,
)


def _make_record(
    execution_id: str = "exe_0123456789abcdef",
    org_id: str = "org_0123456789abcdef",
    user_id: str = "usr_0123456789abcdef",
) -> ExecutionRecord:
    return create_execution_record(
        execution_id=execution_id,
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputs(),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        organization_id=org_id,
        created_by=user_id,
        status=ExecutionStatus.PENDING,
    )


@pytest.fixture
def member_token() -> TokenData:
    return TokenData(id="usr_0123456789abcdef", role=UserRole.MEMBER, organization_id="org_0123456789abcdef")


@pytest.fixture
def root_token() -> TokenData:
    return TokenData(id="usr_root000000000000", role=UserRole.ROOT, organization_id="org_root000000000000")


@pytest.mark.asyncio
async def test_init_binds_resumption_service() -> None:
    """Verify __init__ extracts check_resumability from resumption_service when not passed explicitly."""
    resumption_service = MagicMock()
    resumption_service.check_resumability = AsyncMock(return_value=True)

    service = ExecutionLifecycleService(
        exec_repo=InMemoryExecutionRepository(),
        resumption_service=resumption_service,
    )
    assert service._check_resumability == resumption_service.check_resumability


@pytest.mark.asyncio
async def test_list_executions_root_returns_all(root_token: TokenData) -> None:
    """Verify ROOT user can list all executions across all organizations."""
    rec1 = _make_record(execution_id="exe_0123456789abcdef", org_id="org_aaa0000000000000")
    rec2 = _make_record(execution_id="exe_1123456789abcdef", org_id="org_bbb0000000000000")

    exec_repo = InMemoryExecutionRepository()
    await exec_repo.save_execution(rec1)
    await exec_repo.save_execution(rec2)

    service = ExecutionLifecycleService(exec_repo=exec_repo)
    result = await service.list_executions(root_token)
    assert len(result) == 2


@pytest.mark.asyncio
async def test_list_executions_member_filters_by_org_and_creator(member_token: TokenData) -> None:
    """Verify standard MEMBER lists only executions belonging to their org or created by them."""
    rec_same_org = _make_record(
        execution_id="exe_0123456789abcdef",
        org_id="org_0123456789abcdef",
        user_id="usr_other0000000000",
    )
    rec_same_creator = _make_record(
        execution_id="exe_1123456789abcdef",
        org_id="org_different0000000",
        user_id="usr_0123456789abcdef",
    )
    rec_foreign = _make_record(
        execution_id="exe_2123456789abcdef",
        org_id="org_different0000000",
        user_id="usr_other0000000000",
    )

    exec_repo = InMemoryExecutionRepository()
    await exec_repo.save_execution(rec_same_org)
    await exec_repo.save_execution(rec_same_creator)
    await exec_repo.save_execution(rec_foreign)

    service = ExecutionLifecycleService(exec_repo=exec_repo)
    result = await service.list_executions(member_token)
    assert len(result) == 2
    assert {e.id for e in result} == {"exe_0123456789abcdef", "exe_1123456789abcdef"}


@pytest.mark.asyncio
async def test_list_executions_with_check_resumability(member_token: TokenData) -> None:
    """Verify list_executions concurrently resolves is_resumable flag via TaskGroup."""
    rec = _make_record()
    exec_repo = InMemoryExecutionRepository()
    await exec_repo.save_execution(rec)

    check_fn = AsyncMock(return_value=True)
    service = ExecutionLifecycleService(exec_repo=exec_repo, check_resumability_fn=check_fn)
    result = await service.list_executions(member_token)

    assert len(result) == 1
    assert result[0].is_resumable is True
    check_fn.assert_awaited_once_with(rec)


@pytest.mark.asyncio
async def test_list_executions_repository_error_raises_app_exception(member_token: TokenData) -> None:
    """Verify list_executions wraps unexpected errors into 500 AppException."""
    exec_repo = InMemoryExecutionRepository()
    exec_repo.inject_fault("get_all_executions", RuntimeError("DB disconnected"))

    service = ExecutionLifecycleService(exec_repo=exec_repo)
    with pytest.raises(AppException) as exc_info:
        await service.list_executions(member_token)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_get_execution_happy_path(member_token: TokenData) -> None:
    """Verify get_execution returns record with resumability evaluation."""
    rec = _make_record()
    exec_repo = InMemoryExecutionRepository()
    await exec_repo.save_execution(rec)

    check_fn = AsyncMock(return_value=True)
    service = ExecutionLifecycleService(exec_repo=exec_repo, check_resumability_fn=check_fn)
    result = await service.get_execution(member_token, "exe_0123456789abcdef", hydrate=True)

    assert result.id == "exe_0123456789abcdef"
    assert result.is_resumable is True


@pytest.mark.asyncio
async def test_get_execution_skip_resumability(member_token: TokenData) -> None:
    """Verify get_execution with skip_resumability=True skips check function."""
    rec = _make_record()
    exec_repo = InMemoryExecutionRepository()
    await exec_repo.save_execution(rec)

    check_fn = AsyncMock()
    service = ExecutionLifecycleService(exec_repo=exec_repo, check_resumability_fn=check_fn)
    result = await service.get_execution(member_token, "exe_0123456789abcdef", skip_resumability=True)

    assert result.id == "exe_0123456789abcdef"
    assert not check_fn.called


@pytest.mark.asyncio
async def test_get_execution_not_found(member_token: TokenData) -> None:
    """Verify get_execution raises ResourceNotFoundError when execution is missing."""
    exec_repo = InMemoryExecutionRepository()

    service = ExecutionLifecycleService(exec_repo=exec_repo)
    with pytest.raises(ResourceNotFoundError):
        await service.get_execution(member_token, "exe_missing00000000")


@pytest.mark.asyncio
async def test_get_execution_permission_denied(member_token: TokenData) -> None:
    """Verify get_execution raises PermissionDeniedError when member attempts cross-tenant access."""
    rec = _make_record(
        execution_id="exe_0123456789abcdef",
        org_id="org_other0000000000",
        user_id="usr_other0000000000",
    )
    exec_repo = InMemoryExecutionRepository()
    await exec_repo.save_execution(rec)

    service = ExecutionLifecycleService(exec_repo=exec_repo)
    with pytest.raises(PermissionDeniedError):
        await service.get_execution(member_token, "exe_0123456789abcdef")


@pytest.mark.asyncio
async def test_delete_execution_not_found(member_token: TokenData) -> None:
    """Verify delete_execution raises ResourceNotFoundError when record does not exist."""
    exec_repo = InMemoryExecutionRepository()

    service = ExecutionLifecycleService(exec_repo=exec_repo)
    with pytest.raises(ResourceNotFoundError):
        await service.delete_execution(member_token, "exe_missing00000000")


@pytest.mark.asyncio
async def test_delete_execution_permission_denied(member_token: TokenData) -> None:
    """Verify delete_execution raises PermissionDeniedError when member attempts cross-tenant delete."""
    rec = _make_record(
        execution_id="exe_0123456789abcdef",
        org_id="org_other0000000000",
        user_id="usr_other0000000000",
    )
    exec_repo = InMemoryExecutionRepository()
    await exec_repo.save_execution(rec)

    service = ExecutionLifecycleService(exec_repo=exec_repo)
    with pytest.raises(PermissionDeniedError):
        await service.delete_execution(member_token, "exe_0123456789abcdef")


@pytest.mark.asyncio
async def test_delete_execution_happy_path_with_cascade(member_token: TokenData) -> None:
    """Verify delete_execution cascade cleans report artifacts, files, and blob directories."""
    rec = _make_record()
    exec_repo = InMemoryExecutionRepository()
    await exec_repo.save_execution(rec)

    storage_driver = AsyncMock()
    storage_driver.delete = AsyncMock(return_value=True)
    storage_driver.delete_directory = AsyncMock(return_value=True)

    now = datetime.now(UTC)
    report = ReportArtifact(
        id="rep_0123456789abcdef",
        execution_id=rec.id,
        workflow_id="wor_0123456789abcdef",
        profile_id="prf_0123456789abcdef",
        locale="en",
        title="Test Report",
        status=ReportStatus.READY,
        storage_paths=ReportStoragePathsDTO(
            pdf_path="reports/report.pdf",
            sdui_json_path="reports/report.sdui.json",
            excel_path="reports/report.xlsx",
            csv_path="reports/report.csv",
        ),
        metadata=ReportMetadataDTO(),
        created_at=now,
        updated_at=now,
    )
    report_repo = InMemoryReportArtifactRepository()
    report_repo.save_report_artifact(report)

    service = ExecutionLifecycleService(
        exec_repo=exec_repo,
        storage_driver=storage_driver,
        report_repo=report_repo,
    )
    success = await service.delete_execution(member_token, rec.id)
    assert success is True
    assert storage_driver.delete.call_count == 4
    assert await report_repo.get_report_artifact(report.id) is None
    storage_driver.delete_directory.assert_awaited_once_with(f"executions/{rec.id}")
    assert await exec_repo.get_execution(rec.id) is None


@pytest.mark.asyncio
async def test_delete_execution_cascade_report_error_tolerated(member_token: TokenData) -> None:
    """Verify non-fatal cascade report errors are swallowed without halting execution deletion."""
    rec = _make_record()
    exec_repo = InMemoryExecutionRepository()
    await exec_repo.save_execution(rec)

    storage_driver = AsyncMock()
    storage_driver.delete_directory = AsyncMock(return_value=True)

    report_repo = InMemoryReportArtifactRepository()
    report_repo.inject_fault("list_report_artifacts_by_execution", OSError("Disk read failure"))

    service = ExecutionLifecycleService(
        exec_repo=exec_repo,
        storage_driver=storage_driver,
        report_repo=report_repo,
    )
    success = await service.delete_execution(member_token, rec.id)
    assert success is True
    storage_driver.delete_directory.assert_awaited_once_with(f"executions/{rec.id}")
    assert await exec_repo.get_execution(rec.id) is None


@pytest.mark.asyncio
async def test_delete_execution_storage_delete_directory_app_exception_404_ignored(member_token: TokenData) -> None:
    """Verify 404 from storage.delete_directory is ignored as already cleaned."""
    rec = _make_record()
    exec_repo = InMemoryExecutionRepository()
    await exec_repo.save_execution(rec)

    storage_driver = AsyncMock()
    storage_driver.delete_directory = AsyncMock(side_effect=AppException("Not found", status_code=404))

    service = ExecutionLifecycleService(exec_repo=exec_repo, storage_driver=storage_driver)
    success = await service.delete_execution(member_token, rec.id)
    assert success is True
    assert await exec_repo.get_execution(rec.id) is None


@pytest.mark.asyncio
async def test_delete_execution_storage_delete_directory_app_exception_non_404_raises(
    member_token: TokenData,
) -> None:
    """Verify non-404 AppException from storage.delete_directory raises 500 AppException."""
    rec = _make_record()
    exec_repo = InMemoryExecutionRepository()
    await exec_repo.save_execution(rec)

    storage_driver = AsyncMock()
    storage_driver.delete_directory = AsyncMock(side_effect=AppException("GCS timeout", status_code=503))

    service = ExecutionLifecycleService(exec_repo=exec_repo, storage_driver=storage_driver)
    with pytest.raises(AppException) as exc_info:
        await service.delete_execution(member_token, rec.id)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_delete_execution_storage_delete_directory_generic_error_raises(member_token: TokenData) -> None:
    """Verify unexpected exception from storage.delete_directory raises 500 AppException."""
    rec = _make_record()
    exec_repo = InMemoryExecutionRepository()
    await exec_repo.save_execution(rec)

    storage_driver = AsyncMock()
    storage_driver.delete_directory = AsyncMock(side_effect=RuntimeError("Storage connection failed"))

    service = ExecutionLifecycleService(exec_repo=exec_repo, storage_driver=storage_driver)
    with pytest.raises(AppException) as exc_info:
        await service.delete_execution(member_token, rec.id)
    assert exc_info.value.status_code == 500
