"""Unit tests for OutputProfileRepositoryImpl over EntityPersistencePort."""

from __future__ import annotations

import pytest

from backend_v2.database.postgres.pool import PostgresPoolManager
from backend_v2.database.postgres.uow import PostgresUnitOfWork
from backend_v2.database.repositories.components.output_profile import OutputProfileRepositoryImpl
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.enums import StorageBackend, TargetBlockType
from backend_v2.settings import Settings
from backend_v2.tests.factories.model_factories import I18nTextFactory, OutputProfileFactory
from backend_v2.tests.fakes.in_memory_uow import InMemoryAsyncPgPool, InMemoryUnitOfWork

_PRF_ID = "prf_0195f3a0000070018234567890abcdef"
_PRF_ALT_ID = "prf_0195f3a0000070028222222222222222"
_PRF_MISSING_ID = "prf_0195f3a0000070008000000000000000"
_WF_ID = "wf_0195f3a0000070018234567890abcdef"


@pytest.fixture
def base_uow() -> InMemoryUnitOfWork:
    """Provide a shared InMemoryUnitOfWork store for stateful repository tests."""
    return InMemoryUnitOfWork()


@pytest.fixture
def repo(base_uow: InMemoryUnitOfWork) -> OutputProfileRepositoryImpl:
    """Provide an OutputProfileRepositoryImpl backed by the stateful InMemoryUnitOfWork store."""
    return OutputProfileRepositoryImpl(uow_factory=lambda: InMemoryUnitOfWork(base_uow.store))


@pytest.fixture
def sample_output_profile() -> OutputProfile:
    """Provide a valid OutputProfile instance via Polyfactory."""
    return OutputProfileFactory.build(
        id=_PRF_ID,
        slug="exec-summary",
        workflow_id=_WF_ID,
        name=I18nTextFactory.build(translations={"fi": "Summary FI", "en": "Summary"}),
        target_block_order=[
            TargetBlockType.EXECUTIVE_SUMMARY_BLOCK,
            TargetBlockType.GLOBAL_SCORE_BLOCK,
        ],
        content_blocks=[],
    )


@pytest.mark.asyncio
async def test_output_profile_crud_roundtrip(
    repo: OutputProfileRepositoryImpl,
    sample_output_profile: OutputProfile,
) -> None:
    """Positive: verify full stateful CRUD roundtrip for OutputProfileRepositoryImpl."""
    created_id = await repo.create_output_profile(sample_output_profile)
    assert created_id == sample_output_profile.id

    fetched = await repo.get_output_profile_by_id(sample_output_profile.id)
    assert fetched is not None
    assert fetched.id == sample_output_profile.id
    assert fetched.slug == "exec-summary"

    all_models = await repo.get_all_output_profiles()
    assert len(all_models) == 1
    assert all_models[0].id == sample_output_profile.id

    all_models_alias = await repo.get_all_output_profiles_models()
    assert len(all_models_alias) == 1
    assert all_models_alias[0].id == sample_output_profile.id

    updated_profile = sample_output_profile.model_copy(
        update={"id": _PRF_ALT_ID, "tone_instruction": "Concise executive style."}
    )
    updated_ok = await repo.update_output_profile(sample_output_profile.id, updated_profile)
    assert updated_ok is True

    refetched = await repo.get_output_profile_by_id(sample_output_profile.id)
    assert refetched is not None
    assert refetched.id == sample_output_profile.id
    assert refetched.tone_instruction == "Concise executive style."

    deleted_ok = await repo.delete_output_profile(sample_output_profile.id)
    assert deleted_ok is True
    assert await repo.get_output_profile_by_id(sample_output_profile.id) is None
    assert await repo.get_all_output_profiles() == []


@pytest.mark.asyncio
async def test_get_output_profile_by_id_not_found(repo: OutputProfileRepositoryImpl) -> None:
    """Negative boundary: get_output_profile_by_id returns None when profile does not exist."""
    assert await repo.get_output_profile_by_id(_PRF_MISSING_ID) is None


