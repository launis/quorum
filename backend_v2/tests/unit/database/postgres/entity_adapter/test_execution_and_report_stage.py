"""Unit and boundary tests for PostgreSQL 19 Execution, ReportArtifact, and ReportBinary stage.

Covers positive roundtrip persistence and hydration for ExecutionRecord,
ReportArtifact, and ReportBinaryPayloadDTO, plus negative identifier validation,
size mismatch checks, and driver fault translation.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_core import from_json

from backend_v2.database.postgres.entity_adapter.coercion_and_constants import execute_entity_upsert
from backend_v2.database.postgres.entity_adapter.execution_and_report_stage import (
    get_execution_row,
    get_report_artifact_row,
    get_report_binary_row,
    hydrate_execution_row,
    hydrate_report_artifact_row,
    save_execution_row,
    save_report_binary_row,
    upsert_report_artifact_row,
)
from backend_v2.database.postgres.pool import (
    decode_jsonb_binary,
    encode_jsonb_binary,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import generate_opaque_id, parse_prefixed_uuid7
from backend_v2.models.domain.execution import ExecutionSummarySnapshot
from backend_v2.models.domain.proposition_graph import ReportBinaryPayloadDTO
from backend_v2.models.dtos.global_context import GlobalContextVarsDTO
from backend_v2.models.enums import EntityPrefix
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.tests.factories.model_factories import (
    ExecutionRecordFactory,
    ReportArtifactFactory,
)
from backend_v2.tests.fakes.in_memory_uow import InMemoryAsyncPgPool, InMemoryAsyncPgRecord

_TIMEOUT: float = 5.0


@pytest.mark.asyncio
async def test_execution_report_and_seed_collection_roundtrip_parity() -> None:
    """Verify save_execution_row, get_execution_row, report binary, and report artifact roundtrip parity."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        exec_full = ExecutionRecordFactory.build(
            active_profile_id=generate_opaque_id(EntityPrefix.OUTPUT_PROFILE),
            output_profile_id=generate_opaque_id(EntityPrefix.OUTPUT_PROFILE),
            execution_summary=ExecutionSummarySnapshot(
                strictness_level=90,
                is_ensemble_run=True,
                system_concurrency_snapshot={"max_concurrent_workflows": 4},
            ),
            metadata=ExecutionMetadata(
                matrix_sampling_strategy=5,
                workflow_version=2,
                model_registry_id=generate_opaque_id(EntityPrefix.SYSTEM_CONFIG),
            ),
        )
        saved_exec_id = await save_execution_row(conn, _TIMEOUT, exec_full)
        assert saved_exec_id == exec_full.id
        fetched_exec = await get_execution_row(conn, _TIMEOUT, exec_full.id)
        assert fetched_exec is not None
        assert fetched_exec.id == exec_full.id
        assert fetched_exec.workflow_id == exec_full.workflow_id
        assert fetched_exec.execution_summary == exec_full.execution_summary
        assert fetched_exec.metadata == exec_full.metadata

        exec_minimal = ExecutionRecordFactory.build(
            active_profile_id=None,
            output_profile_id=None,
            frozen_context=None,
            execution_summary=None,
            metadata=None,
        )
        await save_execution_row(conn, _TIMEOUT, exec_minimal)
        fetched_min = await get_execution_row(conn, _TIMEOUT, exec_minimal.id)
        assert fetched_min is not None
        assert fetched_min.frozen_context is None
        assert fetched_min.execution_summary is None
        assert fetched_min.metadata is None

        artifact = ReportArtifactFactory.build(
            execution_id=exec_full.id,
            workflow_id=exec_full.workflow_id,
            custom_preface_md="# Custom Preface",
        )
        saved_rep_id = await upsert_report_artifact_row(conn, _TIMEOUT, artifact)
        assert saved_rep_id == artifact.id
        fetched_rep = await get_report_artifact_row(conn, _TIMEOUT, artifact.id)
        assert fetched_rep is not None
        assert fetched_rep == artifact

        pdf_bytes = b"%PDF-1.7 binary payload"
        binary_dto = ReportBinaryPayloadDTO(
            report_id=artifact.id,
            mime_type="application/pdf",
            pdf_bytes=pdf_bytes,
            size_bytes=len(pdf_bytes),
            created_at=datetime.now(UTC),
        )
        await save_report_binary_row(conn, _TIMEOUT, binary_dto)
        fetched_bin = await get_report_binary_row(conn, _TIMEOUT, artifact.id)
        assert fetched_bin is not None
        assert fetched_bin == binary_dto
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_execution_and_report_get_missing_rows_return_none() -> None:
    """Verify get_execution_row, get_report_artifact_row, and get_report_binary_row return None when missing."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        missing_exe_id = generate_opaque_id(EntityPrefix.EXECUTION)
        missing_rep_id = generate_opaque_id(EntityPrefix.REPORT)

        assert await get_execution_row(conn, _TIMEOUT, missing_exe_id) is None
        assert await get_report_artifact_row(conn, _TIMEOUT, missing_rep_id) is None
        assert await get_report_binary_row(conn, _TIMEOUT, missing_rep_id) is None
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_report_binary_size_mismatch_and_invalid_prefix_raise_validation_failed() -> None:
    """Verify size_bytes mismatch and invalid ID prefixes raise AppException(VALIDATION_FAILED)."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        bad_binary = ReportBinaryPayloadDTO(
            report_id=generate_opaque_id(EntityPrefix.REPORT),
            mime_type="application/pdf",
            pdf_bytes=b"1234",
            size_bytes=99,
            created_at=datetime.now(UTC),
        )
        with pytest.raises(AppException) as size_err:
            await save_report_binary_row(conn, _TIMEOUT, bad_binary)
        assert size_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as exe_err:
            await get_execution_row(conn, _TIMEOUT, "rep_0195f3a0000070008000000000000001")
        assert exe_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as rep_err:
            await get_report_artifact_row(conn, _TIMEOUT, "exe_0195f3a0000070008000000000000001")
        assert rep_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as bin_id_err:
            await get_report_binary_row(conn, None, "exe_0195f3a0000070008000000000000001")
        assert bin_id_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_collection_crud_and_report_artifact_fault_translation() -> None:
    """Verify driver faults in execution, report binary, and report artifact stage raise AppException."""
    pool = InMemoryAsyncPgPool()
    exec_rec = ExecutionRecordFactory.build(active_profile_id=None, output_profile_id=None)
    artifact = ReportArtifactFactory.build(execution_id=exec_rec.id, workflow_id=exec_rec.workflow_id)
    binary_dto = ReportBinaryPayloadDTO(
        report_id=artifact.id,
        mime_type="application/pdf",
        pdf_bytes=b"PDF",
        size_bytes=3,
        created_at=datetime.now(UTC),
    )
    direct_app_err = AppException(
        message="pre-existing app exception",
        status_code=400,
        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
    )
    conn = await pool.acquire()
    try:
        pool.inject_fault("execute", RuntimeError("simulated execute failure"))
        with pytest.raises(AppException) as save_bin_exc:
            await save_report_binary_row(conn, _TIMEOUT, binary_dto)
        assert save_bin_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        with pytest.raises(AppException) as save_exe_exc:
            await save_execution_row(conn, _TIMEOUT, exec_rec)
        assert save_exe_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        with pytest.raises(AppException) as save_rep_exc:
            await upsert_report_artifact_row(conn, _TIMEOUT, artifact)
        assert save_rep_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        pool.inject_fault("execute", direct_app_err)
        with pytest.raises(AppException) as direct_bin_exc:
            await save_report_binary_row(conn, _TIMEOUT, binary_dto)
        assert direct_bin_exc.value is direct_app_err

        with pytest.raises(AppException) as direct_exe_exc:
            await save_execution_row(conn, _TIMEOUT, exec_rec)
        assert direct_exe_exc.value is direct_app_err

        pool.clear_faults()
        pool.inject_fault("fetchrow", RuntimeError("simulated fetchrow failure"))
        with pytest.raises(AppException) as get_bin_exc:
            await get_report_binary_row(conn, _TIMEOUT, artifact.id)
        assert get_bin_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        with pytest.raises(AppException) as get_exe_exc:
            await get_execution_row(conn, _TIMEOUT, exec_rec.id)
        assert get_exe_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        with pytest.raises(AppException) as get_rep_exc:
            await get_report_artifact_row(conn, _TIMEOUT, artifact.id)
        assert get_rep_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        pool.inject_fault("fetchrow", direct_app_err)
        with pytest.raises(AppException) as direct_get_bin:
            await get_report_binary_row(conn, _TIMEOUT, artifact.id)
        assert direct_get_bin.value is direct_app_err

        with pytest.raises(AppException) as direct_get_exe:
            await get_execution_row(conn, _TIMEOUT, exec_rec.id)
        assert direct_get_exe.value is direct_app_err

        with pytest.raises(AppException) as direct_get_rep:
            await get_report_artifact_row(conn, _TIMEOUT, artifact.id)
        assert direct_get_rep.value is direct_app_err
    finally:
        pool.clear_faults()
        await pool.release(conn)
    assert callable(hydrate_execution_row)
    assert callable(hydrate_report_artifact_row)


