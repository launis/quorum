"""LLM Provider implementations (LiteLLM, Mock, Unconfigured)."""

import asyncio
import copy
import json
import logging
import os
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    wait_combine,
    wait_exponential,
    wait_random,
)

from backend_v2.exceptions import (
    AgentExecutionError,
    AppException,
    ConfigurationError,
    ErrorCodes,
    SecurityViolationError,
    ServiceUnavailableError,
)
from backend_v2.llm.mock import MockLLMService
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.enums import SystemConcurrency
from backend_v2.models.llm import LLMProviderConfig, LLMResponse
from backend_v2.services.usage_service import UsageService
from backend_v2.settings import get_settings

# Configure logging
logger = logging.getLogger(__name__)

# Ensure env is loaded from project root for LLM secrets
_root_dir = Path(__file__).resolve().parent.parent.parent
_env_path = _root_dir / ".env"
load_dotenv(dotenv_path=_env_path)


def resolve_env_variables(params: dict[str, Any]) -> dict[str, Any]:
    """Replace ${ENV_VAR} references in parameters with actual environment variables."""
    resolved = {}
    for k, v in params.items():
        if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
            env_key = v[2:-1]
            resolved_value = os.getenv(env_key)
            if not resolved_value:
                raise ConfigurationError(
                    f"Strict Mode: Required environment variable '{env_key}' not found in system for parameter '{k}'."
                )
            resolved[k] = resolved_value
        else:
            resolved[k] = v
    return resolved


def _sync_diagnostic_dump(dump_file: str, model_name: str, payload_str: str) -> None:
    """Synchronous file writing for diagnostic dumps to prevent blocking the async event loop."""
    try:
        with open(dump_file, "a", encoding="utf-8") as f:
            f.write(f"\n\n--- {model_name} ---\n")
            f.write(payload_str)
            f.write("\n")
    except Exception as e:
        logger.error("Failed to dump prompt: %s", e, exc_info=True)
        raise AppException(
            message=f"Dump failed: {e}", status_code=500, details={"error_code": ErrorCodes.FILESYSTEM_VIOLATION.value}
        ) from e


def _is_transient_llm_error(e: BaseException) -> bool:
    """Check if the LiteLLM/asyncio exception is a transient rate limit or timeout."""
    import litellm

    return (
        isinstance(e, asyncio.TimeoutError)
        or (hasattr(e, "status_code") and e.status_code in (429, 502, 503, 504))
        or isinstance(e, getattr(litellm, "RateLimitError", type(None)))
        or isinstance(e, getattr(litellm, "Timeout", type(None)))
        or isinstance(e, getattr(litellm, "ServiceUnavailableError", type(None)))
        or isinstance(e, getattr(litellm, "APIConnectionError", type(None)))
    )


