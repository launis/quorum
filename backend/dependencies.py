"""Core Dependency Injection Module.

Implements Singleton patterns for infrastructure services (DB, Engine, Registry)
using FastAPI's `Depends` system. Validates configurations and abstracts
storage backends (Local vs. Firestore) and Async Repositories.

Exports `Annotated` type aliases (e.g., `EngineDep`) for clean router injection.
"""

import logging
from typing import Annotated, Any

from fastapi import Depends, Header, HTTPException

from backend.core.engine import WorkflowEngine
from backend.database.repository import AbstractWorkflowRepository, TinyDBRepository
from backend.database.wrapper import AbstractDatabase, get_db_client
from backend.llm.provider import LLMProvider
from backend.models.auth import TokenData
from backend.services.agent_registry import AgentRegistry
from backend.services.audit_service import AuditService
from backend.services.auth import AuthService
from backend.services.prompt_builder import PromptBuilder
from backend.services.storage import AbstractStorage
from backend.services.usage_service import UsageService
from backend.settings import Settings, get_settings

logger = logging.getLogger(__name__)

# Global Singleton Instances
_db_client_instance: AbstractDatabase | None = None
_repository_instance: AbstractWorkflowRepository | None = None
_registry_instance: AgentRegistry | None = None
_prompt_builder_instance: PromptBuilder | None = None
_storage_service_instance: AbstractStorage | None = None
_engine_instance: WorkflowEngine | None = None
_auth_service_instance: AuthService | None = None
_usage_service_instance: UsageService | None = None
_audit_service_instance: AuditService | None = None


def get_settings_dep() -> Settings:
    return get_settings()


def get_db_client_dep() -> AbstractDatabase:
    """Dependency to provide a Singleton Database Client."""
    global _db_client_instance
    if _db_client_instance is None:
        logger.info("[Dependencies] Initializing Singleton DB Client...")
        _db_client_instance = get_db_client()
    return _db_client_instance


def get_async_repository(db_client: AbstractDatabase = Depends(get_db_client_dep)) -> AbstractWorkflowRepository:
    """Factory that returns the appropriate ASYNC-FIRST Repository implementation."""
    global _repository_instance

    if _repository_instance is not None:
        return _repository_instance

    settings = get_settings()
    logger.warning(f"### DEBUG CONFIG ###: STORAGE='{settings.storage_backend}', MOCK_DB={settings.use_mock_db} (Env: {settings.environment})")

    # 1. Check for Firestore (Native Async)
    if settings.storage_backend.upper() == "FIRESTORE":
        if settings.use_mock_db:
             raise RuntimeError("CRITICAL CONFIG ERROR: STORAGE_BACKEND=FIRESTORE implies Real DB, but USE_MOCK_DB=True. Check your .bat file or .env variables.")
        
        from backend.database.firestore_repo import FirestoreWorkflowRepository

        logger.info("[Dependencies] Initializing Native Async Firestore.")
        _repository_instance = FirestoreWorkflowRepository(db_client)
    else:
        # 2. Async TinyDB (Dev)
        logger.info("[Dependencies] Initializing Async-First TinyDB.")
        _repository_instance = TinyDBRepository(db_client)

    return _repository_instance


# Alias for compatibility if needed, but get_async_repository is the main entry point
get_repository_dep = get_async_repository


async def get_agent_registry_dep(repo: AbstractWorkflowRepository = Depends(get_async_repository)) -> AgentRegistry:
    global _registry_instance
    if _registry_instance is None:
        # AgentRegistry expects a repo to do recursive updates.
        _registry_instance = AgentRegistry(repo)
        # Now we await discovery
        await _registry_instance.discover_and_register_agents()
    return _registry_instance


async def get_prompt_builder_dep(
    repo: AbstractWorkflowRepository = Depends(get_async_repository),
    registry: AgentRegistry = Depends(get_agent_registry_dep),
) -> PromptBuilder:
    global _prompt_builder_instance
    if _prompt_builder_instance is None:
        _prompt_builder_instance = PromptBuilder(repo, registry)
    return _prompt_builder_instance


