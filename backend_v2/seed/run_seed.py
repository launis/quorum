"""V2 PostgreSQL 19 Authoritative Seeder Script.

Reads from backend_v2/seed/seed_data.json, validates 100% of entities in memory
against strict Pydantic V2 domain models and DAGCompilerService, and idempotently
upserts all collections into PostgreSQL 19 via PostgresUnitOfWork.

Usage:
Execute the script from the project root using `uv run python`:

```powershell
uv run python backend_v2/seed/run_seed.py
uv run python backend_v2/seed/run_seed.py postgres --dry-run
```
"""

from __future__ import annotations

import argparse
import asyncio
import importlib
import json
import logging
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Annotated, Protocol

from pydantic import BaseModel, ConfigDict, Field, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend_v2.database.factory import create_unit_of_work
from backend_v2.database.interfaces import QuorumUnitOfWork
from backend_v2.database.postgres.uow import PostgresUnitOfWork
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import (
    SYSTEM_ROOT_USER_ID,
    Organization,
    SystemOrganizations,
    TenantSecretCreateDTO,
    TokenData,
    User,
)
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import AnyPromptBlock
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.system_config import SystemConfigMCPGateways, SystemConfigModelRegistry
from backend_v2.models.domain.task_brief import TaskBrief
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.enums import LLMProvider, SecretScope, SecretStorageMode, UserRole
from backend_v2.models.state import StateProjector as _StateProjector
from backend_v2.seed.seed_registry import SeedCollectionName
from backend_v2.services.auth.secret_service import SecretService
from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService
from backend_v2.settings import get_settings

_ = _StateProjector

SEED_PATH = Path(get_settings().seed_data_path)
DEFAULT_MCP_GATEWAY_ID: str = "mcp_0195f3a00000700080008172bda70c86"

TOPOLOGICAL_SEED_ORDER: tuple[str, ...] = (
    SeedCollectionName.ORGANIZATIONS.value,
    SeedCollectionName.USERS.value,
    SeedCollectionName.MODEL_REGISTRIES.value,
    SeedCollectionName.MCP_GATEWAYS.value,
    SeedCollectionName.PROMPT_BLOCKS.value,
    SeedCollectionName.TASK_BRIEFS.value,
    SeedCollectionName.STEPS.value,
    SeedCollectionName.WORKFLOWS.value,
    SeedCollectionName.OUTPUT_PROFILES.value,
    SeedCollectionName.EXECUTIONS.value,
)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

__all__ = [
    "DEFAULT_MCP_GATEWAY_ID",
    "LocalSeedSecretsSettings",
    "PROJECT_ROOT",
    "SEED_PATH",
    "TOPOLOGICAL_SEED_ORDER",
    "ValidatedSeedBufferDTO",
    "_provision_root_firebase_user",
    "_seed_local_secrets",
    "_seed_postgres",
    "main",
    "seed_database",
    "validate_all_seed_collections",
    "verify_seed_table_counts",
]


class _FirebaseUserRecordProtocol(Protocol):
    """Protocol for a Firebase Admin user record."""

    @property
    def uid(self) -> str: ...


class _FirebaseAuthClientProtocol(Protocol):
    """Protocol for Firebase Admin Auth user management operations."""

    def get_user_by_email(self, email: str) -> _FirebaseUserRecordProtocol: ...

    def create_user(
        self,
        *,
        uid: str,
        email: str,
        password: str,
        email_verified: bool,
    ) -> _FirebaseUserRecordProtocol: ...

    def update_user(
        self,
        uid: str,
        *,
        email: str,
        password: str,
        email_verified: bool,
    ) -> _FirebaseUserRecordProtocol: ...


