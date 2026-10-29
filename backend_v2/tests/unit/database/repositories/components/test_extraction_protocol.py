"""Unit tests for ExtractionProtocolRepositoryImpl."""

from __future__ import annotations

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.postgres.storage_driver import PostgresStorageDriver
from backend_v2.database.repositories.components.extraction_protocol import (
    ExtractionProtocolRepositoryImpl,
)
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.prompt_blocks import ProtocolPromptBlock
from backend_v2.models.enums import BlockDataType, PromptBlockCategory


@pytest.fixture
def driver() -> StorageDriver:
    """Provide an in-memory PostgresStorageDriver instance for hermetic testing.

    Returns:
        Configured StorageDriver instance with pool initialization disabled.
    """
    return PostgresStorageDriver(auto_initialize_pool=False)


@pytest.fixture
def repo(driver: StorageDriver) -> ExtractionProtocolRepositoryImpl:
    """Provide an ExtractionProtocolRepositoryImpl instance backed by the stateful driver.

    Args:
        driver: Stateful in-memory storage driver.

    Returns:
        Configured ExtractionProtocolRepositoryImpl instance.
    """
    return ExtractionProtocolRepositoryImpl(driver)


@pytest.fixture
def sample_protocol() -> ProtocolPromptBlock:
    """Provide a valid ProtocolPromptBlock instance.

    Returns:
        Validated ProtocolPromptBlock domain model.
    """
    return ProtocolPromptBlock(
        id="blk_0195f3a0000070018234567890abcdef",
        slug="ext_123",
        label=I18nText(translations={"en": "Standard Protocol", "fi": "Vakioprotokolla"}),
        description=I18nText(translations={"en": "Description", "fi": "Kuvaus"}),
        category_id=PromptBlockCategory.PROTOCOL,
        type=BlockDataType.INSTRUCTION,
        protocol_instructions="Extract exact quotes rigorously.",
    )


@pytest.mark.asyncio
async def test_extraction_protocol_crud_roundtrip(
    repo: ExtractionProtocolRepositoryImpl,
    sample_protocol: ProtocolPromptBlock,
) -> None:
    """Positive: verify full stateful CRUD roundtrip for extraction protocols."""
    created_id = await repo.create_extraction_protocol(sample_protocol)
    assert created_id == sample_protocol.id

    fetched = await repo.get_extraction_protocol_by_id(sample_protocol.id)
    assert fetched is not None
    assert isinstance(fetched, ProtocolPromptBlock)
    assert fetched.id == sample_protocol.id
    assert fetched.protocol_instructions == "Extract exact quotes rigorously."

    all_protocols = await repo.get_all_extraction_protocols()
    assert len(all_protocols) == 1
    assert all_protocols[0].id == sample_protocol.id

    updated_protocol = sample_protocol.model_copy(
        update={"protocol_instructions": "Extract forensic evidence with verbatim anchoring."}
    )
    updated_id = await repo.update_extraction_protocol(sample_protocol.id, updated_protocol)
    assert updated_id == sample_protocol.id

    refetched = await repo.get_extraction_protocol_by_id(sample_protocol.id)
    assert refetched is not None
    assert isinstance(refetched, ProtocolPromptBlock)
    assert refetched.protocol_instructions == "Extract forensic evidence with verbatim anchoring."

    deleted = await repo.delete_extraction_protocol(sample_protocol.id)
    assert deleted is True
    assert await repo.get_extraction_protocol_by_id(sample_protocol.id) is None
    assert await repo.get_all_extraction_protocols() == []


@pytest.mark.asyncio
async def test_update_extraction_protocol_not_found(
    repo: ExtractionProtocolRepositoryImpl,
    sample_protocol: ProtocolPromptBlock,
) -> None:
    """Negative: update_extraction_protocol raises ResourceNotFoundError if protocol does not exist."""
    with pytest.raises(ResourceNotFoundError) as exc_info:
        await repo.update_extraction_protocol("blk_0195f3a0000070008000000000000000", sample_protocol)

    assert exc_info.value.details["resource_type"] == "ExtractionProtocol"
    assert exc_info.value.details["resource_id"] == "blk_0195f3a0000070008000000000000000"


@pytest.mark.asyncio
async def test_delete_extraction_protocol_not_found(
    repo: ExtractionProtocolRepositoryImpl,
) -> None:
    """Negative boundary: delete_extraction_protocol returns False when protocol does not exist."""
    assert await repo.delete_extraction_protocol("blk_0195f3a0000070008000000000000000") is False


@pytest.mark.asyncio
async def test_get_extraction_protocol_by_id_corrupted_raises_app_exception(
    repo: ExtractionProtocolRepositoryImpl,
    driver: StorageDriver,
) -> None:
    """Negative: get_extraction_protocol_by_id raises AppException(500) on corrupted record."""
    await driver.upsert(
        "components",
        {"id": "blk_0195f3a0000070018111111111111111", "category_id": "invalid_category"},
        "blk_0195f3a0000070018111111111111111",
    )

    with pytest.raises(AppException) as exc_info:
        await repo.get_extraction_protocol_by_id("blk_0195f3a0000070018111111111111111")

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "blk_0195f3a0000070018111111111111111" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_all_extraction_protocols_corrupted_with_id_raises_app_exception(
    repo: ExtractionProtocolRepositoryImpl,
    driver: StorageDriver,
) -> None:
    """Negative: get_all_extraction_protocols raises AppException(500) when stored record with ID is invalid."""
    await driver.upsert(
        "components",
        {
            "id": "blk_0195f3a0000070028222222222222222",
            "category_id": PromptBlockCategory.PROTOCOL.value,
            "type": "invalid_type",
        },
        "blk_0195f3a0000070028222222222222222",
    )

    with pytest.raises(AppException) as exc_info:
        await repo.get_all_extraction_protocols()

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "blk_0195f3a0000070028222222222222222" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_all_extraction_protocols_corrupted_without_id_raises_app_exception(
    repo: ExtractionProtocolRepositoryImpl,
    driver: StorageDriver,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Negative boundary: get_all_extraction_protocols logs 'unknown' when corrupted record lacks id."""

    async def _query_corrupted(collection: str, *args: object, **kwargs: object) -> list[dict[str, str]]:
        return [{"category_id": PromptBlockCategory.PROTOCOL.value}]

    monkeypatch.setattr(driver, "query", _query_corrupted)

    with pytest.raises(AppException) as exc_info:
        await repo.get_all_extraction_protocols()

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "unknown" in exc_info.value.message
