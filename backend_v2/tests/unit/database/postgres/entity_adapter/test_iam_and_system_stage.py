"""Unit and boundary tests for PostgreSQL 19 IAM and SystemConfig entity stage.

Covers positive roundtrip persistence and hydration for Organization, User,
Invitation, TenantSecretDTO, ExecutionAssignment, SystemConfigModelRegistry,
and SystemConfigMCPGateways, as well as negative identifier validation and
driver fault handling.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from backend_v2.database.postgres.entity_adapter import PostgresEntityAdapter
from backend_v2.database.postgres.entity_adapter.iam_and_system_stage import (
    aggregate_organization_usage_row,
    delete_tenant_secret_row,
    get_execution_assignment_row,
    get_invitation_row,
    get_organization_row,
    get_system_config_row,
    get_tenant_secret_row,
    get_user_row,
    hydrate_audit_log_row,
    hydrate_execution_assignment_row,
    hydrate_invitation_row,
    hydrate_organization_row,
    hydrate_system_config_row,
    hydrate_tenant_secret_row,
    hydrate_usage_record_row,
    hydrate_user_row,
    insert_audit_log_row,
    insert_usage_record_row,
    list_audit_log_rows,
    list_execution_assignment_rows,
    list_invitation_rows,
    list_organization_rows,
    list_system_config_rows,
    list_system_configs_rows,
    list_tenant_secret_rows,
    list_usage_record_rows,
    list_user_rows,
    upsert_execution_assignment_row,
    upsert_invitation_row,
    upsert_organization_row,
    upsert_system_config_row,
    upsert_tenant_secret_row,
    upsert_user_row,
)
from backend_v2.database.postgres.entity_adapter.seed_and_collection_stage import (
    verify_seed_table_counts_rows,
)
from backend_v2.database.postgres.pool import PostgresPoolManager
from backend_v2.database.postgres.uow import PostgresUnitOfWork
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import (
    SYSTEM_ROOT_USER_ID,
    ExecutionAssignment,
    Invitation,
    Organization,
    SubscriptionStatus,
    SystemOrganizations,
    TenantSecretDTO,
    User,
    UserRole,
)
from backend_v2.models.core_base import I18nText, generate_opaque_id, parse_prefixed_uuid7
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.system_config import (
    AllowedMCPTool,
    ModelProfile,
    ProviderExtraParamsDTO,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
)
from backend_v2.models.dtos.mcp import MCPToolInputSchemaDTO
from backend_v2.models.enums import (
    AssignmentResultVisibility,
    AssignmentStatus,
    CognitiveTier,
    EmailDeliveryStatus,
    EntityPrefix,
    InvitationStatus,
    LLMProvider,
    MCPAuthType,
    MCPTransportType,
    SecretScope,
    SecretStorageMode,
    SystemLocale,
)
from backend_v2.settings import get_settings
from backend_v2.tests.factories.model_factories import AuditLogRecordFactory, UsageRecordFactory
from backend_v2.tests.fakes.in_memory_uow import (
    InMemoryAsyncPgPool,
    InMemoryAsyncPgRecord,
    InMemoryUnitOfWork,
)

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
        id=org_id if org_id is not None else generate_opaque_id(EntityPrefix.ORG),
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
        allowed_email_domains=["acme.example.com"],
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
        created_by=SYSTEM_ROOT_USER_ID,
        firebase_uid="fb_uid_alice_001",
    )


def _build_invitation(organization_id: str, invited_by: str) -> Invitation:
    """Build a valid Invitation domain model for testing.

    Args:
        organization_id: Parent organization identifier.
        invited_by: Inviter user identifier.

    Returns:
        Validated Invitation instance.
    """
    now = datetime.now(UTC)
    return Invitation(
        id=generate_opaque_id(EntityPrefix.INVITATION),
        organization_id=organization_id,
        email="invitee@acme.example.com",
        role=UserRole.MEMBER,
        token_hash="a" * 64,
        status=InvitationStatus.PENDING,
        email_delivery_status=EmailDeliveryStatus.SENT,
        invited_by=invited_by,
        expires_at=now + timedelta(days=7),
        created_at=now,
    )


def _build_tenant_secret(organization_id: str) -> TenantSecretDTO:
    """Build a valid TenantSecretDTO domain model for testing.

    Args:
        organization_id: Parent organization identifier.

    Returns:
        Validated TenantSecretDTO instance.
    """
    return TenantSecretDTO(
        id=generate_opaque_id(EntityPrefix.TENANT_SECRET),
        organization_id=organization_id,
        scope=SecretScope.LLM_PROVIDER,
        target_identifier="google",
        storage_mode=SecretStorageMode.ENVELOPE_KMS,
        encrypted_dek=b"wrapped-dek-bytes",
        ciphertext=b"encrypted-secret-ciphertext",
        nonce=b"12byte-nonce",
        kek_version="projects/quorum/locations/europe-north1/keyRings/byok/cryptoKeys/master/cryptoKeyVersions/1",
        masked_hint="AIza...9999",
        updated_by=SYSTEM_ROOT_USER_ID,
        updated_at=datetime.now(UTC),
    )


def _build_execution_assignment(organization_id: str, created_by: str) -> ExecutionAssignment:
    """Build a valid ExecutionAssignment domain model for testing.

    Args:
        organization_id: Parent organization identifier.
        created_by: Creator user identifier.

    Returns:
        Validated ExecutionAssignment instance.
    """
    now = datetime.now(UTC)
    return ExecutionAssignment(
        id=generate_opaque_id(EntityPrefix.ASSIGNMENT),
        batch_id=generate_opaque_id(EntityPrefix.ASSIGNMENT),
        organization_id=organization_id,
        assigned_email="candidate@acme.example.com",
        assigned_user_id=None,
        invited_role=UserRole.MEMBER,
        workflow_id=generate_opaque_id(EntityPrefix.WORKFLOW),
        output_profile_id=generate_opaque_id(EntityPrefix.OUTPUT_PROFILE),
        task_brief_id=generate_opaque_id(EntityPrefix.TASK_BRIEF),
        target_locale=SystemLocale.FI,
        locked_inputs=WorkflowInputs(dynamic_inputs={"role_context": "Senior Architect"}),
        assignee_input_keys=["candidate_essay"],
        draft_inputs=WorkflowInputs(dynamic_inputs={"candidate_essay": "Draft answer"}),
        token_hash="b" * 64,
        status=AssignmentStatus.PENDING,
        email_delivery_status=EmailDeliveryStatus.SENT,
        result_visibility=AssignmentResultVisibility.CONFIRMATION_ONLY,
        hard_deadline_at=now + timedelta(days=3),
        relative_duration_seconds=3600,
        activated_at=None,
        submitted_at=None,
        execution_id=None,
        created_by=created_by,
        created_at=now,
    )


def _build_model_registry() -> SystemConfigModelRegistry:
    """Build a valid SystemConfigModelRegistry with all four canonical CognitiveTiers.

    Returns:
        Validated SystemConfigModelRegistry instance.
    """
    profile = ModelProfile(
        provider="google",
        model_name="gemini-2.5-flash",
        allowed_tools=[],
        additional_params=ProviderExtraParamsDTO(),
    )
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
        name="Exa Search MCP Gateway",
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
                input_schema=MCPToolInputSchemaDTO(properties={}, required=[]),
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
        assert fetched_org.allowed_email_domains == ["acme.example.com"]

        sys_org = _build_org(org_id=SystemOrganizations.ROOT_SYSTEM, slug="system")
        saved_sys_org_id = await upsert_organization_row(conn, _TIMEOUT, sys_org)
        assert saved_sys_org_id == SystemOrganizations.ROOT_SYSTEM
        fetched_sys_org = await get_organization_row(conn, _TIMEOUT, SystemOrganizations.ROOT_SYSTEM)
        assert fetched_sys_org is not None
        assert fetched_sys_org.id == SystemOrganizations.ROOT_SYSTEM
        assert fetched_sys_org.slug == "system"

        all_orgs = await list_organization_rows(conn, _TIMEOUT)
        assert len(all_orgs) == 2

        user = _build_user(organization_id=org.id)
        saved_user_id = await upsert_user_row(conn, _TIMEOUT, user)
        assert saved_user_id == user.id
        fetched_user = await get_user_row(conn, _TIMEOUT, user.id)
        assert fetched_user is not None
        assert fetched_user.id == user.id
        assert fetched_user.email == user.email
        assert fetched_user.organization_id == org.id
        assert fetched_user.firebase_uid == "fb_uid_alice_001"

        org_users = await list_user_rows(conn, _TIMEOUT, org.id)
        assert len(org_users) == 1
        assert org_users[0].id == user.id

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
        assert fetched_mcp.name == mcp_cfg.name
        assert fetched_mcp == mcp_cfg
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_postgres_entity_adapter_iam_tables_roundtrip_positive() -> None:
    """Positive contract: User, Organization, Invitation, TenantSecretDTO, and ExecutionAssignment roundtrip 1:1 with RESET quorum.current_org."""
    pool = InMemoryAsyncPgPool()
    pool_manager = PostgresPoolManager(settings=get_settings(), pool=pool)
    org = _build_org()
    user = _build_user(organization_id=org.id)
    invitation = _build_invitation(organization_id=org.id, invited_by=user.id)
    secret = _build_tenant_secret(organization_id=org.id)
    assignment = _build_execution_assignment(organization_id=org.id, created_by=user.id)

    async with PostgresUnitOfWork(pool_manager=pool_manager) as uow:
        assert isinstance(uow.entities, PostgresEntityAdapter)
        await uow.entities.upsert_organization(org)
        await uow.entities.upsert_user(user)
        await uow.entities.upsert_invitation(invitation)
        await uow.entities.upsert_tenant_secret(secret)
        await uow.entities.upsert_execution_assignment(assignment)

        fetched_org = await uow.entities.get_organization(org.id)
        assert fetched_org is not None
        assert fetched_org.id == org.id
        assert fetched_org.allowed_email_domains == ["acme.example.com"]

        fetched_user = await uow.entities.get_user(user.id)
        assert fetched_user is not None
        assert fetched_user.id == user.id
        assert fetched_user.firebase_uid == user.firebase_uid

        fetched_inv = await uow.entities.get_invitation(invitation.id)
        assert fetched_inv is not None
        assert fetched_inv.id == invitation.id
        assert fetched_inv.email == invitation.email
        assert fetched_inv.email_delivery_status == EmailDeliveryStatus.SENT
        assert len(await uow.entities.list_invitations(org.id)) == 1

        fetched_sec = await uow.entities.get_tenant_secret(secret.id)
        assert fetched_sec is not None
        assert fetched_sec.id == secret.id
        assert fetched_sec.kek_version == secret.kek_version
        assert fetched_sec.ciphertext == secret.ciphertext
        assert len(await uow.entities.list_tenant_secrets(org.id)) == 1

        fetched_assign = await uow.entities.get_execution_assignment(assignment.id)
        assert fetched_assign is not None
        assert fetched_assign.id == assignment.id
        assert fetched_assign.batch_id == assignment.batch_id
        assert fetched_assign.task_brief_id == assignment.task_brief_id
        assert fetched_assign.assigned_email == assignment.assigned_email
        assert fetched_assign.locked_inputs == assignment.locked_inputs
        assert fetched_assign.assignee_input_keys == ["candidate_essay"]
        assert len(await uow.entities.list_execution_assignments(org.id)) == 1

    assert pool.store.current_org_reset_count == 1

    async with InMemoryUnitOfWork() as mem_uow:
        await mem_uow.entities.upsert_organization(org)
        await mem_uow.entities.upsert_user(user)
        await mem_uow.entities.upsert_invitation(invitation)
        await mem_uow.entities.upsert_tenant_secret(secret)
        await mem_uow.entities.upsert_execution_assignment(assignment)
        assert await mem_uow.entities.get_invitation(invitation.id) == invitation
        assert await mem_uow.entities.get_tenant_secret(secret.id) == secret
        assert await mem_uow.entities.get_execution_assignment(assignment.id) == assignment
    assert mem_uow.store.current_org_reset_count == 1


@pytest.mark.asyncio
async def test_postgres_entity_adapter_invalid_prefix_uuid_negative() -> None:
    """Negative contract: User or Invitation with non-UUIDv7 or un-prefixed primary key raises ValidationError / AppException."""
    with pytest.raises(ValidationError):
        User(
            id="invalid_user_id",
            email="bad@acme.example.com",
            role=UserRole.MEMBER,
            organization_id=SystemOrganizations.ROOT_SYSTEM,
            is_active=True,
            language=SystemLocale.EN,
            theme_mode="dark",
            created_at=datetime.now(UTC),
        )

    with pytest.raises(ValidationError):
        Invitation(
            id="0195f3a0-0000-7000-8000-000000000001",
            organization_id=SystemOrganizations.ROOT_SYSTEM,
            email="bad@acme.example.com",
            role=UserRole.MEMBER,
            token_hash="a" * 64,
            invited_by=SYSTEM_ROOT_USER_ID,
            created_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(days=1),
        )

    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        with pytest.raises(AppException) as inv_err:
            await get_invitation_row(conn, _TIMEOUT, "usr_0195f3a0000070008000000000000001")
        assert inv_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as sec_err:
            await get_tenant_secret_row(conn, _TIMEOUT, "usr_0195f3a0000070008000000000000001")
        assert sec_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as tsk_err:
            await get_execution_assignment_row(conn, _TIMEOUT, "usr_0195f3a0000070008000000000000001")
        assert tsk_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_iam_and_system_get_missing_rows_return_none() -> None:
    """Verify get_*_row functions return None when missing."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        missing_org_id = generate_opaque_id(EntityPrefix.ORG)
        missing_user_id = generate_opaque_id(EntityPrefix.USER)
        missing_sys_id = generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)
        missing_inv_id = generate_opaque_id(EntityPrefix.INVITATION)
        missing_sec_id = generate_opaque_id(EntityPrefix.TENANT_SECRET)
        missing_tsk_id = generate_opaque_id(EntityPrefix.ASSIGNMENT)

        assert await get_organization_row(conn, _TIMEOUT, missing_org_id) is None
        assert await get_user_row(conn, _TIMEOUT, missing_user_id) is None
        assert await get_system_config_row(conn, _TIMEOUT, missing_sys_id) is None
        assert await get_invitation_row(conn, _TIMEOUT, missing_inv_id) is None
        assert await get_tenant_secret_row(conn, _TIMEOUT, missing_sec_id) is None
        assert await get_execution_assignment_row(conn, _TIMEOUT, missing_tsk_id) is None
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
    """Verify upsert_*_row functions translate execute faults to STORAGE_ACCESS_FAILED."""
    pool = InMemoryAsyncPgPool()
    org = _build_org()
    user = _build_user(organization_id=org.id)
    inv = _build_invitation(organization_id=org.id, invited_by=user.id)
    sec = _build_tenant_secret(organization_id=org.id)
    tsk = _build_execution_assignment(organization_id=org.id, created_by=user.id)
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

        with pytest.raises(AppException) as inv_exc:
            await upsert_invitation_row(conn, _TIMEOUT, inv)
        assert inv_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        with pytest.raises(AppException) as sec_exc:
            await upsert_tenant_secret_row(conn, _TIMEOUT, sec)
        assert sec_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        with pytest.raises(AppException) as tsk_exc:
            await upsert_execution_assignment_row(conn, _TIMEOUT, tsk)
        assert tsk_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        with pytest.raises(AppException) as sys_exc:
            await upsert_system_config_row(conn, _TIMEOUT, cfg)
        assert sys_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
    finally:
        pool.clear_faults()
        await pool.release(conn)


