"""PostgreSQL 19 SQL constants, hydration, and persistence stage for executions, report_artifacts, and binaries."""

from __future__ import annotations

import logging

from fastapi import status
from pydantic_core import to_json

from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    _coerce_float,
    _coerce_uuid_or_str,
    _decode_jsonb_column,
    _encode_optional_jsonb,
    _format_optional_uuid7,
    _format_org_uuid7,
    _parse_optional_uuid7,
    _parse_org_uuid7,
    _ReportBinaryRowDTO,
    execute_entity_upsert,
)
from backend_v2.database.postgres.pool import AsyncPgConnectionProtocol, AsyncPgRecordProtocol
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import format_prefixed_uuid7, parse_prefixed_uuid7
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.proposition_graph import ReportBinaryPayloadDTO
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.enums import EntityPrefix
from backend_v2.models.state import WorkflowState

logger = logging.getLogger(__name__)
type _Conn = AsyncPgConnectionProtocol

# Ensure ExecutionRecord deferred annotations (TraceEvent union) are rebuilt
_ = WorkflowState
ExecutionRecord.model_rebuild()

__all__ = [
    "_GET_EXECUTION_SQL",
    "_GET_REPORT_ARTIFACT_SQL",
    "_GET_REPORT_BINARY_SQL",
    "_LIST_EXECUTIONS_SQL",
    "_LIST_REPORT_ARTIFACTS_SQL",
    "_MARK_REPORT_ARTIFACT_PDF_SQL",
    "_SAVE_EXECUTION_SQL",
    "_SAVE_REPORT_BINARY_SQL",
    "_UPSERT_REPORT_ARTIFACT_SQL",
    "get_execution_row",
    "get_report_artifact_row",
    "get_report_binary_row",
    "hydrate_execution_row",
    "hydrate_report_artifact_row",
    "save_execution_row",
    "save_report_binary_row",
    "upsert_report_artifact_row",
]

# Phase 3, Step 1: Relocate report_binaries, executions, and report_artifacts SQL constants
_SAVE_REPORT_BINARY_SQL: str = """INSERT INTO report_binaries (report_id, mime_type, pdf_bytes, size_bytes, created_at)
VALUES ($1::uuid, $2, $3::bytea, $4::bigint, $5::timestamptz)
ON CONFLICT (report_id) DO UPDATE SET mime_type = EXCLUDED.mime_type, pdf_bytes = EXCLUDED.pdf_bytes,
    size_bytes = EXCLUDED.size_bytes, created_at = EXCLUDED.created_at"""

_MARK_REPORT_ARTIFACT_PDF_SQL: str = (
    "UPDATE report_artifacts SET has_pdf = TRUE, updated_at = CURRENT_TIMESTAMP WHERE id = $1::uuid"
)

_GET_REPORT_BINARY_SQL: str = (
    "SELECT report_id, mime_type, pdf_bytes, size_bytes, created_at FROM report_binaries WHERE report_id = $1::uuid"
)

_EXECUTION_COLS: str = """id, workflow_id, workflow_version, active_profile_id, output_profile_id, status,
    target_locale, progress, status_message, raw_inputs, frozen_context, frozen_context_storage_path,
    pdf_report_path, steps, step_states, profile_syntheses, source_identity_manifest, execution_trace,
    execution_trace_storage_path, context_variables, context_variables_storage_path, is_resumable,
    prompt_tokens, completion_tokens, cached_tokens, reasoning_tokens, cumulative_synthesis_tokens,
    dag_cost_usd, cumulative_synthesis_cost, cost_estimate, models_used, execution_summary, metadata,
    duration_ms, error, created_at, updated_at, completed_at, created_by, organization_id"""

