"""Core Dependency Injection Module.

Implements Singleton patterns for infrastructure services (DB, Engine, Registry)
using FastAPI's `Depends` system. Validates configurations and abstracts
storage backends (Local vs. Firestore) and Async Repositories.

Exports `Annotated` type aliases (e.g., `EngineDep`) for clean router injection.
"""

import logging
from typing import Annotated, Any

from arq.connections import ArqRedis, RedisSettings, create_pool
from fastapi import Depends, Header

from backend.core.engine import GraphEngine
from backend.database.factory import get_repository
from backend.database.repository import AbstractWorkflowRepository
from backend.database.wrapper import AbstractDatabase, get_db_client
from backend.exceptions import AuthenticationError, AppException, ErrorCodes
from backend.llm.provider import LLMProvider
from backend.models.auth import TokenData
from backend.services.agent_registry import AgentRegistry
from backend.services.audit_service import AuditService
from backend.services.auth import AuthService
from backend.services.file_driver import FileDriver
from backend.services.knowledge_base_service import KnowledgeBaseService
from backend.services.prompt_builder import PromptBuilder
from backend.services.usage_service import UsageService
from backend.settings import Settings, get_settings

# Alias for consistent dependency naming
get_settings_dep = get_settings

logger = logging.getLogger(__name__)

# Singleton Instances
_db_client_instance: AbstractDatabase | None = None
_repository_instance: AbstractWorkflowRepository | None = None
_registry_instance: AgentRegistry | None = None
_prompt_builder_instance: PromptBuilder | None = None
_storage_service_instance: FileDriver | None = None
_document_service_instance: Any | None = None
_audit_service_instance: AuditService | None = None
_auth_service_instance: AuthService | None = None
_usage_service_instance: UsageService | None = None
_knowledge_base_service_instance: KnowledgeBaseService | None = None
_engine_instance: GraphEngine | None = None


def get_db_client_dep() -> AbstractDatabase:
    """Dependency to provide a Singleton Database Client."""
    global _db_client_instance
    if _db_client_instance is None:
        logger.info("[Dependencies] Initializing Singleton DB Client...")
        _db_client_instance = get_db_client()
    return _db_client_instance


async def get_async_repository() -> AbstractWorkflowRepository:
    """Factory that returns the appropriate ASYNC-FIRST Repository implementation."""
    global _repository_instance

    if _repository_instance is not None:
        return _repository_instance

    settings = get_settings()

    # Pass the Singleton DB Client to ensure shared instance usage (Crucial for Tests/TinyDB)
    db_client = get_db_client_dep()

    # Factory handles logic for Firestore vs TinyDB and Mock/Local options.
    _repository_instance = await get_repository(settings, db_client=db_client)
    return _repository_instance


# Alias for compatibility if needed, but get_async_repository is the main entry point
get_repository_dep = get_async_repository


async def get_agent_registry_dep(
    repo: Annotated[AbstractWorkflowRepository, Depends(get_async_repository)],
) -> AgentRegistry:
    """Dependency to provide Singleton Agent Registry."""
    global _registry_instance
    if _registry_instance is None:
        # AgentRegistry expects a repo to do recursive updates.
        _registry_instance = AgentRegistry(repo)
        # Now we await discovery
        await _registry_instance.discover_and_register_agents()
    return _registry_instance


async def get_prompt_builder_dep(
    repo: Annotated[AbstractWorkflowRepository, Depends(get_async_repository)],
    registry: Annotated[AgentRegistry, Depends(get_agent_registry_dep)],
) -> PromptBuilder:
    """Dependency to provide Singleton Prompt Builder."""
    global _prompt_builder_instance
    if _prompt_builder_instance is None:
        _prompt_builder_instance = PromptBuilder(repo, registry)
    return _prompt_builder_instance


def get_storage_service_dep() -> FileDriver:
    """Dependency to provide a Singleton Storage Service."""
    global _storage_service_instance

    if _storage_service_instance is not None:
        return _storage_service_instance

    from backend.services.storage import get_storage_driver

    _storage_service_instance = get_storage_driver()
    logger.info(f"[Dependencies] Initialized Storage Service: {_storage_service_instance.__class__.__name__}")
    return _storage_service_instance


def get_document_service_dep(
    storage_client: Annotated[FileDriver, Depends(get_storage_service_dep)],
) -> Any:
    """Dependency to provide Singleton Document Service."""
    from backend.services.document_service import DocumentService

    return DocumentService(storage_client)


async def get_knowledge_base_service_dep(
    repo: Annotated[AbstractWorkflowRepository, Depends(get_async_repository)],
    storage_client: Annotated[FileDriver, Depends(get_storage_service_dep)],
    document_service: Annotated[Any, Depends(get_document_service_dep)],
    registry: Annotated[AgentRegistry, Depends(get_agent_registry_dep)],
    usage_service: Annotated[UsageService, Depends(get_usage_service)],
) -> KnowledgeBaseService:
    """Dependency to provide Singleton Knowledge Base Service."""
    global _knowledge_base_service_instance
    if _knowledge_base_service_instance is None:
        _knowledge_base_service_instance = KnowledgeBaseService(
            repository=repo,
            storage_client=storage_client,
            document_service=document_service,
            registry=registry,
            usage_service=usage_service,
        )
    return _knowledge_base_service_instance


