import json
import logging
from typing import Any, TypeVar

from pydantic import BaseModel

from backend.exceptions import AgentExecutionError
from backend.llm.provider import LLMFactory

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)


class LLMClient:
    """Singleton LLM Client wrapper adapting LLMFactory for structured outputs.

    Replaces legacy Instructor/OpenAI implementation with unified V2.9 LLMProvider.
    """

    _instance = None
    _config: "LLMProviderConfig | None" = None

    def __new__(cls, config: "LLMProviderConfig | None" = None) -> "LLMClient":
        # We modify Singleton to accept an injected configuration.
        # Note: If called repeatedly with different configs, a true Singleton might clash.
        # For Strategy Pattern, we often want fresh bound instances or ContextVars, 
        # but for backward compatibility we return the instance while updating its transient config.
        # Alternatively, we return a configured wrapper.
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
            
        if config:
            cls._instance._config = config
            
        return cls._instance

    def _initialize(self) -> None:
        """Initialize the client."""
        pass

    @classmethod
    async def from_strategy(cls, strategy_name: str, repository: Any = None) -> "LLMClient":
        """Factory: Create an LLMClient strictly bound to a database-defined Strategy.

        Args:
            strategy_name: The name of the strategy (e.g. 'fast', 'SearchHook', 'cognitive-audit').
            repository: Optional DB repository. If absent, attempts to resolve 'UnifiedWorkflowRepository' globally.
        
        Returns:
            A configured LLMClient instance ready for execution.
            
        Raises:
            ConfigurationError: If the Strategy does not exist.
        """
        from backend.exceptions import ConfigurationError
        from backend.models.llm import LLMProviderConfig, ModelRegistryConfig
        from backend.utils.pydantic_utils import inflate

        if not repository:
            # Fallback to Unified singleton if not passed
            from backend.database.repository import UnifiedWorkflowRepository
            repository = UnifiedWorkflowRepository()

        # 1. Fetch Raw Registry
        raw_registry = await repository.driver.get("system_config", "model_registry")
        if not raw_registry:
            raise ConfigurationError("System config 'model_registry' is missing or empty.")

        # 2. Strict Pydantic Inflation
        try:
            registry = inflate(raw_registry, ModelRegistryConfig)
        except Exception as e:
            raise ConfigurationError(f"Failed to parse strict ModelRegistryConfig: {e}")

        if not registry or not registry.models:
            raise ConfigurationError(f"ModelRegistry is severely corrupted: {registry}")

        # 3. Locate Strategy
        target_strategy = None
        target_provider = None

        for p_name, strategies in registry.models.items():
            if strategy_name in strategies:
                target_strategy = strategies[strategy_name]
                target_provider = p_name
                break

        if not target_strategy or not target_provider:
             raise ConfigurationError(f"Strategy '{strategy_name}' not found in any provider.")

        # 4. Construct Provider Config
        provider_config = LLMProviderConfig(
            id=f"{target_provider}/{strategy_name}",
            provider=target_provider,
            model_name=target_strategy.model_name,
            api_key=target_strategy.api_key,
            temperature=target_strategy.temperature,
            tpm_limit=target_strategy.tpm_limit,
            rpm_limit=target_strategy.rpm_limit,
            default_max_tokens=target_strategy.max_tokens,
            supports_grounding=target_strategy.supports_grounding
        )

        return cls(config=provider_config)

    async def run_structured_task(
        self,
        messages: list[dict[str, Any]],
        response_model: type[T],
        model: str | None = None,
        **kwargs: Any,
    ) -> T:
        """Execute a structured LLM task enforcing a Pydantic schema using LLMProvider.

        Args:
            messages: List of chat messages (system, user, etc.)
            response_model: The Pydantic model class to valid output against.
            model: Optional direct model override. If omitted, uses Strategy-bound config.
            **kwargs: Additional arguments for the completion call.

        Returns:
            The validated Pydantic model instance.
        """
        # 1. Parse Messages to prompt/system inputs expected by LLMProvider.generate
        # Note: LLMProvider interface currently takes (prompt, system_instruction).
        # We flatten the chat history here. For multi-turn support, LLMProvider needs update.
        system_instruction = None
        prompt = ""

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "system":
                if system_instruction:
                    system_instruction += "\n\n" + content
                else:
                    system_instruction = content
            elif role == "user":
                if prompt:
                    prompt += "\n\n" + content
                else:
                    prompt = content
            # Flattening assistant/other roles into prompt if necessary,
            # but currently specific Tasks use only S+U.

        if not prompt:
            # Fallback if no user message found (rare)
            prompt = messages[-1]["content"] if messages else ""

        # 2. Resolve Configuration (SSOT Priority)
        # If client was bound via Strategy Factory, it has priority unless explicitly overridden.
        if model is None:
            if not self._config:
                from backend.exceptions import AppException, ErrorCodes, status
                raise AppException(
                    message="Model Configuration Missing: No bound Strategy config and no 'model' var passed.",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
                )
            # Use Strategy Config
            target_model_name = self._config.model_name
            target_provider_type = "litellm" # Base Default
            
            # Apply Default Overrides from Strategy
            kwargs.setdefault("temperature", self._config.temperature)
            kwargs.setdefault("max_tokens", self._config.default_max_tokens)
            # Future: Tools could be injected here automatically from self._config.allowed_tools
        else:
            # Legacy pass-through
            target_model_name = model
            target_provider_type = "litellm"

        # 3. Create Provider via Factory
        provider = LLMFactory.create_provider(provider_type=target_provider_type, model_name=target_model_name)

        try:
            # 3. Generate with Structured Output
            response = await provider.generate(
                prompt=prompt,
                system_instruction=system_instruction,
                response_schema=response_model,
                temperature=kwargs.get("temperature"),
                max_tokens=kwargs.get("max_tokens"),
            )

            # 4. Parse Result
            # response.content is a JSON string (ensured by LiteLLMProvider)
            data = json.loads(response.content)
            return response_model.model_validate(data)

        except Exception as e:
            logger.error(f"[LLMClient] Execution Failed for model {model}: {e}")
            if "response" in locals() and response:
                logger.error(f"[LLMClient] Raw content causing error: {response.content}")
            raise AgentExecutionError(f"Structured Task Failed: {e}") from e

    async def run_chat(
        self,
        messages: list[dict[str, Any]],
        model: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a free-form chat task returning a string.

        Args:
            messages: List of chat messages.
            model: Model identifier. MUST be provided (Zero-Fallback).
            **kwargs: Additional args (temperature, max_tokens).

        Returns:
            The generated text content.
        """
        # ZERO-FALLBACK ENFORCEMENT
        # 2. Resolve Configuration (SSOT Priority)
        # If client was bound via Strategy Factory, it has priority unless explicitly overridden.
        if model is None:
            if not self._config:
                from backend.exceptions import AppException, ErrorCodes, status
                raise AppException(
                    message="Model Configuration Missing: No bound Strategy config and no 'model' var passed.",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
                )
            # Use Strategy Config
            target_model_name = self._config.model_name
            target_provider_type = "litellm"
            
            # Apply Default Overrides from Strategy
            kwargs.setdefault("temperature", self._config.temperature)
            kwargs.setdefault("max_tokens", self._config.default_max_tokens)
        else:
            # Legacy pass-through
            target_model_name = model
            target_provider_type = "litellm"

        # 1. Parse Prompt (Flattening)
        # Similar logic to run_structured_task
        system_instruction = None
        prompt = ""

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "system":
                system_instruction = (system_instruction + "\n\n" + content) if system_instruction else content
            elif role == "user":
                prompt = (prompt + "\n\n" + content) if prompt else content

        if not prompt:
            prompt = messages[-1]["content"] if messages else ""

        # 2. Create Provider
        provider = LLMFactory.create_provider(provider_type=target_provider_type, model_name=target_model_name)

        # 3. Generate
        try:
            response = await provider.generate(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=kwargs.get("temperature"),
                max_tokens=kwargs.get("max_tokens"),
                **kwargs,
            )
            return response.content
        except Exception as e:
            logger.error(f"[LLMClient] Chat Execution Failed: {e}")
            raise AgentExecutionError(f"Chat Task Failed: {e}") from e
