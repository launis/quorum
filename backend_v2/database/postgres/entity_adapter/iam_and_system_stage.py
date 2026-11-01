"""PostgreSQL 19 SQL constants, hydration, upsert, and fetch stage for IAM and system_configs."""

from __future__ import annotations

import logging

from fastapi import status
from pydantic_core import to_json

from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    _coerce_float,
    _coerce_uuid_or_str,
    _decode_jsonb_column,
    _format_org_uuid7,
    _parse_org_uuid7,
    execute_entity_upsert,
    resolve_effective_timeout,
)
from backend_v2.database.postgres.pool import AsyncPgConnectionProtocol, AsyncPgRecordProtocol
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import Organization, User
from backend_v2.models.core_base import format_prefixed_uuid7, parse_prefixed_uuid7
from backend_v2.models.domain.system_config import SystemConfigMCPGateways, SystemConfigModelRegistry
from backend_v2.models.enums import EntityPrefix

logger = logging.getLogger(__name__)

__all__ = [
    "_GET_ORGANIZATION_SQL",
    "_GET_SYSTEM_CONFIG_SQL",
    "_GET_USER_SQL",
    "_LIST_ORGANIZATIONS_SQL",
    "_LIST_SYSTEM_CONFIGS_SQL",
    "_LIST_USERS_SQL",
    "_UPSERT_ORGANIZATION_SQL",
    "_UPSERT_SYSTEM_CONFIG_SQL",
    "_UPSERT_USER_SQL",
    "get_organization_row",
    "get_system_config_row",
    "get_user_row",
    "hydrate_organization_row",
    "hydrate_system_config_row",
    "hydrate_user_row",
    "upsert_organization_row",
    "upsert_system_config_row",
    "upsert_user_row",
]

_UPSERT_ORGANIZATION_SQL: str = """INSERT INTO organizations (id, slug, name, is_active, tier, contact_email,
    billing_id, subscription_status, quota_limit, tpm_limit, rpm_limit)
VALUES ($1::uuid, $2, $3, $4, $5, $6, $7, $8, $9::numeric, $10::bigint, $11)
ON CONFLICT (id) DO UPDATE SET slug = EXCLUDED.slug, name = EXCLUDED.name, is_active = EXCLUDED.is_active,
    tier = EXCLUDED.tier, contact_email = EXCLUDED.contact_email, billing_id = EXCLUDED.billing_id,
    subscription_status = EXCLUDED.subscription_status, quota_limit = EXCLUDED.quota_limit,
    tpm_limit = EXCLUDED.tpm_limit, rpm_limit = EXCLUDED.rpm_limit"""

_GET_ORGANIZATION_SQL: str = """SELECT id, slug, name, created_at, is_active, tier, contact_email, billing_id,
       subscription_status, quota_limit, tpm_limit, rpm_limit FROM organizations WHERE id = $1::uuid"""

_LIST_ORGANIZATIONS_SQL: str = """SELECT id, slug, name, created_at, is_active, tier, contact_email, billing_id,
       subscription_status, quota_limit, tpm_limit, rpm_limit FROM organizations"""

_UPSERT_USER_SQL: str = """INSERT INTO users (id, slug, email, name, role, organization_id, is_active, language,
    theme_mode, created_by) VALUES ($1::uuid, $2, $3, $4, $5, $6::uuid, $7, $8, $9, $10)
ON CONFLICT (id) DO UPDATE SET slug = EXCLUDED.slug, email = EXCLUDED.email, name = EXCLUDED.name, role = EXCLUDED.role,
    organization_id = EXCLUDED.organization_id, is_active = EXCLUDED.is_active, language = EXCLUDED.language,
    theme_mode = EXCLUDED.theme_mode, created_by = EXCLUDED.created_by"""

_GET_USER_SQL: str = """SELECT id, slug, email, name, role, organization_id, is_active, language, theme_mode,
       created_at, created_by FROM users WHERE id = $1::uuid"""

_LIST_USERS_SQL: str = """SELECT id, slug, email, name, role, organization_id, is_active, language, theme_mode,
       created_at, created_by FROM users"""

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
            "email": row["email"],
            "name": row["name"],
            "role": row["role"],
            "organization_id": _format_org_uuid7(row["organization_id"]),
            "is_active": row["is_active"],
            "language": row["language"],
            "theme_mode": row["theme_mode"],
            "created_at": row["created_at"],
            "created_by": row["created_by"],
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
        str(user.email),
        user.name,
        user.role.value,
        _parse_org_uuid7(user.organization_id),
        user.is_active,
        str(user.language),
        user.theme_mode,
        user.created_by,
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


def hydrate_system_config_row(
    row: AsyncPgRecordProtocol,
) -> SystemConfigModelRegistry | SystemConfigMCPGateways:
    """Hydrate a polymorphic SystemConfig from a database row.

    Args:
        row: Database record from the system_configs table.

    Returns:
        Validated SystemConfigModelRegistry or SystemConfigMCPGateways instance.

    Raises:
        AppException: With VALIDATION_FAILED if the system_config UUID cannot be formatted.
    """
    cfg_id = format_prefixed_uuid7(_coerce_uuid_or_str(row["id"]), EntityPrefix.SYSTEM_CONFIG)
    if row["type"] == "mcp_gateways":
        return SystemConfigMCPGateways.model_validate(
            {
                "id": cfg_id,
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
    name = slug = provider = tiers_json = endpoint_url = transport = auth_type = auth_hdr = auth_env = tools_json = None
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
        name = cfg.name
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
