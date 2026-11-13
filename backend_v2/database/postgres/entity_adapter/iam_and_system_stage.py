"""PostgreSQL 19 SQL constants, hydration, upsert, and fetch stage for IAM, assignments, secrets, and ledgers."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

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
    _parse_system_safe_org_uuid7,
    _parse_system_safe_user_uuid7,
    execute_entity_delete,
    execute_entity_upsert,
    resolve_effective_timeout,
    translate_postgres_exception,
    validate_hydrated_row,
)
from backend_v2.database.postgres.pool import AsyncPgConnectionProtocol, AsyncPgRecordProtocol
from backend_v2.exceptions import AppException
from backend_v2.models.auth import Invitation, Organization, TenantSecretDTO, User
from backend_v2.models.core_base import format_prefixed_uuid7, parse_prefixed_uuid7
from backend_v2.models.domain.base import AuditLogRecord, UsageRecord, UsageRollupSummaryDTO
from backend_v2.models.domain.execution import ExecutionAssignment
from backend_v2.models.domain.system_config import SystemConfigMCPGateways, SystemConfigModelRegistry
from backend_v2.models.enums import EntityPrefix, SecretScope

__all__ = [
    "_AGGREGATE_USAGE_BASE_SQL",
    "_DELETE_INVITATION_SQL",
    "_DELETE_MCP_GATEWAY_SQL",
    "_DELETE_MODEL_REGISTRY_SQL",
    "_DELETE_ORGANIZATION_SQL",
    "_DELETE_TENANT_SECRET_SQL",
    "_DELETE_USER_SQL",
    "_GET_EXECUTION_ASSIGNMENT_SQL",
    "_GET_INVITATION_SQL",
    "_GET_MCP_GATEWAY_SQL",
    "_GET_MODEL_REGISTRY_SQL",
    "_GET_ORGANIZATION_SQL",
    "_GET_TENANT_SECRET_SQL",
    "_GET_USER_BY_EMAIL_SQL",
    "_GET_USER_SQL",
    "_INSERT_AUDIT_LOG_SQL",
    "_INSERT_USAGE_RECORD_SQL",
    "_LIST_AUDIT_LOGS_SQL",
    "_LIST_EXECUTION_ASSIGNMENTS_BY_ORG_SQL",
    "_LIST_EXECUTION_ASSIGNMENTS_SQL",
    "_LIST_INVITATIONS_BY_ORG_SQL",
    "_LIST_INVITATIONS_SQL",
    "_LIST_MCP_GATEWAYS_SQL",
    "_LIST_MODEL_REGISTRIES_SQL",
    "_LIST_ORGANIZATIONS_SQL",
    "_LIST_TENANT_SECRETS_BY_ORG_SQL",
    "_LIST_TENANT_SECRETS_SQL",
    "_LIST_USAGE_RECORDS_SQL",
    "_LIST_USERS_BY_ORG_SQL",
    "_LIST_USERS_SQL",
    "_UPSERT_EXECUTION_ASSIGNMENT_SQL",
    "_UPSERT_INVITATION_SQL",
    "_UPSERT_MCP_GATEWAY_SQL",
    "_UPSERT_MODEL_REGISTRY_SQL",
    "_UPSERT_ORGANIZATION_SQL",
    "_UPSERT_TENANT_SECRET_SQL",
    "_UPSERT_USER_SQL",
    "aggregate_organization_usage_row",
    "delete_invitation_row",
    "delete_mcp_gateway_row",
    "delete_model_registry_row",
    "delete_organization_row",
    "delete_tenant_secret_row",
    "delete_user_row",
    "get_execution_assignment_row",
    "get_invitation_row",
    "get_mcp_gateway_row",
    "get_model_registry_row",
    "get_organization_row",
    "get_tenant_secret_row",
    "get_user_by_email_row",
    "get_user_row",
    "hydrate_audit_log_row",
    "hydrate_execution_assignment_row",
    "hydrate_invitation_row",
    "hydrate_mcp_gateway_row",
    "hydrate_model_registry_row",
    "hydrate_organization_row",
    "hydrate_tenant_secret_row",
    "hydrate_usage_record_row",
    "hydrate_user_row",
    "insert_audit_log_row",
    "insert_usage_record_row",
    "list_audit_log_rows",
    "list_execution_assignment_rows",
    "list_invitation_rows",
    "list_mcp_gateway_rows",
    "list_model_registry_rows",
    "list_organization_rows",
    "list_tenant_secret_rows",
    "list_usage_record_rows",
    "list_user_rows",
    "upsert_execution_assignment_row",
    "upsert_invitation_row",
    "upsert_mcp_gateway_row",
    "upsert_model_registry_row",
    "upsert_organization_row",
    "upsert_tenant_secret_row",
    "upsert_user_row",
]

_UPSERT_ORGANIZATION_SQL: str = """INSERT INTO organizations (id, slug, name, is_active, tier, contact_email,
    billing_id, subscription_status, quota_limit, tpm_limit, rpm_limit, allowed_email_domains)
VALUES ($1::uuid, $2, $3, $4, $5, $6, $7, $8, $9::numeric, $10::bigint, $11, $12::jsonb)
ON CONFLICT (id) DO UPDATE SET slug = EXCLUDED.slug, name = EXCLUDED.name, is_active = EXCLUDED.is_active,
    tier = EXCLUDED.tier, contact_email = EXCLUDED.contact_email, billing_id = EXCLUDED.billing_id,
    subscription_status = EXCLUDED.subscription_status, quota_limit = EXCLUDED.quota_limit,
    tpm_limit = EXCLUDED.tpm_limit, rpm_limit = EXCLUDED.rpm_limit,
    allowed_email_domains = EXCLUDED.allowed_email_domains"""

_GET_ORGANIZATION_SQL: str = """SELECT id, slug, name, created_at, is_active, tier, contact_email, billing_id,
       subscription_status, quota_limit, tpm_limit, rpm_limit, allowed_email_domains
FROM organizations WHERE id = $1::uuid"""

_LIST_ORGANIZATIONS_SQL: str = """SELECT id, slug, name, created_at, is_active, tier, contact_email, billing_id,
       subscription_status, quota_limit, tpm_limit, rpm_limit, allowed_email_domains FROM organizations"""

_UPSERT_USER_SQL: str = """INSERT INTO users (id, slug, firebase_uid, email, name, role, organization_id, is_active,
    language, theme_mode, created_by, deleted_at)
VALUES ($1::uuid, $2, $3, $4, $5, $6, $7::uuid, $8, $9, $10, $11::uuid, $12::timestamptz)
ON CONFLICT (id) DO UPDATE SET slug = EXCLUDED.slug, firebase_uid = EXCLUDED.firebase_uid, email = EXCLUDED.email,
    name = EXCLUDED.name, role = EXCLUDED.role, organization_id = EXCLUDED.organization_id,
    is_active = EXCLUDED.is_active, language = EXCLUDED.language, theme_mode = EXCLUDED.theme_mode,
    created_by = EXCLUDED.created_by, deleted_at = EXCLUDED.deleted_at"""

_GET_USER_SQL: str = """SELECT id, slug, firebase_uid, email, name, role, organization_id, is_active, language,
       theme_mode, created_at, created_by, deleted_at FROM users WHERE id = $1::uuid"""

_LIST_USERS_SQL: str = """SELECT id, slug, firebase_uid, email, name, role, organization_id, is_active, language,
       theme_mode, created_at, created_by, deleted_at FROM users"""

_LIST_USERS_BY_ORG_SQL: str = """SELECT id, slug, firebase_uid, email, name, role, organization_id, is_active, language,
       theme_mode, created_at, created_by, deleted_at FROM users WHERE organization_id = $1::uuid"""

_UPSERT_INVITATION_SQL: str = """INSERT INTO invitations (id, organization_id, email, role, token_hash, status,
    email_delivery_status, invited_by, expires_at)
