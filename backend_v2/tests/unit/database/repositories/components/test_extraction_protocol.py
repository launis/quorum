"""Unit tests for ExtractionProtocolRepositoryImpl."""

from unittest.mock import AsyncMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.components.extraction_protocol import ExtractionProtocolRepositoryImpl
from backend_v2.exceptions import ResourceNotFoundError


@pytest.fixture
def mock_driver() -> AsyncMock:
    """Mock storage driver."""
    driver = AsyncMock(spec=StorageDriver)
    driver.query.return_value = []
    driver.get.return_value = None
    driver.upsert.return_value = "ext_123"
    driver.update.return_value = True
    driver.delete.return_value = True
    return driver


@pytest.fixture
def repo(mock_driver: AsyncMock) -> ExtractionProtocolRepositoryImpl:
    """Extraction protocol repository fixture."""
    return ExtractionProtocolRepositoryImpl(mock_driver)


@pytest.mark.asyncio
async def test_extraction_protocol_crud(repo: ExtractionProtocolRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: tests extraction protocol CRUD operations."""
    sample_doc = {"id": "ext_123", "type": "extraction_protocol", "name": "Standard Protocol"}
    mock_driver.get.return_value = sample_doc
    mock_driver.query.return_value = [sample_doc]

    res = await repo.get_extraction_protocol_by_id("ext_123")
    assert res == sample_doc

    all_res = await repo.get_all_extraction_protocols()
    assert len(all_res) == 1
    assert all_res[0]["id"] == "ext_123"

    assert await repo.create_extraction_protocol(sample_doc) == "ext_123"
    assert await repo.update_extraction_protocol("ext_123", {"name": "Updated"}) == "ext_123"
    assert await repo.delete_extraction_protocol("ext_123") is True


@pytest.mark.asyncio
async def test_update_extraction_protocol_not_found(repo: ExtractionProtocolRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Negative: update raises ResourceNotFoundError if protocol not found."""
    mock_driver.get.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await repo.update_extraction_protocol("ext_missing", {"name": "Updated"})
