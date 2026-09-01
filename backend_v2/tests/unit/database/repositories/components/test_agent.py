"""Tests for AgentRepositoryImpl."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.components.agent import AgentRepositoryImpl
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.prompt_blocks import PersonaPromptBlock
from backend_v2.models.enums import BlockDataType, PromptBlockCategory


@pytest.fixture
def mock_driver() -> AsyncMock:
    """Provides a mocked StorageDriver."""
    return AsyncMock(spec=StorageDriver)


@pytest.fixture
def repo(mock_driver: AsyncMock) -> AgentRepositoryImpl:
    """Provides an AgentRepositoryImpl instance with the mocked driver."""
    return AgentRepositoryImpl(mock_driver)


@pytest.fixture
def sample_agent() -> PersonaPromptBlock:
    """Provides a valid PersonaPromptBlock instance."""
    return PersonaPromptBlock(
        id="blk_1234567890abcdef",
        slug="agent_1",
        label=I18nText(translations={"en": "Test Agent", "fi": "Testiagentti"}),
        description=I18nText(translations={"en": "Description", "fi": "Kuvaus"}),
        category_id=PromptBlockCategory.EXECUTION_PERSONA,
        type=BlockDataType.INSTRUCTION,
        role_enforcement="Strict coach.",
    )


@pytest.mark.asyncio
async def test_agent_crud(repo: AgentRepositoryImpl, mock_driver: AsyncMock, sample_agent: PersonaPromptBlock) -> None:
    """Test CRUD operations for Agents."""
    mock_driver.get.return_value = sample_agent.model_dump(mode="json")
    mock_driver.query.return_value = [sample_agent.model_dump(mode="json")]
    mock_driver.upsert.return_value = "blk_1234567890abcdef"
    mock_driver.delete.return_value = True

    agent = await repo.get_agent_by_id("blk_1234567890abcdef")
    assert agent is not None
    assert agent.id == "blk_1234567890abcdef"

    all_agents = await repo.get_all_agents()
    assert len(all_agents) == 1
    assert all_agents[0].id == "blk_1234567890abcdef"

    assert await repo.create_agent(sample_agent) == "blk_1234567890abcdef"
    assert await repo.delete_agent("blk_1234567890abcdef") is True


@pytest.mark.asyncio
async def test_update_agent(
    repo: AgentRepositoryImpl, mock_driver: AsyncMock, sample_agent: PersonaPromptBlock
) -> None:
    """Test versioned update of Agent."""
    mock_driver.get.return_value = sample_agent.model_dump(mode="json")
    repo._increment_version = MagicMock(return_value=("blk_agent_1", "blk_agent_1_v2", 2))  # type: ignore[method-assign]
    res = await repo.update_agent("blk_1234567890abcdef", sample_agent)
    assert res is True
    mock_driver.upsert.assert_called()
