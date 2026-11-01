"""PostgreSQL 19 seed batch routing, table count verification, and generic collection CRUD stage."""

from __future__ import annotations

import logging
from collections.abc import Callable, Coroutine, Mapping, Sequence

from fastapi import status
from pydantic import BaseModel, JsonValue

import backend_v2.database.postgres.entity_adapter.execution_and_report_stage as _er
import backend_v2.database.postgres.entity_adapter.iam_and_system_stage as _iam
import backend_v2.database.postgres.entity_adapter.prompt_block_and_step_stage as _pbs
import backend_v2.database.postgres.entity_adapter.workflow_and_profile_stage as _wp
from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    _COLLECTION_TO_TABLE_MAP,
    _ROOT_SYSTEM_ORG_UUID7,
    _TABLE_TO_ENTITY_PREFIX,
    CANONICAL_SEED_TABLES,
)
from backend_v2.database.postgres.pool import AsyncPgConnectionProtocol, AsyncPgRecordProtocol
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import Organization, User
from backend_v2.models.core_base import parse_prefixed_uuid7
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PersonaPromptBlock,
    PromptBlockAdapter,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.domain.proposition_graph import ReportBinaryPayloadDTO
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.system_config import SystemConfigMCPGateways, SystemConfigModelRegistry
from backend_v2.models.domain.workflow import Workflow

logger = logging.getLogger(__name__)

__all__ = [
    "clear_collection_documents_rows",
    "delete_collection_document_row",
    "get_collection_document_row",
    "list_collection_documents_rows",
    "seed_collection_batch_rows",
    "upsert_collection_document_row",
    "verify_seed_table_counts_rows",
]

type _Conn = AsyncPgConnectionProtocol
type _HydrateFn = Callable[[AsyncPgRecordProtocol], BaseModel]
type _GetRowFn = Callable[[_Conn, float, str], Coroutine[object, object, BaseModel | None]]

_LIST_SPECS: dict[str, tuple[str, _HydrateFn]] = {
    "organizations": (_iam._LIST_ORGANIZATIONS_SQL, _iam.hydrate_organization_row),
    "users": (_iam._LIST_USERS_SQL, _iam.hydrate_user_row),
    "system_configs": (_iam._LIST_SYSTEM_CONFIGS_SQL, _iam.hydrate_system_config_row),
    "prompt_blocks": (_pbs._LIST_PROMPT_BLOCKS_SQL, _pbs.hydrate_prompt_block_row),
    "steps": (_pbs._LIST_STEPS_SQL, _pbs.hydrate_step_row),
    "workflows": (_wp._LIST_WORKFLOWS_SQL, _wp.hydrate_workflow_row),
    "output_profiles": (_wp._LIST_OUTPUT_PROFILES_SQL, _wp.hydrate_output_profile_row),
    "executions": (_er._LIST_EXECUTIONS_SQL, _er.hydrate_execution_row),
    "report_artifacts": (_er._LIST_REPORT_ARTIFACTS_SQL, _er.hydrate_report_artifact_row),
}

_GET_HANDLERS: dict[str, _GetRowFn] = {
    "organizations": _iam.get_organization_row,
    "users": _iam.get_user_row,
    "system_configs": _iam.get_system_config_row,
    "prompt_blocks": _pbs.get_prompt_block_row,
    "steps": _pbs.get_step_row,
    "workflows": _wp.get_workflow_row,
    "output_profiles": _wp.get_output_profile_row,
    "executions": _er.get_execution_row,
    "report_artifacts": _er.get_report_artifact_row,
}

_MODEL_CLASSES: dict[str, type[BaseModel]] = {
    "organizations": Organization,
    "users": User,
    "steps": Step,
    "workflows": Workflow,
    "output_profiles": OutputProfile,
    "executions": ExecutionRecord,
    "report_artifacts": ReportArtifact,
}


def _log_storage_error(msg: str, table: str, *, exc_info: bool = True) -> AppException:
    """Log a STORAGE_ACCESS_FAILED error and construct the corresponding AppException."""
    code = ErrorCodes.STORAGE_ACCESS_FAILED
    extra = {"error_code": code.value, "table": table}
    logger.error("[PostgresEntityAdapter] %s: %s", code.name, msg, exc_info=exc_info, extra=extra)
    return AppException(
        message=msg, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details={"error_code": code.value}
    )


def _log_validation_error(msg: str) -> AppException:
    """Log a VALIDATION_FAILED error and construct the corresponding AppException."""
    code = ErrorCodes.VALIDATION_FAILED
    logger.error("[PostgresEntityAdapter] %s: %s", code.name, msg, extra={"error_code": code.value})
    return AppException(message=msg, status_code=status.HTTP_400_BAD_REQUEST, details={"error_code": code.value})


