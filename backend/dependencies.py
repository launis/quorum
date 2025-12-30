from typing import Optional, Any
from fastapi import Depends
import logging
from backend.database.wrapper import get_db_client, AbstractDatabase
from backend.services.storage import AbstractStorage
from backend.database.repository import AbstractWorkflowRepository, TinyDBRepository
from backend.services.agent_registry import AgentRegistry
from backend.services.prompt_builder import PromptBuilder
from backend.core.engine import WorkflowEngine
# from backend.config import DB_PATH # Removed
from backend.settings import Settings, get_settings

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
    """
    Dependency to provide a Singleton Database Client.
    """
    global _db_client_instance
    if _db_client_instance is None:
        logger.info("[Dependencies] Initializing Singleton DB Client...")
        _db_client_instance = get_db_client()
    return _db_client_instance

def get_repository_dep(db_client: AbstractDatabase = Depends(get_db_client_dep)) -> AbstractWorkflowRepository:
    global _repository_instance
    if _repository_instance is None:
         # Choose implementation based on Client Type
         client_name = type(db_client).__name__
         
         if client_name == "FirestoreClient":
             try:
                 from backend.database.firestore_repo import FirestoreWorkflowRepository
                 logger.info("[Dependencies] Using FirestoreWorkflowRepository")
                 _repository_instance = FirestoreWorkflowRepository(db_client)
             except ImportError as e:
                 logger.error(f"Could not import FirestoreWorkflowRepository: {e}. Falling back to TinyDB.")
                 from backend.database.repository import TinyDBRepository
                 _repository_instance = TinyDBRepository(db_client)
         else:
             # Default / TinyDB
             from backend.database.repository import TinyDBRepository
             logger.info("[Dependencies] Using TinyDBRepository")
             _repository_instance = TinyDBRepository(db_client)
             
    return _repository_instance


def get_agent_registry_dep(repo: AbstractWorkflowRepository = Depends(get_repository_dep)) -> AgentRegistry:
    global _registry_instance
    if _registry_instance is None:
         _registry_instance = AgentRegistry(repo)
         _registry_instance.discover_and_register_agents()
    return _registry_instance

def get_prompt_builder_dep(
    repo: AbstractWorkflowRepository = Depends(get_repository_dep),
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
    """
    Dependency to provide DocumentService (Unified Ingestion).
    """
    from backend.services.document_service import DocumentService
    return DocumentService(storage_client)

def get_engine(
    repository: AbstractWorkflowRepository = Depends(get_repository_dep),
    registry: AgentRegistry = Depends(get_agent_registry_dep),
    prompt_builder: PromptBuilder = Depends(get_prompt_builder_dep),
    storage_service: AbstractStorage = Depends(get_storage_service_dep),
    document_service: Any = Depends(get_document_service_dep)
) -> WorkflowEngine:
    """
    Dependency to provide a Singleton WorkflowEngine, injected with Services.
    """
    global _engine_instance
    if _engine_instance is None:
        logger.info("[Dependencies] Initializing Singleton WorkflowEngine...")
        
        # MANUAL RESOLUTION IF CALLED WITHOUT DI
        from fastapi.params import Depends as DependsParams
        
        if isinstance(repository, DependsParams):
            repository = get_repository_dep()
        if isinstance(registry, DependsParams):
            # Registry depends on repository, so we must ensure repo is resolved first
            registry = get_agent_registry_dep(repository)
        if isinstance(prompt_builder, DependsParams):
             prompt_builder = get_prompt_builder_dep(repository, registry)
        if isinstance(storage_service, DependsParams):
             storage_service = get_storage_service_dep() # No args needed
        if isinstance(document_service, DependsParams):
             document_service = get_document_service_dep(storage_service)

        # Inject Services
        settings = get_settings()
        _engine_instance = WorkflowEngine(
            db_path=settings.start_db_path, 
            repository=repository,
            registry=registry,
            prompt_builder=prompt_builder,
            storage_client=storage_service,
            document_service=document_service
        )
        
        # Initialize Components - now handled by registry for agents, 
        # but manual components like DocumentProcessor?
        # Engine.register_component was moved to Registry. 
        # But DocumentProcessor is not an Agent. It is a manually registered component.
        # We should call registry.register_component here.
        registry.register_component("DocumentProcessor", "processor", "DocumentProcessor")
        
        # Discovery is already done in get_agent_registry_dep
        
    return _engine_instance

def get_llm_provider(
    model_strategy: str = "fast",
    registry: AgentRegistry = Depends(get_agent_registry_dep)
):
    """
    Dependency to provide a configured LLM Provider.
    By default uses the 'fast' strategy from the DB.
    """
    from backend.llm.provider import LLMFactory
    
    # Resolve strategy from DB
    config = registry.resolve_model_config(model_strategy)
    model_name = config.get("model_name")
    
    # We need provider too. Registry should store it (injected by resolve_model_config)
    provider_type = config.get("provider")
    
    if not provider_type:
         raise ValueError(f"[get_llm_provider] 'provider' missing for strategy '{model_strategy}'. DB Config Error.")
    
    return LLMFactory.create_provider(provider_type=provider_type, model_name=model_name)

def get_llm_handler_dep(db_client: AbstractDatabase = Depends(get_db_client_dep)):
    from backend.llm.handler import LLMHandler
    return LLMHandler(db_client)

def get_llm_factory_dep():
    from backend.llm.provider import LLMFactory
    return LLMFactory


