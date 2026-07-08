from unittest.mock import AsyncMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.components.matrix import MatrixRepositoryImpl


@pytest.fixture
def mock_driver() -> AsyncMock:
    return AsyncMock(spec=StorageDriver)


@pytest.fixture
def repo(mock_driver: AsyncMock) -> MatrixRepositoryImpl:
    return MatrixRepositoryImpl(driver=mock_driver)


@pytest.mark.asyncio
async def test_get_components_using_dimension(repo: MatrixRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test get components using dimension logic."""
    mock_driver.query.return_value = [
        {"id": "m1", "type": "evaluation_matrix", "content": {"criteria": [{"dimension_id": "dim1"}]}},
        {"id": "m2", "type": "evaluation_matrix", "content": {"criteria": [{"dimension_id": "dim2"}]}},
        {"id": "m3", "type": "evaluation_matrix"},  # Missing content
        {"id": "m4", "type": "evaluation_matrix", "content": "not_dict"},
    ]
    res = await repo.get_matrices_using_dimension("dim1")
    assert res == ["m1"]
