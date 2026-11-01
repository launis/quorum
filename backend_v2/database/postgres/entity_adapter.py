"""PostgreSQL 19 Zero-ORM Entity Persistence Adapter & lz4 TOAST Report Binary Streaming.

Implements EntityPersistencePort over asyncpg connections for clean-slate persistence
of all 10 domain entity and binary tables (organizations, users, system_configs,
prompt_blocks, steps, workflows, output_profiles, executions, report_artifacts,
and report_binaries).
"""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from pathlib import Path

from fastapi import status
from pydantic import BaseModel, JsonValue
from pydantic_core import to_json

# Phase 1, Step 2: Declare __path__ so entity_adapter sub-modules resolve while entity_adapter.py exists
__path__: list[str] = [str(Path(__file__).resolve().with_suffix(""))]
if __spec__ is not None:
    __spec__.submodule_search_locations = __path__

from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    _COLLECTION_TO_TABLE_MAP as _COLLECTION_TO_TABLE_MAP,
)
from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    _ROOT_SYSTEM_ORG_UUID7 as _ROOT_SYSTEM_ORG_UUID7,
)
from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    _SYSTEM_ORG_UUID7 as _SYSTEM_ORG_UUID7,
)
from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    _TABLE_TO_ENTITY_PREFIX as _TABLE_TO_ENTITY_PREFIX,
)
from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    CANONICAL_SEED_TABLES as CANONICAL_SEED_TABLES,
)
from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    _coerce_float as _coerce_float,
)
from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    _coerce_uuid_or_str as _coerce_uuid_or_str,
)
from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    _decode_jsonb_column as _decode_jsonb_column,
)
from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    _encode_optional_jsonb as _encode_optional_jsonb,
)
from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    _format_optional_uuid7 as _format_optional_uuid7,
)
from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    _format_org_uuid7 as _format_org_uuid7,
)
from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    _parse_optional_uuid7 as _parse_optional_uuid7,
)
from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    _parse_org_uuid7 as _parse_org_uuid7,
)
from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    _ReportBinaryRowDTO as _ReportBinaryRowDTO,
)
from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    execute_entity_upsert as execute_entity_upsert,
)
from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    resolve_effective_timeout as resolve_effective_timeout,
)
from backend_v2.database.postgres.entity_adapter.iam_and_system_stage import (
    _GET_ORGANIZATION_SQL as _GET_ORGANIZATION_SQL,
)
from backend_v2.database.postgres.entity_adapter.iam_and_system_stage import (
    _GET_SYSTEM_CONFIG_SQL as _GET_SYSTEM_CONFIG_SQL,
)
from backend_v2.database.postgres.entity_adapter.iam_and_system_stage import (
    _GET_USER_SQL as _GET_USER_SQL,
)
from backend_v2.database.postgres.entity_adapter.iam_and_system_stage import (
    _LIST_ORGANIZATIONS_SQL as _LIST_ORGANIZATIONS_SQL,
)
from backend_v2.database.postgres.entity_adapter.iam_and_system_stage import (
    _LIST_SYSTEM_CONFIGS_SQL as _LIST_SYSTEM_CONFIGS_SQL,
)
from backend_v2.database.postgres.entity_adapter.iam_and_system_stage import (
    _LIST_USERS_SQL as _LIST_USERS_SQL,
)
from backend_v2.database.postgres.entity_adapter.iam_and_system_stage import (
    _UPSERT_ORGANIZATION_SQL as _UPSERT_ORGANIZATION_SQL,
)
from backend_v2.database.postgres.entity_adapter.iam_and_system_stage import (
    _UPSERT_SYSTEM_CONFIG_SQL as _UPSERT_SYSTEM_CONFIG_SQL,
)
from backend_v2.database.postgres.entity_adapter.iam_and_system_stage import (
    _UPSERT_USER_SQL as _UPSERT_USER_SQL,
)
from backend_v2.database.postgres.entity_adapter.iam_and_system_stage import (
    get_organization_row as get_organization_row,
)
from backend_v2.database.postgres.entity_adapter.iam_and_system_stage import (
    get_system_config_row as get_system_config_row,
)
from backend_v2.database.postgres.entity_adapter.iam_and_system_stage import (
    get_user_row as get_user_row,
)
from backend_v2.database.postgres.entity_adapter.iam_and_system_stage import (
    hydrate_organization_row as hydrate_organization_row,
)
from backend_v2.database.postgres.entity_adapter.iam_and_system_stage import (
    hydrate_system_config_row as hydrate_system_config_row,
)
from backend_v2.database.postgres.entity_adapter.iam_and_system_stage import (
    hydrate_user_row as hydrate_user_row,
)
from backend_v2.database.postgres.entity_adapter.iam_and_system_stage import (
    upsert_organization_row as upsert_organization_row,
)
from backend_v2.database.postgres.entity_adapter.iam_and_system_stage import (
    upsert_system_config_row as upsert_system_config_row,
)
from backend_v2.database.postgres.entity_adapter.iam_and_system_stage import (
    upsert_user_row as upsert_user_row,
)
from backend_v2.database.postgres.entity_adapter.prompt_block_and_step_stage import (
    _GET_PROMPT_BLOCK_SQL as _GET_PROMPT_BLOCK_SQL,
)
from backend_v2.database.postgres.entity_adapter.prompt_block_and_step_stage import (
    _GET_STEP_SQL as _GET_STEP_SQL,
)
from backend_v2.database.postgres.entity_adapter.prompt_block_and_step_stage import (
    _LIST_PROMPT_BLOCKS_SQL as _LIST_PROMPT_BLOCKS_SQL,
)
from backend_v2.database.postgres.entity_adapter.prompt_block_and_step_stage import (
    _LIST_STEPS_SQL as _LIST_STEPS_SQL,
)
from backend_v2.database.postgres.entity_adapter.prompt_block_and_step_stage import (
    _UPSERT_PROMPT_BLOCK_SQL as _UPSERT_PROMPT_BLOCK_SQL,
)
from backend_v2.database.postgres.entity_adapter.prompt_block_and_step_stage import (
    _UPSERT_STEP_SQL as _UPSERT_STEP_SQL,
)
from backend_v2.database.postgres.entity_adapter.prompt_block_and_step_stage import (
    get_prompt_block_row as get_prompt_block_row,
)
from backend_v2.database.postgres.entity_adapter.prompt_block_and_step_stage import (
    get_step_row as get_step_row,
)
from backend_v2.database.postgres.entity_adapter.prompt_block_and_step_stage import (
    hydrate_prompt_block_row as hydrate_prompt_block_row,
)
from backend_v2.database.postgres.entity_adapter.prompt_block_and_step_stage import (
    hydrate_step_row as hydrate_step_row,
)
from backend_v2.database.postgres.entity_adapter.prompt_block_and_step_stage import (
    upsert_prompt_block_row as upsert_prompt_block_row,
)
from backend_v2.database.postgres.entity_adapter.prompt_block_and_step_stage import (
    upsert_step_row as upsert_step_row,
)
from backend_v2.database.postgres.entity_adapter.workflow_and_profile_stage import (
    _GET_OUTPUT_PROFILE_SQL as _GET_OUTPUT_PROFILE_SQL,
)
from backend_v2.database.postgres.entity_adapter.workflow_and_profile_stage import (
    _GET_WORKFLOW_SQL as _GET_WORKFLOW_SQL,
)
from backend_v2.database.postgres.entity_adapter.workflow_and_profile_stage import (
    _LIST_OUTPUT_PROFILES_SQL as _LIST_OUTPUT_PROFILES_SQL,
)
from backend_v2.database.postgres.entity_adapter.workflow_and_profile_stage import (
    _LIST_WORKFLOWS_SQL as _LIST_WORKFLOWS_SQL,
)
from backend_v2.database.postgres.entity_adapter.workflow_and_profile_stage import (
    _UPSERT_OUTPUT_PROFILE_SQL as _UPSERT_OUTPUT_PROFILE_SQL,
)
from backend_v2.database.postgres.entity_adapter.workflow_and_profile_stage import (
    _UPSERT_WORKFLOW_SQL as _UPSERT_WORKFLOW_SQL,
)
from backend_v2.database.postgres.entity_adapter.workflow_and_profile_stage import (
    get_output_profile_row as get_output_profile_row,
)
from backend_v2.database.postgres.entity_adapter.workflow_and_profile_stage import (
    get_workflow_row as get_workflow_row,
)
from backend_v2.database.postgres.entity_adapter.workflow_and_profile_stage import (
    hydrate_output_profile_row as hydrate_output_profile_row,
)
from backend_v2.database.postgres.entity_adapter.workflow_and_profile_stage import (
    hydrate_workflow_row as hydrate_workflow_row,
)
from backend_v2.database.postgres.entity_adapter.workflow_and_profile_stage import (
    upsert_output_profile_row as upsert_output_profile_row,
)
from backend_v2.database.postgres.entity_adapter.workflow_and_profile_stage import (
    upsert_workflow_row as upsert_workflow_row,
)
from backend_v2.database.postgres.pool import (
    AsyncPgConnectionProtocol,
    AsyncPgRecordProtocol,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import Organization, User
from backend_v2.models.core_base import (
    format_prefixed_uuid7,
    parse_prefixed_uuid7,
)
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import (
    AnyPromptBlock,
    MatrixPromptBlock,
    PersonaPromptBlock,
    PromptBlockAdapter,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.domain.proposition_graph import ReportBinaryPayloadDTO
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.system_config import (
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
)
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.enums import EntityPrefix
from backend_v2.models.state import WorkflowState
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

# Ensure ExecutionRecord deferred annotations (TraceEvent union) are rebuilt
_ = WorkflowState
ExecutionRecord.model_rebuild()

__all__ = [
    "CANONICAL_SEED_TABLES",
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
    $2::uuid,
    $3,
    $4::uuid,
    $5::uuid,
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
    $40::uuid
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

_LIST_EXECUTIONS_SQL: str = """
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
"""

_UPSERT_REPORT_ARTIFACT_SQL: str = """
INSERT INTO report_artifacts (
    id, execution_id, workflow_id, profile_id, locale, title, status,
    storage_paths, metadata, custom_preface_md, error_message, has_pdf,
    created_at, updated_at
) VALUES (
    $1::uuid, $2::uuid, $3::uuid, $4::uuid, $5, $6, $7,
    $8::jsonb, $9::jsonb, $10, $11, $12,
    $13::timestamptz, $14::timestamptz
)
ON CONFLICT (id) DO UPDATE SET
    execution_id = EXCLUDED.execution_id,
    workflow_id = EXCLUDED.workflow_id,
    profile_id = EXCLUDED.profile_id,
    locale = EXCLUDED.locale,
    title = EXCLUDED.title,
    status = EXCLUDED.status,
    storage_paths = EXCLUDED.storage_paths,
    metadata = EXCLUDED.metadata,
    custom_preface_md = EXCLUDED.custom_preface_md,
    error_message = EXCLUDED.error_message,
    updated_at = EXCLUDED.updated_at
"""

_GET_REPORT_ARTIFACT_SQL: str = """
SELECT id, execution_id, workflow_id, profile_id, locale, title, status,
       storage_paths, metadata, custom_preface_md, error_message, has_pdf,
       created_at, updated_at
FROM report_artifacts
WHERE id = $1::uuid
"""

_LIST_REPORT_ARTIFACTS_SQL: str = """
SELECT id, execution_id, workflow_id, profile_id, locale, title, status,
       storage_paths, metadata, custom_preface_md, error_message, has_pdf,
       created_at, updated_at
FROM report_artifacts
"""


class PostgresEntityAdapter:
    """Zero-ORM PostgreSQL 19 adapter implementing EntityPersistencePort.

    Attributes:
        command_timeout_seconds: Bounded query timeout in seconds resolved from settings.py.
    """

    def __init__(
        self,
        connection: AsyncPgConnectionProtocol,
        command_timeout_seconds: float | None = None,
    ) -> None:
        """Initialize the PostgreSQL entity adapter over an active connection.

        Args:
            connection: Active database connection conforming to AsyncPgConnectionProtocol.
            command_timeout_seconds: Explicit command timeout in seconds, or None to use settings.py.
        """
        resolved_timeout = (
            command_timeout_seconds
            if command_timeout_seconds is not None
            else get_settings().postgres_command_timeout_seconds
        )
        self._conn: AsyncPgConnectionProtocol = connection
        self.command_timeout_seconds: float = resolved_timeout

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
                exc_info=True,
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
                exc_info=True,
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

    def _hydrate_execution_row(self, row: AsyncPgRecordProtocol) -> ExecutionRecord:
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

    async def save_execution(self, record: ExecutionRecord) -> str:
        """Persist an ExecutionRecord into the PostgreSQL 19 executions table.

        Args:
            record: Validated ExecutionRecord domain model.

        Returns:
            Canonical exe_<uuid7_hex> execution identifier.

        Raises:
            AppException: With VALIDATION_FAILED on invalid execution ID or
                STORAGE_ACCESS_FAILED if persistence fails.
        """
        exec_uuid = parse_prefixed_uuid7(record.id, EntityPrefix.EXECUTION)
        wf_uuid = parse_prefixed_uuid7(record.workflow_id, EntityPrefix.WORKFLOW)
        active_prf_uuid = _parse_optional_uuid7(record.active_profile_id, EntityPrefix.OUTPUT_PROFILE)
        output_prf_uuid = _parse_optional_uuid7(record.output_profile_id, EntityPrefix.OUTPUT_PROFILE)
        org_uuid = _parse_org_uuid7(record.organization_id)
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
                wf_uuid,
                record.workflow_version,
                active_prf_uuid,
                output_prf_uuid,
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
                org_uuid,
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
                exc_info=True,
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
                exc_info=True,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "execution_id": execution_id},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from exc

        if row is None:
            return None

        return self._hydrate_execution_row(row)

    async def _execute_upsert(
        self,
        sql: str,
        *args: object,
        entity_label: str,
        entity_id: str,
    ) -> str:
        """Execute a parameterized upsert statement and translate transport errors to AppException.

        Args:
            sql: Parameterized INSERT ... ON CONFLICT DO UPDATE statement.
            *args: Positional SQL bind arguments.
            entity_label: Human-readable entity type label for structured error logging.
            entity_id: Canonical Opaque Stripe ID of the entity being persisted.

        Returns:
            Canonical entity_id persisted into PostgreSQL 19.

        Raises:
            AppException: With STORAGE_ACCESS_FAILED if the database command fails.
        """
        # Phase 1, Step 2: Delegate _execute_upsert to execute_entity_upsert
        return await execute_entity_upsert(
            self._conn,
            self.command_timeout_seconds,
            sql,
            *args,
            entity_id=entity_id,
            entity_label=entity_label,
        )

    def _hydrate_organization_row(self, row: AsyncPgRecordProtocol) -> Organization:
        """Hydrate an Organization from a database row.

        Args:
            row: Database record from the organizations table.

        Returns:
            Validated Organization domain model.
        """
        # Phase 2, Step 2: Delegate _hydrate_organization_row to hydrate_organization_row
        return hydrate_organization_row(row)

    async def upsert_organization(self, org: Organization) -> str:
        """Persist an Organization into the organizations table.

        Args:
            org: Validated Organization domain model.

        Returns:
            Canonical org_<hex> organization identifier.

        Raises:
            AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
        """
        # Phase 2, Step 2: Delegate upsert_organization to upsert_organization_row
        return await upsert_organization_row(self._conn, self.command_timeout_seconds, org)

    async def get_organization(self, org_id: str) -> Organization | None:
        """Fetch an Organization by ID.

        Args:
            org_id: Canonical org_<hex> organization identifier.

        Returns:
            Hydrated Organization instance if found, or None.

        Raises:
            AppException: With VALIDATION_FAILED on invalid org_id or STORAGE_ACCESS_FAILED on query failure.
        """
        # Phase 2, Step 2: Delegate get_organization to get_organization_row
        return await get_organization_row(self._conn, self.command_timeout_seconds, org_id)

    def _hydrate_user_row(self, row: AsyncPgRecordProtocol) -> User:
        """Hydrate a User from a database row.

        Args:
            row: Database record from the users table.

        Returns:
            Validated User domain model.
        """
        # Phase 2, Step 2: Delegate _hydrate_user_row to hydrate_user_row
        return hydrate_user_row(row)

    async def upsert_user(self, user: User) -> str:
        """Persist a User into the users table.

        Args:
            user: Validated User domain model.

        Returns:
            Canonical usr_<hex> user identifier.

        Raises:
            AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
        """
        # Phase 2, Step 2: Delegate upsert_user to upsert_user_row
        return await upsert_user_row(self._conn, self.command_timeout_seconds, user)

    async def get_user(self, user_id: str) -> User | None:
        """Fetch a User by ID.

        Args:
            user_id: Canonical usr_<hex> user identifier.

        Returns:
            Hydrated User instance if found, or None.

        Raises:
            AppException: With VALIDATION_FAILED on invalid user_id or STORAGE_ACCESS_FAILED on query failure.
        """
        # Phase 2, Step 2: Delegate get_user to get_user_row
        return await get_user_row(self._conn, self.command_timeout_seconds, user_id)

    def _hydrate_system_config_row(
        self, row: AsyncPgRecordProtocol
    ) -> SystemConfigModelRegistry | SystemConfigMCPGateways:
        """Hydrate a polymorphic SystemConfig from a database row.

        Args:
            row: Database record from the system_configs table.

        Returns:
            Validated SystemConfigModelRegistry or SystemConfigMCPGateways instance.
        """
        # Phase 2, Step 2: Delegate _hydrate_system_config_row to hydrate_system_config_row
        return hydrate_system_config_row(row)

    async def upsert_system_config(self, cfg: SystemConfigModelRegistry | SystemConfigMCPGateways) -> str:
        """Persist a SystemConfigModelRegistry or SystemConfigMCPGateways into system_configs.

        Args:
            cfg: Validated SystemConfigModelRegistry or SystemConfigMCPGateways domain model.

        Returns:
            Canonical sys_<hex> system configuration identifier.

        Raises:
            AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
        """
        # Phase 2, Step 2: Delegate upsert_system_config to upsert_system_config_row
        return await upsert_system_config_row(self._conn, self.command_timeout_seconds, cfg)

    async def get_system_config(self, config_id: str) -> SystemConfigModelRegistry | SystemConfigMCPGateways | None:
        """Fetch a SystemConfig by ID.

        Args:
            config_id: Canonical sys_<hex> system configuration identifier.

        Returns:
            Hydrated SystemConfigModelRegistry or SystemConfigMCPGateways if found, or None.

        Raises:
            AppException: With VALIDATION_FAILED on invalid config_id or STORAGE_ACCESS_FAILED on query failure.
        """
        # Phase 2, Step 2: Delegate get_system_config to get_system_config_row
        return await get_system_config_row(self._conn, self.command_timeout_seconds, config_id)

    def _hydrate_prompt_block_row(self, row: AsyncPgRecordProtocol) -> AnyPromptBlock:
        """Hydrate a polymorphic AnyPromptBlock from a database row.

        Args:
            row: Database record from the prompt_blocks table.

        Returns:
            Validated MatrixPromptBlock, PersonaPromptBlock, ProtocolPromptBlock, or SystemRulePromptBlock.
        """
        # Phase 2, Step 2: Delegate _hydrate_prompt_block_row to hydrate_prompt_block_row
        return hydrate_prompt_block_row(row)

    async def upsert_prompt_block(self, block: AnyPromptBlock) -> str:
        """Persist a polymorphic AnyPromptBlock into prompt_blocks.

        Args:
            block: Validated concrete PromptBlock domain model.

        Returns:
            Canonical blk_<hex> prompt block identifier.

        Raises:
            AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
        """
        # Phase 2, Step 2: Delegate upsert_prompt_block to upsert_prompt_block_row
        return await upsert_prompt_block_row(self._conn, self.command_timeout_seconds, block)

    async def get_prompt_block(self, block_id: str) -> AnyPromptBlock | None:
        """Fetch an AnyPromptBlock by ID.

        Args:
            block_id: Canonical blk_<hex> prompt block identifier.

        Returns:
            Hydrated AnyPromptBlock instance if found, or None.

        Raises:
            AppException: With VALIDATION_FAILED on invalid block_id or STORAGE_ACCESS_FAILED on query failure.
        """
        # Phase 2, Step 2: Delegate get_prompt_block to get_prompt_block_row
        return await get_prompt_block_row(self._conn, self.command_timeout_seconds, block_id)

    def _hydrate_step_row(self, row: AsyncPgRecordProtocol) -> Step:
        """Hydrate a Step from a database row.

        Args:
            row: Database record from the steps table.

        Returns:
            Validated Step domain model.
        """
        # Phase 2, Step 2: Delegate _hydrate_step_row to hydrate_step_row
        return hydrate_step_row(row)

    async def upsert_step(self, step: Step) -> str:
        """Persist a Step into steps.

        Args:
            step: Validated Step domain model.

        Returns:
            Canonical stp_<hex> step identifier.

        Raises:
            AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
        """
        # Phase 2, Step 2: Delegate upsert_step to upsert_step_row
        return await upsert_step_row(self._conn, self.command_timeout_seconds, step)

    async def get_step(self, step_id: str) -> Step | None:
        """Fetch a Step by ID.

        Args:
            step_id: Canonical stp_<hex> step identifier.

        Returns:
            Hydrated Step instance if found, or None.

        Raises:
            AppException: With VALIDATION_FAILED on invalid step_id or STORAGE_ACCESS_FAILED on query failure.
        """
        # Phase 2, Step 2: Delegate get_step to get_step_row
        return await get_step_row(self._conn, self.command_timeout_seconds, step_id)

    def _hydrate_workflow_row(self, row: AsyncPgRecordProtocol) -> Workflow:
        """Hydrate a Workflow from a database row.

        Args:
            row: Database record from the workflows table.

        Returns:
            Validated Workflow domain model.
        """
        # Phase 2, Step 2: Delegate _hydrate_workflow_row to hydrate_workflow_row
        return hydrate_workflow_row(row)

    async def upsert_workflow(self, wf: Workflow) -> str:
        """Persist a Workflow into workflows.

        Args:
            wf: Validated Workflow domain model.

        Returns:
            Canonical wf_<hex> workflow identifier.

        Raises:
            AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
        """
        # Phase 2, Step 2: Delegate upsert_workflow to upsert_workflow_row
        return await upsert_workflow_row(self._conn, self.command_timeout_seconds, wf)

    async def get_workflow(self, workflow_id: str) -> Workflow | None:
        """Fetch a Workflow by ID.

        Args:
            workflow_id: Canonical wf_<hex> workflow identifier.

        Returns:
            Hydrated Workflow instance if found, or None.

        Raises:
            AppException: With VALIDATION_FAILED on invalid workflow_id or STORAGE_ACCESS_FAILED on query failure.
        """
        # Phase 2, Step 2: Delegate get_workflow to get_workflow_row
        return await get_workflow_row(self._conn, self.command_timeout_seconds, workflow_id)

    def _hydrate_output_profile_row(self, row: AsyncPgRecordProtocol) -> OutputProfile:
        """Hydrate an OutputProfile from a database row.

        Args:
            row: Database record from the output_profiles table.

        Returns:
            Validated OutputProfile domain model.
        """
        # Phase 2, Step 2: Delegate _hydrate_output_profile_row to hydrate_output_profile_row
        return hydrate_output_profile_row(row)

    async def upsert_output_profile(self, profile: OutputProfile) -> str:
        """Persist an OutputProfile into output_profiles.

        Args:
            profile: Validated OutputProfile domain model.

        Returns:
            Canonical prf_<hex> output profile identifier.

        Raises:
            AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
        """
        # Phase 2, Step 2: Delegate upsert_output_profile to upsert_output_profile_row
        return await upsert_output_profile_row(self._conn, self.command_timeout_seconds, profile)

    async def get_output_profile(self, profile_id: str) -> OutputProfile | None:
        """Fetch an OutputProfile by ID.

        Args:
            profile_id: Canonical prf_<hex> output profile identifier.

        Returns:
            Hydrated OutputProfile instance if found, or None.

        Raises:
            AppException: With VALIDATION_FAILED on invalid profile_id or STORAGE_ACCESS_FAILED on query failure.
        """
        # Phase 2, Step 2: Delegate get_output_profile to get_output_profile_row
        return await get_output_profile_row(self._conn, self.command_timeout_seconds, profile_id)

    def _hydrate_report_artifact_row(self, row: AsyncPgRecordProtocol) -> ReportArtifact:
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
                "profile_id": format_prefixed_uuid7(
                    _coerce_uuid_or_str(row["profile_id"]), EntityPrefix.OUTPUT_PROFILE
                ),
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

    async def upsert_report_artifact(self, artifact: ReportArtifact) -> str:
        """Persist a ReportArtifact into report_artifacts.

        Args:
            artifact: Validated ReportArtifact domain model.

        Returns:
            Canonical rep_<uuid7_hex> report artifact identifier.

        Raises:
            AppException: With VALIDATION_FAILED on invalid report ID or
                STORAGE_ACCESS_FAILED if persistence fails.
        """
        report_uuid = parse_prefixed_uuid7(artifact.id, EntityPrefix.REPORT)
        exec_uuid = parse_prefixed_uuid7(artifact.execution_id, EntityPrefix.EXECUTION)
        wf_uuid = parse_prefixed_uuid7(artifact.workflow_id, EntityPrefix.WORKFLOW)
        prf_uuid = parse_prefixed_uuid7(artifact.profile_id, EntityPrefix.OUTPUT_PROFILE)
        dumped = artifact.model_dump(mode="json")
        return await self._execute_upsert(
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
            entity_label="report_artifact",
            entity_id=artifact.id,
        )

    async def get_report_artifact(self, report_id: str) -> ReportArtifact | None:
        """Fetch a ReportArtifact by ID.

        Args:
            report_id: Canonical rep_<uuid7_hex> report artifact identifier.

        Returns:
            Hydrated ReportArtifact instance if found, or None.

        Raises:
            AppException: With VALIDATION_FAILED on invalid report_id.
        """
        report_uuid = parse_prefixed_uuid7(report_id, EntityPrefix.REPORT)
        row = await self._conn.fetchrow(_GET_REPORT_ARTIFACT_SQL, report_uuid, timeout=self.command_timeout_seconds)
        if row is None:
            return None
        return self._hydrate_report_artifact_row(row)

    async def seed_collection_batch(self, collection_name: str, items: Sequence[BaseModel]) -> int:
        """Idempotently upsert a validated batch of domain entities into PostgreSQL 19.

        Args:
            collection_name: Canonical seed collection or table name.
            items: Sequence of validated Pydantic BaseModel instances.

        Returns:
            Number of rows upserted.

        Raises:
            AppException: With VALIDATION_FAILED if collection_name or item type is unsupported,
                or STORAGE_ACCESS_FAILED if a database error occurs.
        """
        if collection_name not in _COLLECTION_TO_TABLE_MAP:
            msg = f"Unsupported seed collection '{collection_name}'."
            logger.error(
                "[PostgresEntityAdapter] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        table_name = _COLLECTION_TO_TABLE_MAP[collection_name]
        count = 0
        for item in items:
            if table_name == "organizations" and isinstance(item, Organization):
                await self.upsert_organization(item)
            elif table_name == "users" and isinstance(item, User):
                await self.upsert_user(item)
            elif table_name == "system_configs" and isinstance(
                item, (SystemConfigModelRegistry, SystemConfigMCPGateways)
            ):
                await self.upsert_system_config(item)
            elif table_name == "prompt_blocks" and isinstance(
                item, (MatrixPromptBlock, SystemRulePromptBlock, PersonaPromptBlock, ProtocolPromptBlock)
            ):
                await self.upsert_prompt_block(item)
            elif table_name == "steps" and isinstance(item, Step):
                await self.upsert_step(item)
            elif table_name == "workflows" and isinstance(item, Workflow):
                await self.upsert_workflow(item)
            elif table_name == "output_profiles" and isinstance(item, OutputProfile):
                await self.upsert_output_profile(item)
            elif table_name == "executions" and isinstance(item, ExecutionRecord):
                await self.save_execution(item)
            elif table_name == "report_artifacts" and isinstance(item, ReportArtifact):
                await self.upsert_report_artifact(item)
            elif table_name == "report_binaries" and isinstance(item, ReportBinaryPayloadDTO):
                await self.save_report_binary(item)
            else:
                msg = f"Item type '{type(item).__name__}' does not match target table '{table_name}'."
                logger.error(
                    "[PostgresEntityAdapter] %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    msg,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
            count += 1
        return count

    async def verify_seed_table_counts(self, expected_counts: Mapping[str, int]) -> dict[str, int]:
        """Verify row counts across the 10 core PostgreSQL 19 tables via SELECT count(*).

        Args:
            expected_counts: Mapping of collection/table name to minimum expected row count.

        Returns:
            Dictionary mapping canonical table name to actual row count in PostgreSQL 19.

        Raises:
            AppException: With VALIDATION_FAILED if expected_counts references an unknown table,
                or STORAGE_ACCESS_FAILED if any table fails query execution or has fewer rows than expected.
        """
        actual_counts: dict[str, int] = {}
        for table_name in CANONICAL_SEED_TABLES:
            sql = f"SELECT count(*) AS row_count FROM {table_name}"
            try:
                row = await self._conn.fetchrow(sql, timeout=self.command_timeout_seconds)
            except Exception as exc:
                if isinstance(exc, AppException):
                    raise
                msg = f"Failed to verify row count for table '{table_name}': {exc}"
                logger.error(
                    "[PostgresEntityAdapter] %s: %s",
                    ErrorCodes.STORAGE_ACCESS_FAILED.name,
                    msg,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "table": table_name},
                )
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
                ) from exc

            if row is None:
                row_count = 0
            else:
                row_count = int(str(row["row_count"]))
            actual_counts[table_name] = row_count

        for key, min_expected in expected_counts.items():
            target_table = _COLLECTION_TO_TABLE_MAP[key] if key in _COLLECTION_TO_TABLE_MAP else key
            if target_table not in actual_counts:
                msg = f"Unknown table '{target_table}' in verify_seed_table_counts."
                logger.error(
                    "[PostgresEntityAdapter] %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    msg,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
            if actual_counts[target_table] < min_expected:
                msg = (
                    f"Seed count verification failed for table '{target_table}': "
                    f"expected >= {min_expected}, got {actual_counts[target_table]}."
                )
                logger.error(
                    "[PostgresEntityAdapter] %s: %s",
                    ErrorCodes.STORAGE_ACCESS_FAILED.name,
                    msg,
                    extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "table": target_table},
                )
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
                )

        return actual_counts

    async def list_collection_documents(self, collection_name: str) -> list[dict[str, JsonValue]]:
        """List all documents from a canonical PostgreSQL 19 table as JSON-compatible dictionaries.

        Args:
            collection_name: Canonical collection or table name.

        Returns:
            List of serialized document dictionaries from the mapped table.
        """
        if collection_name not in _COLLECTION_TO_TABLE_MAP:
            return []
        table_name = _COLLECTION_TO_TABLE_MAP[collection_name]
        if table_name == "organizations":
            rows = await self._conn.fetch(_LIST_ORGANIZATIONS_SQL, timeout=self.command_timeout_seconds)
            return [self._hydrate_organization_row(r).model_dump(mode="json") for r in rows]
        if table_name == "users":
            rows = await self._conn.fetch(_LIST_USERS_SQL, timeout=self.command_timeout_seconds)
            return [self._hydrate_user_row(r).model_dump(mode="json") for r in rows]
        if table_name == "system_configs":
            rows = await self._conn.fetch(_LIST_SYSTEM_CONFIGS_SQL, timeout=self.command_timeout_seconds)
            return [self._hydrate_system_config_row(r).model_dump(mode="json") for r in rows]
        if table_name == "prompt_blocks":
            rows = await self._conn.fetch(_LIST_PROMPT_BLOCKS_SQL, timeout=self.command_timeout_seconds)
            return [self._hydrate_prompt_block_row(r).model_dump(mode="json") for r in rows]
        if table_name == "steps":
            rows = await self._conn.fetch(_LIST_STEPS_SQL, timeout=self.command_timeout_seconds)
            return [self._hydrate_step_row(r).model_dump(mode="json") for r in rows]
        if table_name == "workflows":
            rows = await self._conn.fetch(_LIST_WORKFLOWS_SQL, timeout=self.command_timeout_seconds)
            return [self._hydrate_workflow_row(r).model_dump(mode="json") for r in rows]
        if table_name == "output_profiles":
            rows = await self._conn.fetch(_LIST_OUTPUT_PROFILES_SQL, timeout=self.command_timeout_seconds)
            return [self._hydrate_output_profile_row(r).model_dump(mode="json") for r in rows]
        if table_name == "executions":
            rows = await self._conn.fetch(_LIST_EXECUTIONS_SQL, timeout=self.command_timeout_seconds)
            return [self._hydrate_execution_row(r).model_dump(mode="json") for r in rows]
        if table_name == "report_artifacts":
            rows = await self._conn.fetch(_LIST_REPORT_ARTIFACTS_SQL, timeout=self.command_timeout_seconds)
            return [self._hydrate_report_artifact_row(r).model_dump(mode="json") for r in rows]
        return []

    async def get_collection_document(self, collection_name: str, doc_id: str) -> dict[str, JsonValue] | None:
        """Fetch a single document by ID from a canonical PostgreSQL 19 table.

        Args:
            collection_name: Canonical collection or table name.
            doc_id: Primary document identifier.

        Returns:
            Serialized document dictionary if found and valid, or None.
        """
        if collection_name not in _COLLECTION_TO_TABLE_MAP:
            return None
        table_name = _COLLECTION_TO_TABLE_MAP[collection_name]
        entity: BaseModel | None = None
        try:
            if table_name == "organizations":
                entity = await self.get_organization(doc_id)
            elif table_name == "users":
                entity = await self.get_user(doc_id)
            elif table_name == "system_configs":
                entity = await self.get_system_config(doc_id)
            elif table_name == "prompt_blocks":
                entity = await self.get_prompt_block(doc_id)
            elif table_name == "steps":
                entity = await self.get_step(doc_id)
            elif table_name == "workflows":
                entity = await self.get_workflow(doc_id)
            elif table_name == "output_profiles":
                entity = await self.get_output_profile(doc_id)
            elif table_name == "executions":
                entity = await self.get_execution(doc_id)
            elif table_name == "report_artifacts":
                entity = await self.get_report_artifact(doc_id)
        except AppException:
            return None
        if entity is None:
            return None
        return entity.model_dump(mode="json")

    async def upsert_collection_document(
        self, collection_name: str, doc_id: str, data: Mapping[str, JsonValue]
    ) -> bool:
        """Validate and upsert a document dictionary into its canonical PostgreSQL 19 table if schema-valid.

        Args:
            collection_name: Canonical collection or table name.
            doc_id: Primary document identifier.
            data: Raw document dictionary to validate and persist.

        Returns:
            True if the document validated against the table's domain schema and was persisted, else False.
        """
        if collection_name not in _COLLECTION_TO_TABLE_MAP:
            return False
        table_name = _COLLECTION_TO_TABLE_MAP[collection_name]
        payload = {k: v for k, v in data.items()}
        payload["id"] = doc_id
        try:
            if table_name == "organizations":
                await self.upsert_organization(Organization.model_validate(payload, strict=False))
                return True
            if table_name == "users":
                await self.upsert_user(User.model_validate(payload, strict=False))
                return True
            if table_name == "system_configs":
                if "type" in payload and payload["type"] == "mcp_gateways":
                    await self.upsert_system_config(SystemConfigMCPGateways.model_validate(payload, strict=False))
                else:
                    await self.upsert_system_config(SystemConfigModelRegistry.model_validate(payload, strict=False))
                return True
            if table_name == "prompt_blocks":
                block = PromptBlockAdapter.validate_python(payload, strict=False)
                await self.upsert_prompt_block(block)
                return True
            if table_name == "steps":
                await self.upsert_step(Step.model_validate(payload, strict=False))
                return True
            if table_name == "workflows":
                await self.upsert_workflow(Workflow.model_validate(payload, strict=False))
                return True
            if table_name == "output_profiles":
                await self.upsert_output_profile(OutputProfile.model_validate(payload, strict=False))
                return True
            if table_name == "executions":
                await self.save_execution(ExecutionRecord.model_validate(payload, strict=False))
                return True
            if table_name == "report_artifacts":
                await self.upsert_report_artifact(ReportArtifact.model_validate(payload, strict=False))
                return True
        except ValueError, KeyError, TypeError, AppException:
            return False
        return False

    async def delete_collection_document(self, collection_name: str, doc_id: str) -> bool:
        """Delete a row by ID from a canonical PostgreSQL 19 table.

        Args:
            collection_name: Canonical collection or table name.
            doc_id: Primary document identifier.

        Returns:
            True if a row was deleted, else False.
        """
        if collection_name not in _COLLECTION_TO_TABLE_MAP:
            return False
        table_name = _COLLECTION_TO_TABLE_MAP[collection_name]
        if table_name not in _TABLE_TO_ENTITY_PREFIX:
            return False
        try:
            doc_uuid = (
                _ROOT_SYSTEM_ORG_UUID7
                if table_name == "organizations" and doc_id == "org_system000000"
                else parse_prefixed_uuid7(doc_id, _TABLE_TO_ENTITY_PREFIX[table_name])
            )
        except AppException:
            return False
        status_str = await self._conn.execute(
            f"DELETE FROM {table_name} WHERE id = $1::uuid",
            doc_uuid,
            timeout=self.command_timeout_seconds,
        )
        return status_str.endswith(" 1")

    async def clear_collection_documents(self, collection_name: str) -> None:
        """Delete all rows from a canonical PostgreSQL 19 table.

        Args:
            collection_name: Canonical collection or table name.
        """
        if collection_name not in _COLLECTION_TO_TABLE_MAP:
            return
        table_name = _COLLECTION_TO_TABLE_MAP[collection_name]
        await self._conn.execute(f"DELETE FROM {table_name}", timeout=self.command_timeout_seconds)
