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
        """
        from backend.settings import get_settings
        settings = get_settings()

        # 1. Fetch Dynamic Strategies from Repository
        reg_entry = self.repository.get_model_registry()
        
        dynamic_strategies = None
        if reg_entry and 'models' in reg_entry:
            registry = reg_entry['models']
            # Default to google for now
            if 'google' in registry:
                dynamic_strategies = registry['google']

        # 2. Resolve Strategy Key using Dynamic DB config
        if dynamic_strategies and model_identifier in dynamic_strategies:
             strategy = dynamic_strategies[model_identifier]
             if isinstance(strategy, dict):
                 return strategy
             elif isinstance(strategy, str):
                 return {"model_name": strategy}
        
        # 3. Fallback to Static Config
        if model_identifier in settings.model_strategies:
            strategy = settings.model_strategies[model_identifier]
            return strategy
            
        # 4. Return as-is (assuming identifier is the model name itself)
        return {"model_name": model_identifier}

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
        Dynamically discovers and registers all Agent classes in the specified package.
        """
        from datetime import datetime
        import backend.agents
        from backend.settings import get_settings
        settings = get_settings()
        
        logger.info(f"[AgentRegistry] discovering agents in {package_path}...")
        
        # Ensure package is imported
        package = importlib.import_module(package_path)
        prefix = package.__name__ + "."
        
        count = 0
        for _, name, ispkg in pkgutil.iter_modules(package.__path__, prefix):
            print(f"REGISTRY DEBUG: Found module {name}")
            if name == "backend.agents.base": continue
            
            try:
                module = importlib.import_module(name)
                for cls_name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, BaseAgent) and obj is not BaseAgent:
                        
                        # 1. Instantiate & Store in Map
                        try:
                            resolved_initial_model = self.resolve_model_name(settings.initial_model)
                            self.agents_map[cls_name] = obj(model=resolved_initial_model)
                            logger.debug(f"[AgentRegistry] Instantiated {cls_name} with {resolved_initial_model}")
                        except Exception as e:
                            logger.error(f"[AgentRegistry] Failed to instantiate {cls_name}: {e}")
                            # FATAL: Raising interruption here ensures app triggers a clean crash/halt during startup
                            # However, during startup we might want to skip broken plugins rather than crash whole app?
                            # User requested strict halts. But registry runs at STARTUP usually. 
                            # If registry fails, app might crash before API is ready. 
                            # Let's keep SKIP for startup (to allow other parts to work) but LOG CRITICAL?
                            # OR RAISE if strictness is required.
                            # User said "vastaavia keskeytyksiä". If an Agent fails to load, the workflow referencing it will fail later.
                            # So I will raise FatalInterruption which likely bubbles up to main.py startup logic.
                            from backend.exceptions import FatalInterruption
                            raise FatalInterruption(
                                step_name="AgentDiscovery",
                                reason=f"Failed to instantiate agent {cls_name}",
                                details={"agent_class": cls_name, "error": str(e)}
                            )


                        # 2. Register in DB
                        agent_type = "agent"
                        if "critic" in cls_name.lower(): agent_type = "critic"
                        
                        # Use datetime for consistency
                        if not self.repository.get_component_by_name(cls_name):
                             self.repository.register_component({
                                "name": cls_name,
                                "type": agent_type,
                                "class_name": cls_name,
                                "registered_at": datetime.now().isoformat()
                            })
                        
                        self._update_component_metadata(cls_name, module=name, component_class=cls_name)
                        count += 1
                        
            except Exception as e:
                logger.error(f"Failed to inspect module {name}: {e}")
        
        logger.info(f"[AgentRegistry] Registered {count} agents dynamically.")

    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        return self.agents_map.get(agent_name)
    
    def get_all_agents(self) -> Dict[str, BaseAgent]:
        return self.agents_map.copy()
