import copy
import json
import logging
import re
import secrets
from typing import Any

import pydantic
from pydantic import BaseModel

from backend_v2.exceptions import (
    AgentExecutionError,
    AppException,
    ConfigurationError,
    ErrorCodes,
    LLMSchemaValidationError,
)
from backend_v2.llm.provider import LLMFactory
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.enums import SystemConcurrency
from backend_v2.models.llm import LLMProviderConfig
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.models.v2_core import SystemConfigModelRegistry
from backend_v2.utils.pydantic_utils import inflate

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM Client wrapper adapting LLMFactory for structured outputs.

    Replaces legacy Instructor/OpenAI implementation with unified V2.9 LLMProvider.

    Attributes:
        model_config: Raw model parameter override dictionary.
    """

    def __init__(self, config: dict[str, Any] | LLMProviderConfig | None = None) -> None:
        """Initialize the LLMClient with an optional config.

        Args:
            config: LLM provider configuration dict or object.
        """
        self._config: LLMProviderConfig | None
        if isinstance(config, dict):
            self._config = LLMProviderConfig.model_validate(config)
        else:
            self._config = config
        self.model_config = None
        self._initialize()

    def _initialize(self) -> None:
        """Initialize the client state and run validation procedures if required."""
        pass

    @classmethod
    async def from_strategy(cls, strategy_name: str, repository: Any = None) -> LLMClient:
        """Factory: Create an LLMClient strictly bound to a database-defined Strategy.

        Args:
            strategy_name: The name of the strategy (e.g. 'fast', 'SearchHook').
            repository: Optional DB repository.

        Returns:
            A configured LLMClient instance ready for execution.

        Raises:
            ConfigurationError: If the Strategy does not exist or model registry is corrupted (ErrorCodes.CONFIGURATION_ERROR).
        """
        if not repository:
            raise ConfigurationError("Repository dependency must be provided to LLMClient.from_strategy.")

        try:
            raw_registry = await repository.get_model_registry()
        except Exception as e:
            raise ConfigurationError(f"System config 'model_registry' missing or query failed: {e}") from e

        try:
            registry = inflate(raw_registry, SystemConfigModelRegistry)
        except Exception as e:
            msg = f"Failed to parse strict SystemConfigModelRegistry: {e}"
            logger.error(
                "Failed to parse strict SystemConfigModelRegistry.",
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "detail": str(e)},
                exc_info=True,
            )
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}) from e

        if not registry or not registry.models:
            raise ConfigurationError(f"ModelRegistry is severely corrupted or empty: {registry}")

        target_strategy = registry.models.get(strategy_name)

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

        provider = target_strategy.provider

        if target_strategy.tpm_limit is None or target_strategy.rpm_limit is None:
            raise ConfigurationError(
                f"Strict Mode: Strategy '{strategy_name}' is missing required 'tpm_limit' "
                "or 'rpm_limit' in Model Registry.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )
        if target_strategy.temperature is None:
            raise ConfigurationError(
                f"Strict Mode: Strategy '{strategy_name}' is missing required 'temperature' in Model Registry.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )
        if target_strategy.max_tokens is None:
            raise ConfigurationError(
                f"Strict Mode: Strategy '{strategy_name}' is missing required 'max_tokens' in Model Registry.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        random_suffix = secrets.token_hex(16)
        model_name = target_strategy.model_name
        api_key = target_strategy.api_key
        temperature = target_strategy.temperature
        top_p = target_strategy.top_p
        top_k = target_strategy.top_k
        tpm_limit = target_strategy.tpm_limit
        rpm_limit = target_strategy.rpm_limit
        default_max_tokens = target_strategy.max_tokens
        supports_grounding = target_strategy.supports_grounding
        parsing_mode = target_strategy.parsing_mode
        caching_strategy = target_strategy.caching_strategy
        additional_params = target_strategy.additional_params

        provider_config = LLMProviderConfig(
            id=f"prv_{random_suffix}",
            provider=provider,
            model_name=model_name,
            api_key=api_key,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            tpm_limit=tpm_limit,
            rpm_limit=rpm_limit,
            default_max_tokens=default_max_tokens,
            supports_grounding=supports_grounding,
            parsing_mode=parsing_mode,
            caching_strategy=caching_strategy,
            additional_params=additional_params,
        )

        return cls(config=provider_config)

    async def run_structured_task[T: BaseModel](
        self,
        messages: list[dict[str, Any]] | CompiledPrompt,
        response_model: type[T],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        mock_identity: str | None = None,
        validation_context: dict[str, Any] | None = None,
    ) -> tuple[T, TokenUsage]:
        """Execute a structured LLM task enforcing a Pydantic schema using LLMProvider.

        Args:
            messages: List of chat messages or CompiledPrompt.
            response_model: The Pydantic model class to validate output against.
            model: Optional direct model override.
            temperature: Sampling temperature override.
            max_tokens: Max tokens override.
            mock_identity: Identity key for mock provider routing.
            validation_context: Optional context dictionary for strict Pydantic V2 parsing.

        Returns:
            A tuple of (Validated Pydantic Model, TokenUsage).

        Raises:
            AppException: If model configuration is missing (ErrorCodes.CONFIGURATION_ERROR).
            AgentExecutionError: If provider generation or metric loading fails (ErrorCodes.AGENT_EXECUTION_CRITICAL).
            LLMSchemaValidationError: If parsing structured output breaches formatting constraints (ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED).
        """
        if model is None:
            if not self._config:
                raise AppException(
                    message="Model Configuration Missing: No bound Strategy config and no 'model' var passed.",
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )
            target_model_name = self._config.model_name
            target_provider_type = "litellm"

            if temperature is None:
                temperature = self._config.temperature
            if max_tokens is None:
                max_tokens = self._config.default_max_tokens
            top_p = self._config.top_p
            top_k = self._config.top_k
        else:
            target_model_name = model
            target_provider_type = "litellm"
            top_p = None
            top_k = None

        compiled_prompt: CompiledPrompt | None = None
        if isinstance(messages, CompiledPrompt):
            compiled_prompt = messages
            final_messages = compiled_prompt.to_flat_messages()
        else:
            final_messages = []
            for msg in messages:
                final_messages.append(copy.deepcopy(msg))

        has_ephemeral_caching = False
        caching_strategies = ("prompt_caching", "ephemeral", "anthropic_ephemeral", "gemini_native")
        if self._config and self._config.caching_strategy in caching_strategies:
            logger.info(
                "[LLMClient] Enabling Universal Ephemeral Context Caching strategy: %s",
                self._config.caching_strategy,
            )
            has_ephemeral_caching = True

        extra_kwargs: dict[str, Any] = {}
        if has_ephemeral_caching and self._config:
            from backend_v2.llm.caching_service import LLMCachingService
            from backend_v2.services.orchestrator.prompt_compiler_adapter import PromptCompilerAdapter

            if not compiled_prompt:
                prompt_adapter = PromptCompilerAdapter()
                compiled_prompt = prompt_adapter.compile_prompt(final_messages)

            final_messages, extra_kwargs = await LLMCachingService.prepare_caching_payload(
                provider_name=self._config.provider,
                compiled_prompt=compiled_prompt,
                model_name=str(target_model_name),
            )

        provider = LLMFactory.create_provider(
            provider_type=target_provider_type,
            model_name=str(target_model_name),
            config=self._config,
        )

        strict_timeout = SystemConcurrency.LLM_DEFAULT_TIMEOUT_SECONDS.value
        response = None
        token_usage = None

        try:
            adapter_schema: type[T] | dict[str, Any] = response_model
            if isinstance(response_model, type) and issubclass(response_model, BaseModel):
                if self._config and getattr(self._config, "parsing_mode", None) == "STRUCTURED_JSON":
                    adapter_schema = {"type": "json_object"}
                    schema_json = json.dumps(response_model.model_json_schema(), indent=2)
                    schema_instruction = (
                        "\n\n[SYSTEM: STRICT JSON STRUCTURE MANDATE]\n"
                        "You MUST output a valid JSON object matching the following JSON Schema. "
                        "All keys listed in the schema properties are absolutely required and case-sensitive. "
                        "Do NOT omit any keys and do NOT add extra keys not listed in the schema.\n"
                        f"Required JSON Schema:\n{schema_json}"
                    )

                    system_msg_found = False
                    for msg in final_messages:
                        if msg.get("role") == "system":
                            content = msg.get("content")
                            if isinstance(content, str):
                                msg["content"] = content + schema_instruction
                                system_msg_found = True
                                break
                            elif isinstance(content, list):
                                for part in content:
                                    if isinstance(part, dict) and part.get("type") == "text":
                                        part["text"] = (part.get("text") or "") + schema_instruction
                                        system_msg_found = True
                                        break
                                if system_msg_found:
                                    break
                    if not system_msg_found:
                        final_messages.insert(0, {"role": "system", "content": schema_instruction.strip()})
                else:
                    json_schema = response_model.model_json_schema()

                    def strip_unsupported_constraints(schema_dict: Any) -> None:
                        if isinstance(schema_dict, dict):
                            schema_dict.pop("maxLength", None)
                            schema_dict.pop("minLength", None)
                            for v in schema_dict.values():
                                strip_unsupported_constraints(v)
                        elif isinstance(schema_dict, list):
                            for item in schema_dict:
                                strip_unsupported_constraints(item)

                    strip_unsupported_constraints(json_schema)
                    schema_name = response_model.__name__
                    adapter_schema = {
                        "type": "json_schema",
                        "json_schema": {
                            "name": schema_name,
                            "schema": json_schema,
                            "strict": True,
                        },
                    }

            try:
                response = await provider.generate(
                    messages=final_messages,
                    response_schema=adapter_schema,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    top_k=top_k,
                    mock_identity=mock_identity,
                    timeout=strict_timeout,
                    validation_context=validation_context,
                    **extra_kwargs,
                )

                usage_obj = response.token_usage if response else None
                if usage_obj is None:
                    logger.error(
                        "Strict FinOps Mode: LLM Provider failed to return token_usage.",
                        extra={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.name},
                    )
                    raise AgentExecutionError(detail=ErrorCodes.AGENT_EXECUTION_CRITICAL)

                try:
                    token_usage = TokenUsage.model_validate(usage_obj)
                except Exception as e:
                    logger.error(
                        "Strict FinOps Mode: Missing or invalid token metric from provider.",
                        extra={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.name, "detail": str(e)},
                        exc_info=True,
                    )
                    raise AgentExecutionError(
                        detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                        original_error=e,
                    ) from e

                raw_content = response.content.strip()
                json_match = re.search(r"```(?:json)?\s*(.*?)\s*```", raw_content, re.DOTALL | re.IGNORECASE)
                if json_match:
                    raw_content = json_match.group(1)

                start_obj, start_arr = raw_content.find("{"), raw_content.find("[")
                valid_starts = [i for i in (start_obj, start_arr) if i != -1]
                start_idx = min(valid_starts) if valid_starts else -1

                if start_idx != -1:
                    end_obj, end_arr = raw_content.rfind("}"), raw_content.rfind("]")
                    end_idx = max(end_obj, end_arr)
                    if end_idx > start_idx:
                        raw_content = raw_content[start_idx : end_idx + 1]

                raw_content = raw_content.strip()
                parsed_json = response_model.model_validate_json(raw_content, context=validation_context)

                return parsed_json, token_usage

            except (json.JSONDecodeError, pydantic.ValidationError) as schema_err:
                error_str = str(schema_err)
                is_eof = "EOF while parsing" in error_str
                error_msg = schema_err.json() if isinstance(schema_err, pydantic.ValidationError) else error_str
                failed_content = response.content if response else "EMPTY_CONTENT"

                raise LLMSchemaValidationError(
                    raw_llm_payload=failed_content,
                    validation_error_msg=error_msg,
                    is_eof=is_eof,
                    token_usage=token_usage,
                ) from schema_err

        except Exception as e:
            if isinstance(e, (AgentExecutionError, LLMSchemaValidationError)):
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
            err_response = response
            err_content = err_response.content if err_response else None
            if err_content:
                logger.error(
                    "Raw content causing structural error.",
                    extra={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.name, "raw_content": str(err_content)},
                )
            raise AgentExecutionError(
                detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                original_error=e,
            ) from e

    async def run_chat(
        self,
        messages: list[dict[str, Any]] | CompiledPrompt,
        model: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str | dict[str, Any]:
        """Execute a free-form chat task returning a string or tool_calls dict.

        Args:
            messages: List of chat messages or CompiledPrompt.
            model: Model identifier.
            tools: Optional OpenAI-format tool declarations for function calling.
            tool_choice: Optional tool_choice mode ('auto', 'none', 'required').
            temperature: Sampling temperature override.
            max_tokens: Max tokens override.

        Returns:
            str if LLM returns text, or dict with 'tool_calls' key if LLM invokes tools.

        Raises:
            AppException: If model configuration is missing (ErrorCodes.CONFIGURATION_ERROR).
            AgentExecutionError: If provider generation fails (ErrorCodes.AGENT_EXECUTION_CRITICAL).
        """
        if model is None:
            if not self._config:
                raise AppException(
                    message="Model Configuration Missing: No bound Strategy config and no 'model' var passed.",
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )
            target_model_name = self._config.model_name
            target_provider_type = "litellm"

            if temperature is None:
                temperature = self._config.temperature
            if max_tokens is None:
                max_tokens = self._config.default_max_tokens
            top_p = self._config.top_p
            top_k = self._config.top_k
        else:
            target_model_name = model
            target_provider_type = "litellm"
            top_p = None
            top_k = None

        strict_timeout = SystemConcurrency.LLM_DEFAULT_TIMEOUT_SECONDS.value

        compiled_prompt: CompiledPrompt | None = None
        if isinstance(messages, CompiledPrompt):
            compiled_prompt = messages
            final_messages = compiled_prompt.to_flat_messages()
        else:
            final_messages = []
            for msg in messages:
                final_messages.append(copy.deepcopy(msg))

        has_ephemeral_caching = False
        caching_strategies = ("prompt_caching", "ephemeral", "anthropic_ephemeral", "gemini_native")
        if self._config and self._config.caching_strategy in caching_strategies:
            has_ephemeral_caching = True

        extra_kwargs: dict[str, Any] = {}
        if has_ephemeral_caching and self._config:
            from backend_v2.llm.caching_service import LLMCachingService
            from backend_v2.services.orchestrator.prompt_compiler_adapter import PromptCompilerAdapter

            if not compiled_prompt:
                prompt_adapter = PromptCompilerAdapter()
                compiled_prompt = prompt_adapter.compile_prompt(final_messages)

            final_messages, extra_kwargs = await LLMCachingService.prepare_caching_payload(
                provider_name=self._config.provider,
                compiled_prompt=compiled_prompt,
                model_name=str(target_model_name),
            )

        provider = LLMFactory.create_provider(
            provider_type=target_provider_type,
            model_name=str(target_model_name),
            config=self._config,
        )

        try:
            response = await provider.generate(
                messages=final_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                top_k=top_k,
                tools=tools,
                tool_choice=tool_choice,
                timeout=strict_timeout,
                **extra_kwargs,
            )

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