async def _fetch_rows(conn: _Conn, timeout: float, sql: str, table_name: str) -> Sequence[AsyncPgRecordProtocol]:
    """Execute a table fetch query and translate transport errors to AppException."""
    try:
        return await conn.fetch(sql, timeout=timeout)
    except Exception as exc:
        if isinstance(exc, AppException):
            raise
        raise _log_storage_error(f"Failed to list rows from table '{table_name}': {exc}", table_name) from exc


# Phase 3, Step 1: Extract seed batching, table count verification, and generic collection CRUD functions
async def seed_collection_batch_rows(conn: _Conn, timeout: float, col_name: str, items: Sequence[BaseModel]) -> int:
    """Idempotently upsert a validated batch of domain entities into PostgreSQL 19.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        col_name: Canonical seed collection or table name.
        items: Sequence of validated Pydantic BaseModel instances.

    Returns:
        Number of rows upserted.

    Raises:
        AppException: With VALIDATION_FAILED on unsupported collection/type or STORAGE_ACCESS_FAILED on DB error.
    """
    if col_name not in _COLLECTION_TO_TABLE_MAP:
        raise _log_validation_error(f"Unsupported seed collection '{col_name}'.")

    table_name = _COLLECTION_TO_TABLE_MAP[col_name]
    count = 0
    for item in items:
        if table_name == "organizations" and isinstance(item, Organization):
            await _iam.upsert_organization_row(conn, timeout, item)
        elif table_name == "users" and isinstance(item, User):
            await _iam.upsert_user_row(conn, timeout, item)
        elif table_name == "system_configs" and isinstance(item, (SystemConfigModelRegistry, SystemConfigMCPGateways)):
            await _iam.upsert_system_config_row(conn, timeout, item)
        elif table_name == "prompt_blocks" and isinstance(
            item, (MatrixPromptBlock, SystemRulePromptBlock, PersonaPromptBlock, ProtocolPromptBlock)
        ):
            await _pbs.upsert_prompt_block_row(conn, timeout, item)
        elif table_name == "steps" and isinstance(item, Step):
            await _pbs.upsert_step_row(conn, timeout, item)
        elif table_name == "workflows" and isinstance(item, Workflow):
            await _wp.upsert_workflow_row(conn, timeout, item)
        elif table_name == "output_profiles" and isinstance(item, OutputProfile):
            await _wp.upsert_output_profile_row(conn, timeout, item)
        elif table_name == "executions" and isinstance(item, ExecutionRecord):
            await _er.save_execution_row(conn, timeout, item)
        elif table_name == "report_artifacts" and isinstance(item, ReportArtifact):
            await _er.upsert_report_artifact_row(conn, timeout, item)
        elif table_name == "report_binaries" and isinstance(item, ReportBinaryPayloadDTO):
            await _er.save_report_binary_row(conn, timeout, item)
        else:
            raise _log_validation_error(f"Item type '{type(item).__name__}' does not match table '{table_name}'.")
        count += 1
    return count


async def verify_seed_table_counts_rows(conn: _Conn, timeout: float, expected: Mapping[str, int]) -> dict[str, int]:
    """Verify row counts across the 10 core PostgreSQL 19 tables via SELECT count(*).

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        expected: Mapping of collection/table name to minimum expected row count.

    Returns:
        Dictionary mapping canonical table name to actual row count in PostgreSQL 19.

    Raises:
        AppException: With VALIDATION_FAILED on unknown table or STORAGE_ACCESS_FAILED on query/count failure.
    """
    actual_counts: dict[str, int] = {}
    for table_name in CANONICAL_SEED_TABLES:
        try:
            row = await conn.fetchrow(f"SELECT count(*) AS row_count FROM {table_name}", timeout=timeout)
        except Exception as exc:
            if isinstance(exc, AppException):
                raise
            raise _log_storage_error(f"Failed to verify row count for table '{table_name}': {exc}", table_name) from exc
        row_count = 0
        if row is not None:
            row_count = int(str(row["row_count"]))
        actual_counts[table_name] = row_count

    for key, min_expected in expected.items():
        target_table = _COLLECTION_TO_TABLE_MAP[key] if key in _COLLECTION_TO_TABLE_MAP else key
        if target_table not in actual_counts:
            raise _log_validation_error(f"Unknown table '{target_table}' in verify_seed_table_counts.")
        if actual_counts[target_table] < min_expected:
            msg = f"Seed count verification failed for '{target_table}': expected >= {min_expected}."
            raise _log_storage_error(msg, target_table, exc_info=False)
    return actual_counts