_SAVE_EXECUTION_SQL: str = f"""INSERT INTO executions ({_EXECUTION_COLS}) VALUES (
    $1::uuid, $2::uuid, $3, $4::uuid, $5::uuid, $6, $7, $8, $9, $10::jsonb, $11::jsonb, $12, $13, $14::jsonb,
    $15::jsonb, $16::jsonb, $17::jsonb, $18::jsonb, $19, $20::jsonb, $21, $22, $23::bigint, $24::bigint,
    $25::bigint, $26::bigint, $27::bigint, $28::numeric, $29::numeric, $30::numeric, $31::jsonb, $32::jsonb,
    $33::jsonb, $34::bigint, $35, $36::timestamptz, $37::timestamptz, $38::timestamptz, $39, $40::uuid
) ON CONFLICT (id) DO UPDATE SET
    workflow_id = EXCLUDED.workflow_id, workflow_version = EXCLUDED.workflow_version,
    active_profile_id = EXCLUDED.active_profile_id, output_profile_id = EXCLUDED.output_profile_id,
    status = EXCLUDED.status, target_locale = EXCLUDED.target_locale, progress = EXCLUDED.progress,
    status_message = EXCLUDED.status_message, raw_inputs = EXCLUDED.raw_inputs,
    frozen_context = EXCLUDED.frozen_context, frozen_context_storage_path = EXCLUDED.frozen_context_storage_path,
    pdf_report_path = EXCLUDED.pdf_report_path, steps = EXCLUDED.steps, step_states = EXCLUDED.step_states,
    profile_syntheses = EXCLUDED.profile_syntheses, source_identity_manifest = EXCLUDED.source_identity_manifest,
    execution_trace = EXCLUDED.execution_trace, execution_trace_storage_path = EXCLUDED.execution_trace_storage_path,
    context_variables = EXCLUDED.context_variables,
    context_variables_storage_path = EXCLUDED.context_variables_storage_path, is_resumable = EXCLUDED.is_resumable,
    prompt_tokens = EXCLUDED.prompt_tokens, completion_tokens = EXCLUDED.completion_tokens,
    cached_tokens = EXCLUDED.cached_tokens, reasoning_tokens = EXCLUDED.reasoning_tokens,
    cumulative_synthesis_tokens = EXCLUDED.cumulative_synthesis_tokens, dag_cost_usd = EXCLUDED.dag_cost_usd,
    cumulative_synthesis_cost = EXCLUDED.cumulative_synthesis_cost, cost_estimate = EXCLUDED.cost_estimate,
    models_used = EXCLUDED.models_used, execution_summary = EXCLUDED.execution_summary,
    metadata = EXCLUDED.metadata, duration_ms = EXCLUDED.duration_ms, error = EXCLUDED.error,
    updated_at = EXCLUDED.updated_at, completed_at = EXCLUDED.completed_at,
    created_by = EXCLUDED.created_by, organization_id = EXCLUDED.organization_id"""

_LIST_EXECUTIONS_SQL: str = f"SELECT {_EXECUTION_COLS} FROM executions"
_GET_EXECUTION_SQL: str = f"{_LIST_EXECUTIONS_SQL} WHERE id = $1::uuid"

_REPORT_ARTIFACT_COLS: str = """id, execution_id, workflow_id, profile_id, locale, title, status,
    storage_paths, metadata, custom_preface_md, error_message, has_pdf, created_at, updated_at"""

_UPSERT_REPORT_ARTIFACT_SQL: str = f"""INSERT INTO report_artifacts ({_REPORT_ARTIFACT_COLS}) VALUES (
    $1::uuid, $2::uuid, $3::uuid, $4::uuid, $5, $6, $7, $8::jsonb, $9::jsonb, $10, $11, $12,
    $13::timestamptz, $14::timestamptz
) ON CONFLICT (id) DO UPDATE SET execution_id = EXCLUDED.execution_id, workflow_id = EXCLUDED.workflow_id,
    profile_id = EXCLUDED.profile_id, locale = EXCLUDED.locale, title = EXCLUDED.title, status = EXCLUDED.status,
    storage_paths = EXCLUDED.storage_paths, metadata = EXCLUDED.metadata,
    custom_preface_md = EXCLUDED.custom_preface_md, error_message = EXCLUDED.error_message,
    updated_at = EXCLUDED.updated_at"""

_LIST_REPORT_ARTIFACTS_SQL: str = f"SELECT {_REPORT_ARTIFACT_COLS} FROM report_artifacts"
_GET_REPORT_ARTIFACT_SQL: str = f"{_LIST_REPORT_ARTIFACTS_SQL} WHERE id = $1::uuid"


