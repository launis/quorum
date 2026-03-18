import json
import logging
from typing import Any, TypeVar

from pydantic import BaseModel

from backend_v2.exceptions import AgentExecutionError, ErrorCodes
from backend_v2.llm.provider import LLMFactory
from backend_v2.models.llm import LLMProviderConfig

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)


class LLMClient:
    """LLM Client wrapper adapting LLMFactory for structured outputs.

    Replaces legacy Instructor/OpenAI implementation with unified V2.9 LLMProvider.
    """

    def __init__(self, config: dict[str, Any] | LLMProviderConfig | None = None) -> None:
        self._config = config
        self.model_config: dict[str, Any] | None = None
        self._initialize()

    def _initialize(self) -> None:
        """Initialize the client."""
        pass

    @classmethod
    async def from_strategy(cls, strategy_name: str, repository: Any = None) -> LLMClient:
        """Factory: Create an LLMClient strictly bound to a database-defined Strategy.

        Args:
            strategy_name: The name of the strategy (e.g. 'fast', 'SearchHook', 'cognitive-audit').
            repository: Optional DB repository. If absent, attempts to resolve 'UnifiedWorkflowRepository' globally.

        Returns:
            A configured LLMClient instance ready for execution.

        Raises:
            ConfigurationError: If the Strategy does not exist.
        """
        from backend_v2.exceptions import ConfigurationError
        from backend_v2.models.llm import LLMProviderConfig
        from backend_v2.models.v2_core import SystemConfigModelRegistry
        from backend_v2.utils.pydantic_utils import inflate

        if not repository:
            # Fail Fast: Enforce strict dependency injection (Zero-Fallback)
            raise ConfigurationError("Repository dependency must be provided to LLMClient.from_strategy.")

        # 1. Fetch Raw Registry (Opaque ID Standard Supported)
        try:
            raw_registry = await repository.get_model_registry()
        except Exception as e:
            raise ConfigurationError(f"System config 'model_registry' missing or query failed: {e}")

        # 2. Strict Pydantic Inflation (Flattened V2 structure)
        try:
            registry = inflate(raw_registry, SystemConfigModelRegistry)
        except Exception as e:
            msg = f"Failed to parse strict SystemConfigModelRegistry: {e}"
            logger.error(f"[LLMClient] {ErrorCodes.CONFIGURATION_ERROR.name}: {msg}", exc_info=True)
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR}) from e

        if not registry or not registry.models:
            raise ConfigurationError(f"ModelRegistry is severely corrupted or empty: {registry}")

        # 3. Locate Strategy
        target_strategy = registry.models.get(strategy_name)

        # Resolve aliases (e.g. "search" -> "fast" if structured as string)
        visited = {strategy_name}
        while isinstance(target_strategy, str):
            if target_strategy in visited:
                raise ConfigurationError(f"Circular alias '{target_strategy}' in model registry.")
            if target_strategy not in registry.models:
                raise ConfigurationError(f"Alias '{target_strategy}' not found in registry.")
            visited.add(target_strategy)
            target_strategy = registry.models[target_strategy]

        if not target_strategy:
            raise ConfigurationError(f"Strategy '{strategy_name}' not found in registry.")

        target_provider = getattr(target_strategy, "provider", "google")

        # 4. Construct Provider Config
        provider_config = LLMProviderConfig(
            id=f"{target_provider}/{strategy_name}",
            provider=target_provider,
            model_name=target_strategy.model_name,
            api_key=target_strategy.api_key,
            temperature=target_strategy.temperature if target_strategy.temperature is not None else 0.7,
            tpm_limit=target_strategy.tpm_limit if target_strategy.tpm_limit is not None else 100000,
            rpm_limit=target_strategy.rpm_limit if target_strategy.rpm_limit is not None else 10,
            default_max_tokens=target_strategy.max_tokens if target_strategy.max_tokens is not None else 65536,
            supports_grounding=target_strategy.supports_grounding,
            parsing_mode=target_strategy.parsing_mode,
        )

        return cls(config=provider_config)

    async def run_structured_task(
        self,
        messages: list[dict[str, Any]],
        response_model: type[T],
        model: str | None = None,
        **kwargs: Any,
    ) -> tuple[T, dict[str, Any]]:
        """Execute a structured LLM task enforcing a Pydantic schema using LLMProvider.

        Args:
            messages: List of chat messages (system, user, etc.)
            response_model: The Pydantic model class to valid output against.
            model: Optional direct model override. If omitted, uses Strategy-bound config.
            **kwargs: Additional arguments for the completion call.

        Returns:
            A tuple of (Validated Pydantic Model, Token Usage Dictionary).
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
                from backend_v2.exceptions import AppException, ErrorCodes

                raise AppException(
                    message="Model Configuration Missing: No bound Strategy config and no 'model' var passed.",
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
                )
            # Use Strategy Config
            target_model_name = (
                self._config.model_name
                if hasattr(self._config, "model_name")
                else self._config.get("model_name")
            )
            target_provider_type = "litellm"  # Base Default

            # Apply Default Overrides from Strategy
            temp = (
                self._config.temperature
                if hasattr(self._config, "temperature")
                else self._config.get("temperature")
            )
            max_tok = (
                self._config.default_max_tokens
                if hasattr(self._config, "default_max_tokens")
                else self._config.get("default_max_tokens")
            )

            kwargs.setdefault("temperature", temp)
            kwargs.setdefault("max_tokens", max_tok)
            # Future: Tools could be injected here automatically from self._config.allowed_tools
        else:
            # Legacy pass-through
            target_model_name = model
            target_provider_type = "litellm"

        # 3. Create Provider via Factory
        provider = LLMFactory.create_provider(
            provider_type=target_provider_type, model_name=target_model_name, config=self._config  # type: ignore
        )

        try:
            # 3. Generate with Structured Output
            response = await provider.generate(
                prompt=prompt,
                system_instruction=system_instruction,
                response_schema=response_model,
                temperature=kwargs.get("temperature"),
                max_tokens=kwargs.get("max_tokens"),
                mock_identity=kwargs.get("mock_identity")
            )

            # 4. Parse Result
            # response.content is a JSON string (ensured by LiteLLMProvider)
            data = json.loads(response.content)
            validated_model = response_model.model_validate(data)

            # Extract usage securely into a simple dictionary from LLMResponse model
            usage_obj = getattr(response, "token_usage", {})

            usage_dict = {
                "prompt_tokens": usage_obj.get("prompt_tokens", 0),
                "completion_tokens": usage_obj.get("completion_tokens", 0),
                "total_tokens": usage_obj.get("total_tokens", 0),
                "cached_tokens": usage_obj.get("cached_tokens", 0),
                "reasoning_tokens": usage_obj.get("reasoning_tokens", 0),
                "cost_usd": usage_obj.get("cost_usd", 0.0)
            }

            return validated_model, usage_dict

        except Exception as e:
            error_msg = f"Execution Failed for model {model}: {e}"
            logger.error(f"[LLMClient] {ErrorCodes.AGENT_EXECUTION_CRITICAL.name}: {error_msg}", exc_info=True)
            if "response" in locals() and getattr(locals().get("response"), "content", None):
                logger.error(f"[LLMClient] {ErrorCodes.AGENT_EXECUTION_CRITICAL.name}: Raw content causing error: {locals()['response'].content}")
            raise AgentExecutionError(
                detail=f"Structured Task Failed: {e} [{ErrorCodes.AGENT_EXECUTION_CRITICAL.name}]"
            ) from e

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
                from backend_v2.exceptions import AppException, ErrorCodes

                raise AppException(
                    message="Model Configuration Missing: No bound Strategy config and no 'model' var passed.",
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
                )
            # Use Strategy Config
            target_model_name = (
                self._config.model_name
                if hasattr(self._config, "model_name")
                else self._config.get("model_name")
            )
            target_provider_type = "litellm"

            # Apply Default Overrides from Strategy
            temp = (
                self._config.temperature
                if hasattr(self._config, "temperature")
                else self._config.get("temperature")
            )
            max_tok = (
                self._config.default_max_tokens
                if hasattr(self._config, "default_max_tokens")
                else self._config.get("default_max_tokens")
            )

            kwargs.setdefault("temperature", temp)
            kwargs.setdefault("max_tokens", max_tok)
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
        provider = LLMFactory.create_provider(provider_type=target_provider_type, model_name=str(target_model_name))

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
            error_msg = f"Chat Execution Failed: {e}"
            logger.error(f"[LLMClient] {ErrorCodes.AGENT_EXECUTION_CRITICAL.name}: {error_msg}", exc_info=True)
            raise AgentExecutionError(
                detail=f"Chat Task Failed: {e} [{ErrorCodes.AGENT_EXECUTION_CRITICAL.name}]"
            ) from e