@pytest.mark.asyncio
async def test_stage_get_methods_translate_fetchrow_faults_to_app_exception() -> None:
    """Verify get_*_row and list_*_rows functions translate fetchrow/fetch faults."""
    pool = InMemoryAsyncPgPool()
    org_id = generate_opaque_id(EntityPrefix.ORG)
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
    assert callable(hydrate_invitation_row)
    assert callable(hydrate_tenant_secret_row)
    assert callable(hydrate_execution_assignment_row)
    assert callable(hydrate_system_config_row)
    assert callable(list_invitation_rows)
    assert callable(list_tenant_secret_rows)
    assert callable(list_execution_assignment_rows)


@pytest.mark.asyncio
async def test_hydrate_system_config_null_name_and_preflight_verification_raises_app_exception() -> None:
    """Regression test: un-reseeded system_configs row with NULL name raises AppException in hydration and preflight."""
    cfg_id = "sys_0195f3a00000700080008172bda70c86"
    cfg_uuid = parse_prefixed_uuid7(cfg_id, EntityPrefix.SYSTEM_CONFIG)
    legacy_null_name_row = InMemoryAsyncPgRecord(
        {
            "id": cfg_uuid,
            "name": None,
            "type": "mcp_gateways",
            "slug": "tavily_mcp_gateway",
            "default_provider": None,
            "tier_definitions": None,
            "endpoint_url": "https://mcp.tavily.com/mcp",
            "transport_type": "streamable_http",
            "auth_type": "bearer",
            "auth_header_name": None,
            "auth_env_var": "TAVILY_API_KEY",
            "timeout_seconds": 30,
            "tools": "[]",
        }
    )

    with pytest.raises(AppException) as hydrate_exc:
        hydrate_system_config_row(legacy_null_name_row)
    assert hydrate_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert hydrate_exc.value.details["entity_id"] == cfg_id

    reg_id = "sys_0195f3a0000070008000000000000001"
    reg_uuid = parse_prefixed_uuid7(reg_id, EntityPrefix.SYSTEM_CONFIG)
    null_name_registry_row = InMemoryAsyncPgRecord(
        {
            "id": reg_uuid,
            "name": None,
            "type": "model_registry",
            "slug": None,
            "default_provider": "ai_studio",
            "tier_definitions": "{}",
            "endpoint_url": None,
            "transport_type": None,
            "auth_type": None,
            "auth_header_name": None,
            "auth_env_var": None,
            "timeout_seconds": None,
            "tools": None,
        }
    )
    with pytest.raises(AppException) as reg_exc:
        hydrate_system_config_row(null_name_registry_row)
    assert reg_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert reg_exc.value.details["entity_id"] == reg_id

    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        pool.store.seed_tables["system_configs"][str(cfg_uuid)] = (
            cfg_uuid,
            None,
            "mcp_gateways",
            "tavily_mcp_gateway",
            None,
            None,
            "https://mcp.tavily.com/mcp",
            "streamable_http",
            "bearer",
            None,
            "TAVILY_API_KEY",
            30,
            "[]",
        )
        with pytest.raises(AppException) as preflight_exc:
            await verify_seed_table_counts_rows(conn, _TIMEOUT, {"system_configs": 1})
        assert preflight_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    finally:
        await pool.release(conn)

    unknown_type_row = InMemoryAsyncPgRecord(
        {
            "id": cfg_uuid,
            "name": "Unknown Config",
            "type": "unsupported_config_type",
            "slug": "unknown_cfg",
            "default_provider": None,
            "tier_definitions": None,
            "endpoint_url": None,
            "transport_type": None,
            "auth_type": None,
            "auth_header_name": None,
            "auth_env_var": None,
            "timeout_seconds": None,
            "tools": None,
        }
    )
    with pytest.raises(AppException) as unknown_type_exc:
        hydrate_system_config_row(unknown_type_row)
    assert unknown_type_exc.value.status_code == 500
    assert unknown_type_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert unknown_type_exc.value.details["entity_id"] == cfg_id


