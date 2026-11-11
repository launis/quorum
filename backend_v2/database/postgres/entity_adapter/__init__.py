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
from backend_v2.settings import get_settings

# Explicit redundant re-exports (Symbol as Symbol) across all 6 stage sub-modules
from .coercion_and_constants import _COLLECTION_TO_TABLE_MAP as _COLLECTION_TO_TABLE_MAP
from .coercion_and_constants import _ROOT_SYSTEM_ORG_UUID7 as _ROOT_SYSTEM_ORG_UUID7
from .coercion_and_constants import _SYSTEM_ORG_UUID7 as _SYSTEM_ORG_UUID7
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
from .execution_and_report_stage import _GET_EXECUTION_SQL as _GET_EXECUTION_SQL
from .execution_and_report_stage import _GET_REPORT_ARTIFACT_SQL as _GET_REPORT_ARTIFACT_SQL
from .execution_and_report_stage import _GET_REPORT_BINARY_SQL as _GET_REPORT_BINARY_SQL
from .execution_and_report_stage import _LIST_EXECUTIONS_SQL as _LIST_EXECUTIONS_SQL
from .execution_and_report_stage import _LIST_REPORT_ARTIFACTS_SQL as _LIST_REPORT_ARTIFACTS_SQL
from .execution_and_report_stage import _MARK_REPORT_ARTIFACT_PDF_SQL as _MARK_REPORT_ARTIFACT_PDF_SQL
from .execution_and_report_stage import _SAVE_EXECUTION_SQL as _SAVE_EXECUTION_SQL
from .execution_and_report_stage import _SAVE_REPORT_BINARY_SQL as _SAVE_REPORT_BINARY_SQL
from .execution_and_report_stage import _UPSERT_REPORT_ARTIFACT_SQL as _UPSERT_REPORT_ARTIFACT_SQL
from .execution_and_report_stage import get_execution_row as get_execution_row
from .execution_and_report_stage import get_report_artifact_row as get_report_artifact_row
from .execution_and_report_stage import get_report_binary_row as get_report_binary_row
from .execution_and_report_stage import hydrate_execution_row as hydrate_execution_row
from .execution_and_report_stage import hydrate_report_artifact_row as hydrate_report_artifact_row
from .execution_and_report_stage import list_execution_rows as list_execution_rows
from .execution_and_report_stage import save_execution_row as save_execution_row
from .execution_and_report_stage import save_report_binary_row as save_report_binary_row
from .execution_and_report_stage import upsert_report_artifact_row as upsert_report_artifact_row
from .iam_and_system_stage import _AGGREGATE_USAGE_BASE_SQL as _AGGREGATE_USAGE_BASE_SQL
from .iam_and_system_stage import _DELETE_TENANT_SECRET_SQL as _DELETE_TENANT_SECRET_SQL
from .iam_and_system_stage import _GET_EXECUTION_ASSIGNMENT_SQL as _GET_EXECUTION_ASSIGNMENT_SQL
from .iam_and_system_stage import _GET_INVITATION_SQL as _GET_INVITATION_SQL
from .iam_and_system_stage import _GET_ORGANIZATION_SQL as _GET_ORGANIZATION_SQL
from .iam_and_system_stage import _GET_SYSTEM_CONFIG_SQL as _GET_SYSTEM_CONFIG_SQL
from .iam_and_system_stage import _GET_TENANT_SECRET_SQL as _GET_TENANT_SECRET_SQL
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
from .iam_and_system_stage import _LIST_ORGANIZATIONS_SQL as _LIST_ORGANIZATIONS_SQL
from .iam_and_system_stage import _LIST_SYSTEM_CONFIGS_SQL as _LIST_SYSTEM_CONFIGS_SQL
from .iam_and_system_stage import _LIST_TENANT_SECRETS_BY_ORG_SQL as _LIST_TENANT_SECRETS_BY_ORG_SQL
from .iam_and_system_stage import _LIST_TENANT_SECRETS_SQL as _LIST_TENANT_SECRETS_SQL
from .iam_and_system_stage import _LIST_USAGE_RECORDS_SQL as _LIST_USAGE_RECORDS_SQL
from .iam_and_system_stage import _LIST_USERS_BY_ORG_SQL as _LIST_USERS_BY_ORG_SQL
from .iam_and_system_stage import _LIST_USERS_SQL as _LIST_USERS_SQL
from .iam_and_system_stage import _UPSERT_EXECUTION_ASSIGNMENT_SQL as _UPSERT_EXECUTION_ASSIGNMENT_SQL
from .iam_and_system_stage import _UPSERT_INVITATION_SQL as _UPSERT_INVITATION_SQL
from .iam_and_system_stage import _UPSERT_ORGANIZATION_SQL as _UPSERT_ORGANIZATION_SQL
from .iam_and_system_stage import _UPSERT_SYSTEM_CONFIG_SQL as _UPSERT_SYSTEM_CONFIG_SQL
from .iam_and_system_stage import _UPSERT_TENANT_SECRET_SQL as _UPSERT_TENANT_SECRET_SQL
from .iam_and_system_stage import _UPSERT_USER_SQL as _UPSERT_USER_SQL
from .iam_and_system_stage import aggregate_organization_usage_row as aggregate_organization_usage_row
from .iam_and_system_stage import delete_tenant_secret_row as delete_tenant_secret_row
from .iam_and_system_stage import get_execution_assignment_row as get_execution_assignment_row
from .iam_and_system_stage import get_invitation_row as get_invitation_row
from .iam_and_system_stage import get_organization_row as get_organization_row
from .iam_and_system_stage import get_system_config_row as get_system_config_row
from .iam_and_system_stage import get_tenant_secret_row as get_tenant_secret_row
from .iam_and_system_stage import get_user_row as get_user_row
from .iam_and_system_stage import hydrate_audit_log_row as hydrate_audit_log_row
from .iam_and_system_stage import hydrate_execution_assignment_row as hydrate_execution_assignment_row
from .iam_and_system_stage import hydrate_invitation_row as hydrate_invitation_row
from .iam_and_system_stage import hydrate_organization_row as hydrate_organization_row
from .iam_and_system_stage import hydrate_system_config_row as hydrate_system_config_row
from .iam_and_system_stage import hydrate_tenant_secret_row as hydrate_tenant_secret_row
from .iam_and_system_stage import hydrate_usage_record_row as hydrate_usage_record_row
from .iam_and_system_stage import hydrate_user_row as hydrate_user_row
from .iam_and_system_stage import insert_audit_log_row as insert_audit_log_row
from .iam_and_system_stage import insert_usage_record_row as insert_usage_record_row
from .iam_and_system_stage import list_audit_log_rows as list_audit_log_rows
from .iam_and_system_stage import list_execution_assignment_rows as list_execution_assignment_rows
from .iam_and_system_stage import list_invitation_rows as list_invitation_rows
from .iam_and_system_stage import list_organization_rows as list_organization_rows
from .iam_and_system_stage import list_system_config_rows as list_system_config_rows
from .iam_and_system_stage import list_system_configs_rows as list_system_configs_rows
from .iam_and_system_stage import list_tenant_secret_rows as list_tenant_secret_rows
from .iam_and_system_stage import list_usage_record_rows as list_usage_record_rows
from .iam_and_system_stage import list_user_rows as list_user_rows
from .iam_and_system_stage import upsert_execution_assignment_row as upsert_execution_assignment_row
from .iam_and_system_stage import upsert_invitation_row as upsert_invitation_row
from .iam_and_system_stage import upsert_organization_row as upsert_organization_row
from .iam_and_system_stage import upsert_system_config_row as upsert_system_config_row
from .iam_and_system_stage import upsert_tenant_secret_row as upsert_tenant_secret_row
from .iam_and_system_stage import upsert_user_row as upsert_user_row
from .prompt_block_and_step_stage import _GET_PROMPT_BLOCK_SQL as _GET_PROMPT_BLOCK_SQL
from .prompt_block_and_step_stage import _GET_STEP_SQL as _GET_STEP_SQL
from .prompt_block_and_step_stage import _LIST_PROMPT_BLOCKS_SQL as _LIST_PROMPT_BLOCKS_SQL
from .prompt_block_and_step_stage import _LIST_STEPS_SQL as _LIST_STEPS_SQL
from .prompt_block_and_step_stage import _UPSERT_PROMPT_BLOCK_SQL as _UPSERT_PROMPT_BLOCK_SQL
from .prompt_block_and_step_stage import _UPSERT_STEP_SQL as _UPSERT_STEP_SQL
from .prompt_block_and_step_stage import get_prompt_block_row as get_prompt_block_row
from .prompt_block_and_step_stage import get_step_row as get_step_row
from .prompt_block_and_step_stage import hydrate_prompt_block_row as hydrate_prompt_block_row
from .prompt_block_and_step_stage import hydrate_step_row as hydrate_step_row
from .prompt_block_and_step_stage import upsert_prompt_block_row as upsert_prompt_block_row
from .prompt_block_and_step_stage import upsert_step_row as upsert_step_row
from .seed_and_collection_stage import seed_collection_batch_rows as seed_collection_batch_rows
from .seed_and_collection_stage import verify_seed_table_counts_rows as verify_seed_table_counts_rows
from .workflow_and_profile_stage import _GET_OUTPUT_PROFILE_SQL as _GET_OUTPUT_PROFILE_SQL
from .workflow_and_profile_stage import _GET_TASK_BRIEF_SQL as _GET_TASK_BRIEF_SQL
from .workflow_and_profile_stage import _GET_WORKFLOW_SQL as _GET_WORKFLOW_SQL
from .workflow_and_profile_stage import _LIST_OUTPUT_PROFILES_SQL as _LIST_OUTPUT_PROFILES_SQL
from .workflow_and_profile_stage import _LIST_TASK_BRIEFS_SQL as _LIST_TASK_BRIEFS_SQL
from .workflow_and_profile_stage import _LIST_WORKFLOWS_SQL as _LIST_WORKFLOWS_SQL
from .workflow_and_profile_stage import _UPSERT_OUTPUT_PROFILE_SQL as _UPSERT_OUTPUT_PROFILE_SQL
from .workflow_and_profile_stage import _UPSERT_TASK_BRIEF_SQL as _UPSERT_TASK_BRIEF_SQL
from .workflow_and_profile_stage import _UPSERT_WORKFLOW_SQL as _UPSERT_WORKFLOW_SQL
from .workflow_and_profile_stage import get_output_profile_row as get_output_profile_row
from .workflow_and_profile_stage import get_task_brief_row as get_task_brief_row
from .workflow_and_profile_stage import get_workflow_row as get_workflow_row
from .workflow_and_profile_stage import hydrate_output_profile_row as hydrate_output_profile_row
from .workflow_and_profile_stage import hydrate_task_brief_row as hydrate_task_brief_row
from .workflow_and_profile_stage import hydrate_workflow_row as hydrate_workflow_row
from .workflow_and_profile_stage import list_task_brief_rows as list_task_brief_rows
from .workflow_and_profile_stage import upsert_output_profile_row as upsert_output_profile_row
from .workflow_and_profile_stage import upsert_task_brief_row as upsert_task_brief_row
from .workflow_and_profile_stage import upsert_workflow_row as upsert_workflow_row

