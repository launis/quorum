"""Unit tests for SecretService Dual-Tier BYOK Secret Governance and Cross-Tenant Isolation."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

import pytest
from pydantic import SecretStr

from backend_v2.api.routers.iam.organizations import (
    delete_organization_secret,
    list_organization_secrets,
    upsert_organization_secret,
)
from backend_v2.exceptions import (
    AppException,
    ConfigurationError,
    ErrorCodes,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from backend_v2.llm.provider.litellm_provider import LiteLLMProvider
from backend_v2.llm.provider.provider_factory import LLMFactory
from backend_v2.models.auth import (
    ResolvedCredentialDTO,
    SystemOrganizations,
    TenantSecretCreateDTO,
    TenantSecretDTO,
    TokenData,
)
from backend_v2.models.core_base import I18nText, generate_opaque_id
from backend_v2.models.domain.system_config import AllowedMCPTool, SystemConfigMCPGateways
from backend_v2.models.dtos.mcp import (
    MCPToolInputSchemaDTO,
    MCPToolSchemaPropertyDTO,
)
from backend_v2.models.enums import (
    EntityPrefix,
    JSONSchemaPropertyType,
    LLMProvider,
    MCPAuthType,
    MCPTransportType,
    SecretScope,
    SecretStorageMode,
    ToolCapability,
    UserRole,
)
from backend_v2.services.auth.secret_service import (
    AuditLoggerProtocol,
    CloudKMSKeyWrapperProtocol,
    CloudSecretManagerFetcherProtocol,
    SecretService,
    get_secret_service,
)
from backend_v2.services.mcp.dispatcher import ToolDispatcher
from backend_v2.services.mcp.generic_mcp_client import GenericMCPClient
from backend_v2.settings import get_settings
from backend_v2.tests.fakes.in_memory_uow import InMemoryUnitOfWork
from scripts._ast_guardrails import scan_source_code_for_guardrails


class _RecordingAuditLogger(AuditLoggerProtocol):
    """In-memory fake audit logger recording emitted security events."""

    def __init__(self) -> None:
        """Initialize the empty audit event list."""
        self.events: list[tuple[str, str, str, str, dict[str, str]]] = []

    async def log_event(
        self,
        *,
        actor_id: str,
        action: str,
        organization_id: str,
        target_id: str,
        details: dict[str, str],
    ) -> None:
        """Append the audit event tuple for test verification."""
        self.events.append((actor_id, action, organization_id, target_id, dict(details)))


class _FakeKMSWrapper(CloudKMSKeyWrapperProtocol):
    """Deterministic fake Cloud KMS key wrapper for unit tests."""

    def __init__(self, *, fail_encrypt: bool = False, fail_decrypt: bool = False, bad_length: bool = False) -> None:
        """Initialize the fake KMS wrapper with optional fault flags."""
        self._fail_encrypt = fail_encrypt
        self._fail_decrypt = fail_decrypt
        self._bad_length = bad_length

    async def encrypt_dek(self, dek: bytes, kek_version: str) -> bytes:
        """Simulate KMS DEK encryption by prefixing the KEK version."""
        if self._fail_encrypt:
            raise RuntimeError("Simulated Cloud KMS encrypt failure")
        return f"kms:{kek_version}:".encode() + dek

    async def decrypt_dek(self, encrypted_dek: bytes, kek_version: str) -> bytes:
        """Simulate KMS DEK decryption and validate the KEK version prefix."""
        if self._fail_decrypt:
            raise RuntimeError("Simulated Cloud KMS decrypt failure")
        if self._bad_length:
            return b"short"
        prefix = f"kms:{kek_version}:".encode()
        if not encrypted_dek.startswith(prefix):
            raise ValueError("KEK version mismatch")
        return encrypted_dek[len(prefix) :]


class _FakeSecretManagerFetcher(CloudSecretManagerFetcherProtocol):
    """Deterministic fake GCP Secret Manager version fetcher for unit tests."""

    def __init__(self, secrets_by_uri: dict[str, str], *, delay_seconds: float = 0.0) -> None:
        """Initialize the fake Secret Manager mapping."""
        self._secrets_by_uri = secrets_by_uri
        self._delay_seconds = delay_seconds

    async def access_secret_version(self, version_uri: str) -> str:
        """Return the mapped secret version string or raise KeyError if missing."""
        if self._delay_seconds > 0.0:
            await asyncio.sleep(self._delay_seconds)
        if version_uri not in self._secrets_by_uri:
            raise KeyError(f"Secret version URI not found: {version_uri}")
        return self._secrets_by_uri[version_uri]


def _make_token_data(
    *,
    role: UserRole = UserRole.ADMIN,
    organization_id: str | None = None,
) -> TokenData:
    """Create a valid TokenData instance with canonical UUIDv7 identifiers."""
    resolved_org = organization_id if organization_id is not None else generate_opaque_id(EntityPrefix.ORGANIZATION)
    return TokenData(
        id=generate_opaque_id(EntityPrefix.USER),
        email="admin@tenant.example.com",
        role=role,
        organization_id=resolved_org,
        jti=generate_opaque_id(EntityPrefix.EXECUTION),
    )


def _make_mcp_gateway(
    *,
    auth_type: MCPAuthType = MCPAuthType.BEARER,
    auth_env_var: str | None = "MCP_GATEWAY_TOKEN",
) -> SystemConfigMCPGateways:
    """Create a valid SystemConfigMCPGateways instance for unit testing."""
    return SystemConfigMCPGateways(
        id=generate_opaque_id(EntityPrefix.SYSTEM_CONFIG),
        name="Enterprise Search Gateway",
        slug="enterprise_search",
        endpoint_url="https://mcp.example.com/v1/mcp",
        transport_type=MCPTransportType.STREAMABLE_HTTP,
        auth_type=auth_type,
        auth_env_var=auth_env_var,
        timeout_seconds=10,
        tools=[],
    )


@pytest.mark.asyncio
async def test_secret_service_envelope_kms_roundtrip_positive() -> None:
    """Positive: Verify ENVELOPE_KMS encrypts via AES-256-GCM DEK + KEK, stores masked_hint, and resolves SecretStr."""
    uow = InMemoryUnitOfWork()
    audit_logger = _RecordingAuditLogger()
    service = SecretService(entity_adapter=uow.entities, audit_service=audit_logger)

    org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
    admin_token = _make_token_data(role=UserRole.ADMIN, organization_id=org_id)
    create_dto = TenantSecretCreateDTO(
        scope=SecretScope.LLM_PROVIDER,
        target_identifier=LLMProvider.OPENAI.value,
        plaintext_secret=SecretStr("sk-proj-tenant-secret-abcd"),
        storage_mode=SecretStorageMode.ENVELOPE_KMS,
    )

    response = await service.upsert_tenant_secret(
        initiator=admin_token,
        organization_id=org_id,
        payload=create_dto,
        kek_version="kms-kek-v2",
    )

    assert response.organization_id == org_id
    assert response.scope == SecretScope.LLM_PROVIDER
    assert response.target_identifier == LLMProvider.OPENAI.value
    assert response.storage_mode == SecretStorageMode.ENVELOPE_KMS
    assert response.configured is True
    assert response.masked_hint == "****abcd"
    assert response.kek_version == "kms-kek-v2"

    persisted = await uow.entities.get_tenant_secret(response.id)
    assert persisted is not None
    assert persisted.encrypted_dek is not None
    assert persisted.ciphertext is not None
    assert persisted.nonce is not None
    assert len(persisted.nonce) == 12
    assert b"sk-proj-tenant-secret-abcd" not in persisted.ciphertext

    resolved = await service.resolve_llm_key(organization_id=org_id, provider=LLMProvider.OPENAI)
    assert resolved.organization_id == org_id
    assert resolved.scope == SecretScope.LLM_PROVIDER
    assert resolved.target_identifier == LLMProvider.OPENAI.value
    assert resolved.is_tenant_byok is True
    assert resolved.secret_value.get_secret_value() == "sk-proj-tenant-secret-abcd"
    assert "sk-proj-tenant-secret-abcd" not in repr(resolved)

    assert len(audit_logger.events) == 1
    actor_id, action, evt_org, target_id, details = audit_logger.events[0]
    assert actor_id == admin_token.id
    assert action == "TENANT_SECRET_UPSERTED"
    assert evt_org == org_id
    assert target_id == response.id
    assert details["masked_hint"] == "****abcd"
    assert "sk-proj-tenant-secret-abcd" not in str(details)


@pytest.mark.asyncio
async def test_byok_cross_tenant_isolation_negative(monkeypatch: pytest.MonkeyPatch) -> None:
    """Negative: Verify Tenant B cannot resolve Tenant A's BYOK key and fails fast when platform key is unset."""
    clean_settings = get_settings().model_copy(
        update={"openai_api_key": None, "google_api_key": None, "anthropic_api_key": None}
    )
    monkeypatch.setattr("backend_v2.services.auth.secret_service.get_settings", lambda: clean_settings)

    uow = InMemoryUnitOfWork()
    service = SecretService(entity_adapter=uow.entities)

    tenant_a_org = generate_opaque_id(EntityPrefix.ORGANIZATION)
    tenant_b_org = generate_opaque_id(EntityPrefix.ORGANIZATION)
    admin_a = _make_token_data(role=UserRole.ADMIN, organization_id=tenant_a_org)

    await service.upsert_tenant_secret(
        initiator=admin_a,
        organization_id=tenant_a_org,
        payload=TenantSecretCreateDTO(
            scope=SecretScope.LLM_PROVIDER,
            target_identifier=LLMProvider.OPENAI.value,
            plaintext_secret=SecretStr("sk-tenant-a-exclusive-9999"),
            storage_mode=SecretStorageMode.ENVELOPE_KMS,
        ),
    )

    with pytest.raises(ConfigurationError) as exc_info:
        await service.resolve_llm_key(organization_id=tenant_b_org, provider=LLMProvider.OPENAI)

    assert exc_info.value.details["error_code"] == ErrorCodes.SECRET_RESOLUTION_FAILED.value
    assert exc_info.value.details["organization_id"] == tenant_b_org


