"""Tests for PromptBlockRepositoryImpl."""

from unittest.mock import AsyncMock, MagicMock
import pytest
from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.prompt_block import PromptBlockRepositoryImpl
from backend_v2.exceptions import AppException
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.v2_core import PromptBlock


@pytest.fixture
def mock_driver() -> AsyncMock:
    """Provides a mocked StorageDriver."""
    return AsyncMock(spec=StorageDriver)


@pytest.fixture
def repo(mock_driver: AsyncMock) -> PromptBlockRepositoryImpl:
    """Provides a PromptBlockRepositoryImpl instance."""
    return PromptBlockRepositoryImpl(mock_driver)


@pytest.mark.asyncio
async def test_prompt_block_crud(repo: PromptBlockRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test CRUD operations for PromptBlocks."""
    mock_driver.get.return_value = {"id": "pb1"}
    mock_driver.query.return_value = [{"id": "pb1"}]
    mock_driver.upsert.return_value = "pb1"

    assert await repo.get_prompt_block_by_id("pb1") == {"id": "pb1"}
    assert await repo.get_prompt_block("pb1") == {"id": "pb1"}
    assert await repo.get_all_prompt_blocks() == [{"id": "pb1"}]
    assert await repo.create_prompt_block({"id": "pb1"}) == "pb1"


@pytest.mark.asyncio
async def test_update_prompt_block(
    repo: PromptBlockRepositoryImpl, mock_driver: AsyncMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test versioned update of PromptBlock."""
    mock_driver.get.return_value = {"id": "pb1_v1", "version": 1}
    # Mock _increment_version
    repo._increment_version = MagicMock(return_value=("pb1", "pb1_v2", 2))  # type: ignore[method-assign]

    res = await repo.update_prompt_block("pb1_v1", {"foo": "bar"})
    assert res is True
    mock_driver.update.assert_called_with("prompt_blocks", "pb1_v1", {"is_latest": False})

    # Verify upsert call
    args, kwargs = mock_driver.upsert.call_args
    assert args[0] == "prompt_blocks"
    assert args[1]["id"] == "pb1_v2"
    assert args[1]["version"] == 2
    assert args[1]["foo"] == "bar"


@pytest.mark.asyncio
async def test_update_prompt_block_not_found(repo: PromptBlockRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test updating non-existent PromptBlock."""
    mock_driver.get.return_value = None
    res = await repo.update_prompt_block("pb1", {})
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
async def test_get_all_prompt_blocks_models_failure(repo: PromptBlockRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Test parsing failure for PromptBlock models."""
    mock_driver.query.return_value = [{"invalid": "data"}]
    with pytest.raises(AppException) as exc:
        await repo.get_all_prompt_blocks_models()
    assert exc.value.status_code == 500
