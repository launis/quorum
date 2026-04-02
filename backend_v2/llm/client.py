import json
import logging
from typing import Any, TypeVar

from pydantic import BaseModel

from backend_v2.exceptions import AgentExecutionError, AppException, ErrorCodes
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
            raise ConfigurationError(f"System config 'model_registry' missing or query failed: {e}") from e

        # 2. Strict Pydantic Inflation (Flattened V2 structure)
        try:
            registry = inflate(raw_registry, SystemConfigModelRegistry)
        except Exception as e:
            msg = f"Failed to parse strict SystemConfigModelRegistry: {e}"
            logger.error(
                "Failed to parse strict SystemConfigModelRegistry.",
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "detail": str(e)},
                exc_info=True,
            )
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

        target_provider = getattr(target_strategy, "provider", None)
        if not target_provider:
            raise ConfigurationError(
                f"Strict Mode: Strategy '{strategy_name}' is missing required 'provider' in Model Registry.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
            )

        # 4. Construct Provider Config — Fail-Fast: All values MUST come from Model Registry
        if target_strategy.tpm_limit is None or target_strategy.rpm_limit is None:
            raise ConfigurationError(
                f"Strict Mode: Strategy '{strategy_name}' is missing required 'tpm_limit' "
                "or 'rpm_limit' in Model Registry.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
            )
        if target_strategy.temperature is None:
            raise ConfigurationError(
                f"Strict Mode: Strategy '{strategy_name}' is missing required 'temperature' in Model Registry.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
            )
        if target_strategy.max_tokens is None:
            raise ConfigurationError(
                f"Strict Mode: Strategy '{strategy_name}' is missing required 'max_tokens' in Model Registry.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
            )

        provider_config = LLMProviderConfig(
            id=f"{target_provider}/{strategy_name}",
            provider=target_provider,
            model_name=target_strategy.model_name,
            api_key=target_strategy.api_key,
            temperature=target_strategy.temperature,
            tpm_limit=target_strategy.tpm_limit,
            rpm_limit=target_strategy.rpm_limit,
            default_max_tokens=target_strategy.max_tokens,
            supports_grounding=target_strategy.supports_grounding,
            parsing_mode=target_strategy.parsing_mode,
        )

        return cls(config=provider_config)

    async def run_structured_task(
        self,
        messages: list[dict[str, Any]],
        response_model: type[T],
        model: str | None = None,
        max_retries: int = 1,
        temperature: float | None = None,
        max_tokens: int | None = None,
        mock_identity: str | None = None,
    ) -> tuple[T, dict[str, Any]]:
        """Execute a structured LLM task enforcing a Pydantic schema using LLMProvider.

        Args:
            messages: List of chat messages (system, user, etc.)
            response_model: The Pydantic model class to valid output against.
            model: Optional direct model override. If omitted, uses Strategy-bound config.
            max_retries: Number of self-healing retries on schema errors.
            temperature: Sampling temperature override.
            max_tokens: Max tokens override.
            mock_identity: Identity key for mock provider routing.

        Returns:
            A tuple of (Validated Pydantic Model, Token Usage Dictionary).
        """
        # 1. Evaluate Context Caching Requirements (Epic 5 Context Segregation)
        # We process the raw messages array dynamically before handing it to the provider.
        has_anthropic_ephemeral = False
        if self._config and getattr(self._config, "caching_strategy", None) == "anthropic_ephemeral":
            logger.info("[LLMClient] Enabling Anthropic Ephemeral Context Caching strategy.")
            has_anthropic_ephemeral = True

        final_messages = []
        for msg in messages:
            # Create a shallow copy to prevent mutating the original Orchestrator payload
            final_messages.append(dict(msg))

        if has_anthropic_ephemeral:
            # Anthropic requires "cache_control": {"type": "ephemeral"} on the last static block.
            # In our architecture, the System Head contains all static matrices and instructions.
            for msg in reversed(final_messages):
                if msg.get("role") == "system":
                    # Convert simple string content to Anthropic's block format
                    original_text = msg.get("content", "")
                    # Ensure content is a string before wrapping it
                    if isinstance(original_text, str):
                        msg["content"] = [
                            {"type": "text", "text": original_text, "cache_control": {"type": "ephemeral"}}
                        ]
                    break

        # Fallback strings for Legacy Mock logic where string flattening is required
        system_instruction = None
        prompt = ""
        for m in final_messages:
            if m.get("role") == "system":
                if isinstance(m.get("content"), str):
                    s_cont = str(m.get("content", ""))
                    if not system_instruction:
                        system_instruction = m.get("content")
                    else:
                        system_instruction += "\n" + s_cont
            elif m.get("role") == "user":
                if isinstance(m.get("content"), str):
                    u_cont = str(m.get("content", ""))
                    if not prompt:
                        prompt = u_cont
                    else:
                        prompt += "\n" + u_cont

        # 2. Resolve Configuration (SSOT Priority)
        # If client was bound via Strategy Factory, it has priority unless explicitly overridden.
        if model is None:
            if not self._config:
                raise AppException(
                    message="Model Configuration Missing: No bound Strategy config and no 'model' var passed.",
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
                )
            # Use Strategy Config
            target_model_name = (
                self._config.model_name if hasattr(self._config, "model_name") else self._config.get("model_name")
            )
            target_provider_type = "litellm"  # Base Default

            # Apply Strategy defaults only if caller didn't override
            if temperature is None:
                temperature = (
                    self._config.temperature
                    if hasattr(self._config, "temperature")
                    else self._config.get("temperature")
                )
            if max_tokens is None:
                max_tokens = (
                    self._config.default_max_tokens
                    if hasattr(self._config, "default_max_tokens")
                    else self._config.get("default_max_tokens")
                )
        else:
            # Legacy pass-through
            target_model_name = model
            target_provider_type = "litellm"

        # 3. Create Provider via Factory
        provider = LLMFactory.create_provider(
            provider_type=target_provider_type,
            model_name=str(target_model_name),
            config=self._config,  # type: ignore
        )

        try:
            import pydantic

            current_prompt = prompt
            cumulative_usage: dict[str, float | int] = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "cached_tokens": 0,
                "reasoning_tokens": 0,
                "cost_usd": 0.0,
            }

            for attempt in range(max_retries):
                response = None
                try:
                    # 3. Generate with Structured Output (Caching tags active if final_messages manipulated)
                    response = await provider.generate(
                        prompt=current_prompt,
                        system_instruction=system_instruction,
                        messages=final_messages,
                        response_schema=response_model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        mock_identity=mock_identity,
                    )

                    # Extract usage securely into a simple dictionary from LLMResponse model
                    usage_obj = getattr(response, "token_usage", None)
                    if usage_obj is None:
                        logger.error(
                            "Strict FinOps Mode: LLM Provider failed to return token_usage.",
                            extra={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.name},
                        )
                        raise AgentExecutionError(detail=ErrorCodes.AGENT_EXECUTION_CRITICAL)

                    try:
                        cumulative_usage["prompt_tokens"] += int(usage_obj["prompt_tokens"])
                        cumulative_usage["completion_tokens"] += int(usage_obj["completion_tokens"])
                        cumulative_usage["total_tokens"] += int(usage_obj["total_tokens"])
                    except KeyError as e:
                        logger.error(
                            "Strict FinOps Mode: Missing token metric from provider.",
                            extra={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.name, "detail": str(e)},
                            exc_info=True,
                        )
                        raise AgentExecutionError(
                            detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                            original_error=e,
                        ) from e

                    cumulative_usage["cached_tokens"] += int(usage_obj.get("cached_tokens", 0) or 0)
                    cumulative_usage["reasoning_tokens"] += int(usage_obj.get("reasoning_tokens", 0) or 0)
                    cumulative_usage["cost_usd"] += float(usage_obj.get("cost_usd", 0.0) or 0.0)

                    # 4. Parse Result
                    raw_content = response.content.strip()

                    # Defensively strip Markdown JSON blocks if the LLM hallucinates them
                    if raw_content.startswith("```json"):
                        raw_content = raw_content[7:]
                    if raw_content.startswith("```"):
                        raw_content = raw_content[3:]
                    if raw_content.endswith("```"):
                        raw_content = raw_content[:-3]
                    raw_content = raw_content.strip()

                    data = json.loads(raw_content)
                    validated_model = response_model.model_validate(data)

                    return validated_model, cumulative_usage

                except (json.JSONDecodeError, pydantic.ValidationError) as schema_err:
                    if attempt == max_retries - 1:
                        logger.error(
                            "Self-Healing failed after max attempts.",
                            extra={
                                "error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.name,
                                "model": target_model_name,
                                "detail": str(schema_err),
                            },
                        )
                        raise AgentExecutionError(
                            detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                            original_error=schema_err,
                        ) from schema_err

                    logger.warning(
                        "[LLMClient] Schema Error on attempt %d/%d. Initiating Self-Healing.",
                        attempt + 1,
                        max_retries,
                    )

                    # 5. Epic 12: Semantic Self-Healing (Cognitive vs Structural)
                    error_str = str(schema_err)
                    is_logical_error = "CRITICAL LOGICAL ERROR" in error_str or "Value error" in error_str
                    error_msg = schema_err.json() if isinstance(schema_err, pydantic.ValidationError) else error_str

                    if is_logical_error:
                        logger.warning("[LLMClient] Semantic Logic Error detected. Triggering Socratic Self-Healing.")
                        correction_prompt = (
                            f"\n\n[SYSTEM: STRICT LOGICAL COMPLIANCE REQUIRED]\n"
                            f"Your JSON structure was correct, but your logic failed the architectural validation:\n"
                            f"--- VALIDATION ERROR ---\n{error_msg}\n------------------------\n"
                            f"ACTION: You MUST engage System 2 thinking. Correct your cognitive logic. "
                            f"If you cannot provide empirical evidence, you MUST lower your score "
                            f"to match reality. Do not guess."
                        )
                    else:
                        logger.warning("[LLMClient] Structural Schema Error detected. Triggering Syntax Self-Healing.")
                        correction_prompt = (
                            f"\n\n[SYSTEM: SELF-HEALING CORRECTION - STRUCTURAL]\n"
                            f"Validation errors:\n{error_msg}\n"
                            f"ACTION: Please correct the JSON output to strictly match the requested schema types."
                        )

                    # Append the hallucinated response and the correction instruction to guide the next iteration
                    failed_content = getattr(response, "content", "EMPTY_CONTENT") if response else "EMPTY_CONTENT"
                    current_prompt += f"\n\n{failed_content}{correction_prompt}"

                    # Update messages array for Retry Pipeline
                    final_messages.append({"role": "assistant", "content": failed_content})
                    final_messages.append({"role": "user", "content": correction_prompt})

        except Exception as e:
            if isinstance(e, AgentExecutionError):
                raise
            logger.error(
                "Execution of structured LLM task failed.",
                extra={
                    "error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.name,
                    "model": target_model_name,
                    "detail": str(e),
                },
                exc_info=True,
            )
            err_response = locals().get("response")
            err_content = getattr(err_response, "content", None) if err_response else None
            if err_content:
                logger.error(
                    "Raw content causing structural error.",
                    extra={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.name, "raw_content": str(err_content)},
                )
            raise AgentExecutionError(
                detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                original_error=e,
            ) from e

        raise AgentExecutionError(detail=ErrorCodes.AGENT_EXECUTION_CRITICAL)

    async def run_chat(
        self,
        messages: list[dict[str, Any]],
        model: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str | dict[str, Any]:
        """Execute a free-form chat task returning a string or tool_calls dict.

        Args:
            messages: List of chat messages.
            model: Model identifier. MUST be provided (Zero-Fallback).
            tools: Optional OpenAI-format tool declarations for function calling.
            tool_choice: Optional tool_choice mode ('auto', 'none', 'required').
            temperature: Sampling temperature override.
            max_tokens: Max tokens override.

        Returns:
            str if LLM returns text, or dict with 'tool_calls' key if LLM invokes tools.
        """
        # ZERO-FALLBACK ENFORCEMENT
        # Resolve Configuration (SSOT Priority)
        # If client was bound via Strategy Factory, it has priority unless explicitly overridden.
        if model is None:
            if not self._config:
                raise AppException(
                    message="Model Configuration Missing: No bound Strategy config and no 'model' var passed.",
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
                )
            # Use Strategy Config
            target_model_name = (
                self._config.model_name if hasattr(self._config, "model_name") else self._config.get("model_name")
            )
            target_provider_type = "litellm"

            # Apply Strategy defaults only if caller didn't override
            if temperature is None:
                temperature = (
                    self._config.temperature
                    if hasattr(self._config, "temperature")
                    else self._config.get("temperature")
                )
            if max_tokens is None:
                max_tokens = (
                    self._config.default_max_tokens
                    if hasattr(self._config, "default_max_tokens")
                    else self._config.get("default_max_tokens")
                )
        else:
            # Legacy pass-through
            target_model_name = model
            target_provider_type = "litellm"

        # Parse Prompt — detect if this is a multi-turn tool conversation
        # If messages contain roles other than system/user (e.g. assistant, tool),
        # we MUST pass them as-is to generate(messages=...) for correct tool loop behavior.
        has_tool_messages = any(msg.get("role") in ("assistant", "tool") for msg in messages)

        if has_tool_messages:
            # Multi-turn tool conversation: pass messages directly (no flattening)
            system_instruction = None
            prompt = None
        else:
            # Simple system+user: flatten as before (backward compatible)
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

        # Create Provider — pass self._config for TPM/RPM (Strict Mode compliance)
        provider = LLMFactory.create_provider(
            provider_type=target_provider_type,
            model_name=str(target_model_name),
            config=self._config,  # type: ignore
        )

        # Generate
        try:
            if has_tool_messages:
                # Pass full message array for tool conversations
                response = await provider.generate(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    tools=tools,
                    tool_choice=tool_choice,
                )
            else:
                response = await provider.generate(
                    prompt=prompt,
                    system_instruction=system_instruction,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    tools=tools,
                    tool_choice=tool_choice,
                )

            # If LLM returned tool_calls, return as dict for Tool Loop processing
            if response.tool_calls:
                return {"tool_calls": response.tool_calls, "content": response.content}

            return response.content
        except Exception as e:
            logger.error(
                "Execution of free-form chat task failed.",
                extra={
                    "error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.name,
                    "model": target_model_name,
                    "detail": str(e),
                },
                exc_info=True,
            )
            raise AgentExecutionError(
                detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                original_error=e,
            ) from e
