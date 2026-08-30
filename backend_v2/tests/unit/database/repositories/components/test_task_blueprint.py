"""Unit tests for TaskBlueprintRepositoryImpl."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.components.task_blueprint import TaskBlueprintRepositoryImpl
from backend_v2.exceptions import AppException


@pytest.fixture
def mock_driver() -> AsyncMock:
    """Provides a mocked StorageDriver."""
    driver = AsyncMock(spec=StorageDriver)
    driver.query.return_value = []
    driver.get.return_value = None
    driver.upsert.return_value = "stp_1234567890abcdef"
    driver.update.return_value = True
    driver.delete.return_value = True
    return driver


@pytest.fixture
def repo(mock_driver: AsyncMock) -> TaskBlueprintRepositoryImpl:
    """Provides a TaskBlueprintRepositoryImpl instance with the mocked driver."""
    return TaskBlueprintRepositoryImpl(mock_driver)


@pytest.fixture
def valid_step_doc() -> dict:
    """Valid Step document fixture."""
    return {
        "id": "stp_1234567890abcdef",
        "slug": "step_guard",
        "name": {"translations": {"en": "Guard Step", "fi": "Suojavaihe"}},
        "model_strategy": "fast",
        "criteria_block_ids": ["blk_1234567890abcdef"],
        "extraction_protocol_block_id": "blk_1234567890abcdef",
    }


@pytest.mark.asyncio
async def test_task_blueprint_crud(
    repo: TaskBlueprintRepositoryImpl, mock_driver: AsyncMock, valid_step_doc: dict
) -> None:
    """Positive: tests CRUD operations for TaskBlueprints."""
    mock_driver.get.return_value = valid_step_doc
    mock_driver.query.return_value = [valid_step_doc]

    model = await repo.get_task_blueprint_by_id("stp_1234567890abcdef")
    assert model is not None
    assert model.id == "stp_1234567890abcdef"
    assert model.slug == "step_guard"

    all_models = await repo.get_all_task_blueprints()
    assert len(all_models) == 1
    assert all_models[0].id == "stp_1234567890abcdef"

    assert await repo.create_task_blueprint(valid_step_doc) == "stp_1234567890abcdef"
    assert await repo.delete_task_blueprint("stp_1234567890abcdef") is True


@pytest.mark.asyncio
async def test_update_task_blueprint(
    repo: TaskBlueprintRepositoryImpl, mock_driver: AsyncMock, valid_step_doc: dict
) -> None:
    """Positive: tests versioned update of TaskBlueprint."""
    doc_with_version = dict(valid_step_doc)
    doc_with_version["version"] = 1
    mock_driver.get.return_value = doc_with_version
    repo._increment_version = MagicMock(return_value=("stp_guard", "stp_1234567890abcdef_v2", 2))  # type: ignore[method-assign]
    res = await repo.update_task_blueprint("stp_1234567890abcdef", {"slug": "updated"})
    assert res is True
    mock_driver.upsert.assert_called()


@pytest.mark.asyncio
async def test_task_blueprint_parsing_failures(
    repo: TaskBlueprintRepositoryImpl, mock_driver: AsyncMock
) -> None:
    """Negative: corrupted Step blueprint data raises AppException."""
    corrupted_doc = {"id": "invalid_id"}
    mock_driver.get.return_value = corrupted_doc
    mock_driver.query.return_value = [corrupted_doc]

    with pytest.raises(AppException):
        await repo.get_task_blueprint_by_id("invalid_id")

    with pytest.raises(AppException):
        await repo.get_all_task_blueprints()


@pytest.mark.asyncio
async def test_task_blueprint_not_found(
    repo: TaskBlueprintRepositoryImpl, mock_driver: AsyncMock
) -> None:
    """Negative: tests not found branches for get, update, and delete."""
    mock_driver.get.return_value = None

    assert await repo.get_task_blueprint_by_id("stp_missing") is None
    assert await repo.update_task_blueprint("stp_missing", {"slug": "new"}) is False
    assert await repo.delete_task_blueprint("stp_missing") is False