class LocalSeedSecretsSettings(BaseSettings):
    """Typed settings model loading local workspace secrets from .env.secrets.local.

    Attributes:
        secret_ai_studio_api_key: Google AI Studio API key for Root System Organization.
        secret_vertex_ai_sa_json: Google Cloud Vertex AI and Firebase Admin Service Account JSON.
        secret_openai_api_key: OpenAI API key for Root System Organization.
        secret_anthropic_api_key: Anthropic API key for Root System Organization.
        secret_tavily_api_key: Tavily MCP Gateway API key for Root System Organization.
        secret_logfire_token: Pydantic Logfire write token for Root System Organization.
        secret_logfire_read_token: Pydantic Logfire read token for Root System Organization.
        secret_root_user_email: Root user email address for Firebase Authentication provisioning.
        secret_root_user_password: Root user password for Firebase Authentication provisioning.
    """

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env.secrets.local"),
        env_file_encoding="utf-8",
        extra="forbid",
        case_sensitive=False,
    )

    secret_ai_studio_api_key: Annotated[
        SecretStr | None,
        Field(default=None, description="Google AI Studio API key for Root System Organization."),
    ] = None
    secret_vertex_ai_sa_json: Annotated[
        SecretStr | None,
        Field(default=None, description="Vertex AI and Firebase Admin Service Account JSON string."),
    ] = None
    secret_openai_api_key: Annotated[
        SecretStr | None,
        Field(default=None, description="OpenAI API key for Root System Organization."),
    ] = None
    secret_anthropic_api_key: Annotated[
        SecretStr | None,
        Field(default=None, description="Anthropic API key for Root System Organization."),
    ] = None
    secret_tavily_api_key: Annotated[
        SecretStr | None,
        Field(default=None, description="Tavily MCP Gateway API key for Root System Organization."),
    ] = None
    secret_logfire_token: Annotated[
        SecretStr | None,
        Field(default=None, description="Logfire telemetry write token for Root System Organization."),
    ] = None
    secret_logfire_read_token: Annotated[
        SecretStr | None,
        Field(default=None, description="Logfire telemetry read token for Root System Organization."),
    ] = None
    secret_root_user_email: Annotated[
        SecretStr | None,
        Field(default=None, description="Root user email address for Firebase Authentication provisioning."),
    ] = None
    secret_root_user_password: Annotated[
        SecretStr | None,
        Field(default=None, description="Root user password for Firebase Authentication provisioning."),
    ] = None

    def iter_secret_entries(self) -> list[TenantSecretCreateDTO]:
        """Return all non-empty secret entries as validated TenantSecretCreateDTO payloads.

        Returns:
            List of TenantSecretCreateDTO instances ready for envelope encryption.
        """
        entries: list[TenantSecretCreateDTO] = []
        _append_secret_entry(
            entries,
            SecretScope.LLM_PROVIDER,
            LLMProvider.AI_STUDIO.value,
            self.secret_ai_studio_api_key,
        )
        _append_secret_entry(
            entries,
            SecretScope.LLM_PROVIDER,
            LLMProvider.VERTEX_AI.value,
            self.secret_vertex_ai_sa_json,
        )
        _append_secret_entry(
            entries,
            SecretScope.LLM_PROVIDER,
            LLMProvider.OPENAI.value,
            self.secret_openai_api_key,
        )
        _append_secret_entry(
            entries,
            SecretScope.LLM_PROVIDER,
            LLMProvider.ANTHROPIC.value,
            self.secret_anthropic_api_key,
        )
        _append_secret_entry(
            entries,
            SecretScope.MCP_GATEWAY,
            DEFAULT_MCP_GATEWAY_ID,
            self.secret_tavily_api_key,
        )
        _append_secret_entry(
            entries,
            SecretScope.TELEMETRY,
            "logfire",
            self.secret_logfire_token,
        )
        _append_secret_entry(
            entries,
            SecretScope.TELEMETRY,
            "logfire_read",
            self.secret_logfire_read_token,
        )
        return entries


def _extract_stripped_secret(raw_secret: SecretStr | None) -> str:
    """Extract a stripped plaintext string from an optional SecretStr.

    Args:
        raw_secret: Optional SecretStr value.

    Returns:
        Stripped secret string, or empty string when unset.
    """
    value = ""
    if raw_secret is not None:
        value = raw_secret.get_secret_value().strip()
    return value


