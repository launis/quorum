"""Unit tests for PromptBlockRepositoryImpl over EntityPersistencePort."""

from __future__ import annotations

import pytest

from backend_v2.database.postgres.pool import PostgresPoolManager
from backend_v2.database.postgres.uow import PostgresUnitOfWork
from backend_v2.database.repositories.components.prompt_block import PromptBlockRepositoryImpl
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.prompt_blocks import SystemRulePromptBlock
from backend_v2.models.domain.step import Step
from backend_v2.models.enums import (
    BlockDataType,
    CognitiveTier,
    PromptBlockCategory,
    StepType,
    StorageBackend,
)
from backend_v2.settings import Settings
from backend_v2.tests.factories.model_factories import (
    I18nTextFactory,
    SystemRulePromptBlockFactory,
)
from backend_v2.tests.fakes.in_memory_uow import InMemoryAsyncPgPool, InMemoryUnitOfWork

_BLK_ID = "blk_0195f3a0000070018234567890abcdef"
_BLK_ID_1 = "blk_0195f3a0000070018111111111111111"
_BLK_ID_2 = "blk_0195f3a0000070028222222222222222"
_BLK_PROT_ID = "blk_0195f3a0000070008000000000000002"
_BLK_MISSING_1 = "blk_0195f3a0000070008000000000000091"
_BLK_MISSING_2 = "blk_0195f3a0000070008000000000000092"
_STP_ID = "stp_0195f3a0000070008000000000000001"


@pytest.fixture
def base_uow() -> InMemoryUnitOfWork:
    """Provide a shared InMemoryUnitOfWork backing store."""
    return InMemoryUnitOfWork()


@pytest.fixture
def repo(base_uow: InMemoryUnitOfWork) -> PromptBlockRepositoryImpl:
    """Provide a PromptBlockRepositoryImpl backed by the stateful InMemoryUnitOfWork store."""
    return PromptBlockRepositoryImpl(uow_factory=lambda: InMemoryUnitOfWork(base_uow.store))


