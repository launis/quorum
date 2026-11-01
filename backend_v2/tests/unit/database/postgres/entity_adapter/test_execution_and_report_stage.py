"""Unit and boundary tests for PostgreSQL 19 Execution, ReportArtifact, and ReportBinary stage.

Covers positive roundtrip persistence and hydration for ExecutionRecord,
ReportArtifact, and ReportBinaryPayloadDTO, plus negative identifier validation,
size mismatch checks, and driver fault translation.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

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
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.domain.execution import ExecutionSummarySnapshot
from backend_v2.models.domain.proposition_graph import ReportBinaryPayloadDTO
from backend_v2.models.enums import EntityPrefix
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.tests.factories.model_factories import (
    ExecutionRecordFactory,
    ReportArtifactFactory,
)
from backend_v2.tests.fakes.in_memory_uow import InMemoryAsyncPgPool

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
            execution_summary=ExecutionSummarySnapshot(strictness_level=90, is_ensemble_run=True),
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
