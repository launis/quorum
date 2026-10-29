"""Unit tests for ExecutionPersonaRepositoryImpl."""

from __future__ import annotations

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.postgres.storage_driver import PostgresStorageDriver
from backend_v2.database.repositories.components.execution_persona import (
    ExecutionPersonaRepositoryImpl,
)
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.prompt_blocks import PersonaPromptBlock
from backend_v2.models.enums import BlockDataType, PromptBlockCategory


@pytest.fixture
def driver() -> StorageDriver:
    """Provide an in-memory PostgresStorageDriver instance for hermetic testing.

    Returns:
        Configured StorageDriver instance with pool initialization disabled.
    """
    return PostgresStorageDriver(auto_initialize_pool=False)


@pytest.fixture
def repo(driver: StorageDriver) -> ExecutionPersonaRepositoryImpl:
    """Provide an ExecutionPersonaRepositoryImpl instance backed by the stateful driver.

    Args:
        driver: Stateful in-memory storage driver.

    Returns:
        Configured ExecutionPersonaRepositoryImpl instance.
    """
    return ExecutionPersonaRepositoryImpl(driver)


@pytest.fixture
def sample_persona() -> PersonaPromptBlock:
    """Provide a valid PersonaPromptBlock instance.

    Returns:
        Validated PersonaPromptBlock domain model.
    """
    return PersonaPromptBlock(
        id="blk_1234567890abcdef",
        slug="per_123",
        label=I18nText(translations={"en": "Persona 1", "fi": "Persoona 1"}),
        description=I18nText(translations={"en": "Description", "fi": "Kuvaus"}),
        category_id=PromptBlockCategory.EXECUTION_PERSONA,
        type=BlockDataType.INSTRUCTION,
        role_enforcement="Act as senior executive coach.",
    )


@pytest.mark.asyncio
async def test_execution_persona_crud_roundtrip(
    repo: ExecutionPersonaRepositoryImpl,
    sample_persona: PersonaPromptBlock,
) -> None:
    """Positive: verify full stateful CRUD roundtrip for execution personas."""
    created_id = await repo.create_execution_persona(sample_persona)
    assert created_id == sample_persona.id

    fetched = await repo.get_execution_persona_by_id(sample_persona.id)
    assert fetched is not None
    assert isinstance(fetched, PersonaPromptBlock)
    assert fetched.id == sample_persona.id
    assert fetched.role_enforcement == "Act as senior executive coach."

    all_personas = await repo.get_all_execution_personas()
    assert len(all_personas) == 1
    assert all_personas[0].id == sample_persona.id

    updated_persona = sample_persona.model_copy(
        update={"role_enforcement": "Act as principal forensic auditor."}
    )
    updated_id = await repo.update_execution_persona(sample_persona.id, updated_persona)
    assert updated_id == sample_persona.id

    refetched = await repo.get_execution_persona_by_id(sample_persona.id)
    assert refetched is not None
    assert isinstance(refetched, PersonaPromptBlock)
    assert refetched.role_enforcement == "Act as principal forensic auditor."

    deleted = await repo.delete_execution_persona(sample_persona.id)
    assert deleted is True
    assert await repo.get_execution_persona_by_id(sample_persona.id) is None
    assert await repo.get_all_execution_personas() == []


@pytest.mark.asyncio
async def test_update_execution_persona_not_found(
    repo: ExecutionPersonaRepositoryImpl,
    sample_persona: PersonaPromptBlock,
) -> None:
    """Negative: update_execution_persona raises ResourceNotFoundError if persona does not exist."""
    with pytest.raises(ResourceNotFoundError) as exc_info:
        await repo.update_execution_persona("blk_0000000000000000", sample_persona)

    assert exc_info.value.details["resource_type"] == "ExecutionPersona"
    assert exc_info.value.details["resource_id"] == "blk_0000000000000000"


@pytest.mark.asyncio
async def test_delete_execution_persona_not_found(
    repo: ExecutionPersonaRepositoryImpl,
) -> None:
    """Negative boundary: delete_execution_persona returns False when persona does not exist."""
    assert await repo.delete_execution_persona("blk_0000000000000000") is False


@pytest.mark.asyncio
async def test_get_execution_persona_by_id_corrupted_raises_app_exception(
    repo: ExecutionPersonaRepositoryImpl,
    driver: StorageDriver,
) -> None:
    """Negative: get_execution_persona_by_id raises AppException(500) on corrupted record."""
    await driver.upsert(
        "components",
        {"id": "blk_1111111111111111", "category_id": "invalid_category"},
        "blk_1111111111111111",
    )

    with pytest.raises(AppException) as exc_info:
        await repo.get_execution_persona_by_id("blk_1111111111111111")

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "blk_1111111111111111" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_all_execution_personas_corrupted_with_id_raises_app_exception(
    repo: ExecutionPersonaRepositoryImpl,
    driver: StorageDriver,
) -> None:
    """Negative: get_all_execution_personas raises AppException(500) when stored record with ID is invalid."""
    await driver.upsert(
        "components",
        {
            "id": "blk_2222222222222222",
            "category_id": PromptBlockCategory.EXECUTION_PERSONA.value,
            "type": "invalid_type",
        },
        "blk_2222222222222222",
    )

    with pytest.raises(AppException) as exc_info:
        await repo.get_all_execution_personas()

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "blk_2222222222222222" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_all_execution_personas_corrupted_without_id_raises_app_exception(
    repo: ExecutionPersonaRepositoryImpl,
    driver: StorageDriver,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Negative boundary: get_all_execution_personas logs 'unknown' when corrupted record lacks id."""

    async def _query_corrupted(
        collection: str, *args: object, **kwargs: object
    ) -> list[dict[str, str]]:
        return [{"category_id": PromptBlockCategory.EXECUTION_PERSONA.value}]

    monkeypatch.setattr(driver, "query", _query_corrupted)

    with pytest.raises(AppException) as exc_info:
        await repo.get_all_execution_personas()

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "unknown" in exc_info.value.message
