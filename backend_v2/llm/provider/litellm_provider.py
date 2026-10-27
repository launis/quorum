"""LiteLLMProvider orchestrating rate-limited Router calls, pacing, retries, and response stages."""

import asyncio
import json
import logging
import os
import sys
import time
from typing import Any, override

from pydantic import BaseModel
from tenacity import AsyncRetrying, retry_if_exception, stop_after_attempt, wait_exponential_jitter

from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.llm.adapters.base_adapter import apply_provider_pacing
from backend_v2.llm.provider.base_and_mock_provider import LLMProvider, LogfireShieldedClient
from backend_v2.llm.provider.env_and_schema_utils import (
    _INTERNAL_NON_API_KEYS,
    _normalize_mcp_tool_schema_for_llm,
    _sync_diagnostic_dump,
    resolve_env_variables,
)
from backend_v2.llm.provider.litellm_response_stage import (
    _truncate_for_debug,
    classify_and_raise_litellm_error,
    extract_litellm_content_and_usage,
)
from backend_v2.llm.provider.transient_retry_policy import (
    _AdaptiveWaitWithRetryAfter,
    _format_attempt_error,
    _is_transient_llm_error,
)
from backend_v2.models.llm import LLMMessageDTO, LLMProviderConfig, LLMResponse
from backend_v2.services.usage_service import UsageService
from backend_v2.settings import get_settings

__all__ = ["LiteLLMProvider"]

logger = logging.getLogger(__name__)
_ORIG_GET_SETTINGS = get_settings
_ORIG_APPLY_PROVIDER_PACING = apply_provider_pacing


def _resolve_get_settings() -> Any:
    """Resolve get_settings honoring monkeypatches on either submodule or provider facade.

    Returns:
        Active get_settings callable.
    """
    if get_settings is not _ORIG_GET_SETTINGS:
        return get_settings
    if "backend_v2.llm.provider" in sys.modules:
        provider_mod: Any = sys.modules["backend_v2.llm.provider"]
        if "get_settings" in dir(provider_mod):
            return provider_mod.get_settings
    return get_settings


def _resolve_apply_provider_pacing() -> Any:
    """Resolve apply_provider_pacing honoring monkeypatches on either submodule or provider facade.

    Returns:
        Active apply_provider_pacing async callable.
    """
    if apply_provider_pacing is not _ORIG_APPLY_PROVIDER_PACING:
        return apply_provider_pacing
    if "backend_v2.llm.provider" in sys.modules:
        provider_mod: Any = sys.modules["backend_v2.llm.provider"]
        if "apply_provider_pacing" in dir(provider_mod):
            return provider_mod.apply_provider_pacing
    return apply_provider_pacing


