"""Unit and boundary tests for ReportArtifactRepositoryImpl over InMemoryUnitOfWork.

Covers stateful CRUD roundtrips, execution-scoped listing order, UnifiedWorkflowRepository
composition, and negative identifier validation and configuration failure paths.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from backend_v2.database.repositories.report_artifact import ReportArtifactRepositoryImpl
from backend_v2.database.repository import UnifiedWorkflowRepository
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, generate_opaque_id
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.dtos.report_artifact import (
    ReportArtifactUpdateDTO,
    ReportMetadataDTO,
    ReportStoragePathsDTO,
)
from backend_v2.models.enums import CognitiveTier, EntityPrefix, ReportStatus
from backend_v2.tests.factories.model_factories import ReportArtifactFactory
from backend_v2.tests.fakes.in_memory_uow import InMemoryUnitOfWork


@pytest.fixture
def base_uow() -> InMemoryUnitOfWork:
    """Create an isolated InMemoryUnitOfWork backing store for each test.

    Returns:
        Fresh InMemoryUnitOfWork instance.
    """
    return InMemoryUnitOfWork()


@pytest.fixture
def repo(base_uow: InMemoryUnitOfWork) -> ReportArtifactRepositoryImpl:
    """Create a ReportArtifactRepositoryImpl bound to a shared InMemoryUnitOfWork store.

    Args:
        base_uow: Shared in-memory Unit of Work fixture.

    Returns:
        Configured ReportArtifactRepositoryImpl instance.
    """
    return ReportArtifactRepositoryImpl(uow_factory=lambda: InMemoryUnitOfWork(base_uow.store))


@pytest.mark.asyncio
async def test_create_and_get_report_artifact_roundtrip_success(
    repo: ReportArtifactRepositoryImpl,
) -> None:
    """Verify create_report_artifact persists and get_report_artifact reconstitutes full model state."""
    artifact = ReportArtifactFactory.build(
        locale="fi",
        title="Executive Synthesis Report",
        status=ReportStatus.GENERATING,
        custom_preface_md="### Executive Preface",
    )

    persisted = await repo.create_report_artifact(artifact)
    assert persisted == artifact

    fetched = await repo.get_report_artifact(artifact.id)
    assert fetched is not None
    assert fetched == artifact
    assert ReportArtifact.model_validate(fetched.model_dump(mode="json"), strict=False) == artifact


@pytest.mark.asyncio
async def test_list_report_artifacts_by_execution_roundtrip_and_ordering(
    repo: ReportArtifactRepositoryImpl,
) -> None:
    """Verify list_report_artifacts_by_execution filters by execution_id and orders newest first."""
    target_exe_id = generate_opaque_id(EntityPrefix.EXECUTION)
    other_exe_id = generate_opaque_id(EntityPrefix.EXECUTION)
    empty_exe_id = generate_opaque_id(EntityPrefix.EXECUTION)
    base_time = datetime(2026, 5, 1, 12, 0, 0, tzinfo=UTC)

    older_report = ReportArtifactFactory.build(
        id="rep_0195f3a0000070008000000000000001",
        execution_id=target_exe_id,
        title="Older Report",
        updated_at=base_time,
    )
    newer_report = ReportArtifactFactory.build(
        id="rep_0195f3a003e870008000000000000002",
        execution_id=target_exe_id,
        title="Newer Report",
        updated_at=base_time + timedelta(minutes=10),
    )
    unrelated_report = ReportArtifactFactory.build(
        id="rep_0195f3a007d070008000000000000003",
        execution_id=other_exe_id,
        title="Unrelated Execution Report",
        updated_at=base_time + timedelta(minutes=20),
    )

    await repo.create_report_artifact(older_report)
    await repo.create_report_artifact(newer_report)
    await repo.create_report_artifact(unrelated_report)

    listed = await repo.list_report_artifacts_by_execution(target_exe_id)
    assert [item.id for item in listed] == [newer_report.id, older_report.id]
    assert await repo.list_report_artifacts_by_execution(empty_exe_id) == []


@pytest.mark.asyncio
async def test_update_report_artifact_roundtrip_success_and_error_transition(
    repo: ReportArtifactRepositoryImpl,
) -> None:
    """Verify update_report_artifact mutates fields in-place and persists across subsequent fetches."""
    initial = ReportArtifactFactory.build(
        status=ReportStatus.GENERATING,
        custom_preface_md="Immutable preface",
    )
    await repo.create_report_artifact(initial)

    registry_id = generate_opaque_id(EntityPrefix.MODEL_REGISTRY)
    ready_paths = ReportStoragePathsDTO(
        pdf_path="reports/out.pdf",
        sdui_json_path="reports/out.json",
        excel_path="reports/out.xlsx",
        csv_path="reports/out.csv",
    )
    ready_meta = ReportMetadataDTO(
        cost_usd=0.042,
        duration_ms=1350,
        tokens_used=4200,
        llm_model="gemini-2.5-pro",
        provider="vertex_ai",
        cognitive_tier=CognitiveTier.DEEP,
        model_registry_id=registry_id,
        thinking_tokens=512,
    )

    updated_ready = await repo.update_report_artifact(
        initial.id,
        ReportArtifactUpdateDTO(
            status=ReportStatus.READY,
            storage_paths=ready_paths,
            metadata=ready_meta,
        ),
    )
    assert updated_ready.id == initial.id
    assert updated_ready.status == ReportStatus.READY
    assert updated_ready.storage_paths == ready_paths
    assert updated_ready.metadata == ready_meta
    assert updated_ready.custom_preface_md == "Immutable preface"

    fetched_ready = await repo.get_report_artifact(initial.id)
    assert fetched_ready == updated_ready

    updated_failed = await repo.update_report_artifact(
        initial.id,
        ReportArtifactUpdateDTO(
            status=ReportStatus.FAILED,
            error_message="PDF compilation failed due to template error",
        ),
    )
    assert updated_failed.status == ReportStatus.FAILED
    assert updated_failed.error_message == "PDF compilation failed due to template error"
    assert updated_failed.storage_paths == ready_paths

    fetched_failed = await repo.get_report_artifact(initial.id)
    assert fetched_failed == updated_failed


@pytest.mark.asyncio
async def test_delete_report_artifact_roundtrip(repo: ReportArtifactRepositoryImpl) -> None:
    """Verify delete_report_artifact removes persisted record and returns False when already absent."""
    artifact = ReportArtifactFactory.build()
    await repo.create_report_artifact(artifact)

    assert await repo.delete_report_artifact(artifact.id) is True
    assert await repo.get_report_artifact(artifact.id) is None
    assert await repo.delete_report_artifact(artifact.id) is False


@pytest.mark.asyncio
async def test_unified_workflow_repository_report_artifact_roundtrip(
    base_uow: InMemoryUnitOfWork,
) -> None:
    """Verify UnifiedWorkflowRepository inherits ReportArtifactRepositoryImpl and persists statefully."""
    unified_repo = UnifiedWorkflowRepository(uow_factory=lambda: InMemoryUnitOfWork(base_uow.store))
    assert isinstance(unified_repo, ReportArtifactRepositoryImpl)

    artifact = ReportArtifactFactory.build()
    assert artifact.id is not None
    assert OPAQUE_STRIPE_ID_REGEX is not None

    await unified_repo.create_report_artifact(artifact)
    fetched = await unified_repo.get_report_artifact(artifact.id)
    assert fetched == artifact

    assert await unified_repo.delete_report_artifact(artifact.id) is True
    assert await unified_repo.get_report_artifact(artifact.id) is None


@pytest.mark.asyncio
async def test_get_report_artifact_not_found_returns_none(
    repo: ReportArtifactRepositoryImpl,
) -> None:
    """Verify get_report_artifact returns None when canonical report_id does not exist."""
    missing_id = generate_opaque_id(EntityPrefix.REPORT)
    assert await repo.get_report_artifact(missing_id) is None


@pytest.mark.asyncio
async def test_update_report_artifact_not_found_error(
    repo: ReportArtifactRepositoryImpl,
) -> None:
    """Verify update_report_artifact raises AppException RESOURCE_NOT_FOUND when target record is missing."""
    missing_id = generate_opaque_id(EntityPrefix.REPORT)
    update_dto = ReportArtifactUpdateDTO(status=ReportStatus.FAILED, error_message="Missing target")

    with pytest.raises(AppException) as exc_info:
        await repo.update_report_artifact(missing_id, update_dto)

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_report_artifact_invalid_prefix_raises_validation_failure(
    repo: ReportArtifactRepositoryImpl,
) -> None:
    """Verify mismatched Opaque Stripe ID prefixes raise AppException VALIDATION_FAILED."""
    wrong_for_report = generate_opaque_id(EntityPrefix.EXECUTION)
    wrong_for_execution = generate_opaque_id(EntityPrefix.REPORT)

    with pytest.raises(AppException) as get_exc:
        await repo.get_report_artifact(wrong_for_report)
    assert get_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    with pytest.raises(AppException) as list_exc:
        await repo.list_report_artifacts_by_execution(wrong_for_execution)
    assert list_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    with pytest.raises(AppException) as del_exc:
        await repo.delete_report_artifact(wrong_for_report)
    assert del_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_report_artifact_unconfigured_uow_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify repository operations fail fast with ConfigurationError when UnitOfWorkFactory is missing."""
    monkeypatch.setattr("backend_v2.database.repositories.base.get_registered_uow_factory", lambda: None)
    unconfigured_repo = ReportArtifactRepositoryImpl(uow_factory=None)
    artifact = ReportArtifactFactory.build()

    with pytest.raises(ConfigurationError) as exc_info:
        await unconfigured_repo.create_report_artifact(artifact)

    assert exc_info.value.error_code == ErrorCodes.CONFIGURATION_ERROR
