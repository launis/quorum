"""Tests for AgentRepositoryImpl."""

from __future__ import annotations

from pathlib import Path

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.components.agent import AgentRepositoryImpl
from backend_v2.database.tinydb_driver import TinyDBDriver
from backend_v2.database.wrapper import TinyDBClient
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.prompt_blocks import PersonaPromptBlock
from backend_v2.models.enums import BlockDataType, PromptBlockCategory


@pytest.fixture
def driver(tmp_path: Path) -> StorageDriver:
    """Provides a real TinyDBDriver."""
    db_path = str(tmp_path / "test_agent.json")
    return TinyDBDriver(TinyDBClient(db_path))


@pytest.fixture
def repo(driver: StorageDriver) -> AgentRepositoryImpl:
    """Provides an AgentRepositoryImpl instance with the real TinyDB driver."""
    return AgentRepositoryImpl(driver)


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
async def test_agent_crud(repo: AgentRepositoryImpl, sample_agent: PersonaPromptBlock) -> None:
    """Test CRUD operations for Agents with real stateful persistence."""
    created_id = await repo.create_agent(sample_agent)
    assert created_id == sample_agent.id

    agent = await repo.get_agent_by_id(sample_agent.id)
    assert agent is not None
    assert agent.id == sample_agent.id
    assert agent.slug == sample_agent.slug

    all_agents = await repo.get_all_agents()
    assert len(all_agents) == 1
    assert all_agents[0].id == sample_agent.id

    assert await repo.delete_agent(sample_agent.id) is True
    assert await repo.get_agent_by_id(sample_agent.id) is None
    assert len(await repo.get_all_agents()) == 0


@pytest.mark.asyncio
async def test_update_agent(repo: AgentRepositoryImpl, driver: StorageDriver, sample_agent: PersonaPromptBlock) -> None:
    """Test versioned update of Agent with real version incrementation."""
    await repo.create_agent(sample_agent)

    updated_agent = sample_agent.model_copy(update={"role_enforcement": "Updated strict coach."})
    res = await repo.update_agent(sample_agent.id, updated_agent)
    assert res is True

    # Real AppendOnlyRepository version incrementation creates a new version record in TinyDB
    new_version_id = f"{sample_agent.id}_v2"
    persisted_raw = await driver.get("agents", new_version_id)
    assert persisted_raw is not None
    assert persisted_raw["id"] == new_version_id
    assert persisted_raw["version"] == 2
    assert persisted_raw["is_latest"] is True
