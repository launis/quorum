"""Tests for OutputProfileRepositoryImpl."""

from unittest.mock import AsyncMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.components.output_profile import OutputProfileRepositoryImpl
from backend_v2.exceptions import AppException


@pytest.fixture
def mock_driver() -> AsyncMock:
    """Provides a mocked StorageDriver."""
    driver = AsyncMock(spec=StorageDriver)
    return driver


@pytest.fixture
def repo(mock_driver: AsyncMock) -> OutputProfileRepositoryImpl:
    """Provides an OutputProfileRepositoryImpl instance with the mocked driver."""
    return OutputProfileRepositoryImpl(mock_driver)


@pytest.mark.asyncio
async def test_output_profile_crud(repo: OutputProfileRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test CRUD operations for OutputProfiles."""
    mock_driver.get.return_value = {"id": "op1"}
    mock_driver.query.return_value = [{"id": "op1"}]
    mock_driver.upsert.return_value = "op1"
    mock_driver.update.return_value = True
    mock_driver.delete.return_value = True

    assert await repo.get_output_profile_by_id("op1") == {"id": "op1"}
    assert await repo.get_all_output_profiles() == [{"id": "op1"}]
    assert await repo.create_output_profile({"id": "op1"}) == "op1"
    assert await repo.update_output_profile("op1", {"foo": "bar"}) is True
    assert await repo.delete_output_profile("op1") is True


@pytest.mark.asyncio
async def test_get_all_output_profiles_models_failure(
    repo: OutputProfileRepositoryImpl, mock_driver: AsyncMock
) -> None:
    """Test parsing failure for OutputProfiles models."""
    mock_driver.query.return_value = [{"invalid": "data"}]
    with pytest.raises(AppException) as exc:
        await repo.get_all_output_profiles_models()
    assert exc.value.status_code == 500
