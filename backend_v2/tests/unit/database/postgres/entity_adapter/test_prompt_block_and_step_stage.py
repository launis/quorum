"""Unit and boundary tests for PostgreSQL 19 PromptBlock and Step entity stage.

Covers positive roundtrip persistence and hydration for all four AnyPromptBlock
discriminated union variants (MatrixPromptBlock, PersonaPromptBlock,
ProtocolPromptBlock, SystemRulePromptBlock) and Step, plus negative identifier
validation and driver fault handling.
"""

from __future__ import annotations

import pytest

from backend_v2.database.postgres.entity_adapter.prompt_block_and_step_stage import (
    get_prompt_block_row,
    get_step_row,
    hydrate_prompt_block_row,
    hydrate_step_row,
    upsert_prompt_block_row,
    upsert_step_row,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText, generate_opaque_id
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PersonaPromptBlock,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.domain.step import Step
from backend_v2.models.enums import (
    BlockDataType,
    CognitiveTier,
    EngineType,
    EntityPrefix,
    PromptBlockCategory,
    StepType,
    StepZone,
)
from backend_v2.tests.factories.model_factories import (
    MatrixPromptBlockFactory,
    SystemRulePromptBlockFactory,
)
from backend_v2.tests.fakes.in_memory_uow import InMemoryAsyncPgPool

_TIMEOUT: float = 5.0


def _build_persona_block(category: PromptBlockCategory) -> PersonaPromptBlock:
    """Build a valid PersonaPromptBlock for testing.

    Args:
        category: EXECUTION_PERSONA or AGENT_ROLE category.

    Returns:
        Validated PersonaPromptBlock instance.
    """
    return PersonaPromptBlock(
        id=generate_opaque_id(EntityPrefix.PROMPT_BLOCK),
        slug=f"persona_{category.value}",
        organization_id=generate_opaque_id(EntityPrefix.ORGANIZATION),
        label=I18nText(translations={"en": "Persona Label", "fi": "Persoonan Nimike"}),
        description=I18nText(translations={"en": "Persona Description", "fi": "Persoonan Kuvaus"}),
        output_extensions=[],
        category_id= (
            PromptBlockCategory.EXECUTION_PERSONA
            if category == PromptBlockCategory.EXECUTION_PERSONA
            else PromptBlockCategory.AGENT_ROLE
        ),
        type=BlockDataType.INSTRUCTION,
        role_enforcement="Strict Forensic Auditor",
        tone_directives=["Objective", "Analytical"],
    )


def _build_protocol_block() -> ProtocolPromptBlock:
    """Build a valid ProtocolPromptBlock for testing.

    Returns:
        Validated ProtocolPromptBlock instance.
    """
    return ProtocolPromptBlock(
        id=generate_opaque_id(EntityPrefix.PROMPT_BLOCK),
        slug="protocol_evidence_extraction",
        organization_id=generate_opaque_id(EntityPrefix.ORGANIZATION),
        label=I18nText(translations={"en": "Protocol Label", "fi": "Protokollan Nimike"}),
        description=I18nText(translations={"en": "Protocol Description", "fi": "Protokollan Kuvaus"}),
        output_extensions=[],
        category_id=PromptBlockCategory.PROTOCOL,
        type=BlockDataType.INSTRUCTION,
        protocol_instructions="Extract verbatim quotes with character-level accuracy.",
    )


def _build_step(
    *,
    step_type: StepType = StepType.LLM,
    hook: str | None = None,
    role_block_id: str | None = None,
    extraction_protocol_block_id: str | None = None,
    execution_persona_block_id: str | None = None,
    criteria_block_ids: list[str] | None = None,
    cognitive_tier: CognitiveTier | None = CognitiveTier.FAST,
) -> Step:
    """Build a valid Step domain model for testing.

    Args:
        step_type: StepType enum variant.
        hook: Optional logic hook name when step_type is LOGIC.
        role_block_id: Optional role block ID.
        extraction_protocol_block_id: Optional extraction protocol block ID.
        execution_persona_block_id: Optional execution persona block ID.
        criteria_block_ids: Optional list of criteria block IDs.
        cognitive_tier: Optional cognitive tier setting.

    Returns:
        Validated Step instance.
    """
    resolved_criteria = (
        criteria_block_ids
        if criteria_block_ids is not None
        else ([generate_opaque_id(EntityPrefix.PROMPT_BLOCK)] if step_type == StepType.LLM else [])
    )
    resolved_protocol = (
        extraction_protocol_block_id
        if extraction_protocol_block_id is not None
        else (generate_opaque_id(EntityPrefix.PROMPT_BLOCK) if step_type == StepType.LLM else None)
    )
    return Step(
        id=generate_opaque_id(EntityPrefix.STEP),
        slug="step_forensic_evaluation",
        organization_id=generate_opaque_id(EntityPrefix.ORGANIZATION),
        name=I18nText(translations={"en": "Forensic Step", "fi": "Forensinen Vaihe"}),
        description=I18nText(translations={"en": "Step Description", "fi": "Vaiheen Kuvaus"}),
        type=step_type,
        hook=hook,
        role_block_id=role_block_id,
        extraction_protocol_block_id=resolved_protocol,
        execution_persona_block_id=execution_persona_block_id,
        criteria_block_ids=resolved_criteria,
        cognitive_tier=cognitive_tier,
        engine_type=EngineType.PROMPT,
        zone=StepZone.ZONE_B,
    )


@pytest.mark.asyncio
async def test_iam_system_and_studio_entities_roundtrip_parity() -> None:
    """Verify all AnyPromptBlock variants and Step upsert and get roundtrips preserve 100% field parity."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        matrix_blk = MatrixPromptBlockFactory.build()
        saved_matrix_id = await upsert_prompt_block_row(conn, _TIMEOUT, matrix_blk)
        assert saved_matrix_id == matrix_blk.id
        fetched_matrix = await get_prompt_block_row(conn, _TIMEOUT, matrix_blk.id)
        assert isinstance(fetched_matrix, MatrixPromptBlock)
        assert fetched_matrix == matrix_blk

        persona_blk = _build_persona_block(PromptBlockCategory.EXECUTION_PERSONA)
        saved_persona_id = await upsert_prompt_block_row(conn, _TIMEOUT, persona_blk)
        assert saved_persona_id == persona_blk.id
        fetched_persona = await get_prompt_block_row(conn, _TIMEOUT, persona_blk.id)
        assert isinstance(fetched_persona, PersonaPromptBlock)
        assert fetched_persona == persona_blk

        role_blk = _build_persona_block(PromptBlockCategory.AGENT_ROLE)
        saved_role_id = await upsert_prompt_block_row(conn, _TIMEOUT, role_blk)
        assert saved_role_id == role_blk.id
        fetched_role = await get_prompt_block_row(conn, _TIMEOUT, role_blk.id)
        assert isinstance(fetched_role, PersonaPromptBlock)
        assert fetched_role == role_blk

        proto_blk = _build_protocol_block()
        saved_proto_id = await upsert_prompt_block_row(conn, _TIMEOUT, proto_blk)
        assert saved_proto_id == proto_blk.id
        fetched_proto = await get_prompt_block_row(conn, _TIMEOUT, proto_blk.id)
        assert isinstance(fetched_proto, ProtocolPromptBlock)
        assert fetched_proto == proto_blk

        rule_blk = SystemRulePromptBlockFactory.build()
        saved_rule_id = await upsert_prompt_block_row(conn, _TIMEOUT, rule_blk)
        assert saved_rule_id == rule_blk.id
        fetched_rule = await get_prompt_block_row(conn, _TIMEOUT, rule_blk.id)
        assert isinstance(fetched_rule, SystemRulePromptBlock)
        assert fetched_rule == rule_blk

        step_with_tier = _build_step(
            role_block_id=role_blk.id,
            extraction_protocol_block_id=proto_blk.id,
            execution_persona_block_id=persona_blk.id,
            criteria_block_ids=[matrix_blk.id],
            cognitive_tier=CognitiveTier.DEEP,
        )
        saved_step_id = await upsert_step_row(conn, _TIMEOUT, step_with_tier)
        assert saved_step_id == step_with_tier.id
        fetched_step = await get_step_row(conn, _TIMEOUT, step_with_tier.id)
        assert fetched_step is not None
        assert fetched_step == step_with_tier

        step_no_tier = _build_step(
            step_type=StepType.LOGIC,
            hook="normalization_hook",
            role_block_id=None,
            extraction_protocol_block_id=None,
            execution_persona_block_id=None,
            criteria_block_ids=[],
            cognitive_tier=None,
        )
        saved_no_tier_id = await upsert_step_row(conn, _TIMEOUT, step_no_tier)
        assert saved_no_tier_id == step_no_tier.id
        fetched_no_tier = await get_step_row(conn, _TIMEOUT, step_no_tier.id)
        assert fetched_no_tier is not None
        assert fetched_no_tier == step_no_tier
        assert fetched_no_tier.cognitive_tier is None
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_prompt_block_and_step_get_missing_rows_return_none() -> None:
    """Verify get_prompt_block_row and get_step_row return None when missing."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        missing_blk_id = generate_opaque_id(EntityPrefix.PROMPT_BLOCK)
        missing_stp_id = generate_opaque_id(EntityPrefix.STEP)

        assert await get_prompt_block_row(conn, _TIMEOUT, missing_blk_id) is None
        assert await get_step_row(conn, _TIMEOUT, missing_stp_id) is None
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_prompt_block_and_step_invalid_prefix_raises_validation_failed() -> None:
    """Verify invalid entity ID prefixes raise AppException with VALIDATION_FAILED."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        with pytest.raises(AppException) as blk_err:
            await get_prompt_block_row(conn, _TIMEOUT, "stp_0195f3a0000070008000000000000001")
        assert blk_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as stp_err:
            await get_step_row(conn, _TIMEOUT, "blk_0195f3a0000070008000000000000001")
        assert stp_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_prompt_block_and_step_upsert_execute_faults_raise_storage_access_failed() -> None:
    """Verify upsert_prompt_block_row and upsert_step_row translate execute faults."""
    pool = InMemoryAsyncPgPool()
    blk = SystemRulePromptBlockFactory.build()
    step = _build_step()
    conn = await pool.acquire()
    try:
        pool.inject_fault("execute", RuntimeError("simulated execute failure"))
        with pytest.raises(AppException) as blk_exc:
            await upsert_prompt_block_row(conn, _TIMEOUT, blk)
        assert blk_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        with pytest.raises(AppException) as stp_exc:
            await upsert_step_row(conn, _TIMEOUT, step)
        assert stp_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
    finally:
        pool.clear_faults()
        await pool.release(conn)


@pytest.mark.asyncio
async def test_stage_get_methods_translate_fetchrow_faults_to_app_exception() -> None:
    """Verify get_prompt_block_row and get_step_row translate fetchrow faults."""
    pool = InMemoryAsyncPgPool()
    blk_id = generate_opaque_id(EntityPrefix.PROMPT_BLOCK)
    stp_id = generate_opaque_id(EntityPrefix.STEP)
    conn = await pool.acquire()
    try:
        pool.inject_fault("fetchrow", RuntimeError("simulated fetchrow failure"))
        with pytest.raises(AppException) as blk_exc:
            await get_prompt_block_row(conn, _TIMEOUT, blk_id)
        assert blk_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        with pytest.raises(AppException) as stp_exc:
            await get_step_row(conn, _TIMEOUT, stp_id)
        assert stp_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        pool.inject_fault(
            "fetchrow",
            AppException(
                message="pre-existing app exception",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ),
        )
        with pytest.raises(AppException) as direct_blk_exc:
            await get_prompt_block_row(conn, _TIMEOUT, blk_id)
        assert direct_blk_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as direct_stp_exc:
            await get_step_row(conn, _TIMEOUT, stp_id)
        assert direct_stp_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    finally:
        pool.clear_faults()
        await pool.release(conn)
    assert callable(hydrate_prompt_block_row)
    assert callable(hydrate_step_row)
