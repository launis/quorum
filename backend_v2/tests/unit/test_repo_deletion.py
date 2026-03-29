from typing import Any
from unittest.mock import AsyncMock

import pytest

from backend_v2.database.repository import UnifiedWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes


@pytest.fixture
def mock_driver() -> Any:
    driver = AsyncMock()
    return driver


@pytest.mark.asyncio
# Test for Fail-Fast deletion boundary
async def test_delete_prompt_block_blocks_orphan_data(mock_driver: Any) -> None:
    repo = UnifiedWorkflowRepository(driver=mock_driver)

    # Mock get_prompt_block_by_id to simulate the block exists
    repo.get_prompt_block_by_id = AsyncMock(return_value={"id": "m1"})  # type: ignore

    # Mock get_all_steps to simulate it is used in a Step
    repo.get_all_steps = AsyncMock(return_value=[{"id": "step_1", "prompt_blocks": ["m1", "m2"]}])  # type: ignore

    # Should raise AppException with RESOURCE_IN_USE
    with pytest.raises(AppException) as exc_info:
        await repo.delete_prompt_block("m1")

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == str(ErrorCodes.DELETE_BLOCKED_BY_USAGE.value)
    assert "PromptBlock delete blocked by step usage" in exc_info.value.message

    # Force delete should work by bypassing validation
    await repo.delete_prompt_block("m1", force_delete=True)
    mock_driver.delete.assert_called_with("prompt_blocks", "m1")
