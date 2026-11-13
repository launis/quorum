"""PostgreSQL 19 SQL constants, hydration, and persistence stage for executions, payloads, and reports."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Never

from fastapi import status
from pydantic_core import to_json

from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    _coerce_float,
    _coerce_uuid_or_str,
    _decode_jsonb_column,
    _encode_optional_jsonb,
    _format_optional_uuid7,
    _parse_optional_uuid7,
    _ReportBinaryRowDTO,
    execute_entity_delete,
    execute_entity_upsert,
    resolve_effective_timeout,
    translate_postgres_exception,
    validate_hydrated_row,
)
from backend_v2.database.postgres.pool import AsyncPgConnectionProtocol, AsyncPgRecordProtocol
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.core_base import format_prefixed_uuid7, parse_prefixed_uuid7
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.proposition_graph import ReportBinaryPayloadDTO
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.dtos.trace import ExecutionUpdateDTO
from backend_v2.models.enums import EntityPrefix, ExecutionStatus
from backend_v2.models.state import WorkflowState

logger = logging.getLogger(__name__)
type _Conn = AsyncPgConnectionProtocol

# Ensure ExecutionRecord and ExecutionUpdateDTO deferred annotations are rebuilt
_ = WorkflowState
ExecutionRecord.model_rebuild()
ExecutionUpdateDTO.model_rebuild()

__all__ = [
    "_DELETE_EXECUTION_SQL",
    "_DELETE_REPORT_ARTIFACT_SQL",
    "_GET_EXECUTION_SQL",
    "_GET_REPORT_ARTIFACT_SQL",
    "_GET_REPORT_BINARY_SQL",
    "_LIST_EXECUTIONS_SQL",
    "_LIST_REPORT_ARTIFACTS_BY_EXECUTION_SQL",
    "_LIST_REPORT_ARTIFACTS_SQL",
    "_MARK_REPORT_ARTIFACT_PDF_SQL",
    "_PROBE_EXECUTION_STATE_VERSION_SQL",
    "_SAVE_EXECUTION_SQL",
    "_SAVE_REPORT_BINARY_SQL",
    "_UPDATE_EXECUTION_OCC_SQL",
    "_UPSERT_EXECUTION_PAYLOAD_SQL",
    "_UPSERT_REPORT_ARTIFACT_SQL",
    "apply_execution_updates",
    "delete_execution_row",
    "delete_report_artifact_row",
    "get_execution_row",
    "get_report_artifact_row",
    "get_report_binary_row",
    "hydrate_execution_row",
    "hydrate_execution_summary_row",
    "hydrate_report_artifact_row",
    "list_execution_rows",
    "list_executions_filtered_rows",
    "list_report_artifacts_by_execution_row",
    "save_execution_row",
    "save_report_binary_row",
    "update_execution_occ_row",
    "upsert_report_artifact_row",
]

_SAVE_REPORT_BINARY_SQL: str = """INSERT INTO report_binaries (report_id, mime_type, pdf_bytes, size_bytes)
VALUES ($1::uuid, $2, $3::bytea, $4::bigint)
ON CONFLICT (report_id) DO UPDATE SET mime_type = EXCLUDED.mime_type, pdf_bytes = EXCLUDED.pdf_bytes,
    size_bytes = EXCLUDED.size_bytes"""

_MARK_REPORT_ARTIFACT_PDF_SQL: str = (
    "UPDATE report_artifacts SET has_pdf = TRUE, updated_at = CURRENT_TIMESTAMP WHERE id = $1::uuid"
)

_GET_REPORT_BINARY_SQL: str = (
    "SELECT report_id, mime_type, pdf_bytes, size_bytes, created_at FROM report_binaries WHERE report_id = $1::uuid"
)

_EXECUTION_COLS: str = """id, organization_id, workflow_id, workflow_version, state_version, output_profile_id,
    status, target_locale, progress, status_message, steps, source_identity_manifest, is_resumable,
    prompt_tokens, completion_tokens, cached_tokens, reasoning_tokens, cumulative_synthesis_tokens,
    dag_cost_usd, cumulative_synthesis_cost, cost_estimate, models_used, execution_summary, metadata,
    duration_ms, error, created_by, created_at, updated_at, completed_at"""

_EXECUTION_INSERT_COLS: str = """id, organization_id, workflow_id, workflow_version, state_version,
    output_profile_id, status, target_locale, progress, status_message, steps, source_identity_manifest,
    is_resumable, prompt_tokens, completion_tokens, cached_tokens, reasoning_tokens,
    cumulative_synthesis_tokens, dag_cost_usd, cumulative_synthesis_cost, cost_estimate, models_used,
    execution_summary, metadata, duration_ms, error, created_by, updated_at, completed_at"""

_SAVE_EXECUTION_SQL: str = f"""INSERT INTO executions ({_EXECUTION_INSERT_COLS}) VALUES (
    $1::uuid, $2::uuid, $3::uuid, $4, $5, $6::uuid, $7, $8, $9, $10, $11::jsonb, $12::jsonb,
    $13, $14::bigint, $15::bigint, $16::bigint, $17::bigint, $18::bigint, $19::numeric,
    $20::numeric, $21::numeric, $22::jsonb, $23::jsonb, $24::jsonb, $25::bigint, $26,
    $27::uuid, $28::timestamptz, $29::timestamptz
) ON CONFLICT (id) DO UPDATE SET
    organization_id = EXCLUDED.organization_id, workflow_id = EXCLUDED.workflow_id,
    workflow_version = EXCLUDED.workflow_version, state_version = EXCLUDED.state_version,
    output_profile_id = EXCLUDED.output_profile_id, status = EXCLUDED.status,
    target_locale = EXCLUDED.target_locale, progress = EXCLUDED.progress,
    status_message = EXCLUDED.status_message, steps = EXCLUDED.steps,
    source_identity_manifest = EXCLUDED.source_identity_manifest, is_resumable = EXCLUDED.is_resumable,
    prompt_tokens = EXCLUDED.prompt_tokens, completion_tokens = EXCLUDED.completion_tokens,
    cached_tokens = EXCLUDED.cached_tokens, reasoning_tokens = EXCLUDED.reasoning_tokens,
    cumulative_synthesis_tokens = EXCLUDED.cumulative_synthesis_tokens, dag_cost_usd = EXCLUDED.dag_cost_usd,
    cumulative_synthesis_cost = EXCLUDED.cumulative_synthesis_cost, cost_estimate = EXCLUDED.cost_estimate,
    models_used = EXCLUDED.models_used, execution_summary = EXCLUDED.execution_summary,
    metadata = EXCLUDED.metadata, duration_ms = EXCLUDED.duration_ms, error = EXCLUDED.error,
    created_by = EXCLUDED.created_by, updated_at = EXCLUDED.updated_at, completed_at = EXCLUDED.completed_at"""

_UPDATE_EXECUTION_OCC_SQL: str = """UPDATE executions SET
    organization_id = $3::uuid, workflow_id = $4::uuid, workflow_version = $5,
    output_profile_id = $6::uuid, status = $7, target_locale = $8, progress = $9,
    status_message = $10, steps = $11::jsonb, source_identity_manifest = $12::jsonb,
    is_resumable = $13, prompt_tokens = $14::bigint, completion_tokens = $15::bigint,
    cached_tokens = $16::bigint, reasoning_tokens = $17::bigint,
    cumulative_synthesis_tokens = $18::bigint, dag_cost_usd = $19::numeric,
    cumulative_synthesis_cost = $20::numeric, cost_estimate = $21::numeric,
    models_used = $22::jsonb, execution_summary = $23::jsonb, metadata = $24::jsonb,
    duration_ms = $25::bigint, error = $26, created_by = $27::uuid,
    updated_at = $28::timestamptz, completed_at = $29::timestamptz,
    state_version = state_version + 1
