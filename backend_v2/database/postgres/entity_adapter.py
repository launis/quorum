"""PostgreSQL 19 Zero-ORM Entity Persistence Adapter & lz4 TOAST Report Binary Streaming.

Implements EntityPersistencePort over asyncpg connections for clean-slate persistence
of executions (with Flat FinOps columns and lz4-compressed trace events) and
report_binaries (BYTEA TOAST storage).
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import status
from pydantic import ConfigDict, Field
from pydantic_core import from_json, to_json

from backend_v2.database.postgres.pool import (
    AsyncPgConnectionProtocol,
    AsyncPgRecordProtocol,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import (
    OPAQUE_STRIPE_ID_REGEX,
    V2CoreBase,
    format_prefixed_uuid7,
    parse_prefixed_uuid7,
)
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.proposition_graph import ReportBinaryPayloadDTO
from backend_v2.models.enums import EntityPrefix
from backend_v2.models.state import WorkflowState

logger = logging.getLogger(__name__)

# Ensure ExecutionRecord deferred annotations (TraceEvent union) are rebuilt
_ = WorkflowState
ExecutionRecord.model_rebuild()

__all__ = [
    "PostgresEntityAdapter",
]

_SAVE_REPORT_BINARY_SQL: str = """
INSERT INTO report_binaries (report_id, mime_type, pdf_bytes, size_bytes, created_at)
VALUES ($1::uuid, $2, $3::bytea, $4::bigint, $5::timestamptz)
ON CONFLICT (report_id) DO UPDATE SET
    mime_type = EXCLUDED.mime_type,
    pdf_bytes = EXCLUDED.pdf_bytes,
    size_bytes = EXCLUDED.size_bytes,
    created_at = EXCLUDED.created_at
"""

_MARK_REPORT_ARTIFACT_PDF_SQL: str = """
UPDATE report_artifacts
SET has_pdf = TRUE, updated_at = CURRENT_TIMESTAMP
WHERE id = $1::uuid
"""

_GET_REPORT_BINARY_SQL: str = """
SELECT report_id, mime_type, pdf_bytes, size_bytes, created_at
FROM report_binaries
WHERE report_id = $1::uuid
"""

_SAVE_EXECUTION_SQL: str = """
INSERT INTO executions (
    id,
    workflow_id,
    workflow_version,
    active_profile_id,
    output_profile_id,
    status,
    target_locale,
    progress,
    status_message,
    raw_inputs,
    frozen_context,
    frozen_context_storage_path,
    pdf_report_path,
    steps,
    step_states,
    profile_syntheses,
    source_identity_manifest,
    execution_trace,
    execution_trace_storage_path,
    context_variables,
    context_variables_storage_path,
    is_resumable,
    prompt_tokens,
    completion_tokens,
    cached_tokens,
    reasoning_tokens,
    cumulative_synthesis_tokens,
    dag_cost_usd,
    cumulative_synthesis_cost,
    cost_estimate,
    models_used,
    execution_summary,
    metadata,
    duration_ms,
    error,
    created_at,
    updated_at,
    completed_at,
    created_by,
    organization_id
) VALUES (
    $1::uuid,
    $2,
    $3,
    $4,
    $5,
    $6,
    $7,
    $8,
    $9,
    $10::jsonb,
    $11::jsonb,
    $12,
    $13,
    $14::jsonb,
    $15::jsonb,
    $16::jsonb,
    $17::jsonb,
    $18::jsonb,
    $19,
    $20::jsonb,
    $21,
    $22,
    $23::bigint,
    $24::bigint,
    $25::bigint,
    $26::bigint,
    $27::bigint,
    $28::numeric,
    $29::numeric,
    $30::numeric,
    $31::jsonb,
    $32::jsonb,
    $33::jsonb,
    $34::bigint,
    $35,
    $36::timestamptz,
    $37::timestamptz,
    $38::timestamptz,
    $39,
    $40
)
ON CONFLICT (id) DO UPDATE SET
    workflow_id = EXCLUDED.workflow_id,
    workflow_version = EXCLUDED.workflow_version,
    active_profile_id = EXCLUDED.active_profile_id,
    output_profile_id = EXCLUDED.output_profile_id,
    status = EXCLUDED.status,
    target_locale = EXCLUDED.target_locale,
    progress = EXCLUDED.progress,
    status_message = EXCLUDED.status_message,
    raw_inputs = EXCLUDED.raw_inputs,
    frozen_context = EXCLUDED.frozen_context,
    frozen_context_storage_path = EXCLUDED.frozen_context_storage_path,
    pdf_report_path = EXCLUDED.pdf_report_path,
    steps = EXCLUDED.steps,
    step_states = EXCLUDED.step_states,
    profile_syntheses = EXCLUDED.profile_syntheses,
    source_identity_manifest = EXCLUDED.source_identity_manifest,
    execution_trace = EXCLUDED.execution_trace,
    execution_trace_storage_path = EXCLUDED.execution_trace_storage_path,
    context_variables = EXCLUDED.context_variables,
    context_variables_storage_path = EXCLUDED.context_variables_storage_path,
    is_resumable = EXCLUDED.is_resumable,
    prompt_tokens = EXCLUDED.prompt_tokens,
    completion_tokens = EXCLUDED.completion_tokens,
    cached_tokens = EXCLUDED.cached_tokens,
    reasoning_tokens = EXCLUDED.reasoning_tokens,
    cumulative_synthesis_tokens = EXCLUDED.cumulative_synthesis_tokens,
    dag_cost_usd = EXCLUDED.dag_cost_usd,
    cumulative_synthesis_cost = EXCLUDED.cumulative_synthesis_cost,
    cost_estimate = EXCLUDED.cost_estimate,
    models_used = EXCLUDED.models_used,
    execution_summary = EXCLUDED.execution_summary,
    metadata = EXCLUDED.metadata,
    duration_ms = EXCLUDED.duration_ms,
    error = EXCLUDED.error,
    updated_at = EXCLUDED.updated_at,
    completed_at = EXCLUDED.completed_at,
    created_by = EXCLUDED.created_by,
    organization_id = EXCLUDED.organization_id
