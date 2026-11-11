"""Unit and boundary tests for PostgreSQL 19 Workflow and OutputProfile entity stage.

Covers positive roundtrip persistence and hydration for Workflow and OutputProfile
(including non-null language, null language, and empty variance_target_block), plus
negative identifier validation and driver fault handling.
"""

from __future__ import annotations

import pytest

from backend_v2.database.postgres.entity_adapter.workflow_and_profile_stage import (
    get_output_profile_row,
    get_task_brief_row,
    get_workflow_row,
    hydrate_workflow_row,
    list_task_brief_rows,
    upsert_output_profile_row,
    upsert_task_brief_row,
    upsert_workflow_row,
)
from backend_v2.database.postgres.storage_driver import PostgresStorageDriver
from backend_v2.database.repositories.components.task_brief import TaskBriefRepositoryImpl
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import generate_opaque_id, parse_prefixed_uuid7
from backend_v2.models.enums import EntityPrefix
from backend_v2.tests.factories.model_factories import (
    OutputProfileFactory,
    TaskBriefFactory,
    WorkflowFactory,
)
from backend_v2.tests.fakes.in_memory_uow import InMemoryAsyncPgPool, InMemoryAsyncPgRecord

_TIMEOUT: float = 5.0


@pytest.mark.asyncio
async def test_iam_system_and_studio_entities_roundtrip_parity() -> None:
    """Verify Workflow and OutputProfile upsert and get roundtrips preserve 100% field parity."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        wf = WorkflowFactory.build()
        saved_wf_id = await upsert_workflow_row(conn, _TIMEOUT, wf)
        assert saved_wf_id == wf.id
        fetched_wf = await get_workflow_row(conn, _TIMEOUT, wf.id)
        assert fetched_wf is not None
        assert fetched_wf == wf

        profile_with_lang = OutputProfileFactory.build(
            workflow_id=wf.id,
            language="fi",
            variance_target_block=generate_opaque_id(EntityPrefix.PROMPT_BLOCK),
            user_role_target_block=generate_opaque_id(EntityPrefix.PROMPT_BLOCK),
            content_blocks=[],
        )
        saved_prf_id = await upsert_output_profile_row(conn, _TIMEOUT, profile_with_lang)
        assert saved_prf_id == profile_with_lang.id
        fetched_prf = await get_output_profile_row(conn, _TIMEOUT, profile_with_lang.id)
        assert fetched_prf is not None
        assert fetched_prf == profile_with_lang
        assert fetched_prf.language == "fi"

        brief_system = TaskBriefFactory.build(organization_id=None, source_url=None)
        brief_tenant = TaskBriefFactory.build(
            organization_id=generate_opaque_id(EntityPrefix.ORGANIZATION),
            source_url="https://quorum.ai/briefs/1",
        )
        assert await upsert_task_brief_row(conn, _TIMEOUT, brief_system) == brief_system.id
        assert await upsert_task_brief_row(conn, _TIMEOUT, brief_tenant) == brief_tenant.id
        fetched_sys_brief = await get_task_brief_row(conn, _TIMEOUT, brief_system.id)
        fetched_ten_brief = await get_task_brief_row(conn, _TIMEOUT, brief_tenant.id)
        assert fetched_sys_brief == brief_system
        assert fetched_ten_brief == brief_tenant
        all_briefs = await list_task_brief_rows(conn, _TIMEOUT)
        assert len(all_briefs) == 2
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_output_profile_empty_variance_target_block_hydration() -> None:
    """Verify upsert_output_profile_row and hydrate_output_profile_row handle null target blocks and null language."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        wf = WorkflowFactory.build()
        await upsert_workflow_row(conn, _TIMEOUT, wf)

        profile_empty_targets = OutputProfileFactory.build(
            workflow_id=wf.id,
            language=None,
            variance_target_block=None,
            user_role_target_block=None,
            content_blocks=[],
        )
        saved_id = await upsert_output_profile_row(conn, _TIMEOUT, profile_empty_targets)
        assert saved_id == profile_empty_targets.id

        hydrated = await get_output_profile_row(conn, _TIMEOUT, profile_empty_targets.id)
        assert hydrated is not None
        assert hydrated.language is None
        assert hydrated.variance_target_block is None
        assert hydrated.user_role_target_block is None
        assert hydrated.content_blocks == []
        assert hydrated == profile_empty_targets
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_workflow_and_profile_get_missing_rows_return_none() -> None:
    """Verify get_workflow_row and get_output_profile_row return None when missing."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        missing_wf_id = generate_opaque_id(EntityPrefix.WORKFLOW)
        missing_prf_id = generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)

        assert await get_workflow_row(conn, _TIMEOUT, missing_wf_id) is None
        assert await get_output_profile_row(conn, _TIMEOUT, missing_prf_id) is None
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_workflow_and_profile_invalid_prefix_raises_validation_failed() -> None:
    """Verify invalid entity ID prefixes raise AppException with VALIDATION_FAILED."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        with pytest.raises(AppException) as wf_err:
            await get_workflow_row(conn, _TIMEOUT, "prf_0195f3a0000070008000000000000001")
        assert wf_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as prf_err:
            await get_output_profile_row(conn, _TIMEOUT, "wf_0195f3a0000070008000000000000001")
        assert prf_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_workflow_and_profile_upsert_execute_faults_raise_storage_access_failed() -> None:
    """Verify upsert_workflow_row and upsert_output_profile_row translate execute faults."""
    pool = InMemoryAsyncPgPool()
    wf = WorkflowFactory.build()
    prf = OutputProfileFactory.build(workflow_id=wf.id, content_blocks=[])
    conn = await pool.acquire()
    try:
        pool.inject_fault("execute", RuntimeError("simulated execute failure"))
        with pytest.raises(AppException) as wf_exc:
            await upsert_workflow_row(conn, _TIMEOUT, wf)
        assert wf_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        with pytest.raises(AppException) as prf_exc:
            await upsert_output_profile_row(conn, _TIMEOUT, prf)
        assert prf_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
    finally:
        pool.clear_faults()
        await pool.release(conn)


