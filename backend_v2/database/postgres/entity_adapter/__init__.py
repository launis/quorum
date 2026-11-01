"""PostgreSQL 19 Zero-ORM Entity Persistence Package Facade."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from pydantic import BaseModel, JsonValue

from backend_v2.database.postgres.pool import AsyncPgConnectionProtocol
from backend_v2.models.auth import Organization, User
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import AnyPromptBlock
from backend_v2.models.domain.proposition_graph import ReportBinaryPayloadDTO
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.system_config import SystemConfigMCPGateways, SystemConfigModelRegistry
from backend_v2.models.domain.workflow import Workflow
from backend_v2.settings import get_settings

# Phase 4, Step 2: Explicit redundant re-exports (Symbol as Symbol) across all 6 stage sub-modules
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
from .coercion_and_constants import _ReportBinaryRowDTO as _ReportBinaryRowDTO
from .coercion_and_constants import execute_entity_upsert as execute_entity_upsert
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
from .execution_and_report_stage import save_execution_row as save_execution_row
from .execution_and_report_stage import save_report_binary_row as save_report_binary_row
from .execution_and_report_stage import upsert_report_artifact_row as upsert_report_artifact_row
from .iam_and_system_stage import _GET_ORGANIZATION_SQL as _GET_ORGANIZATION_SQL
from .iam_and_system_stage import _GET_SYSTEM_CONFIG_SQL as _GET_SYSTEM_CONFIG_SQL
from .iam_and_system_stage import _GET_USER_SQL as _GET_USER_SQL
from .iam_and_system_stage import _LIST_ORGANIZATIONS_SQL as _LIST_ORGANIZATIONS_SQL
from .iam_and_system_stage import _LIST_SYSTEM_CONFIGS_SQL as _LIST_SYSTEM_CONFIGS_SQL
from .iam_and_system_stage import _LIST_USERS_SQL as _LIST_USERS_SQL
from .iam_and_system_stage import _UPSERT_ORGANIZATION_SQL as _UPSERT_ORGANIZATION_SQL
from .iam_and_system_stage import _UPSERT_SYSTEM_CONFIG_SQL as _UPSERT_SYSTEM_CONFIG_SQL
from .iam_and_system_stage import _UPSERT_USER_SQL as _UPSERT_USER_SQL
from .iam_and_system_stage import get_organization_row as get_organization_row
from .iam_and_system_stage import get_system_config_row as get_system_config_row
from .iam_and_system_stage import get_user_row as get_user_row
from .iam_and_system_stage import hydrate_organization_row as hydrate_organization_row
from .iam_and_system_stage import hydrate_system_config_row as hydrate_system_config_row
from .iam_and_system_stage import hydrate_user_row as hydrate_user_row
from .iam_and_system_stage import upsert_organization_row as upsert_organization_row
from .iam_and_system_stage import upsert_system_config_row as upsert_system_config_row
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
from .seed_and_collection_stage import clear_collection_documents_rows as clear_collection_documents_rows
from .seed_and_collection_stage import delete_collection_document_row as delete_collection_document_row
from .seed_and_collection_stage import get_collection_document_row as get_collection_document_row
from .seed_and_collection_stage import list_collection_documents_rows as list_collection_documents_rows
from .seed_and_collection_stage import seed_collection_batch_rows as seed_collection_batch_rows
from .seed_and_collection_stage import upsert_collection_document_row as upsert_collection_document_row
from .seed_and_collection_stage import verify_seed_table_counts_rows as verify_seed_table_counts_rows
from .workflow_and_profile_stage import _GET_OUTPUT_PROFILE_SQL as _GET_OUTPUT_PROFILE_SQL
from .workflow_and_profile_stage import _GET_WORKFLOW_SQL as _GET_WORKFLOW_SQL
from .workflow_and_profile_stage import _LIST_OUTPUT_PROFILES_SQL as _LIST_OUTPUT_PROFILES_SQL
from .workflow_and_profile_stage import _LIST_WORKFLOWS_SQL as _LIST_WORKFLOWS_SQL
from .workflow_and_profile_stage import _UPSERT_OUTPUT_PROFILE_SQL as _UPSERT_OUTPUT_PROFILE_SQL
from .workflow_and_profile_stage import _UPSERT_WORKFLOW_SQL as _UPSERT_WORKFLOW_SQL
from .workflow_and_profile_stage import get_output_profile_row as get_output_profile_row
from .workflow_and_profile_stage import get_workflow_row as get_workflow_row
from .workflow_and_profile_stage import hydrate_output_profile_row as hydrate_output_profile_row
from .workflow_and_profile_stage import hydrate_workflow_row as hydrate_workflow_row
from .workflow_and_profile_stage import upsert_output_profile_row as upsert_output_profile_row
from .workflow_and_profile_stage import upsert_workflow_row as upsert_workflow_row

type AnySystemConfig = SystemConfigModelRegistry | SystemConfigMCPGateways

__all__ = ["CANONICAL_SEED_TABLES", "PostgresEntityAdapter"]


class PostgresEntityAdapter:
    """Zero-ORM PostgreSQL 19 adapter implementing EntityPersistencePort."""

    _hydrate_execution_row = staticmethod(hydrate_execution_row)
    _hydrate_organization_row = staticmethod(hydrate_organization_row)
    _hydrate_user_row = staticmethod(hydrate_user_row)
    _hydrate_system_config_row = staticmethod(hydrate_system_config_row)
    _hydrate_prompt_block_row = staticmethod(hydrate_prompt_block_row)
    _hydrate_step_row = staticmethod(hydrate_step_row)
    _hydrate_workflow_row = staticmethod(hydrate_workflow_row)
    _hydrate_output_profile_row = staticmethod(hydrate_output_profile_row)
    _hydrate_report_artifact_row = staticmethod(hydrate_report_artifact_row)

    def __init__(self, connection: AsyncPgConnectionProtocol, command_timeout_seconds: float | None = None) -> None:
        """Initialize the PostgreSQL entity adapter over an active connection."""
        self._conn: AsyncPgConnectionProtocol = connection
        if command_timeout_seconds is not None:
            self.command_timeout_seconds: float = command_timeout_seconds
        else:
            self.command_timeout_seconds = get_settings().postgres_command_timeout_seconds

    async def save_report_binary(self, payload: ReportBinaryPayloadDTO) -> None:
        """Persist a ReportBinaryPayloadDTO into report_binaries and mark has_pdf."""
        await save_report_binary_row(self._conn, self.command_timeout_seconds, payload)

    async def get_report_binary(self, report_id: str) -> ReportBinaryPayloadDTO | None:
        """Retrieve a ReportBinaryPayloadDTO from report_binaries by canonical report_id."""
        return await get_report_binary_row(self._conn, self.command_timeout_seconds, report_id)

    async def save_execution(self, record: ExecutionRecord) -> str:
        """Persist an ExecutionRecord into the PostgreSQL 19 executions table."""
        return await save_execution_row(self._conn, self.command_timeout_seconds, record)

    async def get_execution(self, execution_id: str) -> ExecutionRecord | None:
        """Retrieve and reconstitute an ExecutionRecord from PostgreSQL by execution_id."""
        return await get_execution_row(self._conn, self.command_timeout_seconds, execution_id)

    async def _execute_upsert(self, sql: str, *args: object, entity_label: str, entity_id: str) -> str:
        """Execute a parameterized upsert statement and translate transport errors to AppException."""
        return await execute_entity_upsert(
            self._conn, self.command_timeout_seconds, sql, *args, entity_id=entity_id, entity_label=entity_label
        )

    async def upsert_organization(self, org: Organization) -> str:
        """Persist an Organization into the organizations table."""
        return await upsert_organization_row(self._conn, self.command_timeout_seconds, org)

    async def get_organization(self, org_id: str) -> Organization | None:
        """Fetch an Organization by ID."""
        return await get_organization_row(self._conn, self.command_timeout_seconds, org_id)

    async def upsert_user(self, user: User) -> str:
        """Persist a User into the users table."""
        return await upsert_user_row(self._conn, self.command_timeout_seconds, user)

    async def get_user(self, user_id: str) -> User | None:
        """Fetch a User by ID."""
        return await get_user_row(self._conn, self.command_timeout_seconds, user_id)

    async def upsert_system_config(self, cfg: AnySystemConfig) -> str:
        """Persist a SystemConfigModelRegistry or SystemConfigMCPGateways into system_configs."""
        return await upsert_system_config_row(self._conn, self.command_timeout_seconds, cfg)

    async def get_system_config(self, config_id: str) -> AnySystemConfig | None:
        """Fetch a SystemConfig by ID."""
        return await get_system_config_row(self._conn, self.command_timeout_seconds, config_id)

    async def upsert_prompt_block(self, block: AnyPromptBlock) -> str:
        """Persist a polymorphic AnyPromptBlock into prompt_blocks."""
        return await upsert_prompt_block_row(self._conn, self.command_timeout_seconds, block)

    async def get_prompt_block(self, block_id: str) -> AnyPromptBlock | None:
        """Fetch an AnyPromptBlock by ID."""
        return await get_prompt_block_row(self._conn, self.command_timeout_seconds, block_id)

    async def upsert_step(self, step: Step) -> str:
        """Persist a Step into steps."""
        return await upsert_step_row(self._conn, self.command_timeout_seconds, step)

    async def get_step(self, step_id: str) -> Step | None:
        """Fetch a Step by ID."""
        return await get_step_row(self._conn, self.command_timeout_seconds, step_id)

    async def upsert_workflow(self, wf: Workflow) -> str:
        """Persist a Workflow into workflows."""
        return await upsert_workflow_row(self._conn, self.command_timeout_seconds, wf)

    async def get_workflow(self, workflow_id: str) -> Workflow | None:
        """Fetch a Workflow by ID."""
        return await get_workflow_row(self._conn, self.command_timeout_seconds, workflow_id)

    async def upsert_output_profile(self, profile: OutputProfile) -> str:
        """Persist an OutputProfile into output_profiles."""
        return await upsert_output_profile_row(self._conn, self.command_timeout_seconds, profile)

    async def get_output_profile(self, profile_id: str) -> OutputProfile | None:
        """Fetch an OutputProfile by ID."""
        return await get_output_profile_row(self._conn, self.command_timeout_seconds, profile_id)

    async def upsert_report_artifact(self, artifact: ReportArtifact) -> str:
        """Persist a ReportArtifact into report_artifacts."""
        return await upsert_report_artifact_row(self._conn, self.command_timeout_seconds, artifact)

    async def get_report_artifact(self, report_id: str) -> ReportArtifact | None:
        """Fetch a ReportArtifact by ID."""
        return await get_report_artifact_row(self._conn, self.command_timeout_seconds, report_id)

    async def seed_collection_batch(self, collection_name: str, items: Sequence[BaseModel]) -> int:
        """Idempotently upsert a validated batch of domain entities into PostgreSQL 19."""
        return await seed_collection_batch_rows(self._conn, self.command_timeout_seconds, collection_name, items)

    async def verify_seed_table_counts(self, expected_counts: Mapping[str, int]) -> dict[str, int]:
        """Verify row counts across the 10 core PostgreSQL 19 tables via SELECT count(*)."""
        return await verify_seed_table_counts_rows(self._conn, self.command_timeout_seconds, expected_counts)

    async def list_collection_documents(self, collection_name: str) -> list[dict[str, JsonValue]]:
        """List all documents from a canonical PostgreSQL 19 table as JSON-compatible dictionaries."""
        return await list_collection_documents_rows(self._conn, self.command_timeout_seconds, collection_name)

    async def get_collection_document(self, collection_name: str, doc_id: str) -> dict[str, JsonValue] | None:
        """Fetch a single document by ID from a canonical PostgreSQL 19 table."""
        return await get_collection_document_row(self._conn, self.command_timeout_seconds, collection_name, doc_id)

    async def upsert_collection_document(self, col: str, doc_id: str, data: Mapping[str, JsonValue]) -> bool:
        """Validate and upsert a document dictionary into its canonical PostgreSQL 19 table."""
        return await upsert_collection_document_row(self._conn, self.command_timeout_seconds, col, doc_id, data)

    async def delete_collection_document(self, collection_name: str, doc_id: str) -> bool:
        """Delete a row by ID from a canonical PostgreSQL 19 table."""
        return await delete_collection_document_row(self._conn, self.command_timeout_seconds, collection_name, doc_id)

    async def clear_collection_documents(self, collection_name: str) -> None:
        """Delete all rows from a canonical PostgreSQL 19 table."""
        await clear_collection_documents_rows(self._conn, self.command_timeout_seconds, collection_name)