@pytest.mark.asyncio
async def test_update_output_profile_not_found(
    repo: OutputProfileRepositoryImpl,
    sample_output_profile: OutputProfile,
) -> None:
    """Negative boundary: update_output_profile returns False when profile does not exist."""
    assert await repo.update_output_profile(_PRF_MISSING_ID, sample_output_profile) is False


@pytest.mark.asyncio
async def test_delete_output_profile_not_found(repo: OutputProfileRepositoryImpl) -> None:
    """Negative boundary: delete_output_profile returns False when profile does not exist."""
    assert await repo.delete_output_profile(_PRF_MISSING_ID) is False


@pytest.mark.asyncio
async def test_output_profile_invalid_prefix_and_storage_fault_failure() -> None:
    """Negative: invalid ID prefix raises VALIDATION_FAILED and SQL fault raises STORAGE_ACCESS_FAILED."""
    pool = InMemoryAsyncPgPool()
    settings = Settings(
        storage_backend=StorageBackend.POSTGRES,
        postgres_host="db.internal",
        postgres_port=5432,
        postgres_user="quorum",
        postgres_db="quorum",
        postgres_command_timeout_seconds=5.0,
    )
    pool_mgr = PostgresPoolManager(settings=settings, pool=pool)
    pg_repo = OutputProfileRepositoryImpl(uow_factory=lambda: PostgresUnitOfWork(pool_mgr))

    with pytest.raises(AppException) as invalid_exc:
        await pg_repo.get_output_profile_by_id(_WF_ID)
    assert invalid_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    try:
        pool.inject_fault("fetch", RuntimeError("simulated list failure"))
        with pytest.raises(AppException) as fault_exc:
            await pg_repo.get_all_output_profiles()
        assert fault_exc.value.status_code == 500
        assert fault_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
    finally:
        pool.clear_faults()


@pytest.mark.asyncio
async def test_delete_output_profile_blocked_by_workflow_default_and_target_block_uuid_validation(
    repo: OutputProfileRepositoryImpl,
    base_uow: InMemoryUnitOfWork,
    sample_output_profile: OutputProfile,
) -> None:
    """Verify delete_output_profile enforces deferrable FK restrict and OutputProfile validates blk_ target blocks."""
    from backend_v2.tests.factories.model_factories import ReportArtifactFactory, WorkflowFactory

    await repo.create_output_profile(sample_output_profile)
    referencing_wf = WorkflowFactory.build(id=_WF_ID, default_profile_id=sample_output_profile.id)
    async with InMemoryUnitOfWork(base_uow.store) as uow:
        await uow.entities.upsert_workflow(referencing_wf)

    # Negative 1: Workflow default_profile_id reference blocks deletion with DELETE_BLOCKED_BY_USAGE
    with pytest.raises(AppException) as wf_ref_exc:
        await repo.delete_output_profile(sample_output_profile.id)
    assert wf_ref_exc.value.status_code == 400
    assert wf_ref_exc.value.details["error_code"] == ErrorCodes.DELETE_BLOCKED_BY_USAGE.value

    # Detach workflow default_profile_id, attach ReportArtifact.profile_id, verify still blocked
    detached_wf = referencing_wf.model_copy(update={"default_profile_id": None})
    report_ref = ReportArtifactFactory.build(workflow_id=_WF_ID, profile_id=sample_output_profile.id)
    async with InMemoryUnitOfWork(base_uow.store) as uow:
        await uow.entities.upsert_workflow(detached_wf)
        await uow.entities.upsert_report_artifact(report_ref)

    with pytest.raises(AppException) as rep_ref_exc:
        await repo.delete_output_profile(sample_output_profile.id)
    assert rep_ref_exc.value.status_code == 400
    assert rep_ref_exc.value.details["error_code"] == ErrorCodes.DELETE_BLOCKED_BY_USAGE.value

    # Negative 2: Invalid variance_target_block or user_role_target_block fails schema validation
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        OutputProfileFactory.build(variance_target_block="invalid_block_id")

    with pytest.raises(ValidationError):
        OutputProfileFactory.build(user_role_target_block=_WF_ID)