"""

_GET_EXECUTION_SQL: str = """
SELECT
    id,
    workflow_id,
    workflow_version,
    active_profile_id,
    output_profile_id,
    status,
    target_locale,
    progress,
    status_message,
    raw_inputs,
    frozen_context,
    frozen_context_storage_path,
    pdf_report_path,
    steps,
    step_states,
    profile_syntheses,
    source_identity_manifest,
    execution_trace,
    execution_trace_storage_path,
    context_variables,
    context_variables_storage_path,
    is_resumable,
    prompt_tokens,
    completion_tokens,
    cached_tokens,
    reasoning_tokens,
    cumulative_synthesis_tokens,
    dag_cost_usd,
    cumulative_synthesis_cost,
    cost_estimate,
    models_used,
    execution_summary,
    metadata,
    duration_ms,
    error,
    created_at,
    updated_at,
    completed_at,
    created_by,
    organization_id
FROM executions
WHERE id = $1::uuid
"""


class _ReportBinaryRowDTO(V2CoreBase):
    """Strict internal boundary DTO for hydrating a ReportBinaryPayloadDTO row.

    Attributes:
        report_id: Formatted rep_<uuid7_hex> identifier.
        mime_type: MIME type string.
        pdf_bytes: Raw binary PDF payload.
        size_bytes: Exact byte length.
        created_at: Creation timestamp.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    report_id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Report ID.")]
    mime_type: Annotated[str, Field(min_length=1, description="MIME type.")]
    pdf_bytes: Annotated[bytes, Field(description="PDF binary bytes.")]
    size_bytes: Annotated[int, Field(ge=0, description="Byte size.")]
    created_at: Annotated[datetime, Field(description="Creation timestamp.")]


def _coerce_uuid_or_str(raw: object) -> uuid.UUID | str:
    """Narrow a raw database UUID or string column value to uuid.UUID | str.

    Args:
        raw: Database value from an asyncpg record column.

    Returns:
        Value narrowed to uuid.UUID or str.
    """
    if isinstance(raw, (uuid.UUID, str)):
        return raw
    return str(raw)