@pytest.mark.asyncio
async def test_stage_get_methods_translate_fetchrow_faults_to_app_exception() -> None:
    """Verify get_workflow_row and get_output_profile_row translate fetchrow faults."""
    pool = InMemoryAsyncPgPool()
    wf_id = generate_opaque_id(EntityPrefix.WORKFLOW)
    prf_id = generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)
    conn = await pool.acquire()
    try:
        pool.inject_fault("fetchrow", RuntimeError("simulated fetchrow failure"))
        with pytest.raises(AppException) as wf_exc:
            await get_workflow_row(conn, _TIMEOUT, wf_id)
        assert wf_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        with pytest.raises(AppException) as prf_exc:
            await get_output_profile_row(conn, _TIMEOUT, prf_id)
        assert prf_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        pool.inject_fault(
            "fetchrow",
            AppException(
                message="pre-existing app exception",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ),
        )
        with pytest.raises(AppException) as direct_wf_exc:
            await get_workflow_row(conn, _TIMEOUT, wf_id)
        assert direct_wf_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as direct_prf_exc:
            await get_output_profile_row(conn, _TIMEOUT, prf_id)
        assert direct_prf_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    finally:
        pool.clear_faults()
        await pool.release(conn)


@pytest.mark.asyncio
async def test_task_brief_stage_and_repository_crud_and_negative_boundaries() -> None:
    """Verify TaskBrief stage faults and TaskBriefRepositoryImpl positive and negative boundaries."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        missing_tbr_id = generate_opaque_id(EntityPrefix.TASK_BRIEF)
        assert await get_task_brief_row(conn, _TIMEOUT, missing_tbr_id) is None

        # Negative 1: Wrong entity prefix on get_task_brief_row raises VALIDATION_FAILED
        with pytest.raises(AppException) as bad_prefix_exc:
            await get_task_brief_row(conn, _TIMEOUT, generate_opaque_id(EntityPrefix.PROMPT_BLOCK))
        assert bad_prefix_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        # Negative 2: Driver fault during list_task_brief_rows translates to STORAGE_ACCESS_FAILED
        pool.inject_fault("fetch", RuntimeError("simulated fetch failure"))
        with pytest.raises(AppException) as fetch_exc:
            await list_task_brief_rows(conn, _TIMEOUT)
        assert fetch_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
        pool.clear_faults()

        pool.inject_fault(
            "fetch",
            AppException(
                message="pre-existing app exception",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ),
        )
        with pytest.raises(AppException) as direct_fetch_exc:
            await list_task_brief_rows(conn, _TIMEOUT)
        assert direct_fetch_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
        pool.clear_faults()
    finally:
        pool.clear_faults()
        await pool.release(conn)

    # TaskBriefRepositoryImpl end-to-end over PostgresStorageDriver + InMemoryAsyncPgPool
    from backend_v2.database.postgres.pool import PostgresPoolManager
    from backend_v2.models.enums import StorageBackend
    from backend_v2.settings import Settings

    settings = Settings(
        storage_backend=StorageBackend.POSTGRES,
        postgres_host="db.internal",
        postgres_port=5432,
        postgres_user="quorum",
        postgres_db="quorum",
        postgres_command_timeout_seconds=5.0,
    )
    pool_mgr = PostgresPoolManager(settings=settings, pool=pool)
    driver = PostgresStorageDriver(pool_manager=pool_mgr, settings=settings)
    repo = TaskBriefRepositoryImpl(driver)

    brief = TaskBriefFactory.build(organization_id=None, source_url="https://example.com/brief")
    created_id = await repo.create_task_brief(brief)
    assert created_id == brief.id

    fetched = await repo.get_task_brief_by_id(brief.id)
    assert fetched == brief

    updated_brief = brief.model_copy(update={"instruction_text": "Updated instruction text"})
    assert await repo.update_task_brief(brief.id, updated_brief) is True
    assert await repo.update_task_brief(generate_opaque_id(EntityPrefix.TASK_BRIEF), updated_brief) is False

    all_items = await repo.get_all_task_briefs()
    assert len(all_items) == 1
    assert all_items[0].instruction_text == "Updated instruction text"

    assert await repo.delete_task_brief(brief.id) is True
    assert await repo.delete_task_brief(brief.id) is False
    assert await repo.get_task_brief_by_id(brief.id) is None


def test_hydrate_workflow_row_corrupt_steps_raises_validation_failed() -> None:
    """Verify hydrate_workflow_row validates steps via _STEP_RULE_LIST_ADAPTER and raises VALIDATION_FAILED on corruption."""
    wf = WorkflowFactory.build()
    wf_uuid = parse_prefixed_uuid7(wf.id, EntityPrefix.WORKFLOW)
    reg_uuid = parse_prefixed_uuid7(wf.model_registry_id, EntityPrefix.SYSTEM_CONFIG)
    corrupt_row = InMemoryAsyncPgRecord(
        {
            "id": wf_uuid,
            "slug": wf.slug,
            "name": '{"translations":{"en":"WF","fi":"WF"}}',
            "description": '{"translations":{"en":"Desc","fi":"Kuvaus"}}',
            "status": wf.status,
            "version": wf.version,
            "is_public": wf.is_public,
            "organization_id": None,
            "default_profile_id": None,
            "mcp_gateway_id": None,
            "model_registry_id": reg_uuid,
            "default_strictness_level": wf.default_strictness_level,
            "default_lexical_strictness_level": wf.default_lexical_strictness_level,
            "security_penalty": wf.security_penalty,
            "post_hoc_penalty": wf.post_hoc_penalty,
            "passivity_penalty": wf.passivity_penalty,
            "enable_contextual_overrides": wf.enable_contextual_overrides,
            "enable_semantic_smoothing": wf.enable_semantic_smoothing,
            "enable_eager_anonymization": wf.enable_eager_anonymization,
            "system_audit_trail": wf.system_audit_trail,
            "expected_inputs": "[]",
            "steps": '[{"invalid_step_key": "corrupt"}]',
            "historical_context_mode": wf.historical_context_mode.value,
        }
    )
    with pytest.raises(AppException) as exc_info:
        hydrate_workflow_row(corrupt_row)
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert exc_info.value.details["table_name"] == "workflows"
    assert exc_info.value.details["entity_id"] == wf.id
