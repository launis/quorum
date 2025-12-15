from typing import Optional
from fastapi import Depends
import logging
from backend.database.wrapper import get_db_client, AbstractDatabase
from backend.database.repository import WorkflowRepository
from backend.services.agent_registry import AgentRegistry
from backend.services.prompt_builder import PromptBuilder
from backend.core.engine import WorkflowEngine
from backend.config import DB_PATH
from backend.settings import Settings, get_settings

logger = logging.getLogger(__name__)

# Global Singleton Instances
_db_client_instance: Optional[AbstractDatabase] = None
_repository_instance: Optional[WorkflowRepository] = None
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

def get_repository_dep(db_client: AbstractDatabase = Depends(get_db_client_dep)) -> WorkflowRepository:
    global _repository_instance
    if _repository_instance is None:
         _repository_instance = WorkflowRepository(db_client)
    return _repository_instance


    return _repository_instance

def get_agent_registry_dep(repo: WorkflowRepository = Depends(get_repository_dep)) -> AgentRegistry:
    global _registry_instance
    if _registry_instance is None:
         _registry_instance = AgentRegistry(repo)
         _registry_instance.discover_and_register_agents()
    return _registry_instance

def get_prompt_builder_dep(
    repo: WorkflowRepository = Depends(get_repository_dep),
    registry: AgentRegistry = Depends(get_agent_registry_dep)
) -> PromptBuilder:
    global _prompt_builder_instance
    if _prompt_builder_instance is None:
         _prompt_builder_instance = PromptBuilder(repo, registry)
    return _prompt_builder_instance

def get_engine(
    repository: WorkflowRepository = Depends(get_repository_dep),
    registry: AgentRegistry = Depends(get_agent_registry_dep),
    prompt_builder: PromptBuilder = Depends(get_prompt_builder_dep)
) -> WorkflowEngine:
    """
    Dependency to provide a Singleton WorkflowEngine, injected with Services.
    """
    global _engine_instance
    if _engine_instance is None:
        logger.info("[Dependencies] Initializing Singleton WorkflowEngine...")
        # Inject Services
        _engine_instance = WorkflowEngine(
            db_path=DB_PATH, 
            repository=repository,
            registry=registry,
            prompt_builder=prompt_builder
        )
        
        # Initialize Components - now handled by registry for agents, 
        # but manual components like DocumentProcessor?
        # Engine.register_component was moved to Registry. 
        # But DocumentProcessor is not an Agent. It is a manually registered component.
        # We should call registry.register_component here.
        registry.register_component("DocumentProcessor", "processor", "DocumentProcessor")
        
        # Discovery is already done in get_agent_registry_dep
        
    return _engine_instance