def get_storage_service_dep() -> AbstractStorage:
    """Dependency to provide a Singleton Storage Service.
    Selects FirebaseStorage if STORAGE_BACKEND is 'FIRESTORE', otherwise LocalFileStorage.
    """
    global _storage_service_instance

    if _storage_service_instance is not None:
        return _storage_service_instance

    settings = get_settings()
    from backend.services.storage import FirebaseStorage, LocalFileStorage, NoOpStorage

    # Remove debug logging
    # logger.warning(f"### DEBUG CONFIG ###: ...")

    print(f"!!! DEBUG DEPENDENCIES !!! Backend={settings.storage_backend}, Bucket={settings.storage_bucket_name}", flush=True)

    if settings.storage_backend == "NONE":
        logger.info("[Dependencies] Storage disabled (NoOp).")
        print("!!! DEBUG !!! Selected NoOpStorage", flush=True)
        _storage_service_instance = NoOpStorage()

    # Logic matched with repository selection: FIRESTORE means Cloud
    elif settings.storage_backend.upper() == "FIRESTORE" and not settings.use_mock_db:
        bucket_name = settings.storage_bucket_name
        print(f"!!! DEBUG !!! Entering FIRESTORE block. Bucket: {bucket_name}", flush=True)
        
        if bucket_name:
            logger.info(f"[Dependencies] Initializing Firebase Cloud Storage (Bucket: {bucket_name}).")
            _storage_service_instance = FirebaseStorage(bucket_name=bucket_name)
        else:
            print("!!! DEBUG !!! Bucket Missing in FIRESTORE mode!", flush=True)
            # STRICT ZERO-FALLBACK
            msg = "CRITICAL: Firestore backend selected but STORAGE_BUCKET_NAME is missing. Zero-fallback policy in effect."
            logger.critical(msg)
            raise RuntimeError(msg)

    else:
        logger.info("[Dependencies] Initializing Local File Storage.")
        print("!!! DEBUG !!! Selected LocalFileStorage", flush=True)
        _storage_service_instance = LocalFileStorage()

    return _storage_service_instance


def get_document_service_dep(storage_client: AbstractStorage = Depends(get_storage_service_dep)) -> Any:
    from backend.services.document_service import DocumentService

    return DocumentService(storage_client)


def get_audit_service(
    repo: AbstractWorkflowRepository = Depends(get_async_repository),
) -> AuditService:
    """Dependency to provide Singleton Audit Service."""
    global _audit_service_instance
    if _audit_service_instance is None:
        _audit_service_instance = AuditService(repo)
    return _audit_service_instance


def get_auth_service(
    db_client: AbstractDatabase = Depends(get_db_client_dep),
    settings: Settings = Depends(get_settings_dep),
    audit_service: AuditService = Depends(get_audit_service),
) -> AuthService:
    """Dependency to provide Singleton Auth Service.
    Automatically ensures Root User exists.
    """
    global _auth_service_instance
    if _auth_service_instance is None:
        import os

        use_firebase = (settings.storage_backend.upper() == "FIRESTORE" and not settings.use_mock_db) or os.getenv(
            "USE_FIREBASE_AUTH", "false"
        ).lower() == "true"
        logger.info(f"[Dependencies] Initializing AuthService (Firebase={use_firebase})...")
        _auth_service_instance = AuthService(db_client, use_firebase=use_firebase, audit_service=audit_service)

        # Bootstrap Root User
        _auth_service_instance.ensure_root_user()

    return _auth_service_instance


def get_usage_service(
    repo: AbstractWorkflowRepository = Depends(get_async_repository),
) -> UsageService:
    """Dependency to provide Singleton Usage Service."""
    global _usage_service_instance
    if _usage_service_instance is None:
        _usage_service_instance = UsageService(repo)
    return _usage_service_instance


async def get_engine(
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    registry: AgentRegistry = Depends(get_agent_registry_dep),
    prompt_builder: PromptBuilder = Depends(get_prompt_builder_dep),
    storage_service: AbstractStorage = Depends(get_storage_service_dep),
    document_service: Any = Depends(get_document_service_dep),
) -> WorkflowEngine:
    """Dependency to provide a Singleton WorkflowEngine."""
    global _engine_instance
    if _engine_instance is None:
        logger.info("[Dependencies] Initializing Singleton WorkflowEngine (Async Mode)...")

        # Ensure Auth Service is explicitly initialized (sidesteps circular dependency issues)
        # This guarantees Root user exists before Engine starts working
        try:
            # We manually resolve dependencies for the auth service if needed,
            # but usually easiest just to let get_auth_service handle it if called via API.
            # However, let's allow lazy loading for Auth.
            pass
        except Exception as e:
            logger.warning(f"Could not pre-warm Auth Service: {e}")

        # MANUAL RESOLUTION IF CALLED WITHOUT DI
        from fastapi.params import Depends as DependsParams

        if isinstance(repository, DependsParams):
            repository = get_async_repository(get_db_client_dep())

        if isinstance(registry, DependsParams):
            registry = await get_agent_registry_dep(repository)

        if isinstance(prompt_builder, DependsParams):
            prompt_builder = await get_prompt_builder_dep(repository, registry)

        if isinstance(storage_service, DependsParams):
            storage_service = get_storage_service_dep()

        if isinstance(document_service, DependsParams):
            document_service = get_document_service_dep(storage_service)

        settings = get_settings()

        # Inject Services
        _engine_instance = WorkflowEngine(
            db_path=settings.start_db_path,
            repository=repository,
            registry=registry,
            prompt_builder=prompt_builder,
            storage_client=storage_service,
            document_service=document_service,
        )

        await registry.register_component("DocumentProcessor", "processor", "DocumentProcessor")

    return _engine_instance