VALUES ($1::uuid, $2::uuid, $3, $4, $5, $6, $7, $8::uuid, $9::timestamptz)
ON CONFLICT (id) DO UPDATE SET organization_id = EXCLUDED.organization_id, email = EXCLUDED.email,
    role = EXCLUDED.role, token_hash = EXCLUDED.token_hash, status = EXCLUDED.status,
    email_delivery_status = EXCLUDED.email_delivery_status, invited_by = EXCLUDED.invited_by,
    expires_at = EXCLUDED.expires_at"""

_GET_INVITATION_SQL: str = """SELECT id, organization_id, email, role, token_hash, status, email_delivery_status,
       invited_by, expires_at, created_at FROM invitations WHERE id = $1::uuid"""

_LIST_INVITATIONS_SQL: str = """SELECT id, organization_id, email, role, token_hash, status, email_delivery_status,
       invited_by, expires_at, created_at FROM invitations"""

_LIST_INVITATIONS_BY_ORG_SQL: str = """SELECT id, organization_id, email, role, token_hash, status,
       email_delivery_status, invited_by, expires_at, created_at
FROM invitations WHERE organization_id = $1::uuid"""

_UPSERT_TENANT_SECRET_SQL: str = """INSERT INTO tenant_secrets (id, organization_id, mcp_gateway_id, scope,
    target_identifier, storage_mode, secret_manager_version_uri, encrypted_dek, ciphertext, nonce, kek_version,
    masked_hint, updated_by, updated_at)
VALUES ($1::uuid, $2::uuid, $3::uuid, $4, $5, $6, $7, $8::bytea, $9::bytea, $10::bytea, $11, $12, $13::uuid, $14::timestamptz)
ON CONFLICT (id) DO UPDATE SET organization_id = EXCLUDED.organization_id,
    mcp_gateway_id = EXCLUDED.mcp_gateway_id, scope = EXCLUDED.scope,
    target_identifier = EXCLUDED.target_identifier, storage_mode = EXCLUDED.storage_mode,
    secret_manager_version_uri = EXCLUDED.secret_manager_version_uri,
    encrypted_dek = EXCLUDED.encrypted_dek, ciphertext = EXCLUDED.ciphertext, nonce = EXCLUDED.nonce,
    kek_version = EXCLUDED.kek_version, masked_hint = EXCLUDED.masked_hint,
    updated_by = EXCLUDED.updated_by, updated_at = EXCLUDED.updated_at"""

_GET_TENANT_SECRET_SQL: str = """SELECT id, organization_id, mcp_gateway_id, scope, target_identifier, storage_mode,
       secret_manager_version_uri, encrypted_dek, ciphertext, nonce, kek_version, masked_hint, updated_by, updated_at
FROM tenant_secrets WHERE id = $1::uuid"""

_LIST_TENANT_SECRETS_SQL: str = """SELECT id, organization_id, mcp_gateway_id, scope, target_identifier, storage_mode,
       secret_manager_version_uri, encrypted_dek, ciphertext, nonce, kek_version, masked_hint, updated_by, updated_at
FROM tenant_secrets"""

_LIST_TENANT_SECRETS_BY_ORG_SQL: str = """SELECT id, organization_id, mcp_gateway_id, scope, target_identifier, storage_mode,
       secret_manager_version_uri, encrypted_dek, ciphertext, nonce, kek_version, masked_hint, updated_by, updated_at
FROM tenant_secrets WHERE organization_id = $1::uuid"""

_UPSERT_EXECUTION_ASSIGNMENT_SQL: str = """INSERT INTO execution_assignments (id, batch_id, organization_id,
    assigned_email, assigned_user_id, invited_role, workflow_id, output_profile_id, task_brief_id,
    task_brief_snapshot, target_locale, locked_inputs, assignee_input_keys, draft_inputs, token_hash, status,
    email_delivery_status, result_visibility, hard_deadline_at, relative_duration_seconds, activated_at, submitted_at,
    execution_id, created_by)
VALUES ($1::uuid, $2::uuid, $3::uuid, $4, $5::uuid, $6, $7::uuid, $8::uuid, $9::uuid, $10::jsonb, $11, $12::jsonb,
    $13::jsonb, $14::jsonb, $15, $16, $17, $18, $19::timestamptz, $20, $21::timestamptz, $22::timestamptz, $23::uuid,
    $24::uuid)
ON CONFLICT (id) DO UPDATE SET batch_id = EXCLUDED.batch_id, organization_id = EXCLUDED.organization_id,
    assigned_email = EXCLUDED.assigned_email, assigned_user_id = EXCLUDED.assigned_user_id,
    invited_role = EXCLUDED.invited_role, workflow_id = EXCLUDED.workflow_id,
    output_profile_id = EXCLUDED.output_profile_id, task_brief_id = EXCLUDED.task_brief_id,
    task_brief_snapshot = EXCLUDED.task_brief_snapshot, target_locale = EXCLUDED.target_locale,
    locked_inputs = EXCLUDED.locked_inputs, assignee_input_keys = EXCLUDED.assignee_input_keys,
    draft_inputs = EXCLUDED.draft_inputs, token_hash = EXCLUDED.token_hash, status = EXCLUDED.status,
    email_delivery_status = EXCLUDED.email_delivery_status, result_visibility = EXCLUDED.result_visibility,
    hard_deadline_at = EXCLUDED.hard_deadline_at, relative_duration_seconds = EXCLUDED.relative_duration_seconds,
    activated_at = EXCLUDED.activated_at, submitted_at = EXCLUDED.submitted_at,
    execution_id = EXCLUDED.execution_id, created_by = EXCLUDED.created_by"""

_GET_EXECUTION_ASSIGNMENT_SQL: str = """SELECT id, batch_id, organization_id, assigned_email, assigned_user_id,
       invited_role, workflow_id, output_profile_id, task_brief_id, task_brief_snapshot, target_locale, locked_inputs,
       assignee_input_keys, draft_inputs, token_hash, status, email_delivery_status, result_visibility,
       hard_deadline_at, relative_duration_seconds, activated_at, submitted_at, execution_id, created_by, created_at
FROM execution_assignments WHERE id = $1::uuid"""

_LIST_EXECUTION_ASSIGNMENTS_SQL: str = """SELECT id, batch_id, organization_id, assigned_email, assigned_user_id,
       invited_role, workflow_id, output_profile_id, task_brief_id, task_brief_snapshot, target_locale, locked_inputs,
       assignee_input_keys, draft_inputs, token_hash, status, email_delivery_status, result_visibility,
       hard_deadline_at, relative_duration_seconds, activated_at, submitted_at, execution_id, created_by, created_at
FROM execution_assignments"""

_LIST_EXECUTION_ASSIGNMENTS_BY_ORG_SQL: str = """SELECT id, batch_id, organization_id, assigned_email,
       assigned_user_id, invited_role, workflow_id, output_profile_id, task_brief_id, task_brief_snapshot,
       target_locale, locked_inputs, assignee_input_keys, draft_inputs, token_hash, status, email_delivery_status,
       result_visibility, hard_deadline_at, relative_duration_seconds, activated_at, submitted_at, execution_id,
       created_by, created_at
FROM execution_assignments WHERE organization_id = $1::uuid"""

_UPSERT_MODEL_REGISTRY_SQL: str = """INSERT INTO model_registries (id, slug, name, default_provider, tier_definitions)
VALUES ($1::uuid, $2, $3, $4, $5::jsonb)
ON CONFLICT (id) DO UPDATE SET slug = EXCLUDED.slug, name = EXCLUDED.name,
    default_provider = EXCLUDED.default_provider, tier_definitions = EXCLUDED.tier_definitions"""

_GET_MODEL_REGISTRY_SQL: str = """SELECT id, slug, name, default_provider, tier_definitions
FROM model_registries WHERE id = $1::uuid"""

_LIST_MODEL_REGISTRIES_SQL: str = """SELECT id, slug, name, default_provider, tier_definitions FROM model_registries"""

_UPSERT_MCP_GATEWAY_SQL: str = """INSERT INTO mcp_gateways (id, organization_id, slug, name, endpoint_url,
    transport_type, auth_type, auth_env_var, auth_header_name, timeout_seconds, tools)
VALUES ($1::uuid, $2::uuid, $3, $4, $5, $6, $7, $8, $9, $10, $11::jsonb)
ON CONFLICT (id) DO UPDATE SET organization_id = EXCLUDED.organization_id, slug = EXCLUDED.slug,
    name = EXCLUDED.name, endpoint_url = EXCLUDED.endpoint_url, transport_type = EXCLUDED.transport_type,
    auth_type = EXCLUDED.auth_type, auth_env_var = EXCLUDED.auth_env_var,
    auth_header_name = EXCLUDED.auth_header_name, timeout_seconds = EXCLUDED.timeout_seconds,
    tools = EXCLUDED.tools"""

_GET_MCP_GATEWAY_SQL: str = """SELECT id, organization_id, slug, name, endpoint_url, transport_type,
       auth_type, auth_env_var, auth_header_name, timeout_seconds, tools
