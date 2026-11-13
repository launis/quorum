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
    apply_execution_updates,
    delete_execution_row,
    delete_report_artifact_row,
    get_execution_row,
    get_report_artifact_row,
    get_report_binary_row,
    hydrate_execution_row,
    hydrate_report_artifact_row,
    list_execution_rows,
    list_report_artifacts_by_execution_row,
    save_execution_row,
    save_report_binary_row,
    update_execution_occ_row,
    upsert_report_artifact_row,
)
from backend_v2.database.postgres.pool import (
    decode_jsonb_binary,
    encode_jsonb_binary,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import generate_opaque_id, parse_prefixed_uuid7
from backend_v2.models.domain.execution import ExecutionSummarySnapshot, FrozenContext
from backend_v2.models.domain.proposition_graph import ReportBinaryPayloadDTO
from backend_v2.models.dtos.global_context import GlobalContextVarsDTO
from backend_v2.models.dtos.trace import ExecutionUpdateDTO
from backend_v2.models.enums import EntityPrefix, ExecutionStatus
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
                model_registry_id=generate_opaque_id(EntityPrefix.MODEL_REGISTRY),
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
            created_at=artifact.created_at,
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
        assert "UPDATE executions" not in ddl_sql
        assert "GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL" in ddl_sql
        assert "GENERATED ALWAYS AS (uuid_extract_timestamp(report_id)) VIRTUAL" in ddl_sql

        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ExecutionRecordFactory.build(created_by="not_a_user_uuid")

        wrong_prefix_creator = generate_opaque_id(EntityPrefix.ORGANIZATION)
        with pytest.raises(ValidationError):
            ExecutionRecordFactory.build(created_by=wrong_prefix_creator)
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


@pytest.mark.asyncio
async def test_list_update_occ_and_delete_execution_and_report_rows_roundtrip() -> None:
    """Verify list, partial OCC update, and delete stage operations for executions and report_artifacts."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        from backend_v2.models.dtos.schema_manifest import GeneratedSchemaManifestDTO
        from backend_v2.models.dtos.theory_manifest import InjectedTheoryManifestDTO

        missing_exe_id = generate_opaque_id(EntityPrefix.EXECUTION)
        noop_update = ExecutionUpdateDTO(progress=25)
        assert await update_execution_occ_row(conn, _TIMEOUT, missing_exe_id, noop_update) is False
        assert await delete_execution_row(conn, _TIMEOUT, missing_exe_id) is False
        assert await delete_report_artifact_row(conn, _TIMEOUT, generate_opaque_id(EntityPrefix.REPORT)) is False

        empty_frozen = FrozenContext(
            compiled_prompts={},
            injected_theory=InjectedTheoryManifestDTO(theories={}),
            generated_schemas=GeneratedSchemaManifestDTO(schemas={}),
            ui_hints_snapshot={},
            mcp_tool_audit=[],
        )
        exec_rec = ExecutionRecordFactory.build(
            active_profile_id=None,
            output_profile_id=None,
            frozen_context=empty_frozen,
            frozen_context_storage_path="gs://bucket/frozen.json",
            execution_trace_storage_path="gs://bucket/trace.json",
            context_variables_storage_path="gs://bucket/ctx.json",
            status_message="Initial",
            state_version=1,
        )
        await save_execution_row(conn, _TIMEOUT, exec_rec)

        listed_execs = await list_execution_rows(conn, _TIMEOUT)
        assert [r.id for r in listed_execs] == [exec_rec.id]

        step_name_update = ExecutionUpdateDTO(
            status=ExecutionStatus.RUNNING,
            current_step_name="Evaluating Matrix",
            progress=60,
            execution_trace=[],
            frozen_context=empty_frozen,
            expected_state_version=1,
        )
        assert await update_execution_occ_row(conn, _TIMEOUT, exec_rec.id, step_name_update) is True
        after_occ = await get_execution_row(conn, _TIMEOUT, exec_rec.id)
        assert after_occ is not None
        assert after_occ.state_version == 2
        assert after_occ.status == ExecutionStatus.RUNNING
        assert after_occ.status_message == "Evaluating Matrix"
        assert after_occ.progress == 60
        assert after_occ.execution_trace_storage_path is None
        assert after_occ.frozen_context_storage_path is None

        clear_frozen_update = ExecutionUpdateDTO(
            current_step="Finalizing",
            frozen_context=None,
            error=None,
            state_version=5,
        )
        merged_cleared = apply_execution_updates(after_occ, clear_frozen_update)
        assert merged_cleared.status_message == "Finalizing"
        assert merged_cleared.frozen_context is None
        assert merged_cleared.state_version == 5

        rep_a = ReportArtifactFactory.build(
            execution_id=exec_rec.id,
            workflow_id=exec_rec.workflow_id,
        )
        await upsert_report_artifact_row(conn, _TIMEOUT, rep_a)
        by_exec = await list_report_artifacts_by_execution_row(conn, _TIMEOUT, exec_rec.id)
        assert [r.id for r in by_exec] == [rep_a.id]

        assert await delete_report_artifact_row(conn, _TIMEOUT, rep_a.id) is True
        assert await list_report_artifacts_by_execution_row(conn, _TIMEOUT, exec_rec.id) == []
        assert await delete_execution_row(conn, _TIMEOUT, exec_rec.id) is True
        assert await list_execution_rows(conn, _TIMEOUT) == []
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_list_and_delete_execution_and_report_rows_fault_and_invalid_id_failure() -> None:
    """Verify list and delete stage functions translate invalid prefixes and driver faults to AppException."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    valid_exe_id = generate_opaque_id(EntityPrefix.EXECUTION)
    direct_app_err = AppException(
        message="pre-existing app exception",
        status_code=400,
        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
    )
    try:
        with pytest.raises(AppException) as bad_del_exe:
            await delete_execution_row(conn, _TIMEOUT, "rep_0195f3a0000070008000000000000001")
        assert bad_del_exe.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as bad_list_rep:
            await list_report_artifacts_by_execution_row(conn, _TIMEOUT, "rep_0195f3a0000070008000000000000001")
        assert bad_list_rep.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as bad_del_rep:
            await delete_report_artifact_row(conn, _TIMEOUT, "exe_0195f3a0000070008000000000000001")
        assert bad_del_rep.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        pool.inject_fault("fetch", RuntimeError("simulated fetch failure"))
        with pytest.raises(AppException) as fetch_exe_err:
            await list_execution_rows(conn, _TIMEOUT)
        assert fetch_exe_err.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        with pytest.raises(AppException) as fetch_rep_err:
            await list_report_artifacts_by_execution_row(conn, _TIMEOUT, valid_exe_id)
        assert fetch_rep_err.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        pool.inject_fault("fetch", direct_app_err)
        with pytest.raises(AppException) as direct_exe_err:
            await list_execution_rows(conn, _TIMEOUT)
        assert direct_exe_err.value is direct_app_err

        with pytest.raises(AppException) as direct_rep_err:
            await list_report_artifacts_by_execution_row(conn, _TIMEOUT, valid_exe_id)
        assert direct_rep_err.value is direct_app_err
    finally:
        pool.clear_faults()
        await pool.release(conn)
