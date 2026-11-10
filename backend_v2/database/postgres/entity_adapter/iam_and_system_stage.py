"""PostgreSQL 19 SQL constants, hydration, upsert, and fetch stage for IAM, assignments, secrets, and system_configs."""

from __future__ import annotations

import logging
from collections.abc import Sequence

from fastapi import status
from pydantic import ValidationError
from pydantic_core import to_json

from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    _coerce_float,
    _coerce_uuid_or_str,
    _decode_jsonb_column,
    _format_optional_uuid7,
    _format_org_uuid7,
    _parse_optional_uuid7,
    _parse_org_uuid7,
    execute_entity_upsert,
    resolve_effective_timeout,
)
from backend_v2.database.postgres.pool import AsyncPgConnectionProtocol, AsyncPgRecordProtocol
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import Invitation, Organization, TenantSecretDTO, User
from backend_v2.models.core_base import format_prefixed_uuid7, parse_prefixed_uuid7
from backend_v2.models.domain.execution import ExecutionAssignment
from backend_v2.models.domain.system_config import SystemConfigMCPGateways, SystemConfigModelRegistry
from backend_v2.models.enums import EntityPrefix

logger = logging.getLogger(__name__)

__all__ = [
    "_GET_EXECUTION_ASSIGNMENT_SQL",
    "_GET_INVITATION_SQL",
    "_GET_ORGANIZATION_SQL",
    "_GET_SYSTEM_CONFIG_SQL",
    "_GET_TENANT_SECRET_SQL",
    "_GET_USER_SQL",
    "_LIST_EXECUTION_ASSIGNMENTS_BY_ORG_SQL",
    "_LIST_EXECUTION_ASSIGNMENTS_SQL",
    "_LIST_INVITATIONS_BY_ORG_SQL",
    "_LIST_INVITATIONS_SQL",
    "_LIST_ORGANIZATIONS_SQL",
    "_LIST_SYSTEM_CONFIGS_SQL",
    "_LIST_TENANT_SECRETS_BY_ORG_SQL",
    "_LIST_TENANT_SECRETS_SQL",
    "_LIST_USERS_BY_ORG_SQL",
    "_LIST_USERS_SQL",
    "_UPSERT_EXECUTION_ASSIGNMENT_SQL",
    "_UPSERT_INVITATION_SQL",
    "_UPSERT_ORGANIZATION_SQL",
    "_UPSERT_SYSTEM_CONFIG_SQL",
    "_UPSERT_TENANT_SECRET_SQL",
    "_UPSERT_USER_SQL",
    "get_execution_assignment_row",
    "get_invitation_row",
    "get_organization_row",
    "get_system_config_row",
    "get_tenant_secret_row",
    "get_user_row",
    "hydrate_execution_assignment_row",
    "hydrate_invitation_row",
    "hydrate_organization_row",
    "hydrate_system_config_row",
    "hydrate_tenant_secret_row",
    "hydrate_user_row",
    "list_execution_assignment_rows",
    "list_invitation_rows",
    "list_organization_rows",
    "list_tenant_secret_rows",
    "list_user_rows",
    "upsert_execution_assignment_row",
    "upsert_invitation_row",
    "upsert_organization_row",
    "upsert_system_config_row",
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
VALUES ($1::uuid, $2, $3, $4, $5, $6, $7::uuid, $8, $9, $10, $11, $12::timestamptz)
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

_UPSERT_TENANT_SECRET_SQL: str = """INSERT INTO tenant_secrets (id, organization_id, scope, target_identifier,
    storage_mode, secret_manager_version_uri, encrypted_dek, ciphertext, nonce, kek_version, masked_hint,
    updated_by, updated_at)
VALUES ($1::uuid, $2::uuid, $3, $4, $5, $6, $7::bytea, $8::bytea, $9::bytea, $10, $11, $12::uuid, $13::timestamptz)
ON CONFLICT (id) DO UPDATE SET organization_id = EXCLUDED.organization_id, scope = EXCLUDED.scope,
    target_identifier = EXCLUDED.target_identifier, storage_mode = EXCLUDED.storage_mode,
    secret_manager_version_uri = EXCLUDED.secret_manager_version_uri,
    encrypted_dek = EXCLUDED.encrypted_dek, ciphertext = EXCLUDED.ciphertext, nonce = EXCLUDED.nonce,
    kek_version = EXCLUDED.kek_version, masked_hint = EXCLUDED.masked_hint,
    updated_by = EXCLUDED.updated_by, updated_at = EXCLUDED.updated_at"""

_GET_TENANT_SECRET_SQL: str = """SELECT id, organization_id, scope, target_identifier, storage_mode,
       secret_manager_version_uri, encrypted_dek, ciphertext, nonce, kek_version, masked_hint, updated_by, updated_at
FROM tenant_secrets WHERE id = $1::uuid"""

_LIST_TENANT_SECRETS_SQL: str = """SELECT id, organization_id, scope, target_identifier, storage_mode,
       secret_manager_version_uri, encrypted_dek, ciphertext, nonce, kek_version, masked_hint, updated_by, updated_at
FROM tenant_secrets"""

_LIST_TENANT_SECRETS_BY_ORG_SQL: str = """SELECT id, organization_id, scope, target_identifier, storage_mode,
       secret_manager_version_uri, encrypted_dek, ciphertext, nonce, kek_version, masked_hint, updated_by, updated_at
FROM tenant_secrets WHERE organization_id = $1::uuid"""

_UPSERT_EXECUTION_ASSIGNMENT_SQL: str = """INSERT INTO execution_assignments (id, batch_id, organization_id,
    assigned_email, assigned_user_id, invited_role, workflow_id, output_profile_id, task_brief_id, target_locale,
    locked_inputs, assignee_input_keys, draft_inputs, token_hash, status, email_delivery_status, result_visibility,
    hard_deadline_at, relative_duration_seconds, activated_at, submitted_at, execution_id, created_by)
VALUES ($1::uuid, $2::uuid, $3::uuid, $4, $5::uuid, $6, $7::uuid, $8::uuid, $9::uuid, $10, $11::jsonb, $12::jsonb,
    $13::jsonb, $14, $15, $16, $17, $18::timestamptz, $19, $20::timestamptz, $21::timestamptz, $22::uuid, $23::uuid)
ON CONFLICT (id) DO UPDATE SET batch_id = EXCLUDED.batch_id, organization_id = EXCLUDED.organization_id,
    assigned_email = EXCLUDED.assigned_email, assigned_user_id = EXCLUDED.assigned_user_id,
    invited_role = EXCLUDED.invited_role, workflow_id = EXCLUDED.workflow_id,
    output_profile_id = EXCLUDED.output_profile_id, task_brief_id = EXCLUDED.task_brief_id,
    target_locale = EXCLUDED.target_locale, locked_inputs = EXCLUDED.locked_inputs,
    assignee_input_keys = EXCLUDED.assignee_input_keys, draft_inputs = EXCLUDED.draft_inputs,
    token_hash = EXCLUDED.token_hash, status = EXCLUDED.status,
    email_delivery_status = EXCLUDED.email_delivery_status, result_visibility = EXCLUDED.result_visibility,
    hard_deadline_at = EXCLUDED.hard_deadline_at, relative_duration_seconds = EXCLUDED.relative_duration_seconds,
    activated_at = EXCLUDED.activated_at, submitted_at = EXCLUDED.submitted_at,
    execution_id = EXCLUDED.execution_id, created_by = EXCLUDED.created_by"""

_GET_EXECUTION_ASSIGNMENT_SQL: str = """SELECT id, batch_id, organization_id, assigned_email, assigned_user_id,
       invited_role, workflow_id, output_profile_id, task_brief_id, target_locale, locked_inputs, assignee_input_keys,
       draft_inputs, token_hash, status, email_delivery_status, result_visibility, hard_deadline_at,
       relative_duration_seconds, activated_at, submitted_at, execution_id, created_by, created_at
FROM execution_assignments WHERE id = $1::uuid"""

_LIST_EXECUTION_ASSIGNMENTS_SQL: str = """SELECT id, batch_id, organization_id, assigned_email, assigned_user_id,
       invited_role, workflow_id, output_profile_id, task_brief_id, target_locale, locked_inputs, assignee_input_keys,
       draft_inputs, token_hash, status, email_delivery_status, result_visibility, hard_deadline_at,
       relative_duration_seconds, activated_at, submitted_at, execution_id, created_by, created_at
FROM execution_assignments"""

_LIST_EXECUTION_ASSIGNMENTS_BY_ORG_SQL: str = """SELECT id, batch_id, organization_id, assigned_email,
       assigned_user_id, invited_role, workflow_id, output_profile_id, task_brief_id, target_locale, locked_inputs,
       assignee_input_keys, draft_inputs, token_hash, status, email_delivery_status, result_visibility,
       hard_deadline_at, relative_duration_seconds, activated_at, submitted_at, execution_id, created_by, created_at
FROM execution_assignments WHERE organization_id = $1::uuid"""

_UPSERT_SYSTEM_CONFIG_SQL: str = """INSERT INTO system_configs (id, name, type, slug, default_provider,
    tier_definitions, endpoint_url, transport_type, auth_type, auth_header_name, auth_env_var, timeout_seconds, tools)
VALUES ($1::uuid, $2, $3, $4, $5, $6::jsonb, $7, $8, $9, $10, $11, $12, $13::jsonb)
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, type = EXCLUDED.type, slug = EXCLUDED.slug,
    default_provider = EXCLUDED.default_provider, tier_definitions = EXCLUDED.tier_definitions,
    endpoint_url = EXCLUDED.endpoint_url, transport_type = EXCLUDED.transport_type, auth_type = EXCLUDED.auth_type,
    auth_header_name = EXCLUDED.auth_header_name, auth_env_var = EXCLUDED.auth_env_var,
    timeout_seconds = EXCLUDED.timeout_seconds, tools = EXCLUDED.tools"""

_GET_SYSTEM_CONFIG_SQL: str = """SELECT id, name, type, slug, default_provider, tier_definitions, endpoint_url,
       transport_type, auth_type, auth_header_name, auth_env_var, timeout_seconds, tools
FROM system_configs WHERE id = $1::uuid"""

_LIST_SYSTEM_CONFIGS_SQL: str = """SELECT id, name, type, slug, default_provider, tier_definitions, endpoint_url,
       transport_type, auth_type, auth_header_name, auth_env_var, timeout_seconds, tools FROM system_configs"""


async def _fetch_row(
    conn: AsyncPgConnectionProtocol, timeout: float | None, sql: str, entity_uuid: object, entity_id: str
) -> AsyncPgRecordProtocol | None:
    """Execute fetchrow with timeout and translate driver errors to AppException.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds, or None to resolve from settings.
        sql: Parameterized SELECT SQL statement.
        entity_uuid: Parsed 16-byte UUID primary key parameter.
        entity_id: Canonical Opaque Stripe ID of the target entity for error reporting.

    Returns:
        Database record if found, or None.

    Raises:
        AppException: With STORAGE_ACCESS_FAILED if the database query fails.
    """
    effective_timeout = resolve_effective_timeout(timeout)
    try:
        return await conn.fetchrow(sql, entity_uuid, timeout=effective_timeout)
    except Exception as exc:
        if isinstance(exc, AppException):
            raise
        msg = f"Failed to fetch entity '{entity_id}': {exc}"
        logger.error(
            "[PostgresEntityAdapter] %s: %s",
            ErrorCodes.STORAGE_ACCESS_FAILED.name,
            msg,
            exc_info=True,
            extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "entity_id": entity_id},
        )
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
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
    except Exception as exc:
        if isinstance(exc, AppException):
            raise
        msg = f"Failed to list rows from '{table_label}': {exc}"
        logger.error(
            "[PostgresEntityAdapter] %s: %s",
            ErrorCodes.STORAGE_ACCESS_FAILED.name,
            msg,
            exc_info=True,
            extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "table": table_label},
        )
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
        ) from exc