type AnySystemConfig = SystemConfigModelRegistry | SystemConfigMCPGateways

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
    _hydrate_system_config_row = staticmethod(hydrate_system_config_row)
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

    async def upsert_system_config(self, cfg: AnySystemConfig) -> str:
        """Persist a SystemConfigModelRegistry or SystemConfigMCPGateways into system_configs.

        Args:
            cfg: Validated SystemConfigModelRegistry or SystemConfigMCPGateways model.

        Returns:
            Canonical sys_<32_hex> identifier.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on persistence failure.
        """
        return await upsert_system_config_row(self._conn, self.command_timeout_seconds, cfg)

    async def get_system_config(self, config_id: str) -> AnySystemConfig | None:
        """Fetch a SystemConfig by ID.

        Args:
            config_id: Canonical sys_<32_hex> identifier.

        Returns:
            Hydrated SystemConfigModelRegistry or SystemConfigMCPGateways instance, or None if not found.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await get_system_config_row(self._conn, self.command_timeout_seconds, config_id)

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

    async def list_system_configs(self) -> list[AnySystemConfig]:
        """List all polymorphic SystemConfig rows from system_configs.

        Returns:
            List of hydrated SystemConfigModelRegistry and SystemConfigMCPGateways models.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on query failure.
        """
        return await list_system_config_rows(self._conn, self.command_timeout_seconds)

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
