"""Unit tests for ReportArtifactRepositoryImpl.

Verifies full CRUD lifecycle, in-place updates, schema validation, and error boundaries
for the 'report_artifacts' collection in strict adherence to Tripartite Pipeline Architecture.
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from backend_v2.database.repositories.report_artifact import (
    _COLLECTION_NAME,
    ReportArtifactRepositoryImpl,
)
from backend_v2.database.repository import UnifiedWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.dtos.report_artifact import (
    ReportArtifactUpdateDTO,
    ReportMetadataDTO,
    ReportStatus,
    ReportStoragePathsDTO,
)
from backend_v2.models.enums import CognitiveTier


def _build_test_report_artifact(
    report_id: str = "rep_a1b2c3d4e5f60718",
    execution_id: str = "exe_1234567890abcdef",
    workflow_id: str = "wf_abcdef1234567890",
    profile_id: str = "prf_fedcba0987654321",
    locale: str = "fi",
    title: str = "Test Forensic Report",
    status: ReportStatus = ReportStatus.PENDING,
) -> ReportArtifact:
    """Helper to construct a valid ReportArtifact model."""
    return ReportArtifact(
        id=report_id,
        execution_id=execution_id,
        workflow_id=workflow_id,
        profile_id=profile_id,
        locale=locale,
        title=title,
        status=status,
        storage_paths=ReportStoragePathsDTO(pdf_path=f"artifacts/reports/{report_id}/report.pdf"),
        metadata=ReportMetadataDTO(
            cost_usd=0.042,
            duration_ms=1250,
            tokens_used=1800,
            llm_model="gemini-2.5-flash",
            cognitive_tier=CognitiveTier.BALANCED,
        ),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_report() -> ReportArtifact:
    """Fixture returning a canonical ReportArtifact."""
    return _build_test_report_artifact()


# =========================================================================
# 1. CREATE_REPORT_ARTIFACT TESTS
# =========================================================================


@pytest.mark.asyncio
async def test_create_report_artifact_success(sample_report: ReportArtifact) -> None:
    """Positive: creates and persists a new ReportArtifact document."""
    mock_driver = AsyncMock()
    mock_driver.upsert.return_value = sample_report.id

    repo = ReportArtifactRepositoryImpl(driver=mock_driver)
    result = await repo.create_report_artifact(sample_report)

    assert result.id == sample_report.id
    assert result.status == ReportStatus.PENDING
    assert result.title == sample_report.title
    mock_driver.upsert.assert_awaited_once()
    args, _ = mock_driver.upsert.await_args
    assert args[0] == _COLLECTION_NAME
    assert args[1]["id"] == sample_report.id
    assert args[2] == sample_report.id


@pytest.mark.asyncio
async def test_create_report_artifact_driver_failure(sample_report: ReportArtifact) -> None:
    """Negative: propagates exception when underlying driver upsert fails."""
    mock_driver = AsyncMock()
    mock_driver.upsert.side_effect = AppException(
        message="Database disk write error",
        status_code=500,
        details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
    )

    repo = ReportArtifactRepositoryImpl(driver=mock_driver)
    with pytest.raises(AppException) as exc_info:
        await repo.create_report_artifact(sample_report)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value


# =========================================================================
# 2. GET_REPORT_ARTIFACT TESTS
# =========================================================================


@pytest.mark.asyncio
async def test_get_report_artifact_found(sample_report: ReportArtifact) -> None:
    """Positive: retrieves and deserializes existing ReportArtifact."""
    mock_driver = AsyncMock()
    mock_driver.get.return_value = sample_report.model_dump(mode="json")

    repo = ReportArtifactRepositoryImpl(driver=mock_driver)
    result = await repo.get_report_artifact(sample_report.id)

    assert result is not None
    assert result.id == sample_report.id
    assert result.execution_id == sample_report.execution_id
    assert result.status == ReportStatus.PENDING
    assert result.storage_paths.pdf_path == sample_report.storage_paths.pdf_path
    mock_driver.get.assert_awaited_once_with(_COLLECTION_NAME, sample_report.id)


@pytest.mark.asyncio
async def test_get_report_artifact_not_found() -> None:
    """Negative: returns None when document does not exist in collection."""
    mock_driver = AsyncMock()
    mock_driver.get.return_value = None

    repo = ReportArtifactRepositoryImpl(driver=mock_driver)
    result = await repo.get_report_artifact("rep_missing00000000")

    assert result is None
    mock_driver.get.assert_awaited_once_with(_COLLECTION_NAME, "rep_missing00000000")


@pytest.mark.asyncio
async def test_get_report_artifact_validation_failure() -> None:
    """Negative: raises AppException(500) if persisted document fails schema validation."""
    mock_driver = AsyncMock()
    # Malformed document missing mandatory fields
    mock_driver.get.return_value = {"id": "rep_corrupted00000", "invalid_key": 123}

    repo = ReportArtifactRepositoryImpl(driver=mock_driver)
    with pytest.raises(AppException) as exc_info:
        await repo.get_report_artifact("rep_corrupted00000")

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


# =========================================================================
# 3. LIST_REPORT_ARTIFACTS_BY_EXECUTION TESTS
# =========================================================================


@pytest.mark.asyncio
async def test_list_report_artifacts_by_execution_found(sample_report: ReportArtifact) -> None:
    """Positive: retrieves all report artifacts matching execution_id."""
    second_report = _build_test_report_artifact(
        report_id="rep_b2c3d4e5f6071829",
        profile_id="prf_second00000000",
        title="Second Report",
        status=ReportStatus.READY,
    )
    mock_driver = AsyncMock()
    mock_driver.query.return_value = [
        sample_report.model_dump(mode="json"),
        second_report.model_dump(mode="json"),
    ]

    repo = ReportArtifactRepositoryImpl(driver=mock_driver)
    results = await repo.list_report_artifacts_by_execution(sample_report.execution_id)

    assert len(results) == 2
    assert results[0].id == sample_report.id
    assert results[1].id == second_report.id
    assert results[1].status == ReportStatus.READY


@pytest.mark.asyncio
async def test_list_report_artifacts_by_execution_empty() -> None:
    """Negative/Boundary: returns empty list when no reports match execution_id."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = []

    repo = ReportArtifactRepositoryImpl(driver=mock_driver)
    results = await repo.list_report_artifacts_by_execution("exe_unmatched000000")

    assert results == []