FROM mcp_gateways WHERE id = $1::uuid"""

_LIST_MCP_GATEWAYS_SQL: str = """SELECT id, organization_id, slug, name, endpoint_url, transport_type,
       auth_type, auth_env_var, auth_header_name, timeout_seconds, tools FROM mcp_gateways"""

_DELETE_TENANT_SECRET_SQL: str = "DELETE FROM tenant_secrets WHERE id = $1::uuid"

_INSERT_AUDIT_LOG_SQL: str = """INSERT INTO audit_logs (id, organization_id, actor_id, execution_id,
    event_type, resource_type, resource_id, details)
VALUES ($1::uuid, $2::uuid, $3::uuid, $4::uuid, $5, $6, $7, $8::jsonb)"""

_AUDIT_LOG_COLS: str = """id, organization_id, actor_id, execution_id, event_type, resource_type,
       resource_id, details, created_at"""

_LIST_AUDIT_LOGS_SQL: str = f"SELECT {_AUDIT_LOG_COLS} FROM audit_logs"

_INSERT_USAGE_RECORD_SQL: str = """INSERT INTO usage_records (id, organization_id, user_id, execution_id,
    model_name, prompt_tokens, completion_tokens, cached_tokens, reasoning_tokens,
    cache_creation_input_tokens, latency_ms, finish_reason, system_fingerprint, cost_usd, estimated_savings_usd)
VALUES ($1::uuid, $2::uuid, $3::uuid, $4::uuid, $5, $6::bigint, $7::bigint, $8::bigint, $9::bigint,
    $10::bigint, $11, $12, $13, $14::numeric, $15::numeric)"""

_USAGE_RECORD_COLS: str = """id, organization_id, user_id, execution_id, model_name, prompt_tokens,
       completion_tokens, cached_tokens, reasoning_tokens, cache_creation_input_tokens, latency_ms,
       finish_reason, system_fingerprint, cost_usd, estimated_savings_usd, created_at"""

_LIST_USAGE_RECORDS_SQL: str = f"SELECT {_USAGE_RECORD_COLS} FROM usage_records"

_AGGREGATE_USAGE_BASE_SQL: str = """SELECT
    COALESCE(SUM(prompt_tokens), 0)::bigint AS total_prompt_tokens,
    COALESCE(SUM(completion_tokens), 0)::bigint AS total_completion_tokens,
    COALESCE(SUM(cached_tokens), 0)::bigint AS total_cached_tokens,
    COALESCE(SUM(reasoning_tokens), 0)::bigint AS total_reasoning_tokens,
    COALESCE(SUM(cache_creation_input_tokens), 0)::bigint AS total_cache_creation_input_tokens,
    COALESCE(SUM(cost_usd), 0)::numeric AS total_cost_usd,
    COALESCE(SUM(estimated_savings_usd), 0)::numeric AS total_estimated_savings_usd,
    COUNT(*)::bigint AS record_count
