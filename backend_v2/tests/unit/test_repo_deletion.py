"""Unit tests for PromptBlockRepositoryImpl orphan-prevention deletion boundary."""

from __future__ import annotations

import pytest

from backend_v2.database.repositories.components.prompt_block import PromptBlockRepositoryImpl
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.domain.step import Step
from backend_v2.models.enums import CognitiveTier, EntityPrefix, StepType
from backend_v2.tests.factories.model_factories import I18nTextFactory, SystemRulePromptBlockFactory
from backend_v2.tests.fakes.in_memory_uow import InMemoryUnitOfWork


@pytest.mark.asyncio
async def test_delete_prompt_block_blocks_orphan_data_failure() -> None:
    """Verify Fail-Fast deletion boundary when a prompt block is referenced by a persisted Step."""
    base_uow = InMemoryUnitOfWork()
    repo = PromptBlockRepositoryImpl(uow_factory=lambda: InMemoryUnitOfWork(base_uow.store))

    block_id = generate_opaque_id(EntityPrefix.PROMPT_BLOCK)
    step_id = generate_opaque_id(EntityPrefix.STEP)

    block = SystemRulePromptBlockFactory.build(id=block_id)
    step = Step(
        organization_id="org_0195f3a0000070008000000000000001",
        id=step_id,
        slug="test_step_ref",
        name=I18nTextFactory.build(translations={"en": "Step 1", "fi": "Vaihe 1"}),
        type=StepType.LLM,
        cognitive_tier=CognitiveTier.FAST,
        role_block_id=None,
        extraction_protocol_block_id=block_id,
        criteria_block_ids=[block_id],
        pre_hooks=[],
        post_hooks=[],
        allowed_mcp_tools=[],
        mcp_tool_params={},
        expected_inputs=[],
    )

    async with InMemoryUnitOfWork(base_uow.store) as uow:
        await uow.entities.upsert_prompt_block(block)
        await uow.entities.upsert_step(step)

    with pytest.raises(AppException) as exc_info:
        await repo.delete_prompt_block(block_id)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == str(ErrorCodes.DELETE_BLOCKED_BY_USAGE.value)
    assert block_id in exc_info.value.message
    assert "referenced by a persisted step" in exc_info.value.message

    async with InMemoryUnitOfWork(base_uow.store) as uow:
        await uow.entities.delete_step(step_id)

    assert await repo.delete_prompt_block(block_id) is True
    assert await repo.get_prompt_block_by_id(block_id) is None