WHERE id = $1::uuid AND state_version = $2
RETURNING state_version"""

_PROBE_EXECUTION_STATE_VERSION_SQL: str = "SELECT state_version FROM executions WHERE id = $1::uuid"

_UPSERT_EXECUTION_PAYLOAD_SQL: str = """INSERT INTO execution_payloads (
    execution_id, raw_inputs, frozen_context, context_variables,
    execution_trace, profile_syntheses, updated_at
) VALUES (
    $1::uuid, $2::jsonb, $3::jsonb, $4::jsonb, $5::jsonb, $6::jsonb, $7::timestamptz
) ON CONFLICT (execution_id) DO UPDATE SET
    raw_inputs = EXCLUDED.raw_inputs, frozen_context = EXCLUDED.frozen_context,
    context_variables = EXCLUDED.context_variables, execution_trace = EXCLUDED.execution_trace,
    profile_syntheses = EXCLUDED.profile_syntheses, updated_at = EXCLUDED.updated_at"""

_SELECT_EXECUTIONS_BASE_SQL: str = f"SELECT {_EXECUTION_COLS} FROM executions"
_LIST_EXECUTIONS_SQL: str = f"{_SELECT_EXECUTIONS_BASE_SQL} ORDER BY created_at DESC"
_GET_EXECUTION_SQL: str = """SELECT
    e.id, e.organization_id, e.workflow_id, e.workflow_version, e.state_version, e.output_profile_id,
    e.status, e.target_locale, e.progress, e.status_message, e.steps, e.source_identity_manifest,
    e.is_resumable, e.prompt_tokens, e.completion_tokens, e.cached_tokens, e.reasoning_tokens,
    e.cumulative_synthesis_tokens, e.dag_cost_usd, e.cumulative_synthesis_cost, e.cost_estimate,
    e.models_used, e.execution_summary, e.metadata, e.duration_ms, e.error, e.created_by,
    e.created_at, e.updated_at, e.completed_at,
    ep.raw_inputs, ep.frozen_context, ep.context_variables, ep.execution_trace, ep.profile_syntheses
