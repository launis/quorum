"""Registry service for managing Agent components and strategies."""

import logging
from datetime import datetime
from typing import Any

from backend.agents.base import BaseAgent
from backend.database.repository import AbstractWorkflowRepository

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
        self.agents_map: dict[str, BaseAgent] = {}

    async def resolve_model_name(self, model_identifier: str) -> str:
        """Resolves a high-level model key (e.g. 'fast', 'smart') to a concrete model name.

        Prioritizes database configuration over any hardcoded defaults.

        Args:
            model_identifier (str): The strategy key.

        Returns:
            str: The concrete model identifier (e.g. 'gemini-1.5-flash').

        """
        from backend.settings import get_settings

        settings = get_settings()
        config = await self.resolve_model_config(model_identifier)
        return config.get("model_name", settings.initial_model)

    async def resolve_model_config(self, model_identifier: str) -> dict[str, Any]:
        """Resolves a model identifier to a full configuration dictionary (name, tokens, temp, provider).

        STRICT MODE: Fetches ONLY from Database. No fallbacks.

        Args:
            model_identifier (str): The strategy key.

        Returns:
            Dict[str, Any]: Configuration object (e.g. {'model_name': '...', 'provider': '...'}).

        Raises:
            ValueError: If strategy not found in DB.

        """
        # 1. Fetch Dynamic Strategies from Repository
        reg_entry = await self.repository.get_model_registry()

        dynamic_strategies_map = {}
        if reg_entry and "models" in reg_entry:
            dynamic_strategies_map = reg_entry["models"]

        # 2. Search for Strategy across all Providers
        # This makes the code vendor-agnostic.
        for provider_key, strategies in dynamic_strategies_map.items():
            if model_identifier in strategies:
                strategy = strategies[model_identifier]

                # Normalize result
                config = {}
                if isinstance(strategy, dict):
                    config = strategy.copy()
                elif isinstance(strategy, str):
                    config = {"model_name": strategy}

                # Inject provider if missing (derived from registry structure)
                if "provider" not in config:
                    config["provider"] = provider_key

                return config

        # 3. Fail if not found
        # Collect available strategies for error message
        available = []
        for _p, s in dynamic_strategies_map.items():
            available.extend(s.keys())

        from backend.exceptions import ConfigurationError

        err_msg = (
            f"[AgentRegistry] Model Strategy '{model_identifier}' NOT FOUND in Database. "
            f"Available: {sorted(list(set(available)))}. Fallbacks are disabled."
        )
        logger.error(err_msg)
        raise ConfigurationError(err_msg)

    async def register_component(self, name: str, type: str, class_name: str):
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
                    "registered_at": datetime.now().isoformat(),
                }
            )

    async def _update_component_metadata(self, name, module, component_class):
        """Helper to add module/class info for dynamic router loading.

        Updates existing component records with runtime metadata.

        Args:
            name (str): Component ID.
            module (str): Module path.
            component_class (str): Class name.
        """
        await self.repository.update_component_metadata(name, module, component_class)

    async def discover_and_register_agents(self, package_path: str = "backend.agents"):
        """Loads agents using the static AgentFactory and registers them in the DB.

        This bootstraps the system with available code components.

        Args:
            package_path (str): Python package path to scan (default 'backend.agents').

        Raises:
            FatalInterruption: If AgentFactory fails to load.

        """
        from backend.core.factory import AgentFactory
        from backend.settings import get_settings

        get_settings()
        logger.info("[AgentRegistry] Loading agents via AgentFactory...")

        try:
            # Agents are initialized without a pre-set model.
            # The PipelineRunner handles dynamic configuration per step.
            agents_map = AgentFactory.create_agents_map(initial_model=None)
            self.agents_map = agents_map

            count = 0
            for cls_name, agent_instance in self.agents_map.items():
                try:
                    # 2. Register in DB
                    agent_type = "agent"
                    if "critic" in cls_name.lower():
                        agent_type = "critic"

                    if not await self.repository.get_component_by_name(cls_name):
                        await self.repository.register_component(
                            {
                                "id": cls_name,
                                "name": cls_name,
                                "type": agent_type,
                                "class_name": cls_name,
                                "registered_at": datetime.now().isoformat(),
                            }
                        )

                    # 3. Update Metadata
                    # Use __module__ to get the defining module path
                    module_name = agent_instance.__module__
                    await self._update_component_metadata(cls_name, module=module_name, component_class=cls_name)

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
                step_name="AgentDiscovery", reason="AgentFactory Initialization Failed", details={"error": str(e)}
            ) from e

    def get_agent(self, agent_name: str) -> BaseAgent | None:
        """Retrieves an instantiated agent by name.

        Args:
            agent_name (str): Class name of the agent.

        Returns:
            Optional[BaseAgent]: The agent instance or None.

        """
        return self.agents_map.get(agent_name)

    def get_all_agents(self) -> dict[str, BaseAgent]:
        """Returns all registered agent instances.

        Returns:
            Dict[str, BaseAgent]: Map of name -> instance.

        """
        return self.agents_map.copy()
