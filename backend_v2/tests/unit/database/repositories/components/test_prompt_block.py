"""Unit tests for PromptBlockRepositoryImpl."""

from __future__ import annotations

from pathlib import Path

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.components.prompt_block import PromptBlockRepositoryImpl
from backend_v2.database.tinydb_driver import TinyDBDriver
from backend_v2.database.wrapper import TinyDBClient
from backend_v2.exceptions import AppException
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.prompt_blocks import SystemRulePromptBlock
from backend_v2.models.enums import BlockDataType, PromptBlockCategory


@pytest.fixture
def driver(tmp_path: Path) -> StorageDriver:
    """Provides a real TinyDBDriver."""
    db_path = str(tmp_path / "test_pb.json")
    return TinyDBDriver(TinyDBClient(db_path))


@pytest.fixture
def repo(driver: StorageDriver) -> PromptBlockRepositoryImpl:
    """Provides a PromptBlockRepositoryImpl instance with the real TinyDB driver."""
    return PromptBlockRepositoryImpl(driver)


@pytest.fixture
def sample_system_rule() -> SystemRulePromptBlock:
    """Provides a valid SystemRulePromptBlock instance."""
    return SystemRulePromptBlock(
        id="blk_1234567890abcdef",
        slug="rule_clean",
        label=I18nText(translations={"en": "Rule", "fi": "Sääntö"}),
        description=I18nText(translations={"en": "Description", "fi": "Kuvaus"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
        type=BlockDataType.INSTRUCTION,
        instruction_text="Instruction.",
    )


@pytest.mark.asyncio
async def test_prompt_block_crud(repo: PromptBlockRepositoryImpl, sample_system_rule: SystemRulePromptBlock) -> None:
    """Test CRUD operations for PromptBlocks."""
    created_id = await repo.create_prompt_block(sample_system_rule)
    assert created_id == sample_system_rule.id

    model = await repo.get_prompt_block_by_id(sample_system_rule.id)
    assert model is not None
    assert model.id == sample_system_rule.id
    assert model.slug == "rule_clean"

    alias_model = await repo.get_prompt_block(sample_system_rule.id)
    assert alias_model is not None
    assert alias_model.id == sample_system_rule.id

    all_models = await repo.get_all_prompt_blocks()
    assert len(all_models) == 1
    assert all_models[0].id == sample_system_rule.id


@pytest.mark.asyncio
async def test_update_prompt_block(
    repo: PromptBlockRepositoryImpl, driver: StorageDriver, sample_system_rule: SystemRulePromptBlock
) -> None:
    """Test versioned update of PromptBlock with real version incrementation."""
    await repo.create_prompt_block(sample_system_rule)

    updated_rule = sample_system_rule.model_copy(update={"instruction_text": "Updated instruction."})
    res = await repo.update_prompt_block(sample_system_rule.id, updated_rule)
    assert res is True

    # Real AppendOnlyRepository version incrementation creates a new version record
    new_version_id = f"{sample_system_rule.id}_v2"
    persisted_raw = await driver.get("prompt_blocks", new_version_id)
    assert persisted_raw is not None
    assert persisted_raw["id"] == new_version_id
    assert persisted_raw["version"] == 2
    assert persisted_raw["is_latest"] is True


@pytest.mark.asyncio
async def test_update_prompt_block_not_found(
    repo: PromptBlockRepositoryImpl, sample_system_rule: SystemRulePromptBlock
) -> None:
    """Test updating non-existent PromptBlock."""
    res = await repo.update_prompt_block("pb1", sample_system_rule)
    assert res is False


@pytest.mark.asyncio
async def test_delete_prompt_block_blocked_by_usage(
    repo: PromptBlockRepositoryImpl, driver: StorageDriver, sample_system_rule: SystemRulePromptBlock
) -> None:
    """Test delete prompt block when blocked by step usage."""
    await repo.create_prompt_block(sample_system_rule)
    # Seed a step referencing this prompt block
    await driver.upsert("steps", {"id": "step1", "prompt_blocks": [sample_system_rule.id]}, "step1")

    with pytest.raises(AppException) as exc:
        await repo.delete_prompt_block(sample_system_rule.id, force_delete=False)

    assert exc.value.status_code == 400
    assert "delete blocked" in exc.value.message.lower()


@pytest.mark.asyncio
async def test_delete_prompt_block_success(
    repo: PromptBlockRepositoryImpl, sample_system_rule: SystemRulePromptBlock
) -> None:
    """Test successful delete prompt block."""
    await repo.create_prompt_block(sample_system_rule)
    assert await repo.delete_prompt_block(sample_system_rule.id) is True
    assert await repo.get_prompt_block_by_id(sample_system_rule.id) is None


@pytest.mark.asyncio
async def test_get_prompt_blocks_by_ids_success(repo: PromptBlockRepositoryImpl) -> None:
    """Test batch resolution of prompt blocks successfully returning hydrated models."""
    blk_1 = SystemRulePromptBlock(
        id="blk_1111111111111111",
        slug="block_1",
        category_id=PromptBlockCategory.SYSTEM_RULE,
        type=BlockDataType.INSTRUCTION,
        label=I18nText(translations={"en": "Rule 1"}),
        description=I18nText(translations={"en": "Desc 1"}),
        instruction_text="Rule 1 text",
    )
    blk_2 = SystemRulePromptBlock(
        id="blk_2222222222222222",
        slug="block_2",
        category_id=PromptBlockCategory.SYSTEM_RULE,
        type=BlockDataType.INSTRUCTION,
        label=I18nText(translations={"en": "Rule 2"}),
        description=I18nText(translations={"en": "Desc 2"}),
        instruction_text="Rule 2 text",
    )
    await repo.create_prompt_block(blk_1)
    await repo.create_prompt_block(blk_2)

    results = await repo.get_prompt_blocks_by_ids(["blk_1111111111111111", "blk_2222222222222222"])
    assert len(results) == 2
    assert results[0].id == "blk_1111111111111111"
    assert results[1].id == "blk_2222222222222222"


@pytest.mark.asyncio
async def test_get_prompt_blocks_by_ids_empty_list(repo: PromptBlockRepositoryImpl) -> None:
    """Test empty input list fast-path returns empty list with zero queries."""
    results = await repo.get_prompt_blocks_by_ids([])
    assert results == []


@pytest.mark.asyncio
async def test_get_prompt_blocks_by_ids_duplicate_input(
    repo: PromptBlockRepositoryImpl, sample_system_rule: SystemRulePromptBlock
) -> None:
    """Test duplicate IDs are deduplicated during resolution."""
    await repo.create_prompt_block(sample_system_rule)

    results = await repo.get_prompt_blocks_by_ids([sample_system_rule.id, sample_system_rule.id])
    assert len(results) == 1
    assert results[0].id == sample_system_rule.id


@pytest.mark.asyncio
async def test_get_prompt_blocks_by_ids_strict_missing_single_raises_app_exception(
    repo: PromptBlockRepositoryImpl, sample_system_rule: SystemRulePromptBlock
) -> None:
    """Test strict resolution raises AppException(404) when a single block ID is missing."""
    await repo.create_prompt_block(sample_system_rule)

    with pytest.raises(AppException) as exc_info:
        await repo.get_prompt_blocks_by_ids([sample_system_rule.id, "blk_missing_ghost"], strict=True)

    assert exc_info.value.status_code == 404
    assert "blk_missing_ghost" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_prompt_blocks_by_ids_strict_missing_all_raises_app_exception(
    repo: PromptBlockRepositoryImpl,
) -> None:
    """Test strict resolution raises AppException(404) when all block IDs are missing."""
    with pytest.raises(AppException) as exc_info:
        await repo.get_prompt_blocks_by_ids(["blk_ghost_1", "blk_ghost_2"], strict=True)

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_prompt_blocks_by_ids_non_strict_returns_partial(
    repo: PromptBlockRepositoryImpl, sample_system_rule: SystemRulePromptBlock
) -> None:
    """Test non-strict resolution returns partial found items without raising."""
    await repo.create_prompt_block(sample_system_rule)

    results = await repo.get_prompt_blocks_by_ids([sample_system_rule.id, "blk_missing"], strict=False)
    assert len(results) == 1
    assert results[0].id == sample_system_rule.id


@pytest.mark.asyncio
async def test_get_prompt_blocks_by_ids_malformed_raises_app_exception(
    repo: PromptBlockRepositoryImpl, driver: StorageDriver
) -> None:
    """Test get_prompt_blocks_by_ids raises AppException(500) if document fails Pydantic parsing."""
    await driver.upsert(
        "prompt_blocks", {"id": "blk_1111111111111111", "category_id": "invalid_category"}, "blk_1111111111111111"
    )

    with pytest.raises(AppException) as exc_info:
        await repo.get_prompt_blocks_by_ids(["blk_1111111111111111"])

    assert exc_info.value.status_code == 500
    assert "Failed to parse PromptBlock" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_all_prompt_blocks_models_success(
    repo: PromptBlockRepositoryImpl, sample_system_rule: SystemRulePromptBlock
) -> None:
    """Test get_all_prompt_blocks_models parses and returns all models."""
    await repo.create_prompt_block(sample_system_rule)

    results = await repo.get_all_prompt_blocks_models()
    assert len(results) == 1
    assert results[0].id == sample_system_rule.id


@pytest.mark.asyncio
async def test_get_all_prompt_blocks_models_malformed_raises_app_exception(
    repo: PromptBlockRepositoryImpl, driver: StorageDriver
) -> None:
    """Test get_all_prompt_blocks_models raises AppException(500) on malformed document."""
    await driver.upsert("prompt_blocks", {"id": "blk_bad", "category_id": "unknown"}, "blk_bad")

    with pytest.raises(AppException) as exc_info:
        await repo.get_all_prompt_blocks_models()

    assert exc_info.value.status_code == 500
    assert "Failed to parse PromptBlock" in exc_info.value.message


@pytest.mark.asyncio
async def test_delete_prompt_block_not_found(repo: PromptBlockRepositoryImpl) -> None:
    """Test delete_prompt_block returns False when document does not exist."""
    result = await repo.delete_prompt_block("blk_non_existent")
    assert result is False
