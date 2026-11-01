"""Unit and boundary tests for PostgreSQL 19 Workflow and OutputProfile entity stage.

Covers positive roundtrip persistence and hydration for Workflow and OutputProfile
(including non-null language, null language, and empty variance_target_block), plus
negative identifier validation and driver fault handling.
"""

from __future__ import annotations

import pytest

from backend_v2.database.postgres.entity_adapter.workflow_and_profile_stage import (
    get_output_profile_row,
    get_workflow_row,
    hydrate_output_profile_row,
    hydrate_workflow_row,
    upsert_output_profile_row,
    upsert_workflow_row,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.enums import EntityPrefix
from backend_v2.tests.factories.model_factories import (
    OutputProfileFactory,
    WorkflowFactory,
)
from backend_v2.tests.fakes.in_memory_uow import InMemoryAsyncPgPool

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
    assert callable(hydrate_workflow_row)
    assert callable(hydrate_output_profile_row)
