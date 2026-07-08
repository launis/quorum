"""Tests for TaskBlueprintRepositoryImpl."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.components.task_blueprint import TaskBlueprintRepositoryImpl


@pytest.fixture
def mock_driver() -> AsyncMock:
    """Provides a mocked StorageDriver."""
    driver = AsyncMock(spec=StorageDriver)
    return driver


@pytest.fixture
def repo(mock_driver: AsyncMock) -> TaskBlueprintRepositoryImpl:
    """Provides a TaskBlueprintRepositoryImpl instance with the mocked driver."""
    return TaskBlueprintRepositoryImpl(mock_driver)


@pytest.mark.asyncio
async def test_task_blueprint_crud(repo: TaskBlueprintRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test CRUD operations for TaskBlueprints."""
    mock_driver.get.return_value = {"id": "tb1"}
    mock_driver.query.return_value = [{"id": "tb1"}]
    mock_driver.upsert.return_value = "tb1"
    mock_driver.delete.return_value = True

    assert await repo.get_task_blueprint_by_id("tb1") == {"id": "tb1"}
    assert await repo.get_all_task_blueprints() == [{"id": "tb1"}]
    assert await repo.create_task_blueprint({"id": "tb1"}) == "tb1"
    assert await repo.delete_task_blueprint("tb1") is True


@pytest.mark.asyncio
async def test_update_task_blueprint(repo: TaskBlueprintRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test versioned update of TaskBlueprint."""
    mock_driver.get.return_value = {"id": "tb1_v1", "version": 1}
    repo._increment_version = MagicMock(return_value=("tb1", "tb1_v2", 2))  # type: ignore[method-assign]
    res = await repo.update_task_blueprint("tb1_v1", {"foo": "bar"})
    assert res is True
    mock_driver.upsert.assert_called()