async def _fetch_row(conn: _Conn, timeout: float, sql: str, uid: object, eid: str) -> AsyncPgRecordProtocol | None:
    """Execute fetchrow with timeout and translate driver errors to AppException."""
    try:
        return await conn.fetchrow(sql, uid, timeout=timeout)
    except Exception as exc:
        if isinstance(exc, AppException):
            raise
        msg = f"Failed to fetch entity '{eid}': {exc}"
        logger.error("[PostgresEntityAdapter] %s: %s", ErrorCodes.STORAGE_ACCESS_FAILED.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
        ) from exc


# Phase 3, Step 1: Extract report binary, execution, and report artifact persistence and hydration functions
async def save_report_binary_row(conn: _Conn, timeout: float, dto: ReportBinaryPayloadDTO) -> None:
    """Persist a ReportBinaryPayloadDTO into report_binaries (BYTEA TOAST) and mark has_pdf.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        dto: Validated ReportBinaryPayloadDTO instance.

    Raises:
        AppException: With VALIDATION_FAILED on size/ID error or STORAGE_ACCESS_FAILED on DB error.
    """
    if len(dto.pdf_bytes) != dto.size_bytes:
        msg = f"ReportBinaryPayloadDTO size_bytes ({dto.size_bytes}) != len(pdf_bytes) ({len(dto.pdf_bytes)})."
        logger.error("[PostgresEntityAdapter] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    report_uuid = parse_prefixed_uuid7(dto.report_id, EntityPrefix.REPORT)
    await execute_entity_upsert(
        conn,
        timeout,
        _SAVE_REPORT_BINARY_SQL,
        report_uuid,
        dto.mime_type,
        dto.pdf_bytes,
        dto.size_bytes,
        dto.created_at,
        entity_id=dto.report_id,
    )
    await execute_entity_upsert(conn, timeout, _MARK_REPORT_ARTIFACT_PDF_SQL, report_uuid, entity_id=dto.report_id)


async def get_report_binary_row(conn: _Conn, timeout: float, report_id: str) -> ReportBinaryPayloadDTO | None:
    """Retrieve a ReportBinaryPayloadDTO from report_binaries by canonical report_id.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        report_id: Canonical rep_<uuid7_hex> report identifier.

    Returns:
        Hydrated ReportBinaryPayloadDTO if found, or None.

    Raises:
        AppException: With VALIDATION_FAILED on invalid report_id or STORAGE_ACCESS_FAILED on query error.
    """
    report_uuid = parse_prefixed_uuid7(report_id, EntityPrefix.REPORT)
    row = await _fetch_row(conn, timeout, _GET_REPORT_BINARY_SQL, report_uuid, report_id)
    if row is None:
        return None

    raw_bytes = row["pdf_bytes"]
    pdf_bytes: bytes = b""
    if isinstance(raw_bytes, (bytes, bytearray, memoryview)):
        pdf_bytes = bytes(raw_bytes)
    row_dto = _ReportBinaryRowDTO.model_validate(
        {
            "report_id": format_prefixed_uuid7(_coerce_uuid_or_str(row["report_id"]), EntityPrefix.REPORT),
            "mime_type": row["mime_type"],
            "pdf_bytes": pdf_bytes,
            "size_bytes": row["size_bytes"],
            "created_at": row["created_at"],
        },
        strict=False,
    )
    return ReportBinaryPayloadDTO.model_validate(row_dto.model_dump())


def hydrate_execution_row(row: AsyncPgRecordProtocol) -> ExecutionRecord:
    """Hydrate an ExecutionRecord from an asyncpg database record.

    Args:
        row: Database record from executions.

    Returns:
        Validated ExecutionRecord domain model.
    """
    return ExecutionRecord.model_validate(
        {
            "id": format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.EXECUTION),
            "workflow_id": format_prefixed_uuid7(_coerce_uuid_or_str(row["workflow_id"]), EntityPrefix.WORKFLOW),
            "workflow_version": row["workflow_version"],
            "active_profile_id": _format_optional_uuid7(row["active_profile_id"], EntityPrefix.OUTPUT_PROFILE),
            "output_profile_id": _format_optional_uuid7(row["output_profile_id"], EntityPrefix.OUTPUT_PROFILE),
            "status": row["status"],
            "target_locale": row["target_locale"],
            "progress": row["progress"],
            "status_message": row["status_message"],
            "raw_inputs": _decode_jsonb_column(row["raw_inputs"]),
            "frozen_context": _decode_jsonb_column(row["frozen_context"]),
            "frozen_context_storage_path": row["frozen_context_storage_path"],
            "pdf_report_path": row["pdf_report_path"],
            "steps": _decode_jsonb_column(row["steps"]),
            "step_states": _decode_jsonb_column(row["step_states"]),
            "profile_syntheses": _decode_jsonb_column(row["profile_syntheses"]),
            "source_identity_manifest": _decode_jsonb_column(row["source_identity_manifest"]),
            "execution_trace": _decode_jsonb_column(row["execution_trace"]),
            "execution_trace_storage_path": row["execution_trace_storage_path"],
            "context_variables": _decode_jsonb_column(row["context_variables"]),
            "context_variables_storage_path": row["context_variables_storage_path"],
            "is_resumable": row["is_resumable"],
            "prompt_tokens": int(str(row["prompt_tokens"])),
            "completion_tokens": int(str(row["completion_tokens"])),
            "cached_tokens": int(str(row["cached_tokens"])),
            "reasoning_tokens": int(str(row["reasoning_tokens"])),
            "cumulative_synthesis_tokens": int(str(row["cumulative_synthesis_tokens"])),
            "dag_cost_usd": _coerce_float(row["dag_cost_usd"]),
            "cumulative_synthesis_cost": _coerce_float(row["cumulative_synthesis_cost"]),
            "cost_estimate": _coerce_float(row["cost_estimate"]),
            "models_used": _decode_jsonb_column(row["models_used"]),
            "execution_summary": _decode_jsonb_column(row["execution_summary"]),
            "metadata": _decode_jsonb_column(row["metadata"]),
            "duration_ms": int(str(row["duration_ms"])),
            "error": row["error"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "completed_at": row["completed_at"],
            "created_by": row["created_by"],
            "organization_id": _format_org_uuid7(row["organization_id"]),
        },
        strict=False,
    )


async def save_execution_row(conn: AsyncPgConnectionProtocol, timeout: float, record: ExecutionRecord) -> str:
    """Persist an ExecutionRecord into the PostgreSQL 19 executions table.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        record: Validated ExecutionRecord domain model.

    Returns:
        Canonical exe_<uuid7_hex> execution identifier.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
    """
    exec_uuid = parse_prefixed_uuid7(record.id, EntityPrefix.EXECUTION)
    wf_uuid = parse_prefixed_uuid7(record.workflow_id, EntityPrefix.WORKFLOW)
    active_prf_uuid = _parse_optional_uuid7(record.active_profile_id, EntityPrefix.OUTPUT_PROFILE)
    output_prf_uuid = _parse_optional_uuid7(record.output_profile_id, EntityPrefix.OUTPUT_PROFILE)
    org_uuid = _parse_org_uuid7(record.organization_id)
    dumped = record.model_dump(mode="json", exclude_none=True)

    return await execute_entity_upsert(
        conn,
        timeout,
        _SAVE_EXECUTION_SQL,
        exec_uuid,
        wf_uuid,
        record.workflow_version,
        active_prf_uuid,
        output_prf_uuid,
        record.status.value,
        record.target_locale,
        record.progress,
        record.status_message,
        to_json(dumped["raw_inputs"]).decode("utf-8"),
        _encode_optional_jsonb(record.frozen_context),
        record.frozen_context_storage_path,
        record.pdf_report_path,
        to_json(dumped["steps"]).decode("utf-8"),
        to_json(dumped["step_states"]).decode("utf-8"),
        to_json(dumped["profile_syntheses"]).decode("utf-8"),
        to_json(dumped["source_identity_manifest"]).decode("utf-8"),
        to_json(dumped["execution_trace"]).decode("utf-8"),
        record.execution_trace_storage_path,
        to_json(dumped["context_variables"]).decode("utf-8"),
        record.context_variables_storage_path,
        record.is_resumable,
        record.prompt_tokens,
        record.completion_tokens,
        record.cached_tokens,
        record.reasoning_tokens,
        record.cumulative_synthesis_tokens,
        record.dag_cost_usd,
        record.cumulative_synthesis_cost,
        record.cost_estimate,
        to_json(dumped["models_used"]).decode("utf-8"),
        _encode_optional_jsonb(record.execution_summary),
        _encode_optional_jsonb(record.metadata),
        record.duration_ms,
        record.error,
        record.created_at,
        record.updated_at,
        record.completed_at,
        record.created_by,
        org_uuid,
        entity_id=record.id,
        entity_label="execution",
    )


async def get_execution_row(conn: AsyncPgConnectionProtocol, timeout: float, exec_id: str) -> ExecutionRecord | None:
    """Retrieve and reconstitute an ExecutionRecord from PostgreSQL by execution_id.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        exec_id: Canonical exe_<uuid7_hex> execution identifier.

    Returns:
        Reconstituted ExecutionRecord instance or None if not found.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED on query error.
    """
    exec_uuid = parse_prefixed_uuid7(exec_id, EntityPrefix.EXECUTION)
    row = await _fetch_row(conn, timeout, _GET_EXECUTION_SQL, exec_uuid, exec_id)
    if row is None:
        return None
    return hydrate_execution_row(row)


def hydrate_report_artifact_row(row: AsyncPgRecordProtocol) -> ReportArtifact:
    """Hydrate a ReportArtifact from a database row.

    Args:
        row: Database record from the report_artifacts table.

    Returns:
        Validated ReportArtifact domain model.
    """
    return ReportArtifact.model_validate(
        {
            "id": format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.REPORT),
            "execution_id": format_prefixed_uuid7(_coerce_uuid_or_str(row["execution_id"]), EntityPrefix.EXECUTION),
            "workflow_id": format_prefixed_uuid7(_coerce_uuid_or_str(row["workflow_id"]), EntityPrefix.WORKFLOW),
            "profile_id": format_prefixed_uuid7(_coerce_uuid_or_str(row["profile_id"]), EntityPrefix.OUTPUT_PROFILE),
            "locale": row["locale"],
            "title": row["title"],
            "status": row["status"],
            "storage_paths": _decode_jsonb_column(row["storage_paths"]),
            "metadata": _decode_jsonb_column(row["metadata"]),
            "custom_preface_md": row["custom_preface_md"],
            "error_message": row["error_message"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        },
        strict=False,
    )


async def upsert_report_artifact_row(conn: AsyncPgConnectionProtocol, timeout: float, artifact: ReportArtifact) -> str:
    """Persist a ReportArtifact into report_artifacts.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        artifact: Validated ReportArtifact domain model.

    Returns:
        Canonical rep_<uuid7_hex> report artifact identifier.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
    """
    report_uuid = parse_prefixed_uuid7(artifact.id, EntityPrefix.REPORT)
    exec_uuid = parse_prefixed_uuid7(artifact.execution_id, EntityPrefix.EXECUTION)
    wf_uuid = parse_prefixed_uuid7(artifact.workflow_id, EntityPrefix.WORKFLOW)
    prf_uuid = parse_prefixed_uuid7(artifact.profile_id, EntityPrefix.OUTPUT_PROFILE)
    dumped = artifact.model_dump(mode="json")
    return await execute_entity_upsert(
        conn,
        timeout,
        _UPSERT_REPORT_ARTIFACT_SQL,
        report_uuid,
        exec_uuid,
        wf_uuid,
        prf_uuid,
        artifact.locale,
        artifact.title,
        str(artifact.status),
        to_json(dumped["storage_paths"]).decode("utf-8"),
        to_json(dumped["metadata"]).decode("utf-8"),
        artifact.custom_preface_md,
        artifact.error_message,
        False,
        artifact.created_at,
        artifact.updated_at,
        entity_id=artifact.id,
        entity_label="report_artifact",
    )


async def get_report_artifact_row(conn: _Conn, timeout: float, rep_id: str) -> ReportArtifact | None:
    """Fetch a ReportArtifact by ID.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        rep_id: Canonical rep_<uuid7_hex> report artifact identifier.

    Returns:
        Hydrated ReportArtifact instance if found, or None.

    Raises:
        AppException: With VALIDATION_FAILED on invalid report_id or STORAGE_ACCESS_FAILED on query error.
    """
    report_uuid = parse_prefixed_uuid7(rep_id, EntityPrefix.REPORT)
    row = await _fetch_row(conn, timeout, _GET_REPORT_ARTIFACT_SQL, report_uuid, rep_id)
    if row is None:
        return None
    return hydrate_report_artifact_row(row)
