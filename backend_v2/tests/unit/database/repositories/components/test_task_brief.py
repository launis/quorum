"""Unit tests for TaskBriefRepositoryImpl over EntityPersistencePort."""

from __future__ import annotations

import pytest

from backend_v2.database.postgres.pool import PostgresPoolManager
from backend_v2.database.postgres.uow import PostgresUnitOfWork
from backend_v2.database.repositories.components.task_brief import TaskBriefRepositoryImpl
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.task_brief import TaskBrief
from backend_v2.models.enums import StorageBackend
from backend_v2.settings import Settings
from backend_v2.tests.factories.model_factories import I18nTextFactory, TaskBriefFactory
from backend_v2.tests.fakes.in_memory_uow import InMemoryAsyncPgPool, InMemoryUnitOfWork

_TBR_ID = "tbr_0195f3a0000070018234567890abcdef"
_TBR_ALT_ID = "tbr_0195f3a0000070028222222222222222"
_TBR_MISSING_ID = "tbr_0195f3a0000070008000000000000000"
_BLK_ID = "blk_0195f3a0000070018234567890abcdef"


@pytest.fixture
def base_uow() -> InMemoryUnitOfWork:
    """Provide a shared InMemoryUnitOfWork store for stateful repository tests."""
    return InMemoryUnitOfWork()


@pytest.fixture
def repo(base_uow: InMemoryUnitOfWork) -> TaskBriefRepositoryImpl:
    """Provide a TaskBriefRepositoryImpl backed by the stateful InMemoryUnitOfWork store."""
    return TaskBriefRepositoryImpl(uow_factory=lambda: InMemoryUnitOfWork(base_uow.store))


@pytest.fixture
def sample_task_brief() -> TaskBrief:
    """Provide a valid TaskBrief instance via Polyfactory."""
    return TaskBriefFactory.build(
        id=_TBR_ID,
        slug="strategic-case-brief",
        label=I18nTextFactory.build(translations={"fi": "Task Brief FI", "en": "Task Brief"}),
        description=I18nTextFactory.build(translations={"fi": "Description FI", "en": "Description"}),
        instruction_text="Evaluate the executive memo and dialogue log.",
        source_url="https://quorum.ai/briefs/1",
    )


@pytest.mark.asyncio
async def test_task_brief_crud_roundtrip(
    repo: TaskBriefRepositoryImpl,
    sample_task_brief: TaskBrief,
) -> None:
    """Positive: verify full stateful CRUD roundtrip for TaskBriefRepositoryImpl."""
    created_id = await repo.create_task_brief(sample_task_brief)
    assert created_id == sample_task_brief.id

    fetched = await repo.get_task_brief_by_id(sample_task_brief.id)
    assert fetched is not None
    assert fetched.id == sample_task_brief.id
    assert fetched.slug == "strategic-case-brief"
    assert fetched.source_url == "https://quorum.ai/briefs/1"

    all_models = await repo.get_all_task_briefs()
    assert len(all_models) == 1
    assert all_models[0].id == sample_task_brief.id

    updated_brief = sample_task_brief.model_copy(
        update={"id": _TBR_ALT_ID, "instruction_text": "Updated instruction text."}
    )
    updated_ok = await repo.update_task_brief(sample_task_brief.id, updated_brief)
    assert updated_ok is True

    refetched = await repo.get_task_brief_by_id(sample_task_brief.id)
    assert refetched is not None
    assert refetched.id == sample_task_brief.id
    assert refetched.instruction_text == "Updated instruction text."

    deleted_ok = await repo.delete_task_brief(sample_task_brief.id)
    assert deleted_ok is True
    assert await repo.get_task_brief_by_id(sample_task_brief.id) is None
    assert await repo.get_all_task_briefs() == []


@pytest.mark.asyncio
async def test_get_task_brief_by_id_not_found(repo: TaskBriefRepositoryImpl) -> None:
    """Negative boundary: get_task_brief_by_id returns None when brief does not exist."""
    assert await repo.get_task_brief_by_id(_TBR_MISSING_ID) is None


@pytest.mark.asyncio
async def test_update_task_brief_not_found(
    repo: TaskBriefRepositoryImpl,
    sample_task_brief: TaskBrief,
) -> None:
    """Negative boundary: update_task_brief returns False when brief does not exist."""
    assert await repo.update_task_brief(_TBR_MISSING_ID, sample_task_brief) is False


@pytest.mark.asyncio
async def test_delete_task_brief_not_found(repo: TaskBriefRepositoryImpl) -> None:
    """Negative boundary: delete_task_brief returns False when brief does not exist."""
    assert await repo.delete_task_brief(_TBR_MISSING_ID) is False


@pytest.mark.asyncio
async def test_task_brief_invalid_prefix_and_storage_fault_failure() -> None:
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
    pg_repo = TaskBriefRepositoryImpl(uow_factory=lambda: PostgresUnitOfWork(pool_mgr))

    with pytest.raises(AppException) as invalid_exc:
        await pg_repo.get_task_brief_by_id(_BLK_ID)
    assert invalid_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    try:
        pool.inject_fault("fetch", RuntimeError("simulated list failure"))
        with pytest.raises(AppException) as fault_exc:
            await pg_repo.get_all_task_briefs()
        assert fault_exc.value.status_code == 500
        assert fault_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
    finally:
        pool.clear_faults()
