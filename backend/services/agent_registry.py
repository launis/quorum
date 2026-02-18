"""Registry service for managing Agent components and strategies."""

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from backend.core.registry import TaskRegistry
from backend.database.repository import AbstractWorkflowRepository
from backend.exceptions import (
    AppException,
    ConfigurationError,
    ErrorCodes,
    FatalInterruption,
)
from backend.models.domain.agent import ModelConfig

if TYPE_CHECKING:
    from backend.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Service for discovering, instantiating, and managing Agent components.

    Handles Model Strategy resolution against the database.
    """

    def __init__(self, repository: AbstractWorkflowRepository):
        """Initializes the registry.

        Args:
            repository (AbstractWorkflowRepository): Storage for component metadata and configs.

        """
        self.repository = repository
        self.agents_map: Dict[str, "BaseAgent"] = {}

    async def resolve_model_name(self, model_identifier: str) -> str:
        """Resolves a high-level model key (e.g. 'fast', 'smart') to a concrete model name.

        Prioritizes database configuration over any hardcoded defaults.

        Args:
            model_identifier (str): The strategy key.

        Returns:
            str: The concrete model identifier (e.g. 'gemini-1.5-flash').

        Raises:
            AppException: If model name is missing in config.
        """
        config = await self.resolve_model_config(model_identifier)
        # ZERO-FALLBACK ENFORCEMENT:
        # We expect 'resolve_model_config' to fully hydrate the dictionary or raise an error.
        # We do NOT fallback to settings.initial_model anymore.
        # model_name is required in ModelConfig, so access directly
        return config.model_name

    async def resolve_model_config(self, model_identifier: str) -> ModelConfig:
        """Resolves a model identifier to a full configuration object.

        STRICT MODE: Fetches ONLY from Database. No fallbacks.
        NO FALLBACKS: If the strategy is not found, we RAISE an error. We do NOT use defaults.

        Args:
            model_identifier (str): The strategy key.

        Returns:
            ModelConfig: Strict configuration object.

        Raises:
            AppException: If strategy not found in DB.

        """
        # 1. Fetch Dynamic Strategies from Repository
        reg_entry = await self.repository.get_model_registry()

        logger.info(f"[AgentRegistry] Resolving config for identifier: '{model_identifier}'")

        dynamic_strategies_map = {}
        if reg_entry and "models" in reg_entry:
            dynamic_strategies_map = reg_entry["models"]
            logger.debug(f"[AgentRegistry] Loaded Registry with providers: {list(dynamic_strategies_map.keys())}")
        else:
            logger.error("[AgentRegistry] Registry is EMPTY or missing 'models' key!")

        # 2. Search for Strategy across all Providers
        # This makes the code vendor-agnostic.
        for provider_key, strategies in dynamic_strategies_map.items():
            found_strategy = None
            
            # Case A: Direct Match (e.g. "fast")
            if model_identifier in strategies:
                logger.info(f"[AgentRegistry] Found identifier '{model_identifier}' in provider '{provider_key}'")
                found_strategy = strategies[model_identifier]
            
            # Case B: Scoped Match (e.g. "google/deep")
            elif "/" in model_identifier:
                parts = model_identifier.split("/", 1)
                if parts[0] == provider_key and parts[1] in strategies:
                     logger.info(f"[AgentRegistry] Found scoped identifier '{model_identifier}' in provider '{provider_key}'")
                     found_strategy = strategies[parts[1]]

            if found_strategy:
                logger.debug(f"[AgentRegistry] Raw Strategy Data: {found_strategy}")

                # Normalize result
                config = {}
                if isinstance(found_strategy, dict):
                    config = found_strategy.copy()
                elif isinstance(found_strategy, str):
                    config = {"model_name": found_strategy}

                # Inject provider if missing (derived from registry structure)
                if "provider" not in config:
                    config["provider"] = provider_key

                # CHAINED RESOLUTION: If model_name is a reference (not a real model name),
                # resolve it recursively. Real model names contain "/" (e.g., "vertex_ai/gemini-2.5-pro")
                # References are simple aliases like "fast" or "deep".
                model_name = config.get("model_name", "")
                if model_name and "/" not in model_name and model_name != model_identifier:
                    # This is a reference to another alias - resolve recursively
                    logger.debug(f"[AgentRegistry] Chained resolution: '{model_identifier}' -> '{model_name}'")
                    referenced_config = await self.resolve_model_config(model_name)
                    
                    # Convert referenced_config (ModelConfig) to dict to serve as base
                    base_dict = referenced_config.model_dump()
                    
                    # Apply overrides from current alias definition
                    for k, v in config.items():
                        if k != "model_name":
                            if k in base_dict or hasattr(ModelConfig, k):
                                base_dict[k] = v
                            else:
                                if "extra_params" not in base_dict:
                                    base_dict["extra_params"] = {}
                                base_dict["extra_params"][k] = v

                    # Re-instantiate
                    merged_config = ModelConfig(**base_dict)
                    return merged_config
                else:
                    logger.debug(f"[AgentRegistry] Direct resolution (No Chain). Final Config: {config}")

                    return ModelConfig(
                        model_name=config.get("model_name", "unknown"),
                        provider=config.get("provider", "unknown"),
                        max_tokens=config.get("max_tokens"),
                        temperature=config.get("temperature"),
                        top_p=config.get("top_p"),
                        supports_grounding=config.get("supports_grounding", False),
                        extra_params={k: v for k, v in config.items() if k not in ["model_name", "provider", "max_tokens", "temperature", "top_p", "supports_grounding"]}
                    )

        # 3. Fail if not found
        # Collect available strategies for error message
        available = []
        for _p, s in dynamic_strategies_map.items():
            available.extend(s.keys())

        err_msg = (
            f"[AgentRegistry] Model Strategy '{model_identifier}' NOT FOUND in Database. "
            f"Available: {sorted(list(set(available)))}. Fallbacks are disabled."
        )
        logger.error(err_msg)
        raise ConfigurationError(err_msg)

    async def register_component(self, name: str, type: str, class_name: str) -> None:
        """Registers a new component definition in the database.

        Args:
            name (str): Component ID/Name.
            type (str): Type category (e.g. 'agent', 'tool').
            class_name (str): Python class name.

        """
        if not await self.repository.get_component_by_name(name):
            await self.repository.register_component(
                {
                    "id": name,
                    "name": name,
                    "type": type,
                    "class_name": class_name,
                    "registered_at": datetime.now(),
                }
            )

    async def _update_component_metadata(self, name: str, module: str, component_class: str) -> None:
        """Helper to add module/class info for dynamic router loading.

        Updates existing component records with runtime metadata.

        Args:
            name (str): Component ID.
            module (str): Module path.
            component_class (str): Class name.
        """
        await self.repository.update_component_metadata(name, module, component_class)

    async def discover_and_register_agents(self, package_path: str = "backend.agents") -> None:
        """Registers agents found in TaskRegistry into the Database.

        Replaces legacy AgentFactory. Scans TaskRegistry for tasks with agent metadata.

        Args:
            package_path (str): Unused (legacy signature).

        """
        logger.info("[AgentRegistry] Discovering agents via TaskRegistry...")

        try:
            count = 0
            # Scan TaskRegistry for tasks that are actually Agents
            for task_key, task_def in TaskRegistry._tasks.items():
                meta = task_def.metadata
                if not meta or "agent_class" not in meta:
                    continue

                agent_class_name = meta["agent_class"]
                module_name = meta.get("module", "unknown")
                agent_type = meta.get("type", "agent")

                try:
                    # 1. Register in DB
                    if not await self.repository.get_component_by_name(task_key):
                        await self.repository.register_component(
                            {
                                "id": task_key,
                                "name": task_key,
                                "type": agent_type,
                                "class_name": agent_class_name,
                                "registered_at": datetime.now(),
                            }
                        )

                    # 2. Update Metadata
                    await self._update_component_metadata(
                        task_key,
                        module=module_name,
                        component_class=agent_class_name
                    )

                    logger.debug(f"[AgentRegistry] Registered {task_key} ({agent_class_name})")
                    count += 1

                except Exception as e:
                    logger.error(f"[AgentRegistry] Failed to register {task_key}: {e}")

            logger.info(f"[AgentRegistry] Successfully registered {count} agents from TaskMetadata.")

        except Exception as e:
            logger.critical(f"[AgentRegistry] FATAL: Discovery failed: {e}")
            raise FatalInterruption(
                step_name="AgentDiscovery",
                reason="TaskRegistry Scan Failed",
                details={"error": str(e)},
            ) from e

    def get_agent(self, agent_name: str) -> Optional["BaseAgent"]:
        """Retrieves an instantiated agent by name.

        Args:
            agent_name (str): Class name of the agent.

        Returns:
            Optional[BaseAgent]: The agent instance or None.

        """
        return self.agents_map.get(agent_name)

    def get_all_agents(self) -> Dict[str, "BaseAgent"]:
        """Returns all registered agent instances.

        Returns:
            Dict[str, BaseAgent]: Map of name -> instance.

        """
        return self.agents_map.copy()

    def get_agent_config(self, agent_name: str) -> Optional["BaseAgent"]:
        """Retrieves agent configuration (the Agent Instance itself).

        Used by functional tasks to resolve model strategies.
        
        Args:
            agent_name (str): Agent name.

        Returns:
            Optional[BaseAgent]: The agent instance if found.
        """
        return self.get_agent(agent_name)

    async def get_all_strategies(self) -> Dict[str, str]:
        """Retrieves all available model strategies and their resolved model names.

        Returns:
            Dict[str, str]: Map of strategy name (e.g. 'fast') -> resolved model name (e.g. 'vertex_ai/gemini-2.5-flash').
        """
        reg_entry = await self.repository.get_model_registry()
        if not reg_entry or "models" not in reg_entry:
            return {}

        # 1. Collect all raw keys
        all_keys = set()
        for provider_strategies in reg_entry["models"].values():
            all_keys.update(provider_strategies.keys())

        # 2. Resolve each strategy safely
        strategies = {}
        for key in all_keys:
            try:
                # We reuse resolve_model_name because it handles alias chaining
                model_name = await self.resolve_model_name(key)
                strategies[key] = model_name
            except Exception as e:
                # Skip invalid strategies (e.g. missing recursive definitions)
                logger.warning(f"[AgentRegistry] Skipping unresolvable strategy '{key}': {e}")
        
        return strategies

    async def update_model_registry_config(self, registry_data: Dict[str, Dict[str, str]]) -> None:
        """Updates the system's model registry configuration.

        Args:
            registry_data (dict): The new configuration map.
        """
        # Wrap in expected structure if needed, or just pass 'models' key?
        # Repository expects 'registry_data' which it saves.
        # implementation details: repo.update_model_registry saves the dict passed to it.
        # But list_strategies expects 'models' key in the saved record.
        # So we should save {"models": registry_data}
        
        payload = {"models": registry_data}
        await self.repository.update_model_registry(payload)
        logger.info(f"[AgentRegistry] Updated model registry with {len(registry_data)} strategies.")
