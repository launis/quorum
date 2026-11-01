"""Leaf table constants, column coercion helpers, and parameterized upsert execution for PostgreSQL 19."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Self

from fastapi import status
from pydantic import ConfigDict, Field, model_validator
from pydantic_core import from_json, to_json

from backend_v2.database.postgres.pool import AsyncPgConnectionProtocol
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import (
    OPAQUE_STRIPE_ID_REGEX,
    V2CoreBase,
    format_prefixed_uuid7,
    parse_prefixed_uuid7,
)
from backend_v2.models.enums import EntityPrefix
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = [
    "CANONICAL_SEED_TABLES",
    "_COLLECTION_TO_TABLE_MAP",
    "_ROOT_SYSTEM_ORG_UUID7",
    "_ReportBinaryRowDTO",
    "_SYSTEM_ORG_UUID7",
    "_TABLE_TO_ENTITY_PREFIX",
    "_coerce_float",
    "_coerce_uuid_or_str",
    "_decode_jsonb_column",
    "_encode_optional_jsonb",
    "_format_optional_uuid7",
    "_format_org_uuid7",
    "_parse_optional_uuid7",
    "_parse_org_uuid7",
    "execute_entity_upsert",
    "resolve_effective_timeout",
]

CANONICAL_SEED_TABLES: tuple[str, ...] = (
    "organizations",
    "users",
    "system_configs",
    "prompt_blocks",
    "steps",
    "workflows",
    "output_profiles",
    "executions",
    "report_artifacts",
    "report_binaries",
)

_COLLECTION_TO_TABLE_MAP: dict[str, str] = {
    "organizations": "organizations",
    "users": "users",
    "system_config": "system_configs",
    "system_configs": "system_configs",
    "prompt_blocks": "prompt_blocks",
    "components": "prompt_blocks",
    "agents": "prompt_blocks",
    "steps": "steps",
    "task_blueprints": "steps",
    "workflows": "workflows",
    "output_profiles": "output_profiles",
    "executions": "executions",
    "report_artifacts": "report_artifacts",
    "report_binaries": "report_binaries",
}

_TABLE_TO_ENTITY_PREFIX: dict[str, EntityPrefix] = {
    "organizations": EntityPrefix.ORGANIZATION,
    "users": EntityPrefix.USER,
    "system_configs": EntityPrefix.SYSTEM_CONFIG,
    "prompt_blocks": EntityPrefix.PROMPT_BLOCK,
    "steps": EntityPrefix.STEP,
    "workflows": EntityPrefix.WORKFLOW,
    "output_profiles": EntityPrefix.OUTPUT_PROFILE,
    "executions": EntityPrefix.EXECUTION,
    "report_artifacts": EntityPrefix.REPORT,
    "report_binaries": EntityPrefix.REPORT,
}

_SYSTEM_ORG_UUID7: uuid.UUID = uuid.UUID("0195f3a0-0000-7000-8000-000000000000")
_ROOT_SYSTEM_ORG_UUID7: uuid.UUID = uuid.UUID("0195f3a0-0000-7000-8000-000000000001")


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

    @model_validator(mode="after")
    def validate_size_bytes_matches_pdf_bytes(self) -> Self:
        """Verify size_bytes matches the actual byte length of pdf_bytes.

        Returns:
            Validated _ReportBinaryRowDTO instance.

        Raises:
            ValueError: If size_bytes does not equal len(pdf_bytes).
        """
        if self.size_bytes != len(self.pdf_bytes):
            raise ValueError(f"size_bytes ({self.size_bytes}) must equal len(pdf_bytes) ({len(self.pdf_bytes)}).")
        return self


def _coerce_uuid_or_str(raw: object) -> uuid.UUID | str:
    """Narrow a raw database UUID or string column value to uuid.UUID | str.

    Args:
        raw: Raw database column value to coerce.

    Returns:
        Original uuid.UUID or str instance, or string representation of raw.
    """
    if isinstance(raw, (uuid.UUID, str)):
        return raw
    return str(raw)


def _parse_optional_uuid7(raw: str | None, prefix: EntityPrefix) -> uuid.UUID | None:
    """Parse an optional Opaque Stripe ID into a 16-byte UUIDv7 or None.

    Args:
        raw: Optional canonical Opaque Stripe ID string.
        prefix: Expected EntityPrefix for validation.

    Returns:
        Parsed 16-byte uuid.UUID instance, or None when raw is None.

    Raises:
        AppException: With VALIDATION_FAILED if raw does not match the prefix or 32-hex UUID format.
    """
    if raw is None:
        return None
    return parse_prefixed_uuid7(raw, prefix)


def _format_optional_uuid7(raw: object, prefix: EntityPrefix) -> str | None:
    """Format an optional database UUID column value into a {prefix}_{32_hex} string or None.

    Args:
        raw: Optional raw database UUID or string column value.
        prefix: Target EntityPrefix to prepend.

    Returns:
        Formatted Opaque Stripe ID string, or None when raw is None.

    Raises:
        AppException: With VALIDATION_FAILED if raw cannot be formatted as a valid UUID.
    """
    if raw is None:
        return None
    return format_prefixed_uuid7(_coerce_uuid_or_str(raw), prefix)


def _parse_org_uuid7(raw: str | None) -> uuid.UUID | None:
    """Parse an optional organization_id into a 16-byte UUIDv7, bridging 'SYSTEM' deterministically.

    Args:
        raw: Optional organization identifier ('SYSTEM', 'org_system000000', or 'org_<32_hex>').

    Returns:
        Parsed 16-byte uuid.UUID instance, or None for global/SYSTEM scope.

    Raises:
        AppException: With VALIDATION_FAILED if raw is not a valid organization identifier.
    """
    if raw is None or raw == "SYSTEM":
        return None
    if raw == "org_system000000":
        return _ROOT_SYSTEM_ORG_UUID7
    return parse_prefixed_uuid7(raw, EntityPrefix.ORGANIZATION)


def _format_org_uuid7(raw: object, *, default_system: bool = False) -> str | None:
    """Format a database organization_id UUID column into 'org_<32_hex>', 'org_system000000', 'SYSTEM', or None.

    Args:
        raw: Raw database organization_id column value or None.
        default_system: Whether None should resolve to 'SYSTEM' instead of None.

    Returns:
        Canonical organization identifier string or None.

    Raises:
        AppException: With VALIDATION_FAILED if raw cannot be formatted as a valid organization UUID.
    """
    if raw is None:
        return "SYSTEM" if default_system else None
    coerced = _coerce_uuid_or_str(raw)
    if coerced == _SYSTEM_ORG_UUID7 or str(coerced) in {str(_SYSTEM_ORG_UUID7), "SYSTEM"}:
        return "SYSTEM"
    if coerced == _ROOT_SYSTEM_ORG_UUID7 or str(coerced) in {str(_ROOT_SYSTEM_ORG_UUID7), "org_system000000"}:
        return "org_system000000"
    return format_prefixed_uuid7(coerced, EntityPrefix.ORGANIZATION)


def _decode_jsonb_column(raw: object) -> object:
    """Decode a JSONB column value if returned as raw UTF-8 string or bytes.

    Args:
        raw: Raw JSONB column payload from asyncpg or in-memory driver.

    Returns:
        Decoded Python object, or None when raw is None.
    """
    if raw is None:
        return None
    if isinstance(raw, (str, bytes, bytearray)):
        return from_json(raw)
    if isinstance(raw, memoryview):
        return from_json(bytes(raw))
    return raw


def _encode_optional_jsonb(val: object) -> str | None:
    """Encode an optional value to a UTF-8 JSON string for asyncpg JSONB parameters.

    Args:
        val: Optional serializable Python value.

    Returns:
        UTF-8 JSON string, or None when val is None.
    """
    if val is None:
        return None
    return to_json(val).decode("utf-8")


def _coerce_float(raw: object) -> float:
    """Convert a database NUMERIC/Decimal or float column value to float.

    Args:
        raw: Database numeric column value (float, int, Decimal, or numeric string).

    Returns:
        Converted Python float value.

    Raises:
        ValueError: If the string representation of raw cannot be converted to float.
    """
    if isinstance(raw, (float, int, Decimal)):
        return float(raw)
    return float(str(raw))


def resolve_effective_timeout(command_timeout_seconds: float | None = None) -> float:
    """Resolve the effective PostgreSQL command timeout in seconds from settings.py when omitted.

    Args:
        command_timeout_seconds: Explicit timeout override in seconds, or None.

    Returns:
        Positive timeout duration in seconds.
    """
    if command_timeout_seconds is not None:
        return command_timeout_seconds
    return get_settings().postgres_command_timeout_seconds


async def execute_entity_upsert(
    conn: AsyncPgConnectionProtocol,
    timeout: float,
    sql: str,
    *args: object,
    entity_id: str,
    table: str = "",
    entity_label: str = "entity",
) -> str:
    """Execute a parameterized upsert statement and translate transport errors to AppException.

    Args:
        conn: Active database connection conforming to AsyncPgConnectionProtocol.
        timeout: Command execution timeout in seconds.
        sql: Parameterized INSERT ... ON CONFLICT DO UPDATE statement.
        *args: Positional SQL bind arguments.
        entity_id: Canonical Opaque Stripe ID of the entity being persisted.
        table: Optional canonical table name for structured error logging.
        entity_label: Human-readable entity type label for structured error logging.

    Returns:
        Canonical entity_id persisted into PostgreSQL 19.

    Raises:
        AppException: With STORAGE_ACCESS_FAILED if the database command fails.
    """
    label = table if table else entity_label
    try:
        await conn.execute(sql, *args, timeout=timeout)
    except Exception as exc:
        if isinstance(exc, AppException):
            raise
        msg = f"Failed to upsert {label} '{entity_id}': {exc}"
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
    return entity_id