@pytest.fixture
def sample_system_rule() -> SystemRulePromptBlock:
    """Provide a valid SystemRulePromptBlock instance via Polyfactory."""
    return SystemRulePromptBlockFactory.build(
        id=_BLK_ID,
        slug="rule_clean",
        label=I18nTextFactory.build(translations={"en": "Rule", "fi": "Rule FI"}),
        description=I18nTextFactory.build(translations={"en": "Description", "fi": "Description FI"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
        type=BlockDataType.INSTRUCTION,
        instruction_text="Instruction.",
    )


@pytest.mark.asyncio
async def test_prompt_block_crud_and_in_place_update(
    repo: PromptBlockRepositoryImpl,
    sample_system_rule: SystemRulePromptBlock,
) -> None:
    """Positive: verify CRUD operations and in-place primary-ID preservation on update."""
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

    all_models_alias = await repo.get_all_prompt_blocks_models()
    assert len(all_models_alias) == 1

    updated_rule = sample_system_rule.model_copy(update={"id": _BLK_ID_2, "instruction_text": "Updated instruction."})
    res = await repo.update_prompt_block(sample_system_rule.id, updated_rule)
    assert res is True

    persisted = await repo.get_prompt_block_by_id(sample_system_rule.id)
    assert isinstance(persisted, SystemRulePromptBlock)
    assert persisted.id == sample_system_rule.id
    assert persisted.instruction_text == "Updated instruction."


@pytest.mark.asyncio
async def test_update_prompt_block_not_found(
    repo: PromptBlockRepositoryImpl,
    sample_system_rule: SystemRulePromptBlock,
) -> None:
    """Negative: update_prompt_block returns False when target block does not exist."""
    assert await repo.update_prompt_block(_BLK_MISSING_1, sample_system_rule) is False


@pytest.mark.asyncio
async def test_delete_prompt_block_blocked_by_usage_and_force_delete(
    repo: PromptBlockRepositoryImpl,
    base_uow: InMemoryUnitOfWork,
    sample_system_rule: SystemRulePromptBlock,
) -> None:
    """Negative & Positive: delete_prompt_block blocks on Step reference unless force_delete is True."""
    await repo.create_prompt_block(sample_system_rule)
    step = Step(
        id=_STP_ID,
        slug="test_step_usage",
        name=I18nTextFactory.build(translations={"en": "Test Step", "fi": "Test Step FI"}),
        type=StepType.LLM,
        cognitive_tier=CognitiveTier.FAST,
        extraction_protocol_block_id=_BLK_PROT_ID,
        criteria_block_ids=[sample_system_rule.id],
        pre_hooks=[],
        post_hooks=[],
        allowed_mcp_tools=[],
        mcp_tool_params={},
        expected_inputs=[],
    )
    async with InMemoryUnitOfWork(base_uow.store) as uow:
        await uow.entities.upsert_step(step)

    with pytest.raises(AppException) as exc:
        await repo.delete_prompt_block(sample_system_rule.id, force_delete=False)

    assert exc.value.status_code == 400
    assert exc.value.details["error_code"] == ErrorCodes.DELETE_BLOCKED_BY_USAGE.value

    assert await repo.delete_prompt_block(sample_system_rule.id, force_delete=True) is True
    assert await repo.get_prompt_block_by_id(sample_system_rule.id) is None


@pytest.mark.asyncio
async def test_delete_prompt_block_success_and_not_found(
    repo: PromptBlockRepositoryImpl,
    sample_system_rule: SystemRulePromptBlock,
) -> None:
    """Positive & Negative: delete_prompt_block deletes unreferenced block and returns False when missing."""
    assert await repo.delete_prompt_block(_BLK_MISSING_1) is False
    await repo.create_prompt_block(sample_system_rule)
    assert await repo.delete_prompt_block(sample_system_rule.id) is True
    assert await repo.get_prompt_block_by_id(sample_system_rule.id) is None


@pytest.mark.asyncio
async def test_get_prompt_blocks_by_ids_resolution_modes(
    repo: PromptBlockRepositoryImpl,
    sample_system_rule: SystemRulePromptBlock,
) -> None:
    """Verify batch resolution order, empty fast-path, deduplication, strict 404, and non-strict partial return."""
    assert await repo.get_prompt_blocks_by_ids([]) == []

    blk_1 = SystemRulePromptBlockFactory.build(id=_BLK_ID_1, slug="block_1")
    blk_2 = SystemRulePromptBlockFactory.build(id=_BLK_ID_2, slug="block_2")
    await repo.create_prompt_block(blk_1)
    await repo.create_prompt_block(blk_2)
    await repo.create_prompt_block(sample_system_rule)

    ordered = await repo.get_prompt_blocks_by_ids([_BLK_ID_2, _BLK_ID_1])
    assert [b.id for b in ordered] == [_BLK_ID_2, _BLK_ID_1]

    deduped = await repo.get_prompt_blocks_by_ids([sample_system_rule.id, sample_system_rule.id])
    assert len(deduped) == 1
    assert deduped[0].id == sample_system_rule.id

    partial = await repo.get_prompt_blocks_by_ids([sample_system_rule.id, _BLK_MISSING_1], strict=False)
    assert len(partial) == 1
    assert partial[0].id == sample_system_rule.id

    with pytest.raises(AppException) as single_exc:
        await repo.get_prompt_blocks_by_ids([sample_system_rule.id, _BLK_MISSING_1], strict=True)
    assert single_exc.value.status_code == 404
    assert _BLK_MISSING_1 in single_exc.value.message

    with pytest.raises(AppException) as all_exc:
        await repo.get_prompt_blocks_by_ids([_BLK_MISSING_1, _BLK_MISSING_2], strict=True)
    assert all_exc.value.status_code == 404


@pytest.mark.asyncio
async def test_prompt_block_invalid_prefix_and_storage_fault_failure() -> None:
    """Negative: invalid ID prefix raises VALIDATION_FAILED and SQL fault raises STORAGE_ACCESS_FAILED."""
    pool = InMemoryAsyncPgPool()
    settings = Settings(
        storage_backend=StorageBackend.POSTGRES,
        postgres_host="db.internal",
        postgres_port=5432,
        postgres_user="quorum",
        postgres_db="quorum",
        postgres_command_timeout_seconds=5.0,
    )
    pool_mgr = PostgresPoolManager(settings=settings, pool=pool)
    pg_repo = PromptBlockRepositoryImpl(uow_factory=lambda: PostgresUnitOfWork(pool_mgr))

    with pytest.raises(AppException) as invalid_exc:
        await pg_repo.get_prompt_block_by_id(_STP_ID)
    assert invalid_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    try:
        pool.inject_fault("fetch", RuntimeError("simulated list failure"))
        with pytest.raises(AppException) as fault_exc:
            await pg_repo.get_all_prompt_blocks()
        assert fault_exc.value.status_code == 500
        assert fault_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
    finally:
        pool.clear_faults()