# Phase 3, Step 1: Relocate LiteLLMProvider into dedicated module (< 430 lines)
class LiteLLMProvider(LLMProvider):
    """Unified LLM Provider using LiteLLM to support multiple models (Gemini, OpenAI, Anthropic).

    Provides a consistent interface with dynamic RPM semaphores and adaptive retry policies.
    """

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
    ) -> None:
        """Initialize the LiteLLM provider.

        Args:
            model_name: The model identifier.
            api_key: API Key.
            settings: System settings object.
            usage_service: Service for cost tracking.
            organization_id: Context organization ID.
            limits: Override TPM/RPM limits (specifically from Organization or ModelProfile).
            supports_grounding: Whether this model strategy requires Vertex Grounding.
            config: Strict configuration object.

        Raises:
            ConfigurationError: If strict tpm/rpm limits are not provided.
        """
        self.model_name = model_name
        self.api_key = api_key
        self.settings = settings
        self.usage_service = usage_service
        self.organization_id = "UNKNOWN_ORG" if not organization_id else organization_id
        self.supports_grounding = supports_grounding
        self._config = config

        import litellm
        from litellm.router import Router

        litellm.drop_params = True
        litellm.num_retries = 0  # CRITICAL: Disable internal retries so Tenacity is in control

        if not limits:
            msg = (
                "Strict Mode: LLM Rate Limits (TPM/RPM) must be explicitly passed "
                "to Provider. No hardcoded defaults allowed."
            )
            logger.error("[LiteLLMProvider] %s", msg)
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})

        tpm = None if "tpm" not in limits else limits["tpm"]
        rpm = None if "rpm" not in limits else limits["rpm"]

        if tpm is None or rpm is None:
            msg = "Strict Mode: Both TPM and RPM must be defined in limits config."
            logger.error("[LiteLLMProvider] %s", msg)
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})

        cache_key = f"{model_name}_{tpm}_{rpm}"
        self.cache_key = cache_key

        active_settings_fn = _resolve_get_settings()
        if cache_key in self.__class__._router_cache:
            self.router = self.__class__._router_cache[cache_key]
        else:
            litellm_params: dict[str, Any] = {"model": model_name, "tpm": tpm, "rpm": rpm}
            if self.api_key is not None:
                litellm_params["api_key"] = self.api_key

            model_config = {
                "model_name": model_name,
                "litellm_params": litellm_params,
                "model_info": {"id": model_name},
            }
            resolved_settings = active_settings_fn()
            self.router = Router(
                model_list=[model_config],
                set_verbose=False,
                num_retries=0,
                timeout=float(resolved_settings.llm_default_timeout),
                routing_strategy="simple-shuffle",
                allowed_fails=0,
                cooldown_time=0,
            )
            self.__class__._router_cache[cache_key] = self.router

        if cache_key not in self.__class__._semaphores:
            sem_cfg = active_settings_fn()
            div_limit = min(sem_cfg.semaphore_max_concurrency, max(1, rpm // sem_cfg.semaphore_rpm_divisor))
            limit = sem_cfg.semaphore_low_rpm_limit if rpm <= sem_cfg.semaphore_low_rpm_threshold else div_limit
            sem_msg = "[LiteLLMProvider] Initializing HTTP concurrency semaphore for '%s' (limit=%d)"
            logger.info(sem_msg, cache_key, limit)
            self.__class__._semaphores[cache_key] = asyncio.Semaphore(limit)

    @override
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
        """Generate content using LiteLLM with dynamic RPM semaphore and adaptive retries.

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
            Unified LLMResponse with content, token usage, and reasoning state.

        Raises:
            AgentExecutionError: On context bounds exceeded or bad request.
            AppException: On internal generation or usage tracking errors.
            ConfigurationError: On missing temperature/max_tokens or invalid credentials.
            SecurityViolationError: On blocked content.
            ServiceUnavailableError: On provider rate limit exhaustion or network timeout.
        """
        final_messages: list[LLMMessageDTO | dict[str, Any]] = []
        if messages and "cached_content" in kwargs:
            for m in messages:
                has_role = type(m) is dict and "role" in m
                role = m.role if isinstance(m, LLMMessageDTO) else ("" if not has_role else m["role"])
                if role != "system":
                    final_messages.append(m)
        elif messages:
            final_messages.extend(messages)
        else:
            if system_instruction and "cached_content" not in kwargs:
                final_messages.append({"role": "system", "content": system_instruction})
            if prompt:
                final_messages.append({"role": "user", "content": prompt})

        adapter = None
        if self._config:
            from backend_v2.llm.adapters.adapter_factory import LLMCacheAdapterFactory

            try:
                adapter = LLMCacheAdapterFactory.get_adapter(self._config.provider, model_name=self.model_name)
                final_messages = adapter.sanitize_messages(final_messages)
            except AppException as e:
                logger.debug("[LiteLLMProvider] No adapter found (provider: %s): %s", self._config.provider, e)

        if temperature is None or max_tokens is None:
            missing_param = "temperature" if temperature is None else "max_tokens"
            msg = (
                f"Strict Mode: '{missing_param}' must be explicitly provided "
                "from configuration (Database/Registry). No default allowed."
            )
            logger.error("[LiteLLMProvider] %s", msg)
            raise ConfigurationError(msg)

        if pass_reasoning_token:
            blob_content = f"[SYSTEM: RESUME_THOUGHT_PROCESS] PREVIOUS_STATE_BLOB: {pass_reasoning_token}"
            final_messages.append({"role": "system", "content": blob_content})

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

        try:
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

            active_settings_fn = _resolve_get_settings()
            cfg_settings = self.settings if self.settings is not None else active_settings_fn()
            default_timeout = cfg_settings.llm_default_timeout
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
                "timeout": kwargs["timeout"] if "timeout" in kwargs else default_timeout,
            }
            if self.api_key is not None:
                call_kwargs["api_key"] = self.api_key

            call_kwargs.update(kwargs)
            if "tools" in call_kwargs and call_kwargs["tools"]:
                call_kwargs["tools"] = [
                    _normalize_mcp_tool_schema_for_llm(
                        t.model_dump(mode="json", by_alias=True, exclude_none=True) if isinstance(t, BaseModel) else t
                    )
                    for t in call_kwargs["tools"]
                ]
            for key in _INTERNAL_NON_API_KEYS & call_kwargs.keys():
                del call_kwargs[key]

            if adapter:
                call_kwargs = adapter.prepare_kwargs(call_kwargs, self._config, self.settings)

            if self._config and self._config.additional_params:
                extra_dump = self._config.additional_params.model_dump(exclude_none=True)
                call_kwargs.update(resolve_env_variables(extra_dump))

            if dump_file := os.getenv("DUMP_PROMPTS_FILE"):
                try:
                    payload = json.dumps(serialized_messages, indent=2, ensure_ascii=False)
                    await asyncio.to_thread(_sync_diagnostic_dump, dump_file, f"[LiteLLM] {self.model_name}", payload)
                except Exception as e:
                    logger.error("Failed to schedule diagnostic dump: %s", e)
                    raise ConfigurationError(
                        message=f"Diagnostic dump dispatch failed: {e}",
                        details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                    ) from e

            call_kwargs["model"] = self.model_name
            for key in _INTERNAL_NON_API_KEYS & call_kwargs.keys():
                del call_kwargs[key]

            _timeout_val = float(default_timeout)
            if "timeout" in call_kwargs and call_kwargs["timeout"] is not None:
                _timeout_val = float(call_kwargs["timeout"])
            provider_suffix = "default" if not self._config else self._config.provider
            _client_key = f"httpx_{_timeout_val}_{provider_suffix}"

            if "PYTEST_CURRENT_TEST" not in os.environ:
                if _client_key not in self.__class__._httpx_clients:
                    custom_client = None if not adapter else adapter.build_http_client(_timeout_val)
                    if custom_client:
                        logger.info(
                            "[LiteLLMProvider] Using provider-specific persistent HTTPX client for timeout %s s",
                            _timeout_val,
                        )
                    self.__class__._httpx_clients[_client_key] = custom_client

                resolved_client = self.__class__._httpx_clients[_client_key]
                if resolved_client:
                    call_kwargs["client"] = LogfireShieldedClient(resolved_client)

            retry_settings = active_settings_fn()
            max_rate_limit_retries = retry_settings.llm_max_transient_retries
            response = None
            start_time = time.perf_counter()

            # Phase 3, Step 1: Enforce Adaptive Exponential Backoff with Upstream Retry-After
            j_init = retry_settings.llm_retry_jitter_initial_seconds
            j_max = retry_settings.llm_retry_max_seconds
            j_base = retry_settings.llm_retry_jitter_exp_base
            base_wait = wait_exponential_jitter(initial=j_init, max=j_max, exp_base=j_base, jitter=1)
            adaptive_wait = _AdaptiveWaitWithRetryAfter(base_wait=base_wait, max_seconds=float(j_max))
            pacing_fn = _resolve_apply_provider_pacing()

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
                    async with self.__class__._semaphores[self.cache_key]:
                        start_time = time.perf_counter()

                        async def _execute_paced_completion() -> Any:
                            prov_prefix = self.model_name.split("/")[0] if "/" in self.model_name else self.model_name
                            provider_key = self._config.provider if self._config else prov_prefix
                            target_resource = self._config.model_name if self._config else self.model_name
                            config_rpm_limit = None if not self._config else self._config.rpm_limit
                            await pacing_fn(
                                provider_name=provider_key, strategy_id=target_resource, rpm_limit=config_rpm_limit
                            )
                            return await self.router.acompletion(**call_kwargs)

                        response = await asyncio.wait_for(_execute_paced_completion(), timeout=float(_timeout))

            return await extract_litellm_content_and_usage(
                response,
                self.model_name,
                start_time,
                final_messages,
                response_schema,
                self.usage_service,
                self.organization_id,
                kwargs,
            )
        except Exception as e:
            classify_and_raise_litellm_error(e, self.model_name)
            raise
