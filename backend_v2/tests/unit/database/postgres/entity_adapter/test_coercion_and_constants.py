"""Unit and boundary tests for PostgreSQL 19 leaf constants, coercion helpers, and upsert execution."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend_v2.database.postgres.entity_adapter import coercion_and_constants as coercion_mod
from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    _COLLECTION_TO_TABLE_MAP,
    _ROOT_SYSTEM_ORG_UUID7,
    _SYSTEM_ORG_UUID7,
    _TABLE_TO_ENTITY_PREFIX,
    CANONICAL_SEED_TABLES,
    _coerce_float,
    _coerce_uuid_or_str,
    _decode_jsonb_column,
    _encode_optional_jsonb,
    _format_optional_uuid7,
    _format_org_uuid7,
    _parse_optional_uuid7,
    _parse_org_uuid7,
    _ReportBinaryRowDTO,
    execute_entity_upsert,
    resolve_effective_timeout,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import generate_opaque_id, generate_uuid7, parse_prefixed_uuid7
from backend_v2.models.enums import EntityPrefix
from backend_v2.tests.fakes.in_memory_uow import InMemoryAsyncPgPool


def test_coercion_helpers_and_canonical_seed_tables_parity() -> None:
    """Verify CANONICAL_SEED_TABLES, org UUIDv7 helpers, JSONB decode/encode, and float coercion parity."""
    assert len(CANONICAL_SEED_TABLES) == 10
    assert "organizations" in CANONICAL_SEED_TABLES
    assert "report_binaries" in CANONICAL_SEED_TABLES
    assert _COLLECTION_TO_TABLE_MAP["components"] == "prompt_blocks"
    assert _COLLECTION_TO_TABLE_MAP["task_blueprints"] == "steps"
    assert _TABLE_TO_ENTITY_PREFIX["workflows"] == EntityPrefix.WORKFLOW

    sample_uuid = generate_uuid7()
    assert _coerce_uuid_or_str(sample_uuid) == sample_uuid
    assert _coerce_uuid_or_str(str(sample_uuid)) == str(sample_uuid)
    assert _coerce_uuid_or_str(12345) == "12345"

    assert _parse_optional_uuid7(None, EntityPrefix.WORKFLOW) is None
    wf_id = generate_opaque_id(EntityPrefix.WORKFLOW)
    parsed_wf = _parse_optional_uuid7(wf_id, EntityPrefix.WORKFLOW)
    assert isinstance(parsed_wf, uuid.UUID)
    assert _format_optional_uuid7(None, EntityPrefix.WORKFLOW) is None
    assert _format_optional_uuid7(parsed_wf, EntityPrefix.WORKFLOW) == wf_id

    assert _parse_org_uuid7(None) is None
    assert _parse_org_uuid7("SYSTEM") is None
    assert _parse_org_uuid7("org_0195f3a0000070008000000000000001") == _ROOT_SYSTEM_ORG_UUID7
    org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
    parsed_org = _parse_org_uuid7(org_id)
    assert isinstance(parsed_org, uuid.UUID)

    assert _format_org_uuid7(None, default_system=False) is None
    assert _format_org_uuid7(None, default_system=True) == "SYSTEM"
    assert _format_org_uuid7(_SYSTEM_ORG_UUID7) == "SYSTEM"
    assert _format_org_uuid7(str(_SYSTEM_ORG_UUID7)) == "SYSTEM"
    assert _format_org_uuid7(_ROOT_SYSTEM_ORG_UUID7) == "org_0195f3a0000070008000000000000001"
    assert _format_org_uuid7("org_0195f3a0000070008000000000000001") == "org_0195f3a0000070008000000000000001"
    assert _format_org_uuid7(parsed_org) == org_id

    assert _decode_jsonb_column(None) is None
    assert _decode_jsonb_column('{"k": 1}') == {"k": 1}
    assert _decode_jsonb_column(b'["a", "b"]') == ["a", "b"]
    assert _decode_jsonb_column(bytearray(b'{"x": true}')) == {"x": True}
    assert _decode_jsonb_column(memoryview(b"[1, 2]")) == [1, 2]
    already_decoded = ["pre_decoded"]
    assert _decode_jsonb_column(already_decoded) == already_decoded

    assert _encode_optional_jsonb(None) is None
    assert _encode_optional_jsonb({"a": 1}) == '{"a":1}'

    assert _coerce_float(1.25) == 1.25
    assert _coerce_float(5) == 5.0
    assert _coerce_float(Decimal("3.75")) == 3.75
    assert _coerce_float("9.5") == 9.5

    assert resolve_effective_timeout(12.5) == 12.5
    assert resolve_effective_timeout(None) > 0.0


@pytest.mark.asyncio
async def test_execute_entity_upsert_executes_parameterized_sql() -> None:
    """Verify execute_entity_upsert forwards SQL, parameters, and command_timeout_seconds to connection.execute."""
    pool = InMemoryAsyncPgPool()
    org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
    org_uuid = parse_prefixed_uuid7(org_id, EntityPrefix.ORGANIZATION)
    now = datetime.now(UTC)
    sql = """
    INSERT INTO organizations (id, name, description, is_active, created_at, updated_at)
    VALUES ($1, $2, $3, $4, $5, $6)
    ON CONFLICT (id) DO UPDATE SET
        name = EXCLUDED.name,
        description = EXCLUDED.description,
        is_active = EXCLUDED.is_active,
        updated_at = EXCLUDED.updated_at
    """
    conn = await pool.acquire()
    try:
        persisted_id = await execute_entity_upsert(
            conn,
            15.0,
            sql,
            org_uuid,
            "Acme Org",
            "Description",
            True,
            now,
            now,
            entity_id=org_id,
            table="organizations",
        )
        assert persisted_id == org_id
        row = await conn.fetchrow(
            "SELECT id, name, description, is_active, created_at, updated_at FROM organizations WHERE id = $1",
            org_uuid,
            timeout=5.0,
        )
        assert row is not None
        assert row["name"] == "Acme Org"
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_report_binary_row_dto_size_mismatch_and_upsert_driver_fault() -> None:
    """Verify _ReportBinaryRowDTO rejects mismatched size_bytes and execute_entity_upsert translates driver faults."""
    report_id = generate_opaque_id(EntityPrefix.REPORT)
    now = datetime.now(UTC)
    valid_row = _ReportBinaryRowDTO(
        report_id=report_id,
        mime_type="application/pdf",
        pdf_bytes=b"%PDF-1.7-payload",
        size_bytes=len(b"%PDF-1.7-payload"),
        created_at=now,
    )
    assert valid_row.report_id == report_id

    with pytest.raises(ValidationError):
        _ReportBinaryRowDTO(
            report_id=report_id,
            mime_type="application/pdf",
            pdf_bytes=b"%PDF-1.7-payload",
            size_bytes=999,
            created_at=now,
        )

    with pytest.raises(ValidationError):
        _ReportBinaryRowDTO(
            report_id=report_id,
            mime_type="application/pdf",
            pdf_bytes=b"%PDF-1.7-payload",
            size_bytes=-1,
            created_at=now,
        )

    pool = InMemoryAsyncPgPool()
    direct_app_exc = AppException(
        message="Pre-existing validation error",
        status_code=422,
        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
    )
    conn = await pool.acquire()
    try:
        pool.inject_fault("execute", RuntimeError("connection reset"))
        with pytest.raises(AppException) as exc_info:
            await execute_entity_upsert(
                conn,
                5.0,
                "INSERT INTO organizations (id) VALUES ($1)",
                generate_uuid7(),
                entity_id=report_id,
                table="organizations",
            )
        assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        pool.inject_fault("execute", direct_app_exc)
        with pytest.raises(AppException) as passthrough_info:
            await execute_entity_upsert(
                conn,
                5.0,
                "INSERT INTO organizations (id) VALUES ($1)",
                generate_uuid7(),
                entity_id=report_id,
                entity_label="organization",
            )
        assert passthrough_info.value is direct_app_exc
    finally:
        pool.clear_faults()
        await pool.release(conn)


def test_coercion_helpers_negative_boundary_cases(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify negative and boundary inputs raise AppException or ValueError deterministically."""
    with pytest.raises(AppException) as exc_opt_parse:
        _parse_optional_uuid7("invalid_id", EntityPrefix.WORKFLOW)
    assert exc_opt_parse.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    with pytest.raises(AppException) as exc_opt_fmt:
        _format_optional_uuid7("not-a-uuid", EntityPrefix.WORKFLOW)
    assert exc_opt_fmt.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    with pytest.raises(AppException) as exc_org_parse:
        _parse_org_uuid7("org_invalid")
    assert exc_org_parse.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    with pytest.raises(AppException) as exc_org_fmt:
        _format_org_uuid7("not-an-org-uuid")
    assert exc_org_fmt.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    with pytest.raises(ValueError):
        _coerce_float("not_a_float")

    class _DummySettings:
        postgres_command_timeout_seconds: float = 42.0

    monkeypatch.setattr(coercion_mod, "get_settings", lambda: _DummySettings())
    assert resolve_effective_timeout(None) == 42.0
