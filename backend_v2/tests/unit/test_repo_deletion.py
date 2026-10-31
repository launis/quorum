from __future__ import annotations

import pytest

from backend_v2.database.postgres.storage_driver import PostgresStorageDriver
from backend_v2.database.repositories.components.prompt_block import PromptBlockRepositoryImpl
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.step import Step
from backend_v2.models.enums import CognitiveTier, StepType
from backend_v2.tests.factories import SystemRulePromptBlockFactory


@pytest.fixture
def driver() -> PostgresStorageDriver:
    """Provides a PostgresStorageDriver instance."""
    return PostgresStorageDriver(auto_initialize_pool=False)


@pytest.mark.asyncio
async def test_delete_prompt_block_blocks_orphan_data(driver: PostgresStorageDriver) -> None:
    """Positive: tests Fail-Fast deletion boundary when prompt block is used by a Step."""
    repo = PromptBlockRepositoryImpl(driver=driver)

    block_id = "blk_0195f3a0000070008000000000000001"
    step_id = "stp_0195f3a0000070008000000000000001"

    block = SystemRulePromptBlockFactory.build(id=block_id)
    step = Step(
        id=step_id,
        slug="test_step_ref",
        name=I18nText(translations={"en": "Step 1", "fi": "Vaihe 1"}),
        type=StepType.LLM,
        cognitive_tier=CognitiveTier.FAST,
        role_block_id=None,
        extraction_protocol_block_id=block_id,
        criteria_block_ids=[block_id],
    )

    # Seed block and referencing step in storage
    await driver.upsert("prompt_blocks", block.model_dump(mode="json"), block_id)
    await driver.upsert("steps", step.model_dump(mode="json"), step_id)

    # Should raise AppException with RESOURCE_IN_USE / DELETE_BLOCKED_BY_USAGE
    with pytest.raises(AppException) as exc_info:
        await repo.delete_prompt_block(block_id)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == str(ErrorCodes.DELETE_BLOCKED_BY_USAGE.value)
    assert "PromptBlock delete blocked by step" in exc_info.value.message

    # Force delete should work by bypassing validation
    assert await repo.delete_prompt_block(block_id, force_delete=True) is True
    assert await driver.get("prompt_blocks", block_id) is None
