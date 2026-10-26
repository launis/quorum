"""LLM Provider implementations (LiteLLM, Mock, Unconfigured)."""

import asyncio
import json
import logging
import os
import time
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import opentelemetry.trace as otel_trace
from pydantic import BaseModel
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential_jitter,
)

# Phase 1, Step 2: Enable Two-Phase Package Strangler submodule resolution while provider.py acts as proxy
__path__: list[str] = [str(Path(__file__).resolve().with_suffix(""))]

from backend_v2.exceptions import (
    AgentExecutionError,
    AppException,
    ConfigurationError,
    ErrorCodes,
    SecurityViolationError,
    ServiceUnavailableError,
)
from backend_v2.llm.adapters.base_adapter import apply_provider_pacing
from backend_v2.llm.caching_service import LLMCachingService
from backend_v2.llm.mock import MockLLMService
from backend_v2.llm.provider.env_and_schema_utils import (
    _INTERNAL_NON_API_KEYS as _INTERNAL_NON_API_KEYS,
)
from backend_v2.llm.provider.env_and_schema_utils import (
    _normalize_mcp_tool_schema_for_llm as _normalize_mcp_tool_schema_for_llm,
)
from backend_v2.llm.provider.env_and_schema_utils import (
    _safe_static_getattr as _safe_static_getattr,
)
from backend_v2.llm.provider.env_and_schema_utils import (
    _safe_static_hasattr as _safe_static_hasattr,
)
from backend_v2.llm.provider.env_and_schema_utils import (
    _sync_diagnostic_dump as _sync_diagnostic_dump,
)
from backend_v2.llm.provider.env_and_schema_utils import (
    resolve_env_variables as resolve_env_variables,
)
from backend_v2.llm.provider.transient_retry_policy import (
    _RETRY_AFTER_REGEX as _RETRY_AFTER_REGEX,
)
from backend_v2.llm.provider.transient_retry_policy import (
    _AdaptiveWaitWithRetryAfter as _AdaptiveWaitWithRetryAfter,
)
from backend_v2.llm.provider.transient_retry_policy import (
    _extract_retry_after_seconds as _extract_retry_after_seconds,
)
from backend_v2.llm.provider.transient_retry_policy import (
    _format_attempt_error as _format_attempt_error,
)
from backend_v2.llm.provider.transient_retry_policy import (
    _is_transient_llm_error as _is_transient_llm_error,
)
from backend_v2.models.domain.mcp import OpenAIFunctionCallDTO, OpenAIToolCallDTO
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.enums import LLMProviderName
from backend_v2.models.llm import LLMMessageDTO, LLMProviderConfig, LLMResponse, ProviderMetadataDTO
from backend_v2.services.usage_service import UsageService
from backend_v2.settings import get_settings

__all__ = [
    "LLMFactory",
    "LLMProvider",
    "LiteLLMProvider",
    "LogfireShieldedClient",
    "MockProvider",
    "_AdaptiveWaitWithRetryAfter",
    "_INTERNAL_NON_API_KEYS",
    "_RETRY_AFTER_REGEX",
    "_extract_retry_after_seconds",
    "_format_attempt_error",
    "_is_transient_llm_error",
    "_normalize_mcp_tool_schema_for_llm",
    "_safe_static_getattr",
    "_safe_static_hasattr",
    "_sync_diagnostic_dump",
    "resolve_env_variables",
]

# Configure logging
logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers.

    Defines the contract for text generation and structured data extraction.
    """

    @abstractmethod
    async def generate(
        self,
        prompt: str | None = None,
        system_instruction: str | None = None,
        messages: list[LLMMessageDTO] | list[dict[str, Any]] | None = None,
        response_schema: type[BaseModel] | dict[str, Any] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        frequency_penalty: float | None = None,
        presence_penalty: float | None = None,
        pass_reasoning_token: str | None = None,
        validation_context: dict[str, Any] | None = None,
        mock_identity: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generates content from the LLM.

        Args:
            prompt: The user prompt.
            system_instruction: System prompt/context.
            messages: Fallback context or chat history.
            response_schema: Pydantic model or JSON Schema.
            temperature: Sampling temperature.
            max_tokens: Max tokens to generate.
            top_p: Nucleus sampling mass.
            top_k: Top-K sampling count.
            frequency_penalty: Penalizes tokens based on their frequency.
            presence_penalty: Penalizes tokens based on their presence.
            pass_reasoning_token: Encrypted state blob from previous turn.
            validation_context: Optional context for validation.
            mock_identity: Optional internal mock identity for unit test routing.
            **kwargs: Additional provider-specific arguments.

        Returns:
            LLMResponse: The generated response object.

        Raises:
            AgentExecutionError: On context bounds exceeded.
            AppException: On internal generation errors.
            ConfigurationError: On malformed config.
            SecurityViolationError: On blocked content.
            ServiceUnavailableError: On provider network failure.
        """
        pass


class LogfireShieldedClient:
    """Proxy class to hide httpx.AsyncClient from Logfire's deep serialization hook.

    Prevents 'RuntimeError: dictionary changed size during iteration' when Logfire
    iterates over kwargs containing a shared mutating httpx client.
    """

    __slots__ = ("_client",)

    def __init__(self, client: Any):
        """Initializes proxy."""
        self._client = client

    def __getattr__(self, name: str) -> Any:
        """Forwards attributes to actual client."""
        return object.__getattribute__(self._client, name)

    async def __aenter__(self) -> Any:
        """Forwards context manager enter to actual client."""
        if "__aenter__" in dir(self._client):
            return await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> Any:
        """Forwards context manager exit to actual client."""
        if "__aexit__" in dir(self._client):
            return await self._client.__aexit__(exc_type, exc_val, exc_tb)

    def __repr__(self) -> str:
        """Returns safe representation string for Logfire."""
        return "<LogfireShieldedClient protecting httpx.AsyncClient>"


