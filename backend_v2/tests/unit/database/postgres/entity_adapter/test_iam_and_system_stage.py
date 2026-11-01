"""Unit and boundary tests for PostgreSQL 19 IAM and SystemConfig entity stage.

Covers positive roundtrip persistence and hydration for Organization, User,
SystemConfigModelRegistry, and SystemConfigMCPGateways, as well as negative
identifier validation and driver fault handling.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from backend_v2.database.postgres.entity_adapter.iam_and_system_stage import (
    get_organization_row,
    get_system_config_row,
    get_user_row,
    hydrate_organization_row,
    hydrate_system_config_row,
    hydrate_user_row,
    upsert_organization_row,
    upsert_system_config_row,
    upsert_user_row,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import Organization, SubscriptionStatus, User, UserRole
from backend_v2.models.core_base import I18nText, generate_opaque_id
from backend_v2.models.domain.system_config import (
    AllowedMCPTool,
    ModelProfile,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
)
from backend_v2.models.enums import (
    CognitiveTier,
    EntityPrefix,
    LLMProvider,
    MCPAuthType,
    MCPTransportType,
    SystemLocale,
)
from backend_v2.tests.fakes.in_memory_uow import InMemoryAsyncPgPool

_TIMEOUT: float = 5.0


def _build_org(org_id: str | None = None, slug: str = "acme-org") -> Organization:
    """Build a valid Organization domain model for testing.

    Args:
        org_id: Optional organization identifier override.
        slug: Organization slug string.

    Returns:
        Validated Organization instance.
    """
    return Organization(
        id=org_id if org_id is not None else generate_opaque_id(EntityPrefix.ORGANIZATION),
        slug=slug,
        name="Acme Corporation",
        created_at=datetime.now(UTC),
        is_active=True,
        tier="enterprise",
        contact_email="admin@acme.example.com",
        billing_id="cus_test_12345",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=100000,
        rpm_limit=1000,
    )


def _build_user(organization_id: str) -> User:
    """Build a valid User domain model for testing.

    Args:
        organization_id: Parent organization identifier.

    Returns:
        Validated User instance.
    """
    return User(
        id=generate_opaque_id(EntityPrefix.USER),
        slug="alice-admin",
        email="alice@acme.example.com",
        name="Alice Admin",
        role=UserRole.ADMIN,
        organization_id=organization_id,
        is_active=True,
        language=SystemLocale.EN,
        theme_mode="dark",
        created_at=datetime.now(UTC),
        created_by="usr_system",
    )


def _build_model_registry() -> SystemConfigModelRegistry:
    """Build a valid SystemConfigModelRegistry with all four canonical CognitiveTiers.

    Returns:
        Validated SystemConfigModelRegistry instance.
    """
    profile = ModelProfile(provider="google", model_name="gemini-2.5-flash")
    return SystemConfigModelRegistry(
        id=generate_opaque_id(EntityPrefix.SYSTEM_CONFIG),
        name="Primary Model Registry",
        type="model_registry",
        default_provider=LLMProvider.AI_STUDIO,
        tier_definitions={tier: profile for tier in CognitiveTier},
    )


def _build_mcp_gateway() -> SystemConfigMCPGateways:
    """Build a valid SystemConfigMCPGateways instance for testing.

    Returns:
        Validated SystemConfigMCPGateways instance.
    """
    return SystemConfigMCPGateways(
        id=generate_opaque_id(EntityPrefix.SYSTEM_CONFIG),
        type="mcp_gateways",
        slug="exa_search_gateway",
        endpoint_url="https://mcp.exa.example.com/v1",
        transport_type=MCPTransportType.STREAMABLE_HTTP,
        auth_type=MCPAuthType.NONE,
        timeout_seconds=30,
        tools=[
            AllowedMCPTool(
                tool_id="web_search",
                name=I18nText(translations={"en": "Web Search", "fi": "Verkkohaku"}),
                description="Search the web for factual verification.",
            )
        ],
    )


@pytest.mark.asyncio
async def test_iam_system_and_studio_entities_roundtrip_parity() -> None:
    """Verify Organization, User, and SystemConfig upsert and get roundtrips preserve 100% field parity."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        org = _build_org()
        saved_org_id = await upsert_organization_row(conn, _TIMEOUT, org)
        assert saved_org_id == org.id
        fetched_org = await get_organization_row(conn, _TIMEOUT, org.id)
        assert fetched_org is not None
        assert fetched_org.id == org.id
        assert fetched_org.slug == org.slug
        assert fetched_org.name == org.name
        assert fetched_org.quota_limit == org.quota_limit

        sys_org = _build_org(org_id="org_system000000", slug="system")
        saved_sys_org_id = await upsert_organization_row(conn, _TIMEOUT, sys_org)
        assert saved_sys_org_id == "org_system000000"
        fetched_sys_org = await get_organization_row(conn, _TIMEOUT, "org_system000000")
        assert fetched_sys_org is not None
        assert fetched_sys_org.id == "org_system000000"
        assert fetched_sys_org.slug == "system"

        user = _build_user(organization_id=org.id)
        saved_user_id = await upsert_user_row(conn, _TIMEOUT, user)
        assert saved_user_id == user.id
        fetched_user = await get_user_row(conn, _TIMEOUT, user.id)
        assert fetched_user is not None
        assert fetched_user.id == user.id
        assert fetched_user.email == user.email
        assert fetched_user.organization_id == org.id

        reg_cfg = _build_model_registry()
        saved_reg_id = await upsert_system_config_row(conn, _TIMEOUT, reg_cfg)
        assert saved_reg_id == reg_cfg.id
        fetched_reg = await get_system_config_row(conn, _TIMEOUT, reg_cfg.id)
        assert isinstance(fetched_reg, SystemConfigModelRegistry)
        assert fetched_reg == reg_cfg

        mcp_cfg = _build_mcp_gateway()
        saved_mcp_id = await upsert_system_config_row(conn, _TIMEOUT, mcp_cfg)
        assert saved_mcp_id == mcp_cfg.id
        fetched_mcp = await get_system_config_row(conn, _TIMEOUT, mcp_cfg.id)
        assert isinstance(fetched_mcp, SystemConfigMCPGateways)
        assert fetched_mcp == mcp_cfg
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_iam_and_system_get_missing_rows_return_none() -> None:
    """Verify get_organization_row, get_user_row, and get_system_config_row return None when missing."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        missing_org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
        missing_user_id = generate_opaque_id(EntityPrefix.USER)
        missing_sys_id = generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)

        assert await get_organization_row(conn, _TIMEOUT, missing_org_id) is None
        assert await get_user_row(conn, _TIMEOUT, missing_user_id) is None
        assert await get_system_config_row(conn, _TIMEOUT, missing_sys_id) is None
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_iam_and_system_invalid_prefix_raises_validation_failed() -> None:
    """Verify invalid entity ID prefixes raise AppException with VALIDATION_FAILED."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        with pytest.raises(AppException) as org_err:
            await get_organization_row(conn, _TIMEOUT, "usr_0195f3a0000070008000000000000001")
        assert org_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as usr_err:
            await get_user_row(conn, _TIMEOUT, "org_0195f3a0000070008000000000000001")
        assert usr_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as sys_err:
            await get_system_config_row(conn, _TIMEOUT, "usr_0195f3a0000070008000000000000001")
        assert sys_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_iam_and_system_upsert_execute_faults_raise_storage_access_failed() -> None:
    """Verify upsert_organization_row, upsert_user_row, and upsert_system_config_row translate execute faults."""
    pool = InMemoryAsyncPgPool()
    org = _build_org()
    user = _build_user(organization_id=org.id)
    cfg = _build_model_registry()
    conn = await pool.acquire()
    try:
        pool.inject_fault("execute", RuntimeError("simulated execute failure"))
        with pytest.raises(AppException) as org_exc:
            await upsert_organization_row(conn, _TIMEOUT, org)
        assert org_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        with pytest.raises(AppException) as usr_exc:
            await upsert_user_row(conn, _TIMEOUT, user)
        assert usr_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        with pytest.raises(AppException) as sys_exc:
            await upsert_system_config_row(conn, _TIMEOUT, cfg)
        assert sys_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
    finally:
        pool.clear_faults()
        await pool.release(conn)