async def get_llm_provider(
    model_strategy: str,
    registry: AgentRegistry = Depends(get_agent_registry_dep),
    usage_service: UsageService = Depends(get_usage_service),
):
    from backend.llm.provider import LLMFactory

    config = await registry.resolve_model_config(model_strategy)
    model_name = config.get("model_name")
    provider_type = config.get("provider")

    if not provider_type:
        raise ValueError(f"[get_llm_provider] 'provider' missing for strategy '{model_strategy}'.")

    return LLMFactory.create_provider(provider_type=provider_type, model_name=model_name, usage_service=usage_service)


def get_llm_provider_factory(strategy: str):
    """Returns a dependency callable that provides an LLMProvider configured with the specified strategy.
    Enforces that the strategy must exist in the database configuration.
    """

    async def _provider_dependency(
        registry: AgentRegistry = Depends(get_agent_registry_dep),
        usage_service: UsageService = Depends(get_usage_service),
    ):
        return await get_llm_provider(strategy, registry, usage_service)

    return _provider_dependency


def get_llm_handler_dep(db_client: AbstractDatabase = Depends(get_db_client_dep)):
    from backend.llm.handler import LLMHandler

    return LLMHandler(db_client)


def get_llm_factory_dep():
    from backend.llm.provider import LLMFactory

    return LLMFactory


# --- Type Aliases for Clean Injection (Dependency Injection Standards) ---
# These aliases facilitate cleaner function signatures in FastAPI router endpoints.
# Instead of `engine: WorkflowEngine = Depends(get_engine)`, use `engine: EngineDep`.

# Provides a configured LLM Provider for 'fast' tasks (low latency).
LLMProviderFast = Annotated[LLMProvider, Depends(get_llm_provider_factory("fast"))]

# Provides a configured LLM Provider for 'deep' tasks (reasoning/complex).
LLMProviderDeep = Annotated[LLMProvider, Depends(get_llm_provider_factory("deep"))]

# --- Standard Infrastructure Dependencies ---

# Provides the global application settings (loaded from env/pydantic).
SettingsDep = Annotated[Settings, Depends(get_settings_dep)]

# Provides the active database client (TinyDB or Firestore).
DatabaseDep = Annotated[AbstractDatabase, Depends(get_db_client_dep)]

# Provides the Async Repository layer (abstracts DB operations).
RepositoryDep = Annotated[AbstractWorkflowRepository, Depends(get_async_repository)]

# Provides the Auth Service (Identity & Roles).
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

# Provides the Agent Registry service (manages agent discovery and config).
RegistryDep = Annotated[AgentRegistry, Depends(get_agent_registry_dep)]

UsageServiceDep = Annotated[UsageService, Depends(get_usage_service)]

AuditServiceDep = Annotated[AuditService, Depends(get_audit_service)]

# Provides the Prompt Builder service (renders templates).
PromptBuilderDep = Annotated[PromptBuilder, Depends(get_prompt_builder_dep)]

# Provides the Storage Service (Local File System or Firebase Cloud Storage).
StorageDep = Annotated[AbstractStorage, Depends(get_storage_service_dep)]

# Provides the Document Service (handles text extraction and ingestion).
DocumentServiceDep = Annotated[Any, Depends(get_document_service_dep)]

# Provides the central Workflow Engine (orchestrates agents and execution).
EngineDep = Annotated[WorkflowEngine, Depends(get_engine)]

# Provides the LLM Handler (manages conversational state and high-level LLM interactions).
# Note: Requires importing LLMHandler inside the file or using TYPE_CHECKING to avoid circular imports if lazily loaded.
# But get_llm_handler_dep returns the instance.
from backend.llm.handler import LLMHandler

LLMHandlerDep = Annotated[LLMHandler, Depends(get_llm_handler_dep)]


# --- Security / Auth Dependencies ---


async def get_current_user_from_header(
    authorization: Annotated[str | None, Header()] = None, auth_service: AuthService = Depends(get_auth_service)
) -> TokenData:
    """Helper dependency to extract user from Bearer token.
    Allows accessing 'CurrentUser' in any router.
    """
    if not authorization:
        # For public endpoints or dev mode without token, we might relax this?
        # But for 'me' or 'executions' involving tenant data, we need it.
        # If no header, maybe return None?
        # Let's enforce it. If frontend doesn't send it, it's 401.
        raise HTTPException(status_code=401, detail="Missing Authorization Header")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid Authorization Scheme")

    try:
        return auth_service.verify_token(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


CurrentUserDep = Annotated[TokenData, Depends(get_current_user_from_header)]
