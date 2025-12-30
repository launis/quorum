from typing import Optional, Any, Annotated
from fastapi import Depends
import logging
from backend.database.wrapper import get_db_client, AbstractDatabase
from backend.services.storage import AbstractStorage
from backend.database.repository import AbstractWorkflowRepository, TinyDBRepository
from backend.services.agent_registry import AgentRegistry
from backend.services.prompt_builder import PromptBuilder
from backend.core.engine import WorkflowEngine
from backend.settings import Settings, get_settings
from backend.llm.provider import LLMProvider

logger = logging.getLogger(__name__)

# Global Singleton Instances
_db_client_instance: Optional[AbstractDatabase] = None
_repository_instance: Optional[AbstractWorkflowRepository] = None
_registry_instance: Optional[AgentRegistry] = None
_prompt_builder_instance: Optional[PromptBuilder] = None
_engine_instance: Optional[WorkflowEngine] = None

def get_settings_dep() -> Settings:
    return get_settings()

def get_db_client_dep() -> AbstractDatabase:
    """Dependency to provide a Singleton Database Client."""
    global _db_client_instance
    if _db_client_instance is None:
        logger.info("[Dependencies] Initializing Singleton DB Client...")
        _db_client_instance = get_db_client()
    return _db_client_instance

def get_async_repository(
     db_client: AbstractDatabase = Depends(get_db_client_dep)
) -> AbstractWorkflowRepository:
    """
    Factory that returns the appropriate ASYNC-FIRST Repository implementation.
    """
    global _repository_instance
    
    if _repository_instance is not None:
        return _repository_instance

    settings = get_settings()

    # 1. Check for Firestore (Native Async)
    if settings.storage_backend.upper() == "FIRESTORE" and not settings.use_mock_db:
        try:
            from backend.database.firestore_repo import FirestoreWorkflowRepository
            logger.info("[Dependencies] Initializing Native Async Firestore.")
            _repository_instance = FirestoreWorkflowRepository(db_client)
        except ImportError as e:
             logger.warning(f"[Dependencies] Native Async Firestore failed to import: {e}. Falling back to TinyDB.")
             _repository_instance = TinyDBRepository(db_client)
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
    registry: AgentRegistry = Depends(get_agent_registry_dep)
) -> PromptBuilder:
    global _prompt_builder_instance
    if _prompt_builder_instance is None:
         _prompt_builder_instance = PromptBuilder(repo, registry)
    return _prompt_builder_instance

def get_storage_service_dep() -> AbstractStorage:
    from backend.services.storage import get_storage_client
    return get_storage_client()

def get_document_service_dep(storage_client: AbstractStorage = Depends(get_storage_service_dep)) -> Any:
    from backend.services.document_service import DocumentService
    return DocumentService(storage_client)

async def get_engine(
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    registry: AgentRegistry = Depends(get_agent_registry_dep),
    prompt_builder: PromptBuilder = Depends(get_prompt_builder_dep),
    storage_service: AbstractStorage = Depends(get_storage_service_dep),
    document_service: Any = Depends(get_document_service_dep)
) -> WorkflowEngine:
    """
    Dependency to provide a Singleton WorkflowEngine.
    """
    global _engine_instance
    if _engine_instance is None:
        logger.info("[Dependencies] Initializing Singleton WorkflowEngine (Async Mode)...")
        
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
            document_service=document_service
        )
        
        await registry.register_component("DocumentProcessor", "processor", "DocumentProcessor")
        
    return _engine_instance

async def get_llm_provider(
    model_strategy: str,
    registry: AgentRegistry = Depends(get_agent_registry_dep)
):
    from backend.llm.provider import LLMFactory
    config = await registry.resolve_model_config(model_strategy)
    model_name = config.get("model_name")
    provider_type = config.get("provider")
    
    if not provider_type:
         raise ValueError(f"[get_llm_provider] 'provider' missing for strategy '{model_strategy}'.")
    
    return LLMFactory.create_provider(provider_type=provider_type, model_name=model_name)

def get_llm_provider_factory(strategy: str):
    """
    Returns a dependency callable that provides an LLMProvider configured with the specified strategy.
    Enforces that the strategy must exist in the database configuration.
    """
    async def _provider_dependency(registry: AgentRegistry = Depends(get_agent_registry_dep)):
        return await get_llm_provider(strategy, registry)
    return _provider_dependency

def get_llm_handler_dep(db_client: AbstractDatabase = Depends(get_db_client_dep)):
    from backend.llm.handler import LLMHandler
    return LLMHandler(db_client)

def get_llm_factory_dep():
    from backend.llm.provider import LLMFactory
    return LLMFactory

# --- Type Aliases for Clean Injection ---
LLMProviderFast = Annotated[LLMProvider, Depends(get_llm_provider_factory("fast"))]
LLMProviderDeep = Annotated[LLMProvider, Depends(get_llm_provider_factory("deep"))]