def get_audit_service(
    repo: Annotated[AbstractWorkflowRepository, Depends(get_async_repository)],
) -> AuditService:
    """Dependency to provide Singleton Audit Service."""
    global _audit_service_instance
    if _audit_service_instance is None:
        _audit_service_instance = AuditService(repo)
    return _audit_service_instance


def get_auth_service(
    db_client: Annotated[AbstractDatabase, Depends(get_db_client_dep)],
    settings: Annotated[Settings, Depends(get_settings_dep)],
    audit_service: Annotated[AuditService, Depends(get_audit_service)],
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

        if settings.use_mock_db or settings.active_backend == "LOCAL":
            _auth_service_instance.ensure_root_user()

    return _auth_service_instance


def get_usage_service(
    repo: Annotated[AbstractWorkflowRepository, Depends(get_async_repository)],
) -> UsageService:
    """Dependency to provide Singleton Usage Service."""
    global _usage_service_instance
    if _usage_service_instance is None:
        _usage_service_instance = UsageService(repo)
    return _usage_service_instance


async def get_engine() -> GraphEngine:
    """Dependency to provide a Singleton GraphEngine."""
    global _engine_instance
    if _engine_instance is None:
        logger.info("[Dependencies] Initializing Singleton GraphEngine...")
        _engine_instance = GraphEngine()
    return _engine_instance


async def get_llm_provider(
    model_strategy: str,
    registry: Annotated[AgentRegistry, Depends(get_agent_registry_dep)],
    usage_service: Annotated[UsageService, Depends(get_usage_service)],
):
    """Dependency to provide a configured LLM Provider."""
    from backend.llm.provider import LLMFactory

    config = await registry.resolve_model_config(model_strategy)
    model_name = str(config.get("model_name", ""))
    provider_type = config.get("provider")

    if not provider_type:
        raise AppException(
            message=f"[get_llm_provider] 'provider' missing for strategy '{model_strategy}'.",
            status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR}
        )

    return LLMFactory.create_provider(provider_type=provider_type, model_name=model_name, usage_service=usage_service)


def get_llm_provider_factory(strategy: str):
    """Returns a dependency callable that provides an LLMProvider configured with the specified strategy.

    Enforces that the strategy must exist in the database configuration.
    """

    async def _provider_dependency(
        registry: Annotated[AgentRegistry, Depends(get_agent_registry_dep)],
        usage_service: Annotated[UsageService, Depends(get_usage_service)],
    ):
        return await get_llm_provider(strategy, registry, usage_service)

    return _provider_dependency


def get_llm_handler_dep(
    db_client: Annotated[AbstractDatabase, Depends(get_db_client_dep)],
):
    """Dependency to provide Singleton LLM Handler."""
    from backend.llm.handler import LLMHandler

    return LLMHandler(db_client)


def get_llm_factory_dep():
    """Dependency to provide LLM Factory."""
    from backend.llm.provider import LLMFactory

    return LLMFactory


async def get_arq_pool() -> ArqRedis:
    """Dependency to provide Arq Redis Pool."""
    settings = get_settings()
    return await create_pool(RedisSettings(host=settings.redis_host, port=settings.redis_port))


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
StorageDep = Annotated[FileDriver, Depends(get_storage_service_dep)]

# Provides the Document Service (handles text extraction and ingestion).
DocumentServiceDep = Annotated[Any, Depends(get_document_service_dep)]

# Provides the Knowledge Base Service.
KnowledgeBaseServiceDep = Annotated[KnowledgeBaseService, Depends(get_knowledge_base_service_dep)]

# Provides the central Graph Engine.
EngineDep = Annotated[GraphEngine, Depends(get_engine)]

# Provides the LLM Handler (manages conversational state and high-level LLM interactions).
# Note: Requires importing LLMHandler inside the file or using TYPE_CHECKING to avoid circular imports if lazily loaded.
# But get_llm_handler_dep returns the instance.
from backend.llm.handler import LLMHandler  # noqa: E402

LLMHandlerDep = Annotated[LLMHandler, Depends(get_llm_handler_dep)]


# --- Security / Auth Dependencies ---


async def get_current_user_from_header(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> TokenData:
    """Helper dependency to extract user from Bearer token.

    Allows accessing 'CurrentUser' in any router.
    """
    if not authorization:
        # For public endpoints or dev mode without token, we might relax this?
        # But for 'me' or 'executions' involving tenant data, we need it.
        # If no header, maybe return None?
        # Let's enforce it. If frontend doesn't send it, it's 401.
        raise AuthenticationError(
            message="Missing Authorization Header",
            details={"error_code": "AUTH_HEADER_MISSING"},
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise AuthenticationError(
            message="Invalid Authorization Scheme",
            details={"error_code": "AUTH_SCHEME_INVALID"},
        )

    try:
        return auth_service.verify_token(token)
    except ValueError as e:
        raise AuthenticationError(
            message=str(e),
            details={"error_code": "AUTH_TOKEN_INVALID"},
        ) from e


CurrentUserDep = Annotated[TokenData, Depends(get_current_user_from_header)]
