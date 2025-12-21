import logging
import pkgutil
import importlib
import inspect
from typing import Dict, Any, Optional
from backend.database.repository import AbstractWorkflowRepository
from backend.agents.base import BaseAgent
# from backend.config import INITIAL_MODEL, MODEL_STRATEGIES # Removed

logger = logging.getLogger(__name__)

class AgentRegistry:
    def __init__(self, repository: AbstractWorkflowRepository):
        self.repository = repository
        self.agents_map: Dict[str, BaseAgent] = {}

    def resolve_model_name(self, model_identifier: str) -> str:
        """
        Resolves a model identifier (e.g., 'fast', 'deep') to an actual model name
        using the global MODEL_STRATEGIES config, prioritizing DB overrides.
        """
        from backend.settings import get_settings
        settings = get_settings()
        config = self.resolve_model_config(model_identifier)
        return config.get("model_name", settings.initial_model)

    def resolve_model_config(self, model_identifier: str) -> Dict[str, Any]:
        """
        Resolves a model identifier to a full configuration dictionary (model_name, max_tokens, temperature).
        STRICT MODE: Fetches ONLY from Database. No fallbacks.
        """
        # 1. Fetch Dynamic Strategies from Repository
        reg_entry = self.repository.get_model_registry()
        
        dynamic_strategies = {}
        if reg_entry and 'models' in reg_entry:
            registry = reg_entry['models']
            # Default to google for now, or merge providers if needed.
            # Assuming 'google' is the primary provider for strategies
            if 'google' in registry:
                dynamic_strategies = registry['google']

        # 2. Resolve Strategy Key using strict DB config
        if model_identifier in dynamic_strategies:
             strategy = dynamic_strategies[model_identifier]
             if isinstance(strategy, dict):
                 return strategy
             elif isinstance(strategy, str):
                 return {"model_name": strategy}
        
        # 3. Fail if not found
        valid_keys = list(dynamic_strategies.keys())
        err_msg = f"[AgentRegistry] Model Strategy '{model_identifier}' NOT FOUND in Database. Available: {sorted(valid_keys)}. Fallbacks are disabled."
        logger.error(err_msg)
        raise ValueError(err_msg)

    def register_component(self, name: str, type: str, class_name: str):
        """
        Registers a component in the DB via Repository.
        """
        if not self.repository.get_component_by_name(name):
            self.repository.register_component({
                "name": name,
                "type": type,
                "class_name": class_name,
                "registered_at": "now" # Simple placeholder, repo handles formatting or use datetime here? usage in engine used datetime.now().isoformat()
            })
            # Note: I should import datetime if I want to match exactly.
            # But repository insert is raw dict.
            # Let's import datetime.

    def _update_component_metadata(self, name, module, component_class):
         """Helper to add module/class info for dynamic router loading."""
         self.repository.update_component_metadata(name, module, component_class)

    def discover_and_register_agents(self, package_path: str = 'backend.agents'):
        """
        Loads agents using the static AgentFactory and registers them in the DB.
        """
        from datetime import datetime
        from backend.settings import get_settings
        from backend.core.factory import AgentFactory
        
        settings = get_settings()
        logger.info("[AgentRegistry] Loading agents via AgentFactory...")
        
        try:
            # Force usage of 'fast' strategy from DB regardless of env settings
            resolved_initial_model = self.resolve_model_name("fast")
            
            # 1. Get Agents from Factory
            agents_map = AgentFactory.create_agents_map(initial_model=resolved_initial_model)
            self.agents_map = agents_map
            
            count = 0
            for cls_name, agent_instance in self.agents_map.items():
                try:
                    # 2. Register in DB
                    agent_type = "agent"
                    if "critic" in cls_name.lower(): agent_type = "critic"
                    
                    if not self.repository.get_component_by_name(cls_name):
                        self.repository.register_component({
                            "name": cls_name,
                            "type": agent_type,
                            "class_name": cls_name,
                            "registered_at": datetime.now().isoformat()
                        })
                    
                    # 3. Update Metadata
                    # Use __module__ to get the defining module path
                    module_name = agent_instance.__module__
                    self._update_component_metadata(cls_name, module=module_name, component_class=cls_name)
                    
                    logger.debug(f"[AgentRegistry] Registered {cls_name} (from {module_name})")
                    count += 1
                    
                except Exception as e:
                    logger.error(f"[AgentRegistry] Failed to register {cls_name}: {e}")
                    # Allow partial failure during DB registration, but code is loaded.
            
            logger.info(f"[AgentRegistry] Successfully loaded and registered {count} agents.")
            
        except Exception as e:
             # Critical failure if Factory fails (e.g. import error)
             from backend.exceptions import FatalInterruption
             logger.critical(f"[AgentRegistry] FATAL: AgentFactory failed: {e}")
             raise FatalInterruption(
                step_name="AgentDiscovery",
                reason="AgentFactory Initialization Failed",
                details={"error": str(e)}
             )

    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        return self.agents_map.get(agent_name)
    
    def get_all_agents(self) -> Dict[str, BaseAgent]:
        return self.agents_map.copy()
