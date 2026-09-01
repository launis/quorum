"""Unit tests for PromptBlockRepositoryImpl."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.components.prompt_block import PromptBlockRepositoryImpl
from backend_v2.exceptions import AppException
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.prompt_blocks import SystemRulePromptBlock
from backend_v2.models.enums import BlockDataType, PromptBlockCategory


@pytest.fixture
def mock_driver() -> AsyncMock:
    """Provides a mocked StorageDriver."""
    return AsyncMock(spec=StorageDriver)


@pytest.fixture
def repo(mock_driver: AsyncMock) -> PromptBlockRepositoryImpl:
    """Provides a PromptBlockRepositoryImpl instance with the mocked driver."""
    return PromptBlockRepositoryImpl(mock_driver)


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
async def test_prompt_block_crud(
    repo: PromptBlockRepositoryImpl, mock_driver: AsyncMock, sample_system_rule: SystemRulePromptBlock
) -> None:
    """Test CRUD operations for PromptBlocks."""
    sample_doc = sample_system_rule.model_dump(mode="json")
    mock_driver.get.return_value = sample_doc
    mock_driver.query.return_value = [sample_doc]
    mock_driver.upsert.return_value = "blk_1234567890abcdef"

    model = await repo.get_prompt_block_by_id("blk_1234567890abcdef")
    assert model is not None
    assert model.id == "blk_1234567890abcdef"
    assert model.slug == "rule_clean"

    alias_model = await repo.get_prompt_block("blk_1234567890abcdef")
    assert alias_model is not None
    assert alias_model.id == "blk_1234567890abcdef"

    all_models = await repo.get_all_prompt_blocks()
    assert len(all_models) == 1
    assert all_models[0].id == "blk_1234567890abcdef"

    assert await repo.create_prompt_block(sample_system_rule) == "blk_1234567890abcdef"


@pytest.mark.asyncio
async def test_update_prompt_block(
    repo: PromptBlockRepositoryImpl, mock_driver: AsyncMock, sample_system_rule: SystemRulePromptBlock
) -> None:
    """Test versioned update of PromptBlock."""
    doc_with_version = sample_system_rule.model_dump(mode="json")
    doc_with_version["version"] = 1
    mock_driver.get.return_value = doc_with_version
    repo._increment_version = MagicMock(return_value=("rule_clean", "blk_1234567890abcdef_v2", 2))  # type: ignore[method-assign]

    res = await repo.update_prompt_block("blk_1234567890abcdef", sample_system_rule)
    assert res is True
    mock_driver.update.assert_called_with("prompt_blocks", "blk_1234567890abcdef", {"is_latest": False})
    mock_driver.upsert.assert_called()


@pytest.mark.asyncio
async def test_update_prompt_block_not_found(
    repo: PromptBlockRepositoryImpl, mock_driver: AsyncMock, sample_system_rule: SystemRulePromptBlock
) -> None:
    """Test updating non-existent PromptBlock."""
    mock_driver.get.return_value = None
    res = await repo.update_prompt_block("pb1", sample_system_rule)
    assert res is False


@pytest.mark.asyncio
async def test_delete_prompt_block_blocked_by_usage(repo: PromptBlockRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test delete prompt block when blocked by step usage."""
    mock_driver.get.return_value = {"id": "pb1"}
    mock_driver.query.return_value = [{"id": "step1", "prompt_blocks": ["pb1"]}]

    with pytest.raises(AppException) as exc:
        await repo.delete_prompt_block("pb1", force_delete=False)

    assert exc.value.status_code == 400
    assert "delete blocked" in exc.value.message.lower()


