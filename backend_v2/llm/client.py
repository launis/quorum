import copy
import json
import logging
import re
import uuid
from typing import Any, cast

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
    """

    def __init__(self, config: dict[str, Any] | LLMProviderConfig | None = None) -> None:
        self._config: LLMProviderConfig | None
        if isinstance(config, dict):
            self._config = LLMProviderConfig.model_validate(config)
        else:
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
            repository: Optional DB repository (e.g. ISystemRepository or IWorkflowRepository).

        Returns:
            A configured LLMClient instance ready for execution.

        Raises:
            ConfigurationError: If the Strategy does not exist.
        """
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
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}) from e

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

        # DEV MODE DYNAMIC REDIRECT: Redirect expensive gemini-2.5-pro to the "fast" strategy config in dev mode
        from backend_v2.settings import get_settings

        settings = get_settings()
        if settings.environment == "development" and not settings.use_mock_llm:
            if target_strategy.model_name and "gemini-2.5-pro" in target_strategy.model_name:
                fast_strategy = registry.models.get("fast")
                if fast_strategy:
                    logger.warning(
                        "[LLMClient] Dev Mode: Redirecting strategy '%s' (%s) -> "
                        "'fast' strategy (%s) dynamically to save costs.",
                        strategy_name,
                        target_strategy.model_name,
                        fast_strategy.model_name,
                    )
                    target_strategy = fast_strategy

        target_provider = target_strategy.provider

        # 4. Construct Provider Config — Fail-Fast: All values MUST come from Model Registry
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

        provider_config = LLMProviderConfig(
            id=f"prv_{uuid.uuid4().hex}",
            provider=target_provider,
            model_name=target_strategy.model_name,
            api_key=target_strategy.api_key,
            temperature=target_strategy.temperature,
            top_p=target_strategy.top_p,
            top_k=target_strategy.top_k,
            tpm_limit=target_strategy.tpm_limit,
            rpm_limit=target_strategy.rpm_limit,
            default_max_tokens=target_strategy.max_tokens,
            supports_grounding=target_strategy.supports_grounding,
            parsing_mode=target_strategy.parsing_mode,
            caching_strategy=target_strategy.caching_strategy,
            additional_params=target_strategy.additional_params,
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
            messages: List of chat messages (system, user, etc.) or CompiledPrompt.
            response_model: The Pydantic model class to valid output against.
            model: Optional direct model override. If omitted, uses Strategy-bound config.
            temperature: Sampling temperature override.
            max_tokens: Max tokens override.
            mock_identity: Identity key for mock provider routing.
            validation_context: Optional context dictionary for strict Pydantic V2 parsing (e.g. strictness_level).

        Returns:
            A tuple of (Validated Pydantic Model, TokenUsage).
        """
        # ZERO-FALLBACK ENFORCEMENT
        # Resolve Configuration (SSOT Priority)
        # If client was bound via Strategy Factory, it has priority unless explicitly overridden.
        if model is None:
            if not self._config:
                raise AppException(
                    message="Model Configuration Missing: No bound Strategy config and no 'model' var passed.",
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )
            # Use Strategy Config
            target_model_name = self._config.model_name
            target_provider_type = "litellm"  # Base Default

            # Apply Strategy defaults only if caller didn't override
            if temperature is None:
                temperature = self._config.temperature
            if max_tokens is None:
                max_tokens = self._config.default_max_tokens
            top_p = self._config.top_p
            top_k = self._config.top_k
        else:
            # Legacy pass-through
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
                # Create a deep copy to prevent mutating the original Orchestrator payload
                final_messages.append(copy.deepcopy(msg))

        # 1. Evaluate Context Caching Requirements (Epic 5 Context Segregation)
        # We process the raw messages array dynamically before handing it to the provider.
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

            # V3 Cache Fix: Observability telemetry for caching diagnostics
            if "cached_content" in extra_kwargs:
                logger.info(
                    "[LLMClient] Context Cache ACTIVE: %s | Dynamic payload: %d messages, ~%d chars",
                    extra_kwargs["cached_content"],
                    len(final_messages),
                    sum(len(str(m.get("content", ""))) for m in final_messages),
                )

        # 3. Create Provider via Factory
        provider = LLMFactory.create_provider(
            provider_type=target_provider_type,
            model_name=str(target_model_name),
            config=self._config,
        )

        # STRICT TIMEOUT PROTOCOL: Apply global Enum constraint to structured tasks as well
        strict_timeout = SystemConcurrency.LLM_DEFAULT_TIMEOUT_SECONDS.value

        response = None
        try:
            # Epic 56 Phase 3: Dynamic Schema Stripping
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

                    user_msg_found = False
                    for msg in reversed(final_messages):
                        if msg.get("role") == "user":
                            content = msg.get("content")
                            if isinstance(content, str):
                                msg["content"] = content + schema_instruction
                                user_msg_found = True
                                break
                            elif isinstance(content, list):
                                for part in content:
                                    if isinstance(part, dict) and part.get("type") == "text":
                                        part["text"] = (part.get("text") or "") + schema_instruction
                                        user_msg_found = True
                                        break
                                if user_msg_found:
                                    break
                    if not user_msg_found:
                        final_messages.append({"role": "user", "content": schema_instruction.strip()})
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
                # 3. Generate with Structured Output (Caching tags active if final_messages manipulated)
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

                # Extract usage securely into TokenUsage
                usage_obj = response.token_usage if response else None
                if usage_obj is None:
                    logger.error(
                        "Strict FinOps Mode: LLM Provider failed to return token_usage.",
                        extra={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.name},
                    )
                    raise AgentExecutionError(detail=ErrorCodes.AGENT_EXECUTION_CRITICAL)

                token_usage = None
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

                # 4. Parse Result
                raw_content = response.content.strip()

                # Defensively extract JSON if the LLM hallucinates markdown blocks or conversational text
                json_match = re.search(r"```(?:json)?\s*(.*?)\s*```", raw_content, re.DOTALL | re.IGNORECASE)
                if json_match:
                    raw_content = json_match.group(1)

                # Strip conversational prefix/suffix by finding the outermost JSON structure
                start_obj, start_arr = raw_content.find("{"), raw_content.find("[")
                valid_starts = [i for i in (start_obj, start_arr) if i != -1]
                start_idx = min(valid_starts) if valid_starts else -1

                if start_idx != -1:
                    end_obj, end_arr = raw_content.rfind("}"), raw_content.rfind("]")
                    end_idx = max(end_obj, end_arr)
                    if end_idx > start_idx:
                        raw_content = raw_content[start_idx : end_idx + 1]

                raw_content = raw_content.strip()

                # Epic 56 Phase 3: Defensive wrap for single-key array hallucinations
                if raw_content.startswith("[") and raw_content.endswith("]"):
                    if isinstance(response_model, type) and issubclass(response_model, BaseModel):
                        fields = response_model.model_fields
                        if len(fields) == 1:
                            root_key = list(fields.keys())[0]
                            logger.warning(
                                "[LLMClient] LLM returned a raw array. Auto-wrapping into single root key '%s'.",
                                root_key,
                            )
                            raw_content = f'{{"{root_key}": {raw_content}}}'

                parsed_json = response_model.model_validate_json(raw_content, context=validation_context)
                validated_model = cast(T, parsed_json)  # type: ignore[redundant-cast]

                return validated_model, token_usage

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
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )
            # Use Strategy Config
            target_model_name = self._config.model_name
            target_provider_type = "litellm"

            # Apply Strategy defaults only if caller didn't override
            if temperature is None:
                temperature = self._config.temperature
            if max_tokens is None:
                max_tokens = self._config.default_max_tokens
            top_p = self._config.top_p
            top_k = self._config.top_k
        else:
            # Legacy pass-through
            target_model_name = model
            target_provider_type = "litellm"
            top_p = None
            top_k = None

        # STRICT TIMEOUT PROTOCOL: Never overridden by caller, always uses global Enum constraint.
        strict_timeout = SystemConcurrency.LLM_DEFAULT_TIMEOUT_SECONDS.value

        compiled_prompt: CompiledPrompt | None = None
        if isinstance(messages, CompiledPrompt):
            compiled_prompt = messages
            final_messages = compiled_prompt.to_flat_messages()
        else:
            final_messages = []
            for msg in messages:
                final_messages.append(copy.deepcopy(msg))

        # 1. Evaluate Context Caching Requirements
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

        # Create Provider — pass self._config for TPM/RPM (Strict Mode compliance)
        provider = LLMFactory.create_provider(
            provider_type=target_provider_type,
            model_name=str(target_model_name),
            config=self._config,
        )

        # Generate
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
