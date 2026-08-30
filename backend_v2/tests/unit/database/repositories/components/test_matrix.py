"""Unit tests for MatrixRepositoryImpl."""

from unittest.mock import AsyncMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.components.matrix import MatrixRepositoryImpl
from backend_v2.exceptions import ResourceNotFoundError


@pytest.fixture
def mock_driver() -> AsyncMock:
    """Provides a mocked StorageDriver."""
    driver = AsyncMock(spec=StorageDriver)
    driver.query.return_value = []
    driver.get.return_value = None
    driver.upsert.return_value = "mat_1"
    driver.update.return_value = True
    driver.delete.return_value = True
    return driver


@pytest.fixture
def repo(mock_driver: AsyncMock) -> MatrixRepositoryImpl:
    """Provides a MatrixRepositoryImpl instance with the mocked driver."""
    return MatrixRepositoryImpl(mock_driver)


@pytest.mark.asyncio
async def test_matrix_crud_and_dimension_lookup(repo: MatrixRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: tests matrix listing, getting by ID, creation, update, deletion, and dimension search."""
    sample_doc = {
        "id": "mat_1",
        "type": "evaluation_matrix",
        "content": {"criteria": [{"dimension_id": "dim_1"}]},
    }
    mock_driver.query.return_value = [sample_doc]
    mock_driver.get.return_value = sample_doc

    matrices = await repo.get_all_matrices()
    assert len(matrices) == 1
    assert matrices[0]["id"] == "mat_1"

    matrix = await repo.get_matrix_by_id("mat_1")
    assert matrix is not None

    dim_matches = await repo.get_matrices_using_dimension("dim_1")
    assert dim_matches == ["mat_1"]

    assert await repo.create_matrix({"id": "mat_1"}) == "mat_1"
    assert await repo.update_matrix("mat_1", {"name": "Updated"}) == "mat_1"
    assert await repo.delete_matrix("mat_1") is True


@pytest.mark.asyncio
async def test_matrix_not_found(repo: MatrixRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Negative: update raises ResourceNotFoundError and delete returns False when matrix is missing."""
    mock_driver.get.return_value = None

    assert await repo.get_matrix_by_id("mat_missing") is None

    with pytest.raises(ResourceNotFoundError):
        await repo.update_matrix("mat_missing", {"name": "Updated"})

    assert await repo.delete_matrix("mat_missing") is False