def _append_secret_entry(
    entries: list[TenantSecretCreateDTO],
    scope: SecretScope,
    target_identifier: str,
    raw_secret: SecretStr | None,
) -> None:
    """Append a TenantSecretCreateDTO to entries when raw_secret is non-empty.

    Args:
        entries: Target list of TenantSecretCreateDTO payloads.
        scope: Canonical SecretScope for the secret.
        target_identifier: Canonical target identifier within the scope.
        raw_secret: Optional SecretStr value from LocalSeedSecretsSettings.
    """
    stripped = _extract_stripped_secret(raw_secret)
    if stripped:
        entries.append(
            TenantSecretCreateDTO(
                scope=scope,
                target_identifier=target_identifier,
                plaintext_secret=SecretStr(stripped),
                storage_mode=SecretStorageMode.ENVELOPE_KMS,
            )
        )


class ValidatedSeedBufferDTO(BaseModel):
    """Strongly typed container for validated in-memory seed collections.

    Attributes:
        system_config: Validated system configuration entities.
        workflows: Validated workflow blueprint entities.
        prompt_blocks: Validated polymorphic prompt block entities.
        task_briefs: Validated reusable task brief entities.
        steps: Validated workflow step entities.
        output_profiles: Validated output profile entities.
        executions: Validated historical execution records.
        organizations: Validated tenant organization entities.
        users: Validated user entities.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    model_registries: Annotated[
        list[SystemConfigModelRegistry],
        Field(default_factory=list, description="Validated model registry entities."),
    ]
    mcp_gateways: Annotated[
        list[SystemConfigMCPGateways],
        Field(default_factory=list, description="Validated MCP gateway entities."),
    ]
    workflows: Annotated[
        list[Workflow],
        Field(default_factory=list, description="Validated workflow blueprint entities."),
    ]
    prompt_blocks: Annotated[
        list[AnyPromptBlock],
        Field(default_factory=list, description="Validated polymorphic prompt block entities."),
    ]
    task_briefs: Annotated[
        list[TaskBrief],
        Field(default_factory=list, description="Validated reusable task brief entities."),
    ]
    steps: Annotated[
        list[Step],
        Field(default_factory=list, description="Validated workflow step entities."),
    ]
    output_profiles: Annotated[
        list[OutputProfile],
        Field(default_factory=list, description="Validated output profile entities."),
    ]
    executions: Annotated[
        list[ExecutionRecord],
        Field(default_factory=list, description="Validated historical execution records."),
    ]
    organizations: Annotated[
        list[Organization],
        Field(default_factory=list, description="Validated tenant organization entities."),
    ]
    users: Annotated[
        list[User],
        Field(default_factory=list, description="Validated user entities."),
    ]

    def get_collection(self, col_key: str) -> Sequence[BaseModel]:
        """Return the typed collection sequence by canonical collection name.

        Args:
            col_key: Canonical collection key name.

        Returns:
            Sequence of validated Pydantic domain models for the requested collection.

        Raises:
            KeyError: If col_key does not match a registered seed collection.
        """
        match col_key:
            case "model_registries":
                return self.model_registries
            case "mcp_gateways":
                return self.mcp_gateways
            case "workflows":
                return self.workflows
            case "prompt_blocks":
                return self.prompt_blocks
            case "task_briefs":
                return self.task_briefs
            case "steps":
                return self.steps
            case "output_profiles":
                return self.output_profiles
            case "executions":
                return self.executions
            case "organizations":
                return self.organizations
            case "users":
                return self.users
            case _:
                raise KeyError(f"Unknown seed collection: '{col_key}'")

    def __getitem__(self, col_key: str) -> Sequence[BaseModel]:
        """Retrieve a seed collection sequence by registry key name.

        Args:
            col_key: Canonical collection key name.

        Returns:
            Sequence of validated Pydantic domain models for the requested collection.

        Raises:
            KeyError: If col_key does not match a registered seed collection.
        """
        return self.get_collection(col_key)

    def __contains__(self, col_key: object) -> bool:
        """Verify whether a collection key name belongs to standard seed collections.

        Args:
            col_key: Candidate collection key to check.

        Returns:
            True if col_key is a recognized seed collection identifier, otherwise False.
        """
        return col_key in {
            "model_registries",
            "mcp_gateways",
            "workflows",
            "prompt_blocks",
            "task_briefs",
            "steps",
            "output_profiles",
            "executions",
            "organizations",
            "users",
        }


def _fail_fast(msg: str, error: Exception) -> AppException:
    """Log a structured RFC 7807 error and return a typed AppException.

    Args:
        msg: The failure message describing the validation context.
        error: The caught exception instance.

    Returns:
        Typed application exception configured with ErrorCodes.VALIDATION_FAILED.
    """
    logger.error(
        "[Seeder] %s: [CRITICAL FAIL FAST] %s - %s",
        ErrorCodes.VALIDATION_FAILED.name,
        msg,
        str(error),
        exc_info=True,
    )
    print(f"\033[91m[CRITICAL FAIL FAST] {msg}\n{str(error)}\033[0m")
    return AppException(
        message=f"{msg}: {error}",
        status_code=400,
        details={"error_code": ErrorCodes.VALIDATION_FAILED},
    )


def validate_all_seed_collections(seed_data: object) -> ValidatedSeedBufferDTO:
    """Validate 100% of seed items in-memory across all collections before any database operations.

    Stage 1 of Two-Stage Seeding: validates schemas and DAG workflows in memory.
    If ANY item is invalid, triggers Fail-Fast before tables are touched.

    Args:
        seed_data: Raw JSON payload loaded from the seed file.

    Returns:
        Validated domain models grouped per collection.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if schema or DAG validation fails.
    """
    try:
        validated_buffer = ValidatedSeedBufferDTO.model_validate(seed_data)
    except ValidationError as ve:
        raise _fail_fast("Seed buffer validation failed", ve) from ve
    except Exception as e:
        raise _fail_fast("Processing error during seed validation", e) from e

    for wf in validated_buffer.workflows:
        try:
            DAGCompilerService.validate_workflow(wf)
        except Exception as e:
            raise _fail_fast(f"Workflow DAG validation failed for '{wf.id}'", e) from e

    return validated_buffer


async def _seed_local_secrets(
    uow: QuorumUnitOfWork,
    secrets_settings: LocalSeedSecretsSettings,
) -> int:
    """Encrypt and upsert all configured local secrets into PostgreSQL 19 tenant_secrets.

    Args:
        uow: Active QuorumUnitOfWork instance.
        secrets_settings: Validated LocalSeedSecretsSettings instance.

    Returns:
        Number of secrets encrypted and upserted under the Root System Organization.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED or ErrorCodes.STORAGE_ACCESS_FAILED if secret encryption or persistence fails.
    """
    entries = secrets_settings.iter_secret_entries()
    if not entries:
        return 0

    secret_service = SecretService(entity_adapter=uow.entities)
    root_initiator = TokenData(
        id=SYSTEM_ROOT_USER_ID,
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM.value,
        email="root@example.com",
        mfa_verified=True,
    )
    count = 0
    for secret_payload in entries:
        await secret_service.upsert_tenant_secret(
            initiator=root_initiator,
            organization_id=SystemOrganizations.ROOT_SYSTEM.value,
            payload=secret_payload,
        )
        count += 1
    print(f"[Seeder V2] Upserted {count} encrypted secrets to 'tenant_secrets'.")
    return count


def _resolve_firebase_auth_client(
    raw_sa_json: str,
    firebase_auth_client: _FirebaseAuthClientProtocol | None,
) -> _FirebaseAuthClientProtocol:
    """Resolve or initialize the Firebase Admin Auth client using the Service Account JSON.

    Args:
        raw_sa_json: Raw JSON string containing the GCP/Firebase Service Account credentials.
        firebase_auth_client: Optional injected Firebase Auth client for unit testing.

    Returns:
        Initialized Firebase Admin Auth module or injected client.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if Service Account JSON is malformed or Firebase Admin fails to initialize.
    """
    if not raw_sa_json.startswith("{"):
        raise _fail_fast(
            "SECRET_VERTEX_AI_SA_JSON must be a valid JSON object string for Firebase ROOT provisioning",
            ValueError("Malformed Service Account JSON prefix"),
        )
    try:
        sa_payload: object = json.loads(raw_sa_json)
    except ValueError as exc:
        raise _fail_fast(
            "Failed to parse SECRET_VERTEX_AI_SA_JSON for Firebase ROOT provisioning",
            exc,
        ) from exc

    if firebase_auth_client is not None:
        return firebase_auth_client

    try:
        firebase_admin = importlib.import_module("firebase_admin")
        credentials_mod = importlib.import_module("firebase_admin.credentials")
        auth_mod = importlib.import_module("firebase_admin.auth")
        if not firebase_admin._apps:
            cred = credentials_mod.Certificate(sa_payload)
            firebase_admin.initialize_app(cred)
        resolved_auth: _FirebaseAuthClientProtocol = auth_mod
        return resolved_auth
    except Exception as exc:
        raise _fail_fast("Failed to initialize Firebase Admin SDK for ROOT provisioning", exc) from exc


async def _provision_root_firebase_user(
    uow: QuorumUnitOfWork,
    secrets_settings: LocalSeedSecretsSettings,
    firebase_auth_client: _FirebaseAuthClientProtocol | None = None,
) -> None:
    """Provision or synchronize ONLY the ROOT user in Firebase Authentication and PostgreSQL 19.

    Args:
        uow: Active QuorumUnitOfWork instance.
        secrets_settings: Validated LocalSeedSecretsSettings instance.
        firebase_auth_client: Optional injected Firebase Auth client for unit testing.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if ROOT credentials are incomplete, Service Account JSON is missing, or Firebase/DB sync fails.
    """
    raw_email = _extract_stripped_secret(secrets_settings.secret_root_user_email)
    raw_password = _extract_stripped_secret(secrets_settings.secret_root_user_password)
    if not raw_email and not raw_password:
        return

    if not raw_email or not raw_password:
        raise _fail_fast(
            "Both SECRET_ROOT_USER_EMAIL and SECRET_ROOT_USER_PASSWORD must be provided together",
            ValueError("Incomplete ROOT Firebase credentials"),
        )

    raw_sa_json = _extract_stripped_secret(secrets_settings.secret_vertex_ai_sa_json)
    if not raw_sa_json:
        raise _fail_fast(
            "SECRET_VERTEX_AI_SA_JSON is required to provision ROOT user in Firebase Authentication",
            ValueError("Missing SECRET_VERTEX_AI_SA_JSON"),
        )

    fb_auth = _resolve_firebase_auth_client(raw_sa_json, firebase_auth_client)

    existing_fb_user: _FirebaseUserRecordProtocol | None = None
    try:
        existing_fb_user = fb_auth.get_user_by_email(raw_email)
    except Exception as exc:
        exc_type_name = type(exc).__name__
        if exc_type_name != "UserNotFoundError" and "not found" not in str(exc).lower():
            raise _fail_fast("Firebase get_user_by_email failed during ROOT provisioning", exc) from exc

    try:
        if existing_fb_user is not None:
            fb_auth.update_user(
                existing_fb_user.uid,
                email=raw_email,
                password=raw_password,
                email_verified=True,
            )
            resolved_uid = str(existing_fb_user.uid)
        else:
            created_fb_user = fb_auth.create_user(
                uid=SYSTEM_ROOT_USER_ID,
                email=raw_email,
                password=raw_password,
                email_verified=True,
            )
            resolved_uid = str(created_fb_user.uid)
    except Exception as exc:
        raise _fail_fast("Firebase ROOT user create/update failed", exc) from exc

    root_user = await uow.entities.get_user(SYSTEM_ROOT_USER_ID)
    if root_user is None:
        raise _fail_fast(
            f"ROOT user '{SYSTEM_ROOT_USER_ID}' missing in database after seed batch",
            ValueError("Missing ROOT user row"),
        )

    updated_root = root_user.model_copy(update={"firebase_uid": resolved_uid, "email": raw_email})
    await uow.entities.upsert_user(updated_root)
    print(f"[Seeder V2] Synchronized ROOT user '{SYSTEM_ROOT_USER_ID}' with Firebase Authentication.")


async def verify_seed_table_counts(
    uow: QuorumUnitOfWork,
    expected_counts: Mapping[str, int],
) -> dict[str, int]:
    """Verify row counts across the 11 core PostgreSQL 19 tables via EntityPersistencePort.

    Args:
        uow: Active QuorumUnitOfWork instance.
        expected_counts: Mapping of collection/table name to minimum expected row count.

    Returns:
        Dictionary mapping canonical table name to actual row count in PostgreSQL 19.

    Raises:
        AppException: With ErrorCodes.STORAGE_ACCESS_FAILED or ErrorCodes.VALIDATION_FAILED if row counts fail verification.
    """
    return await uow.entities.verify_seed_table_counts(expected_counts)


def _resolve_seed_secrets_settings(
    uow: QuorumUnitOfWork | None,
    secrets_settings: LocalSeedSecretsSettings | None,
) -> LocalSeedSecretsSettings:
    """Resolve LocalSeedSecretsSettings for seeding or dry-run validation.

    Args:
        uow: Optional QuorumUnitOfWork passed by caller.
        secrets_settings: Optional explicit LocalSeedSecretsSettings override.

    Returns:
        Validated LocalSeedSecretsSettings instance.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if .env.secrets.local fails schema validation.
    """
    if secrets_settings is not None:
        return secrets_settings
    try:
        if uow is None:
            return LocalSeedSecretsSettings()
        return LocalSeedSecretsSettings(_env_file=None)
    except ValidationError as ve:
        raise _fail_fast("Local seed secrets validation failed", ve) from ve


async def _seed_postgres(
    seed_data: object,
    dry_run: bool = False,
    uow: QuorumUnitOfWork | None = None,
    secrets_settings: LocalSeedSecretsSettings | None = None,
    firebase_auth_client: _FirebaseAuthClientProtocol | None = None,
) -> dict[str, int]:
    """Seed the PostgreSQL 19 database with validated V2 domain models and local secrets.

    Enforces Two-Stage Pre-Flight In-Memory Validation:
    Stage 1: Validates 100% of seed items and local secrets settings in-memory.
    Stage 2: Executes transactional idempotent UPSERT across all collections in topological order,
        encrypts local secrets into tenant_secrets, provisions the ROOT Firebase user,
        and verifies row counts across all 11 tables via SELECT count(*).

    Args:
        seed_data: Raw JSON payload loaded from the seed file.
        dry_run: If True, validate in memory and bypass database modifications.
        uow: Optional QuorumUnitOfWork instance for dependency injection in tests.
        secrets_settings: Optional LocalSeedSecretsSettings override for testing.
        firebase_auth_client: Optional Firebase Auth client override for testing.

    Returns:
        Mapping of table name to verified row count.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED or ErrorCodes.STORAGE_ACCESS_FAILED if validation or seeding fails.
    """
    validated_buffers = validate_all_seed_collections(seed_data)
    resolved_secrets = _resolve_seed_secrets_settings(uow, secrets_settings)
    print("[Seeder V2] Pre-flight in-memory validation passed for all collections.")

    expected_counts: dict[str, int] = {
        "organizations": max(1, len(validated_buffers.organizations)),
        "users": max(1, len(validated_buffers.users)),
        "tenant_secrets": len(resolved_secrets.iter_secret_entries()),
        "model_registries": max(1, len(validated_buffers.model_registries)),
        "mcp_gateways": max(1, len(validated_buffers.mcp_gateways)),
        "prompt_blocks": max(1, len(validated_buffers.prompt_blocks)),
        "task_briefs": max(1, len(validated_buffers.task_briefs)),
        "steps": max(1, len(validated_buffers.steps)),
        "workflows": max(1, len(validated_buffers.workflows)),
        "output_profiles": max(1, len(validated_buffers.output_profiles)),
        "executions": len(validated_buffers.executions),
        "report_artifacts": 0,
        "report_binaries": 0,
    }

    if dry_run:
        print("[Seeder V2] DRY-RUN ACTIVE: Completed validation without modifying PostgreSQL 19.")
        return expected_counts

    resolved_uow: QuorumUnitOfWork = uow if uow is not None else create_unit_of_work(get_settings())
    try:
        if isinstance(resolved_uow, PostgresUnitOfWork):
            await resolved_uow.pool_manager.apply_migrations()
        async with resolved_uow as active_uow:
            for col_key in TOPOLOGICAL_SEED_ORDER:
                items = validated_buffers.get_collection(col_key)
                upserted_count = await active_uow.entities.seed_collection_batch(col_key, items)
                print(f"[Seeder V2] Upserted {upserted_count} items to '{col_key}'.")

            seeded_secrets_count = await _seed_local_secrets(active_uow, resolved_secrets)
            expected_counts["tenant_secrets"] = seeded_secrets_count
            await _provision_root_firebase_user(
                active_uow,
                resolved_secrets,
                firebase_auth_client=firebase_auth_client,
            )

            actual_counts = await verify_seed_table_counts(active_uow, expected_counts)
        if isinstance(resolved_uow, PostgresUnitOfWork):
            await resolved_uow.pool_manager.apply_migrations()
    except AppException:
        raise
    except Exception as exc:
        raise _fail_fast("PostgreSQL 19 transactional seeding failed", exc) from exc

    print(f"[Seeder V2] Verified PostgreSQL 19 table counts: {actual_counts}")
    return actual_counts


async def seed_database(
    target: str = "postgres",
    dry_run: bool = False,
    uow: QuorumUnitOfWork | None = None,
) -> dict[str, int]:
    """Orchestrate the seeding process for PostgreSQL 19.

    Args:
        target: Target database environment ('postgres', 'local', or 'all').
        dry_run: If True, bypass database modifications.
        uow: Optional QuorumUnitOfWork override for testing.

    Returns:
        Mapping of table name to verified row count.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED or ErrorCodes.STORAGE_ACCESS_FAILED if target is invalid or seeding fails.
        SystemExit: If seed file is missing on disk.
    """
    normalized_target = target.strip().lower()
    if normalized_target not in ("postgres", "postgresql", "local", "all"):
        raise _fail_fast(
            f"Unsupported seed target '{target}'. Only PostgreSQL 19 ('postgres') is supported",
            ValueError(f"Invalid target: {target}"),
        )

    print(f"--- V2 SEEDING TARGET: POSTGRESQL 19 ({normalized_target.upper()}) ---")

    if not SEED_PATH.exists():
        logger.critical("[Seeder] %s: Seed file not found at %s", ErrorCodes.FILE_NOT_FOUND.name, SEED_PATH)
        print(f"\033[91mCRITICAL: Seed file not found at {SEED_PATH}\033[0m")
        sys.exit(1)

    with open(SEED_PATH, encoding="utf-8") as f:
        data = json.load(f)

    counts = await _seed_postgres(data, dry_run=dry_run, uow=uow)
    print("[SUCCESS] V2 Seeded PostgreSQL 19 Database.")
    return counts


def main(argv: list[str] | None = None) -> None:
    """Parse command line arguments and initialize the async PostgreSQL 19 seeding loop.

    Args:
        argv: Optional list of argument strings for invocation.

    Raises:
        SystemExit: If argument parsing fails or an unhandled seeding error occurs.
    """
    parser = argparse.ArgumentParser(description="Unified V2 PostgreSQL 19 Database Seeder")
    parser.add_argument(
        "targets",
        nargs="*",
        default=["postgres"],
        choices=["postgres", "postgresql", "local", "all"],
        help="Target environment (defaults to 'postgres').",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate seed data in memory without modifying PostgreSQL 19.",
    )

    args = parser.parse_args(argv)
    target_list: list[str] = list(args.targets)
    if not target_list:
        target_list = ["postgres"]

    try:
        asyncio.run(seed_database(target_list[0], dry_run=args.dry_run))
    except (OSError, RuntimeError, ValueError, AppException) as e:
        logger.critical(
            "[Seeder] %s: Failed to seed PostgreSQL 19: %s",
            ErrorCodes.INTERNAL_SERVER_ERROR.name,
            e,
            exc_info=True,
        )
        print(f"\033[91m[ERROR] Failed to seed PostgreSQL 19: {e}\033[0m")
        raise SystemExit(1) from e

    print("\n[SUCCESS] All requested targets completed successfully.")


if __name__ == "__main__":
    main()
