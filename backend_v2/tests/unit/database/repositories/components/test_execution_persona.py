"""Unit tests for ExecutionPersonaRepositoryImpl."""

from unittest.mock import AsyncMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.components.execution_persona import ExecutionPersonaRepositoryImpl
from backend_v2.exceptions import ResourceNotFoundError


@pytest.fixture
def mock_driver() -> AsyncMock:
    """Mock storage driver."""
    driver = AsyncMock(spec=StorageDriver)
    driver.query.return_value = []
    driver.get.return_value = None
    driver.upsert.return_value = "per_123"
    driver.update.return_value = True
    driver.delete.return_value = True
    return driver


@pytest.fixture
def repo(mock_driver: AsyncMock) -> ExecutionPersonaRepositoryImpl:
    """Execution persona repository fixture."""
    return ExecutionPersonaRepositoryImpl(mock_driver)


@pytest.mark.asyncio
async def test_execution_persona_crud(repo: ExecutionPersonaRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: tests execution persona CRUD operations."""
    sample_doc = {"id": "per_123", "type": "execution_persona", "name": "Persona 1"}
    mock_driver.get.return_value = sample_doc
    mock_driver.query.return_value = [sample_doc]

    res = await repo.get_execution_persona_by_id("per_123")
    assert res == sample_doc

    all_res = await repo.get_all_execution_personas()
    assert len(all_res) == 1
    assert all_res[0]["id"] == "per_123"

    assert await repo.create_execution_persona(sample_doc) == "per_123"
    assert await repo.update_execution_persona("per_123", {"name": "Updated"}) == "per_123"
    assert await repo.delete_execution_persona("per_123") is True


@pytest.mark.asyncio
async def test_update_execution_persona_not_found(repo: ExecutionPersonaRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Negative: update raises ResourceNotFoundError if persona not found."""
    mock_driver.get.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await repo.update_execution_persona("per_missing", {"name": "Updated"})
