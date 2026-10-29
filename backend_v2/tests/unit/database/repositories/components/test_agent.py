"""Tests for AgentRepositoryImpl."""

from __future__ import annotations

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.postgres.storage_driver import PostgresStorageDriver
from backend_v2.database.repositories.components.agent import AgentRepositoryImpl
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.prompt_blocks import PersonaPromptBlock
from backend_v2.models.enums import BlockDataType, PromptBlockCategory


@pytest.fixture
def driver() -> StorageDriver:
    """Provides a PostgresStorageDriver instance."""
    return PostgresStorageDriver(auto_initialize_pool=False)


@pytest.fixture
def repo(driver: StorageDriver) -> AgentRepositoryImpl:
    """Provides an AgentRepositoryImpl instance with the real TinyDB driver."""
    return AgentRepositoryImpl(driver)


@pytest.fixture
def sample_agent() -> PersonaPromptBlock:
    """Provides a valid PersonaPromptBlock instance."""
    return PersonaPromptBlock(
        id="blk_0195f3a0000070018234567890abcdef",
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


@pytest.mark.asyncio
async def test_get_agent_by_id_malformed_raises_app_exception(repo: AgentRepositoryImpl, driver: StorageDriver) -> None:
    """Test get_agent_by_id raises AppException(500) when stored document fails validation."""
    await driver.upsert(
        "agents",
        {"id": "blk_0195f3a0000070018111111111111111", "category_id": "invalid_category"},
        "blk_0195f3a0000070018111111111111111",
    )

    with pytest.raises(AppException) as exc_info:
        await repo.get_agent_by_id("blk_0195f3a0000070018111111111111111")

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "blk_0195f3a0000070018111111111111111" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_all_agents_malformed_with_id_raises_app_exception(
    repo: AgentRepositoryImpl, driver: StorageDriver
) -> None:
    """Test get_all_agents raises AppException(500) when a document with ID fails validation."""
    await driver.upsert(
        "agents",
        {"id": "blk_0195f3a0000070028222222222222222", "category_id": "invalid_category"},
        "blk_0195f3a0000070028222222222222222",
    )

    with pytest.raises(AppException) as exc_info:
        await repo.get_all_agents()

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "blk_0195f3a0000070028222222222222222" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_all_agents_malformed_without_id_raises_app_exception(
    repo: AgentRepositoryImpl,
    driver: StorageDriver,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test get_all_agents raises AppException(500) with 'unknown' when malformed doc lacks id."""

    async def _query_corrupted(collection: str, *args: object, **kwargs: object) -> list[dict[str, str]]:
        return [{"category_id": "invalid_category"}]

    monkeypatch.setattr(driver, "query", _query_corrupted)

    with pytest.raises(AppException) as exc_info:
        await repo.get_all_agents()

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "unknown" in exc_info.value.message


@pytest.mark.asyncio
async def test_update_agent_not_found_returns_false(
    repo: AgentRepositoryImpl, sample_agent: PersonaPromptBlock
) -> None:
    """Test update_agent returns False when target agent ID does not exist."""
    res = await repo.update_agent("blk_0195f3a0000070008000000000000000", sample_agent)
    assert res is False


@pytest.mark.asyncio
async def test_delete_agent_not_found_returns_false(repo: AgentRepositoryImpl) -> None:
    """Test delete_agent returns False when target agent ID does not exist."""
    res = await repo.delete_agent("blk_0195f3a0000070008000000000000000")
    assert res is False
