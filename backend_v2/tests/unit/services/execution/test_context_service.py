"""Unit tests for ExecutionContextService."""

from __future__ import annotations

import logging
import re
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, generate_opaque_id
from backend_v2.models.domain.execution import ExecutionRecord, FrozenContext
from backend_v2.models.dtos.schema_manifest import GeneratedSchemaManifestDTO
from backend_v2.models.dtos.theory_manifest import InjectedTheoryManifestDTO
from backend_v2.models.enums import EntityPrefix, ExecutionStatus
from backend_v2.services.execution.context_service import ExecutionContextService
from backend_v2.tests.factories.model_factories import ExecutionRecordFactory, MCPAuditTraceFactory
from backend_v2.tests.fakes.in_memory_repositories import InMemoryExecutionRepository


def _empty_frozen_context() -> FrozenContext:
    """Construct an empty FrozenContext instance with explicit typed manifests."""
    return FrozenContext(
        compiled_prompts={},
        injected_theory=InjectedTheoryManifestDTO(theories={}),
        generated_schemas=GeneratedSchemaManifestDTO(schemas={}),
        ui_hints_snapshot={},
        mcp_tool_audit=[],
    )


def _make_record(
    execution_id: str | None = None,
    org_id: str | None = None,
    user_id: str | None = None,
    status: ExecutionStatus = ExecutionStatus.PASSED,
    frozen_context: FrozenContext | None = None,
) -> ExecutionRecord:
    """Build a canonical ExecutionRecord via Polyfactory with optional overrides."""
    resolved_exec_id = execution_id if execution_id is not None else generate_opaque_id(EntityPrefix.EXECUTION)
    resolved_org_id = org_id if org_id is not None else generate_opaque_id(EntityPrefix.ORGANIZATION)
    resolved_user_id = user_id if user_id is not None else generate_opaque_id(EntityPrefix.USER)
    record = ExecutionRecordFactory.build(
        id=resolved_exec_id,
        organization_id=resolved_org_id,
        created_by=resolved_user_id,
        status=status,
        frozen_context=frozen_context,
    )
    validated = ExecutionRecord.model_validate(record.model_dump(mode="json", exclude_none=True), strict=False)
    assert re.fullmatch(OPAQUE_STRIPE_ID_REGEX, validated.id) is not None
    return validated


@pytest.fixture
def org_id() -> str:
    """Return a canonical 32-hex organization Opaque Stripe ID."""
    return generate_opaque_id(EntityPrefix.ORGANIZATION)


@pytest.fixture
def member_token(org_id: str) -> TokenData:
    """Return a standard MEMBER token fixture scoped to org_id."""
    return TokenData(
        id=generate_opaque_id(EntityPrefix.USER),
        role=UserRole.MEMBER,
        organization_id=org_id,
    )


@pytest.fixture
def admin_token(org_id: str) -> TokenData:
    """Return an ADMIN token fixture scoped to org_id."""
    return TokenData(
        id=generate_opaque_id(EntityPrefix.USER),
        role=UserRole.ADMIN,
        organization_id=org_id,
    )


@pytest.fixture
def manager_token(org_id: str) -> TokenData:
    """Return a MANAGER token fixture scoped to org_id."""
    return TokenData(
        id=generate_opaque_id(EntityPrefix.USER),
        role=UserRole.MANAGER,
        organization_id=org_id,
    )


@pytest.fixture
def root_token() -> TokenData:
    """Return a ROOT administrator token fixture."""
    return TokenData(
        id=generate_opaque_id(EntityPrefix.USER),
        role=UserRole.ROOT,
        organization_id=generate_opaque_id(EntityPrefix.ORGANIZATION),
    )


@pytest.mark.asyncio
async def test_default_get_execution_happy_path_owner_member(member_token: TokenData, org_id: str) -> None:
    """Verify _default_get_execution returns record when MEMBER owns the execution."""
    rec = _make_record(org_id=org_id, user_id=member_token.id)
    exec_repo = InMemoryExecutionRepository()
    await exec_repo.save_execution(rec)

    storage_mock = AsyncMock()
    service = ExecutionContextService(exec_repo=exec_repo, storage_driver=storage_mock)
    result = await service._default_get_execution(member_token, rec.id)
    assert result.id == rec.id
    assert service.storage is storage_mock


@pytest.mark.asyncio
async def test_default_get_execution_happy_path_admin_and_manager_same_org(
    admin_token: TokenData, manager_token: TokenData, org_id: str
) -> None:
    """Verify _default_get_execution allows ADMIN and MANAGER to access same-org executions owned by others."""
    other_user_id = generate_opaque_id(EntityPrefix.USER)
    rec = _make_record(org_id=org_id, user_id=other_user_id)
    exec_repo = InMemoryExecutionRepository()
    await exec_repo.save_execution(rec)

    service = ExecutionContextService(exec_repo=exec_repo)
    admin_res = await service._default_get_execution(admin_token, rec.id)
    manager_res = await service._default_get_execution(manager_token, rec.id)
    assert admin_res.id == rec.id
    assert manager_res.id == rec.id


@pytest.mark.asyncio
async def test_default_get_execution_happy_path_root_cross_org(root_token: TokenData) -> None:
    """Verify _default_get_execution allows ROOT user to access execution across organizations."""
    rec = _make_record(
        org_id=generate_opaque_id(EntityPrefix.ORGANIZATION),
        user_id=generate_opaque_id(EntityPrefix.USER),
    )
    exec_repo = InMemoryExecutionRepository()
    await exec_repo.save_execution(rec)

    service = ExecutionContextService(exec_repo=exec_repo)
    result = await service._default_get_execution(root_token, rec.id)
    assert result.id == rec.id


