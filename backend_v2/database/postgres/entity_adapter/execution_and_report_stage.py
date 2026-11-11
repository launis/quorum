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
    resolve_effective_timeout,
    translate_postgres_exception,
    validate_hydrated_row,
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
    "list_execution_rows",
    "save_execution_row",
    "save_report_binary_row",
    "upsert_report_artifact_row",
]

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
    duration_ms, error, created_at, updated_at, completed_at, created_by, organization_id, state_version"""

_SAVE_EXECUTION_SQL: str = f"""INSERT INTO executions ({_EXECUTION_COLS}) VALUES (
    $1::uuid, $2::uuid, $3, $4::uuid, $5::uuid, $6, $7, $8, $9, $10::jsonb, $11::jsonb, $12, $13, $14::jsonb,
    $15::jsonb, $16::jsonb, $17::jsonb, $18::jsonb, $19, $20::jsonb, $21, $22, $23::bigint, $24::bigint,
    $25::bigint, $26::bigint, $27::bigint, $28::numeric, $29::numeric, $30::numeric, $31::jsonb, $32::jsonb,
    $33::jsonb, $34::bigint, $35, $36::timestamptz, $37::timestamptz, $38::timestamptz, $39, $40::uuid, $41
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
    created_by = EXCLUDED.created_by, organization_id = EXCLUDED.organization_id,
    state_version = EXCLUDED.state_version"""

_SELECT_EXECUTIONS_BASE_SQL: str = f"SELECT {_EXECUTION_COLS} FROM executions"
_LIST_EXECUTIONS_SQL: str = f"{_SELECT_EXECUTIONS_BASE_SQL} ORDER BY created_at DESC"
_GET_EXECUTION_SQL: str = f"{_SELECT_EXECUTIONS_BASE_SQL} WHERE id = $1::uuid"

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


async def _fetch_row(
    conn: _Conn, timeout: float | None, sql: str, uid: object, eid: str, table_name: str = "executions"
) -> AsyncPgRecordProtocol | None:
    """Execute fetchrow with timeout and translate driver errors to AppException.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds, or None to resolve from settings.
        sql: Parameterized SELECT SQL statement.
        uid: Parsed 16-byte UUID primary key parameter.
        eid: Canonical Opaque Stripe ID of the target entity for error reporting.
        table_name: Canonical PostgreSQL table name for error reporting.

    Returns:
        Database record if found, or None.

    Raises:
        AppException: With STORAGE_ACCESS_FAILED if the database query fails.
    """
    effective_timeout = resolve_effective_timeout(timeout)
    try:
        return await conn.fetchrow(sql, uid, timeout=effective_timeout)
    except AppException:
        raise
    except Exception as exc:
        raise translate_postgres_exception(
            exc,
            operation="SELECT",
            table_name=table_name,
            entity_id=eid,
        ) from exc


async def save_report_binary_row(conn: _Conn, timeout: float | None, dto: ReportBinaryPayloadDTO) -> None:
    """Persist a ReportBinaryPayloadDTO into report_binaries (BYTEA TOAST) and mark has_pdf.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds, or None to resolve from settings.
        dto: Validated ReportBinaryPayloadDTO instance.

    Raises:
        AppException: With VALIDATION_FAILED on size/ID error or STORAGE_ACCESS_FAILED on DB error.
    """
    effective_timeout = resolve_effective_timeout(timeout)
    if len(dto.pdf_bytes) != dto.size_bytes:
        msg = f"ReportBinaryPayloadDTO size_bytes ({dto.size_bytes}) != len(pdf_bytes) ({len(dto.pdf_bytes)})."
        logger.error(
            "[PostgresEntityAdapter] %s: %s",
            ErrorCodes.VALIDATION_FAILED.name,
            msg,
            exc_info=True,
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "entity_id": dto.report_id},
        )
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    report_uuid = parse_prefixed_uuid7(dto.report_id, EntityPrefix.REPORT)
    await execute_entity_upsert(
        conn,
        effective_timeout,
        _SAVE_REPORT_BINARY_SQL,
        report_uuid,
        dto.mime_type,
        dto.pdf_bytes,
        dto.size_bytes,
        dto.created_at,
        entity_id=dto.report_id,
    )
    await execute_entity_upsert(
        conn, effective_timeout, _MARK_REPORT_ARTIFACT_PDF_SQL, report_uuid, entity_id=dto.report_id
    )


async def get_report_binary_row(conn: _Conn, timeout: float | None, report_id: str) -> ReportBinaryPayloadDTO | None:
    """Retrieve a ReportBinaryPayloadDTO from report_binaries by canonical report_id.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds, or None to resolve from settings.
        report_id: Canonical rep_<uuid7_hex> report identifier.

    Returns:
        Hydrated ReportBinaryPayloadDTO if found, or None.

    Raises:
        AppException: With VALIDATION_FAILED on invalid report_id or corrupt binary payload,
            or STORAGE_ACCESS_FAILED on query error.
    """
    report_uuid = parse_prefixed_uuid7(report_id, EntityPrefix.REPORT)
    row = await _fetch_row(conn, timeout, _GET_REPORT_BINARY_SQL, report_uuid, report_id, "report_binaries")
    if row is None:
        return None

    formatted_rep_id = format_prefixed_uuid7(_coerce_uuid_or_str(row["report_id"]), EntityPrefix.REPORT)
    row_dto = validate_hydrated_row(
        _ReportBinaryRowDTO,
        {
            "report_id": formatted_rep_id,
            "mime_type": row["mime_type"],
            "pdf_bytes": row["pdf_bytes"],
            "size_bytes": row["size_bytes"],
            "created_at": row["created_at"],
        },
        table_name="report_binaries",
        entity_id=formatted_rep_id,
    )
    return validate_hydrated_row(
        ReportBinaryPayloadDTO,
        row_dto.model_dump(),
        table_name="report_binaries",
        entity_id=row_dto.report_id,
    )


def hydrate_execution_row(row: AsyncPgRecordProtocol) -> ExecutionRecord:
    """Hydrate an ExecutionRecord from an asyncpg database record.

    Args:
        row: Database record from executions.

    Returns:
        Validated ExecutionRecord domain model.

    Raises:
        AppException: With VALIDATION_FAILED if UUID identifiers or row fields are invalid.
    """
    exe_id = format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.EXECUTION)
    return validate_hydrated_row(
        ExecutionRecord,
        {
            "id": exe_id,
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
            "state_version": int(str(row["state_version"])),
        },
        table_name="executions",
        entity_id=exe_id,
    )


async def save_execution_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    record: ExecutionRecord,
    *,
    expected_state_version: int | None = None,
) -> str:
    """Persist an ExecutionRecord into the PostgreSQL 19 executions table with OCC enforcement.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        record: Validated ExecutionRecord domain model.
        expected_state_version: Optional expected state_version for optimistic concurrency control.

    Returns:
        Canonical exe_<uuid7_hex> execution identifier.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID, CONFLICT on OCC version mismatch,
            or STORAGE_ACCESS_FAILED if persistence fails.
    """
    exec_uuid = parse_prefixed_uuid7(record.id, EntityPrefix.EXECUTION)
    wf_uuid = parse_prefixed_uuid7(record.workflow_id, EntityPrefix.WORKFLOW)
    active_prf_uuid = _parse_optional_uuid7(record.active_profile_id, EntityPrefix.OUTPUT_PROFILE)
    output_prf_uuid = _parse_optional_uuid7(record.output_profile_id, EntityPrefix.OUTPUT_PROFILE)
    org_uuid = _parse_org_uuid7(record.organization_id)
    # Enforce conditional expected_state_version OCC check and atomic increment
    persisted_state_version = record.state_version
    if expected_state_version is not None:
        existing = await get_execution_row(conn, timeout, record.id)
        actual_state_version = 1
        if existing is not None:
            actual_state_version = existing.state_version
        if actual_state_version != expected_state_version:
            msg = (
                f"Optimistic concurrency conflict for execution '{record.id}': "
                f"expected state_version={expected_state_version}, actual state_version={actual_state_version}."
            )
            logger.error(
                "[PostgresEntityAdapter] %s: %s",
                ErrorCodes.CONFLICT.name,
                msg,
                exc_info=True,
                extra={
                    "error_code": ErrorCodes.CONFLICT.value,
                    "execution_id": record.id,
                    "expected_state_version": expected_state_version,
                    "actual_state_version": actual_state_version,
                },
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_409_CONFLICT,
                details={
                    "error_code": ErrorCodes.CONFLICT.value,
                    "expected_state_version": expected_state_version,
                    "actual_state_version": actual_state_version,
                },
            )
        persisted_state_version = actual_state_version + 1
    dumped = record.model_dump(mode="json", exclude_none=True)
    frozen_context_json: str | None = None
    if record.frozen_context is not None:
        frozen_context_json = _encode_optional_jsonb(dumped["frozen_context"])
    execution_summary_json: str | None = None
    if record.execution_summary is not None:
        execution_summary_json = _encode_optional_jsonb(dumped["execution_summary"])
    metadata_json: str | None = None
    if record.metadata is not None:
        metadata_json = _encode_optional_jsonb(dumped["metadata"])

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
        frozen_context_json,
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
        execution_summary_json,
        metadata_json,
        record.duration_ms,
        record.error,
        record.created_at,
        record.updated_at,
        record.completed_at,
        record.created_by,
        org_uuid,
        persisted_state_version,
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

    Raises:
        AppException: With VALIDATION_FAILED if UUID identifiers or row fields are invalid.
    """
    rep_id = format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.REPORT)
    return validate_hydrated_row(
        ReportArtifact,
        {
            "id": rep_id,
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
        table_name="report_artifacts",
        entity_id=rep_id,
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
    row = await _fetch_row(conn, timeout, _GET_REPORT_ARTIFACT_SQL, report_uuid, rep_id, "report_artifacts")
    if row is None:
        return None
    return hydrate_report_artifact_row(row)


async def list_execution_rows(conn: _Conn, timeout: float) -> list[ExecutionRecord]:
    """List all ExecutionRecord rows ordered by created_at DESC.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.

    Returns:
        List of hydrated ExecutionRecord models ordered newest-first.

    Raises:
        AppException: With VALIDATION_FAILED on corrupt row or STORAGE_ACCESS_FAILED on query error.
    """
    effective_timeout = resolve_effective_timeout(timeout)
    try:
        rows = await conn.fetch(_LIST_EXECUTIONS_SQL, timeout=effective_timeout)
    except AppException:
        raise
    except Exception as exc:
        raise translate_postgres_exception(
            exc,
            operation="SELECT",
            table_name="executions",
            entity_id="*",
        ) from exc
    return [hydrate_execution_row(r) for r in rows]