FROM usage_records"""


async def _fetch_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float | None,
    sql: str,
    entity_uuid: object,
    entity_id: str,
    *,
    table_name: str = "iam_entities",
) -> AsyncPgRecordProtocol | None:
    """Execute fetchrow with timeout and translate driver errors to AppException.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds, or None to resolve from settings.
        sql: Parameterized SELECT SQL statement.
        entity_uuid: Parsed 16-byte UUID primary key parameter.
        entity_id: Canonical Opaque Stripe ID of the target entity for error reporting.
        table_name: Canonical PostgreSQL table name for structured diagnostics.

    Returns:
        Database record if found, or None.

    Raises:
        AppException: With STORAGE_ACCESS_FAILED if the database query fails.
    """
    effective_timeout = resolve_effective_timeout(timeout)
    try:
        return await conn.fetchrow(sql, entity_uuid, timeout=effective_timeout)
    except AppException:
        raise
    except Exception as exc:
        raise translate_postgres_exception(
            exc,
            operation="SELECT",
            table_name=table_name,
            entity_id=entity_id,
        ) from exc


async def _fetch_list_rows(
    conn: AsyncPgConnectionProtocol,
    timeout: float | None,
    sql: str,
    *args: object,
    table_label: str,
) -> Sequence[AsyncPgRecordProtocol]:
    """Execute fetch with timeout and translate driver errors to AppException.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds, or None to resolve from settings.
        sql: Parameterized SELECT SQL statement.
        *args: Positional bind arguments.
        table_label: Table name for error reporting.

    Returns:
        Sequence of database records.

    Raises:
        AppException: With STORAGE_ACCESS_FAILED if the database query fails.
    """
    effective_timeout = resolve_effective_timeout(timeout)
    try:
        return await conn.fetch(sql, *args, timeout=effective_timeout)
    except AppException:
        raise
    except Exception as exc:
        raise translate_postgres_exception(
            exc,
            operation="SELECT",
            table_name=table_label,
            entity_id="*",
        ) from exc


def hydrate_organization_row(row: AsyncPgRecordProtocol) -> Organization:
    """Hydrate an Organization from a database row.

    Args:
        row: Database record from the organizations table.

    Returns:
        Validated Organization domain model.

    Raises:
        AppException: With VALIDATION_FAILED if the organization UUID or row schema is invalid.
    """
    org_id = str(_format_org_uuid7(row["id"]))
    return validate_hydrated_row(
        Organization,
        {
            "id": org_id,
            "slug": row["slug"],
            "name": row["name"],
            "created_at": row["created_at"],
            "is_active": row["is_active"],
            "tier": row["tier"],
            "contact_email": row["contact_email"],
            "billing_id": row["billing_id"],
            "subscription_status": row["subscription_status"],
            "quota_limit": _coerce_float(row["quota_limit"]),
            "tpm_limit": int(str(row["tpm_limit"])),
            "rpm_limit": int(str(row["rpm_limit"])),
            "allowed_email_domains": _decode_jsonb_column(row["allowed_email_domains"]),
        },
        table_name="organizations",
        entity_id=org_id,
    )


async def upsert_organization_row(conn: AsyncPgConnectionProtocol, timeout: float, org: Organization) -> str:
    """Persist an Organization into the organizations table.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        org: Validated Organization domain model.

    Returns:
        Canonical org_<hex> organization identifier.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
    """
    return await execute_entity_upsert(
        conn,
        timeout,
        _UPSERT_ORGANIZATION_SQL,
        _parse_org_uuid7(org.id),
        org.slug,
        org.name,
        org.is_active,
        org.tier,
        org.contact_email,
        org.billing_id,
        org.subscription_status.value,
        org.quota_limit,
        org.tpm_limit,
        org.rpm_limit,
        to_json(org.allowed_email_domains).decode("utf-8"),
        entity_id=org.id,
        entity_label="organization",
    )


async def get_organization_row(conn: AsyncPgConnectionProtocol, timeout: float, org_id: str) -> Organization | None:
    """Fetch an Organization by ID.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        org_id: Canonical org_<hex> organization identifier.

    Returns:
        Hydrated Organization instance if found, or None.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED on query error.
    """
    row = await _fetch_row(conn, timeout, _GET_ORGANIZATION_SQL, _parse_org_uuid7(org_id), org_id)
    if row is None:
        return None
    return hydrate_organization_row(row)


async def list_organization_rows(conn: AsyncPgConnectionProtocol, timeout: float) -> list[Organization]:
    """List all Organizations from the organizations table.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.

    Returns:
        List of hydrated Organization models.

    Raises:
        AppException: With STORAGE_ACCESS_FAILED on query error.
    """
    rows = await _fetch_list_rows(conn, timeout, _LIST_ORGANIZATIONS_SQL, table_label="organizations")
    return [hydrate_organization_row(r) for r in rows]


def hydrate_user_row(row: AsyncPgRecordProtocol) -> User:
    """Hydrate a User from a database row.

    Args:
        row: Database record from the users table.

    Returns:
        Validated User domain model.

    Raises:
        AppException: With VALIDATION_FAILED if the user UUID or row schema is invalid.
    """
    user_id = format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.USER)
    return validate_hydrated_row(
        User,
        {
            "id": user_id,
            "slug": row["slug"],
            "firebase_uid": row["firebase_uid"],
            "email": row["email"],
            "name": row["name"],
            "role": row["role"],
            "organization_id": _format_org_uuid7(row["organization_id"]),
            "is_active": row["is_active"],
            "language": row["language"],
            "theme_mode": row["theme_mode"],
            "created_at": row["created_at"],
            "created_by": _format_optional_uuid7(row["created_by"], EntityPrefix.USER),
            "deleted_at": row["deleted_at"],
        },
        table_name="users",
        entity_id=user_id,
    )


async def upsert_user_row(conn: AsyncPgConnectionProtocol, timeout: float, user: User) -> str:
    """Persist a User into the users table.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        user: Validated User domain model.

    Returns:
        Canonical usr_<hex> user identifier.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
    """
    return await execute_entity_upsert(
        conn,
        timeout,
        _UPSERT_USER_SQL,
        parse_prefixed_uuid7(user.id, EntityPrefix.USER),
        user.slug,
        user.firebase_uid,
        str(user.email),
        user.name,
        user.role.value,
        _parse_org_uuid7(user.organization_id),
        user.is_active,
        str(user.language),
        user.theme_mode,
        _parse_optional_uuid7(user.created_by, EntityPrefix.USER),
        user.deleted_at,
        entity_id=user.id,
        entity_label="user",
    )


async def get_user_row(conn: AsyncPgConnectionProtocol, timeout: float, user_id: str) -> User | None:
    """Fetch a User by ID.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        user_id: Canonical usr_<hex> user identifier.

    Returns:
        Hydrated User instance if found, or None.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED on query error.
    """
    user_uuid = parse_prefixed_uuid7(user_id, EntityPrefix.USER)
    row = await _fetch_row(conn, timeout, _GET_USER_SQL, user_uuid, user_id)
    if row is None:
        return None
    return hydrate_user_row(row)


async def list_user_rows(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    organization_id: str | None = None,
) -> list[User]:
    """List Users optionally filtered by parameterized organization_id.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        organization_id: Optional canonical org_<hex> organization filter.

    Returns:
        List of hydrated User models.

    Raises:
        AppException: With VALIDATION_FAILED on invalid org_id or STORAGE_ACCESS_FAILED on query error.
    """
    if organization_id is not None:
        org_uuid = parse_prefixed_uuid7(organization_id, EntityPrefix.ORGANIZATION)
        rows = await _fetch_list_rows(conn, timeout, _LIST_USERS_BY_ORG_SQL, org_uuid, table_label="users")
    else:
        rows = await _fetch_list_rows(conn, timeout, _LIST_USERS_SQL, table_label="users")
    return [hydrate_user_row(r) for r in rows]


def hydrate_invitation_row(row: AsyncPgRecordProtocol) -> Invitation:
    """Hydrate an Invitation from a database row.

    Args:
        row: Database record from the invitations table.

    Returns:
        Validated Invitation domain model.

    Raises:
        AppException: With VALIDATION_FAILED if UUID columns or row schema are invalid.
    """
    inv_id = format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.INVITATION)
    return validate_hydrated_row(
        Invitation,
        {
            "id": inv_id,
            "organization_id": format_prefixed_uuid7(
                _coerce_uuid_or_str(row["organization_id"]), EntityPrefix.ORGANIZATION
            ),
            "email": row["email"],
            "role": row["role"],
            "token_hash": row["token_hash"],
            "status": row["status"],
            "email_delivery_status": row["email_delivery_status"],
            "invited_by": format_prefixed_uuid7(_coerce_uuid_or_str(row["invited_by"]), EntityPrefix.USER),
            "expires_at": row["expires_at"],
            "created_at": row["created_at"],
        },
        table_name="invitations",
        entity_id=inv_id,
    )


async def upsert_invitation_row(conn: AsyncPgConnectionProtocol, timeout: float, invitation: Invitation) -> str:
    """Persist an Invitation into the invitations table.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        invitation: Validated Invitation domain model.

    Returns:
        Canonical inv_<hex> invitation identifier.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
    """
    return await execute_entity_upsert(
        conn,
        timeout,
        _UPSERT_INVITATION_SQL,
        parse_prefixed_uuid7(invitation.id, EntityPrefix.INVITATION),
        parse_prefixed_uuid7(invitation.organization_id, EntityPrefix.ORGANIZATION),
        str(invitation.email),
        invitation.role.value,
        invitation.token_hash,
        invitation.status.value,
        invitation.email_delivery_status.value,
        parse_prefixed_uuid7(invitation.invited_by, EntityPrefix.USER),
        invitation.expires_at,
        entity_id=invitation.id,
        entity_label="invitation",
    )


async def get_invitation_row(conn: AsyncPgConnectionProtocol, timeout: float, invitation_id: str) -> Invitation | None:
    """Fetch an Invitation by ID.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        invitation_id: Canonical inv_<hex> invitation identifier.

    Returns:
        Hydrated Invitation instance if found, or None.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED on query error.
    """
    inv_uuid = parse_prefixed_uuid7(invitation_id, EntityPrefix.INVITATION)
    row = await _fetch_row(conn, timeout, _GET_INVITATION_SQL, inv_uuid, invitation_id)
    if row is None:
        return None
    return hydrate_invitation_row(row)


async def list_invitation_rows(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    organization_id: str | None = None,
) -> list[Invitation]:
    """List Invitations optionally filtered by parameterized organization_id.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        organization_id: Optional canonical org_<hex> organization filter.

    Returns:
        List of hydrated Invitation models.

    Raises:
        AppException: With VALIDATION_FAILED on invalid org_id or STORAGE_ACCESS_FAILED on query error.
    """
    if organization_id is not None:
        org_uuid = parse_prefixed_uuid7(organization_id, EntityPrefix.ORGANIZATION)
        rows = await _fetch_list_rows(conn, timeout, _LIST_INVITATIONS_BY_ORG_SQL, org_uuid, table_label="invitations")
    else:
        rows = await _fetch_list_rows(conn, timeout, _LIST_INVITATIONS_SQL, table_label="invitations")
    return [hydrate_invitation_row(r) for r in rows]


def _coerce_optional_bytes(val: object) -> bytes | None:
    """Narrow a nullable database bytea column value to bytes or None.

    Args:
        val: Raw column value from AsyncPgRecordProtocol.

    Returns:
        Coerced bytes value or None.
    """
    if val is None:
        return None
    if isinstance(val, (bytes, bytearray, memoryview)):
        return bytes(val)
    return str(val).encode("utf-8")


def hydrate_tenant_secret_row(row: AsyncPgRecordProtocol) -> TenantSecretDTO:
    """Hydrate a TenantSecretDTO from a database row.

    Args:
        row: Database record from the tenant_secrets table.

    Returns:
        Validated TenantSecretDTO model.

    Raises:
        AppException: With VALIDATION_FAILED if UUID columns or row schema are invalid.
    """
    sec_id = format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.TENANT_SECRET)
    return validate_hydrated_row(
        TenantSecretDTO,
        {
            "id": sec_id,
            "organization_id": format_prefixed_uuid7(
                _coerce_uuid_or_str(row["organization_id"]), EntityPrefix.ORGANIZATION
            ),
            "scope": row["scope"],
            "target_identifier": row["target_identifier"],
            "storage_mode": row["storage_mode"],
            "secret_manager_version_uri": row["secret_manager_version_uri"],
            "encrypted_dek": _coerce_optional_bytes(row["encrypted_dek"]),
            "ciphertext": _coerce_optional_bytes(row["ciphertext"]),
            "nonce": _coerce_optional_bytes(row["nonce"]),
            "kek_version": row["kek_version"],
            "masked_hint": row["masked_hint"],
            "updated_by": format_prefixed_uuid7(_coerce_uuid_or_str(row["updated_by"]), EntityPrefix.USER),
            "updated_at": row["updated_at"],
        },
        table_name="tenant_secrets",
        entity_id=sec_id,
    )


async def upsert_tenant_secret_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    secret: TenantSecretDTO,
) -> str:
    """Persist a TenantSecretDTO into the tenant_secrets table.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        secret: Validated TenantSecretDTO model.

    Returns:
        Canonical sec_<hex> tenant secret identifier.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
    """
    mcp_gateway_uuid: UUID | None = None
    if secret.scope == SecretScope.MCP_GATEWAY:
        mcp_gateway_uuid = parse_prefixed_uuid7(secret.target_identifier, EntityPrefix.MCP_GATEWAY)
    return await execute_entity_upsert(
        conn,
        timeout,
        _UPSERT_TENANT_SECRET_SQL,
        parse_prefixed_uuid7(secret.id, EntityPrefix.TENANT_SECRET),
        parse_prefixed_uuid7(secret.organization_id, EntityPrefix.ORGANIZATION),
        mcp_gateway_uuid,
        secret.scope.value,
        secret.target_identifier,
        secret.storage_mode.value,
        secret.secret_manager_version_uri,
        secret.encrypted_dek,
        secret.ciphertext,
        secret.nonce,
        secret.kek_version,
        secret.masked_hint,
        parse_prefixed_uuid7(secret.updated_by, EntityPrefix.USER),
        secret.updated_at,
        entity_id=secret.id,
        entity_label="tenant_secret",
    )


async def get_tenant_secret_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    secret_id: str,
) -> TenantSecretDTO | None:
    """Fetch a TenantSecretDTO by ID.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        secret_id: Canonical sec_<hex> tenant secret identifier.

    Returns:
        Hydrated TenantSecretDTO instance if found, or None.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED on query error.
    """
    sec_uuid = parse_prefixed_uuid7(secret_id, EntityPrefix.TENANT_SECRET)
    row = await _fetch_row(conn, timeout, _GET_TENANT_SECRET_SQL, sec_uuid, secret_id)
    if row is None:
        return None
    return hydrate_tenant_secret_row(row)


async def list_tenant_secret_rows(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    organization_id: str | None = None,
) -> list[TenantSecretDTO]:
    """List TenantSecretDTO rows optionally filtered by parameterized organization_id.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        organization_id: Optional canonical org_<hex> organization filter.

    Returns:
        List of hydrated TenantSecretDTO models.

    Raises:
        AppException: With VALIDATION_FAILED on invalid org_id or STORAGE_ACCESS_FAILED on query error.
    """
    if organization_id is not None:
        org_uuid = parse_prefixed_uuid7(organization_id, EntityPrefix.ORGANIZATION)
        rows = await _fetch_list_rows(
            conn, timeout, _LIST_TENANT_SECRETS_BY_ORG_SQL, org_uuid, table_label="tenant_secrets"
        )
    else:
        rows = await _fetch_list_rows(conn, timeout, _LIST_TENANT_SECRETS_SQL, table_label="tenant_secrets")
    return [hydrate_tenant_secret_row(r) for r in rows]


def hydrate_execution_assignment_row(row: AsyncPgRecordProtocol) -> ExecutionAssignment:
    """Hydrate an ExecutionAssignment from a database row.

    Args:
        row: Database record from the execution_assignments table.

    Returns:
        Validated ExecutionAssignment domain model.

    Raises:
        AppException: With VALIDATION_FAILED if UUID columns or row schema are invalid.
    """
    asg_id = format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.ASSIGNMENT)
    return validate_hydrated_row(
        ExecutionAssignment,
        {
            "id": asg_id,
            "batch_id": _format_optional_uuid7(row["batch_id"], EntityPrefix.ASSIGNMENT),
            "organization_id": format_prefixed_uuid7(
                _coerce_uuid_or_str(row["organization_id"]), EntityPrefix.ORGANIZATION
            ),
            "assigned_email": row["assigned_email"],
            "assigned_user_id": _format_optional_uuid7(row["assigned_user_id"], EntityPrefix.USER),
            "invited_role": row["invited_role"],
            "workflow_id": format_prefixed_uuid7(_coerce_uuid_or_str(row["workflow_id"]), EntityPrefix.WORKFLOW),
            "output_profile_id": _format_optional_uuid7(row["output_profile_id"], EntityPrefix.OUTPUT_PROFILE),
            "task_brief_id": _format_optional_uuid7(row["task_brief_id"], EntityPrefix.TASK_BRIEF),
            "task_brief_snapshot": _decode_jsonb_column(row["task_brief_snapshot"]),
            "target_locale": row["target_locale"],
            "locked_inputs": _decode_jsonb_column(row["locked_inputs"]),
            "assignee_input_keys": _decode_jsonb_column(row["assignee_input_keys"]),
            "draft_inputs": _decode_jsonb_column(row["draft_inputs"]),
            "token_hash": row["token_hash"],
            "status": row["status"],
            "email_delivery_status": row["email_delivery_status"],
            "result_visibility": row["result_visibility"],
            "hard_deadline_at": row["hard_deadline_at"],
            "relative_duration_seconds": row["relative_duration_seconds"],
            "activated_at": row["activated_at"],
            "submitted_at": row["submitted_at"],
            "execution_id": _format_optional_uuid7(row["execution_id"], EntityPrefix.EXECUTION),
            "created_by": format_prefixed_uuid7(_coerce_uuid_or_str(row["created_by"]), EntityPrefix.USER),
            "created_at": row["created_at"],
        },
        table_name="execution_assignments",
        entity_id=asg_id,
    )


async def upsert_execution_assignment_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    assignment: ExecutionAssignment,
) -> str:
    """Persist an ExecutionAssignment into the execution_assignments table.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        assignment: Validated ExecutionAssignment domain model.

    Returns:
        Canonical tsk_<hex> assignment identifier.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
    """
    return await execute_entity_upsert(
        conn,
        timeout,
        _UPSERT_EXECUTION_ASSIGNMENT_SQL,
        parse_prefixed_uuid7(assignment.id, EntityPrefix.ASSIGNMENT),
        _parse_optional_uuid7(assignment.batch_id, EntityPrefix.ASSIGNMENT),
        parse_prefixed_uuid7(assignment.organization_id, EntityPrefix.ORGANIZATION),
        str(assignment.assigned_email),
        _parse_optional_uuid7(assignment.assigned_user_id, EntityPrefix.USER),
        assignment.invited_role.value,
        parse_prefixed_uuid7(assignment.workflow_id, EntityPrefix.WORKFLOW),
        _parse_optional_uuid7(assignment.output_profile_id, EntityPrefix.OUTPUT_PROFILE),
        _parse_optional_uuid7(assignment.task_brief_id, EntityPrefix.TASK_BRIEF),
        _encode_optional_jsonb(assignment.task_brief_snapshot),
        str(assignment.target_locale),
        to_json(assignment.locked_inputs.model_dump(mode="json")).decode("utf-8"),
        to_json(assignment.assignee_input_keys).decode("utf-8"),
        to_json(assignment.draft_inputs.model_dump(mode="json")).decode("utf-8"),
        assignment.token_hash,
        assignment.status.value,
        assignment.email_delivery_status.value,
        assignment.result_visibility.value,
        assignment.hard_deadline_at,
        assignment.relative_duration_seconds,
        assignment.activated_at,
        assignment.submitted_at,
        _parse_optional_uuid7(assignment.execution_id, EntityPrefix.EXECUTION),
        parse_prefixed_uuid7(assignment.created_by, EntityPrefix.USER),
        entity_id=assignment.id,
        entity_label="execution_assignment",
    )


async def get_execution_assignment_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    assignment_id: str,
) -> ExecutionAssignment | None:
    """Fetch an ExecutionAssignment by ID.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        assignment_id: Canonical tsk_<hex> assignment identifier.

    Returns:
        Hydrated ExecutionAssignment instance if found, or None.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED on query error.
    """
    tsk_uuid = parse_prefixed_uuid7(assignment_id, EntityPrefix.ASSIGNMENT)
    row = await _fetch_row(conn, timeout, _GET_EXECUTION_ASSIGNMENT_SQL, tsk_uuid, assignment_id)
    if row is None:
        return None
    return hydrate_execution_assignment_row(row)


async def list_execution_assignment_rows(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    organization_id: str | None = None,
) -> list[ExecutionAssignment]:
    """List ExecutionAssignments optionally filtered by parameterized organization_id.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        organization_id: Optional canonical org_<hex> organization filter.

    Returns:
        List of hydrated ExecutionAssignment models.

    Raises:
        AppException: With VALIDATION_FAILED on invalid org_id or STORAGE_ACCESS_FAILED on query error.
    """
    if organization_id is not None:
        org_uuid = parse_prefixed_uuid7(organization_id, EntityPrefix.ORGANIZATION)
        rows = await _fetch_list_rows(
            conn,
            timeout,
            _LIST_EXECUTION_ASSIGNMENTS_BY_ORG_SQL,
            org_uuid,
            table_label="execution_assignments",
        )
    else:
        rows = await _fetch_list_rows(
            conn, timeout, _LIST_EXECUTION_ASSIGNMENTS_SQL, table_label="execution_assignments"
        )
    return [hydrate_execution_assignment_row(r) for r in rows]


def hydrate_model_registry_row(row: AsyncPgRecordProtocol) -> SystemConfigModelRegistry:
    """Hydrate a SystemConfigModelRegistry from a model_registries database row.

    Args:
        row: Database record from the model_registries table.

    Returns:
        Validated SystemConfigModelRegistry instance.

    Raises:
        AppException: With VALIDATION_FAILED if the model_registry UUID or row validation fails.
    """
    reg_id = format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.MODEL_REGISTRY)
    return validate_hydrated_row(
        SystemConfigModelRegistry,
        {
            "id": reg_id,
            "slug": row["slug"],
            "name": row["name"],
            "default_provider": row["default_provider"],
            "tier_definitions": _decode_jsonb_column(row["tier_definitions"]),
        },
        table_name="model_registries",
        entity_id=reg_id,
    )


async def upsert_model_registry_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    registry: SystemConfigModelRegistry,
) -> str:
    """Persist a SystemConfigModelRegistry into model_registries.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        registry: Validated SystemConfigModelRegistry domain model.

    Returns:
        Canonical mrg_<hex> model registry identifier.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
    """
    reg_uuid = parse_prefixed_uuid7(registry.id, EntityPrefix.MODEL_REGISTRY)
    dumped = registry.model_dump(mode="json")
    return await execute_entity_upsert(
        conn,
        timeout,
        _UPSERT_MODEL_REGISTRY_SQL,
        reg_uuid,
        registry.slug,
        registry.name,
        str(registry.default_provider),
        to_json(dumped["tier_definitions"]).decode("utf-8"),
        entity_id=registry.id,
        entity_label="model_registry",
    )


async def get_model_registry_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    registry_id: str,
) -> SystemConfigModelRegistry | None:
    """Fetch a SystemConfigModelRegistry by ID from model_registries.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        registry_id: Canonical mrg_<hex> model registry identifier.

    Returns:
        Hydrated SystemConfigModelRegistry if found, or None.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED on query error.
    """
    reg_uuid = parse_prefixed_uuid7(registry_id, EntityPrefix.MODEL_REGISTRY)
    row = await _fetch_row(conn, timeout, _GET_MODEL_REGISTRY_SQL, reg_uuid, registry_id, table_name="model_registries")
    if row is None:
        return None
    return hydrate_model_registry_row(row)


async def list_model_registry_rows(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
) -> list[SystemConfigModelRegistry]:
    """List all SystemConfigModelRegistry rows from model_registries.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.

    Returns:
        List of hydrated SystemConfigModelRegistry domain models.

    Raises:
        AppException: With VALIDATION_FAILED on corrupt row or STORAGE_ACCESS_FAILED on query error.
    """
    rows = await _fetch_list_rows(conn, timeout, _LIST_MODEL_REGISTRIES_SQL, table_label="model_registries")
    return [hydrate_model_registry_row(r) for r in rows]


def hydrate_mcp_gateway_row(row: AsyncPgRecordProtocol) -> SystemConfigMCPGateways:
    """Hydrate a SystemConfigMCPGateways from an mcp_gateways database row.

    Args:
        row: Database record from the mcp_gateways table.

    Returns:
        Validated SystemConfigMCPGateways instance.

    Raises:
        AppException: With VALIDATION_FAILED if the mcp_gateway UUID or row validation fails.
    """
    gw_id = format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.MCP_GATEWAY)
    org_id = format_prefixed_uuid7(_coerce_uuid_or_str(row["organization_id"]), EntityPrefix.ORGANIZATION)
    return validate_hydrated_row(
        SystemConfigMCPGateways,
        {
            "id": gw_id,
            "organization_id": org_id,
            "slug": row["slug"],
            "name": row["name"],
            "endpoint_url": row["endpoint_url"],
            "transport_type": row["transport_type"],
            "auth_type": row["auth_type"],
            "auth_env_var": row["auth_env_var"],
            "auth_header_name": row["auth_header_name"],
            "timeout_seconds": row["timeout_seconds"],
            "tools": _decode_jsonb_column(row["tools"]),
        },
        table_name="mcp_gateways",
        entity_id=gw_id,
    )


async def upsert_mcp_gateway_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    gateway: SystemConfigMCPGateways,
) -> str:
    """Persist a SystemConfigMCPGateways into mcp_gateways.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        gateway: Validated SystemConfigMCPGateways domain model.

    Returns:
        Canonical mcp_<hex> MCP gateway identifier.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
    """
    gw_uuid = parse_prefixed_uuid7(gateway.id, EntityPrefix.MCP_GATEWAY)
    org_uuid = parse_prefixed_uuid7(gateway.organization_id, EntityPrefix.ORGANIZATION)
    dumped = gateway.model_dump(mode="json")
    return await execute_entity_upsert(
        conn,
        timeout,
        _UPSERT_MCP_GATEWAY_SQL,
        gw_uuid,
        org_uuid,
        gateway.slug,
        gateway.name,
        gateway.endpoint_url,
        str(gateway.transport_type),
        str(gateway.auth_type),
        gateway.auth_env_var,
        gateway.auth_header_name,
        gateway.timeout_seconds,
        to_json(dumped["tools"]).decode("utf-8"),
        entity_id=gateway.id,
        entity_label="mcp_gateway",
    )


async def get_mcp_gateway_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    gateway_id: str,
) -> SystemConfigMCPGateways | None:
    """Fetch a SystemConfigMCPGateways by ID from mcp_gateways.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        gateway_id: Canonical mcp_<hex> MCP gateway identifier.

    Returns:
        Hydrated SystemConfigMCPGateways if found, or None.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED on query error.
    """
    gw_uuid = parse_prefixed_uuid7(gateway_id, EntityPrefix.MCP_GATEWAY)
    row = await _fetch_row(conn, timeout, _GET_MCP_GATEWAY_SQL, gw_uuid, gateway_id, table_name="mcp_gateways")
    if row is None:
        return None
    return hydrate_mcp_gateway_row(row)


async def list_mcp_gateway_rows(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
) -> list[SystemConfigMCPGateways]:
    """List all SystemConfigMCPGateways rows from mcp_gateways.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.

    Returns:
        List of hydrated SystemConfigMCPGateways domain models.

    Raises:
        AppException: With VALIDATION_FAILED on corrupt row or STORAGE_ACCESS_FAILED on query error.
    """
    rows = await _fetch_list_rows(conn, timeout, _LIST_MCP_GATEWAYS_SQL, table_label="mcp_gateways")
    return [hydrate_mcp_gateway_row(r) for r in rows]


async def delete_tenant_secret_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    secret_id: str,
) -> bool:
    """Delete a TenantSecretDTO row by primary key from tenant_secrets.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        secret_id: Canonical sec_<hex32> secret identifier.

    Returns:
        True if a matching row was deleted, False otherwise.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
    """
    sec_uuid = parse_prefixed_uuid7(secret_id, EntityPrefix.TENANT_SECRET)
    return await execute_entity_delete(
        conn,
        timeout,
        _DELETE_TENANT_SECRET_SQL,
        sec_uuid,
        entity_id=secret_id,
        table="tenant_secrets",
    )


def hydrate_audit_log_row(row: AsyncPgRecordProtocol) -> AuditLogRecord:
    """Hydrate an AuditLogRecord from a database row in audit_logs.

    Args:
        row: Database record from the audit_logs table.

    Returns:
        Validated immutable AuditLogRecord domain model.

    Raises:
        AppException: With VALIDATION_FAILED if UUID columns or row schema are invalid.
    """
    aud_id = format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.AUDIT_LOG)
    return validate_hydrated_row(
        AuditLogRecord,
        {
            "id": aud_id,
            "organization_id": _format_org_uuid7(row["organization_id"]),
            "actor_id": _format_optional_uuid7(row["actor_id"], EntityPrefix.USER),
            "execution_id": _format_optional_uuid7(row["execution_id"], EntityPrefix.EXECUTION),
            "event_type": row["event_type"],
            "resource_type": row["resource_type"],
            "resource_id": row["resource_id"],
            "details": _decode_jsonb_column(row["details"]),
            "created_at": row["created_at"],
        },
        table_name="audit_logs",
        entity_id=aud_id,
    )


async def insert_audit_log_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    record: AuditLogRecord,
) -> str:
    """Insert an immutable AuditLogRecord into the append-only audit_logs table.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        record: Validated AuditLogRecord domain model.

    Returns:
        Canonical aud_<hex32> identifier inserted.

    Raises:
        AppException: With VALIDATION_FAILED, CONFLICT, or STORAGE_ACCESS_FAILED if insertion fails.
    """
    aud_uuid = parse_prefixed_uuid7(record.id, EntityPrefix.AUDIT_LOG)
    org_uuid = _parse_system_safe_org_uuid7(record.organization_id)
    actor_uuid = _parse_system_safe_user_uuid7(record.actor_id)
    exec_uuid = _parse_optional_uuid7(record.execution_id, EntityPrefix.EXECUTION)
    details_json = to_json(record.details).decode("utf-8")
    effective_timeout = resolve_effective_timeout(timeout)
    try:
        await conn.execute(
            _INSERT_AUDIT_LOG_SQL,
            aud_uuid,
            org_uuid,
            actor_uuid,
            exec_uuid,
            record.event_type,
            record.resource_type,
            record.resource_id,
            details_json,
            timeout=effective_timeout,
        )
    except AppException:
        raise
    except Exception as exc:
        raise translate_postgres_exception(
            exc,
            operation="INSERT",
            table_name="audit_logs",
            entity_id=record.id,
        ) from exc
    return record.id


async def list_audit_log_rows(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    *,
    organization_id: str | None = None,
    actor_id: str | None = None,
    event_type: str | None = None,
    limit: int = 100,
) -> list[AuditLogRecord]:
    """List AuditLogRecord entries ordered by id DESC with optional parameterized filters.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        organization_id: Optional organization filter ('org_<hex32>' or 'SYSTEM').
        actor_id: Optional actor filter ('usr_<hex32>' or 'system').
        event_type: Optional event_type string filter.
        limit: Maximum number of records to return.

    Returns:
        List of hydrated AuditLogRecord models ordered newest-first.

    Raises:
        AppException: With VALIDATION_FAILED on invalid filter ID or STORAGE_ACCESS_FAILED on query error.
    """
    if limit <= 0:
        return []
    conditions: list[str] = []
    params: list[object] = []
    if organization_id is not None:
        org_uuid = _parse_system_safe_org_uuid7(organization_id)
        if org_uuid is not None:
            params.append(org_uuid)
            conditions.append(f"organization_id = ${len(params)}::uuid")
        else:
            conditions.append("organization_id IS NULL")
    if actor_id is not None:
        actor_uuid = _parse_system_safe_user_uuid7(actor_id)
        if actor_uuid is not None:
            params.append(actor_uuid)
            conditions.append(f"actor_id = ${len(params)}::uuid")
        else:
            conditions.append("actor_id IS NULL")
    if event_type is not None:
        params.append(event_type)
        conditions.append(f"event_type = ${len(params)}")
    where_clause = ""
    if conditions:
        where_clause = f" WHERE {' AND '.join(conditions)}"
    params.append(limit)
    sql = f"{_LIST_AUDIT_LOGS_SQL}{where_clause} ORDER BY id DESC LIMIT ${len(params)}"
    rows = await _fetch_list_rows(conn, timeout, sql, *params, table_label="audit_logs")
    return [hydrate_audit_log_row(r) for r in rows]


def hydrate_usage_record_row(row: AsyncPgRecordProtocol) -> UsageRecord:
    """Hydrate a UsageRecord from a database row in usage_records.

    Args:
        row: Database record from the usage_records table.

    Returns:
        Validated immutable UsageRecord domain model.

    Raises:
        AppException: With VALIDATION_FAILED if UUID columns or row schema are invalid.
    """
    usg_id = format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.USAGE_RECORD)
    formatted_org = _format_org_uuid7(row["organization_id"])
    resolved_org = "system"
    if formatted_org is not None:
        resolved_org = formatted_org
    formatted_usr = _format_optional_uuid7(row["user_id"], EntityPrefix.USER)
    resolved_usr = "system"
    if formatted_usr is not None:
        resolved_usr = formatted_usr
    latency_raw = row["latency_ms"]
    latency_val: int | None = None
    if latency_raw is not None:
        latency_val = int(str(latency_raw))
    return validate_hydrated_row(
        UsageRecord,
        {
            "id": usg_id,
            "org_id": resolved_org,
            "user_id": resolved_usr,
            "execution_id": _format_optional_uuid7(row["execution_id"], EntityPrefix.EXECUTION),
            "model": row["model_name"],
            "input_tokens": int(str(row["prompt_tokens"])),
            "output_tokens": int(str(row["completion_tokens"])),
            "cached_tokens": int(str(row["cached_tokens"])),
            "reasoning_tokens": int(str(row["reasoning_tokens"])),
            "cache_creation_input_tokens": int(str(row["cache_creation_input_tokens"])),
            "latency_ms": latency_val,
            "finish_reason": row["finish_reason"],
            "system_fingerprint": row["system_fingerprint"],
            "cost_usd": _coerce_float(row["cost_usd"]),
            "estimated_savings_usd": _coerce_float(row["estimated_savings_usd"]),
            "timestamp": row["created_at"],
        },
        table_name="usage_records",
        entity_id=usg_id,
    )


async def insert_usage_record_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    record: UsageRecord,
) -> str:
    """Insert an immutable UsageRecord into the append-only usage_records table.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        record: Validated UsageRecord domain model.

    Returns:
        Canonical usg_<hex32> identifier inserted.

    Raises:
        AppException: With VALIDATION_FAILED, CONFLICT, or STORAGE_ACCESS_FAILED if insertion fails.
    """
    usg_uuid = parse_prefixed_uuid7(record.id, EntityPrefix.USAGE_RECORD)
    org_uuid = _parse_system_safe_org_uuid7(record.org_id)
    usr_uuid = _parse_system_safe_user_uuid7(record.user_id)
    exec_uuid = _parse_optional_uuid7(record.execution_id, EntityPrefix.EXECUTION)
    effective_timeout = resolve_effective_timeout(timeout)
    try:
        await conn.execute(
            _INSERT_USAGE_RECORD_SQL,
            usg_uuid,
            org_uuid,
            usr_uuid,
            exec_uuid,
            record.model,
            record.input_tokens,
            record.output_tokens,
            record.cached_tokens,
            record.reasoning_tokens,
            record.cache_creation_input_tokens,
            record.latency_ms,
            record.finish_reason,
            record.system_fingerprint,
            record.cost_usd,
            record.estimated_savings_usd,
            timeout=effective_timeout,
        )
    except AppException:
        raise
    except Exception as exc:
        raise translate_postgres_exception(
            exc,
            operation="INSERT",
            table_name="usage_records",
            entity_id=record.id,
        ) from exc
    return record.id


async def list_usage_record_rows(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    *,
    organization_id: str | None = None,
    user_id: str | None = None,
    since: datetime | None = None,
) -> list[UsageRecord]:
    """List UsageRecord entries ordered chronologically by id ASC with parameterized filters.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        organization_id: Optional organization filter ('org_<hex32>' or 'system').
        user_id: Optional user filter ('usr_<hex32>' or 'system').
        since: Optional UTC timestamp lower bound.

    Returns:
        List of hydrated UsageRecord models ordered chronologically.

    Raises:
        AppException: With VALIDATION_FAILED on invalid filter ID or STORAGE_ACCESS_FAILED on query error.
    """
    conditions: list[str] = []
    params: list[object] = []
    if organization_id is not None:
        org_uuid = _parse_system_safe_org_uuid7(organization_id)
        if org_uuid is not None:
            params.append(org_uuid)
            conditions.append(f"organization_id = ${len(params)}::uuid")
        else:
            conditions.append("organization_id IS NULL")
    if user_id is not None:
        usr_uuid = _parse_system_safe_user_uuid7(user_id)
        if usr_uuid is not None:
            params.append(usr_uuid)
            conditions.append(f"user_id = ${len(params)}::uuid")
        else:
            conditions.append("user_id IS NULL")
    if since is not None:
        params.append(since)
        conditions.append(f"created_at >= ${len(params)}::timestamptz")
    where_clause = ""
    if conditions:
        where_clause = f" WHERE {' AND '.join(conditions)}"
    sql = f"{_LIST_USAGE_RECORDS_SQL}{where_clause} ORDER BY id ASC"
    rows = await _fetch_list_rows(conn, timeout, sql, *params, table_label="usage_records")
    return [hydrate_usage_record_row(r) for r in rows]


async def aggregate_organization_usage_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    *,
    organization_id: str | None = None,
    since: datetime | None = None,
) -> UsageRollupSummaryDTO:
    """Compute FinOps token and USD cost rollups via parameterized SQL SUM/COUNT over usage_records.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        organization_id: Optional organization filter ('org_<hex32>' or None for global system rollup).
        since: Optional UTC timestamp lower bound.

    Returns:
        Validated UsageRollupSummaryDTO containing aggregated token and cost metrics.

    Raises:
        AppException: With VALIDATION_FAILED on invalid organization_id or STORAGE_ACCESS_FAILED on query error.
    """
    conditions: list[str] = []
    params: list[object] = []
    if organization_id is not None:
        org_uuid = _parse_system_safe_org_uuid7(organization_id)
        if org_uuid is not None:
            params.append(org_uuid)
            conditions.append(f"organization_id = ${len(params)}::uuid")
        else:
            conditions.append("organization_id IS NULL")
    if since is not None:
        params.append(since)
        conditions.append(f"created_at >= ${len(params)}::timestamptz")
    where_clause = ""
    if conditions:
        where_clause = f" WHERE {' AND '.join(conditions)}"
    sql = f"{_AGGREGATE_USAGE_BASE_SQL}{where_clause}"
    target_label = "system"
    if organization_id is not None:
        target_label = organization_id
    effective_timeout = resolve_effective_timeout(timeout)
    try:
        row = await conn.fetchrow(sql, *params, timeout=effective_timeout)
    except AppException:
        raise
    except Exception as exc:
        raise translate_postgres_exception(
            exc,
            operation="SELECT",
            table_name="usage_records",
            entity_id=target_label,
        ) from exc
    if row is None:
        return UsageRollupSummaryDTO(organization_id=organization_id)
    return validate_hydrated_row(
        UsageRollupSummaryDTO,
        {
            "organization_id": organization_id,
            "total_prompt_tokens": int(str(row["total_prompt_tokens"])),
            "total_completion_tokens": int(str(row["total_completion_tokens"])),
            "total_cached_tokens": int(str(row["total_cached_tokens"])),
            "total_reasoning_tokens": int(str(row["total_reasoning_tokens"])),
            "total_cache_creation_input_tokens": int(str(row["total_cache_creation_input_tokens"])),
            "total_cost_usd": _coerce_float(row["total_cost_usd"]),
            "total_estimated_savings_usd": _coerce_float(row["total_estimated_savings_usd"]),
            "record_count": int(str(row["record_count"])),
        },
        table_name="usage_records",
        entity_id=target_label,
    )


_GET_USER_BY_EMAIL_SQL: str = """SELECT id, slug, firebase_uid, email, name, role, organization_id, is_active,
       language, theme_mode, created_at, created_by, deleted_at