@pytest.mark.asyncio
async def test_default_get_execution_not_found_logs_and_raises(
    member_token: TokenData, caplog: pytest.LogCaptureFixture
) -> None:
    """ISTQB Negative: _default_get_execution logs RFC 7807 error and raises ResourceNotFoundError when missing."""
    exec_repo = InMemoryExecutionRepository()
    service = ExecutionContextService(exec_repo=exec_repo)
    missing_id = generate_opaque_id(EntityPrefix.EXECUTION)

    with caplog.at_level(logging.ERROR), pytest.raises(ResourceNotFoundError) as exc_info:
        await service._default_get_execution(member_token, missing_id)

    assert exc_info.value.status_code == 404
    assert ErrorCodes.RESOURCE_NOT_FOUND.name in caplog.text


@pytest.mark.asyncio
async def test_default_get_execution_member_same_org_other_owner_denied(
    member_token: TokenData, org_id: str, caplog: pytest.LogCaptureFixture
) -> None:
    """ISTQB Negative Boundary (4-Tier RBAC): MEMBER cannot access another user's execution in the same org."""
    rec = _make_record(org_id=org_id, user_id=generate_opaque_id(EntityPrefix.USER))
    exec_repo = InMemoryExecutionRepository()
    await exec_repo.save_execution(rec)

    service = ExecutionContextService(exec_repo=exec_repo)
    with caplog.at_level(logging.ERROR), pytest.raises(PermissionDeniedError) as exc_info:
        await service._default_get_execution(member_token, rec.id)

    assert exc_info.value.status_code == 403
    assert ErrorCodes.PERMISSION_DENIED.name in caplog.text


@pytest.mark.asyncio
async def test_default_get_execution_admin_cross_org_permission_denied(
    admin_token: TokenData, caplog: pytest.LogCaptureFixture
) -> None:
    """ISTQB Negative: ADMIN denied access to execution belonging to another organization."""
    rec = _make_record(
        org_id=generate_opaque_id(EntityPrefix.ORGANIZATION),
        user_id=generate_opaque_id(EntityPrefix.USER),
    )
    exec_repo = InMemoryExecutionRepository()
    await exec_repo.save_execution(rec)

    service = ExecutionContextService(exec_repo=exec_repo)
    with caplog.at_level(logging.ERROR), pytest.raises(PermissionDeniedError) as exc_info:
        await service._default_get_execution(admin_token, rec.id)

    assert exc_info.value.status_code == 403
    assert ErrorCodes.PERMISSION_DENIED.name in caplog.text


@pytest.mark.asyncio
async def test_get_frozen_context_bytes_inline_frozen_context(member_token: TokenData, org_id: str) -> None:
    """Verify get_frozen_context_bytes serializes hydrated FrozenContext including mcp_tool_audit."""
    fc = FrozenContext(
        compiled_prompts={"stp_0195f3a0000070008123456789abcdef": "System prompt"},
        injected_theory=InjectedTheoryManifestDTO(theories={}),
        generated_schemas=GeneratedSchemaManifestDTO(schemas={}),
        ui_hints_snapshot={},
        mcp_tool_audit=[
            MCPAuditTraceFactory.build(
                gateway_id="mcp_0195f3a0000070008123456789abcdef",
                tool_id="fetch_filing",
                step_name="stp_0195f3a0000070008123456789abcdef",
                duration_ms=42,
            )
        ],
    )
    rec = _make_record(
        org_id=org_id,
        user_id=member_token.id,
        frozen_context=fc,
    )
    exec_repo = InMemoryExecutionRepository()
    await exec_repo.save_execution(rec)

    service = ExecutionContextService(exec_repo=exec_repo)
    payload_bytes, filename = await service.get_frozen_context_bytes(member_token, rec.id)

    assert filename == f"frozen_context_{rec.id}.json"
    parsed = FrozenContext.model_validate_json(payload_bytes)
    assert parsed == fc
    assert len(parsed.mcp_tool_audit) == 1


@pytest.mark.asyncio
async def test_get_frozen_context_bytes_none_frozen_context_defaults_empty(
    member_token: TokenData, org_id: str
) -> None:
    """Verify get_frozen_context_bytes returns empty FrozenContext JSON when inline context is None."""
    rec = _make_record(
        org_id=org_id,
        user_id=member_token.id,
        frozen_context=None,
    )

    async def custom_get_exec(initiator: TokenData, execution_id: str) -> ExecutionRecord:
        return rec

    exec_repo = InMemoryExecutionRepository()
    service = ExecutionContextService(exec_repo=exec_repo, get_execution_fn=custom_get_exec)
    payload_bytes, filename = await service.get_frozen_context_bytes(member_token, rec.id)

    assert filename == f"frozen_context_{rec.id}.json"
    parsed = FrozenContext.model_validate_json(payload_bytes)
    assert parsed == _empty_frozen_context()


@pytest.mark.asyncio
async def test_get_frozen_context_bytes_missing_execution_raises_404(member_token: TokenData) -> None:
    """ISTQB Negative: get_frozen_context_bytes raises ResourceNotFoundError when execution does not exist."""
    exec_repo = InMemoryExecutionRepository()
    service = ExecutionContextService(exec_repo=exec_repo)
    missing_id = generate_opaque_id(EntityPrefix.EXECUTION)

    with pytest.raises(ResourceNotFoundError) as exc_info:
        await service.get_frozen_context_bytes(member_token, missing_id)

    assert exc_info.value.status_code == 404


def test_frozen_context_invalid_extra_field_rejected() -> None:
    """ISTQB Negative Boundary: extra='forbid' rejects unexpected keys in FrozenContext JSON."""
    with pytest.raises(ValidationError):
        FrozenContext.model_validate_json(b'{"unexpected_schema_key": "forbid_me"}')
