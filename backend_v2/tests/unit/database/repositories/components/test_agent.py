"""Tests for AgentRepositoryImpl."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.components.agent import AgentRepositoryImpl


@pytest.fixture
def mock_driver() -> AsyncMock:
    """Provides a mocked StorageDriver."""
    driver = AsyncMock(spec=StorageDriver)
    return driver


@pytest.fixture
def repo(mock_driver: AsyncMock) -> AgentRepositoryImpl:
    """Provides an AgentRepositoryImpl instance with the mocked driver."""
    return AgentRepositoryImpl(mock_driver)


@pytest.mark.asyncio
async def test_agent_crud(repo: AgentRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test CRUD operations for Agents."""
    mock_driver.get.return_value = {"id": "a1"}
    mock_driver.query.return_value = [{"id": "a1"}]
    mock_driver.upsert.return_value = "a1"
    mock_driver.delete.return_value = True

    assert await repo.get_agent_by_id("a1") == {"id": "a1"}
    assert await repo.get_all_agents() == [{"id": "a1"}]
    assert await repo.create_agent({"id": "a1"}) == "a1"
    assert await repo.delete_agent("a1") is True


@pytest.mark.asyncio
async def test_update_agent(repo: AgentRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test versioned update of Agent."""
    mock_driver.get.return_value = {"id": "a1_v1", "version": 1}
    repo._increment_version = MagicMock(return_value=("a1", "a1_v2", 2))  # type: ignore[method-assign]
    res = await repo.update_agent("a1_v1", {"foo": "bar"})
    assert res is True
    mock_driver.upsert.assert_called()