FROM executions e
INNER JOIN execution_payloads ep ON ep.execution_id = e.id
WHERE e.id = $1::uuid"""

_REPORT_ARTIFACT_COLS: str = """id, execution_id, workflow_id, profile_id, locale, title, status,
    storage_paths, metadata, custom_preface_md, error_message, has_pdf, created_at, updated_at"""

_REPORT_ARTIFACT_INSERT_COLS: str = """id, execution_id, workflow_id, profile_id, locale, title, status,
    storage_paths, metadata, custom_preface_md, error_message, has_pdf, updated_at"""

_UPSERT_REPORT_ARTIFACT_SQL: str = f"""INSERT INTO report_artifacts ({_REPORT_ARTIFACT_INSERT_COLS}) VALUES (
    $1::uuid, $2::uuid, $3::uuid, $4::uuid, $5, $6, $7, $8::jsonb, $9::jsonb, $10, $11, $12,
    $13::timestamptz
) ON CONFLICT (id) DO UPDATE SET execution_id = EXCLUDED.execution_id, workflow_id = EXCLUDED.workflow_id,
    profile_id = EXCLUDED.profile_id, locale = EXCLUDED.locale, title = EXCLUDED.title, status = EXCLUDED.status,
    storage_paths = EXCLUDED.storage_paths, metadata = EXCLUDED.metadata,
    custom_preface_md = EXCLUDED.custom_preface_md, error_message = EXCLUDED.error_message,
    updated_at = EXCLUDED.updated_at"""

_LIST_REPORT_ARTIFACTS_SQL: str = f"SELECT {_REPORT_ARTIFACT_COLS} FROM report_artifacts"
_GET_REPORT_ARTIFACT_SQL: str = f"{_LIST_REPORT_ARTIFACTS_SQL} WHERE id = $1::uuid"


async def _fetch_row(
    conn: _Conn, timeout: float | None, sql: str, uid: uuid.UUID, eid: str, table_name: str = "executions"
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


def hydrate_execution_summary_row(row: AsyncPgRecordProtocol) -> ExecutionRecord:
    """Hydrate a summary ExecutionRecord from the 30-column executions table without sidecar joins.

    Args:
        row: Database record from the hot executions table.

    Returns:
        Validated ExecutionRecord with default empty sidecar containers and frozen_context=None.

    Raises:
        AppException: With VALIDATION_FAILED if UUID identifiers or row fields are invalid.
    """
    exe_id = format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.EXECUTION)
    return validate_hydrated_row(
        ExecutionRecord,
        {
            "id": exe_id,
            "organization_id": format_prefixed_uuid7(
                _coerce_uuid_or_str(row["organization_id"]),
                EntityPrefix.ORGANIZATION,
            ),
            "workflow_id": format_prefixed_uuid7(_coerce_uuid_or_str(row["workflow_id"]), EntityPrefix.WORKFLOW),
            "workflow_version": row["workflow_version"],
            "state_version": int(str(row["state_version"])),
            "output_profile_id": _format_optional_uuid7(row["output_profile_id"], EntityPrefix.OUTPUT_PROFILE),
            "status": row["status"],
            "target_locale": row["target_locale"],
            "progress": row["progress"],
            "status_message": row["status_message"],
            "raw_inputs": {"dynamic_inputs": {}},
            "frozen_context": None,
            "steps": _decode_jsonb_column(row["steps"]),
            "profile_syntheses": {},
            "source_identity_manifest": _decode_jsonb_column(row["source_identity_manifest"]),
            "execution_trace": [],
            "context_variables": {},
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
            "created_by": _format_optional_uuid7(row["created_by"], EntityPrefix.USER),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "completed_at": row["completed_at"],
        },
        table_name="executions",
        entity_id=exe_id,
    )


def hydrate_execution_row(row: AsyncPgRecordProtocol) -> ExecutionRecord:
    """Hydrate a full ExecutionRecord from an INNER JOIN of executions and execution_payloads.

    Args:
        row: Database record combining hot executions columns and lz4 execution_payloads columns.

    Returns:
        Validated ExecutionRecord domain model including cold sidecar payloads.

    Raises:
        AppException: With VALIDATION_FAILED if UUID identifiers or JSONB sidecar payloads are invalid.
    """
    summary = hydrate_execution_summary_row(row)
    dumped = summary.model_dump(mode="json", exclude_none=True)
    dumped["raw_inputs"] = _decode_jsonb_column(row["raw_inputs"])
    dumped["frozen_context"] = _decode_jsonb_column(row["frozen_context"])
    dumped["context_variables"] = _decode_jsonb_column(row["context_variables"])
    dumped["execution_trace"] = _decode_jsonb_column(row["execution_trace"])
    dumped["profile_syntheses"] = _decode_jsonb_column(row["profile_syntheses"])
    return validate_hydrated_row(
        ExecutionRecord,
        dumped,
        table_name="executions",
        entity_id=summary.id,
    )


def _raise_missing_execution(execution_id: str) -> Never:
    """Log RFC 7807 structured error and raise ResourceNotFoundError (HTTP 404) for a missing execution."""
    msg = f"Execution with ID '{execution_id}' not found."
    logger.error(
        "[PostgresEntityAdapter] %s: %s",
        ErrorCodes.RESOURCE_NOT_FOUND.name,
        msg,
        exc_info=True,
        extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "execution_id": execution_id},
    )
    raise ResourceNotFoundError("Execution", execution_id)


async def _raise_execution_occ_miss(
    conn: _Conn,
    effective_timeout: float,
    exec_uuid: uuid.UUID,
    exec_id: str,
    expected_state_version: int,
) -> Never:
    """Probe executions.state_version on OCC update miss and raise 404 Not Found or 409 Conflict."""
    probe_row = await _fetch_row(conn, effective_timeout, _PROBE_EXECUTION_STATE_VERSION_SQL, exec_uuid, exec_id)
    if probe_row is None:
        _raise_missing_execution(exec_id)

    actual_state_version = int(str(probe_row["state_version"]))
    msg = (
        f"Optimistic concurrency conflict for execution '{exec_id}': "
        f"expected state_version={expected_state_version}, actual state_version={actual_state_version}."
    )
    logger.error(
        "[PostgresEntityAdapter] %s: %s",
        ErrorCodes.CONFLICT.name,
        msg,
        exc_info=True,
        extra={
            "error_code": ErrorCodes.CONFLICT.value,
            "execution_id": exec_id,
            "expected_state_version": expected_state_version,
            "actual_state_version": actual_state_version,
        },
    )
    raise AppException(
        message=msg,
        status_code=status.HTTP_409_CONFLICT,
        details={
            "error_code": ErrorCodes.CONFLICT.value,
            "execution_id": exec_id,
            "expected_state_version": expected_state_version,
            "actual_state_version": actual_state_version,
        },
    )


async def save_execution_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    record: ExecutionRecord,
    *,
    expected_state_version: int | None = None,
) -> str:
    """Persist an ExecutionRecord across executions and execution_payloads with atomic SQL OCC.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        record: Validated ExecutionRecord domain model with non-null organization_id.
        expected_state_version: Optional expected state_version for single-statement SQL OCC.

    Returns:
        Canonical exe_<uuid7_hex> execution identifier.

    Raises:
        ResourceNotFoundError: With RESOURCE_NOT_FOUND (HTTP 404) when expected_state_version targets a missing ID.
        AppException: With VALIDATION_FAILED on missing/invalid ID, CONFLICT on OCC version mismatch,
            or STORAGE_ACCESS_FAILED if persistence fails.
    """
    if record.organization_id is None:
        msg = f"Execution '{record.id}' requires a non-null canonical organization_id."
        logger.error(
            "[PostgresEntityAdapter] %s: %s",
            ErrorCodes.VALIDATION_FAILED.name,
            msg,
            exc_info=True,
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "execution_id": record.id},
        )
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "execution_id": record.id},
        )

    effective_timeout = resolve_effective_timeout(timeout)
    exec_uuid = parse_prefixed_uuid7(record.id, EntityPrefix.EXECUTION)
    org_uuid = parse_prefixed_uuid7(record.organization_id, EntityPrefix.ORGANIZATION)
    wf_uuid = parse_prefixed_uuid7(record.workflow_id, EntityPrefix.WORKFLOW)
    output_prf_uuid = _parse_optional_uuid7(record.output_profile_id, EntityPrefix.OUTPUT_PROFILE)
    created_by_uuid = _parse_optional_uuid7(record.created_by, EntityPrefix.USER)

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

    steps_json = to_json(dumped["steps"]).decode("utf-8")
    manifest_json = to_json(dumped["source_identity_manifest"]).decode("utf-8")
    models_used_json = to_json(dumped["models_used"]).decode("utf-8")
    raw_inputs_json = to_json(dumped["raw_inputs"]).decode("utf-8")
    context_vars_json = to_json(dumped["context_variables"]).decode("utf-8")
    trace_json = to_json(dumped["execution_trace"]).decode("utf-8")
    syntheses_json = to_json(dumped["profile_syntheses"]).decode("utf-8")

    if expected_state_version is None:
        await execute_entity_upsert(
            conn,
            effective_timeout,
            _SAVE_EXECUTION_SQL,
            exec_uuid,
            org_uuid,
            wf_uuid,
            record.workflow_version,
            record.state_version,
            output_prf_uuid,
            record.status.value,
            record.target_locale,
            record.progress,
            record.status_message,
            steps_json,
            manifest_json,
            record.is_resumable,
            record.prompt_tokens,
            record.completion_tokens,
            record.cached_tokens,
            record.reasoning_tokens,
            record.cumulative_synthesis_tokens,
            record.dag_cost_usd,
            record.cumulative_synthesis_cost,
            record.cost_estimate,
            models_used_json,
            execution_summary_json,
            metadata_json,
            record.duration_ms,
            record.error,
            created_by_uuid,
            record.updated_at,
            record.completed_at,
            entity_id=record.id,
            entity_label="execution",
        )
    else:
        try:
            occ_row = await conn.fetchrow(
                _UPDATE_EXECUTION_OCC_SQL,
                exec_uuid,
                expected_state_version,
                org_uuid,
                wf_uuid,
                record.workflow_version,
                output_prf_uuid,
                record.status.value,
                record.target_locale,
                record.progress,
                record.status_message,
                steps_json,
                manifest_json,
                record.is_resumable,
                record.prompt_tokens,
                record.completion_tokens,
                record.cached_tokens,
                record.reasoning_tokens,
                record.cumulative_synthesis_tokens,
                record.dag_cost_usd,
                record.cumulative_synthesis_cost,
                record.cost_estimate,
                models_used_json,
                execution_summary_json,
                metadata_json,
                record.duration_ms,
                record.error,
                created_by_uuid,
                record.updated_at,
                record.completed_at,
                timeout=effective_timeout,
            )
        except AppException:
            raise
        except Exception as exc:
            raise translate_postgres_exception(
                exc,
                operation="UPDATE",
                table_name="executions",
                entity_id=record.id,
            ) from exc
        if occ_row is None:
            await _raise_execution_occ_miss(conn, effective_timeout, exec_uuid, record.id, expected_state_version)

    return await execute_entity_upsert(
        conn,
        effective_timeout,
        _UPSERT_EXECUTION_PAYLOAD_SQL,
        exec_uuid,
        raw_inputs_json,
        frozen_context_json,
        context_vars_json,
        trace_json,
        syntheses_json,
        record.updated_at,
        entity_id=record.id,
        entity_label="execution_payload",
    )


async def get_execution_row(conn: AsyncPgConnectionProtocol, timeout: float, exec_id: str) -> ExecutionRecord | None:
    """Retrieve and reconstitute a full ExecutionRecord via INNER JOIN with execution_payloads.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        exec_id: Canonical exe_<uuid7_hex> execution identifier.

    Returns:
        Reconstituted ExecutionRecord instance or None if not found.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID/corrupt row or STORAGE_ACCESS_FAILED on query error.
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
    """List summary ExecutionRecord rows ordered by created_at DESC without sidecar joins.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.

    Returns:
        List of summary ExecutionRecord models ordered newest-first.

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
    return [hydrate_execution_summary_row(r) for r in rows]


async def list_executions_filtered_rows(
    conn: _Conn,
    timeout: float,
    *,
    organization_id: str | None = None,
    created_by: str | None = None,
    workflow_id: str | None = None,
    status: ExecutionStatus | None = None,
    limit: int = 100,
) -> list[ExecutionRecord]:
    """List summary ExecutionRecord rows filtered by indexed columns and ordered by id DESC.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        organization_id: Optional canonical org_<32_hex> organization filter.
        created_by: Optional canonical usr_<32_hex> creator filter.
        workflow_id: Optional canonical wf_<32_hex> workflow filter.
        status: Optional ExecutionStatus filter.
        limit: Maximum number of records to return.

    Returns:
        List of summary ExecutionRecord models ordered by id DESC.

    Raises:
        AppException: With VALIDATION_FAILED on invalid filter ID or STORAGE_ACCESS_FAILED on query error.
    """
    conditions: list[str] = []
    params: list[object] = []
    if organization_id is not None:
        org_uuid = parse_prefixed_uuid7(organization_id, EntityPrefix.ORGANIZATION)
        params.append(org_uuid)
        conditions.append(f"organization_id = ${len(params)}::uuid")
    if created_by is not None:
        usr_uuid = parse_prefixed_uuid7(created_by, EntityPrefix.USER)
        params.append(usr_uuid)
        conditions.append(f"created_by = ${len(params)}::uuid")
    if workflow_id is not None:
        wf_uuid = parse_prefixed_uuid7(workflow_id, EntityPrefix.WORKFLOW)
        params.append(wf_uuid)
        conditions.append(f"workflow_id = ${len(params)}::uuid")
    if status is not None:
        params.append(status.value)
        conditions.append(f"status = ${len(params)}")
    if limit <= 0:
        return []
    where_clause = ""
    if conditions:
        where_clause = f" WHERE {' AND '.join(conditions)}"
    params.append(limit)
    sql = f"{_SELECT_EXECUTIONS_BASE_SQL}{where_clause} ORDER BY id DESC LIMIT ${len(params)}"
    effective_timeout = resolve_effective_timeout(timeout)
    try:
        rows = await conn.fetch(sql, *params, timeout=effective_timeout)
    except AppException:
        raise
    except Exception as exc:
        raise translate_postgres_exception(
            exc,
            operation="SELECT",
            table_name="executions",
            entity_id="*",
        ) from exc
    return [hydrate_execution_summary_row(r) for r in rows]


_DELETE_EXECUTION_SQL: str = "DELETE FROM executions WHERE id = $1::uuid"
_LIST_REPORT_ARTIFACTS_BY_EXECUTION_SQL: str = (
    f"{_LIST_REPORT_ARTIFACTS_SQL} WHERE execution_id = $1::uuid ORDER BY created_at DESC"
)
_DELETE_REPORT_ARTIFACT_SQL: str = "DELETE FROM report_artifacts WHERE id = $1::uuid"


def _coalesce_optional[T](updated: T | None, current: T) -> T:
    """Return updated when explicitly provided as non-None, otherwise preserve current.

    Args:
        updated: Candidate replacement value from the partial update DTO.
        current: Existing value on the persisted ExecutionRecord.

    Returns:
        Resolved field value for the updated ExecutionRecord.
    """
    return current if updated is None else updated


def _resolve_updated_status_message(existing: ExecutionRecord, updates: ExecutionUpdateDTO) -> str | None:
    """Resolve status_message from current_step or current_step_name field presence.

    Args:
        existing: Currently persisted ExecutionRecord instance.
        updates: Partial ExecutionUpdateDTO describing requested field updates.

    Returns:
        Updated status message or None depending on explicit DTO field presence.
    """
    fields_set = updates.model_fields_set
    if "current_step" in fields_set:
        return updates.current_step
    if "current_step_name" in fields_set:
        return updates.current_step_name
    return existing.status_message


def _apply_nullable_execution_fields(record: ExecutionRecord, updates: ExecutionUpdateDTO) -> ExecutionRecord:
    """Apply nullable ExecutionUpdateDTO fields gated by model_fields_set membership.

    Args:
        record: Source ExecutionRecord instance.
        updates: Partial ExecutionUpdateDTO describing requested field updates.

    Returns:
        ExecutionRecord copy with explicitly supplied nullable fields applied.
    """
    fields_set = updates.model_fields_set
    return record.model_copy(
        update={
            "progress": updates.progress if "progress" in fields_set else record.progress,
            "error": updates.error if "error" in fields_set else record.error,
            "output_profile_id": (
                updates.output_profile_id if "output_profile_id" in fields_set else record.output_profile_id
            ),
            "metadata": updates.metadata if "metadata" in fields_set else record.metadata,
            "execution_summary": (
                updates.execution_summary if "execution_summary" in fields_set else record.execution_summary
            ),
            "completed_at": updates.completed_at if "completed_at" in fields_set else record.completed_at,
        }
    )


def apply_execution_updates(existing: ExecutionRecord, updates: ExecutionUpdateDTO) -> ExecutionRecord:
    """Merge partial ExecutionUpdateDTO fields onto an existing ExecutionRecord.

    Args:
        existing: Currently persisted ExecutionRecord instance.
        updates: Partial ExecutionUpdateDTO describing requested field updates.

    Returns:
        Updated immutable ExecutionRecord prior to persistence-layer state_version increment.

    Raises:
        AppException: With VALIDATION_FAILED if the merged ExecutionRecord violates schema invariants.
    """
    stage1 = _apply_nullable_execution_fields(existing, updates)
    fields_set = updates.model_fields_set
    next_frozen_context = updates.frozen_context if "frozen_context" in fields_set else stage1.frozen_context
    next_state_version = stage1.state_version
    if updates.expected_state_version is None and updates.state_version is not None:
        next_state_version = updates.state_version

    merged = stage1.model_copy(
        update={
            "status": _coalesce_optional(updates.status, stage1.status),
            "status_message": _resolve_updated_status_message(stage1, updates),
            "steps": _coalesce_optional(updates.steps, stage1.steps),
            "execution_trace": _coalesce_optional(updates.execution_trace, stage1.execution_trace),
            "frozen_context": next_frozen_context,
            "profile_syntheses": _coalesce_optional(updates.profile_syntheses, stage1.profile_syntheses),
            "context_variables": _coalesce_optional(updates.context_variables, stage1.context_variables),
            "is_resumable": _coalesce_optional(updates.is_resumable, stage1.is_resumable),
            "prompt_tokens": _coalesce_optional(updates.prompt_tokens, stage1.prompt_tokens),
            "completion_tokens": _coalesce_optional(updates.completion_tokens, stage1.completion_tokens),
            "cached_tokens": _coalesce_optional(updates.cached_tokens, stage1.cached_tokens),
            "reasoning_tokens": _coalesce_optional(updates.reasoning_tokens, stage1.reasoning_tokens),
            "cumulative_synthesis_tokens": _coalesce_optional(
                updates.cumulative_synthesis_tokens,
                stage1.cumulative_synthesis_tokens,
            ),
            "dag_cost_usd": _coalesce_optional(updates.dag_cost_usd, stage1.dag_cost_usd),
            "cumulative_synthesis_cost": _coalesce_optional(
                updates.cumulative_synthesis_cost,
                stage1.cumulative_synthesis_cost,
            ),
            "duration_ms": _coalesce_optional(updates.duration_ms, stage1.duration_ms),
            "cost_estimate": _coalesce_optional(updates.cost_estimate, stage1.cost_estimate),
            "models_used": _coalesce_optional(updates.models_used, stage1.models_used),
            "created_at": _coalesce_optional(updates.created_at, stage1.created_at),
            "updated_at": _coalesce_optional(updates.updated_at, datetime.now(UTC)),
            "state_version": next_state_version,
        }
    )
    dumped = merged.model_dump(mode="json", exclude_none=True)
    if merged.frozen_context is None:
        dumped["frozen_context"] = None
    return validate_hydrated_row(
        ExecutionRecord,
        dumped,
        table_name="executions",
        entity_id=existing.id,
    )


async def update_execution_occ_row(
    conn: _Conn,
    timeout: float,
    execution_id: str,
    updates: ExecutionUpdateDTO,
) -> bool:
    """Apply partial ExecutionUpdateDTO updates to an existing ExecutionRecord with SQL OCC checking.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        execution_id: Canonical exe_<hex32> execution identifier.
        updates: Validated ExecutionUpdateDTO carrying field updates and optional expected_state_version.

    Returns:
        True when the execution and its execution_payloads sidecar are atomically updated.

    Raises:
        ResourceNotFoundError: With RESOURCE_NOT_FOUND (HTTP 404) when execution_id does not exist.
        AppException: With VALIDATION_FAILED on invalid ID/payload, CONFLICT on OCC mismatch,
            or STORAGE_ACCESS_FAILED on database error.
    """
    existing = await get_execution_row(conn, timeout, execution_id)
    if existing is None:
        _raise_missing_execution(execution_id)
    merged = apply_execution_updates(existing, updates)
    resolved_expected: int | None = updates.expected_state_version
    if resolved_expected is None and updates.state_version is None:
        resolved_expected = existing.state_version
    await save_execution_row(
        conn,
        timeout,
        merged,
        expected_state_version=resolved_expected,
    )
    return True


async def delete_execution_row(conn: _Conn, timeout: float, execution_id: str) -> bool:
    """Delete an ExecutionRecord row by primary key from executions.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        execution_id: Canonical exe_<hex32> execution identifier.

    Returns:
        True if a matching row was deleted, False otherwise.

    Raises:
        AppException: With VALIDATION_FAILED, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
    """
    exec_uuid = parse_prefixed_uuid7(execution_id, EntityPrefix.EXECUTION)
    return await execute_entity_delete(
        conn,
        timeout,
        _DELETE_EXECUTION_SQL,
        exec_uuid,
        entity_id=execution_id,
        table="executions",
    )


async def list_report_artifacts_by_execution_row(
    conn: _Conn,
    timeout: float,
    execution_id: str,
) -> list[ReportArtifact]:
    """List all ReportArtifact rows belonging to a parent execution ordered newest-first.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        execution_id: Canonical exe_<hex32> parent execution identifier.

    Returns:
        List of hydrated ReportArtifact models ordered by created_at DESC.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID/corrupt row or STORAGE_ACCESS_FAILED on query error.
    """
    exec_uuid = parse_prefixed_uuid7(execution_id, EntityPrefix.EXECUTION)
    effective_timeout = resolve_effective_timeout(timeout)
    try:
        rows = await conn.fetch(_LIST_REPORT_ARTIFACTS_BY_EXECUTION_SQL, exec_uuid, timeout=effective_timeout)
    except AppException:
        raise
    except Exception as exc:
        raise translate_postgres_exception(
            exc,
            operation="SELECT",
            table_name="report_artifacts",
            entity_id=execution_id,
        ) from exc
    return [hydrate_report_artifact_row(row) for row in rows]


async def delete_report_artifact_row(conn: _Conn, timeout: float, report_id: str) -> bool:
    """Delete a ReportArtifact row by primary key from report_artifacts.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        report_id: Canonical rep_<hex32> report artifact identifier.

    Returns:
        True if a matching row was deleted, False otherwise.

    Raises:
        AppException: With VALIDATION_FAILED, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
    """
    report_uuid = parse_prefixed_uuid7(report_id, EntityPrefix.REPORT)
    return await execute_entity_delete(
        conn,
        timeout,
        _DELETE_REPORT_ARTIFACT_SQL,
        report_uuid,
        entity_id=report_id,
        table="report_artifacts",
    )