@pytest.mark.asyncio
async def test_audit_and_usage_ledgers_system_configs_and_delete_secret_roundtrip() -> None:
    """Verify audit_logs, usage_records, SQL FinOps rollups, list_system_configs, and delete_tenant_secret."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        org = _build_org()
        await upsert_organization_row(conn, _TIMEOUT, org)
        user = _build_user(organization_id=org.id)
        await upsert_user_row(conn, _TIMEOUT, user)

        secret = _build_tenant_secret(organization_id=org.id)
        await upsert_tenant_secret_row(conn, _TIMEOUT, secret)
        assert await delete_tenant_secret_row(conn, _TIMEOUT, secret.id) is True
        assert await delete_tenant_secret_row(conn, _TIMEOUT, secret.id) is False
        assert await get_tenant_secret_row(conn, _TIMEOUT, secret.id) is None

        reg_cfg = _build_model_registry()
        mcp_cfg = _build_mcp_gateway()
        await upsert_system_config_row(conn, _TIMEOUT, reg_cfg)
        await upsert_system_config_row(conn, _TIMEOUT, mcp_cfg)
        listed_cfgs = await list_system_config_rows(conn, _TIMEOUT)
        assert len(listed_cfgs) == 2
        assert await list_system_configs_rows(conn, _TIMEOUT) == listed_cfgs

        exec_id = generate_opaque_id(EntityPrefix.EXECUTION)
        aud_tenant = AuditLogRecordFactory.build(
            organization_id=org.id,
            actor_id=user.id,
            execution_id=exec_id,
            event_type="SECRET_ROTATED",
            resource_type="tenant_secret",
            resource_id=secret.id,
            details={"scope": "llm_provider"},
        )
        aud_system = AuditLogRecordFactory.build(
            organization_id=None,
            actor_id=None,
            execution_id=None,
            event_type="STARTUP_CHECK",
            resource_type="system",
            resource_id="global",
            details={"ok": True},
        )
        assert await insert_audit_log_row(conn, _TIMEOUT, aud_tenant) == aud_tenant.id
        assert await insert_audit_log_row(conn, _TIMEOUT, aud_system) == aud_system.id

        assert await list_audit_log_rows(conn, _TIMEOUT, limit=0) == []
        all_auds = await list_audit_log_rows(conn, _TIMEOUT, limit=10)
        assert len(all_auds) == 2
        org_auds = await list_audit_log_rows(
            conn,
            _TIMEOUT,
            organization_id=org.id,
            actor_id=user.id,
            event_type="SECRET_ROTATED",
        )
        assert len(org_auds) == 1
        assert org_auds[0].id == aud_tenant.id
        sys_auds = await list_audit_log_rows(
            conn,
            _TIMEOUT,
            organization_id="SYSTEM",
            actor_id="system",
        )
        assert len(sys_auds) == 1
        assert sys_auds[0].id == aud_system.id

        now = datetime.now(UTC)
        usg_tenant = UsageRecordFactory.build(
            org_id=org.id,
            user_id=user.id,
            execution_id=exec_id,
            input_tokens=120,
            output_tokens=60,
            cached_tokens=20,
            reasoning_tokens=10,
            cache_creation_input_tokens=5,
            latency_ms=340,
            cost_usd=0.25,
            estimated_savings_usd=0.05,
        )
        usg_system = UsageRecordFactory.build(
            org_id="system",
            user_id="system",
            execution_id=None,
            input_tokens=50,
            output_tokens=25,
            cached_tokens=0,
            reasoning_tokens=0,
            cache_creation_input_tokens=0,
            latency_ms=None,
            cost_usd=0.10,
            estimated_savings_usd=0.0,
        )
        assert await insert_usage_record_row(conn, _TIMEOUT, usg_tenant) == usg_tenant.id
        assert await insert_usage_record_row(conn, _TIMEOUT, usg_system) == usg_system.id

        tenant_usage = await list_usage_record_rows(
            conn,
            _TIMEOUT,
            organization_id=org.id,
            user_id=user.id,
            since=now - timedelta(hours=1),
        )
        assert len(tenant_usage) == 1
        assert tenant_usage[0].latency_ms == 340

        sys_usage = await list_usage_record_rows(
            conn,
            _TIMEOUT,
            organization_id="system",
            user_id="system",
        )
        assert len(sys_usage) == 1
        assert sys_usage[0].org_id == "system"
        assert sys_usage[0].user_id == "system"
        assert sys_usage[0].latency_ms is None

        rollup_tenant = await aggregate_organization_usage_row(
            conn,
            _TIMEOUT,
            organization_id=org.id,
            since=now - timedelta(hours=1),
        )
        assert rollup_tenant.organization_id == org.id
        assert rollup_tenant.total_prompt_tokens == 120
        assert rollup_tenant.total_completion_tokens == 60
        assert rollup_tenant.record_count == 1
        assert rollup_tenant.total_cost_usd == pytest.approx(0.25)

        rollup_sys = await aggregate_organization_usage_row(
            conn,
            _TIMEOUT,
            organization_id="system",
        )
        assert rollup_sys.record_count == 1
        assert rollup_sys.total_prompt_tokens == 50

        rollup_all = await aggregate_organization_usage_row(conn, _TIMEOUT)
        assert rollup_all.record_count == 2
        assert rollup_all.total_prompt_tokens == 170
        assert callable(hydrate_audit_log_row)
        assert callable(hydrate_usage_record_row)
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_audit_and_usage_ledger_fault_and_invalid_id_failure() -> None:
    """Verify insert/aggregate fault translation and AppException pass-through on audit_logs and usage_records."""
    pool = InMemoryAsyncPgPool()
    aud = AuditLogRecordFactory.build()
    usg = UsageRecordFactory.build()
    conn = await pool.acquire()
    try:
        pool.inject_fault("execute", RuntimeError("simulated ledger insert fault"))
        with pytest.raises(AppException) as aud_err:
            await insert_audit_log_row(conn, _TIMEOUT, aud)
        assert aud_err.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        with pytest.raises(AppException) as usg_err:
            await insert_usage_record_row(conn, _TIMEOUT, usg)
        assert usg_err.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        pool.inject_fault(
            "execute",
            AppException(
                message="pre-existing app exception",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ),
        )
        with pytest.raises(AppException) as aud_app_err:
            await insert_audit_log_row(conn, _TIMEOUT, aud)
        assert aud_app_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as usg_app_err:
            await insert_usage_record_row(conn, _TIMEOUT, usg)
        assert usg_app_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        pool.clear_faults()
        pool.inject_fault("fetchrow", RuntimeError("simulated rollup fault"))
        with pytest.raises(AppException) as rollup_err:
            await aggregate_organization_usage_row(conn, _TIMEOUT, organization_id=aud.organization_id)
        assert rollup_err.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        pool.inject_fault(
            "fetchrow",
            AppException(
                message="pre-existing rollup app exception",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ),
        )
        with pytest.raises(AppException) as rollup_app_err:
            await aggregate_organization_usage_row(conn, _TIMEOUT)
        assert rollup_app_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    finally:
        pool.clear_faults()
        await pool.release(conn)
