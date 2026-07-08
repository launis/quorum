from unittest.mock import AsyncMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.components.role import RoleRepositoryImpl


@pytest.fixture
def mock_driver() -> AsyncMock:
    return AsyncMock(spec=StorageDriver)


@pytest.fixture
def repo(mock_driver: AsyncMock) -> RoleRepositoryImpl:
    return RoleRepositoryImpl(driver=mock_driver)


@pytest.mark.asyncio
async def test_get_all_roles(repo: RoleRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test get all roles logic."""
    mock_driver.query.return_value = [{"id": "r1", "type": "role"}]
    res = await repo.get_all_roles()
    assert res == [{"id": "r1", "type": "role"}]