async def list_collection_documents_rows(conn: _Conn, timeout: float, col_name: str) -> list[dict[str, JsonValue]]:
    """List all documents from a canonical PostgreSQL 19 table as JSON-compatible dictionaries.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        col_name: Canonical collection or table name.

    Returns:
        List of serialized document dictionaries from the mapped table.

    Raises:
        AppException: With STORAGE_ACCESS_FAILED if the database query fails.
    """
    if col_name not in _COLLECTION_TO_TABLE_MAP:
        return []
    table_name = _COLLECTION_TO_TABLE_MAP[col_name]
    if table_name not in _LIST_SPECS:
        return []
    list_sql, hydrate_fn = _LIST_SPECS[table_name]
    rows = await _fetch_rows(conn, timeout, list_sql, table_name)
    return [hydrate_fn(r).model_dump(mode="json") for r in rows]


async def get_collection_document_row(
    conn: _Conn, timeout: float, col_name: str, doc_id: str
) -> dict[str, JsonValue] | None:
    """Fetch a single document by ID from a canonical PostgreSQL 19 table.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        col_name: Canonical collection or table name.
        doc_id: Primary document identifier.

    Returns:
        Serialized document dictionary if found and valid, or None.
    """
    if col_name not in _COLLECTION_TO_TABLE_MAP:
        return None
    table_name = _COLLECTION_TO_TABLE_MAP[col_name]
    if table_name not in _GET_HANDLERS:
        return None
    try:
        entity = await _GET_HANDLERS[table_name](conn, timeout, doc_id)
    except AppException:
        return None
    if entity is None:
        return None
    return entity.model_dump(mode="json")


async def upsert_collection_document_row(
    conn: _Conn, timeout: float, col_name: str, doc_id: str, data: Mapping[str, JsonValue]
) -> bool:
    """Validate and upsert a document dictionary into its canonical PostgreSQL 19 table if schema-valid.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        col_name: Canonical collection or table name.
        doc_id: Primary document identifier.
        data: Raw document dictionary to validate and persist.

    Returns:
        True if the document validated against the table's domain schema and was persisted, else False.

    Raises:
        AppException: With STORAGE_ACCESS_FAILED if database command execution fails.
    """
    if col_name not in _COLLECTION_TO_TABLE_MAP:
        return False
    table_name = _COLLECTION_TO_TABLE_MAP[col_name]
    payload = {k: v for k, v in data.items()}
    payload["id"] = doc_id
    try:
        model: BaseModel | None = None
        if table_name in _MODEL_CLASSES:
            model = _MODEL_CLASSES[table_name].model_validate(payload, strict=False)
        elif table_name == "system_configs":
            if "type" in payload and payload["type"] == "mcp_gateways":
                model = SystemConfigMCPGateways.model_validate(payload, strict=False)
            else:
                model = SystemConfigModelRegistry.model_validate(payload, strict=False)
        elif table_name == "prompt_blocks":
            model = PromptBlockAdapter.validate_python(payload, strict=False)
        if model is None:
            return False
        await seed_collection_batch_rows(conn, timeout, table_name, (model,))
        return True
    except AppException as exc:
        if exc.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value:
            raise
        return False
    except ValueError, KeyError, TypeError:
        return False


async def delete_collection_document_row(conn: _Conn, timeout: float, col_name: str, doc_id: str) -> bool:
    """Delete a row by ID from a canonical PostgreSQL 19 table.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        col_name: Canonical collection or table name.
        doc_id: Primary document identifier.

    Returns:
        True if a row was deleted, else False.

    Raises:
        AppException: With STORAGE_ACCESS_FAILED if database command execution fails.
    """
    if col_name not in _COLLECTION_TO_TABLE_MAP:
        return False
    table_name = _COLLECTION_TO_TABLE_MAP[col_name]
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
    try:
        status_str = await conn.execute(f"DELETE FROM {table_name} WHERE id = $1::uuid", doc_uuid, timeout=timeout)
    except Exception as exc:
        if isinstance(exc, AppException):
            raise
        raise _log_storage_error(f"Failed to delete '{doc_id}' from '{table_name}': {exc}", table_name) from exc
    return status_str.endswith(" 1")


async def clear_collection_documents_rows(conn: _Conn, timeout: float, col_name: str) -> None:
    """Delete all rows from a canonical PostgreSQL 19 table.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        col_name: Canonical collection or table name.

    Raises:
        AppException: With STORAGE_ACCESS_FAILED if database command execution fails.
    """
    if col_name not in _COLLECTION_TO_TABLE_MAP:
        return
    table_name = _COLLECTION_TO_TABLE_MAP[col_name]
    try:
        await conn.execute(f"DELETE FROM {table_name}", timeout=timeout)
    except Exception as exc:
        if isinstance(exc, AppException):
            raise
        raise _log_storage_error(f"Failed to clear table '{table_name}': {exc}", table_name) from exc