@pytest.mark.asyncio
async def test_list_report_artifacts_by_execution_validation_failure() -> None:
    """Negative: raises AppException(500) if any item in queried collection fails validation."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = [{"corrupted": True}]

    repo = ReportArtifactRepositoryImpl(driver=mock_driver)
    with pytest.raises(AppException) as exc_info:
        await repo.list_report_artifacts_by_execution("exe_1234567890abcdef")

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


# =========================================================================
# 4. UPDATE_REPORT_ARTIFACT TESTS
# =========================================================================


@pytest.mark.asyncio
async def test_update_report_artifact_success(sample_report: ReportArtifact) -> None:
    """Positive: applies in-place partial update to existing report artifact."""
    mock_driver = AsyncMock()
    mock_driver.get.return_value = sample_report.model_dump(mode="json")
    mock_driver.upsert.return_value = sample_report.id

    repo = ReportArtifactRepositoryImpl(driver=mock_driver)
    update_dto = ReportArtifactUpdateDTO(
        status=ReportStatus.READY,
        storage_paths=ReportStoragePathsDTO(
            pdf_path=f"artifacts/reports/{sample_report.id}/report.pdf",
            sdui_json_path=f"artifacts/reports/{sample_report.id}/report.sdui.json",
            excel_path=f"artifacts/reports/{sample_report.id}/report.xlsx",
        ),
        metadata=ReportMetadataDTO(
            cost_usd=0.085,
            duration_ms=2500,
            tokens_used=3600,
            llm_model="gemini-2.5-flash",
            cognitive_tier=CognitiveTier.BALANCED,
        ),
    )

    updated = await repo.update_report_artifact(sample_report.id, update_dto)

    assert updated.id == sample_report.id
    assert updated.status == ReportStatus.READY
    assert updated.storage_paths.sdui_json_path is not None
    assert updated.storage_paths.excel_path is not None
    assert updated.metadata.cost_usd == 0.085
    mock_driver.upsert.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_report_artifact_not_found() -> None:
    """Negative: raises AppException(404) with RESOURCE_NOT_FOUND when record missing."""
    mock_driver = AsyncMock()
    mock_driver.get.return_value = None

    repo = ReportArtifactRepositoryImpl(driver=mock_driver)
    update_dto = ReportArtifactUpdateDTO(status=ReportStatus.FAILED, error_message="Generation crashed")

    with pytest.raises(AppException) as exc_info:
        await repo.update_report_artifact("rep_missing00000000", update_dto)

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_update_report_artifact_with_error_message(sample_report: ReportArtifact) -> None:
    """Positive/Edge: updates report status to FAILED with error message."""
    mock_driver = AsyncMock()
    mock_driver.get.return_value = sample_report.model_dump(mode="json")
    mock_driver.upsert.return_value = sample_report.id

    repo = ReportArtifactRepositoryImpl(driver=mock_driver)
    update_dto = ReportArtifactUpdateDTO(
        status=ReportStatus.FAILED,
        error_message="Synthesis timeout exceeded after 60s",
    )

    updated = await repo.update_report_artifact(sample_report.id, update_dto)

    assert updated.status == ReportStatus.FAILED
    assert updated.error_message == "Synthesis timeout exceeded after 60s"


# =========================================================================
# 5. DELETE_REPORT_ARTIFACT TESTS
# =========================================================================


@pytest.mark.asyncio
async def test_delete_report_artifact_success() -> None:
    """Positive: deletes document and returns True."""
    mock_driver = AsyncMock()
    mock_driver.delete.return_value = True

    repo = ReportArtifactRepositoryImpl(driver=mock_driver)
    result = await repo.delete_report_artifact("rep_a1b2c3d4e5f60718")

    assert result is True
    mock_driver.delete.assert_awaited_once_with(_COLLECTION_NAME, "rep_a1b2c3d4e5f60718")


@pytest.mark.asyncio
async def test_delete_report_artifact_not_found() -> None:
    """Negative: returns False when document does not exist."""
    mock_driver = AsyncMock()
    mock_driver.delete.return_value = False

    repo = ReportArtifactRepositoryImpl(driver=mock_driver)
    result = await repo.delete_report_artifact("rep_nonexistent0000")

    assert result is False


# =========================================================================
# 6. UNIFIED_WORKFLOW_REPOSITORY INTEGRATION TEST
# =========================================================================


def test_unified_workflow_repository_inheritance() -> None:
    """Verifies that UnifiedWorkflowRepository inherits ReportArtifactRepositoryImpl."""
    mock_driver = AsyncMock()
    unified = UnifiedWorkflowRepository(driver=mock_driver)

    assert isinstance(unified, ReportArtifactRepositoryImpl)
    assert hasattr(unified, "create_report_artifact")
    assert hasattr(unified, "get_report_artifact")
    assert hasattr(unified, "list_report_artifacts_by_execution")
    assert hasattr(unified, "update_report_artifact")
    assert hasattr(unified, "delete_report_artifact")