@pytest.mark.asyncio
async def test_secret_service_corrupted_ciphertext_no_fallback_negative(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Negative: Verify corrupted ciphertext or invalid encrypted_dek raises ConfigurationError with zero fallback."""
    platform_settings = get_settings().model_copy(
        update={
            "openai_api_key": "sk-platform-global-fallback-key",
            "google_api_key": "ai-studio-global-fallback-key",
        }
    )
    monkeypatch.setattr("backend_v2.services.auth.secret_service.get_settings", lambda: platform_settings)

    uow = InMemoryUnitOfWork()
    service = SecretService(entity_adapter=uow.entities)

    tenant_a_org = generate_opaque_id(EntityPrefix.ORGANIZATION)
    admin_a = _make_token_data(role=UserRole.ADMIN, organization_id=tenant_a_org)

    created = await service.upsert_tenant_secret(
        initiator=admin_a,
        organization_id=tenant_a_org,
        payload=TenantSecretCreateDTO(
            scope=SecretScope.LLM_PROVIDER,
            target_identifier=LLMProvider.OPENAI.value,
            plaintext_secret=SecretStr("sk-tenant-a-secret-1234"),
            storage_mode=SecretStorageMode.ENVELOPE_KMS,
        ),
    )

    original_record = await uow.entities.get_tenant_secret(created.id)
    assert original_record is not None
    corrupted_record = original_record.model_copy(update={"ciphertext": b"corrupted-aes-gcm-bytes"})
    await uow.entities.upsert_tenant_secret(corrupted_record)

    with pytest.raises(ConfigurationError) as exc_info:
        await service.resolve_llm_key(organization_id=tenant_a_org, provider=LLMProvider.OPENAI)

    assert exc_info.value.details["error_code"] == ErrorCodes.SECRET_RESOLUTION_FAILED.value
    assert exc_info.value.details["secret_id"] == created.id

    corrupted_dek_record = original_record.model_copy(update={"encrypted_dek": b"bad-dek"})
    await uow.entities.upsert_tenant_secret(corrupted_dek_record)

    with pytest.raises(ConfigurationError) as dek_exc:
        await service.resolve_llm_key(organization_id=tenant_a_org, provider=LLMProvider.OPENAI)

    assert dek_exc.value.details["error_code"] == ErrorCodes.SECRET_RESOLUTION_FAILED.value


@pytest.mark.asyncio
async def test_secret_service_cloud_secret_manager_and_mcp_resolution_positive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Positive: Verify CLOUD_SECRET_MANAGER URI resolution, in-place rotation, deletion, and MCP fallback."""
    monkeypatch.setenv("MCP_PLATFORM_TOKEN", "mcp-platform-token-xyz")
    uow = InMemoryUnitOfWork()
    audit_logger = _RecordingAuditLogger()
    uri = "projects/quorum-prod/secrets/org-mcp-token/versions/3"
    fetcher = _FakeSecretManagerFetcher({uri: "mcp-byok-secret-7890"})
    kms = _FakeKMSWrapper()
    service = SecretService(
        entity_adapter=uow.entities,
        audit_service=audit_logger,
        kms_wrapper=kms,
        secret_manager_fetcher=fetcher,
    )

    org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
    root_token = _make_token_data(role=UserRole.ROOT, organization_id=SystemOrganizations.ROOT_SYSTEM)
    gateway = _make_mcp_gateway(auth_type=MCPAuthType.BEARER, auth_env_var="MCP_PLATFORM_TOKEN")

    platform_cred = await service.resolve_mcp_credential(organization_id=org_id, gateway=gateway)
    assert platform_cred.is_tenant_byok is False
    assert platform_cred.secret_value.get_secret_value() == "mcp-platform-token-xyz"

    created = await service.upsert_tenant_secret(
        initiator=root_token,
        organization_id=org_id,
        payload=TenantSecretCreateDTO(
            scope=SecretScope.MCP_GATEWAY,
            target_identifier=gateway.id,
            plaintext_secret=SecretStr(uri),
            storage_mode=SecretStorageMode.CLOUD_SECRET_MANAGER,
        ),
    )
    assert created.storage_mode == SecretStorageMode.CLOUD_SECRET_MANAGER

    byok_cred = await service.resolve_mcp_credential(organization_id=org_id, gateway=gateway)
    assert byok_cred.is_tenant_byok is True
    assert byok_cred.secret_value.get_secret_value() == "mcp-byok-secret-7890"

    rotated = await service.upsert_tenant_secret(
        initiator=root_token,
        organization_id=org_id,
        payload=TenantSecretCreateDTO(
            scope=SecretScope.MCP_GATEWAY,
            target_identifier=gateway.id,
            plaintext_secret=SecretStr("short"),
            storage_mode=SecretStorageMode.ENVELOPE_KMS,
        ),
        kek_version="kms-v3",
    )
    assert rotated.id == created.id
    assert rotated.masked_hint == "****hort"

    listed = await service.list_tenant_secrets(initiator=root_token, organization_id=org_id)
    assert len(listed) == 1
    assert listed[0].id == created.id

    deleted = await service.delete_tenant_secret(
        initiator=root_token,
        organization_id=org_id,
        secret_id=created.id,
    )
    assert deleted is True
    assert await uow.entities.get_tenant_secret(created.id) is None
    assert await service.list_tenant_secrets(initiator=root_token, organization_id=org_id) == []
    assert audit_logger.events[-1][1] == "TENANT_SECRET_DELETED"

    vertex_cred = await service.resolve_llm_key(organization_id=org_id, provider=LLMProvider.VERTEX_AI)
    assert vertex_cred.is_tenant_byok is False
    assert vertex_cred.secret_value.get_secret_value() == "vertex-adc-managed"
    assert isinstance(get_secret_service(), SecretService)


@pytest.mark.asyncio
async def test_secret_service_rbac_and_validation_failures_negative() -> None:
    """Negative: Verify RBAC cross-tenant rejection, empty secret rejection, invalid URI, and missing secret delete."""
    uow = InMemoryUnitOfWork()
    service = SecretService(entity_adapter=uow.entities)

    org_a = generate_opaque_id(EntityPrefix.ORGANIZATION)
    org_b = generate_opaque_id(EntityPrefix.ORGANIZATION)
    admin_a = _make_token_data(role=UserRole.ADMIN, organization_id=org_a)
    member_a = _make_token_data(role=UserRole.MEMBER, organization_id=org_a)

    # 1. Cross-tenant ADMIN attempting to list or upsert in org_b
    with pytest.raises(PermissionDeniedError) as perm_exc:
        await service.list_tenant_secrets(initiator=admin_a, organization_id=org_b)
    assert perm_exc.value.details["error_code"] == ErrorCodes.PERMISSION_DENIED.value

    # 2. Non-admin MEMBER attempting to manage secrets in own org
    with pytest.raises(PermissionDeniedError) as member_exc:
        await service.list_tenant_secrets(initiator=member_a, organization_id=org_a)
    assert member_exc.value.details["error_code"] == ErrorCodes.PERMISSION_DENIED.value

    # 3. Whitespace-only plaintext secret
    with pytest.raises(AppException) as empty_exc:
        await service.upsert_tenant_secret(
            initiator=admin_a,
            organization_id=org_a,
            payload=TenantSecretCreateDTO(
                scope=SecretScope.LLM_PROVIDER,
                target_identifier=LLMProvider.OPENAI.value,
                plaintext_secret=SecretStr("   "),
                storage_mode=SecretStorageMode.ENVELOPE_KMS,
            ),
        )
    assert empty_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    # 4. Malformed Cloud Secret Manager version URI
    with pytest.raises(AppException) as uri_exc:
        await service.upsert_tenant_secret(
            initiator=admin_a,
            organization_id=org_a,
            payload=TenantSecretCreateDTO(
                scope=SecretScope.LLM_PROVIDER,
                target_identifier=LLMProvider.OPENAI.value,
                plaintext_secret=SecretStr("invalid-uri-format"),
                storage_mode=SecretStorageMode.CLOUD_SECRET_MANAGER,
            ),
        )
    assert uri_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    # 5. Informational slug passed as target_identifier for MCP_GATEWAY (slug_data_relation_ban)
    with pytest.raises(AppException) as slug_exc:
        await service.upsert_tenant_secret(
            initiator=admin_a,
            organization_id=org_a,
            payload=TenantSecretCreateDTO(
                scope=SecretScope.MCP_GATEWAY,
                target_identifier="default_mcp_gateway",
                plaintext_secret=SecretStr("tvly-dev-key-1234"),
                storage_mode=SecretStorageMode.ENVELOPE_KMS,
            ),
        )
    assert slug_exc.value.status_code == 400
    assert slug_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    # 6. Wrong entity prefix passed as target_identifier for MCP_GATEWAY
    with pytest.raises(AppException) as prefix_exc:
        await service.upsert_tenant_secret(
            initiator=admin_a,
            organization_id=org_a,
            payload=TenantSecretCreateDTO(
                scope=SecretScope.MCP_GATEWAY,
                target_identifier=generate_opaque_id(EntityPrefix.WORKFLOW),
                plaintext_secret=SecretStr("tvly-dev-key-1234"),
                storage_mode=SecretStorageMode.ENVELOPE_KMS,
            ),
        )
    assert prefix_exc.value.status_code == 400
    assert prefix_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    # 7. Unknown provider string passed as target_identifier for LLM_PROVIDER
    with pytest.raises(AppException) as provider_exc:
        await service.upsert_tenant_secret(
            initiator=admin_a,
            organization_id=org_a,
            payload=TenantSecretCreateDTO(
                scope=SecretScope.LLM_PROVIDER,
                target_identifier="unknown_provider_slug",
                plaintext_secret=SecretStr("sk-invalid-provider"),
                storage_mode=SecretStorageMode.ENVELOPE_KMS,
            ),
        )
    assert provider_exc.value.status_code == 400
    assert provider_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    # 8. Deleting a non-existent secret ID
    missing_sec_id = generate_opaque_id(EntityPrefix.TENANT_SECRET)
    with pytest.raises(ResourceNotFoundError) as not_found_exc:
        await service.delete_tenant_secret(
            initiator=admin_a,
            organization_id=org_a,
            secret_id=missing_sec_id,
        )
    assert not_found_exc.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_secret_service_uow_factory_roundtrip_and_unconfigured_fail_fast() -> None:
    """Positive & Negative: Verify uow_factory cross-instance persistence, physical deletion, and unconfigured Fail-Fast."""
    uow = InMemoryUnitOfWork()
    writer_service = SecretService(uow_factory=lambda: uow)
    reader_service = SecretService(uow_factory=lambda: uow)

    org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
    admin_token = _make_token_data(role=UserRole.ADMIN, organization_id=org_id)
    gateway = _make_mcp_gateway(auth_type=MCPAuthType.BEARER, auth_env_var="MCP_GATEWAY_TOKEN")

    created = await writer_service.upsert_tenant_secret(
        initiator=admin_token,
        organization_id=org_id,
        payload=TenantSecretCreateDTO(
            scope=SecretScope.MCP_GATEWAY,
            target_identifier=gateway.id,
            plaintext_secret=SecretStr("tvly-dev-key-1234"),
            storage_mode=SecretStorageMode.ENVELOPE_KMS,
        ),
    )
    assert await uow.entities.get_tenant_secret(created.id) is not None

    # Second SecretService instance resolves persisted secret without any process-local RAM cache
    resolved = await reader_service.resolve_mcp_credential(organization_id=org_id, gateway=gateway)
    assert resolved.is_tenant_byok is True
    assert resolved.secret_value.get_secret_value() == "tvly-dev-key-1234"

    # Physical deletion removes record from uow.entities
    deleted = await writer_service.delete_tenant_secret(
        initiator=admin_token,
        organization_id=org_id,
        secret_id=created.id,
    )
    assert deleted is True
    assert await uow.entities.get_tenant_secret(created.id) is None

    # Deleting an already-deleted secret raises ResourceNotFoundError
    with pytest.raises(ResourceNotFoundError):
        await reader_service.delete_tenant_secret(
            initiator=admin_token,
            organization_id=org_id,
            secret_id=created.id,
        )

    # Unconfigured SecretService (both entity_adapter=None and uow_factory=None) fails fast with ConfigurationError
    unconfigured = SecretService(entity_adapter=None, uow_factory=None)
    with pytest.raises(ConfigurationError) as list_exc:
        await unconfigured.list_tenant_secrets(initiator=admin_token, organization_id=org_id)
    assert list_exc.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value

    with pytest.raises(ConfigurationError) as upsert_exc:
        await unconfigured.upsert_tenant_secret(
            initiator=admin_token,
            organization_id=org_id,
            payload=TenantSecretCreateDTO(
                scope=SecretScope.LLM_PROVIDER,
                target_identifier=LLMProvider.OPENAI.value,
                plaintext_secret=SecretStr("sk-test-1234"),
                storage_mode=SecretStorageMode.ENVELOPE_KMS,
            ),
        )
    assert upsert_exc.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value

    with pytest.raises(ConfigurationError) as del_exc:
        await unconfigured.delete_tenant_secret(
            initiator=admin_token,
            organization_id=org_id,
            secret_id=created.id,
        )
    assert del_exc.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value


@pytest.mark.asyncio
async def test_secret_service_kms_and_platform_mcp_failures_negative(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Negative: Verify KMS encrypt/decrypt failures, Secret Manager missing fetcher, and missing MCP env var fail fast."""
    monkeypatch.delenv("MISSING_GATEWAY_ENV", raising=False)
    uow = InMemoryUnitOfWork()
    org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
    admin_token = _make_token_data(role=UserRole.ADMIN, organization_id=org_id)

    # 1. KMS encrypt failure on upsert
    failing_kms_service = SecretService(
        entity_adapter=uow.entities,
        kms_wrapper=_FakeKMSWrapper(fail_encrypt=True),
    )
    with pytest.raises(ConfigurationError) as kms_enc_exc:
        await failing_kms_service.upsert_tenant_secret(
            initiator=admin_token,
            organization_id=org_id,
            payload=TenantSecretCreateDTO(
                scope=SecretScope.LLM_PROVIDER,
                target_identifier=LLMProvider.ANTHROPIC.value,
                plaintext_secret=SecretStr("sk-ant-valid-1234"),
                storage_mode=SecretStorageMode.ENVELOPE_KMS,
            ),
        )
    assert kms_enc_exc.value.details["error_code"] == ErrorCodes.SECRET_RESOLUTION_FAILED.value

    # 2. KMS decrypt returning invalid DEK byte length
    bad_len_kms_service = SecretService(
        entity_adapter=uow.entities,
        kms_wrapper=_FakeKMSWrapper(bad_length=True),
    )
    await bad_len_kms_service.upsert_tenant_secret(
        initiator=admin_token,
        organization_id=org_id,
        payload=TenantSecretCreateDTO(
            scope=SecretScope.LLM_PROVIDER,
            target_identifier=LLMProvider.ANTHROPIC.value,
            plaintext_secret=SecretStr("sk-ant-valid-1234"),
            storage_mode=SecretStorageMode.ENVELOPE_KMS,
        ),
    )
    with pytest.raises(ConfigurationError) as kms_dec_exc:
        await bad_len_kms_service.resolve_llm_key(organization_id=org_id, provider=LLMProvider.ANTHROPIC)
    assert kms_dec_exc.value.details["error_code"] == ErrorCodes.SECRET_RESOLUTION_FAILED.value

    # 3. Cloud Secret Manager record resolved without a configured fetcher
    no_fetcher_service = SecretService(entity_adapter=uow.entities)
    await no_fetcher_service.upsert_tenant_secret(
        initiator=admin_token,
        organization_id=org_id,
        payload=TenantSecretCreateDTO(
            scope=SecretScope.LLM_PROVIDER,
            target_identifier=LLMProvider.AI_STUDIO.value,
            plaintext_secret=SecretStr("projects/p1/secrets/s1/versions/1"),
            storage_mode=SecretStorageMode.CLOUD_SECRET_MANAGER,
        ),
    )
    with pytest.raises(ConfigurationError) as sm_exc:
        await no_fetcher_service.resolve_llm_key(organization_id=org_id, provider=LLMProvider.AI_STUDIO)
    assert sm_exc.value.details["error_code"] == ErrorCodes.SECRET_RESOLUTION_FAILED.value

    # 4. Platform MCP gateway missing auth_env_var and unset env var
    gw_no_env_name = _make_mcp_gateway(auth_type=MCPAuthType.BEARER, auth_env_var=None)
    with pytest.raises(ConfigurationError) as mcp_no_var_exc:
        await no_fetcher_service.resolve_mcp_credential(organization_id=org_id, gateway=gw_no_env_name)
    assert mcp_no_var_exc.value.details["error_code"] == ErrorCodes.SECRET_RESOLUTION_FAILED.value

    gw_unset_env = _make_mcp_gateway(auth_type=MCPAuthType.BEARER, auth_env_var="MISSING_GATEWAY_ENV")
    with pytest.raises(ConfigurationError) as mcp_unset_exc:
        await no_fetcher_service.resolve_mcp_credential(organization_id=org_id, gateway=gw_unset_env)
    assert mcp_unset_exc.value.details["error_code"] == ErrorCodes.SECRET_RESOLUTION_FAILED.value

    # 5. Incomplete ENVELOPE_KMS record missing nonce
    incomplete_record = TenantSecretDTO(
        id=generate_opaque_id(EntityPrefix.TENANT_SECRET),
        organization_id=org_id,
        scope=SecretScope.LLM_PROVIDER,
        target_identifier=LLMProvider.LOCAL.value,
        storage_mode=SecretStorageMode.ENVELOPE_KMS,
        encrypted_dek=b"12345678901234567890123456789012",
        ciphertext=b"cipher",
        nonce=None,
        kek_version="v1",
        masked_hint="****",
        updated_by=generate_opaque_id(EntityPrefix.USER),
        updated_at=datetime.now(UTC),
    )
    await uow.entities.upsert_tenant_secret(incomplete_record)
    with pytest.raises(ConfigurationError) as inc_exc:
        await no_fetcher_service.resolve_llm_key(organization_id=org_id, provider=LLMProvider.LOCAL)
    assert inc_exc.value.details["error_code"] == ErrorCodes.SECRET_RESOLUTION_FAILED.value


def test_generic_mcp_client_missing_resolved_credential_negative() -> None:
    """Negative: Verify GenericMCPClient._build_request_headers raises ConfigurationError when resolved_credential is None."""
    client = GenericMCPClient()
    gateway = _make_mcp_gateway(auth_type=MCPAuthType.BEARER, auth_env_var="MCP_GATEWAY_TOKEN")

    with pytest.raises(ConfigurationError) as exc_info:
        client._build_request_headers(gateway, resolved_credential=None)

    assert exc_info.value.details["error_code"] == ErrorCodes.SECRET_RESOLUTION_FAILED.value
    assert exc_info.value.details["gateway_id"] == gateway.id


@pytest.mark.asyncio
async def test_llm_factory_and_dispatcher_byok_request_scoped_injection_positive() -> None:
    """Positive: Verify LLMFactory, LiteLLMProvider, ToolDispatcher, and GenericMCPClient isolate BYOK keys per tenant."""
    LiteLLMProvider._router_cache.clear()
    LiteLLMProvider._semaphores.clear()

    uow = InMemoryUnitOfWork()
    service = SecretService(entity_adapter=uow.entities)

    org_a = generate_opaque_id(EntityPrefix.ORGANIZATION)
    org_b = generate_opaque_id(EntityPrefix.ORGANIZATION)
    admin_a = _make_token_data(role=UserRole.ADMIN, organization_id=org_a)
    admin_b = _make_token_data(role=UserRole.ADMIN, organization_id=org_b)

    await service.upsert_tenant_secret(
        initiator=admin_a,
        organization_id=org_a,
        payload=TenantSecretCreateDTO(
            scope=SecretScope.LLM_PROVIDER,
            target_identifier=LLMProvider.OPENAI.value,
            plaintext_secret=SecretStr("sk-tenant-a-byok-1111"),
            storage_mode=SecretStorageMode.ENVELOPE_KMS,
        ),
    )
    await service.upsert_tenant_secret(
        initiator=admin_b,
        organization_id=org_b,
        payload=TenantSecretCreateDTO(
            scope=SecretScope.LLM_PROVIDER,
            target_identifier=LLMProvider.OPENAI.value,
            plaintext_secret=SecretStr("sk-tenant-b-byok-2222"),
            storage_mode=SecretStorageMode.ENVELOPE_KMS,
        ),
    )

    cred_a = await service.resolve_llm_key(organization_id=org_a, provider=LLMProvider.OPENAI)
    cred_b = await service.resolve_llm_key(organization_id=org_b, provider=LLMProvider.OPENAI)

    prov_a = LLMFactory.create_provider(
        "openai",
        "openai/gpt-4o",
        limits={"tpm": 50000, "rpm": 60},
        resolved_credential=cred_a,
    )
    prov_b = LLMFactory.create_provider(
        "openai",
        "openai/gpt-4o",
        limits={"tpm": 50000, "rpm": 60},
        resolved_credential=cred_b,
    )

    assert isinstance(prov_a, LiteLLMProvider)
    assert isinstance(prov_b, LiteLLMProvider)
    assert prov_a.organization_id == org_a
    assert prov_b.organization_id == org_b
    assert prov_a.cache_key != prov_b.cache_key
    assert prov_a.router is not prov_b.router
    assert prov_a.api_key == "sk-tenant-a-byok-1111"
    assert prov_b.api_key == "sk-tenant-b-byok-2222"

    # Verify MCP credential injection in ToolDispatcher and GenericMCPClient with zero audit trace leakage
    search_tool = AllowedMCPTool(
        tool_id="search_docs",
        capability=ToolCapability.SEARCH,
        name=I18nText(translations={"en": "Search Docs", "fi": "Hae dokumentit"}),
        description="Search enterprise docs.",
        input_schema=MCPToolInputSchemaDTO(
            properties={"query": MCPToolSchemaPropertyDTO(type=JSONSchemaPropertyType.STRING)},
            required=["query"],
        ),
        enabled=True,
    )
    gateway = SystemConfigMCPGateways(
        id=generate_opaque_id(EntityPrefix.SYSTEM_CONFIG),
        name="Enterprise Search Gateway",
        slug="ent_search",
        endpoint_url="https://mcp.example.com/v1/mcp",
        transport_type=MCPTransportType.STREAMABLE_HTTP,
        auth_type=MCPAuthType.BEARER,
        auth_env_var="MCP_GATEWAY_TOKEN",
        timeout_seconds=10,
        tools=[search_tool],
    )

    await service.upsert_tenant_secret(
        initiator=admin_a,
        organization_id=org_a,
        payload=TenantSecretCreateDTO(
            scope=SecretScope.MCP_GATEWAY,
            target_identifier=gateway.id,
            plaintext_secret=SecretStr("mcp-bearer-secret-9999"),
            storage_mode=SecretStorageMode.ENVELOPE_KMS,
        ),
    )

    mcp_cred = await service.resolve_mcp_credential(organization_id=org_a, gateway=gateway)
    client = GenericMCPClient(secret_service=service)
    headers = client._build_request_headers(gateway, resolved_credential=mcp_cred)
    assert headers["Authorization"] == "Bearer mcp-bearer-secret-9999"

    captured_cred: list[ResolvedCredentialDTO | None] = []

    class _StubMCPClient(GenericMCPClient):
        async def call_tool(
            self,
            gw: SystemConfigMCPGateways,
            invocation: object,
            *,
            organization_id: str | None = None,
            resolved_credential: ResolvedCredentialDTO | None = None,
        ) -> str:
            captured_cred.append(resolved_credential)
            return "<![CDATA[Evidence from https://docs.example.com/1]]>"

    dispatcher = ToolDispatcher(
        [gateway],
        mcp_client=_StubMCPClient(secret_service=service),
        secret_service=service,
        organization_id=org_a,
    )
    alias = "ent_search__search_docs"
    audit_trace = await dispatcher.execute_tool(
        tool_id=alias,
        raw_arguments={"query": "quarterly revenue"},
        allowed_step_tools={alias},
        step_name="stp_audit",
    )
    assert len(captured_cred) == 1
    assert captured_cred[0] is not None
    assert captured_cred[0].secret_value.get_secret_value() == "mcp-bearer-secret-9999"
    assert "mcp-bearer-secret-9999" not in str(audit_trace.model_dump(mode="json"))


@pytest.mark.asyncio
async def test_organizations_byok_router_endpoints_positive_and_negative() -> None:
    """Positive & Negative: Verify GET/PUT/DELETE /organizations/{org_id}/secrets endpoints and tenant isolation."""
    uow = InMemoryUnitOfWork()
    audit_logger = _RecordingAuditLogger()
    service = SecretService(entity_adapter=uow.entities, audit_service=audit_logger)

    org_a = generate_opaque_id(EntityPrefix.ORGANIZATION)
    org_b = generate_opaque_id(EntityPrefix.ORGANIZATION)
    admin_a = _make_token_data(role=UserRole.ADMIN, organization_id=org_a)

    created = await upsert_organization_secret(
        org_id=org_a,
        payload=TenantSecretCreateDTO(
            scope=SecretScope.LLM_PROVIDER,
            target_identifier=LLMProvider.OPENAI.value,
            plaintext_secret=SecretStr("sk-org-router-test-7777"),
            storage_mode=SecretStorageMode.ENVELOPE_KMS,
        ),
        current_user=admin_a,
        secret_service=service,
    )
    assert created.organization_id == org_a
    assert created.masked_hint == "****7777"

    listed = await list_organization_secrets(
        org_id=org_a,
        current_user=admin_a,
        secret_service=service,
    )
    assert len(listed) == 1
    assert listed[0].id == created.id

    with pytest.raises(PermissionDeniedError) as cross_exc:
        await list_organization_secrets(
            org_id=org_b,
            current_user=admin_a,
            secret_service=service,
        )
    assert cross_exc.value.details["error_code"] == ErrorCodes.PERMISSION_DENIED.value

    del_resp = await delete_organization_secret(
        org_id=org_a,
        secret_id=created.id,
        current_user=admin_a,
        secret_service=service,
    )
    assert del_resp.status == "success"
    assert del_resp.deleted_id == created.id


def test_dlp_ast_guardrail_secret_str_leakage_detection_positive_and_negative() -> None:
    """Positive & Negative: Verify QGR033 catches get_secret_value() in logger and MCPAuditTrace calls."""
    bad_source = '''"""Module docstring."""
import logging
from backend_v2.models.auth import ResolvedCredentialDTO
from backend_v2.models.domain.mcp import MCPAuditTrace

logger = logging.getLogger(__name__)


def leak_in_log(cred: ResolvedCredentialDTO) -> None:
    """Bad function leaking secret in logger."""
    logger.info("Resolved key", extra={"raw": cred.secret_value.get_secret_value()})
    MCPAuditTrace(
        step_id="stp_0195f3a0000070008000000000000001",
        gateway_id="sys_0195f3a0000070008000000000000001",
        tool_name=cred.secret_value.get_secret_value(),
        arguments={},
        status="SUCCESS",
        latency_ms=1.0,
    )
'''
    violations = scan_source_code_for_guardrails("backend_v2/services/mcp/bad_sink.py", bad_source.encode("utf-8"))
    qgr033_msgs = [v.message for v in violations if v.rule_code == "QGR033" and "get_secret_value" in v.message]
    assert len(qgr033_msgs) == 2

    clean_source = '''"""Module docstring."""
from backend_v2.models.auth import ResolvedCredentialDTO


def safe_header_bind(cred: ResolvedCredentialDTO) -> str:
    """Bind header safely outside logger or audit trace."""
    return f"Bearer {cred.secret_value.get_secret_value()}"
'''
    clean_violations = scan_source_code_for_guardrails(
        "backend_v2/services/mcp/safe_bind.py", clean_source.encode("utf-8")
    )
    clean_qgr033 = [v for v in clean_violations if v.rule_code == "QGR033" and "get_secret_value" in v.message]
    assert clean_qgr033 == []


@pytest.mark.asyncio
async def test_secret_service_root_system_inheritance_and_custom_mcp_gateway_without_env_var_positive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Positive: Verify ROOT_SYSTEM DB secrets inherit for tenants without overrides and support custom MCP gateways with auth_env_var=None."""
    clean_settings = get_settings().model_copy(
        update={"openai_api_key": None, "google_api_key": None, "anthropic_api_key": None}
    )
    monkeypatch.setattr("backend_v2.services.auth.secret_service.get_settings", lambda: clean_settings)

    uow = InMemoryUnitOfWork()
    service = SecretService(entity_adapter=uow.entities)

    root_org_id = SystemOrganizations.ROOT_SYSTEM.value
    tenant_org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
    root_token = _make_token_data(role=UserRole.ROOT, organization_id=root_org_id)

    multiline_vertex_sa_json = (
        '{\n  "type": "service_account",\n  "project_id": "vertex-proj-1234",\n'
        '  "client_email": "sa@vertex-proj-1234.iam.gserviceaccount.com",\n'
        '  "private_key": "-----BEGIN PRIVATE KEY-----\\nabc9876\\n-----END PRIVATE KEY-----\\n"\n}'
    )
    vertex_resp = await service.upsert_tenant_secret(
        initiator=root_token,
        organization_id=root_org_id,
        payload=TenantSecretCreateDTO(
            scope=SecretScope.LLM_PROVIDER,
            target_identifier=LLMProvider.VERTEX_AI.value,
            plaintext_secret=SecretStr(multiline_vertex_sa_json),
            storage_mode=SecretStorageMode.ENVELOPE_KMS,
        ),
    )
    assert vertex_resp.masked_hint == "****KEYn"
    assert "\n" not in vertex_resp.masked_hint
    assert "}" not in vertex_resp.masked_hint

    resolved_llm = await service.resolve_llm_key(
        organization_id=tenant_org_id,
        provider=LLMProvider.VERTEX_AI,
    )
    assert resolved_llm.is_tenant_byok is True
    assert resolved_llm.secret_value.get_secret_value() == multiline_vertex_sa_json

    custom_gateway = SystemConfigMCPGateways(
        id=generate_opaque_id(EntityPrefix.SYSTEM_CONFIG),
        name="Custom Enterprise MCP Server",
        slug="custom_enterprise_mcp",
        endpoint_url="https://mcp.custom.example.com/v1/mcp",
        transport_type=MCPTransportType.STREAMABLE_HTTP,
        auth_type=MCPAuthType.API_KEY_HEADER,
        auth_header_name="X-Custom-Mcp-Key",
        auth_env_var=None,
        timeout_seconds=10,
        tools=[],
    )
    await service.upsert_tenant_secret(
        initiator=root_token,
        organization_id=root_org_id,
        payload=TenantSecretCreateDTO(
            scope=SecretScope.MCP_GATEWAY,
            target_identifier=custom_gateway.id,
            plaintext_secret=SecretStr("custom-mcp-header-secret-xyz9"),
            storage_mode=SecretStorageMode.ENVELOPE_KMS,
        ),
    )

    resolved_mcp = await service.resolve_mcp_credential(
        organization_id=tenant_org_id,
        gateway=custom_gateway,
    )
    assert resolved_mcp.is_tenant_byok is True
    assert resolved_mcp.secret_value.get_secret_value() == "custom-mcp-header-secret-xyz9"

    client = GenericMCPClient(secret_service=service)
    headers = client._build_request_headers(custom_gateway, resolved_credential=resolved_mcp)
    assert headers["X-Custom-Mcp-Key"] == "custom-mcp-header-secret-xyz9"


def test_secret_service_masked_hint_short_json_boundary() -> None:
    """Boundary: Verify _build_masked_hint returns '****' when a JSON secret has fewer than 4 alphanumeric characters."""
    assert SecretService._build_masked_hint("{}") == "****"
    assert SecretService._build_masked_hint('{"a": 1}') == "****"
    assert SecretService._build_masked_hint('{"key": "ab12"}') == "****ab12"