@pytest.mark.asyncio
async def test_save_execution_row_increments_state_version_on_matching_expected_state_version() -> None:
    """Verify save_execution_row increments state_version when expected_state_version matches."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        exec_rec = ExecutionRecordFactory.build(
            active_profile_id=None,
            output_profile_id=None,
            state_version=1,
        )
        await save_execution_row(conn, _TIMEOUT, exec_rec)
        initial = await get_execution_row(conn, _TIMEOUT, exec_rec.id)
        assert initial is not None
        assert initial.state_version == 1

        await save_execution_row(
            conn,
            _TIMEOUT,
            exec_rec.model_copy(update={"progress": 50}),
            expected_state_version=1,
        )
        updated = await get_execution_row(conn, _TIMEOUT, exec_rec.id)
        assert updated is not None
        assert updated.state_version == 2
        assert updated.progress == 50
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_save_execution_row_raises_conflict_409_on_stale_expected_state_version() -> None:
    """Verify save_execution_row raises AppException(CONFLICT, 409) when expected_state_version is stale."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        exec_rec = ExecutionRecordFactory.build(
            active_profile_id=None,
            output_profile_id=None,
            state_version=2,
            progress=40,
        )
        await save_execution_row(conn, _TIMEOUT, exec_rec)

        with pytest.raises(AppException) as conflict_err:
            await save_execution_row(
                conn,
                _TIMEOUT,
                exec_rec.model_copy(update={"progress": 90}),
                expected_state_version=1,
            )
        assert conflict_err.value.status_code == 409
        assert conflict_err.value.details["error_code"] == ErrorCodes.CONFLICT.value
        assert conflict_err.value.details["expected_state_version"] == 1
        assert conflict_err.value.details["actual_state_version"] == 2

        persisted = await get_execution_row(conn, _TIMEOUT, exec_rec.id)
        assert persisted is not None
        assert persisted.state_version == 2
        assert persisted.progress == 40
    finally:
        await pool.release(conn)