def hydrate_organization_row(row: AsyncPgRecordProtocol) -> Organization:
    """Hydrate an Organization from a database row.

    Args:
        row: Database record from the organizations table.

    Returns:
        Validated Organization domain model.

    Raises:
        AppException: With VALIDATION_FAILED if the organization UUID cannot be formatted.
    """
    return Organization.model_validate(
        {
            "id": str(_format_org_uuid7(row["id"])),
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
        strict=False,
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
        AppException: With VALIDATION_FAILED if the user or organization UUID cannot be formatted.
    """
    return User.model_validate(
        {
            "id": format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.USER),
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
            "created_by": row["created_by"],
            "deleted_at": row["deleted_at"],
        },
        strict=False,
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
        user.created_by,
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
        AppException: With VALIDATION_FAILED if UUID columns cannot be formatted.
    """
    return Invitation.model_validate(
        {
            "id": format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.INVITATION),
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
        strict=False,
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
        AppException: With VALIDATION_FAILED if UUID columns cannot be formatted.
    """
    return TenantSecretDTO.model_validate(
        {
            "id": format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.TENANT_SECRET),
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
        strict=False,
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
    return await execute_entity_upsert(
        conn,
        timeout,
        _UPSERT_TENANT_SECRET_SQL,
        parse_prefixed_uuid7(secret.id, EntityPrefix.TENANT_SECRET),
        parse_prefixed_uuid7(secret.organization_id, EntityPrefix.ORGANIZATION),
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
        AppException: With VALIDATION_FAILED if UUID columns cannot be formatted.
    """
    return ExecutionAssignment.model_validate(
        {
            "id": format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.ASSIGNMENT),
            "batch_id": _format_optional_uuid7(row["batch_id"], EntityPrefix.ASSIGNMENT),
            "organization_id": format_prefixed_uuid7(
                _coerce_uuid_or_str(row["organization_id"]), EntityPrefix.ORGANIZATION
            ),
            "assigned_email": row["assigned_email"],
            "assigned_user_id": _format_optional_uuid7(row["assigned_user_id"], EntityPrefix.USER),
            "invited_role": row["invited_role"],
            "workflow_id": format_prefixed_uuid7(_coerce_uuid_or_str(row["workflow_id"]), EntityPrefix.WORKFLOW),
            "output_profile_id": _format_optional_uuid7(row["output_profile_id"], EntityPrefix.OUTPUT_PROFILE),
            "task_brief_id": _format_optional_uuid7(row["task_brief_id"], EntityPrefix.PROMPT_BLOCK),
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
        strict=False,
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
        _parse_optional_uuid7(assignment.task_brief_id, EntityPrefix.PROMPT_BLOCK),
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


def hydrate_system_config_row(
    row: AsyncPgRecordProtocol,
) -> SystemConfigModelRegistry | SystemConfigMCPGateways:
    """Hydrate a polymorphic SystemConfig from a database row.

    Args:
        row: Database record from the system_configs table.

    Returns:
        Validated SystemConfigModelRegistry or SystemConfigMCPGateways instance.

    Raises:
        AppException: With VALIDATION_FAILED if the system_config UUID cannot be formatted or row validation fails.
    """
    cfg_id = format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.SYSTEM_CONFIG)
    try:
        if row["type"] == "mcp_gateways":
            return SystemConfigMCPGateways.model_validate(
                {
                    "id": cfg_id,
                    "name": row["name"],
                    "type": "mcp_gateways",
                    "slug": row["slug"],
                    "endpoint_url": row["endpoint_url"],
                    "transport_type": row["transport_type"],
                    "auth_type": row["auth_type"],
                    "auth_header_name": row["auth_header_name"],
                    "auth_env_var": row["auth_env_var"],
                    "timeout_seconds": row["timeout_seconds"],
                    "tools": _decode_jsonb_column(row["tools"]),
                },
                strict=False,
            )
        return SystemConfigModelRegistry.model_validate(
            {
                "id": cfg_id,
                "name": row["name"],
                "type": "model_registry",
                "default_provider": row["default_provider"],
                "tier_definitions": _decode_jsonb_column(row["tier_definitions"]),
            },
            strict=False,
        )
    except ValidationError as exc:
        msg = f"Failed to hydrate system_config '{cfg_id}': {exc}"
        logger.error(
            "[PostgresEntityAdapter] %s: %s",
            ErrorCodes.VALIDATION_FAILED.name,
            msg,
            exc_info=True,
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "entity_id": cfg_id},
        )
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "entity_id": cfg_id},
        ) from exc


