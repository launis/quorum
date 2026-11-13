"""PostgreSQL 19 Zero-ORM Entity Persistence Package Facade."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime

from pydantic import BaseModel

from backend_v2.database.postgres.pool import AsyncPgConnectionProtocol
from backend_v2.models.auth import Invitation, Organization, TenantSecretDTO, User
from backend_v2.models.domain.base import AuditLogRecord, UsageRecord, UsageRollupSummaryDTO
from backend_v2.models.domain.execution import ExecutionAssignment, ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import AnyPromptBlock
from backend_v2.models.domain.proposition_graph import ReportBinaryPayloadDTO
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.system_config import SystemConfigMCPGateways, SystemConfigModelRegistry
from backend_v2.models.domain.task_brief import TaskBrief
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.trace import ExecutionUpdateDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.settings import get_settings

# Explicit redundant re-exports (Symbol as Symbol) across all 6 stage sub-modules
from .coercion_and_constants import _COLLECTION_TO_TABLE_MAP as _COLLECTION_TO_TABLE_MAP
from .coercion_and_constants import _ROOT_SYSTEM_ORG_UUID7 as _ROOT_SYSTEM_ORG_UUID7
from .coercion_and_constants import _TABLE_TO_ENTITY_PREFIX as _TABLE_TO_ENTITY_PREFIX
from .coercion_and_constants import CANONICAL_SEED_TABLES as CANONICAL_SEED_TABLES
from .coercion_and_constants import _coerce_float as _coerce_float
from .coercion_and_constants import _coerce_uuid_or_str as _coerce_uuid_or_str
from .coercion_and_constants import _decode_jsonb_column as _decode_jsonb_column
from .coercion_and_constants import _encode_optional_jsonb as _encode_optional_jsonb
from .coercion_and_constants import _format_optional_uuid7 as _format_optional_uuid7
from .coercion_and_constants import _format_org_uuid7 as _format_org_uuid7
from .coercion_and_constants import _parse_optional_uuid7 as _parse_optional_uuid7
from .coercion_and_constants import _parse_org_uuid7 as _parse_org_uuid7
from .coercion_and_constants import _parse_system_safe_org_uuid7 as _parse_system_safe_org_uuid7
from .coercion_and_constants import _parse_system_safe_user_uuid7 as _parse_system_safe_user_uuid7
from .coercion_and_constants import _ReportBinaryRowDTO as _ReportBinaryRowDTO
from .coercion_and_constants import execute_entity_delete as execute_entity_delete
from .coercion_and_constants import execute_entity_upsert as execute_entity_upsert
from .coercion_and_constants import translate_postgres_exception as translate_postgres_exception
from .coercion_and_constants import validate_hydrated_row as validate_hydrated_row
from .execution_and_report_stage import _DELETE_EXECUTION_SQL as _DELETE_EXECUTION_SQL
from .execution_and_report_stage import _DELETE_REPORT_ARTIFACT_SQL as _DELETE_REPORT_ARTIFACT_SQL
from .execution_and_report_stage import _GET_EXECUTION_SQL as _GET_EXECUTION_SQL
from .execution_and_report_stage import _GET_REPORT_ARTIFACT_SQL as _GET_REPORT_ARTIFACT_SQL
from .execution_and_report_stage import _GET_REPORT_BINARY_SQL as _GET_REPORT_BINARY_SQL
from .execution_and_report_stage import _LIST_EXECUTIONS_SQL as _LIST_EXECUTIONS_SQL
from .execution_and_report_stage import (
    _LIST_REPORT_ARTIFACTS_BY_EXECUTION_SQL as _LIST_REPORT_ARTIFACTS_BY_EXECUTION_SQL,
)
from .execution_and_report_stage import _LIST_REPORT_ARTIFACTS_SQL as _LIST_REPORT_ARTIFACTS_SQL
from .execution_and_report_stage import _MARK_REPORT_ARTIFACT_PDF_SQL as _MARK_REPORT_ARTIFACT_PDF_SQL
from .execution_and_report_stage import (
    _PROBE_EXECUTION_STATE_VERSION_SQL as _PROBE_EXECUTION_STATE_VERSION_SQL,
)
from .execution_and_report_stage import _SAVE_EXECUTION_SQL as _SAVE_EXECUTION_SQL
from .execution_and_report_stage import _SAVE_REPORT_BINARY_SQL as _SAVE_REPORT_BINARY_SQL
from .execution_and_report_stage import _UPDATE_EXECUTION_OCC_SQL as _UPDATE_EXECUTION_OCC_SQL
from .execution_and_report_stage import _UPSERT_EXECUTION_PAYLOAD_SQL as _UPSERT_EXECUTION_PAYLOAD_SQL
from .execution_and_report_stage import _UPSERT_REPORT_ARTIFACT_SQL as _UPSERT_REPORT_ARTIFACT_SQL
from .execution_and_report_stage import apply_execution_updates as apply_execution_updates
from .execution_and_report_stage import delete_execution_row as delete_execution_row
from .execution_and_report_stage import delete_report_artifact_row as delete_report_artifact_row
from .execution_and_report_stage import get_execution_row as get_execution_row
from .execution_and_report_stage import get_report_artifact_row as get_report_artifact_row
from .execution_and_report_stage import get_report_binary_row as get_report_binary_row
from .execution_and_report_stage import hydrate_execution_row as hydrate_execution_row
from .execution_and_report_stage import hydrate_execution_summary_row as hydrate_execution_summary_row
from .execution_and_report_stage import hydrate_report_artifact_row as hydrate_report_artifact_row
from .execution_and_report_stage import list_execution_rows as list_execution_rows
from .execution_and_report_stage import list_executions_filtered_rows as list_executions_filtered_rows
from .execution_and_report_stage import (
    list_report_artifacts_by_execution_row as list_report_artifacts_by_execution_row,
)
from .execution_and_report_stage import save_execution_row as save_execution_row
from .execution_and_report_stage import save_report_binary_row as save_report_binary_row
from .execution_and_report_stage import update_execution_occ_row as update_execution_occ_row
from .execution_and_report_stage import upsert_report_artifact_row as upsert_report_artifact_row
from .iam_and_system_stage import _AGGREGATE_USAGE_BASE_SQL as _AGGREGATE_USAGE_BASE_SQL
from .iam_and_system_stage import _DELETE_INVITATION_SQL as _DELETE_INVITATION_SQL
from .iam_and_system_stage import _DELETE_MCP_GATEWAY_SQL as _DELETE_MCP_GATEWAY_SQL
from .iam_and_system_stage import _DELETE_MODEL_REGISTRY_SQL as _DELETE_MODEL_REGISTRY_SQL
from .iam_and_system_stage import _DELETE_ORGANIZATION_SQL as _DELETE_ORGANIZATION_SQL
from .iam_and_system_stage import _DELETE_TENANT_SECRET_SQL as _DELETE_TENANT_SECRET_SQL
from .iam_and_system_stage import _DELETE_USER_SQL as _DELETE_USER_SQL
from .iam_and_system_stage import (
    _GET_EXECUTION_ASSIGNMENT_BY_EXECUTION_ID_SQL as _GET_EXECUTION_ASSIGNMENT_BY_EXECUTION_ID_SQL,
)
from .iam_and_system_stage import (
    _GET_EXECUTION_ASSIGNMENT_BY_TOKEN_HASH_SQL as _GET_EXECUTION_ASSIGNMENT_BY_TOKEN_HASH_SQL,
)
from .iam_and_system_stage import _GET_EXECUTION_ASSIGNMENT_SQL as _GET_EXECUTION_ASSIGNMENT_SQL
from .iam_and_system_stage import _GET_INVITATION_SQL as _GET_INVITATION_SQL
from .iam_and_system_stage import _GET_MCP_GATEWAY_SQL as _GET_MCP_GATEWAY_SQL
from .iam_and_system_stage import _GET_MODEL_REGISTRY_SQL as _GET_MODEL_REGISTRY_SQL
from .iam_and_system_stage import _GET_ORGANIZATION_SQL as _GET_ORGANIZATION_SQL
from .iam_and_system_stage import _GET_TENANT_SECRET_SQL as _GET_TENANT_SECRET_SQL
from .iam_and_system_stage import _GET_USER_BY_EMAIL_SQL as _GET_USER_BY_EMAIL_SQL
from .iam_and_system_stage import _GET_USER_SQL as _GET_USER_SQL
from .iam_and_system_stage import _INSERT_AUDIT_LOG_SQL as _INSERT_AUDIT_LOG_SQL
from .iam_and_system_stage import _INSERT_USAGE_RECORD_SQL as _INSERT_USAGE_RECORD_SQL
from .iam_and_system_stage import _LIST_AUDIT_LOGS_SQL as _LIST_AUDIT_LOGS_SQL
from .iam_and_system_stage import (
    _LIST_EXECUTION_ASSIGNMENTS_BY_ORG_SQL as _LIST_EXECUTION_ASSIGNMENTS_BY_ORG_SQL,
)
from .iam_and_system_stage import _LIST_EXECUTION_ASSIGNMENTS_SQL as _LIST_EXECUTION_ASSIGNMENTS_SQL
from .iam_and_system_stage import _LIST_INVITATIONS_BY_ORG_SQL as _LIST_INVITATIONS_BY_ORG_SQL
from .iam_and_system_stage import _LIST_INVITATIONS_SQL as _LIST_INVITATIONS_SQL
from .iam_and_system_stage import _LIST_MCP_GATEWAYS_SQL as _LIST_MCP_GATEWAYS_SQL
from .iam_and_system_stage import _LIST_MODEL_REGISTRIES_SQL as _LIST_MODEL_REGISTRIES_SQL
from .iam_and_system_stage import _LIST_ORGANIZATIONS_SQL as _LIST_ORGANIZATIONS_SQL
from .iam_and_system_stage import _LIST_TENANT_SECRETS_BY_ORG_SQL as _LIST_TENANT_SECRETS_BY_ORG_SQL
from .iam_and_system_stage import _LIST_TENANT_SECRETS_SQL as _LIST_TENANT_SECRETS_SQL
from .iam_and_system_stage import _LIST_USAGE_RECORDS_SQL as _LIST_USAGE_RECORDS_SQL
from .iam_and_system_stage import _LIST_USERS_BY_ORG_SQL as _LIST_USERS_BY_ORG_SQL
from .iam_and_system_stage import _LIST_USERS_SQL as _LIST_USERS_SQL
from .iam_and_system_stage import _UPSERT_EXECUTION_ASSIGNMENT_SQL as _UPSERT_EXECUTION_ASSIGNMENT_SQL
from .iam_and_system_stage import _UPSERT_INVITATION_SQL as _UPSERT_INVITATION_SQL
from .iam_and_system_stage import _UPSERT_MCP_GATEWAY_SQL as _UPSERT_MCP_GATEWAY_SQL
from .iam_and_system_stage import _UPSERT_MODEL_REGISTRY_SQL as _UPSERT_MODEL_REGISTRY_SQL
from .iam_and_system_stage import _UPSERT_ORGANIZATION_SQL as _UPSERT_ORGANIZATION_SQL
from .iam_and_system_stage import _UPSERT_TENANT_SECRET_SQL as _UPSERT_TENANT_SECRET_SQL
from .iam_and_system_stage import _UPSERT_USER_SQL as _UPSERT_USER_SQL
from .iam_and_system_stage import aggregate_organization_usage_row as aggregate_organization_usage_row
from .iam_and_system_stage import delete_invitation_row as delete_invitation_row
from .iam_and_system_stage import delete_mcp_gateway_row as delete_mcp_gateway_row
from .iam_and_system_stage import delete_model_registry_row as delete_model_registry_row
from .iam_and_system_stage import delete_organization_row as delete_organization_row
from .iam_and_system_stage import delete_tenant_secret_row as delete_tenant_secret_row
from .iam_and_system_stage import delete_user_row as delete_user_row
from .iam_and_system_stage import (
    get_execution_assignment_by_execution_id_row as get_execution_assignment_by_execution_id_row,
)
from .iam_and_system_stage import (
    get_execution_assignment_by_token_hash_row as get_execution_assignment_by_token_hash_row,
)
from .iam_and_system_stage import get_execution_assignment_row as get_execution_assignment_row
from .iam_and_system_stage import get_invitation_row as get_invitation_row
from .iam_and_system_stage import get_mcp_gateway_row as get_mcp_gateway_row
from .iam_and_system_stage import get_model_registry_row as get_model_registry_row
from .iam_and_system_stage import get_organization_row as get_organization_row
from .iam_and_system_stage import get_tenant_secret_row as get_tenant_secret_row
from .iam_and_system_stage import get_user_by_email_row as get_user_by_email_row
from .iam_and_system_stage import get_user_row as get_user_row
from .iam_and_system_stage import hydrate_audit_log_row as hydrate_audit_log_row
from .iam_and_system_stage import hydrate_execution_assignment_row as hydrate_execution_assignment_row
from .iam_and_system_stage import hydrate_invitation_row as hydrate_invitation_row
from .iam_and_system_stage import hydrate_mcp_gateway_row as hydrate_mcp_gateway_row
from .iam_and_system_stage import hydrate_model_registry_row as hydrate_model_registry_row
from .iam_and_system_stage import hydrate_organization_row as hydrate_organization_row
from .iam_and_system_stage import hydrate_tenant_secret_row as hydrate_tenant_secret_row
from .iam_and_system_stage import hydrate_usage_record_row as hydrate_usage_record_row
from .iam_and_system_stage import hydrate_user_row as hydrate_user_row
from .iam_and_system_stage import insert_audit_log_row as insert_audit_log_row
from .iam_and_system_stage import insert_usage_record_row as insert_usage_record_row
from .iam_and_system_stage import list_audit_log_rows as list_audit_log_rows
from .iam_and_system_stage import list_execution_assignment_rows as list_execution_assignment_rows
from .iam_and_system_stage import (
    list_execution_assignments_by_organization_rows as list_execution_assignments_by_organization_rows,
)
from .iam_and_system_stage import list_invitation_rows as list_invitation_rows
from .iam_and_system_stage import list_mcp_gateway_rows as list_mcp_gateway_rows
from .iam_and_system_stage import list_model_registry_rows as list_model_registry_rows
from .iam_and_system_stage import list_organization_rows as list_organization_rows
from .iam_and_system_stage import list_tenant_secret_rows as list_tenant_secret_rows
from .iam_and_system_stage import list_usage_record_rows as list_usage_record_rows
from .iam_and_system_stage import list_user_rows as list_user_rows
from .iam_and_system_stage import upsert_execution_assignment_row as upsert_execution_assignment_row
from .iam_and_system_stage import upsert_invitation_row as upsert_invitation_row
from .iam_and_system_stage import upsert_mcp_gateway_row as upsert_mcp_gateway_row
from .iam_and_system_stage import upsert_model_registry_row as upsert_model_registry_row
from .iam_and_system_stage import upsert_organization_row as upsert_organization_row
from .iam_and_system_stage import upsert_tenant_secret_row as upsert_tenant_secret_row
from .iam_and_system_stage import upsert_user_row as upsert_user_row
from .prompt_block_and_step_stage import _DELETE_PROMPT_BLOCK_SQL as _DELETE_PROMPT_BLOCK_SQL
from .prompt_block_and_step_stage import _DELETE_STEP_SQL as _DELETE_STEP_SQL
from .prompt_block_and_step_stage import _GET_PROMPT_BLOCK_SQL as _GET_PROMPT_BLOCK_SQL
from .prompt_block_and_step_stage import _GET_STEP_SQL as _GET_STEP_SQL
from .prompt_block_and_step_stage import _LIST_PROMPT_BLOCKS_SQL as _LIST_PROMPT_BLOCKS_SQL
from .prompt_block_and_step_stage import _LIST_STEPS_SQL as _LIST_STEPS_SQL
from .prompt_block_and_step_stage import _UPSERT_PROMPT_BLOCK_SQL as _UPSERT_PROMPT_BLOCK_SQL
from .prompt_block_and_step_stage import _UPSERT_STEP_SQL as _UPSERT_STEP_SQL
from .prompt_block_and_step_stage import delete_prompt_block_row as delete_prompt_block_row
from .prompt_block_and_step_stage import delete_step_row as delete_step_row
from .prompt_block_and_step_stage import get_prompt_block_row as get_prompt_block_row
from .prompt_block_and_step_stage import get_step_row as get_step_row
from .prompt_block_and_step_stage import hydrate_prompt_block_row as hydrate_prompt_block_row
from .prompt_block_and_step_stage import hydrate_step_row as hydrate_step_row
from .prompt_block_and_step_stage import list_prompt_block_rows as list_prompt_block_rows
from .prompt_block_and_step_stage import list_step_rows as list_step_rows
from .prompt_block_and_step_stage import upsert_prompt_block_row as upsert_prompt_block_row
from .prompt_block_and_step_stage import upsert_step_row as upsert_step_row
from .seed_and_collection_stage import _TRUNCATE_ALL_TABLES_SQL as _TRUNCATE_ALL_TABLES_SQL
from .seed_and_collection_stage import seed_collection_batch_rows as seed_collection_batch_rows
from .seed_and_collection_stage import truncate_seed_tables_rows as truncate_seed_tables_rows
from .seed_and_collection_stage import verify_seed_table_counts_rows as verify_seed_table_counts_rows
from .workflow_and_profile_stage import _DELETE_OUTPUT_PROFILE_SQL as _DELETE_OUTPUT_PROFILE_SQL
from .workflow_and_profile_stage import _DELETE_TASK_BRIEF_SQL as _DELETE_TASK_BRIEF_SQL
from .workflow_and_profile_stage import _DELETE_WORKFLOW_SQL as _DELETE_WORKFLOW_SQL
from .workflow_and_profile_stage import _GET_OUTPUT_PROFILE_SQL as _GET_OUTPUT_PROFILE_SQL
from .workflow_and_profile_stage import _GET_TASK_BRIEF_SQL as _GET_TASK_BRIEF_SQL
from .workflow_and_profile_stage import _GET_WORKFLOW_SQL as _GET_WORKFLOW_SQL
from .workflow_and_profile_stage import _LIST_OUTPUT_PROFILES_SQL as _LIST_OUTPUT_PROFILES_SQL
from .workflow_and_profile_stage import _LIST_TASK_BRIEFS_SQL as _LIST_TASK_BRIEFS_SQL
from .workflow_and_profile_stage import _LIST_WORKFLOWS_SQL as _LIST_WORKFLOWS_SQL
from .workflow_and_profile_stage import _UPSERT_OUTPUT_PROFILE_SQL as _UPSERT_OUTPUT_PROFILE_SQL
from .workflow_and_profile_stage import _UPSERT_TASK_BRIEF_SQL as _UPSERT_TASK_BRIEF_SQL
from .workflow_and_profile_stage import _UPSERT_WORKFLOW_SQL as _UPSERT_WORKFLOW_SQL
from .workflow_and_profile_stage import delete_output_profile_row as delete_output_profile_row
from .workflow_and_profile_stage import delete_task_brief_row as delete_task_brief_row
from .workflow_and_profile_stage import delete_workflow_row as delete_workflow_row
from .workflow_and_profile_stage import get_output_profile_row as get_output_profile_row
from .workflow_and_profile_stage import get_task_brief_row as get_task_brief_row
from .workflow_and_profile_stage import get_workflow_row as get_workflow_row
from .workflow_and_profile_stage import hydrate_output_profile_row as hydrate_output_profile_row
from .workflow_and_profile_stage import hydrate_task_brief_row as hydrate_task_brief_row
from .workflow_and_profile_stage import hydrate_workflow_row as hydrate_workflow_row
from .workflow_and_profile_stage import list_output_profile_rows as list_output_profile_rows
from .workflow_and_profile_stage import list_task_brief_rows as list_task_brief_rows
from .workflow_and_profile_stage import list_workflow_rows as list_workflow_rows
from .workflow_and_profile_stage import upsert_output_profile_row as upsert_output_profile_row
from .workflow_and_profile_stage import upsert_task_brief_row as upsert_task_brief_row
from .workflow_and_profile_stage import upsert_workflow_row as upsert_workflow_row

__all__ = ["CANONICAL_SEED_TABLES", "PostgresEntityAdapter"]


class PostgresEntityAdapter:
    """Zero-ORM PostgreSQL 19 adapter implementing EntityPersistencePort.

    Attributes:
        command_timeout_seconds: Timeout in seconds for PostgreSQL command execution.
    """

    _hydrate_execution_row = staticmethod(hydrate_execution_row)
    _hydrate_organization_row = staticmethod(hydrate_organization_row)
    _hydrate_user_row = staticmethod(hydrate_user_row)
    _hydrate_invitation_row = staticmethod(hydrate_invitation_row)
    _hydrate_tenant_secret_row = staticmethod(hydrate_tenant_secret_row)
    _hydrate_execution_assignment_row = staticmethod(hydrate_execution_assignment_row)
    _hydrate_model_registry_row = staticmethod(hydrate_model_registry_row)
    _hydrate_mcp_gateway_row = staticmethod(hydrate_mcp_gateway_row)
    _hydrate_prompt_block_row = staticmethod(hydrate_prompt_block_row)
    _hydrate_task_brief_row = staticmethod(hydrate_task_brief_row)
    _hydrate_step_row = staticmethod(hydrate_step_row)
    _hydrate_workflow_row = staticmethod(hydrate_workflow_row)
    _hydrate_output_profile_row = staticmethod(hydrate_output_profile_row)
    _hydrate_report_artifact_row = staticmethod(hydrate_report_artifact_row)
    _hydrate_audit_log_row = staticmethod(hydrate_audit_log_row)
    _hydrate_usage_record_row = staticmethod(hydrate_usage_record_row)

    def __init__(self, connection: AsyncPgConnectionProtocol, command_timeout_seconds: float | None = None) -> None:
        """Initialize the PostgreSQL entity adapter over an active connection.

        Args:
            connection: Active PostgreSQL connection conforming to AsyncPgConnectionProtocol.
            command_timeout_seconds: Optional command timeout override in seconds.
        """
        self._conn: AsyncPgConnectionProtocol = connection
        if command_timeout_seconds is not None:
            self.command_timeout_seconds: float = command_timeout_seconds
        else:
            self.command_timeout_seconds = get_settings().postgres_command_timeout_seconds

    async def save_report_binary(self, payload: ReportBinaryPayloadDTO) -> None:
        """Persist a ReportBinaryPayloadDTO into report_binaries and mark has_pdf.

        Args:
            payload: Validated ReportBinaryPayloadDTO containing PDF bytes.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on persistence failure.
        """
        await save_report_binary_row(self._conn, self.command_timeout_seconds, payload)

    async def get_report_binary(self, report_id: str) -> ReportBinaryPayloadDTO | None:
        """Retrieve a ReportBinaryPayloadDTO from report_binaries by canonical report_id.

        Args:
            report_id: Canonical rep_<32_hex> identifier.

        Returns:
            Hydrated ReportBinaryPayloadDTO instance, or None if not found.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await get_report_binary_row(self._conn, self.command_timeout_seconds, report_id)

    async def save_execution(
        self,
        record: ExecutionRecord,
        *,
        expected_state_version: int | None = None,
    ) -> str:
        """Persist an ExecutionRecord into the PostgreSQL 19 executions table.

        Args:
            record: Validated ExecutionRecord domain model.
            expected_state_version: Optional expected state_version for optimistic concurrency control.

        Returns:
            Canonical exe_<32_hex> execution identifier.

        Raises:
            AppException: With VALIDATION_FAILED, CONFLICT, or STORAGE_ACCESS_FAILED on persistence failure.
        """
        return await save_execution_row(
            self._conn,
            self.command_timeout_seconds,
            record,
            expected_state_version=expected_state_version,
        )

    async def get_execution(self, execution_id: str) -> ExecutionRecord | None:
        """Retrieve and reconstitute an ExecutionRecord from PostgreSQL by execution_id.

        Args:
            execution_id: Canonical exe_<32_hex> identifier.

        Returns:
            Reconstituted ExecutionRecord instance, or None if not found.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await get_execution_row(self._conn, self.command_timeout_seconds, execution_id)

    async def list_executions_filtered(
        self,
        *,
        organization_id: str | None = None,
        created_by: str | None = None,
        workflow_id: str | None = None,
        status: ExecutionStatus | None = None,
        limit: int = 100,
    ) -> list[ExecutionRecord]:
        """List ExecutionRecord rows filtered by indexed columns and ordered by id DESC.

        Args:
            organization_id: Optional canonical org_<32_hex> organization filter.
            created_by: Optional canonical usr_<32_hex> creator filter.
            workflow_id: Optional canonical wf_<32_hex> workflow filter.
            status: Optional ExecutionStatus filter.
            limit: Maximum number of records to return.

        Returns:
            List of hydrated ExecutionRecord models ordered by id DESC.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await list_executions_filtered_rows(
            self._conn,
            self.command_timeout_seconds,
            organization_id=organization_id,
            created_by=created_by,
            workflow_id=workflow_id,
            status=status,
            limit=limit,
        )

    async def _execute_upsert(self, sql: str, *args: object, entity_label: str, entity_id: str) -> str:
        """Execute a parameterized upsert statement and translate transport errors to AppException.

        Args:
            sql: Parameterized INSERT ... ON CONFLICT DO UPDATE SQL statement.
            *args: Positional SQL bind arguments.
            entity_label: Human-readable entity type label for structured error logging.
            entity_id: Canonical Opaque Stripe ID of the entity being persisted.

        Returns:
            Canonical entity_id persisted into PostgreSQL 19.

        Raises:
            AppException: With STORAGE_ACCESS_FAILED if the database command fails.
        """
        return await execute_entity_upsert(
            self._conn, self.command_timeout_seconds, sql, *args, entity_id=entity_id, entity_label=entity_label
        )

    async def upsert_organization(self, org: Organization) -> str:
        """Persist an Organization into the organizations table.

        Args:
            org: Validated Organization domain model.

        Returns:
            Canonical Organization identifier.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on persistence failure.
        """
        return await upsert_organization_row(self._conn, self.command_timeout_seconds, org)

    async def get_organization(self, org_id: str) -> Organization | None:
        """Fetch an Organization by ID.

        Args:
            org_id: Canonical Organization identifier.

        Returns:
            Hydrated Organization instance, or None if not found.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await get_organization_row(self._conn, self.command_timeout_seconds, org_id)

    async def list_organizations(self) -> list[Organization]:
        """List all Organizations.

        Returns:
            List of hydrated Organization models.

        Raises:
            AppException: With STORAGE_ACCESS_FAILED on query failure.
        """
        return await list_organization_rows(self._conn, self.command_timeout_seconds)

    async def upsert_user(self, user: User) -> str:
        """Persist a User into the users table.

        Args:
            user: Validated User domain model.

        Returns:
            Canonical usr_<32_hex> identifier.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on persistence failure.
        """
        return await upsert_user_row(self._conn, self.command_timeout_seconds, user)

    async def get_user(self, user_id: str) -> User | None:
        """Fetch a User by ID.

        Args:
            user_id: Canonical usr_<32_hex> identifier.

        Returns:
            Hydrated User instance, or None if not found.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await get_user_row(self._conn, self.command_timeout_seconds, user_id)

    async def list_users(self, organization_id: str | None = None) -> list[User]:
        """List Users optionally filtered by parameterized organization_id.

        Args:
            organization_id: Optional canonical org_<32_hex> organization filter.

        Returns:
            List of hydrated User models.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await list_user_rows(self._conn, self.command_timeout_seconds, organization_id=organization_id)

    async def upsert_invitation(self, invitation: Invitation) -> str:
        """Persist an Invitation into the invitations table.

        Args:
            invitation: Validated Invitation domain model.

        Returns:
            Canonical inv_<32_hex> identifier.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on persistence failure.
        """
        return await upsert_invitation_row(self._conn, self.command_timeout_seconds, invitation)

    async def get_invitation(self, invitation_id: str) -> Invitation | None:
        """Fetch an Invitation by ID.

        Args:
            invitation_id: Canonical inv_<32_hex> identifier.

        Returns:
            Hydrated Invitation instance, or None if not found.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await get_invitation_row(self._conn, self.command_timeout_seconds, invitation_id)

    async def list_invitations(self, organization_id: str | None = None) -> list[Invitation]:
        """List Invitations optionally filtered by parameterized organization_id.

        Args:
            organization_id: Optional canonical org_<32_hex> organization filter.

        Returns:
            List of hydrated Invitation models.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await list_invitation_rows(self._conn, self.command_timeout_seconds, organization_id=organization_id)

    async def upsert_tenant_secret(self, secret: TenantSecretDTO) -> str:
        """Persist a TenantSecretDTO into the tenant_secrets table.

        Args:
            secret: Validated TenantSecretDTO model.

        Returns:
            Canonical sec_<32_hex> identifier.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on persistence failure.
        """
        return await upsert_tenant_secret_row(self._conn, self.command_timeout_seconds, secret)

    async def get_tenant_secret(self, secret_id: str) -> TenantSecretDTO | None:
        """Fetch a TenantSecretDTO by ID.

        Args:
            secret_id: Canonical sec_<32_hex> identifier.

        Returns:
            Hydrated TenantSecretDTO instance, or None if not found.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await get_tenant_secret_row(self._conn, self.command_timeout_seconds, secret_id)

    async def list_tenant_secrets(self, organization_id: str | None = None) -> list[TenantSecretDTO]:
        """List TenantSecretDTO rows optionally filtered by parameterized organization_id.

        Args:
            organization_id: Optional canonical org_<32_hex> organization filter.

        Returns:
            List of hydrated TenantSecretDTO models.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await list_tenant_secret_rows(self._conn, self.command_timeout_seconds, organization_id=organization_id)

    async def upsert_execution_assignment(self, assignment: ExecutionAssignment) -> str:
        """Persist an ExecutionAssignment into the execution_assignments table.

        Args:
            assignment: Validated ExecutionAssignment domain model.

        Returns:
            Canonical tsk_<32_hex> identifier.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on persistence failure.
        """
        return await upsert_execution_assignment_row(self._conn, self.command_timeout_seconds, assignment)

    async def get_execution_assignment(self, assignment_id: str) -> ExecutionAssignment | None:
        """Fetch an ExecutionAssignment by ID.

        Args:
            assignment_id: Canonical tsk_<32_hex> identifier.

        Returns:
            Hydrated ExecutionAssignment instance, or None if not found.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await get_execution_assignment_row(self._conn, self.command_timeout_seconds, assignment_id)

    async def list_execution_assignments(self, organization_id: str | None = None) -> list[ExecutionAssignment]:
        """List ExecutionAssignments optionally filtered by parameterized organization_id.

        Args:
            organization_id: Optional canonical org_<32_hex> organization filter.

        Returns:
            List of hydrated ExecutionAssignment models.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await list_execution_assignment_rows(
            self._conn, self.command_timeout_seconds, organization_id=organization_id
        )

    async def get_execution_assignment_by_token_hash(self, token_hash: str) -> ExecutionAssignment | None:
        """Fetch an ExecutionAssignment by indexed SHA-256 token_hash lookup.

        Args:
            token_hash: 64-character hex SHA-256 token digest.

        Returns:
            Hydrated ExecutionAssignment instance, or None if not found.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await get_execution_assignment_by_token_hash_row(self._conn, self.command_timeout_seconds, token_hash)

    async def get_execution_assignment_by_execution_id(self, execution_id: str) -> ExecutionAssignment | None:
        """Fetch the newest ExecutionAssignment referencing execution_id via indexed SQL lookup.

        Args:
            execution_id: Canonical exe_<32_hex> execution identifier.

        Returns:
            Hydrated ExecutionAssignment instance, or None if not found.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await get_execution_assignment_by_execution_id_row(
            self._conn, self.command_timeout_seconds, execution_id
        )

    async def list_execution_assignments_by_organization(
        self,
        organization_id: str,
        *,
        batch_id: str | None = None,
        workflow_id: str | None = None,
        limit: int = 100,
    ) -> list[ExecutionAssignment]:
        """List ExecutionAssignments for an organization with optional batch_id and workflow_id filters.

        Args:
            organization_id: Canonical org_<32_hex> organization identifier.
            batch_id: Optional canonical tsk_<32_hex> batch identifier filter.
            workflow_id: Optional canonical wf_<32_hex> workflow identifier filter.
            limit: Maximum number of assignments to return.

        Returns:
            List of hydrated ExecutionAssignment models ordered by id DESC.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await list_execution_assignments_by_organization_rows(
            self._conn,
            self.command_timeout_seconds,
            organization_id,
            batch_id=batch_id,
            workflow_id=workflow_id,
            limit=limit,
        )

    async def upsert_model_registry(self, registry: SystemConfigModelRegistry) -> str:
        """Persist a SystemConfigModelRegistry into model_registries.

        Args:
            registry: Validated SystemConfigModelRegistry model.

        Returns:
            Canonical mrg_<32_hex> identifier.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on persistence failure.
        """
        return await upsert_model_registry_row(self._conn, self.command_timeout_seconds, registry)

    async def get_model_registry(self, registry_id: str) -> SystemConfigModelRegistry | None:
        """Fetch a SystemConfigModelRegistry by ID.

        Args:
            registry_id: Canonical mrg_<32_hex> identifier.

        Returns:
            Hydrated SystemConfigModelRegistry instance, or None if not found.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await get_model_registry_row(self._conn, self.command_timeout_seconds, registry_id)

    async def upsert_mcp_gateway(self, gateway: SystemConfigMCPGateways) -> str:
        """Persist a SystemConfigMCPGateways into mcp_gateways.

        Args:
            gateway: Validated SystemConfigMCPGateways model.

        Returns:
            Canonical mcp_<32_hex> identifier.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on persistence failure.
        """
        return await upsert_mcp_gateway_row(self._conn, self.command_timeout_seconds, gateway)

    async def get_mcp_gateway(self, gateway_id: str) -> SystemConfigMCPGateways | None:
        """Fetch a SystemConfigMCPGateways by ID.

        Args:
            gateway_id: Canonical mcp_<32_hex> identifier.

        Returns:
            Hydrated SystemConfigMCPGateways instance, or None if not found.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await get_mcp_gateway_row(self._conn, self.command_timeout_seconds, gateway_id)

    async def upsert_prompt_block(self, block: AnyPromptBlock) -> str:
        """Persist a polymorphic AnyPromptBlock into prompt_blocks.

        Args:
            block: Validated polymorphic AnyPromptBlock model.

        Returns:
            Canonical blk_<32_hex> identifier.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on persistence failure.
        """
        return await upsert_prompt_block_row(self._conn, self.command_timeout_seconds, block)

    async def get_prompt_block(self, block_id: str) -> AnyPromptBlock | None:
        """Fetch an AnyPromptBlock by ID.

        Args:
            block_id: Canonical blk_<32_hex> identifier.

        Returns:
            Hydrated polymorphic AnyPromptBlock instance, or None if not found.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await get_prompt_block_row(self._conn, self.command_timeout_seconds, block_id)

    async def upsert_step(self, step: Step) -> str:
        """Persist a Step into steps.

        Args:
            step: Validated Step domain model.

        Returns:
            Canonical stp_<32_hex> identifier.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on persistence failure.
        """
        return await upsert_step_row(self._conn, self.command_timeout_seconds, step)

    async def get_step(self, step_id: str) -> Step | None:
        """Fetch a Step by ID.

        Args:
            step_id: Canonical stp_<32_hex> identifier.

        Returns:
            Hydrated Step instance, or None if not found.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await get_step_row(self._conn, self.command_timeout_seconds, step_id)

    async def upsert_workflow(self, wf: Workflow) -> str:
        """Persist a Workflow into workflows.

        Args:
            wf: Validated Workflow domain model.

        Returns:
            Canonical wor_<32_hex> identifier.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on persistence failure.
        """
        return await upsert_workflow_row(self._conn, self.command_timeout_seconds, wf)

    async def get_workflow(self, workflow_id: str) -> Workflow | None:
        """Fetch a Workflow by ID.

        Args:
            workflow_id: Canonical wor_<32_hex> identifier.

        Returns:
            Hydrated Workflow instance, or None if not found.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await get_workflow_row(self._conn, self.command_timeout_seconds, workflow_id)

    async def upsert_output_profile(self, profile: OutputProfile) -> str:
        """Persist an OutputProfile into output_profiles.

        Args:
            profile: Validated OutputProfile domain model.

        Returns:
            Canonical prf_<32_hex> identifier.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on persistence failure.
        """
        return await upsert_output_profile_row(self._conn, self.command_timeout_seconds, profile)

    async def get_output_profile(self, profile_id: str) -> OutputProfile | None:
        """Fetch an OutputProfile by ID.

        Args:
            profile_id: Canonical prf_<32_hex> identifier.

        Returns:
            Hydrated OutputProfile instance, or None if not found.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await get_output_profile_row(self._conn, self.command_timeout_seconds, profile_id)

    async def upsert_task_brief(self, brief: TaskBrief) -> str:
        """Persist a TaskBrief into task_briefs.

        Args:
            brief: Validated TaskBrief domain model.

        Returns:
            Canonical tbr_<32_hex> identifier.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on persistence failure.
        """
        return await upsert_task_brief_row(self._conn, self.command_timeout_seconds, brief)

    async def get_task_brief(self, brief_id: str) -> TaskBrief | None:
        """Fetch a TaskBrief by ID.

        Args:
            brief_id: Canonical tbr_<32_hex> identifier.

        Returns:
            Hydrated TaskBrief instance, or None if not found.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await get_task_brief_row(self._conn, self.command_timeout_seconds, brief_id)

    async def list_task_briefs(self) -> list[TaskBrief]:
        """List all TaskBrief records from task_briefs.

        Returns:
            List of hydrated TaskBrief domain models.

        Raises:
            AppException: With STORAGE_ACCESS_FAILED on query failure.
        """
        return await list_task_brief_rows(self._conn, self.command_timeout_seconds)

    async def upsert_report_artifact(self, artifact: ReportArtifact) -> str:
        """Persist a ReportArtifact into report_artifacts.

        Args:
            artifact: Validated ReportArtifact domain model.

        Returns:
            Canonical rep_<32_hex> identifier.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on persistence failure.
        """
        return await upsert_report_artifact_row(self._conn, self.command_timeout_seconds, artifact)

    async def get_report_artifact(self, report_id: str) -> ReportArtifact | None:
        """Fetch a ReportArtifact by ID.

        Args:
            report_id: Canonical rep_<32_hex> identifier.

        Returns:
            Hydrated ReportArtifact instance, or None if not found.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await get_report_artifact_row(self._conn, self.command_timeout_seconds, report_id)

    async def seed_collection_batch(self, collection_name: str, items: Sequence[BaseModel]) -> int:
        """Idempotently upsert a validated batch of domain entities into PostgreSQL 19.

        Args:
            collection_name: Target collection or table name.
            items: Sequence of validated Pydantic domain models to persist.

        Returns:
            Count of persisted entities.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on batch persistence failure.
        """
        return await seed_collection_batch_rows(self._conn, self.command_timeout_seconds, collection_name, items)

    async def verify_seed_table_counts(self, expected_counts: Mapping[str, int]) -> dict[str, int]:
        """Verify row counts across the canonical PostgreSQL 19 seed tables via SELECT count(*).

        Args:
            expected_counts: Mapping of canonical table/collection names to minimum expected row counts.

        Returns:
            Dictionary mapping canonical table names to verified row counts.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED if verification fails.
        """
        return await verify_seed_table_counts_rows(self._conn, self.command_timeout_seconds, expected_counts)

    async def delete_tenant_secret(self, secret_id: str) -> bool:
        """Delete a TenantSecretDTO row by primary key from tenant_secrets.

        Args:
            secret_id: Canonical sec_<32_hex> secret identifier.

        Returns:
            True if a matching row was deleted, False otherwise.

        Raises:
            AppException: With VALIDATION_FAILED, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
        """
        return await delete_tenant_secret_row(self._conn, self.command_timeout_seconds, secret_id)

    async def list_model_registries(self) -> list[SystemConfigModelRegistry]:
        """List all SystemConfigModelRegistry rows from model_registries.

        Returns:
            List of hydrated SystemConfigModelRegistry domain models.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await list_model_registry_rows(self._conn, self.command_timeout_seconds)

    async def list_mcp_gateways(self) -> list[SystemConfigMCPGateways]:
        """List all SystemConfigMCPGateways rows from mcp_gateways.

        Returns:
            List of hydrated SystemConfigMCPGateways domain models.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await list_mcp_gateway_rows(self._conn, self.command_timeout_seconds)

    async def list_executions(self) -> list[ExecutionRecord]:
        """List all ExecutionRecord rows ordered by created_at DESC.

        Returns:
            List of hydrated ExecutionRecord models ordered newest-first.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await list_execution_rows(self._conn, self.command_timeout_seconds)

    async def insert_audit_log(self, record: AuditLogRecord) -> str:
        """Insert an immutable AuditLogRecord into the append-only audit_logs table.

        Args:
            record: Validated AuditLogRecord domain model.

        Returns:
            Canonical aud_<32_hex> identifier inserted.

        Raises:
            AppException: With VALIDATION_FAILED, CONFLICT, or STORAGE_ACCESS_FAILED on persistence failure.
        """
        return await insert_audit_log_row(self._conn, self.command_timeout_seconds, record)

    async def list_audit_logs(
        self,
        *,
        organization_id: str | None = None,
        actor_id: str | None = None,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[AuditLogRecord]:
        """List AuditLogRecord entries ordered by id DESC with optional parameterized filters.

        Args:
            organization_id: Optional organization filter ('org_<32_hex>' or 'SYSTEM').
            actor_id: Optional actor filter ('usr_<32_hex>' or 'system').
            event_type: Optional event_type string filter.
            limit: Maximum number of records to return.

        Returns:
            List of hydrated AuditLogRecord models ordered newest-first.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await list_audit_log_rows(
            self._conn,
            self.command_timeout_seconds,
            organization_id=organization_id,
            actor_id=actor_id,
            event_type=event_type,
            limit=limit,
        )

    async def insert_usage_record(self, record: UsageRecord) -> str:
        """Insert an immutable UsageRecord into the append-only usage_records table.

        Args:
            record: Validated UsageRecord domain model.

        Returns:
            Canonical usg_<32_hex> identifier inserted.

        Raises:
            AppException: With VALIDATION_FAILED, CONFLICT, or STORAGE_ACCESS_FAILED on persistence failure.
        """
        return await insert_usage_record_row(self._conn, self.command_timeout_seconds, record)

    async def list_usage_records(
        self,
        *,
        organization_id: str | None = None,
        user_id: str | None = None,
        since: datetime | None = None,
    ) -> list[UsageRecord]:
        """List UsageRecord entries ordered chronologically by id ASC with parameterized filters.

        Args:
            organization_id: Optional organization filter ('org_<32_hex>' or 'system').
            user_id: Optional user filter ('usr_<32_hex>' or 'system').
            since: Optional UTC timestamp lower bound.

        Returns:
            List of hydrated UsageRecord models ordered chronologically.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await list_usage_record_rows(
            self._conn,
            self.command_timeout_seconds,
            organization_id=organization_id,
            user_id=user_id,
            since=since,
        )

    async def aggregate_organization_usage(
        self,
        organization_id: str | None = None,
        since: datetime | None = None,
    ) -> UsageRollupSummaryDTO:
        """Compute FinOps token and USD cost rollups via parameterized SQL SUM/COUNT over usage_records.

        Args:
            organization_id: Optional organization filter ('org_<32_hex>' or None for global rollup).
            since: Optional UTC timestamp lower bound.

        Returns:
            Validated UsageRollupSummaryDTO containing aggregated token and cost metrics.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await aggregate_organization_usage_row(
            self._conn,
            self.command_timeout_seconds,
            organization_id=organization_id,
            since=since,
        )

    async def get_user_by_email(self, email: str) -> User | None:
        """Fetch a User by case-insensitive email lookup.

        Args:
            email: Target user email address.

        Returns:
            Hydrated User domain model, or None if not found.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await get_user_by_email_row(self._conn, self.command_timeout_seconds, email)

    async def delete_organization(self, org_id: str) -> bool:
        """Delete an Organization row by primary key from organizations.

        Args:
            org_id: Canonical org_<32_hex> organization identifier.

        Returns:
            True if a matching row was deleted, False otherwise.

        Raises:
            AppException: With VALIDATION_FAILED, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
        """
        return await delete_organization_row(self._conn, self.command_timeout_seconds, org_id)

    async def delete_user(self, user_id: str) -> bool:
        """Delete a User row by primary key from users.

        Args:
            user_id: Canonical usr_<32_hex> user identifier.

        Returns:
            True if a matching row was deleted, False otherwise.

        Raises:
            AppException: With VALIDATION_FAILED, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
        """
        return await delete_user_row(self._conn, self.command_timeout_seconds, user_id)

    async def delete_invitation(self, invitation_id: str) -> bool:
        """Delete an Invitation row by primary key from invitations.

        Args:
            invitation_id: Canonical inv_<32_hex> invitation identifier.

        Returns:
            True if a matching row was deleted, False otherwise.

        Raises:
            AppException: With VALIDATION_FAILED, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
        """
        return await delete_invitation_row(self._conn, self.command_timeout_seconds, invitation_id)

    async def delete_model_registry(self, registry_id: str) -> bool:
        """Delete a SystemConfigModelRegistry row by primary key from model_registries.

        Args:
            registry_id: Canonical mrg_<32_hex> model registry identifier.

        Returns:
            True if a matching row was deleted, False otherwise.

        Raises:
            AppException: With VALIDATION_FAILED, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
        """
        return await delete_model_registry_row(self._conn, self.command_timeout_seconds, registry_id)

    async def delete_mcp_gateway(self, gateway_id: str) -> bool:
        """Delete a SystemConfigMCPGateways row by primary key from mcp_gateways.

        Args:
            gateway_id: Canonical mcp_<32_hex> MCP gateway identifier.

        Returns:
            True if a matching row was deleted, False otherwise.

        Raises:
            AppException: With VALIDATION_FAILED, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
        """
        return await delete_mcp_gateway_row(self._conn, self.command_timeout_seconds, gateway_id)

    async def list_prompt_blocks(self) -> list[AnyPromptBlock]:
        """List all polymorphic AnyPromptBlock rows from prompt_blocks.

        Returns:
            List of hydrated AnyPromptBlock domain models.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await list_prompt_block_rows(self._conn, self.command_timeout_seconds)

    async def delete_prompt_block(self, block_id: str) -> bool:
        """Delete a PromptBlock row by primary key from prompt_blocks.

        Args:
            block_id: Canonical blk_<32_hex> prompt block identifier.

        Returns:
            True if a matching row was deleted, False otherwise.

        Raises:
            AppException: With VALIDATION_FAILED, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
        """
        return await delete_prompt_block_row(self._conn, self.command_timeout_seconds, block_id)

    async def delete_task_brief(self, brief_id: str) -> bool:
        """Delete a TaskBrief row by primary key from task_briefs.

        Args:
            brief_id: Canonical tbr_<32_hex> task brief identifier.

        Returns:
            True if a matching row was deleted, False otherwise.

        Raises:
            AppException: With VALIDATION_FAILED, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
        """
        return await delete_task_brief_row(self._conn, self.command_timeout_seconds, brief_id)

    async def list_output_profiles(self) -> list[OutputProfile]:
        """List all OutputProfile rows from output_profiles.

        Returns:
            List of hydrated OutputProfile domain models.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await list_output_profile_rows(self._conn, self.command_timeout_seconds)

    async def delete_output_profile(self, profile_id: str) -> bool:
        """Delete an OutputProfile row by primary key from output_profiles.

        Args:
            profile_id: Canonical prf_<32_hex> output profile identifier.

        Returns:
            True if a matching row was deleted, False otherwise.

        Raises:
            AppException: With VALIDATION_FAILED, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
        """
        return await delete_output_profile_row(self._conn, self.command_timeout_seconds, profile_id)

    async def list_workflows(self) -> list[Workflow]:
        """List all Workflow rows from workflows.

        Returns:
            List of hydrated Workflow domain models.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await list_workflow_rows(self._conn, self.command_timeout_seconds)

    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a Workflow row by primary key from workflows.

        Args:
            workflow_id: Canonical wf_<32_hex> workflow identifier.

        Returns:
            True if a matching row was deleted, False otherwise.

        Raises:
            AppException: With VALIDATION_FAILED, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
        """
        return await delete_workflow_row(self._conn, self.command_timeout_seconds, workflow_id)

    async def list_steps(self) -> list[Step]:
        """List all Step rows from steps.

        Returns:
            List of hydrated Step domain models.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await list_step_rows(self._conn, self.command_timeout_seconds)

    async def delete_step(self, step_id: str) -> bool:
        """Delete a Step row by primary key from steps.

        Args:
            step_id: Canonical stp_<32_hex> step identifier.

        Returns:
            True if a matching row was deleted, False otherwise.

        Raises:
            AppException: With VALIDATION_FAILED, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
        """
        return await delete_step_row(self._conn, self.command_timeout_seconds, step_id)

    async def update_execution_occ(self, execution_id: str, updates: ExecutionUpdateDTO) -> bool:
        """Apply partial ExecutionUpdateDTO updates to an existing ExecutionRecord with OCC checking.

        Args:
            execution_id: Canonical exe_<32_hex> execution identifier.
            updates: Validated ExecutionUpdateDTO carrying field updates and optional expected_state_version.

        Returns:
            True if the execution existed and was updated, False otherwise.

        Raises:
            AppException: With VALIDATION_FAILED, CONFLICT, or STORAGE_ACCESS_FAILED.
        """
        return await update_execution_occ_row(self._conn, self.command_timeout_seconds, execution_id, updates)

    async def delete_execution(self, execution_id: str) -> bool:
        """Delete an ExecutionRecord row by primary key from executions.

        Args:
            execution_id: Canonical exe_<32_hex> execution identifier.

        Returns:
            True if a matching row was deleted, False otherwise.

        Raises:
            AppException: With VALIDATION_FAILED, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
        """
        return await delete_execution_row(self._conn, self.command_timeout_seconds, execution_id)

    async def list_report_artifacts_by_execution(self, execution_id: str) -> list[ReportArtifact]:
        """List all ReportArtifact rows belonging to a parent execution ordered newest-first.

        Args:
            execution_id: Canonical exe_<32_hex> parent execution identifier.

        Returns:
            List of hydrated ReportArtifact domain models ordered by created_at DESC.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await list_report_artifacts_by_execution_row(self._conn, self.command_timeout_seconds, execution_id)

    async def delete_report_artifact(self, report_id: str) -> bool:
        """Delete a ReportArtifact row by primary key from report_artifacts.

        Args:
            report_id: Canonical rep_<32_hex> report artifact identifier.

        Returns:
            True if a matching row was deleted, False otherwise.

        Raises:
            AppException: With VALIDATION_FAILED, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
        """
        return await delete_report_artifact_row(self._conn, self.command_timeout_seconds, report_id)
