"""Unit tests for ExecutionPersonaRepositoryImpl."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.components.execution_persona import ExecutionPersonaRepositoryImpl
from backend_v2.exceptions import ResourceNotFoundError
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.prompt_blocks import PersonaPromptBlock
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
def repo(mock_driver: AsyncMock) -> ExecutionPersonaRepositoryImpl:
    """Execution persona repository fixture."""
    return ExecutionPersonaRepositoryImpl(mock_driver)


@pytest.fixture
def sample_persona() -> PersonaPromptBlock:
    """Provides a valid PersonaPromptBlock instance."""
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
async def test_execution_persona_crud(
    repo: ExecutionPersonaRepositoryImpl, mock_driver: AsyncMock, sample_persona: PersonaPromptBlock
) -> None:
    """Positive: tests execution persona CRUD operations."""
    sample_doc = sample_persona.model_dump(mode="json")
    mock_driver.get.return_value = sample_doc
    mock_driver.query.return_value = [sample_doc]

    res = await repo.get_execution_persona_by_id("blk_1234567890abcdef")
    assert res is not None
    assert res.id == "blk_1234567890abcdef"

    all_res = await repo.get_all_execution_personas()
    assert len(all_res) == 1
    assert all_res[0].id == "blk_1234567890abcdef"

    assert await repo.create_execution_persona(sample_persona) == "blk_1234567890abcdef"
    assert await repo.update_execution_persona("blk_1234567890abcdef", sample_persona) == "blk_1234567890abcdef"
    assert await repo.delete_execution_persona("blk_1234567890abcdef") is True


@pytest.mark.asyncio
async def test_update_execution_persona_not_found(
    repo: ExecutionPersonaRepositoryImpl, mock_driver: AsyncMock, sample_persona: PersonaPromptBlock
) -> None:
    """Negative: update raises ResourceNotFoundError if persona not found."""
    mock_driver.get.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await repo.update_execution_persona("blk_0000000000000000", sample_persona)
