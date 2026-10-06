from __future__ import annotations

from pathlib import Path

import pytest

from backend_v2.database.repositories.components.prompt_block import PromptBlockRepositoryImpl
from backend_v2.database.tinydb_driver import TinyDBDriver
from backend_v2.database.wrapper import TinyDBClient
from backend_v2.exceptions import AppException, ErrorCodes


@pytest.fixture
def driver(tmp_path: Path) -> TinyDBDriver:
    """Provides a real TinyDBDriver over ephemeral tmp_path."""
    db_path = str(tmp_path / "test_repo_deletion.json")
    return TinyDBDriver(TinyDBClient(db_path))


@pytest.mark.asyncio
async def test_delete_prompt_block_blocks_orphan_data(driver: TinyDBDriver) -> None:
    """Positive: tests Fail-Fast deletion boundary when prompt block is used by a Step."""
    repo = PromptBlockRepositoryImpl(driver=driver)

    block_id = "blk_0000000000000001"
    step_id = "stp_0000000000000001"

    # Seed block and referencing step in physical storage
    await driver.upsert("prompt_blocks", {"id": block_id, "name": "block1"}, block_id)
    await driver.upsert("steps", {"id": step_id, "prompt_blocks": [block_id]}, step_id)

    # Should raise AppException with RESOURCE_IN_USE / DELETE_BLOCKED_BY_USAGE
    with pytest.raises(AppException) as exc_info:
        await repo.delete_prompt_block(block_id)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == str(ErrorCodes.DELETE_BLOCKED_BY_USAGE.value)
    assert "PromptBlock delete blocked by step usage" in exc_info.value.message

    # Force delete should work by bypassing validation
    assert await repo.delete_prompt_block(block_id, force_delete=True) is True
    assert await driver.get("prompt_blocks", block_id) is None
