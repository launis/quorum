"""Enterprise BYOK and Cloud Secrets Governance Service for LLM and MCP Credentials."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import re
import secrets
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import NoReturn, Protocol

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pydantic import SecretStr

from backend_v2.database.interfaces import (
    EntityPersistencePort,
    UnitOfWorkFactory,
    get_registered_uow_factory,
)
from backend_v2.exceptions import (
    AppException,
    ConfigurationError,
    ErrorCodes,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from backend_v2.models.auth import (
    ResolvedCredentialDTO,
    SystemOrganizations,
    TenantSecretCreateDTO,
    TenantSecretDTO,
    TenantSecretResponseDTO,
    TokenData,
)
from backend_v2.models.core_base import (
    PrefixedUUID7,
    generate_opaque_id,
    parse_prefixed_uuid7,
)
from backend_v2.models.domain.system_config import SystemConfigMCPGateways
from backend_v2.models.enums import (
    EntityPrefix,
    LLMProvider,
    SecretScope,
    SecretStorageMode,
    UserRole,
)
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = [
    "AuditLoggerProtocol",
    "CloudKMSKeyWrapperProtocol",
    "CloudSecretManagerFetcherProtocol",
    "SecretService",
    "get_secret_service",
    "reset_secret_service",
]

_SECRET_MANAGER_URI_PATTERN: re.Pattern[str] = re.compile(r"^projects/[^/\s]+/secrets/[^/\s]+/versions/[^/\s]+$")
_DEFAULT_LOCAL_KEK_VERSION: str = "local-kms-v1"
_DEK_BYTE_LENGTH: int = 32
_AES_GCM_NONCE_BYTE_LENGTH: int = 12
_MIN_WRAPPED_DEK_BYTE_LENGTH: int = 28
_VALID_LLM_PROVIDER_IDS: frozenset[str] = frozenset(provider.value for provider in LLMProvider)
_VALID_TELEMETRY_TARGET_IDS: frozenset[str] = frozenset({"logfire", "logfire_read"})


class AuditLoggerProtocol(Protocol):
    """Protocol for structured security audit event recording."""

    async def log_event(
        self,
        *,
        actor_id: str,
        action: str,
        organization_id: str,
        target_id: str,
        details: dict[str, str],
    ) -> None:
        """Record a security audit event without sensitive secret material."""
        ...


class CloudKMSKeyWrapperProtocol(Protocol):
    """Protocol for Cloud KMS Key Encryption Key (KEK) DEK wrapping and unwrapping."""

    async def encrypt_dek(self, dek: bytes, kek_version: str) -> bytes:
        """Wrap a 256-bit Data Encryption Key using the specified Cloud KMS KEK version."""
        ...

    async def decrypt_dek(self, encrypted_dek: bytes, kek_version: str) -> bytes:
        """Unwrap an encrypted Data Encryption Key using the specified Cloud KMS KEK version."""
        ...


class CloudSecretManagerFetcherProtocol(Protocol):
    """Protocol for resolving tenant secret payloads from GCP Secret Manager."""

    async def access_secret_version(self, version_uri: str) -> str:
        """Fetch the plaintext secret payload for a canonical Secret Manager version URI."""
        ...


class SecretService:
    """Dual-Tier BYOK Secret Governance Service enforcing Single-Pipeline Non-Nullable resolution.

    Supports both GCP Cloud Secret Manager version URI resolution (`CLOUD_SECRET_MANAGER`)
    and NIST SP 800-57 envelope encryption (`ENVELOPE_KMS`) using a unique 256-bit AES-GCM
    Data Encryption Key (DEK) wrapped by a Cloud KMS or local Key Encryption Key (KEK).

    Attributes:
        audit_service: Optional structured audit event logger.
    """

    def __init__(
        self,
        entity_adapter: EntityPersistencePort | None = None,
        audit_service: AuditLoggerProtocol | None = None,
        kms_wrapper: CloudKMSKeyWrapperProtocol | None = None,
        secret_manager_fetcher: CloudSecretManagerFetcherProtocol | None = None,
        uow_factory: UnitOfWorkFactory | None = None,
    ) -> None:
        """Initialize the SecretService with persistence and cryptographic adapters.

        Args:
            entity_adapter: Optional hexagonal entity persistence port for tenant_secrets.
            audit_service: Optional structured audit logger for secret lifecycle events.
            kms_wrapper: Optional Cloud KMS key wrapper for DEK encryption/decryption.
            secret_manager_fetcher: Optional GCP Secret Manager version accessor.
            uow_factory: Optional UnitOfWorkFactory for transactional persistence when entity_adapter is None.
        """
        # Bind persistence strictly via entity_adapter or uow_factory with zero in-memory fallback
        self._entity_adapter = entity_adapter
        self.audit_service = audit_service
        self._kms_wrapper = kms_wrapper
        self._secret_manager_fetcher = secret_manager_fetcher
        self._uow_factory = uow_factory

    async def list_tenant_secrets(
        self,
        initiator: TokenData,
        organization_id: PrefixedUUID7,
    ) -> list[TenantSecretResponseDTO]:
        """List all redacted BYOK secret metadata records for an organization.

        Args:
            initiator: Authenticated caller token data.
            organization_id: Target organization identifier (org_<hex32>).

        Returns:
            List of redacted TenantSecretResponseDTO objects containing masked_hint only.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if caller lacks tenant admin rights.
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if persistence is unconfigured.
        """
        self._verify_tenant_admin_access(initiator=initiator, organization_id=organization_id)
        records = await self._list_org_secret_records(organization_id)
        can_view_telemetry = (
            initiator.role == UserRole.ROOT and organization_id == SystemOrganizations.ROOT_SYSTEM.value
        )
        return [
            self._to_response_dto(record)
            for record in records
            if record.scope != SecretScope.TELEMETRY or can_view_telemetry
        ]

    async def upsert_tenant_secret(
        self,
        initiator: TokenData,
        organization_id: PrefixedUUID7,
        payload: TenantSecretCreateDTO,
        *,
        secret_manager_version_uri: str | None = None,
        kek_version: str | None = None,
    ) -> TenantSecretResponseDTO:
        """Provision or rotate a tenant-scoped BYOK secret and emit a TENANT_SECRET_UPSERTED audit event.

        Args:
            initiator: Authenticated caller token data.
            organization_id: Target organization identifier (org_<hex32>).
            payload: Validated TenantSecretCreateDTO containing the SecretStr secret and storage_mode.
            secret_manager_version_uri: Optional GCP Secret Manager version URI when mode is CLOUD_SECRET_MANAGER.
            kek_version: Optional KEK version identifier override.

        Returns:
            Redacted TenantSecretResponseDTO with masked_hint and active kek_version.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if caller lacks tenant admin rights
                or attempts to mutate SecretScope.TELEMETRY outside UserRole.ROOT on ROOT_SYSTEM.
            AppException: With ErrorCodes.VALIDATION_FAILED if secret payload, target_identifier, or URI is invalid.
            ConfigurationError: With ErrorCodes.SECRET_RESOLUTION_FAILED if KMS wrapping fails or ErrorCodes.CONFIGURATION_ERROR if persistence is unconfigured.
        """
        self._verify_tenant_admin_access(initiator=initiator, organization_id=organization_id)
        if payload.scope == SecretScope.TELEMETRY:
            self._verify_telemetry_root_access(initiator=initiator, organization_id=organization_id)
        self._validate_target_identifier(
            organization_id=organization_id,
            scope=payload.scope,
            target_identifier=payload.target_identifier,
        )
        raw_secret = payload.plaintext_secret.get_secret_value().strip()
        if not raw_secret:
            msg = "Tenant secret plaintext value cannot be empty or whitespace."
            logger.error(
                "[SecretService] %s: %s (organization_id=%s, target=%s)",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                organization_id,
                payload.target_identifier,
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={
                    "error_code": ErrorCodes.VALIDATION_FAILED.value,
                    "organization_id": organization_id,
                    "target_identifier": payload.target_identifier,
                },
            )

        existing = await self._find_secret_record(
            organization_id=organization_id,
            scope=payload.scope,
            target_identifier=payload.target_identifier,
        )
        secret_id: PrefixedUUID7 = (
            existing.id if existing is not None else generate_opaque_id(EntityPrefix.TENANT_SECRET)
        )
        resolved_kek_version = self._resolve_kek_version(kek_version)
        masked_hint = self._build_masked_hint(raw_secret)

        record = await self._build_encrypted_record(
            secret_id=secret_id,
            organization_id=organization_id,
            payload=payload,
            raw_secret=raw_secret,
            storage_mode=payload.storage_mode,
            secret_manager_version_uri=secret_manager_version_uri,
            kek_version=resolved_kek_version,
            masked_hint=masked_hint,
            updated_by=initiator.id,
        )

        await self._persist_secret_record(record)

        await self._record_audit_event(
            actor_id=initiator.id,
            action="TENANT_SECRET_UPSERTED",
            organization_id=organization_id,
            record=record,
        )
        return self._to_response_dto(record)

    async def delete_tenant_secret(
        self,
        initiator: TokenData,
        organization_id: PrefixedUUID7,
        secret_id: PrefixedUUID7,
    ) -> bool:
        """Delete a tenant-scoped BYOK secret and emit a TENANT_SECRET_DELETED audit event.

        Args:
            initiator: Authenticated caller token data.
            organization_id: Owning organization identifier (org_<hex32>).
            secret_id: Canonical tenant secret identifier (sec_<hex32>).

        Returns:
            True once the secret has been physically removed and audited.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if caller lacks tenant admin rights.
            ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if secret does not exist in organization.
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if persistence is unconfigured.
        """
        self._verify_tenant_admin_access(initiator=initiator, organization_id=organization_id)
        record = await self._get_secret_record_by_id(secret_id)
        if record is None or record.organization_id != organization_id:
            msg = f"Tenant secret '{secret_id}' not found in organization '{organization_id}'."
            logger.error(
                "[SecretService] %s: %s",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                msg,
                exc_info=True,
            )
            raise ResourceNotFoundError(
                "TenantSecret",
                secret_id,
                details={
                    "error_code": ErrorCodes.RESOURCE_NOT_FOUND.value,
                    "secret_id": secret_id,
                    "organization_id": organization_id,
                },
            )
        if record.scope == SecretScope.TELEMETRY:
            self._verify_telemetry_root_access(initiator=initiator, organization_id=organization_id)

        await self._delete_secret_record(secret_id)

        await self._record_audit_event(
            actor_id=initiator.id,
            action="TENANT_SECRET_DELETED",
            organization_id=organization_id,
            record=record,
        )
        return True

    async def resolve_llm_key(
        self,
        organization_id: PrefixedUUID7,
        provider: LLMProvider,
    ) -> ResolvedCredentialDTO:
        """Resolve an LLM provider credential for an organization strictly from database tenant_secrets.

        Args:
            organization_id: Tenant organization identifier (org_<hex32>).
            provider: Target LLMProvider enum member.

        Returns:
            Non-nullable ResolvedCredentialDTO wrapping the decrypted SecretStr.

        Raises:
            ConfigurationError: With ErrorCodes.SECRET_RESOLUTION_FAILED if decryption fails
                or if neither the tenant nor ROOT_SYSTEM has a secret record in tenant_secrets.
        """
        return await self._resolve_scoped_secret(
            organization_id=organization_id,
            scope=SecretScope.LLM_PROVIDER,
            target_identifier=provider.value,
            target_kind_label="LLM provider",
            detail_key="provider",
        )

    async def resolve_mcp_credential(
        self,
        organization_id: PrefixedUUID7,
        gateway: SystemConfigMCPGateways,
    ) -> ResolvedCredentialDTO:
        """Resolve an MCP gateway credential for an organization strictly from database tenant_secrets.

        Args:
            organization_id: Tenant organization identifier (org_<hex32>).
            gateway: Target SystemConfigMCPGateways domain model.

        Returns:
            Non-nullable ResolvedCredentialDTO wrapping the decrypted SecretStr.

        Raises:
            ConfigurationError: With ErrorCodes.SECRET_RESOLUTION_FAILED if decryption fails
                or if neither the tenant nor ROOT_SYSTEM has a secret record in tenant_secrets.
        """
        return await self._resolve_scoped_secret(
            organization_id=organization_id,
            scope=SecretScope.MCP_GATEWAY,
            target_identifier=gateway.id,
            target_kind_label="MCP gateway",
            detail_key="gateway_id",
        )

    async def resolve_telemetry_secret(
        self,
        target_identifier: str = "logfire",
    ) -> ResolvedCredentialDTO:
        """Resolve a platform-level telemetry credential strictly from ROOT_SYSTEM in tenant_secrets.

        Args:
            target_identifier: Telemetry target identifier ('logfire' or 'logfire_read').

        Returns:
            Non-nullable ResolvedCredentialDTO wrapping the decrypted SecretStr.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if target_identifier is not a valid telemetry target.
            ConfigurationError: With ErrorCodes.SECRET_RESOLUTION_FAILED if decryption fails
                or if ROOT_SYSTEM has no telemetry secret record in tenant_secrets.
        """
        root_org_id: PrefixedUUID7 = SystemOrganizations.ROOT_SYSTEM.value
        self._validate_target_identifier(
            organization_id=root_org_id,
            scope=SecretScope.TELEMETRY,
            target_identifier=target_identifier,
        )
        return await self._resolve_scoped_secret(
            organization_id=root_org_id,
            scope=SecretScope.TELEMETRY,
            target_identifier=target_identifier,
            target_kind_label="telemetry target",
            detail_key="target_identifier",
        )

    async def _resolve_scoped_secret(
        self,
        *,
        organization_id: PrefixedUUID7,
        scope: SecretScope,
        target_identifier: str,
        target_kind_label: str,
        detail_key: str,
    ) -> ResolvedCredentialDTO:
        """Resolve a scoped BYOK secret for an organization with ROOT_SYSTEM inheritance.

        Args:
            organization_id: Tenant organization identifier (org_<hex32>).
            scope: Secret capability scope (LLM_PROVIDER or MCP_GATEWAY).
            target_identifier: Provider enum value or canonical MCP gateway ID.
            target_kind_label: Human-readable target label for structured error diagnostics.
            detail_key: Structured RFC 7807 details key ('provider' or 'gateway_id').

        Returns:
            Non-nullable ResolvedCredentialDTO containing the decrypted SecretStr.

        Raises:
            ConfigurationError: With ErrorCodes.SECRET_RESOLUTION_FAILED if no secret record exists
                or if decryption/Secret Manager lookup fails.
        """
        record = await self._find_secret_record(
            organization_id=organization_id,
            scope=scope,
            target_identifier=target_identifier,
        )
        root_org_id: PrefixedUUID7 = SystemOrganizations.ROOT_SYSTEM.value
        if record is None and organization_id != root_org_id:
            # Inherit platform-wide credential stored under ROOT_SYSTEM when the tenant has no override
            record = await self._find_secret_record(
                organization_id=root_org_id,
                scope=scope,
                target_identifier=target_identifier,
            )
        if record is None:
            msg = (
                f"No database secret configured in tenant_secrets for {target_kind_label} "
                f"'{target_identifier}' (organization_id='{organization_id}')."
            )
            logger.error(
                "[SecretService] %s: %s",
                ErrorCodes.SECRET_RESOLUTION_FAILED.name,
                msg,
                exc_info=True,
                extra={
                    "error_code": ErrorCodes.SECRET_RESOLUTION_FAILED.value,
                    "organization_id": organization_id,
                    detail_key: target_identifier,
                },
            )
            raise ConfigurationError(
                message=msg,
                details={
                    "error_code": ErrorCodes.SECRET_RESOLUTION_FAILED.value,
                    "organization_id": organization_id,
                    detail_key: target_identifier,
                },
            )

        plaintext = await self._decrypt_or_fetch_secret(record)
        return ResolvedCredentialDTO(
            organization_id=organization_id,
            scope=scope,
            target_identifier=target_identifier,
            secret_value=SecretStr(plaintext),
            is_tenant_byok=True,
        )

    @staticmethod
    def _verify_tenant_admin_access(initiator: TokenData, organization_id: str) -> None:
        """Verify that the caller is ROOT or an ADMIN belonging to the target organization.

        Args:
            initiator: Authenticated caller token data.
            organization_id: Target organization ID.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED on role or tenant mismatch.
        """
        is_authorized = initiator.role == UserRole.ROOT or (
            initiator.role == UserRole.ADMIN and initiator.organization_id == organization_id
        )
        if not is_authorized:
            msg = f"Caller '{initiator.id}' is not authorized to manage BYOK secrets for '{organization_id}'."
            logger.error(
                "[SecretService] %s: %s",
                ErrorCodes.PERMISSION_DENIED.name,
                msg,
                exc_info=True,
            )
            raise PermissionDeniedError(
                message=msg,
                details={
                    "error_code": ErrorCodes.PERMISSION_DENIED.value,
                    "organization_id": organization_id,
                },
            )

    @staticmethod
    def _verify_telemetry_root_access(initiator: TokenData, organization_id: str) -> None:
        """Verify that SecretScope.TELEMETRY operations are performed by ROOT on ROOT_SYSTEM.

        Args:
            initiator: Authenticated caller token data.
            organization_id: Target organization ID.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if caller is not ROOT
                or organization_id is not ROOT_SYSTEM.
        """
        root_org_id: str = SystemOrganizations.ROOT_SYSTEM.value
        if initiator.role != UserRole.ROOT or organization_id != root_org_id:
            msg = (
                f"Caller '{initiator.id}' (role='{initiator.role.value}') is not authorized to manage "
                f"telemetry secrets for organization '{organization_id}'."
            )
            logger.error(
                "[SecretService] %s: %s",
                ErrorCodes.PERMISSION_DENIED.name,
                msg,
                exc_info=True,
                extra={
                    "error_code": ErrorCodes.PERMISSION_DENIED.value,
                    "organization_id": organization_id,
                    "scope": SecretScope.TELEMETRY.value,
                },
            )
            raise PermissionDeniedError(
                message=msg,
                details={
                    "error_code": ErrorCodes.PERMISSION_DENIED.value,
                    "organization_id": organization_id,
                    "scope": SecretScope.TELEMETRY.value,
                },
            )

    @staticmethod
    def _build_masked_hint(raw_secret: str) -> str:
        """Build a 4-character redacted suffix hint from a plaintext secret.

        Args:
            raw_secret: Stripped plaintext secret string.

        Returns:
            Redacted hint formatted as '****<last4>' or '****' for short secrets.
        """
        # Sanitize multiline JSON secrets (such as Vertex AI Service Account JSON) to a clean 4-char suffix
        if raw_secret.startswith("{"):
            alnum_tail = "".join(ch for ch in raw_secret if ch.isalnum())[-4:]
            if len(alnum_tail) == 4:
                return f"****{alnum_tail}"
            return "****"
        if len(raw_secret) >= 4:
            return f"****{raw_secret[-4:]}"
        return "****"

    @staticmethod
    def _resolve_kek_version(kek_version: str | None) -> str:
        """Resolve the active KEK version identifier from explicit parameter or Settings.

        Args:
            kek_version: Optional explicit KEK version override.

        Returns:
            Non-empty KEK version identifier string.
        """
        if kek_version is not None and kek_version.strip():
            return kek_version.strip()
        settings = get_settings()
        if settings.kms_master_key_id is not None and settings.kms_master_key_id.strip():
            return settings.kms_master_key_id.strip()
        return _DEFAULT_LOCAL_KEK_VERSION

    @staticmethod
    def _build_aead_aad(organization_id: str, scope: SecretScope, target_identifier: str) -> bytes:
        """Build deterministic AEAD associated data binding ciphertext to tenant and target scope.

        Args:
            organization_id: Owning organization ID.
            scope: Secret capability scope.
            target_identifier: Provider or gateway identifier.

        Returns:
            UTF-8 encoded associated data bytes.
        """
        return f"{organization_id}:{scope.value}:{target_identifier}".encode()

    @staticmethod
    def _derive_local_kek(kek_version: str) -> bytes:
        """Derive a deterministic 256-bit local Key Encryption Key from Settings and kek_version.

        Args:
            kek_version: Active KEK version string.

        Returns:
            32-byte AES-256 key encryption key.
        """
        settings = get_settings()
        master_seed = settings.jwt_secret_key.get_secret_value()
        if settings.kms_master_key_id is not None and settings.kms_master_key_id.strip():
            master_seed = f"{master_seed}:{settings.kms_master_key_id.strip()}"
        return hashlib.sha256(f"quorum-byok-kek:{master_seed}:{kek_version}".encode()).digest()

    async def _wrap_dek(self, dek: bytes, kek_version: str) -> bytes:
        """Wrap a 256-bit DEK using Cloud KMS wrapper or local AES-256-GCM KEK.

        Args:
            dek: Raw 32-byte Data Encryption Key.
            kek_version: Active KEK version identifier.

        Returns:
            Wrapped DEK bytes.

        Raises:
            ConfigurationError: With ErrorCodes.SECRET_RESOLUTION_FAILED if wrapping fails.
        """
        try:
            if self._kms_wrapper is not None:
                return await self._kms_wrapper.encrypt_dek(dek, kek_version)
            kek = self._derive_local_kek(kek_version)
            kek_nonce = secrets.token_bytes(_AES_GCM_NONCE_BYTE_LENGTH)
            wrapped = AESGCM(kek).encrypt(kek_nonce, dek, kek_version.encode("utf-8"))
            return kek_nonce + wrapped
        except Exception as exc:
            msg = f"Failed to wrap BYOK Data Encryption Key with KEK '{kek_version}'."
            logger.error(
                "[SecretService] %s: %s",
                ErrorCodes.SECRET_RESOLUTION_FAILED.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.SECRET_RESOLUTION_FAILED.value, "kek_version": kek_version},
            )
            raise ConfigurationError(
                message=msg,
                details={"error_code": ErrorCodes.SECRET_RESOLUTION_FAILED.value, "kek_version": kek_version},
            ) from exc

    async def _unwrap_dek(self, encrypted_dek: bytes, kek_version: str) -> bytes:
        """Unwrap an encrypted 256-bit DEK using Cloud KMS wrapper or local AES-256-GCM KEK.

        Args:
            encrypted_dek: Wrapped DEK bytes from TenantSecretDTO.
            kek_version: KEK version identifier recorded on TenantSecretDTO.

        Returns:
            Raw 32-byte Data Encryption Key.

        Raises:
            ValueError: If wrapped DEK bytes are truncated or authentication tag verification fails.
        """
        if self._kms_wrapper is not None:
            dek = await self._kms_wrapper.decrypt_dek(encrypted_dek, kek_version)
            if len(dek) != _DEK_BYTE_LENGTH:
                raise ValueError("Unwrapped KMS DEK must be exactly 32 bytes.")
            return dek

        if len(encrypted_dek) < _MIN_WRAPPED_DEK_BYTE_LENGTH:
            raise ValueError("Encrypted DEK envelope is truncated or malformed.")
        kek = self._derive_local_kek(kek_version)
        kek_nonce = encrypted_dek[:_AES_GCM_NONCE_BYTE_LENGTH]
        wrapped_payload = encrypted_dek[_AES_GCM_NONCE_BYTE_LENGTH:]
        dek = AESGCM(kek).decrypt(kek_nonce, wrapped_payload, kek_version.encode("utf-8"))
        if len(dek) != _DEK_BYTE_LENGTH:
            raise ValueError("Unwrapped local DEK must be exactly 32 bytes.")
        return dek

    async def _build_encrypted_record(
        self,
        *,
        secret_id: PrefixedUUID7,
        organization_id: PrefixedUUID7,
        payload: TenantSecretCreateDTO,
        raw_secret: str,
        storage_mode: SecretStorageMode,
        secret_manager_version_uri: str | None,
        kek_version: str,
        masked_hint: str,
        updated_by: PrefixedUUID7,
    ) -> TenantSecretDTO:
        """Construct a validated TenantSecretDTO for either CLOUD_SECRET_MANAGER or ENVELOPE_KMS.

        Args:
            secret_id: Canonical sec_<hex32> identifier.
            organization_id: Owning organization ID (org_<hex32>).
            payload: Validated creation payload.
            raw_secret: Stripped secret string.
            storage_mode: Selected cryptographic storage mode.
            secret_manager_version_uri: Optional explicit Secret Manager version URI.
            kek_version: Active KEK version string.
            masked_hint: Redacted display hint.
            updated_by: Initiator user ID.

        Returns:
            Validated TenantSecretDTO ready for persistence.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if Secret Manager URI is malformed.
            ConfigurationError: With ErrorCodes.SECRET_RESOLUTION_FAILED if KMS wrapping fails.
        """
        if storage_mode == SecretStorageMode.CLOUD_SECRET_MANAGER:
            resolved_uri = raw_secret
            if secret_manager_version_uri is not None and secret_manager_version_uri.strip():
                resolved_uri = secret_manager_version_uri.strip()
            if not _SECRET_MANAGER_URI_PATTERN.match(resolved_uri):
                msg = "Cloud Secret Manager URI must match 'projects/{project}/secrets/{name}/versions/{version}'."
                logger.error(
                    "[SecretService] %s: %s (organization_id=%s)",
                    ErrorCodes.VALIDATION_FAILED.name,
                    msg,
                    organization_id,
                    exc_info=True,
                )
                raise AppException(
                    message=msg,
                    status_code=400,
                    details={
                        "error_code": ErrorCodes.VALIDATION_FAILED.value,
                        "organization_id": organization_id,
                    },
                )
            return TenantSecretDTO(
                id=secret_id,
                organization_id=organization_id,
                scope=payload.scope,
                target_identifier=payload.target_identifier,
                storage_mode=SecretStorageMode.CLOUD_SECRET_MANAGER,
                secret_manager_version_uri=resolved_uri,
                encrypted_dek=None,
                ciphertext=None,
                nonce=None,
                kek_version=kek_version,
                masked_hint=masked_hint,
                updated_by=updated_by,
                updated_at=datetime.now(UTC),
            )

        dek = secrets.token_bytes(_DEK_BYTE_LENGTH)
        nonce = secrets.token_bytes(_AES_GCM_NONCE_BYTE_LENGTH)
        aad = self._build_aead_aad(
            organization_id=organization_id,
            scope=payload.scope,
            target_identifier=payload.target_identifier,
        )
        ciphertext = AESGCM(dek).encrypt(nonce, raw_secret.encode("utf-8"), aad)
        encrypted_dek = await self._wrap_dek(dek=dek, kek_version=kek_version)

        return TenantSecretDTO(
            id=secret_id,
            organization_id=organization_id,
            scope=payload.scope,
            target_identifier=payload.target_identifier,
            storage_mode=SecretStorageMode.ENVELOPE_KMS,
            secret_manager_version_uri=None,
            encrypted_dek=encrypted_dek,
            ciphertext=ciphertext,
            nonce=nonce,
            kek_version=kek_version,
            masked_hint=masked_hint,
            updated_by=updated_by,
            updated_at=datetime.now(UTC),
        )

    async def _decrypt_or_fetch_secret(self, record: TenantSecretDTO) -> str:
        """Decrypt an ENVELOPE_KMS record or fetch a CLOUD_SECRET_MANAGER version with zero fallback.

        Args:
            record: Persisted TenantSecretDTO record for the tenant.

        Returns:
            Non-empty decrypted plaintext secret string.

        Raises:
            ConfigurationError: With ErrorCodes.SECRET_RESOLUTION_FAILED if decryption or lookup fails.
        """
        settings = get_settings()
        timeout_sec = float(settings.mcp_default_timeout_seconds)
        try:
            if record.storage_mode == SecretStorageMode.CLOUD_SECRET_MANAGER:
                if (
                    record.secret_manager_version_uri is None
                    or not _SECRET_MANAGER_URI_PATTERN.match(record.secret_manager_version_uri)
                    or self._secret_manager_fetcher is None
                ):
                    raise ValueError("Cloud Secret Manager URI or fetcher is not configured.")
                async with asyncio.timeout(timeout_sec):
                    fetched = await self._secret_manager_fetcher.access_secret_version(
                        record.secret_manager_version_uri
                    )
                stripped = fetched.strip()
                if not stripped:
                    raise ValueError("Resolved Cloud Secret Manager payload is empty.")
                return stripped

            if (
                record.encrypted_dek is None
                or record.ciphertext is None
                or record.nonce is None
                or len(record.nonce) != _AES_GCM_NONCE_BYTE_LENGTH
            ):
                raise ValueError("Envelope KMS record is missing encrypted_dek, ciphertext, or 12-byte nonce.")

            dek = await self._unwrap_dek(record.encrypted_dek, record.kek_version)
            aad = self._build_aead_aad(
                organization_id=record.organization_id,
                scope=record.scope,
                target_identifier=record.target_identifier,
            )
            plaintext_bytes = AESGCM(dek).decrypt(record.nonce, record.ciphertext, aad)
            plaintext = plaintext_bytes.decode("utf-8").strip()
            if not plaintext:
                raise ValueError("Decrypted BYOK secret payload is empty.")
            return plaintext
        except Exception as exc:
            msg = (
                f"BYOK secret resolution failed for organization '{record.organization_id}' "
                f"and target '{record.target_identifier}' (secret_id='{record.id}')."
            )
            logger.error(
                "[SecretService] %s: %s",
                ErrorCodes.SECRET_RESOLUTION_FAILED.name,
                msg,
                exc_info=True,
                extra={
                    "error_code": ErrorCodes.SECRET_RESOLUTION_FAILED.value,
                    "organization_id": record.organization_id,
                    "secret_id": record.id,
                    "target_identifier": record.target_identifier,
                },
            )
            raise ConfigurationError(
                message=msg,
                details={
                    "error_code": ErrorCodes.SECRET_RESOLUTION_FAILED.value,
                    "organization_id": record.organization_id,
                    "secret_id": record.id,
                    "target_identifier": record.target_identifier,
                },
            ) from exc

    @staticmethod
    def _validate_target_identifier(
        *,
        organization_id: str,
        scope: SecretScope,
        target_identifier: str,
    ) -> None:
        """Validate that target_identifier matches the canonical contract for the selected SecretScope.

        Args:
            organization_id: Target organization identifier (org_<hex32>).
            scope: Capability scope (LLM_PROVIDER or MCP_GATEWAY).
            target_identifier: Candidate provider identifier or MCP gateway ID.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if target_identifier violates the scope contract.
        """
        if scope == SecretScope.LLM_PROVIDER:
            if target_identifier not in _VALID_LLM_PROVIDER_IDS:
                msg = (
                    f"Target identifier '{target_identifier}' is not a valid LLMProvider value "
                    f"for organization '{organization_id}'."
                )
                logger.error(
                    "[SecretService] %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    msg,
                    exc_info=True,
                )
                raise AppException(
                    message=msg,
                    status_code=400,
                    details={
                        "error_code": ErrorCodes.VALIDATION_FAILED.value,
                        "organization_id": organization_id,
                        "target_identifier": target_identifier,
                    },
                )
            return

        if scope == SecretScope.TELEMETRY:
            if target_identifier not in _VALID_TELEMETRY_TARGET_IDS:
                msg = (
                    f"Telemetry target_identifier '{target_identifier}' is not in "
                    f"{sorted(_VALID_TELEMETRY_TARGET_IDS)} for organization '{organization_id}'."
                )
                logger.error(
                    "[SecretService] %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    msg,
                    exc_info=True,
                )
                raise AppException(
                    message=msg,
                    status_code=400,
                    details={
                        "error_code": ErrorCodes.VALIDATION_FAILED.value,
                        "organization_id": organization_id,
                        "target_identifier": target_identifier,
                    },
                )
            return

        try:
            parse_prefixed_uuid7(target_identifier, expected_prefix=EntityPrefix.SYSTEM_CONFIG)
        except AppException as exc:
            msg = (
                f"MCP gateway target_identifier '{target_identifier}' must be a canonical "
                f"'sys_<hex32>' Opaque Stripe ID for organization '{organization_id}'."
            )
            logger.error(
                "[SecretService] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={
                    "error_code": ErrorCodes.VALIDATION_FAILED.value,
                    "organization_id": organization_id,
                    "target_identifier": target_identifier,
                },
            ) from exc

    @staticmethod
    def _raise_unconfigured_persistence_error() -> NoReturn:
        """Fail fast when neither entity_adapter nor uow_factory is configured on SecretService.

        Raises:
            ConfigurationError: Always raised with ErrorCodes.CONFIGURATION_ERROR.
        """
        msg = "SecretService requires either entity_adapter or uow_factory to be configured for persistence."
        logger.error(
            "[SecretService] %s: %s",
            ErrorCodes.CONFIGURATION_ERROR.name,
            msg,
            exc_info=True,
        )
        raise ConfigurationError(
            message=msg,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )

    @asynccontextmanager
    async def _acquire_entity_port(
        self,
        *,
        commit: bool = False,
    ) -> AsyncIterator[EntityPersistencePort]:
        """Yield the active EntityPersistencePort from entity_adapter or a uow_factory transaction.

        Args:
            commit: Whether to commit the UnitOfWork transaction upon successful exit.

        Yields:
            Configured EntityPersistencePort instance.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if persistence is unconfigured.
        """
        if self._entity_adapter is not None:
            yield self._entity_adapter
            return
        if self._uow_factory is not None:
            async with self._uow_factory() as uow:
                yield uow.entities
                if commit:
                    await uow.commit()
            return
        self._raise_unconfigured_persistence_error()

    async def _persist_secret_record(self, record: TenantSecretDTO) -> None:
        """Persist a TenantSecretDTO record via entity_adapter or uow_factory transaction.

        Args:
            record: Validated TenantSecretDTO to upsert.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if persistence is unconfigured.
        """
        async with self._acquire_entity_port(commit=True) as entities:
            await entities.upsert_tenant_secret(record)

    async def _delete_secret_record(self, secret_id: str) -> None:
        """Physically delete a tenant secret row via entity_adapter or uow_factory transaction.

        Args:
            secret_id: Canonical sec_<hex32> identifier to delete.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if persistence is unconfigured.
        """
        async with self._acquire_entity_port(commit=True) as entities:
            await entities.delete_collection_document("tenant_secrets", secret_id)

    async def _list_org_secret_records(self, organization_id: str) -> list[TenantSecretDTO]:
        """List active TenantSecretDTO records for an organization from persistent storage.

        Args:
            organization_id: Target organization identifier.

        Returns:
            List of TenantSecretDTO records belonging strictly to organization_id.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if persistence is unconfigured.
        """
        async with self._acquire_entity_port() as entities:
            persisted = await entities.list_tenant_secrets(organization_id=organization_id)
        return [item for item in persisted if item.organization_id == organization_id]

    async def _find_secret_record(
        self,
        *,
        organization_id: str,
        scope: SecretScope,
        target_identifier: str,
    ) -> TenantSecretDTO | None:
        """Find a TenantSecretDTO record matching (organization_id, scope, target_identifier).

        Args:
            organization_id: Tenant organization ID.
            scope: Capability scope (LLM_PROVIDER or MCP_GATEWAY).
            target_identifier: Provider enum value or gateway ID.

        Returns:
            Matching TenantSecretDTO if configured for the organization, otherwise None.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if persistence is unconfigured.
        """
        records = await self._list_org_secret_records(organization_id)
        for record in records:
            if record.scope == scope and record.target_identifier == target_identifier:
                return record
        return None

    async def _get_secret_record_by_id(self, secret_id: str) -> TenantSecretDTO | None:
        """Fetch a single TenantSecretDTO record by its primary ID from persistent storage.

        Args:
            secret_id: Canonical sec_<hex32> identifier.

        Returns:
            Matching TenantSecretDTO if present, otherwise None.

        Raises:
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if persistence is unconfigured.
        """
        async with self._acquire_entity_port() as entities:
            return await entities.get_tenant_secret(secret_id)

    @staticmethod
    def _to_response_dto(record: TenantSecretDTO) -> TenantSecretResponseDTO:
        """Project a persisted TenantSecretDTO into a zero-leakage TenantSecretResponseDTO.

        Args:
            record: Persisted TenantSecretDTO model.

        Returns:
            Redacted TenantSecretResponseDTO containing metadata and masked_hint only.
        """
        return TenantSecretResponseDTO(
            id=record.id,
            organization_id=record.organization_id,
            scope=record.scope,
            target_identifier=record.target_identifier,
            storage_mode=record.storage_mode,
            configured=True,
            masked_hint=record.masked_hint,
            kek_version=record.kek_version,
            updated_at=record.updated_at,
        )

    async def _record_audit_event(
        self,
        *,
        actor_id: str,
        action: str,
        organization_id: str,
        record: TenantSecretDTO,
    ) -> None:
        """Emit a structured audit log entry containing exclusively non-sensitive secret metadata.

        Args:
            actor_id: Initiating user ID.
            action: Audit event action name ('TENANT_SECRET_UPSERTED' or 'TENANT_SECRET_DELETED').
            organization_id: Owning organization ID.
            record: Target TenantSecretDTO metadata record.
        """
        if self.audit_service is None:
            return
        provider_val = ""
        gateway_val = ""
        if record.scope == SecretScope.LLM_PROVIDER:
            provider_val = record.target_identifier
        elif record.scope == SecretScope.MCP_GATEWAY:
            gateway_val = record.target_identifier
        await self.audit_service.log_event(
            actor_id=actor_id,
            action=action,
            organization_id=organization_id,
            target_id=record.id,
            details={
                "secret_id": record.id,
                "scope": record.scope.value,
                "provider": provider_val,
                "gateway_id": gateway_val,
                "storage_mode": record.storage_mode.value,
                "masked_hint": record.masked_hint,
            },
        )


_default_secret_service: SecretService | None = None


def get_secret_service() -> SecretService:
    """Return the process-scoped SecretService singleton instance for dependency injection.

    Returns:
        Configured SecretService instance bound to the registered UnitOfWorkFactory.
    """
    global _default_secret_service
    if _default_secret_service is None:
        _default_secret_service = SecretService(uow_factory=get_registered_uow_factory())
    return _default_secret_service


def reset_secret_service() -> None:
    """Reset the process-scoped SecretService singleton instance for hermetic test isolation."""
    global _default_secret_service
    _default_secret_service = None
