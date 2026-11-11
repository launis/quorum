"""Unit tests for TaskBriefRepositoryImpl."""

from __future__ import annotations

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.postgres.storage_driver import PostgresStorageDriver
from backend_v2.database.repositories.components.task_brief import TaskBriefRepositoryImpl
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.task_brief import TaskBrief
from backend_v2.tests.factories.model_factories import TaskBriefFactory


@pytest.fixture
def driver() -> StorageDriver:
    """Provide an in-memory PostgresStorageDriver instance for hermetic testing.

    Returns:
        Configured StorageDriver instance with pool initialization disabled.
    """
    return PostgresStorageDriver(auto_initialize_pool=False)


@pytest.fixture
def repo(driver: StorageDriver) -> TaskBriefRepositoryImpl:
    """Provide a TaskBriefRepositoryImpl instance backed by the stateful driver.

    Args:
        driver: Stateful in-memory storage driver.

    Returns:
        Configured TaskBriefRepositoryImpl instance.
    """
    return TaskBriefRepositoryImpl(driver)


@pytest.fixture
def sample_task_brief() -> TaskBrief:
    """Provide a valid TaskBrief instance.

    Returns:
        Validated TaskBrief domain model.
    """
    return TaskBriefFactory.build(
        id="tbr_0195f3a0000070018234567890abcdef",
        slug="strategic-case-brief",
        label=I18nText(translations={"fi": "Tehtävänanto", "en": "Task Brief"}),
        description=I18nText(translations={"fi": "Kuvaus", "en": "Description"}),
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

    updated_brief = sample_task_brief.model_copy(update={"instruction_text": "Updated instruction text."})
    updated_ok = await repo.update_task_brief(sample_task_brief.id, updated_brief)
    assert updated_ok is True

    refetched = await repo.get_task_brief_by_id(sample_task_brief.id)
    assert refetched is not None
    assert refetched.instruction_text == "Updated instruction text."

    deleted_ok = await repo.delete_task_brief(sample_task_brief.id)
    assert deleted_ok is True
    assert await repo.get_task_brief_by_id(sample_task_brief.id) is None
    assert await repo.get_all_task_briefs() == []


@pytest.mark.asyncio
async def test_get_task_brief_by_id_not_found(repo: TaskBriefRepositoryImpl) -> None:
    """Negative boundary: get_task_brief_by_id returns None when brief does not exist."""
    assert await repo.get_task_brief_by_id("tbr_0195f3a0000070008000000000000000") is None


@pytest.mark.asyncio
async def test_update_task_brief_not_found(
    repo: TaskBriefRepositoryImpl,
    sample_task_brief: TaskBrief,
) -> None:
    """Negative boundary: update_task_brief returns False when brief does not exist."""
    assert await repo.update_task_brief("tbr_0195f3a0000070008000000000000000", sample_task_brief) is False


@pytest.mark.asyncio
async def test_delete_task_brief_not_found(repo: TaskBriefRepositoryImpl) -> None:
    """Negative boundary: delete_task_brief returns False when brief does not exist."""
    assert await repo.delete_task_brief("tbr_0195f3a0000070008000000000000000") is False


@pytest.mark.asyncio
async def test_get_task_brief_by_id_corrupted_invalid_error(
    repo: TaskBriefRepositoryImpl,
    driver: StorageDriver,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Negative: get_task_brief_by_id raises AppException(500) on corrupted record."""

    async def _get_corrupted(collection: str, doc_id: str) -> dict[str, str]:
        return {"id": doc_id, "invalid_field": "corrupted"}

    monkeypatch.setattr(driver, "get", _get_corrupted)

    with pytest.raises(AppException) as exc_info:
        await repo.get_task_brief_by_id("tbr_0195f3a0000070018111111111111111")

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "tbr_0195f3a0000070018111111111111111" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_all_task_briefs_corrupted_with_id_failure(
    repo: TaskBriefRepositoryImpl,
    driver: StorageDriver,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Negative: get_all_task_briefs raises AppException(500) when stored record with ID is invalid."""

    async def _query_corrupted(collection: str, *args: object, **kwargs: object) -> list[dict[str, str]]:
        return [{"id": "tbr_0195f3a0000070028222222222222222", "invalid_field": "corrupted"}]

    monkeypatch.setattr(driver, "query", _query_corrupted)

    with pytest.raises(AppException) as exc_info:
        await repo.get_all_task_briefs()

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "tbr_0195f3a0000070028222222222222222" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_all_task_briefs_corrupted_without_id_error(
    repo: TaskBriefRepositoryImpl,
    driver: StorageDriver,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Negative boundary: get_all_task_briefs logs 'unknown' when corrupted record lacks id."""

    async def _query_corrupted(collection: str, *args: object, **kwargs: object) -> list[dict[str, str]]:
        return [{"invalid_field": "corrupted"}]

    monkeypatch.setattr(driver, "query", _query_corrupted)

    with pytest.raises(AppException) as exc_info:
        await repo.get_all_task_briefs()

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "unknown" in exc_info.value.message