class LLMProvider(ABC):
    """Abstract base class for LLM providers.

    Defines the contract for text generation and structured data extraction.
    """

    @abstractmethod
    async def generate(
        self,
        prompt: str | None = None,
        system_instruction: str | None = None,
        messages: list[dict[str, Any]] | None = None,
        response_schema: type[BaseModel] | dict[str, Any] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        pass_reasoning_token: str | None = None,
        validation_context: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generates content from the LLM.

        Args:
        prompt (str): The user prompt.
        system_instruction (str | None): System prompt/context.
        messages (list[dict[str, Any]] | None): Message history.
        response_schema (type[BaseModel] | dict[str, Any] | None): Pydantic model or JSON Schema.
        temperature (float): Sampling temperature.
        max_tokens (int | None): Max tokens to generate.
        top_p (float | None): Top p.
        top_k (int | None): Top k.
        pass_reasoning_token (str | None): Encrypted state blob from previous turn.
        validation_context (dict[str, Any] | None): Validation Context.
        **kwargs: Additional provider-specific arguments.

        Returns:
            LLMResponse: The generated response object.

        """
        pass


class LiteLLMProvider(LLMProvider):
    """Unified LLM Provider using LiteLLM to support multiple models (Gemini, OpenAI, etc.).

    Provides a consistent interface.
    """

    # Class-level cache to prevent litellm callbacks memory leak during bulk executions
    _router_cache: dict[str, Any] = {}
    _semaphores: dict[str, asyncio.Semaphore] = {}

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
            model_name (str): The model identifier.
            api_key (Optional[str]): API Key.
            settings (Any): System settings object.
            usage_service (Optional[UsageService]): Service for cost tracking.
            organization_id (Optional[str]): Context organization ID.
            limits (Optional[dict]): Override TPM/RPM limits (e.g. from Organization).
            supports_grounding (bool): Whether this model strategy requires Vertex Grounding.
            config (Optional[LLMProviderConfig]): Strict configuration object.
        """
        self.model_name = model_name
        self.api_key = api_key
        self.settings = settings
        self.usage_service = usage_service
        self.organization_id = organization_id or "UNKNOWN_ORG"
        self.supports_grounding = supports_grounding
        self._config = config

        import litellm
        from litellm import Router  # type: ignore[attr-defined] # External library typing constraint

        # litellm general config
        litellm.drop_params = True
        litellm.num_retries = 0  # CRITICAL: Disable internal retries so Tenacity is in control

        if not limits:
            msg = (
                "Strict Mode: LLM Rate Limits (TPM/RPM) must be explicitly passed "
                "to Provider. No hardcoded defaults allowed."
            )
            logger.error("[LiteLLMProvider] %s", msg)
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR})

        tpm = limits.get("tpm")
        rpm = limits.get("rpm")

        if tpm is None or rpm is None:
            msg = "Strict Mode: Both TPM and RPM must be defined in limits config."
            logger.error("[LiteLLMProvider] %s", msg)
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR})

        # Use Class Cache for Router to avoid MAX_CALLBACKS leak
        cache_key = f"{model_name}_{tpm}_{rpm}"
        self.cache_key = cache_key

        if cache_key in self.__class__._router_cache:
            self.router = self.__class__._router_cache[cache_key]
        else:
            # 2. Build deployment config
            model_config = {
                "model_name": model_name,  # The alias we use
                "litellm_params": {
                    "model": model_name,  # The actual provider model name
                    "api_key": api_key,
                    "tpm": tpm,
                    "rpm": rpm,
                },
            }

            # 3. Initialize Router
            self.router = Router(
                model_list=[model_config],
                set_verbose=False,
                num_retries=0,
            )

            # Save to class cache
            self.__class__._router_cache[cache_key] = self.router

        # Initialize and store Semaphore dynamically to throttle HTTP-level requests
        if cache_key not in self.__class__._semaphores:
            if rpm <= 20:
                concurrency_limit = 2
            else:
                concurrency_limit = min(5, max(1, rpm // 10))

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
        messages: list[dict[str, Any]] | None = None,
        response_schema: type[BaseModel] | dict[str, Any] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        pass_reasoning_token: str | None = None,
        validation_context: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generates content using LiteLLM.

        Returns unified LLMResponse with content and reasoning state.
        """
        import litellm

        final_messages: list[dict[str, Any]] = []
        if messages:
            final_messages.extend(messages)
        else:
            if system_instruction:
                final_messages.append({"role": "system", "content": system_instruction})
            if prompt:
                final_messages.append({"role": "user", "content": prompt})

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
                    schema_name = response_schema.__name__ if hasattr(response_schema, "__name__") else "dict"

                logger.info("[LiteLLM] Enabling Structured Output for schema: %s", schema_name)
                response_format = response_schema
            except Exception as schema_err:
                logger.error("[LiteLLM] Could not resolve schema name: %s", schema_err, exc_info=True)
                raise ConfigurationError(
                    message=f"Schema resolution failed: {schema_err}",
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                ) from schema_err

        # Epic 65: Resolve active location with strict priority logic
        config_location = self._config.vertex_location if self._config else None
        settings_location = self.settings.vertex_location if self.settings else None
        env_location = os.getenv("HARDENING_VERTEX_LOCATION")
        active_location = (
            kwargs.get("vertex_location") or config_location or settings_location or env_location or "europe-north1"
        )

        # Primarily region selected from UI/config
        os.environ["VERTEX_LOCATION"] = active_location
        os.environ["VERTEXAI_LOCATION"] = active_location

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

            logger.info("[LiteLLM] Calling %s in region %s...", self.model_name, active_location)

            # Prepare arguments
            call_kwargs = {
                "model": self.model_name,
                "messages": final_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
                "top_k": top_k,
                "response_format": response_format,
                "api_key": self.api_key,
                "drop_params": True,
                "vertex_location": active_location,
                "timeout": kwargs.get("timeout", self.settings.llm_default_timeout if self.settings else 600),
                "safety_settings": getattr(self.settings, "default_safety_settings", None) if self.settings else None,
            }
            call_kwargs.update(kwargs)

            if "cached_content" in kwargs:
                cache_id = kwargs["cached_content"]

                if call_kwargs.get("extra_headers") is None:
                    call_kwargs["extra_headers"] = {}
                call_kwargs["extra_headers"]["cached_content"] = cache_id

                if call_kwargs.get("extra_body") is None:
                    call_kwargs["extra_body"] = {}
                call_kwargs["extra_body"]["cachedContent"] = cache_id
                call_kwargs["extra_body"]["cached_content"] = cache_id

                call_kwargs["cached_content"] = cache_id

            if self._config and self._config.additional_params:
                resolved_additional = resolve_env_variables(self._config.additional_params)
                call_kwargs.update(resolved_additional)

            # --- DIAGNOSTIC DUMP ---
            dump_file = os.getenv("DUMP_PROMPTS_FILE")
            if dump_file:
                try:
                    payload = json.dumps(messages, indent=2, ensure_ascii=False)
                    await asyncio.to_thread(_sync_diagnostic_dump, dump_file, f"[LiteLLM] {self.model_name}", payload)
                except Exception as e:
                    logger.error("Failed to schedule diagnostic dump: %s", e, exc_info=True)
                    raise ConfigurationError(
                        message=f"Diagnostic dump dispatch failed: {e}",
                        details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                    ) from e

            # --- CALL LiteLLM ---
            call_kwargs["model"] = self.model_name

            max_rate_limit_retries = SystemConcurrency.LLM_MAX_RETRIES.value
            response = None
            fallback_occurred = False
            actual_model = self.model_name

            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(max_rate_limit_retries + 1),
                wait=wait_combine(
                    wait_exponential(
                        multiplier=SystemConcurrency.LLM_RETRY_MULTIPLIER.value,
                        min=SystemConcurrency.LLM_RETRY_MIN_SECONDS.value,
                        max=SystemConcurrency.LLM_RETRY_MAX_SECONDS.value,
                    ),
                    wait_random(1, 5),
                ),
                retry=retry_if_exception(_is_transient_llm_error),
                reraise=True,
                before_sleep=lambda rs: logger.warning(
                    "[LiteLLMProvider] Transient Error or Quota Exhausted (Attempt %s/%s). "
                    "Initiating dynamic exponential backoff... | Error: %s",
                    rs.attempt_number,
                    max_rate_limit_retries,
                    type(rs.outcome.exception()).__name__ if rs.outcome and rs.outcome.failed else "Unknown",
                ),
            ):
                with attempt:
                    _timeout = float(call_kwargs["timeout"])
                    semaphore = self.__class__._semaphores[self.cache_key]

                    if attempt.retry_state.attempt_number == (max_rate_limit_retries + 1):
                        if self.model_name != "vertex_ai/gemini-2.5-flash":
                            logger.warning(
                                "[Fail-Soft Fallback] Heavy model strategy '%s' exhausted on attempt %s. "
                                "Downgrading model to 'vertex_ai/gemini-2.5-flash' to guarantee execution safety.",
                                self.model_name,
                                attempt.retry_state.attempt_number,
                            )
                            call_kwargs["model"] = "vertex_ai/gemini-2.5-flash"
                            actual_model = "vertex_ai/gemini-2.5-flash"
                            fallback_occurred = True

                            if "messages" in call_kwargs:
                                clean_messages = []
                                for msg in call_kwargs["messages"]:
                                    clean_msg = copy.deepcopy(msg)
                                    content = clean_msg.get("content")
                                    if isinstance(content, list):
                                        new_content = []
                                        for part in content:
                                            if isinstance(part, dict):
                                                part_copy = copy.deepcopy(part)
                                                part_copy.pop("cache_control", None)
                                                new_content.append(part_copy)
                                            else:
                                                new_content.append(part)
                                        clean_msg["content"] = new_content
                                    clean_messages.append(clean_msg)
                                call_kwargs["messages"] = clean_messages

                    async with semaphore:
                        start_time = time.perf_counter()

                        # Phase 8: Apply Provider-Scoped Pacing Lock to prevent 429 exhaustion
                        from backend_v2.llm.adapters.base_adapter import apply_provider_pacing

                        provider_key = (
                            self._config.provider
                            if self._config
                            else (actual_model.split("/")[0] if "/" in actual_model else actual_model)
                        )
                        await apply_provider_pacing(provider_key)

                        if fallback_occurred:
                            response = await asyncio.wait_for(litellm.acompletion(**call_kwargs), timeout=_timeout)
                        else:
                            response = await asyncio.wait_for(self.router.acompletion(**call_kwargs), timeout=_timeout)

            if response is None:
                raise ServiceUnavailableError("Failed to get a response from the model provider.")

            latency_ms = int((time.perf_counter() - start_time) * 1000)

            choice = response.choices[0]
            message = choice.message
            raw_content = message.content or ""
            finish_reason = getattr(choice, "finish_reason", None)

            reasoning_token = None

            if hasattr(message, "provider_specific_fields") and message.provider_specific_fields:
                psf = message.provider_specific_fields
                if "thought_signature" in psf:
                    reasoning_token = psf["thought_signature"]
                elif "reasoning_blob" in psf:
                    reasoning_token = psf["reasoning_blob"]
                else:
                    reasoning_token = None

            if not reasoning_token and hasattr(response, "model_extra") and response.model_extra:
                me = response.model_extra
                reasoning_token = me.get("thought_signature")

            usage: dict[str, Any] = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "cached_tokens": 0,
                "reasoning_tokens": 0,
            }
            if hasattr(response, "usage") and response.usage:
                if getattr(response.usage, "prompt_tokens", None) is not None:
                    usage["prompt_tokens"] = response.usage.prompt_tokens
                if getattr(response.usage, "completion_tokens", None) is not None:
                    usage["completion_tokens"] = response.usage.completion_tokens
                if getattr(response.usage, "total_tokens", None) is not None:
                    usage["total_tokens"] = response.usage.total_tokens

                if getattr(response.usage, "prompt_tokens_details", None):
                    details = response.usage.prompt_tokens_details
                    if getattr(details, "cached_tokens", None) is not None:
                        usage["cached_tokens"] = details.cached_tokens

                if getattr(response.usage, "completion_tokens_details", None):
                    details = response.usage.completion_tokens_details
                    if getattr(details, "reasoning_tokens", None) is not None:
                        usage["reasoning_tokens"] = details.reasoning_tokens

            final_content = raw_content
            parsed_obj = None
            system_fingerprint = getattr(response, "system_fingerprint", None)
            if finish_reason in ["stop", "eos"]:
                finish_reason = None

            provider_meta = response.model_dump() if hasattr(response, "model_dump") else {}

            if hasattr(response, "_hidden_params") and isinstance(response._hidden_params, dict):
                hidden_params = response._hidden_params
                headers = hidden_params.get("headers", {})
                if isinstance(headers, dict):
                    ratelimit_key = "x-ratelimit-remaining-requests"
                    rem_reqs = headers.get(ratelimit_key)
                    if rem_reqs:
                        provider_meta["rate_limit_remaining"] = rem_reqs
                        if str(rem_reqs).isdigit() and int(rem_reqs) < 10:
                            logger.warning("[LiteLLMProvider] QUOTA WARNING: Only %s requests remaining.", rem_reqs)

            if hasattr(response, "model_extra") and isinstance(response.model_extra, dict):
                if "safety_ratings" in response.model_extra:
                    provider_meta["safety_ratings"] = response.model_extra["safety_ratings"]
                gm = response.model_extra.get("grounding_metadata", {})
                if isinstance(gm, dict) and "grounding_chunks" in gm:
                    urls = [
                        chunk["web"]["uri"]
                        for chunk in gm["grounding_chunks"]
                        if isinstance(chunk, dict) and "web" in chunk and "uri" in chunk["web"]
                    ]
                    if urls:
                        provider_meta["grounding_urls"] = urls
                        if not response_schema:
                            final_content += "\n\n**Sources (Google Search Grounding):**\n"
                            final_content += "\n".join([f"- [{url}]({url})" for url in urls])

            cost = 0.0
            try:
                base_model_name = actual_model.split("/")[-1] if "/" in actual_model else actual_model
                cost = litellm.completion_cost(completion_response=response, model=base_model_name)
            except Exception as e:
                logger.error("[LiteLLMProvider] Cost Calculation Failed: %s", e, exc_info=True)
                raise AgentExecutionError(
                    detail=ErrorCodes.UNKNOWN_ERROR.value, original_error=e, agent_name=self.model_name
                ) from e

            if self.usage_service:
                try:
                    target_org = kwargs.get("organization_id") or self.organization_id
                    target_user = kwargs.get("user_id") or "system_agent"

                    await self.usage_service.track_usage(
                        org_id=target_org,
                        user_id=target_user,
                        model=actual_model,
                        input_tokens=int(usage.get("prompt_tokens", 0)),
                        output_tokens=int(usage.get("completion_tokens", 0)),
                        cached_tokens=int(usage.get("cached_tokens", 0)),
                        reasoning_tokens=int(usage.get("reasoning_tokens", 0)),
                        latency_ms=latency_ms,
                        finish_reason=str(finish_reason) if finish_reason else None,
                        system_fingerprint=system_fingerprint,
                        cost_usd=cost,
                    )
                except Exception as e:
                    logger.error("[LiteLLMProvider] Usage Tracking Failed: %s", e, exc_info=True)
                    raise AppException(
                        message=f"Usage Tracking Failed: {e}",
                        status_code=500,
                        details={"error_code": ErrorCodes.UNKNOWN_ERROR.value},
                    ) from e

            usage["cost_usd"] = cost

            extracted_tool_calls: list[dict[str, Any]] = []
            if getattr(message, "tool_calls", None):
                for tc in message.tool_calls:
                    tc_dict = tc.model_dump() if hasattr(tc, "model_dump") else dict(tc)
                    extracted_tool_calls.append(tc_dict)

            return LLMResponse(
                content=final_content,
                parsed_content=parsed_obj if response_schema else None,
                reasoning_token=reasoning_token,
                token_usage=TokenUsage.model_validate(usage),
                provider_metadata=provider_meta,
                system_fingerprint=system_fingerprint,
                tool_calls=extracted_tool_calls if extracted_tool_calls else [],
                messages=final_messages,
                override_reason=(
                    "Downgraded to vertex_ai/gemini-2.5-flash due to rate limit or timeout on heavy model"
                    if fallback_occurred
                    else None
                ),
            )

        except Exception as e:
            if isinstance(e, AppException):
                raise e

            error_msg = str(e)
            error_type = type(e).__name__

            if (
                isinstance(e, getattr(litellm, "APIConnectionError", type(None)))
                or "NameResolutionError" in error_type
                or "ConnectTimeout" in error_type
                or "gaierror" in error_type
            ):
                raise e

            if (
                isinstance(e, getattr(litellm, "RateLimitError", type(None)))
                or (hasattr(e, "status_code") and e.status_code == 429)
                or "Resource exhausted" in error_msg
            ):
                logger.error(
                    "[LiteLLM] %s: RESOURCE EXHAUSTED (Retries depleted): %s",
                    ErrorCodes.RATE_LIMIT_EXCEEDED.name,
                    error_msg,
                )
                raise ServiceUnavailableError(
                    message="Model provider rate limit exceeded and all automatic retries failed.",
                    details={"error_code": ErrorCodes.RATE_LIMIT_EXCEEDED.value, "original_error": error_msg},
                ) from e

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

            elif (
                isinstance(e, getattr(litellm, "AuthenticationError", type(None)))
                or (hasattr(e, "status_code") and e.status_code == 401)
                or "invalid_api_key" in error_msg
            ):
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

            elif isinstance(e, getattr(litellm, "ContextWindowExceededError", type(None))) or (
                hasattr(e, "status_code")
                and e.status_code == 400
                and ("context" in error_msg.lower() or "token" in error_msg.lower())
            ):
                logger.error(
                    "[LiteLLM] %s: CONTEXT EXCEEDED (Prompt too long): %s",
                    ErrorCodes.AGENT_EXECUTION_CRITICAL.name,
                    error_msg,
                )
                raise AgentExecutionError(
                    detail=ErrorCodes.AGENT_EXECUTION_CRITICAL.value, original_error=e, agent_name=self.model_name
                ) from e
            elif hasattr(e, "status_code") and e.status_code == 400:
                logger.error("[LiteLLM] %s: BAD REQUEST (400): %s", ErrorCodes.AGENT_RESPONSE_MALFORMED.name, error_msg)
                raise AgentExecutionError(
                    detail=ErrorCodes.AGENT_RESPONSE_MALFORMED.value, original_error=e, agent_name=self.model_name
                ) from e

            elif (
                isinstance(e, getattr(litellm, "ServiceUnavailableError", type(None)))
                or isinstance(e, getattr(litellm, "Timeout", type(None)))
                or isinstance(e, asyncio.TimeoutError)
                or (hasattr(e, "status_code") and e.status_code in (500, 502, 503, 504))
            ):
                logger.error(
                    "[LiteLLM] %s: SERVICE UNAVAILABLE (Upstream/Timeout): %s",
                    ErrorCodes.UPSTREAM_TIMEOUT.name,
                    error_msg,
                )
                raise AppException(
                    message="Upstream LLM service timed out or is unavailable.",
                    status_code=503,
                    details={"error_code": ErrorCodes.UPSTREAM_TIMEOUT.value},
                ) from e

            elif "ContentPolicyViolation" in error_type or "blocked" in error_msg.lower():
                logger.warning(
                    "[LiteLLM] %s: SAFETY FILTER TRIGGERED: %s", ErrorCodes.SECURITY_VIOLATION.name, error_msg
                )
                raise SecurityViolationError(
                    message="Content blocked by safety filters.",
                    details={"error_code": ErrorCodes.SECURITY_VIOLATION.value, "original_error": error_msg},
                ) from e

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
        """Initialize the Mock Provider."""
        self.model_name = model_name
        self.usage_service = usage_service
        self.organization_id = organization_id or "UNKNOWN_ORG"

    async def generate(
        self,
        prompt: str | None = None,
        system_instruction: str | None = None,
        messages: list[dict[str, Any]] | None = None,
        response_schema: type[BaseModel] | dict[str, Any] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        pass_reasoning_token: str | None = None,
        validation_context: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Simulates generation by invoking the MockLLMService."""
        logger.info("[MockProvider] Calling Mock Service (Simulating Async)... %s", kwargs)

        if temperature is None:
            msg = "Strict Mode: 'temperature' must be explicitly provided from configuration. No default allowed."
            logger.error("[MockProvider] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
            raise ConfigurationError(message=msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})

        if max_tokens is None:
            msg = "Strict Mode: 'max_tokens' must be explicitly provided from configuration. No default allowed."
            logger.error("[MockProvider] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
            raise ConfigurationError(message=msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})

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
                logger.warning("Failed to schedule diagnostic dump: %s", e, exc_info=True)
                raise AppException(
                    message=str(e), status_code=500, details={"error_code": ErrorCodes.FILESYSTEM_VIOLATION.value}
                ) from e

        await asyncio.sleep(0.5)

        mock = MockLLMService()  # MockLLMService is an untyped legacy module

        agent_identity = kwargs.get("mock_identity")

        prompt_str = prompt or ""
        if messages and not prompt_str:
            prompt_str = json.dumps(messages)

        result = mock.generate_content(
            prompt_str,
            system_instruction,
            agent_identity=agent_identity,
            response_schema=response_schema,
        )

        content_str = ""
        parsed_result = None

        if isinstance(result, dict) and result.get("message") == "Mock data not found for key":
            raise ConfigurationError(
                message=(
                    f"Fail-Fast: Mock data not found in Seed Vault. "
                    f"Prompt missing mock definition: {prompt_str[:100]}..."
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
                content_str = str(result)
                try:
                    parsed_result = json.loads(content_str)
                except Exception as parse_err:
                    raise AppException(
                        message=f"Mock response parsing failed: {parse_err}",
                        status_code=500,
                        details={"error_code": ErrorCodes.AGENT_RESPONSE_PARSING_FAILED.value},
                    ) from parse_err

        usage_data = {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
            "total_cost": 0.002,
        }

        if self.usage_service:
            try:
                target_org = kwargs.get("organization_id") or self.organization_id
                target_user = kwargs.get("user_id") or "system_agent"

                await self.usage_service.track_usage(
                    org_id=target_org,
                    user_id=target_user,
                    model=self.model_name,
                    input_tokens=int(usage_data["prompt_tokens"]),
                    output_tokens=int(usage_data["completion_tokens"]),
                    cost_usd=float(usage_data["total_cost"]),
                )
            except Exception as e:
                logger.error("[MockProvider] Usage Tracking Failed: %s", e, exc_info=True)
                raise AppException(
                    message=f"Usage Tracking Failed: {e}",
                    status_code=500,
                    details={"error_code": ErrorCodes.UNKNOWN_ERROR.value},
                ) from e

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
            tool_calls=[],
            provider_metadata={},
            messages=[
                {"role": "system", "content": system_instruction} if system_instruction else {},
                {"role": "user", "content": prompt_str},
            ],
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
            provider_type (str): Type key (e.g. 'litellm', 'mock').
            model_name (str): Model identifier.
            context (Optional[dict]): Additional context or settings.
            organization_id (Optional[str]): Organization ID for tracking.
            usage_service (Optional[UsageService]): Usage service instance.
            limits (Optional[dict]): Usage limits (tpm, rpm).
            api_key (Optional[str]): Explicit API Key override (e.g. for ad-hoc testing).
            config (Optional[LLMProviderConfig]): Strict configuration object (Database-Driven).
            **kwargs: Additional arguments.

        Returns:
            LLMProvider: Configured provider instance.
        """
        settings = get_settings()

        if config:
            provider_type = config.provider
            model_name = config.model_name
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

            if not limits:
                limits = {}
            if config.tpm_limit > 0:
                limits["tpm"] = config.tpm_limit
            if config.rpm_limit > 0:
                limits["rpm"] = config.rpm_limit

            if config.api_key:
                api_key = config.api_key

            tools = kwargs.get("tools", [])
            enable_grounding = kwargs.get("enable_grounding", False)

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

        if settings and settings.use_mock_llm:
            logger.warning(
                "[LLMFactory] Global USE_MOCK_LLM=True. Overriding request for '%s' -> MockProvider.", provider_type
            )
            return MockProvider(
                model_name=model_name or "mock",
                usage_service=usage_service,
                organization_id=organization_id,
            )

        if provider_type == "mock":
            return MockProvider(
                model_name=model_name or "mock",
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

        if provider_type == "anthropic" and not model_name.startswith("anthropic/"):
            model_name = f"anthropic/{model_name}"

        resolved_api_key = api_key
        if not resolved_api_key and settings:
            if provider_type == "litellm":
                if "gemini" in model_name:
                    resolved_api_key = getattr(settings, "google_api_key", None)
                elif "gpt" in model_name or "o1" in model_name:
                    resolved_api_key = getattr(settings, "openai_api_key", None)
                elif "claude" in model_name or "anthropic" in model_name:
                    resolved_api_key = getattr(settings, "anthropic_api_key", None)

        if not resolved_api_key:
            match provider_type.lower():
                case "gemini" | "vertex_ai":
                    resolved_api_key = getattr(settings, "google_api_key", None) if settings else None
                case "openai":
                    resolved_api_key = getattr(settings, "openai_api_key", None) if settings else None
                    if not resolved_api_key:
                        resolved_api_key = os.getenv("OPENAI_API_KEY")
                case "anthropic":
                    resolved_api_key = getattr(settings, "anthropic_api_key", None) if settings else None
                    if not resolved_api_key:
                        resolved_api_key = os.getenv("ANTHROPIC_API_KEY")

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