def _decode_jsonb_column(raw: object) -> object:
    """Decode a JSONB column value if returned as raw UTF-8 string or bytes.

    Args:
        raw: Column value returned by asyncpg or InMemoryAsyncPgConnection.

    Returns:
        Decoded Python structure ready for Pydantic validation.
    """
    if raw is None:
        return None
    if isinstance(raw, (str, bytes, bytearray)):
        return from_json(raw)
    if isinstance(raw, memoryview):
        return from_json(bytes(raw))
    return raw


def _coerce_float(raw: object) -> float:
    """Convert a database NUMERIC/Decimal or float column value to float.

    Args:
        raw: Database numeric column value.

    Returns:
        Python float value.
    """
    if isinstance(raw, (float, int, Decimal)):
        return float(raw)
    return float(str(raw))


class PostgresEntityAdapter:
    """Zero-ORM PostgreSQL 19 adapter implementing EntityPersistencePort.

    Attributes:
        command_timeout_seconds: Bounded query timeout in seconds resolved from settings.py.
    """

    def __init__(
        self,
        connection: AsyncPgConnectionProtocol,
        command_timeout_seconds: float = 15.0,
    ) -> None:
        """Initialize the PostgreSQL entity adapter over an active connection.

        Args:
            connection: Active database connection conforming to AsyncPgConnectionProtocol.
            command_timeout_seconds: Explicit command timeout in seconds.
        """
        self._conn: AsyncPgConnectionProtocol = connection
        self.command_timeout_seconds: float = command_timeout_seconds

    async def save_report_binary(self, payload: ReportBinaryPayloadDTO) -> None:
        """Persist a ReportBinaryPayloadDTO into report_binaries (BYTEA TOAST) and mark has_pdf.

        Args:
            payload: Validated ReportBinaryPayloadDTO instance.

        Raises:
            AppException: With VALIDATION_FAILED if report_id is invalid or size_bytes mismatches
                len(pdf_bytes), or STORAGE_ACCESS_FAILED if persistence fails.
        """
        if len(payload.pdf_bytes) != payload.size_bytes:
            msg = (
                f"ReportBinaryPayloadDTO size_bytes ({payload.size_bytes}) does not match "
                f"actual pdf_bytes length ({len(payload.pdf_bytes)})."
            )
            logger.error(
                "[PostgresEntityAdapter] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "report_id": payload.report_id},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        report_uuid = parse_prefixed_uuid7(payload.report_id, EntityPrefix.REPORT)
        try:
            await self._conn.execute(
                _SAVE_REPORT_BINARY_SQL,
                report_uuid,
                payload.mime_type,
                payload.pdf_bytes,
                payload.size_bytes,
                payload.created_at,
                timeout=self.command_timeout_seconds,
            )
            await self._conn.execute(
                _MARK_REPORT_ARTIFACT_PDF_SQL,
                report_uuid,
                timeout=self.command_timeout_seconds,
            )
        except Exception as exc:
            if isinstance(exc, AppException):
                raise
            msg = f"Failed to persist report binary for '{payload.report_id}': {exc}"
            logger.error(
                "[PostgresEntityAdapter] %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "report_id": payload.report_id},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from exc

    async def get_report_binary(self, report_id: str) -> ReportBinaryPayloadDTO | None:
        """Retrieve a ReportBinaryPayloadDTO from report_binaries by canonical report_id.

        Args:
            report_id: Canonical rep_<uuid7_hex> report identifier.

        Returns:
            Hydrated ReportBinaryPayloadDTO if found, or None.

        Raises:
            AppException: With VALIDATION_FAILED on invalid report_id or STORAGE_ACCESS_FAILED on query error.
        """
        report_uuid = parse_prefixed_uuid7(report_id, EntityPrefix.REPORT)
        try:
            row: AsyncPgRecordProtocol | None = await self._conn.fetchrow(
                _GET_REPORT_BINARY_SQL,
                report_uuid,
                timeout=self.command_timeout_seconds,
            )
        except Exception as exc:
            if isinstance(exc, AppException):
                raise
            msg = f"Failed to fetch report binary for '{report_id}': {exc}"
            logger.error(
                "[PostgresEntityAdapter] %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "report_id": report_id},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from exc

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
        return ReportBinaryPayloadDTO(
            report_id=row_dto.report_id,
            mime_type=row_dto.mime_type,
            pdf_bytes=row_dto.pdf_bytes,
            size_bytes=row_dto.size_bytes,
            created_at=row_dto.created_at,
        )

    async def save_execution(self, record: ExecutionRecord) -> str:
        """Persist an ExecutionRecord into the PostgreSQL 19 executions table.

        Serializes trace events and nested DTOs with exclude_none=True to preserve
        Full-Duplex Serialization Parity across strict extra='forbid' consumers.

        Args:
            record: Validated ExecutionRecord domain model.

        Returns:
            Canonical exe_<uuid7_hex> execution identifier.

        Raises:
            AppException: With VALIDATION_FAILED on invalid execution ID or
                STORAGE_ACCESS_FAILED if persistence fails.
        """
        exec_uuid = parse_prefixed_uuid7(record.id, EntityPrefix.EXECUTION)
        dumped = record.model_dump(mode="json", exclude_none=True)

        frozen_ctx_json: str | None = None
        if record.frozen_context is not None:
            frozen_ctx_json = to_json(dumped["frozen_context"]).decode("utf-8")

        exec_summary_json: str | None = None
        if record.execution_summary is not None:
            exec_summary_json = to_json(dumped["execution_summary"]).decode("utf-8")

        metadata_json: str | None = None
        if record.metadata is not None:
            metadata_json = to_json(dumped["metadata"]).decode("utf-8")

        try:
            await self._conn.execute(
                _SAVE_EXECUTION_SQL,
                exec_uuid,
                record.workflow_id,
                record.workflow_version,
                record.active_profile_id,
                record.output_profile_id,
                record.status.value,
                record.target_locale,
                record.progress,
                record.status_message,
                to_json(dumped["raw_inputs"]).decode("utf-8"),
                frozen_ctx_json,
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
                exec_summary_json,
                metadata_json,
                record.duration_ms,
                record.error,
                record.created_at,
                record.updated_at,
                record.completed_at,
                record.created_by,
                record.organization_id,
                timeout=self.command_timeout_seconds,
            )
        except Exception as exc:
            if isinstance(exc, AppException):
                raise
            msg = f"Failed to persist execution '{record.id}': {exc}"
            logger.error(
                "[PostgresEntityAdapter] %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "execution_id": record.id},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from exc

        return record.id

    async def get_execution(self, execution_id: str) -> ExecutionRecord | None:
        """Retrieve and reconstitute an ExecutionRecord from PostgreSQL by execution_id.

        Args:
            execution_id: Canonical exe_<uuid7_hex> execution identifier.

        Returns:
            Reconstituted ExecutionRecord instance or None if not found.

        Raises:
            AppException: With VALIDATION_FAILED on invalid execution_id or
                STORAGE_ACCESS_FAILED if query execution fails.
        """
        exec_uuid = parse_prefixed_uuid7(execution_id, EntityPrefix.EXECUTION)
        try:
            row: AsyncPgRecordProtocol | None = await self._conn.fetchrow(
                _GET_EXECUTION_SQL,
                exec_uuid,
                timeout=self.command_timeout_seconds,
            )
        except Exception as exc:
            if isinstance(exc, AppException):
                raise
            msg = f"Failed to fetch execution '{execution_id}': {exc}"
            logger.error(
                "[PostgresEntityAdapter] %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "execution_id": execution_id},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from exc

        if row is None:
            return None

        return ExecutionRecord.model_validate(
            {
                "id": format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.EXECUTION),
                "workflow_id": row["workflow_id"],
                "workflow_version": row["workflow_version"],
                "active_profile_id": row["active_profile_id"],
                "output_profile_id": row["output_profile_id"],
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
                "organization_id": row["organization_id"],
            },
            strict=False,
        )