async def upsert_system_config_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    cfg: SystemConfigModelRegistry | SystemConfigMCPGateways,
) -> str:
    """Persist a SystemConfigModelRegistry or SystemConfigMCPGateways into system_configs.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        cfg: Validated SystemConfigModelRegistry or SystemConfigMCPGateways domain model.

    Returns:
        Canonical sys_<hex> system configuration identifier.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED if persistence fails.
    """
    cfg_uuid = parse_prefixed_uuid7(cfg.id, EntityPrefix.SYSTEM_CONFIG)
    dumped = cfg.model_dump(mode="json")
    name = cfg.name
    slug = provider = tiers_json = endpoint_url = transport = auth_type = auth_hdr = auth_env = tools_json = None
    timeout_sec: int | None = None
    if isinstance(cfg, SystemConfigMCPGateways):
        slug = cfg.slug
        endpoint_url = cfg.endpoint_url
        transport = str(cfg.transport_type)
        auth_type = str(cfg.auth_type)
        auth_hdr = cfg.auth_header_name
        auth_env = cfg.auth_env_var
        timeout_sec = cfg.timeout_seconds
        tools_json = to_json(dumped["tools"]).decode("utf-8")
    else:
        provider = str(cfg.default_provider)
        tiers_json = to_json(dumped["tier_definitions"]).decode("utf-8")
    return await execute_entity_upsert(
        conn,
        timeout,
        _UPSERT_SYSTEM_CONFIG_SQL,
        cfg_uuid,
        name,
        cfg.type,
        slug,
        provider,
        tiers_json,
        endpoint_url,
        transport,
        auth_type,
        auth_hdr,
        auth_env,
        timeout_sec,
        tools_json,
        entity_id=cfg.id,
        entity_label="system_config",
    )


async def get_system_config_row(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    config_id: str,
) -> SystemConfigModelRegistry | SystemConfigMCPGateways | None:
    """Fetch a SystemConfig by ID.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        config_id: Canonical sys_<hex> system configuration identifier.

    Returns:
        Hydrated SystemConfigModelRegistry or SystemConfigMCPGateways if found, or None.

    Raises:
        AppException: With VALIDATION_FAILED on invalid ID or STORAGE_ACCESS_FAILED on query error.
    """
    cfg_uuid = parse_prefixed_uuid7(config_id, EntityPrefix.SYSTEM_CONFIG)
    row = await _fetch_row(conn, timeout, _GET_SYSTEM_CONFIG_SQL, cfg_uuid, config_id)
    if row is None:
        return None
    return hydrate_system_config_row(row)