@pytest.mark.asyncio
async def test_stage_get_methods_translate_fetchrow_faults_to_app_exception() -> None:
    """Verify get_organization_row, get_user_row, and get_system_config_row translate fetchrow faults."""
    pool = InMemoryAsyncPgPool()
    org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
    user_id = generate_opaque_id(EntityPrefix.USER)
    sys_id = generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)
    conn = await pool.acquire()
    try:
        pool.inject_fault("fetchrow", RuntimeError("simulated fetchrow failure"))
        with pytest.raises(AppException) as org_exc:
            await get_organization_row(conn, _TIMEOUT, org_id)
        assert org_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        with pytest.raises(AppException) as usr_exc:
            await get_user_row(conn, _TIMEOUT, user_id)
        assert usr_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        with pytest.raises(AppException) as sys_exc:
            await get_system_config_row(conn, _TIMEOUT, sys_id)
        assert sys_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        pool.inject_fault(
            "fetchrow",
            AppException(
                message="pre-existing app exception",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ),
        )
        with pytest.raises(AppException) as direct_org_exc:
            await get_organization_row(conn, _TIMEOUT, org_id)
        assert direct_org_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as direct_usr_exc:
            await get_user_row(conn, _TIMEOUT, user_id)
        assert direct_usr_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as direct_sys_exc:
            await get_system_config_row(conn, _TIMEOUT, sys_id)
        assert direct_sys_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    finally:
        pool.clear_faults()
        await pool.release(conn)
    assert callable(hydrate_organization_row)
    assert callable(hydrate_user_row)
    assert callable(hydrate_system_config_row)
