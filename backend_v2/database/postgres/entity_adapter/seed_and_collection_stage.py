"""PostgreSQL 19 seed batch routing and table count verification stage."""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence

from fastapi import status
from pydantic import BaseModel

import backend_v2.database.postgres.entity_adapter.execution_and_report_stage as _er
import backend_v2.database.postgres.entity_adapter.iam_and_system_stage as _iam
import backend_v2.database.postgres.entity_adapter.prompt_block_and_step_stage as _pbs
import backend_v2.database.postgres.entity_adapter.workflow_and_profile_stage as _wp
from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    _COLLECTION_TO_TABLE_MAP,
    CANONICAL_SEED_TABLES,
    resolve_effective_timeout,
)
from backend_v2.database.postgres.pool import AsyncPgConnectionProtocol
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import Invitation, Organization, TenantSecretDTO, User
from backend_v2.models.domain.base import AuditLogRecord, UsageRecord
from backend_v2.models.domain.execution import ExecutionAssignment, ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PersonaPromptBlock,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.domain.proposition_graph import ReportBinaryPayloadDTO
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.system_config import SystemConfigMCPGateways, SystemConfigModelRegistry
from backend_v2.models.domain.task_brief import TaskBrief
from backend_v2.models.domain.workflow import Workflow

logger = logging.getLogger(__name__)

__all__ = [
    "_TRUNCATE_ALL_TABLES_SQL",
    "seed_collection_batch_rows",
    "truncate_seed_tables_rows",
    "verify_seed_table_counts_rows",
]

type _Conn = AsyncPgConnectionProtocol

_TRUNCATE_ALL_TABLES_SQL: str = (
    "TRUNCATE TABLE report_binaries, report_artifacts, quorum_edges, quorum_nodes, "
    "execution_assignments, execution_payloads, executions, workflow_step_refs, "
    "step_criteria_blocks, output_profiles, workflows, steps, task_briefs, prompt_blocks, "
    "tenant_secrets, mcp_gateways, model_registries, audit_logs, usage_records, "
    "invitations, users, organizations RESTART IDENTITY CASCADE"
)


def _log_storage_error(msg: str, table: str, *, exc_info: bool = True) -> AppException:
    """Log a STORAGE_ACCESS_FAILED error and construct the corresponding AppException.

    Args:
        msg: Human-readable storage error message.
        table: Target PostgreSQL table name where the failure occurred.
        exc_info: Whether to attach active exception traceback information to the log entry.

    Returns:
        Configured AppException with HTTP 500 status and STORAGE_ACCESS_FAILED error code.
    """
    code = ErrorCodes.STORAGE_ACCESS_FAILED
    extra = {"error_code": code.value, "table": table}
    logger.error("[PostgresEntityAdapter] %s: %s", code.name, msg, exc_info=exc_info, extra=extra)
    return AppException(
        message=msg, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details={"error_code": code.value}
    )


def _log_validation_error(msg: str, *, exc_info: bool = True) -> AppException:
    """Log a VALIDATION_FAILED error and construct the corresponding AppException.

    Args:
        msg: Human-readable validation error message.
        exc_info: Whether to attach active exception traceback information to the log entry.

    Returns:
        Configured AppException with HTTP 400 status and VALIDATION_FAILED error code.
    """
    code = ErrorCodes.VALIDATION_FAILED
    logger.error("[PostgresEntityAdapter] %s: %s", code.name, msg, exc_info=exc_info, extra={"error_code": code.value})
    return AppException(message=msg, status_code=status.HTTP_400_BAD_REQUEST, details={"error_code": code.value})


async def seed_collection_batch_rows(conn: _Conn, timeout: float, col_name: str, items: Sequence[BaseModel]) -> int:
    """Idempotently upsert or insert a validated batch of domain entities into PostgreSQL 19.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        col_name: Canonical seed collection or table name.
        items: Sequence of validated Pydantic BaseModel instances.

    Returns:
        Number of rows persisted.

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
        elif table_name == "invitations" and isinstance(item, Invitation):
            await _iam.upsert_invitation_row(conn, timeout, item)
        elif table_name == "tenant_secrets" and isinstance(item, TenantSecretDTO):
            await _iam.upsert_tenant_secret_row(conn, timeout, item)
        elif table_name == "execution_assignments" and isinstance(item, ExecutionAssignment):
            await _iam.upsert_execution_assignment_row(conn, timeout, item)
        elif table_name == "model_registries" and isinstance(item, SystemConfigModelRegistry):
            await _iam.upsert_model_registry_row(conn, timeout, item)
        elif table_name == "mcp_gateways" and isinstance(item, SystemConfigMCPGateways):
            await _iam.upsert_mcp_gateway_row(conn, timeout, item)
        elif table_name == "prompt_blocks" and isinstance(
            item, (MatrixPromptBlock, SystemRulePromptBlock, PersonaPromptBlock, ProtocolPromptBlock)
        ):
            await _pbs.upsert_prompt_block_row(conn, timeout, item)
        elif table_name == "task_briefs" and isinstance(item, TaskBrief):
            await _wp.upsert_task_brief_row(conn, timeout, item)
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
        elif table_name == "audit_logs" and isinstance(item, AuditLogRecord):
            await _iam.insert_audit_log_row(conn, timeout, item)
        elif table_name == "usage_records" and isinstance(item, UsageRecord):
            await _iam.insert_usage_record_row(conn, timeout, item)
        else:
            raise _log_validation_error(f"Item type '{type(item).__name__}' does not match table '{table_name}'.")
        count += 1
    return count


async def verify_seed_table_counts_rows(conn: _Conn, timeout: float, expected: Mapping[str, int]) -> dict[str, int]:
    """Verify row counts across the canonical PostgreSQL 19 seed tables via SELECT count(*).

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

    # Validate full Pydantic V2 hydration of model_registries and mcp_gateways rows during preflight and post-seed checks
    if "model_registries" in expected and expected["model_registries"] >= 1:
        await _iam.list_model_registry_rows(conn, timeout)
    if "mcp_gateways" in expected and expected["mcp_gateways"] >= 1:
        await _iam.list_mcp_gateway_rows(conn, timeout)
    return actual_counts


async def truncate_seed_tables_rows(conn: _Conn, timeout: float) -> None:
    """Truncate all 22 canonical PostgreSQL 19 tables including execution_payloads with RESTART IDENTITY CASCADE.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.

    Raises:
        AppException: With STORAGE_ACCESS_FAILED if the database truncate command fails.
    """
    effective_timeout = resolve_effective_timeout(timeout)
    try:
        await conn.execute(_TRUNCATE_ALL_TABLES_SQL, timeout=effective_timeout)
    except Exception as exc:
        if isinstance(exc, AppException):
            raise
        raise _log_storage_error(f"Failed to truncate canonical tables: {exc}", "executions") from exc