class LiteLLMProvider(LLMProvider):
    """Unified LLM Provider using LiteLLM to support multiple models (Gemini, OpenAI, etc.).

    Provides a consistent interface.
    """

    # Class-level cache to prevent litellm callbacks memory leak during bulk executions
    _router_cache: dict[str, Any] = {}
    _semaphores: dict[str, asyncio.Semaphore] = {}
    _httpx_clients: dict[str, Any] = {}

    def __init__(
        self,
        model_name: str,
        api_key: str | None = None,
        settings: Any = None,
        usage_service: UsageService | None = None,
        organization_id: str | None = None,
        limits: dict[str, int] | None = None,
        supports_grounding: bool = False,
        config: LLMProviderConfig | None = None,
    ):
        """Initializes the LiteLLM provider.

        Args:
            model_name: The model identifier.
            api_key: API Key.
            settings: System settings object.
            usage_service: Service for cost tracking.
            organization_id: Context organization ID.
            limits: Override TPM/RPM limits (e.g. from Organization).
            supports_grounding: Whether this model strategy requires Vertex Grounding.
            config: Strict configuration object.

        Raises:
            ConfigurationError: If strict tpm/rpm limits are not provided.
        """
        self.model_name = model_name
        self.api_key = api_key
        self.settings = settings
        self.usage_service = usage_service
        if organization_id:
            self.organization_id = organization_id
        else:
            self.organization_id = "UNKNOWN_ORG"
        self.supports_grounding = supports_grounding
        self._config = config

        import litellm
        from litellm.router import Router

        # litellm general config
        litellm.drop_params = True
        litellm.num_retries = 0  # CRITICAL: Disable internal retries so Tenacity is in control

        # --- Configure Router for Rate Limiting ---
        # We construct a single-item model list for this provider instance
        # to leverage Router's TPM/RPM enforcement logic.

        # 1. Determine Limits
        # STRICT CONFIGURATION (Jan 2026): No hardcoded defaults.
        # Limits must be provided via specific configuration (Organization/User/System).

        if not limits:
            msg = (
                "Strict Mode: LLM Rate Limits (TPM/RPM) must be explicitly passed "
                "to Provider. No hardcoded defaults allowed."
            )
            logger.error("[LiteLLMProvider] %s", msg)
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})

        tpm = None
        if "tpm" in limits:
            tpm = limits["tpm"]
        rpm = None
        if "rpm" in limits:
            rpm = limits["rpm"]

        if tpm is None or rpm is None:
            msg = "Strict Mode: Both TPM and RPM must be defined in limits config."
            logger.error("[LiteLLMProvider] %s", msg)
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})

        # Use Class Cache for Router to avoid MAX_CALLBACKS leak
        cache_key = f"{model_name}_{tpm}_{rpm}"
        self.cache_key = cache_key

        if cache_key in self.__class__._router_cache:
            self.router = self.__class__._router_cache[cache_key]
        else:
            # 2. Build deployment config
            litellm_params: dict[str, Any] = {
                "model": model_name,
                "tpm": tpm,
                "rpm": rpm,
            }
            if self.api_key is not None:
                litellm_params["api_key"] = self.api_key

            model_config = {
                "model_name": model_name,
                "litellm_params": litellm_params,
                "model_info": {
                    "id": model_name,
                },
            }

            settings = get_settings()

            # CRITICAL: Disable internal Router retries (num_retries=0) to allow Fail-Fast Tenacity handling.
            # Use native in-memory caching to avoid unmanaged background Redis socket timeouts.
            self.router = Router(
                model_list=[model_config],
                set_verbose=False,
                num_retries=0,
                timeout=float(settings.llm_default_timeout),
                routing_strategy="simple-shuffle",
                allowed_fails=0,
                cooldown_time=0,
            )

            # Save to class cache
            self.__class__._router_cache[cache_key] = self.router

        # Initialize and store Semaphore dynamically to throttle HTTP-level requests
        if cache_key not in self.__class__._semaphores:
            if rpm <= get_settings().semaphore_low_rpm_threshold:
                concurrency_limit = get_settings().semaphore_low_rpm_limit
            else:
                concurrency_limit = min(
                    get_settings().semaphore_max_concurrency,
                    max(1, rpm // get_settings().semaphore_rpm_divisor),
                )

            logger.info(
                "[LiteLLMProvider] Initializing HTTP concurrency semaphore for cache_key '%s' with limit %d",
                cache_key,
                concurrency_limit,
            )
            self.__class__._semaphores[cache_key] = asyncio.Semaphore(concurrency_limit)

    async def generate(
        self,
        prompt: str | None = None,
        system_instruction: str | None = None,
        messages: list[LLMMessageDTO] | list[dict[str, Any]] | None = None,
        response_schema: type[BaseModel] | dict[str, Any] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        frequency_penalty: float | None = None,
        presence_penalty: float | None = None,
        pass_reasoning_token: str | None = None,
        validation_context: dict[str, Any] | None = None,
        mock_identity: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generates content using LiteLLM.

        Args:
            prompt: The user prompt.
            system_instruction: System prompt/context.
            messages: Fallback context or chat history.
            response_schema: Pydantic model or JSON Schema.
            temperature: Sampling temperature.
            max_tokens: Max tokens to generate.
            top_p: Nucleus sampling mass.
            top_k: Top-K sampling count.
            frequency_penalty: Penalizes tokens based on their frequency.
            presence_penalty: Penalizes tokens based on their presence.
            pass_reasoning_token: Encrypted state blob from previous turn.
            validation_context: Optional context for validation.
            mock_identity: Optional internal mock identity for unit test routing.
            **kwargs: Additional provider-specific arguments.

        Returns:
            Unified LLMResponse with content and reasoning state.

        Raises:
            AgentExecutionError: On context bounds exceeded.
            AppException: On internal generation errors.
            ConfigurationError: On malformed config.
            SecurityViolationError: On blocked content.
            ServiceUnavailableError: On provider network failure.
        """
        import litellm

        final_messages: list[LLMMessageDTO | dict[str, Any]] = []
        if messages:
            if "cached_content" in kwargs:
                final_messages.extend(
                    [
                        m
                        for m in messages
                        if (
                            m.role != "system"
                            if isinstance(m, LLMMessageDTO)
                            else (m["role"] != "system" if type(m) is dict and "role" in m else True)
                        )
                    ]
                )
            else:
                final_messages.extend(messages)
        else:
            if system_instruction and "cached_content" not in kwargs:
                final_messages.append({"role": "system", "content": system_instruction})
            if prompt:
                final_messages.append({"role": "user", "content": prompt})

        # Tier 4 Fix: Sanitize messages to prevent provider-specific API crashes
        adapter = None
        if self._config:
            from backend_v2.llm.adapters.adapter_factory import LLMCacheAdapterFactory

            try:
                adapter = LLMCacheAdapterFactory.get_adapter(self._config.provider, model_name=self.model_name)
                final_messages = adapter.sanitize_messages(final_messages)
            except AppException as e:
                logger.debug("[LiteLLMProvider] No adapter found (provider: %s): %s", self._config.provider, e)

        # STRICT CONFIGURATION (Jan 2026): Reject defaults.
        if temperature is None:
            msg = (
                "Strict Mode: 'temperature' must be explicitly provided "
                "from configuration (Database/Registry). No default allowed."
            )
            logger.error("[LiteLLMProvider] %s", msg)
            raise ConfigurationError(msg)

        if max_tokens is None:
            msg = (
                "Strict Mode: 'max_tokens' must be explicitly provided "
                "from configuration (Database/Registry). No default allowed."
            )
            logger.error("[LiteLLMProvider] %s", msg)
            raise ConfigurationError(msg)

        # Context Continuity (Stateless Reasoning Blob)
        if pass_reasoning_token:
            # Abstraction: We pass it as a developer hint for now.
            # Real implementation would use provider-specific params in `litellm.acompletion`
            final_messages.append(
                {
                    "role": "system",
                    "content": f"[SYSTEM: RESUME_THOUGHT_PROCESS] PREVIOUS_STATE_BLOB: {pass_reasoning_token}",
                }
            )

        response_format = None
        if response_schema:
            try:
                schema_name = "dict"
                if isinstance(response_schema, type):
                    schema_name = response_schema.__name__
                elif type(response_schema) is dict and "json_schema" in response_schema:
                    js = response_schema["json_schema"]
                    if type(js) is dict and "name" in js and js["name"]:
                        schema_name = str(js["name"])

                logger.info("[LiteLLM] Enabling Structured Output for schema: %s", schema_name)
                response_format = response_schema
            except Exception as schema_err:
                logger.error("[LiteLLM] Could not resolve schema name: %s", schema_err)
                raise ConfigurationError(
                    message=f"Schema resolution failed: {schema_err}",
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                ) from schema_err

        # Location resolution has been moved to adapter.prepare_kwargs

        try:
            # --- LOGGING ---
            def _truncate_for_debug(text: str, label: str) -> None:
                if not text:
                    logger.info("[LiteLLM] [%s]: <empty>", label)
                    return

                logger.info(
                    "[LiteLLM] [%s]: Length=%d chars | Content=[REDACTED_FOR_SECURITY]",
                    label,
                    len(text),
                )

            if system_instruction:
                _truncate_for_debug(system_instruction, "SYSTEM INSTRUCTION")
            if prompt:
                _truncate_for_debug(prompt, "USER PROMPT")
            elif messages:
                _truncate_for_debug(str(messages)[:100] + "...(truncated)", "MESSAGES ARRAY")

            logger.info("[LiteLLM] Calling %s...", self.model_name)

            serialized_messages = [
                m.model_dump(mode="json", exclude_none=True) if isinstance(m, BaseModel) else m for m in final_messages
            ]

            # Prepare arguments
            call_kwargs: dict[str, Any] = {
                "model": self.model_name,
                "messages": serialized_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
                "top_k": top_k,
                "frequency_penalty": frequency_penalty,
                "presence_penalty": presence_penalty,
                "response_format": response_format,
                "drop_params": True,
                # STRICT NETWORK TIMEOUT: Fail fast instead of hanging forever.
                "timeout": kwargs["timeout"] if "timeout" in kwargs else self.settings.llm_default_timeout,
            }
            if self.api_key is not None:
                call_kwargs["api_key"] = self.api_key

            # Inject dynamic extra params (top_p, top_k, etc.) provided via kwargs
            # Filter out internal keys if necessary, but litellm.drop_params=True handles most.
            call_kwargs.update(kwargs)
            if "tools" in call_kwargs and call_kwargs["tools"]:
                call_kwargs["tools"] = [
                    _normalize_mcp_tool_schema_for_llm(
                        t.model_dump(mode="json", by_alias=True, exclude_none=True) if isinstance(t, BaseModel) else t
                    )
                    for t in call_kwargs["tools"]
                ]
            for key in _INTERNAL_NON_API_KEYS:
                if key in call_kwargs:
                    del call_kwargs[key]

            # Delegate provider-specific kwargs adjustments (e.g., Vertex caching, location)
            if adapter:
                call_kwargs = adapter.prepare_kwargs(call_kwargs, self._config, self.settings)

            if self._config and self._config.additional_params:
                resolved_additional = resolve_env_variables(
                    self._config.additional_params.model_dump(exclude_none=True)
                )
                call_kwargs.update(resolved_additional)

            # --- DIAGNOSTIC DUMP ---
            dump_file = os.getenv("DUMP_PROMPTS_FILE")
            if dump_file:
                try:
                    payload = json.dumps(serialized_messages, indent=2, ensure_ascii=False)
                    await asyncio.to_thread(_sync_diagnostic_dump, dump_file, f"[LiteLLM] {self.model_name}", payload)
                except Exception as e:
                    logger.error("Failed to schedule diagnostic dump: %s", e)
                    raise ConfigurationError(
                        message=f"Diagnostic dump dispatch failed: {e}",
                        details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                    ) from e

            # --- CALL LiteLLM (Unstructured or Structured Native) ---
            # Remove keys that shouldn't be passed directly
            call_kwargs["model"] = self.model_name
            for key in _INTERNAL_NON_API_KEYS:
                if key in call_kwargs:
                    del call_kwargs[key]

            # Tier 4 Fix: HTTPX Configuration for Server Disconnected Issues
            _timeout_val = float(self.settings.llm_default_timeout)
            if "timeout" in call_kwargs and call_kwargs["timeout"] is not None:
                _timeout_val = float(call_kwargs["timeout"])
            provider_suffix = "default"
            if self._config:
                provider_suffix = self._config.provider
            _client_key = f"httpx_{_timeout_val}_{provider_suffix}"

            # Use dynamic client in tests to prevent cross-loop event loop hangs
            if "PYTEST_CURRENT_TEST" in os.environ:
                # Do not inject explicit custom client during tests to prevent pytest-asyncio event loop hangs
                # litellm will fall back to its internal client which closes safely per test.
                pass
            else:
                if _client_key not in self.__class__._httpx_clients:
                    custom_client = None
                    if adapter:
                        custom_client = adapter.build_http_client(_timeout_val)
                    if custom_client:
                        logger.info(
                            "[LiteLLMProvider] Using provider-specific persistent HTTPX client for timeout %s s",
                            _timeout_val,
                        )
                        self.__class__._httpx_clients[_client_key] = custom_client
                    else:
                        # Fallback to LiteLLM default client behavior
                        self.__class__._httpx_clients[_client_key] = None

                resolved_client = self.__class__._httpx_clients[_client_key]
                if resolved_client:
                    call_kwargs["client"] = LogfireShieldedClient(resolved_client)

            max_rate_limit_retries = get_settings().llm_max_transient_retries
            response = None

            # Phase 3, Step 4: Enforce Adaptive Exponential Backoff with Upstream Retry-After
            base_wait = wait_exponential_jitter(
                initial=get_settings().llm_retry_jitter_initial_seconds,
                max=get_settings().llm_retry_max_seconds,
                exp_base=get_settings().llm_retry_jitter_exp_base,
                jitter=1,
            )
            adaptive_wait = _AdaptiveWaitWithRetryAfter(
                base_wait=base_wait,
                max_seconds=float(get_settings().llm_retry_max_seconds),
            )

            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(max_rate_limit_retries + 1),
                wait=adaptive_wait,
                retry=retry_if_exception(_is_transient_llm_error),
                reraise=True,
                before_sleep=lambda rs: logger.warning(
                    "[LiteLLMProvider] Transient Error or Quota Exhausted (Attempt %s/%s). "
                    "Initiating dynamic exponential backoff... | Error: %s",
                    rs.attempt_number,
                    max_rate_limit_retries,
                    _format_attempt_error(rs),
                ),
            ):
                with attempt:
                    _timeout = call_kwargs["timeout"]

                    # Grab the stored dynamic Semaphore to throttle HTTP-level requests under low RPM
                    semaphore = self.__class__._semaphores[self.cache_key]

                    async with semaphore:
                        start_time = time.perf_counter()

                        async def _execute_paced_completion() -> Any:
                            # Phase 8: Apply Provider-Scoped Pacing Lock to prevent 429 exhaustion
                            provider_key = (
                                self._config.provider
                                if self._config
                                else (self.model_name.split("/")[0] if "/" in self.model_name else self.model_name)
                            )
                            target_resource = self._config.model_name if self._config else self.model_name
                            config_rpm_limit = None
                            if self._config:
                                config_rpm_limit = self._config.rpm_limit
                            await apply_provider_pacing(
                                provider_name=provider_key,
                                strategy_id=target_resource,
                                rpm_limit=config_rpm_limit,
                            )
                            return await self.router.acompletion(**call_kwargs)

                        response = await asyncio.wait_for(_execute_paced_completion(), timeout=float(_timeout))

            if response is None:
                raise ServiceUnavailableError("Failed to get a response from the model provider.")

            actual_model = response.model if "model" in dir(response) else self.model_name
            clean_req = (
                self.model_name.removeprefix("openai/").removeprefix("vertex_ai/").removeprefix("gemini/").lower()
            )
            clean_act = (
                str(actual_model).removeprefix("openai/").removeprefix("vertex_ai/").removeprefix("gemini/").lower()
            )
            is_same_family = clean_req in clean_act or clean_act in clean_req
            if isinstance(actual_model, str) and actual_model and not is_same_family:
                logger.info(
                    "[LiteLLMProvider] LLM Fallback utilized: Primary model '%s' failed, "
                    "successfully routed to fallback model '%s'.",
                    self.model_name,
                    actual_model,
                )

            latency_ms = int((time.perf_counter() - start_time) * 1000)

            # Extract basic content
            choice = response.choices[0]
            message = choice.message
            raw_content = ""
            if message.content:
                raw_content = message.content

            # Vertex AI / LiteLLM Structured Output Bug Fix:
            # If the response was forced into a tool call instead of content (common with Vertex Caching/Gemini),
            # extract the raw JSON string from the first tool call's arguments.
            if not raw_content and "tool_calls" in dir(message) and message.tool_calls:
                tc = message.tool_calls[0]
                if "function" in dir(tc) and "arguments" in dir(tc.function):
                    raw_content = ""
                    if tc.function.arguments:
                        raw_content = tc.function.arguments
                elif (
                    type(tc) is dict
                    and "function" in tc
                    and type(tc["function"]) is dict
                    and "arguments" in tc["function"]
                ):
                    raw_content = ""
                    if tc["function"]["arguments"]:
                        raw_content = tc["function"]["arguments"]

            finish_reason = None
            if "finish_reason" in dir(choice):
                finish_reason = choice.finish_reason

            # --- EMERGENCY DIAGNOSTIC DUMP (TIER 4) ---
            if not raw_content:
                dump_str = response.model_dump_json() if "model_dump_json" in dir(response) else str(response)
                logger.critical("[DIAGNOSTIC] LLM Output was completely empty! Raw response object dump: %s", dump_str)

            # Extract Reasoning Token (Gemini 3 / GPT-5.1)
            reasoning_token = None

            # Check standard LiteLLM extra fields
            psf = _safe_static_getattr(message, "provider_specific_fields")
            if psf and isinstance(psf, dict):
                if "thought_signature" in psf:
                    reasoning_token = psf["thought_signature"]
                elif "reasoning_blob" in psf:
                    reasoning_token = psf["reasoning_blob"]
                else:
                    reasoning_token = None

            # Fallback: Check top level attributes
            me = _safe_static_getattr(response, "model_extra")
            if not reasoning_token and isinstance(me, dict):
                if "thought_signature" in me:
                    reasoning_token = me["thought_signature"]

            usage: dict[str, Any] = {}
            resp_usage = _safe_static_getattr(response, "usage")
            if resp_usage:
                p_tokens = _safe_static_getattr(resp_usage, "prompt_tokens")
                c_tokens = _safe_static_getattr(resp_usage, "completion_tokens")
                t_tokens = _safe_static_getattr(resp_usage, "total_tokens")

                if p_tokens is not None:
                    usage["prompt_tokens"] = p_tokens
                if c_tokens is not None:
                    usage["completion_tokens"] = c_tokens
                if t_tokens is not None:
                    usage["total_tokens"] = t_tokens
                elif p_tokens is not None or c_tokens is not None:
                    # STRICT MATHEMATICAL INVARIANT: Calculated explicitly at the boundary
                    # rather than relying on silent fallbacks in the domain model.
                    sum_tokens = 0
                    if p_tokens is not None:
                        sum_tokens += p_tokens
                    if c_tokens is not None:
                        sum_tokens += c_tokens
                    usage["total_tokens"] = sum_tokens

                p_details = _safe_static_getattr(resp_usage, "prompt_tokens_details")
                if p_details:
                    cached_tok = _safe_static_getattr(p_details, "cached_tokens")
                    if cached_tok is not None:
                        usage["cached_tokens"] = cached_tok

                c_details = _safe_static_getattr(resp_usage, "completion_tokens_details")
                if c_details:
                    reasoning_tok = _safe_static_getattr(c_details, "reasoning_tokens")
                    if reasoning_tok is not None:
                        usage["reasoning_tokens"] = reasoning_tok

            final_content = raw_content
            parsed_obj = None

            cached_tokens_val = 0
            if "cached_tokens" in usage and usage["cached_tokens"] is not None:
                cached_tokens_val = usage["cached_tokens"]
            LLMCachingService.record_cache_hit(bool(cached_tokens_val and cached_tokens_val > 0))

            active_span = otel_trace.get_current_span()
            if active_span.is_recording():
                resp_model = _safe_static_getattr(response, "model")
                if resp_model:
                    active_span.set_attribute("gen_ai.response.model", str(resp_model))
                if "prompt_tokens" in usage and usage["prompt_tokens"] is not None:
                    active_span.set_attribute("gen_ai.usage.input_tokens", int(usage["prompt_tokens"]))
                if "completion_tokens" in usage and usage["completion_tokens"] is not None:
                    active_span.set_attribute("gen_ai.usage.output_tokens", int(usage["completion_tokens"]))

            # --- ADVANCED TELEMETRY & METADATA ---
            system_fingerprint = _safe_static_getattr(response, "system_fingerprint")
            if finish_reason in ["stop", "eos"]:
                finish_reason = None

            provider_meta = {}
            dump_fn = _safe_static_getattr(response, "model_dump")
            if callable(dump_fn):
                provider_meta = dump_fn()

            # Rate limits
            hidden_params = _safe_static_getattr(response, "_hidden_params")
            if isinstance(hidden_params, dict):
                headers = {}
                if "headers" in hidden_params:
                    headers = hidden_params["headers"]
                if isinstance(headers, dict):
                    ratelimit_key = "x-ratelimit-remaining-requests"
                    rem_reqs = None
                    if ratelimit_key in headers:
                        rem_reqs = headers[ratelimit_key]
                    if rem_reqs:
                        provider_meta["rate_limit_remaining"] = rem_reqs
                        if str(rem_reqs).isdigit() and int(rem_reqs) < 10:
                            logger.warning("[LiteLLMProvider] QUOTA WARNING: Only %s requests remaining.", rem_reqs)

            # Vertex AI Safety & Grounding Citations
            model_extra = _safe_static_getattr(response, "model_extra")
            if isinstance(model_extra, dict):
                if "safety_ratings" in model_extra:
                    provider_meta["safety_ratings"] = model_extra["safety_ratings"]
                gm = {}
                if "grounding_metadata" in model_extra:
                    gm = model_extra["grounding_metadata"]
                if isinstance(gm, dict) and "grounding_chunks" in gm:
                    urls = [
                        chunk["web"]["uri"]
                        for chunk in gm["grounding_chunks"]
                        if isinstance(chunk, dict) and "web" in chunk and "uri" in chunk["web"]
                    ]
                    if urls:
                        provider_meta["grounding_urls"] = urls
                        if not response_schema:
                            # Only inject raw markdown if we are NOT expecting a strictly structured JSON response.
                            final_content += "\n\n**Lähteet (Google Search Grounding):**\n"
                            final_content += "\n".join([f"- [{url}]({url})" for url in urls])

            # --- COST TRACKING ---
            cost = 0.0
            try:
                # Calculate cost using LiteLLM, explicitly passing the actual model name to ensure FinOps accuracy.
                base_model_name = self.model_name.split("/")[-1] if "/" in self.model_name else self.model_name
                cost = litellm.completion_cost(completion_response=response, model=base_model_name)
            except Exception as e:
                logger.error("[LiteLLMProvider] Cost Calculation Failed: %s", e)
                raise AgentExecutionError(
                    detail=ErrorCodes.UNKNOWN_ERROR, original_error=e, agent_name=self.model_name
                ) from e

            if self.usage_service:
                try:
                    # Resolve IDs from kwargs (execution config) or provider instance
                    target_org = self.organization_id
                    if "organization_id" in kwargs and kwargs["organization_id"]:
                        target_org = kwargs["organization_id"]
                    target_user = "system_agent"
                    if "user_id" in kwargs and kwargs["user_id"]:
                        target_user = kwargs["user_id"]

                    in_tokens = 0
                    if "prompt_tokens" in usage:
                        in_tokens = int(usage["prompt_tokens"])
                    out_tokens = 0
                    if "completion_tokens" in usage:
                        out_tokens = int(usage["completion_tokens"])
                    cached_tok = 0
                    if "cached_tokens" in usage:
                        cached_tok = int(usage["cached_tokens"])
                    reasoning_tok = 0
                    if "reasoning_tokens" in usage:
                        reasoning_tok = int(usage["reasoning_tokens"])
                    finish_reason_str = None
                    if finish_reason:
                        finish_reason_str = str(finish_reason)

                    # Track usage asynchronously using the actual model name to log fallback statistics correctly.
                    await self.usage_service.track_usage(
                        org_id=target_org,
                        user_id=target_user,
                        model=self.model_name,
                        input_tokens=in_tokens,
                        output_tokens=out_tokens,
                        cached_tokens=cached_tok,
                        reasoning_tokens=reasoning_tok,
                        latency_ms=latency_ms,
                        finish_reason=finish_reason_str,
                        system_fingerprint=system_fingerprint,
                        cost_usd=cost,
                    )
                except Exception as e:
                    logger.error("[LiteLLMProvider] Usage Tracking Failed: %s", e)
                    raise AppException(
                        message=f"Usage Tracking Failed: {e}",
                        status_code=500,
                        details={"error_code": ErrorCodes.UNKNOWN_ERROR.value},
                    ) from e

            # Inject cost into usage dict so BaseAgent can pick it up
            usage["cost_usd"] = cost

            # Extract tool_calls from LLM response (MCP Tool Loop support)
            extracted_tool_calls: list[OpenAIToolCallDTO] = []
            raw_tool_calls = None
            if "tool_calls" in dir(message):
                raw_tool_calls = message.tool_calls
            if raw_tool_calls:
                for tc in raw_tool_calls:
                    if isinstance(tc, OpenAIToolCallDTO):
                        extracted_tool_calls.append(tc)
                    elif "model_dump" in dir(tc):
                        extracted_tool_calls.append(OpenAIToolCallDTO.model_validate(tc.model_dump()))
                    elif type(tc) is dict:
                        extracted_tool_calls.append(OpenAIToolCallDTO.model_validate(tc))
                    else:
                        fn = None
                        if "function" in dir(tc):
                            fn = tc.function
                        fn_name = "unknown"
                        fn_args = "{}"
                        if fn:
                            if "name" in dir(fn):
                                fn_name = fn.name
                            if "arguments" in dir(fn):
                                fn_args = fn.arguments
                        fn_dto = OpenAIFunctionCallDTO(name=fn_name, arguments=fn_args)
                        tc_id = f"call_{uuid.uuid4().hex[:8]}"
                        if "id" in dir(tc):
                            tc_id = str(tc.id)
                        extracted_tool_calls.append(OpenAIToolCallDTO(id=tc_id, function=fn_dto))

            prov_finish_str = None
            if finish_reason:
                prov_finish_str = str(finish_reason)
            prov_raw_extra = None
            if provider_meta:
                prov_raw_extra = provider_meta

            provider_meta_dto = ProviderMetadataDTO(
                finish_reason=prov_finish_str,
                raw_extra=prov_raw_extra,
            )

            typed_messages: list[LLMMessageDTO] = [
                m if isinstance(m, LLMMessageDTO) else LLMMessageDTO.model_validate(m) for m in final_messages
            ]

            parsed_content_val = None
            if response_schema:
                parsed_content_val = parsed_obj
            tool_calls_val = None
            if extracted_tool_calls:
                tool_calls_val = extracted_tool_calls

            return LLMResponse(
                content=final_content,
                parsed_content=parsed_content_val,
                reasoning_token=reasoning_token,
                token_usage=TokenUsage.model_validate(usage),
                provider_metadata=provider_meta_dto,
                system_fingerprint=system_fingerprint,
                tool_calls=tool_calls_val,
                messages=typed_messages,
                override_reason=None,
            )

        except Exception as e:
            err_span = otel_trace.get_current_span()
            if err_span.is_recording():
                err_span.record_exception(e)
                err_span.set_status(otel_trace.StatusCode.ERROR, str(e))

            if isinstance(e, AppException):
                raise e

            # Jan 2026: Reduce Error Verbosity & Improve Classification
            error_msg = str(e)
            error_type = type(e).__name__
            status_code = _safe_static_getattr(e, "status_code")
            from litellm.exceptions import (
                APIConnectionError,
                AuthenticationError,
                ContextWindowExceededError,
                RateLimitError,
            )
            from litellm.exceptions import (
                ServiceUnavailableError as LiteLLMServiceUnavailableError,
            )
            from litellm.exceptions import (
                Timeout as LiteLLMTimeout,
            )

            # 0. DIRECT PASS-THROUGH (Network Errors for BaseAgent)
            if (
                isinstance(e, APIConnectionError)
                or "NameResolutionError" in error_type
                or "ConnectTimeout" in error_type
                or "gaierror" in error_type
            ):
                raise e

            # 1. RATE LIMITS & QUOTA (Critical Infra)
            # 429s are natively handled in the inner retry loop! If they bubble here, retries were exhausted.
            if isinstance(e, RateLimitError) or status_code == 429 or "Resource exhausted" in error_msg:
                logger.error(
                    "[LiteLLM] %s: RESOURCE EXHAUSTED (Retries depleted): %s",
                    ErrorCodes.RATE_LIMIT_EXCEEDED.name,
                    error_msg,
                )
                raise ServiceUnavailableError(
                    message="Model provider rate limit exceeded and all automatic retries failed.",
                    details={"error_code": ErrorCodes.RATE_LIMIT_EXCEEDED.value, "original_error": error_msg},
                ) from e

            # 1.1 OUTPUT LIMIT (Model Looping/Max Tokens/Empty Response)
            elif "InstructorRetryException" in error_type or "ResponseParsingError" in error_type:
                logger.error(
                    "[LiteLLM] %s: INSTRUCTOR / MODEL FAILURE (Empty choices or schema mismatch): %s",
                    ErrorCodes.AGENT_RESPONSE_PARSING_FAILED.name,
                    error_msg,
                )
                raise AppException(
                    message="Model failed to generate structured output (empty response or looping).",
                    status_code=500,
                    details={"error_code": ErrorCodes.AGENT_RESPONSE_PARSING_FAILED.value, "original_error": error_msg},
                ) from e

            # 2. AUTHENTICATION ALERTS (Security/Config)
            elif isinstance(e, AuthenticationError) or status_code == 401 or "invalid_api_key" in error_msg:
                logger.critical(
                    "[LiteLLM] %s: AUTH FAILED (Check API Keys): %s", ErrorCodes.CONFIGURATION_ERROR.name, error_msg
                )
                raise ConfigurationError(
                    message="LLM Provider authentication failed.",
                    details={
                        "error_code": ErrorCodes.CONFIGURATION_ERROR.value,
                        "original_error": "Invalid API Key or Credential",
                    },
                ) from e

            # 3. CONTEXT WINDOW (Data/Prompt Engineering)
            elif isinstance(e, ContextWindowExceededError) or (
                status_code == 400 and ("context" in error_msg.lower() or "token" in error_msg.lower())
            ):
                logger.error(
                    "[LiteLLM] %s: CONTEXT EXCEEDED (Prompt too long): %s",
                    ErrorCodes.AGENT_EXECUTION_CRITICAL.name,
                    error_msg,
                )
                raise AgentExecutionError(
                    detail=ErrorCodes.AGENT_EXECUTION_CRITICAL, original_error=e, agent_name=self.model_name
                ) from e
            elif status_code == 400:
                logger.error("[LiteLLM] %s: BAD REQUEST (400): %s", ErrorCodes.AGENT_RESPONSE_MALFORMED.name, error_msg)
                raise AgentExecutionError(
                    detail=ErrorCodes.AGENT_RESPONSE_MALFORMED, original_error=e, agent_name=self.model_name
                ) from e

            # 4. SERVICE INSTABILITY (Infra)
            elif (
                isinstance(e, LiteLLMServiceUnavailableError)
                or isinstance(e, LiteLLMTimeout)
                or isinstance(e, asyncio.TimeoutError)
                or (isinstance(status_code, int) and status_code in (500, 502, 503, 504))
            ):
                logger.error(
                    "[LiteLLM] %s: SERVICE UNAVAILABLE (Upstream/Timeout): %s",
                    ErrorCodes.UPSTREAM_TIMEOUT.name,
                    error_msg,
                )
                raise ServiceUnavailableError(
                    message="Upstream LLM service timed out or is unavailable.",
                    details={"error_code": ErrorCodes.UPSTREAM_TIMEOUT.value, "original_error": error_msg},
                ) from e

            # 5. CONTENT POLICY (Safety)
            elif "ContentPolicyViolation" in error_type or "blocked" in error_msg.lower():
                logger.warning(
                    "[LiteLLM] %s: SAFETY FILTER TRIGGERED: %s", ErrorCodes.SECURITY_VIOLATION.name, error_msg
                )
                raise SecurityViolationError(
                    message="Content blocked by safety filters.",
                    details={"error_code": ErrorCodes.SECURITY_VIOLATION.value, "original_error": error_msg},
                ) from e

            # 6. GENERIC FALLBACK (Fail Fast)
            else:
                if len(error_msg) > 500:
                    error_msg = error_msg[:500] + "... [TRUNCATED]"
                logger.error(
                    "[LiteLLM] %s: Execution Failed (%s): %s",
                    ErrorCodes.UNKNOWN_ERROR.name,
                    error_type,
                    error_msg,
                    exc_info=True,
                )

                # Default to ServiceUnavailable for unknown upstream errors
                raise ServiceUnavailableError(
                    message=f"Unknown upstream LLM error: {error_type}",
                    details={"error_code": ErrorCodes.UNKNOWN_ERROR.value, "original_error": error_msg},
                ) from e


class MockProvider(LLMProvider):
    """Mock LLM Provider for offline testing and development.

    Uses cached/simulated responses from MockLLMService.
    """

    def __init__(
        self,
        model_name: str = "mock",
        usage_service: UsageService | None = None,
        organization_id: str | None = None,
    ):
        """Initialize the Mock Provider.

        Args:
            model_name: Identifier.
            usage_service: Optional usage tracking.
            organization_id: Identity.

        Raises:
            ConfigurationError: If mock environment is completely misconfigured.
        """
        self.model_name = model_name
        self.usage_service = usage_service
        if organization_id:
            self.organization_id = organization_id
        else:
            self.organization_id = "UNKNOWN_ORG"

    async def generate(
        self,
        prompt: str | None = None,
        system_instruction: str | None = None,
        messages: list[LLMMessageDTO] | list[dict[str, Any]] | None = None,
        response_schema: type[BaseModel] | dict[str, Any] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        frequency_penalty: float | None = None,
        presence_penalty: float | None = None,
        pass_reasoning_token: str | None = None,
        validation_context: dict[str, Any] | None = None,
        mock_identity: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Simulates generation by invoking the MockLLMService.

        Args:
            prompt: Text to generate from.
            system_instruction: System prompt.
            messages: Fallback conversational state.
            response_schema: Return type constraints.
            temperature: (float) sampling value.
            max_tokens: Limit.
            top_p: P-sample.
            top_k: K-sample.
            frequency_penalty: Penalty for repeated tokens.
            presence_penalty: Penalty for new topic presence.
            pass_reasoning_token: Blob.
            validation_context: Custom dict.
            mock_identity: Explicit mock fixture identity.
            **kwargs: Extra parameters.

        Returns:
            LLMResponse: A mocked success response matching the requested schema.

        Raises:
            ConfigurationError: If parameters missing or seed not found.
            AppException: If parsing fails.
        """
        logger.info("[MockProvider] Calling Mock Service (Simulating Async)... %s", kwargs)

        # STRICT CONFIGURATION (Jan 2026): Reject defaults in Mock too.
        if temperature is None:
            msg = "Strict Mode: 'temperature' must be explicitly provided from configuration. No default allowed."
            logger.error("[MockProvider] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
            raise ConfigurationError(message=msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})

        if max_tokens is None:
            msg = "Strict Mode: 'max_tokens' must be explicitly provided from configuration. No default allowed."
            logger.error("[MockProvider] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
            raise ConfigurationError(message=msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})

        # --- DIAGNOSTIC DUMP ---
        dump_file = os.getenv("DUMP_PROMPTS_FILE")
        if dump_file:
            try:
                payload_parts = []
                if prompt:
                    payload_parts.append(f"PROMPT:\n{prompt}")
                if messages:
                    payload_parts.append(f"MESSAGES:\n{messages}")
                if system_instruction:
                    payload_parts.append(f"SYSTEM:\n{system_instruction}")
                payload = "\n".join(payload_parts)
                await asyncio.to_thread(_sync_diagnostic_dump, dump_file, f"[MockProvider] {self.model_name}", payload)
            except Exception as e:
                logger.error("Failed to schedule diagnostic dump: %s", e)
                raise ConfigurationError(
                    message=f"Diagnostic dump dispatch failed: {e}",
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                ) from e

        # Simulate network delay for verification of async behavior
        mock_pacing_delay = get_settings().pacing_delay_mock_seconds
        if mock_pacing_delay > 0:
            await asyncio.sleep(mock_pacing_delay)

        mock = MockLLMService()  # MockLLMService on untyped legacy moduuli

        # Extract explicit identity if provided
        agent_identity = mock_identity

        prompt_str = ""
        if prompt:
            prompt_str = prompt
        if messages and not prompt_str:
            # Fallback to serializing messages if prompt is empty
            prompt_str = json.dumps(
                [m.model_dump(mode="json", exclude_none=True) if isinstance(m, BaseModel) else m for m in messages]
            )

        result = mock.generate_content(
            prompt_str,
            system_instruction,
            agent_identity=agent_identity,
            response_schema=response_schema,
        )

        # Determine content string and parsed object
        content_str = ""
        parsed_result = None

        if isinstance(result, dict) and "message" in result and result["message"] == "Mock data not found for key":
            # STRICT MANDATE: No mock hydration fallbacks. If seed missing, crash properly.
            raise ConfigurationError(
                message=(
                    f"Fail-Fast: Mock data not found in Seed Vault. Prompt missing mock definition: {prompt[:100]}..."
                ),
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )
        else:
            if isinstance(result, dict):
                content_str = json.dumps(result, ensure_ascii=False)
                parsed_result = result
            elif isinstance(result, BaseModel):
                content_str = result.model_dump_json()
                parsed_result = result.model_dump()
            else:
                # Assume it's a string (JSON)
                content_str = str(result)
                try:
                    parsed_result = json.loads(content_str)
                except Exception as parse_err:
                    raise AppException(
                        message=f"Mock response parsing failed: {parse_err}",
                        status_code=500,
                        details={"error_code": ErrorCodes.AGENT_RESPONSE_PARSING_FAILED.value},
                    ) from parse_err

        # Simulated Usage

        # Simulated Usage
        usage_data = {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
            "total_cost": 0.002,
        }

        # --- COST TRACKING (Mock) ---
        if self.usage_service:
            try:
                target_org = self.organization_id
                if "organization_id" in kwargs and kwargs["organization_id"]:
                    target_org = kwargs["organization_id"]
                target_user = "system_agent"
                if "user_id" in kwargs and kwargs["user_id"]:
                    target_user = kwargs["user_id"]

                await self.usage_service.track_usage(
                    org_id=target_org,
                    user_id=target_user,
                    model=self.model_name,
                    input_tokens=int(usage_data["prompt_tokens"]),
                    output_tokens=int(usage_data["completion_tokens"]),
                    cost_usd=usage_data["total_cost"],
                )
            except Exception as e:
                logger.error("[MockProvider] Usage Tracking Failed: %s", e)
                raise AppException(
                    message=f"Usage Tracking Failed: {e}",
                    status_code=500,
                    details={"error_code": ErrorCodes.UNKNOWN_ERROR.value},
                ) from e

        mock_messages: list[LLMMessageDTO] = []
        if system_instruction:
            mock_messages.append(LLMMessageDTO(role="system", content=system_instruction))
        if prompt:
            mock_messages.append(LLMMessageDTO(role="user", content=prompt))

        return LLMResponse(
            content=content_str,
            parsed_content=parsed_result,
            reasoning_token="mock_thought_signature_123456",
            token_usage=TokenUsage(
                prompt_tokens=int(usage_data["prompt_tokens"]),
                completion_tokens=int(usage_data["completion_tokens"]),
                total_tokens=int(usage_data["total_tokens"]),
                cost_usd=float(usage_data["total_cost"]),
            ),
            tool_calls=None,
            provider_metadata=ProviderMetadataDTO(),
            messages=mock_messages,
        )


class LLMFactory:
    """Factory class to instantiate the appropriate LLMProvider based on configuration."""

    @staticmethod
    def create_provider(
        provider_type: str,
        model_name: str,
        context: dict[str, Any] | Any | None = None,
        organization_id: str | None = None,
        usage_service: UsageService | None = None,
        limits: dict[str, int] | None = None,
        api_key: str | None = None,
        config: LLMProviderConfig | None = None,
        **kwargs: Any,
    ) -> LLMProvider:
        """Factory method to create an LLM Provider instance.

        Args:
            provider_type: Type key (e.g. 'litellm', 'mock').
            model_name: Model identifier.
            context: Additional context or settings.
            organization_id: Organization ID for tracking.
            usage_service: Usage service instance.
            limits: Usage limits (tpm, rpm).
            api_key: Explicit API Key override (e.g. for ad-hoc testing).
            config: Strict configuration object (Database-Driven).
            **kwargs: Additional arguments.

        Returns:
            Configured provider instance.

        Raises:
            ConfigurationError: If provider configuration is invalid or grounding is requested but not supported.
            ServiceUnavailableError: If the provider is disabled.
        """
        settings = get_settings()

        # Resolve Configuration Source
        # If 'config' is passed, it is the Authority.
        if config:
            provider_type = config.provider
            model_name = config.model_name
            # If Config says "is_active=False", we should have caught this upstream,
            # but we can enforce it here too as a fail-safe.
            if not config.is_active:
                logger.error(
                    "[LLMFactory] %s: Provider '%s' is disabled in configuration.",
                    ErrorCodes.SERVICE_DISABLED.name,
                    model_name,
                )
                raise ServiceUnavailableError(
                    message=f"Provider '{model_name}' is disabled in configuration.",
                    details={"error_code": ErrorCodes.SERVICE_DISABLED.value},
                )

            # Resolve Limits from Config
            if not limits:
                limits = {}
            if config.tpm_limit > 0:
                limits["tpm"] = config.tpm_limit
            if config.rpm_limit > 0:
                limits["rpm"] = config.rpm_limit

            # Resolve API Key
            if config.api_key:
                api_key = config.api_key

            # Check Grounding Capability (Strict Mode: Fail Fast)
            # If caller requests grounding, but config says NO, we RAISE ERROR.
            # We do NOT fallback to non-grounded generation.
            tools = []
            if "tools" in kwargs:
                tools = kwargs["tools"]
            enable_grounding = False
            if "enable_grounding" in kwargs:
                enable_grounding = kwargs["enable_grounding"]

            # Check for Google Search tool or explicit flag
            has_search_intent = enable_grounding or (tools and any("google_search" in str(t) for t in tools))

            if has_search_intent:
                if not config.supports_grounding:
                    msg = (
                        f"Grounding/Search requested for '{model_name}' "
                        "but provider config 'supports_grounding' is False."
                    )
                    logger.error("[LLMFactory] %s: %s", ErrorCodes.CAPABILITY_NOT_SUPPORTED.name, msg)
                raise ConfigurationError(
                    message=msg,
                    details={"error_code": ErrorCodes.CAPABILITY_NOT_SUPPORTED.value},
                )

            # Strict Limits: If limits are missing in config, we do NOT default to empty.
            # However, logic above extracts them from config if present.
            # If they are 0 in config, that's explicit "unlimited".
            # If config was None (legacy path?), we fall through.

        # Placeholder for BYOK (Bring Your Own Key) Logic

        # STRICT EXECUTION AUTHORITY (Jan 19 Update):
        # GLOBAL SAFETY: If 'settings.use_mock_llm' is True, we FORCE the MockProvider.
        # This guarantees that 'run_mock.bat' implies 100% offline mode, regardless of
        # what provider specific agents request (e.g. 'vertex_ai').
        mock_model_name = "mock"
        if model_name:
            mock_model_name = model_name

        if settings.use_mock_llm:
            logger.warning(
                "[LLMFactory] Global USE_MOCK_LLM=True. Overriding request for '%s' -> MockProvider.", provider_type
            )
            return MockProvider(
                model_name=mock_model_name,
                usage_service=usage_service,
                organization_id=organization_id,
            )

        # STRICT CONFIGURATION:
        # If not in global mock mode, we DO NOT allow 'mock' to be implicitly selected
        # unless explicitly requested. If 'vertex_ai' is requested, we get Vertex (or fail).
        if provider_type in ("mock", "mock_llm_99"):
            return MockProvider(
                model_name=mock_model_name,
                usage_service=usage_service,
                organization_id=organization_id,
            )

        if not model_name:
            logger.error(
                "[LLMFactory] %s: Model name is required for LLMProvider creation.", ErrorCodes.CONFIGURATION_ERROR.name
            )
            raise ConfigurationError(
                message="Model name is required for LLMProvider creation.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        resolved_api_key = api_key
        match provider_type.lower():
            case LLMProviderName.VERTEX_AI.value | "vertex_ai":
                # Vertex AI authenticates via GCP Application Default Credentials backed by service-account.json
                resolved_api_key = None
            case LLMProviderName.AI_STUDIO.value | "ai_studio":
                resolved_api_key = resolved_api_key or settings.google_api_key
                if not resolved_api_key:
                    logger.error(
                        "Fail-Fast: GEMINI_API_KEY / GOOGLE_API_KEY is not configured in settings or environment.",
                        extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "model_name": model_name},
                    )
                    raise ConfigurationError(
                        message=(
                            "Fail-Fast: GEMINI_API_KEY / GOOGLE_API_KEY is not configured in settings or environment."
                        ),
                        details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                    )
            case LLMProviderName.OPENAI.value | "openai":
                resolved_api_key = resolved_api_key or settings.openai_api_key
                if not resolved_api_key:
                    logger.error(
                        "Fail-Fast: OPENAI_API_KEY is not configured in settings or environment.",
                        extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "model_name": model_name},
                    )
                    raise ConfigurationError(
                        message="Fail-Fast: OPENAI_API_KEY is not configured in settings or environment.",
                        details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                    )
            case LLMProviderName.ANTHROPIC.value | "anthropic":
                resolved_api_key = resolved_api_key or settings.anthropic_api_key
                if not resolved_api_key:
                    logger.error(
                        "Fail-Fast: ANTHROPIC_API_KEY is not configured in settings or environment.",
                        extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "model_name": model_name},
                    )
                    raise ConfigurationError(
                        message="Fail-Fast: ANTHROPIC_API_KEY is not configured in settings or environment.",
                        details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                    )
            case "litellm":
                pass
            case _:
                pass

        return LiteLLMProvider(
            model_name=model_name,
            api_key=resolved_api_key,
            settings=settings,
            usage_service=usage_service,
            organization_id=organization_id,
            limits=limits,
            supports_grounding=config.supports_grounding if config else False,
            config=config,
        )