def test_execution_record_rejects_state_version_less_than_one() -> None:
    """Verify ExecutionRecord boundary validation rejects state_version=0 (ge=1)."""
    with pytest.raises(ValidationError):
        ExecutionRecordFactory.build(state_version=0)


@pytest.mark.asyncio
async def test_save_execution_row_excludes_none_in_metadata_and_encode_jsonb_binary_unwraps_json_str() -> None:
    """Verify save_execution_row serializes metadata with exclude_none=True and encode_jsonb_binary unwraps JSON strings."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
        exec_rec = ExecutionRecordFactory.build(
            active_profile_id=None,
            output_profile_id=None,
            execution_summary=ExecutionSummarySnapshot(
                strictness_level=80,
                is_ensemble_run=False,
                system_concurrency_snapshot={"max_concurrent_workflows": 2},
            ),
            metadata=ExecutionMetadata(
                matrix_sampling_strategy=0,
                workflow_version=1,
                global_context_vars=GlobalContextVarsDTO(
                    organization_id=org_id,
                    language="fi",
                    target_locale="fi",
                ),
            ),
        )
        with patch(
            "backend_v2.database.postgres.entity_adapter.execution_and_report_stage.execute_entity_upsert",
            wraps=execute_entity_upsert,
        ) as spy_upsert:
            await save_execution_row(conn, _TIMEOUT, exec_rec)
            assert spy_upsert.call_args is not None
            metadata_sql_arg = spy_upsert.call_args.args[35]
        assert isinstance(metadata_sql_arg, str)
        parsed_metadata = from_json(metadata_sql_arg)
        assert "initiator_id" not in parsed_metadata["global_context_vars"]
        assert "_sys_initiator_id" not in parsed_metadata["global_context_vars"]
        assert "null" not in metadata_sql_arg

        wire_bytes = encode_jsonb_binary(metadata_sql_arg)
        decoded_obj = decode_jsonb_binary(wire_bytes)
        assert isinstance(decoded_obj, dict)
        assert decoded_obj["workflow_version"] == 1

        with pytest.raises(AppException) as exc_info:
            encode_jsonb_binary("{malformed_json")
        assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        with pytest.raises(AppException) as empty_exc_info:
            encode_jsonb_binary("")
        assert empty_exc_info.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        ddl_sql = Path("backend_v2/database/migrations/001_pg19_uuidv7_schema.sql").read_text(encoding="utf-8")
        assert "_sys_initiator_id" in ddl_sql
        assert "jsonb_typeof(metadata) = 'string'" in ddl_sql
    finally:
        await pool.release(conn)


def test_hydrate_report_artifact_row_corrupt_status_raises_validation_failed() -> None:
    """Verify hydrate_report_artifact_row translates ValidationError to AppException(VALIDATION_FAILED, 500)."""
    art = ReportArtifactFactory.build()
    corrupt_row = InMemoryAsyncPgRecord(
        {
            "id": parse_prefixed_uuid7(art.id, EntityPrefix.REPORT),
            "execution_id": parse_prefixed_uuid7(art.execution_id, EntityPrefix.EXECUTION),
            "workflow_id": parse_prefixed_uuid7(art.workflow_id, EntityPrefix.WORKFLOW),
            "profile_id": parse_prefixed_uuid7(art.profile_id, EntityPrefix.OUTPUT_PROFILE),
            "locale": art.locale,
            "title": art.title,
            "status": "INVALID_CORRUPT_STATUS",
            "storage_paths": "{}",
            "metadata": "{}",
            "custom_preface_md": None,
            "error_message": None,
            "created_at": art.created_at,
            "updated_at": art.updated_at,
        }
    )
    with pytest.raises(AppException) as exc_info:
        hydrate_report_artifact_row(corrupt_row)
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert exc_info.value.details["table_name"] == "report_artifacts"
    assert exc_info.value.details["entity_id"] == art.id
