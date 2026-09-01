"""Unit tests for ExtractionProtocolRepositoryImpl."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.components.extraction_protocol import ExtractionProtocolRepositoryImpl
from backend_v2.exceptions import ResourceNotFoundError
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.prompt_blocks import ProtocolPromptBlock
from backend_v2.models.enums import BlockDataType, PromptBlockCategory


@pytest.fixture
def mock_driver() -> AsyncMock:
    """Mock storage driver."""
    driver = AsyncMock(spec=StorageDriver)
    driver.query.return_value = []
    driver.get.return_value = None
    driver.upsert.return_value = "blk_1234567890abcdef"
    driver.update.return_value = True
    driver.delete.return_value = True
    return driver


@pytest.fixture
def repo(mock_driver: AsyncMock) -> ExtractionProtocolRepositoryImpl:
    """Extraction protocol repository fixture."""
    return ExtractionProtocolRepositoryImpl(mock_driver)


@pytest.fixture
def sample_protocol() -> ProtocolPromptBlock:
    """Provides a valid ProtocolPromptBlock instance."""
    return ProtocolPromptBlock(
        id="blk_1234567890abcdef",
        slug="ext_123",
        label=I18nText(translations={"en": "Standard Protocol", "fi": "Vakioprotokolla"}),
        description=I18nText(translations={"en": "Description", "fi": "Kuvaus"}),
        category_id=PromptBlockCategory.PROTOCOL,
        type=BlockDataType.INSTRUCTION,
        protocol_instructions="Extract exact quotes rigorously.",
    )


@pytest.mark.asyncio
async def test_extraction_protocol_crud(
    repo: ExtractionProtocolRepositoryImpl, mock_driver: AsyncMock, sample_protocol: ProtocolPromptBlock
) -> None:
    """Positive: tests extraction protocol CRUD operations."""
    sample_doc = sample_protocol.model_dump(mode="json")
    mock_driver.get.return_value = sample_doc
    mock_driver.query.return_value = [sample_doc]

    res = await repo.get_extraction_protocol_by_id("blk_1234567890abcdef")
    assert res is not None
    assert res.id == "blk_1234567890abcdef"

    all_res = await repo.get_all_extraction_protocols()
    assert len(all_res) == 1
    assert all_res[0].id == "blk_1234567890abcdef"

    assert await repo.create_extraction_protocol(sample_protocol) == "blk_1234567890abcdef"
    assert await repo.update_extraction_protocol("blk_1234567890abcdef", sample_protocol) == "blk_1234567890abcdef"
    assert await repo.delete_extraction_protocol("blk_1234567890abcdef") is True


@pytest.mark.asyncio
async def test_update_extraction_protocol_not_found(
    repo: ExtractionProtocolRepositoryImpl, mock_driver: AsyncMock, sample_protocol: ProtocolPromptBlock
) -> None:
    """Negative: update raises ResourceNotFoundError if protocol not found."""
    mock_driver.get.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await repo.update_extraction_protocol("blk_0000000000000000", sample_protocol)
