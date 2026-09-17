from __future__ import annotations

import json
import logging
import uuid
from typing import Any, Self, cast

import pydantic
from pydantic import BaseModel

from backend_v2.exceptions import (
    AgentExecutionError,
    AppException,
    ConfigurationError,
    ErrorCodes,
    LLMSchemaValidationError,
    ResourceNotFoundError,
    ServiceUnavailableError,
)
from backend_v2.llm.adapters.adapter_factory import LLMCacheAdapterFactory
from backend_v2.llm.caching_service import LLMCachingService
from backend_v2.llm.ingress_pipeline import UniversalIngress
from backend_v2.llm.provider import LLMFactory
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.enums import PIPELINE_REGISTRY, CognitiveTier, ExecutionProfile, LLMProvider
from backend_v2.models.llm import LLMMessageDTO, LLMProviderConfig
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.models.v2_core import SystemConfigModelRegistry
from backend_v2.services.orchestrator.prompt_compiler_adapter import PromptCompilerAdapter
from backend_v2.settings import get_settings
from backend_v2.utils.pydantic_utils import inflate

logger = logging.getLogger(__name__)

__all__ = ["LLMClient"]


class LLMClient:
    """LLM Client wrapper adapting LLMFactory for structured outputs.

    Replaces legacy Instructor/OpenAI implementation with unified V2.9 LLMProvider.
    """

    def __init__(self, config: dict[str, Any] | LLMProviderConfig | None = None) -> None:
        self._config: LLMProviderConfig | None
        if config is not None:
            self._config = LLMProviderConfig.model_validate(config)
        else:
            self._config = None
        self.model_config: dict[str, Any] | None = None
        self._initialize()

    def _initialize(self) -> None:
        """Initialize the client."""
        pass

    @property
    def provider_name(self) -> str:
        if self._config is not None:
            return str(self._config.provider)
        return "unknown"

    @property
    def model_name(self) -> str:
        if self._config is not None:
            return str(self._config.model_name)
        return "unknown"

    @property
    def config(self) -> LLMProviderConfig | None:
        return self._config

    def _build_structured_schema(
        self,
        response_model: type[BaseModel],
        final_messages: list[LLMMessageDTO] | list[dict[str, Any]],
        validation_context: dict[str, Any] | None,
    ) -> Any:
        """Build the structured JSON schema for the provider, applying caching and strictness constraints."""
        adapter_schema: Any = {"type": "json_schema"}
        if self._config and self._config.provider:
            try:
                adapter = LLMCacheAdapterFactory.get_adapter(self._config.provider, model_name=self.model_name)
                adapter_schema = adapter.prepare_structured_output(response_model)
            except Exception as e:  # noqa: QGR003 [REASON: Non-fatal fallback to basic JSON mode if custom adapter fails]
                logger.error(
                    "[LLMClient] Could not fetch adapter for structured output. Fallback to basic JSON mode. Error: %s",
                    e,
                )
                adapter_schema = {"type": "json_object"}
        else:
            # Fallback for unconfigured clients
            adapter_schema = {"type": "json_object"}

        return adapter_schema

    @classmethod
    async def from_tier(
        cls,
        tier: CognitiveTier,
        repository: Any = None,
        provider: LLMProvider | None = None,
        execution_profile: ExecutionProfile | None = None,
        pipeline_name: str | None = None,
        registry_id: str | None = None,
    ) -> Self:
        """Factory: Create an LLMClient strictly bound to a database-defined CognitiveTier and Provider.

        Args:
            tier: Canonical CognitiveTier (FAST, BALANCED, DEEP, REASONING).
            repository: Required DB repository instance.
            provider: Optional explicit provider override. If None, uses registry.default_provider.
            execution_profile: Optional intent defining if the cache should be bypassed (e.g. ONE_SHOT).
            pipeline_name: Optional explicit pipeline context to look up configuration for.
            registry_id: Optional specific model registry stack ID. If None, uses default registry.

        Returns:
            A configured client instance ready for execution.

        Raises:
            ConfigurationError (ErrorCodes.CONFIGURATION_ERROR): If the tier or provider is missing or misconfigured.
        """
        if not repository:
            raise ConfigurationError("Repository dependency must be provided to LLMClient.from_tier.")

        # 0. Load Execution Pipelines from static registry
        try:
            if pipeline_name and pipeline_name in PIPELINE_REGISTRY:
                pipeline = PIPELINE_REGISTRY[pipeline_name]
                if execution_profile is None and pipeline.profile:
                    execution_profile = ExecutionProfile(pipeline.profile.value.lower())
        except (KeyError, ValueError, AttributeError) as e:
            logger.warning("[LLMClient] Execution pipelines lookup failed: %s", e)

        # 1. Fetch Raw Registry (Opaque ID Standard Supported)
        try:
            if registry_id:
                raw_registry = await repository.get_model_registry(registry_id)
            else:
                all_registries = await repository.get_all_model_registries()
                if not all_registries:
                    raise ResourceNotFoundError(resource_type="system_config", resource_id="model_registry")
                raw_registry = all_registries[0]
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

        if not registry or not registry.tier_definitions:
            raise ConfigurationError(f"ModelRegistry is severely corrupted or empty: {registry}")

        # 3. Resolve Tier directly from flat tier_definitions in O(1)
        tier_enum = tier if isinstance(tier, CognitiveTier) else CognitiveTier(str(tier).lower())
        if tier_enum not in registry.tier_definitions:
            raise ConfigurationError(
                f"CognitiveTier '{tier}' not found in registry '{registry.name}' (id={registry.id}) tier_definitions.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        target_strategy = registry.tier_definitions[tier_enum]

        # Fail-Fast check on provider override mismatch if explicitly specified
        if provider is not None and provider != target_strategy.provider:
            raise ConfigurationError(
                f"Provider '{provider}' not found in registry tier_definitions for stack '{registry.name}' "
                f"(configured for provider '{target_strategy.provider}').",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        target_provider_type = target_strategy.provider
        target_model_name = target_strategy.model_name
        target_rpm_limit = target_strategy.rpm_limit

        # 4. Construct Provider Config — Fail-Fast: All values MUST come from Model Registry
        if target_strategy.tpm_limit is None or target_rpm_limit is None:
            raise ConfigurationError(
                f"Strict Mode: Tier '{tier}' in Model Registry '{registry.name}' is missing required 'tpm_limit' "
                "or 'rpm_limit' in Model Registry.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )
        if target_strategy.temperature is None:
            raise ConfigurationError(
                f"Strict Mode: Tier '{tier}' in Model Registry '{registry.name}' is missing required 'temperature' in Model Registry.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )
        if target_strategy.max_tokens is None:
            raise ConfigurationError(
                f"Strict Mode: Tier '{tier}' in Model Registry '{registry.name}' is missing required 'max_tokens' in Model Registry.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        # 4.5 Apply Execution Profile (Dynamic overrides)
        final_caching_strategy = target_strategy.caching_strategy
        if execution_profile:
            if execution_profile == ExecutionProfile.ONE_SHOT:
                final_caching_strategy = "none"
                logger.info(
                    "[LLMClient] ExecutionProfile.ONE_SHOT activated: Context Caching explicitly disabled for %s/%s.",
                    target_provider_type,
                    tier,
                )

        provider_config = LLMProviderConfig(
            id=f"prv_{uuid.uuid4().hex}",
            provider=target_provider_type,
            model_name=target_model_name,
            api_key=target_strategy.api_key,
            temperature=target_strategy.temperature,
            top_p=target_strategy.top_p,
            top_k=target_strategy.top_k,
            tpm_limit=target_strategy.tpm_limit,
            rpm_limit=target_rpm_limit,
            default_max_tokens=target_strategy.max_tokens,
            supports_grounding=target_strategy.supports_grounding,
            parsing_mode=target_strategy.parsing_mode,
            caching_strategy=final_caching_strategy,
            additional_params=target_strategy.additional_params,
            frequency_penalty=target_strategy.frequency_penalty,
            presence_penalty=target_strategy.presence_penalty,
        )

        return cls(config=provider_config)

    @classmethod
    async def from_strategy(
        cls,
        strategy_name: str,
        repository: Any = None,
        execution_profile: ExecutionProfile | None = None,
        pipeline_name: str | None = None,
        registry_id: str | None = None,
        provider: LLMProvider | None = None,
    ) -> Self:
        """Compatibility bridge: parses strategy_name as CognitiveTier and delegates to from_tier."""
        try:
            tier = CognitiveTier(strategy_name.lower())
        except ValueError as e:
            raise ConfigurationError(
                f"Unknown strategy or tier '{strategy_name}'. Must be a canonical CognitiveTier.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            ) from e
        return await cls.from_tier(
            tier=tier,
            repository=repository,
            execution_profile=execution_profile,
            pipeline_name=pipeline_name,
            registry_id=registry_id,
            provider=provider,
        )

    async def run_structured_task[T: BaseModel](
        self,
        messages: list[LLMMessageDTO] | list[dict[str, Any]] | CompiledPrompt,
        response_model: type[T],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        mock_identity: str | None = None,
        validation_context: dict[str, Any] | None = None,
    ) -> tuple[T, TokenUsage]:
        """Execute a structured LLM task enforcing a Pydantic schema using LLMProvider.

        Args:
            messages: List of chat messages or compiled prompt.
            response_model: The Pydantic model class to validate output against.
            model: Optional direct model override.
            temperature: Sampling temperature override.
            max_tokens: Max tokens override.
            mock_identity: Identity key for mock provider routing.
            validation_context: Optional context dictionary for strict Pydantic V2 parsing.

        Returns:
            A tuple of the validated model and usage metrics.

        Raises:
            AppException (ErrorCodes.CONFIGURATION_ERROR): If configuration is missing.
            AgentExecutionError (ErrorCodes.AGENT_EXECUTION_CRITICAL): On API or execution failure.
            LLMSchemaValidationError: On schema validation failure.
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
            frequency_penalty = self._config.frequency_penalty
            presence_penalty = self._config.presence_penalty
        else:
            # Legacy pass-through
            target_model_name = model
            target_provider_type = "litellm"
            top_p = None
            top_k = None
            frequency_penalty = None
            presence_penalty = None

        compiled_prompt: CompiledPrompt | None = None
        final_messages: list[LLMMessageDTO] | list[dict[str, Any]]
        if isinstance(messages, CompiledPrompt):
            compiled_prompt = messages
            final_messages = compiled_prompt.to_flat_messages()
        else:
            final_messages = [m if isinstance(m, LLMMessageDTO) else LLMMessageDTO.model_validate(m) for m in messages]

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

        if self._config and self._config.provider:
            try:
                adapter = LLMCacheAdapterFactory.get_adapter(
                    self._config.provider,
                    model_name=str(target_model_name),
                )
                extra_kwargs.update(adapter.prepare_provider_kwargs(str(target_model_name)))
            except Exception as e:
                logger.error("Could not fetch adapter for kwargs injection.", exc_info=True)
                raise ConfigurationError(
                    f"LLM Adapter loading failed for provider {self._config.provider}: {e}",
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                ) from e

        if has_ephemeral_caching and self._config:
            if not compiled_prompt:
                prompt_adapter = PromptCompilerAdapter()
                compiled_prompt = prompt_adapter.compile_prompt(final_messages)

            caching_messages, caching_kwargs = await LLMCachingService.prepare_caching_payload(
                provider_name=self._config.provider,
                compiled_prompt=compiled_prompt,
                model_name=str(target_model_name),
            )
            final_messages = caching_messages
            extra_kwargs.update(caching_kwargs)

            # V3 Cache Fix: Observability telemetry for caching diagnostics
            if "cached_content" in extra_kwargs:
                num_msgs = len(final_messages)
                dynamic_chars = 0
                for m in final_messages:
                    if isinstance(m, LLMMessageDTO):
                        dynamic_chars += len(m.content)
                    elif not isinstance(m, (str, int, float, bool, list)) and m is not None:
                        if "content" in m:
                            dynamic_chars += len(str(m["content"]))

                logger.info(
                    "[LLMClient] Context Cache ACTIVE: %s | Dynamic payload: %d messages, ~%d chars",
                    extra_kwargs["cached_content"],
                    num_msgs,
                    dynamic_chars,
                )

                if num_msgs == 0:
                    error_msg = (
                        "Fail-Fast: Context Caching FATAL ERROR. The dynamic payload is empty (0 messages). "
                        "This usually means PromptCompilerAdapter failed to find an <execution_parameters> or "
                        "similar tag to separate the static cache from the dynamic prompt. "
                        "Vertex AI will reject this with a 400 Bad Request."
                    )
                    logger.error(error_msg)
                    raise AppException(
                        message=error_msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                    )

        # 3. Create Provider via Factory
        provider = LLMFactory.create_provider(
            provider_type=target_provider_type,
            model_name=str(target_model_name),
            config=self._config,
        )

        # STRICT TIMEOUT PROTOCOL: Apply global Enum constraint to structured tasks as well
        strict_timeout = get_settings().llm_default_timeout_seconds

        response = None
        try:
            # Epic 56 Phase 3: Dynamic Schema Stripping
            adapter_schema: Any = response_model
            if isinstance(response_model, type) and issubclass(response_model, BaseModel):
                adapter_schema = self._build_structured_schema(
                    response_model=response_model,
                    final_messages=final_messages,
                    validation_context=validation_context,
                )

            try:
                try:
                    # 3. Generate with Structured Output (Caching tags active if final_messages manipulated)
                    token_usage = None
                    response = await provider.generate(
                        messages=final_messages,
                        response_schema=adapter_schema,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=top_p,
                        top_k=top_k,
                        frequency_penalty=frequency_penalty,
                        presence_penalty=presence_penalty,
                        mock_identity=mock_identity,
                        timeout=strict_timeout,
                        validation_context=validation_context,
                        **extra_kwargs,
                    )
                except Exception as gen_err:
                    err_str = str(gen_err).lower()
                    if "404" in err_str and ("cache" in err_str or "not found" in err_str):
                        logger.warning("Cache Miss Fallback Triggered. Resending full payload natively.", exc_info=True)
                        extra_kwargs.pop("cached_content", None)
                        if "extra_headers" in extra_kwargs:
                            extra_kwargs["extra_headers"].pop("cached_content", None)
                        if "extra_body" in extra_kwargs:
                            extra_kwargs["extra_body"].pop("cachedContent", None)
                            extra_kwargs["extra_body"].pop("cached_content", None)

                        fallback_messages: list[LLMMessageDTO] | list[dict[str, Any]]
                        if compiled_prompt is not None:
                            fallback_messages = compiled_prompt.to_flat_messages()
                        else:
                            fallback_messages = final_messages

                        response = await provider.generate(
                            messages=fallback_messages,
                            response_schema=adapter_schema,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            top_p=top_p,
                            top_k=top_k,
                            frequency_penalty=frequency_penalty,
                            presence_penalty=presence_penalty,
                            mock_identity=mock_identity,
                            timeout=strict_timeout,
                            validation_context=validation_context,
                            **extra_kwargs,
                        )
                    else:
                        raise gen_err

                # Extract usage securely into TokenUsage
                if response is None or response.token_usage is None:
                    logger.error(
                        "Strict FinOps Mode: LLM Provider failed to return token_usage.",
                        extra={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.name},
                    )
                    raise AgentExecutionError(detail=ErrorCodes.AGENT_EXECUTION_CRITICAL.value)
                usage_obj = response.token_usage

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
                        detail=ErrorCodes.AGENT_EXECUTION_CRITICAL.value,
                        original_error=e,
                    ) from e

                # 4. Parse Result
                raw_content = response.content

                finish_reason = ""
                if response is not None and response.provider_metadata is not None:
                    finish_reason = str(response.provider_metadata.finish_reason)

                if finish_reason and str(finish_reason).lower() in ("safety", "content_filtered", "recitation"):
                    raise AgentExecutionError(
                        detail=ErrorCodes.AGENT_EXECUTION_CRITICAL.value,
                        original_error=Exception(
                            f"Safety Filter Triggered - LLM output blocked (finish_reason: {finish_reason})"
                        ),
                    )

                if not raw_content or not str(raw_content).strip():
                    raise LLMSchemaValidationError(
                        validation_error_msg=(
                            "Safety Filter Triggered - LLM output was empty or blocked without explicit reason."
                        ),
                        raw_llm_payload="",
                        is_eof=True,
                        token_usage=token_usage,
                    )

                raw_content = str(raw_content).strip()

                parsed_dict = UniversalIngress.parse_llm_output(raw_content)
                cleaned_dict = UniversalIngress.clean_dict_against_model(parsed_dict, response_model)
                cleaned_json_str = json.dumps(cleaned_dict)
                parsed_json = response_model.model_validate_json(cleaned_json_str, context=validation_context)

                validated_model = cast(T, parsed_json)  # type: ignore[redundant-cast]

                return validated_model, token_usage

            except (json.JSONDecodeError, pydantic.ValidationError, AppException) as schema_err:
                if (
                    isinstance(schema_err, AgentExecutionError)
                    and schema_err.error_code == ErrorCodes.AGENT_EXECUTION_CRITICAL.value
                ):
                    raise schema_err
                if isinstance(schema_err, LLMSchemaValidationError):
                    raise schema_err
                if isinstance(schema_err, (ServiceUnavailableError, ConfigurationError)):
                    raise schema_err
                if isinstance(schema_err, AppException) and (
                    schema_err.status_code in (502, 503, 504)
                    or (
                        schema_err.details and schema_err.details.get("error_code") == ErrorCodes.UPSTREAM_TIMEOUT.value
                    )
                ):
                    raise schema_err

                error_str = str(schema_err)
                if isinstance(schema_err, AppException):
                    error_msg = schema_err.message
                    is_eof = "Missing" in error_msg or "Malformed JSON" in error_msg
                else:
                    is_eof = "EOF while parsing" in error_str
                    error_msg = schema_err.json() if isinstance(schema_err, pydantic.ValidationError) else error_str

                failed_content = "EMPTY_CONTENT"
                if response is not None and response.content is not None:
                    failed_content = response.content

                raise LLMSchemaValidationError(
                    raw_llm_payload=failed_content,
                    validation_error_msg=error_msg,
                    is_eof=is_eof,
                    token_usage=token_usage,
                ) from schema_err

        except Exception as e:
            if isinstance(e, (AgentExecutionError, LLMSchemaValidationError, AppException)):
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
            err_content = None
            if err_response is not None:
                err_content = err_response.content
            if err_content:
                logger.error(
                    "Raw content causing structural error.",
                    extra={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.name, "raw_content": str(err_content)},
                )
            raise AgentExecutionError(
                detail=ErrorCodes.AGENT_EXECUTION_CRITICAL.value,
                original_error=e,
            ) from e

    async def run_chat(
        self,
        messages: list[LLMMessageDTO] | list[dict[str, Any]] | CompiledPrompt,
        model: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str | dict[str, Any]:
        """Execute a free-form chat task returning a string or tool_calls dict.

        Args:
            messages: List of chat messages or compiled prompt.
            model: Model identifier. MUST be provided.
            tools: Optional tool declarations for function calling.
            tool_choice: Optional tool_choice mode.
            temperature: Sampling temperature override.
            max_tokens: Max tokens override.

        Returns:
            A string response or a dictionary containing tool calls.

        Raises:
            AppException (ErrorCodes.CONFIGURATION_ERROR): If configuration is missing.
            AgentExecutionError (ErrorCodes.AGENT_EXECUTION_CRITICAL): On API or execution failure.
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
            frequency_penalty = self._config.frequency_penalty
            presence_penalty = self._config.presence_penalty
        else:
            # Legacy pass-through
            target_model_name = model
            target_provider_type = "litellm"
            top_p = None
            top_k = None
            frequency_penalty = None
            presence_penalty = None

        # STRICT TIMEOUT PROTOCOL: Never overridden by caller, always uses global Enum constraint.
        strict_timeout = get_settings().llm_default_timeout_seconds

        compiled_prompt: CompiledPrompt | None = None
        final_messages: list[LLMMessageDTO] | list[dict[str, Any]]
        if isinstance(messages, CompiledPrompt):
            compiled_prompt = messages
            final_messages = compiled_prompt.to_flat_messages()
        else:
            final_messages = [m if isinstance(m, LLMMessageDTO) else LLMMessageDTO.model_validate(m) for m in messages]

        # 1. Evaluate Context Caching Requirements
        has_ephemeral_caching = False
        caching_strategies = ("prompt_caching", "ephemeral", "anthropic_ephemeral", "gemini_native")
        if self._config and self._config.caching_strategy in caching_strategies:
            has_ephemeral_caching = True

        extra_kwargs: dict[str, Any] = {}
        if has_ephemeral_caching and self._config:
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

        # Force parallel tool calls to dramatically speed up MCP tool execution
        if tools:
            extra_kwargs["parallel_tool_calls"] = True

        try:
            try:
                response = await provider.generate(
                    messages=final_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    top_k=top_k,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty,
                    tools=tools,
                    tool_choice=tool_choice,
                    timeout=strict_timeout,
                    **extra_kwargs,
                )
            except Exception as gen_err:
                err_str = str(gen_err).lower()
                if "404" in err_str and ("cache" in err_str or "not found" in err_str):
                    logger.warning("Cache Miss Fallback Triggered. Resending full payload natively.", exc_info=True)
                    extra_kwargs.pop("cached_content", None)
                    if "extra_headers" in extra_kwargs:
                        extra_kwargs["extra_headers"].pop("cached_content", None)
                    if "extra_body" in extra_kwargs:
                        extra_kwargs["extra_body"].pop("cachedContent", None)
                        extra_kwargs["extra_body"].pop("cached_content", None)

                    fallback_messages: list[LLMMessageDTO] | list[dict[str, Any]]
                    if compiled_prompt is not None:
                        fallback_messages = compiled_prompt.to_flat_messages()
                    else:
                        fallback_messages = final_messages

                    response = await provider.generate(
                        messages=fallback_messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=top_p,
                        top_k=top_k,
                        frequency_penalty=frequency_penalty,
                        presence_penalty=presence_penalty,
                        tools=tools,
                        tool_choice=tool_choice,
                        timeout=strict_timeout,
                        **extra_kwargs,
                    )
                else:
                    raise gen_err

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