FROM users WHERE LOWER(email) = LOWER($1) LIMIT 1"""

_DELETE_ORGANIZATION_SQL: str = "DELETE FROM organizations WHERE id = $1::uuid"
_DELETE_USER_SQL: str = "DELETE FROM users WHERE id = $1::uuid"
_DELETE_INVITATION_SQL: str = "DELETE FROM invitations WHERE id = $1::uuid"
_DELETE_MODEL_REGISTRY_SQL: str = "DELETE FROM model_registries WHERE id = $1::uuid"
_DELETE_MCP_GATEWAY_SQL: str = "DELETE FROM mcp_gateways WHERE id = $1::uuid"


async def get_user_by_email_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    email: str,
) -> User | None:
    """Fetch a User by case-insensitive email lookup from users.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        email: Target user email address.

    Returns:
        Hydrated User domain model if found, or None.

    Raises:
        AppException: With VALIDATION_FAILED on corrupt row or STORAGE_ACCESS_FAILED on query error.
    """
    normalized_email = email.strip()
    if not normalized_email:
        return None
    effective_timeout = resolve_effective_timeout(timeout)
    try:
        row = await conn.fetchrow(_GET_USER_BY_EMAIL_SQL, normalized_email, timeout=effective_timeout)
    except AppException:
        raise
    except Exception as exc:
        raise translate_postgres_exception(
            exc,
            operation="SELECT",
            table_name="users",
            entity_id=normalized_email,
        ) from exc
    if row is None:
        return None
    return hydrate_user_row(row)


async def delete_organization_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    org_id: str,
) -> bool:
    """Delete an Organization row by primary key from organizations.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        org_id: Canonical org_<hex32> organization identifier.

    Returns:
        True if a matching row was deleted, False otherwise.

    Raises:
        AppException: With VALIDATION_FAILED, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
    """
    org_uuid = parse_prefixed_uuid7(org_id, EntityPrefix.ORGANIZATION)
    return await execute_entity_delete(
        conn,
        timeout,
        _DELETE_ORGANIZATION_SQL,
        org_uuid,
        entity_id=org_id,
        table="organizations",
    )


async def delete_user_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    user_id: str,
) -> bool:
    """Delete a User row by primary key from users.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        user_id: Canonical usr_<hex32> user identifier.

    Returns:
        True if a matching row was deleted, False otherwise.

    Raises:
        AppException: With VALIDATION_FAILED, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
    """
    user_uuid = parse_prefixed_uuid7(user_id, EntityPrefix.USER)
    return await execute_entity_delete(
        conn,
        timeout,
        _DELETE_USER_SQL,
        user_uuid,
        entity_id=user_id,
        table="users",
    )


async def delete_invitation_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    invitation_id: str,
) -> bool:
    """Delete an Invitation row by primary key from invitations.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        invitation_id: Canonical inv_<hex32> invitation identifier.

    Returns:
        True if a matching row was deleted, False otherwise.

    Raises:
        AppException: With VALIDATION_FAILED, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
    """
    inv_uuid = parse_prefixed_uuid7(invitation_id, EntityPrefix.INVITATION)
    return await execute_entity_delete(
        conn,
        timeout,
        _DELETE_INVITATION_SQL,
        inv_uuid,
        entity_id=invitation_id,
        table="invitations",
    )


async def delete_model_registry_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    registry_id: str,
) -> bool:
    """Delete a SystemConfigModelRegistry row by primary key from model_registries.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        registry_id: Canonical mrg_<hex32> model registry identifier.

    Returns:
        True if a matching row was deleted, False otherwise.

    Raises:
        AppException: With VALIDATION_FAILED, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
    """
    reg_uuid = parse_prefixed_uuid7(registry_id, EntityPrefix.MODEL_REGISTRY)
    return await execute_entity_delete(
        conn,
        timeout,
        _DELETE_MODEL_REGISTRY_SQL,
        reg_uuid,
        entity_id=registry_id,
        table="model_registries",
    )


async def delete_mcp_gateway_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    gateway_id: str,
) -> bool:
    """Delete a SystemConfigMCPGateways row by primary key from mcp_gateways.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        gateway_id: Canonical mcp_<hex32> MCP gateway identifier.

    Returns:
        True if a matching row was deleted, False otherwise.

    Raises:
        AppException: With VALIDATION_FAILED, DELETE_BLOCKED_BY_USAGE, or STORAGE_ACCESS_FAILED.
    """
    gw_uuid = parse_prefixed_uuid7(gateway_id, EntityPrefix.MCP_GATEWAY)
    return await execute_entity_delete(
        conn,
        timeout,
        _DELETE_MCP_GATEWAY_SQL,
        gw_uuid,
        entity_id=gateway_id,
        table="mcp_gateways",
    )