@pytest.mark.asyncio
async def test_delete_prompt_block_success(repo: PromptBlockRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test successful delete prompt block."""
    mock_driver.get.return_value = {"id": "pb1"}
    mock_driver.query.return_value = [{"id": "step1", "prompt_blocks": ["pb2"]}]
    mock_driver.delete.return_value = True

    assert await repo.delete_prompt_block("pb1") is True


@pytest.mark.asyncio
async def test_get_prompt_blocks_by_ids_success(repo: PromptBlockRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test batch resolution of prompt blocks successfully returning hydrated models."""
    blk_1_data = {
        "id": "blk_1111111111111111",
        "slug": "block_1",
        "category_id": "system_rule",
        "type": "instruction",
        "label": {"translations": {"en": "Rule 1"}},
        "description": {"translations": {"en": "Desc 1"}},
    }
    blk_2_data = {
        "id": "blk_2222222222222222",
        "slug": "block_2",
        "category_id": "system_rule",
        "type": "instruction",
        "label": {"translations": {"en": "Rule 2"}},
        "description": {"translations": {"en": "Desc 2"}},
    }

    async def mock_get(collection: str, doc_id: str) -> dict[str, Any] | None:
        if doc_id == "blk_1111111111111111":
            return blk_1_data
        if doc_id == "blk_2222222222222222":
            return blk_2_data
        return None

    mock_driver.get.side_effect = mock_get

    results = await repo.get_prompt_blocks_by_ids(["blk_1111111111111111", "blk_2222222222222222"])
    assert len(results) == 2
    assert results[0].id == "blk_1111111111111111"
    assert results[1].id == "blk_2222222222222222"


@pytest.mark.asyncio
async def test_get_prompt_blocks_by_ids_empty_list(repo: PromptBlockRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test empty input list fast-path returns empty list with zero queries."""
    results = await repo.get_prompt_blocks_by_ids([])
    assert results == []
    mock_driver.get.assert_not_called()


@pytest.mark.asyncio
async def test_get_prompt_blocks_by_ids_duplicate_input(
    repo: PromptBlockRepositoryImpl, mock_driver: AsyncMock
) -> None:
    """Test duplicate IDs are deduplicated during resolution."""
    blk_1_data = {
        "id": "blk_1111111111111111",
        "slug": "block_1",
        "category_id": "system_rule",
        "type": "instruction",
        "label": {"translations": {"en": "Rule 1"}},
        "description": {"translations": {"en": "Desc 1"}},
    }
    mock_driver.get.return_value = blk_1_data

    results = await repo.get_prompt_blocks_by_ids(["blk_1111111111111111", "blk_1111111111111111"])
    assert len(results) == 1
    assert results[0].id == "blk_1111111111111111"
    assert mock_driver.get.call_count == 1


@pytest.mark.asyncio
async def test_get_prompt_blocks_by_ids_strict_missing_single_raises_app_exception(
    repo: PromptBlockRepositoryImpl, mock_driver: AsyncMock
) -> None:
    """Test strict resolution raises AppException(404) when a single block ID is missing."""
    blk_1_data = {
        "id": "blk_1111111111111111",
        "slug": "block_1",
        "category_id": "system_rule",
        "type": "instruction",
        "label": {"translations": {"en": "Rule 1"}},
        "description": {"translations": {"en": "Desc 1"}},
    }

    async def mock_get(collection: str, doc_id: str) -> dict[str, Any] | None:
        if doc_id == "blk_1111111111111111":
            return blk_1_data
        return None

    mock_driver.get.side_effect = mock_get

    with pytest.raises(AppException) as exc_info:
        await repo.get_prompt_blocks_by_ids(["blk_1111111111111111", "blk_missing_ghost"], strict=True)

    assert exc_info.value.status_code == 404
    assert "blk_missing_ghost" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_prompt_blocks_by_ids_strict_missing_all_raises_app_exception(
    repo: PromptBlockRepositoryImpl, mock_driver: AsyncMock
) -> None:
    """Test strict resolution raises AppException(404) when all block IDs are missing."""
    mock_driver.get.return_value = None

    with pytest.raises(AppException) as exc_info:
        await repo.get_prompt_blocks_by_ids(["blk_ghost_1", "blk_ghost_2"], strict=True)

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_prompt_blocks_by_ids_non_strict_returns_partial(
    repo: PromptBlockRepositoryImpl, mock_driver: AsyncMock
) -> None:
    """Test non-strict resolution returns partial found items without raising."""
    blk_1_data = {
        "id": "blk_1111111111111111",
        "slug": "block_1",
        "category_id": "system_rule",
        "type": "instruction",
        "label": {"translations": {"en": "Rule 1"}},
        "description": {"translations": {"en": "Desc 1"}},
    }

    async def mock_get(collection: str, doc_id: str) -> dict[str, Any] | None:
        if doc_id == "blk_1111111111111111":
            return blk_1_data
        return None

    mock_driver.get.side_effect = mock_get

    results = await repo.get_prompt_blocks_by_ids(["blk_1111111111111111", "blk_missing"], strict=False)
    assert len(results) == 1
    assert results[0].id == "blk_1111111111111111"


@pytest.mark.asyncio
async def test_get_prompt_blocks_by_ids_malformed_raises_app_exception(
    repo: PromptBlockRepositoryImpl, mock_driver: AsyncMock
) -> None:
    """Test get_prompt_blocks_by_ids raises AppException(500) if document fails Pydantic parsing."""
    mock_driver.get.return_value = {"id": "blk_1111111111111111", "category_id": "invalid_category"}

    with pytest.raises(AppException) as exc_info:
        await repo.get_prompt_blocks_by_ids(["blk_1111111111111111"])

    assert exc_info.value.status_code == 500
    assert "Failed to parse PromptBlock" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_all_prompt_blocks_models_success(repo: PromptBlockRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test get_all_prompt_blocks_models parses and returns all models."""
    blk_1_data = {
        "id": "blk_1111111111111111",
        "slug": "block_1",
        "category_id": "system_rule",
        "type": "instruction",
        "label": {"translations": {"en": "Rule 1"}},
        "description": {"translations": {"en": "Desc 1"}},
    }
    mock_driver.query.return_value = [blk_1_data]

    results = await repo.get_all_prompt_blocks_models()
    assert len(results) == 1
    assert results[0].id == "blk_1111111111111111"


@pytest.mark.asyncio
async def test_get_all_prompt_blocks_models_malformed_raises_app_exception(
    repo: PromptBlockRepositoryImpl, mock_driver: AsyncMock
) -> None:
    """Test get_all_prompt_blocks_models raises AppException(500) on malformed document."""
    mock_driver.query.return_value = [{"id": "blk_bad", "category_id": "unknown"}]

    with pytest.raises(AppException) as exc_info:
        await repo.get_all_prompt_blocks_models()

    assert exc_info.value.status_code == 500
    assert "Failed to parse PromptBlock" in exc_info.value.message


@pytest.mark.asyncio
async def test_delete_prompt_block_not_found(repo: PromptBlockRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test delete_prompt_block returns False when document does not exist."""
    mock_driver.get.return_value = None

    result = await repo.delete_prompt_block("blk_non_existent")
    assert result is False
