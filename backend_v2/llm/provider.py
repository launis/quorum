"""LLM Provider implementations (LiteLLM, Mock, Unconfigured)."""

import asyncio
import json
import logging
import os
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import litellm
from dotenv import load_dotenv
from litellm import Router  # type: ignore[attr-defined] # LiteLLM ei eksplisiittisesti exporttaa Routeria
from pydantic import BaseModel
from tenacity import AsyncRetrying, retry_if_exception, stop_after_attempt, wait_combine, wait_fixed, wait_random

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

_settings = get_settings()

# Ensure env is loaded from project root for LLM secrets
_root_dir = Path(__file__).resolve().parent.parent.parent
_env_path = _root_dir / ".env"
load_dotenv(dotenv_path=_env_path)


def _sync_diagnostic_dump(dump_file: str, model_name: str, payload_str: str) -> None:
    """Synchronous file writing for diagnostic dumps to prevent blocking the async event loop."""
    try:
        with open(dump_file, "a", encoding="utf-8") as f:
            f.write(f"\n\n--- {model_name} ---\n")
            f.write(payload_str)
            f.write("\n")
    except Exception as e:
        logger.error("Failed to dump prompt: %s", e)


def _is_transient_llm_error(e: BaseException) -> bool:
    """Check if the LiteLLM/asyncio exception is a transient rate limit or timeout."""
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
        response_schema (type[BaseModel] | dict[str, Any] | None): Pydantic model or JSON Schema.
        temperature (float): Sampling temperature.
        max_tokens (int | None): Max tokens to generate.
        pass_reasoning_token (str | None): Encrypted state blob from previous turn.
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

    def __init__(
        self,
        model_name: str,
        api_key: str | None = None,
        settings: Any = None,
        usage_service: UsageService | None = None,
        organization_id: str | None = None,
        limits: dict[str, int] | None = None,
        supports_grounding: bool = False,
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
        """
        self.model_name = model_name
        self.api_key = api_key
        self.settings = settings
        self.usage_service = usage_service
        self.organization_id = organization_id or "UNKNOWN_ORG"
        self.supports_grounding = supports_grounding

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
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR})

        tpm = limits["tpm"] if "tpm" in limits else None
        rpm = limits["rpm"] if "rpm" in limits else None

        if tpm is None or rpm is None:
            msg = "Strict Mode: Both TPM and RPM must be defined in limits config."
            logger.error("[LiteLLMProvider] %s", msg)
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR})

        # Use Class Cache for Router to avoid MAX_CALLBACKS leak
        cache_key = f"{model_name}_{tpm}_{rpm}"

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
            # set_verbose=False to reduce noise, unless debugging
            # CRITICAL: Disable internal Router retries (num_retries=0) to allow Fail-Fast Tenacity handling
            self.router = Router(
                model_list=[model_config],
                set_verbose=False,
                num_retries=0,
            )

            # Save to class cache
            self.__class__._router_cache[cache_key] = self.router

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
                    schema_name = response_schema.__name__ if hasattr(response_schema, "__name__") else "dict"

                logger.info("[LiteLLM] Enabling Structured Output for schema: %s", schema_name)
                response_format = response_schema
            except Exception as schema_err:
                logger.error("[LiteLLM] Could not resolve schema name: %s", schema_err)
                raise ConfigurationError(
                    message=f"Schema resolution failed: {schema_err}",
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                ) from schema_err

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
                # STRICT NETWORK TIMEOUT: Fail fast instead of hanging forever.
                "timeout": kwargs["timeout"] if "timeout" in kwargs else self.settings.llm_default_timeout,
                # SAFETY FILTERS (Auditing Requirement):
                # We must be able to process "unsafe" content (e.g. Hate Speech in logs) without blocking.
                # Therefore, we disable safety filters for the Analyzer.
                "safety_settings": self.settings.default_safety_settings,
            }
            # Inject dynamic extra params (top_p, top_k, etc.) provided via kwargs
            # Filter out internal keys if necessary, but litellm.drop_params=True handles most.
            call_kwargs.update(kwargs)

            # Explicitly force Vertex Location (Fixes 403 default-to-us-central1 issue)
            # Robustly resolve location (Settings attr or Env Var)
            v_loc = None
            if self.settings and hasattr(self.settings, "vertex_location"):
                v_loc = self.settings.vertex_location

            if not v_loc:
                v_loc = os.getenv("VERTEX_LOCATION")

            # STRICT MODE: No defaults. Fail if missing.
            if not v_loc:
                logger.error(
                    "[LiteLLMProvider] Critical Error: VERTEX_LOCATION not found in settings or environment variables."
                )
                raise ValueError(
                    "[LiteLLMProvider] Critical Error: VERTEX_LOCATION not found in settings or environment. "
                    "Cannot proceed."
                )

            logger.info("[LiteLLMProvider] Using Vertex Location: %s", v_loc)
            call_kwargs["vertex_location"] = v_loc

            # --- DIAGNOSTIC DUMP ---
            dump_file = os.getenv("DUMP_PROMPTS_FILE")
            if dump_file:
                try:
                    payload = json.dumps(messages, indent=2, ensure_ascii=False)
                    await asyncio.to_thread(_sync_diagnostic_dump, dump_file, f"[LiteLLM] {self.model_name}", payload)
                except Exception as e:
                    logger.error("Failed to schedule diagnostic dump: %s", e)
                    raise ConfigurationError(
                        message=f"Diagnostic dump dispatch failed: {e}",
                        details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                    ) from e

            start_time = time.perf_counter()

            # --- CALL LiteLLM (Unstructured or Structured Native) ---
            # Remove keys that shouldn't be passed directly
            call_kwargs["model"] = self.model_name

            max_rate_limit_retries = SystemConcurrency.LLM_MAX_RETRIES.value
            response = None

            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(max_rate_limit_retries),
                wait=wait_combine(
                    wait_fixed(SystemConcurrency.RATE_LIMIT_COOLDOWN_SECONDS.value),
                    wait_random(1, 15),
                ),
                retry=retry_if_exception(_is_transient_llm_error),
                reraise=True,
                before_sleep=lambda rs: logger.warning(
                    "[LiteLLMProvider] Transient Error or Quota Exhausted (Attempt %s/%s). "
                    "Initiating cooldown before automatic retry... | Error: %s",
                    rs.attempt_number,
                    max_rate_limit_retries,
                    type(rs.outcome.exception()).__name__ if rs.outcome and rs.outcome.failed else "Unknown",
                ),
            ):
                with attempt:
                    _timeout = call_kwargs["timeout"]
                    response = await asyncio.wait_for(self.router.acompletion(**call_kwargs), timeout=float(_timeout))

            if response is None:
                raise ServiceUnavailableError("Failed to get a response from the model provider.")

            latency_ms = int((time.perf_counter() - start_time) * 1000)

            # Extract basic content
            choice = response.choices[0]
            message = choice.message
            raw_content = message.content or ""
            finish_reason = choice.finish_reason if hasattr(choice, "finish_reason") else None

            # Extract Reasoning Token (Gemini 3 / GPT-5.1)
            reasoning_token = None

            # Check standard LiteLLM extra fields
            if hasattr(message, "provider_specific_fields") and message.provider_specific_fields:
                psf = message.provider_specific_fields
                if "thought_signature" in psf:
                    reasoning_token = psf["thought_signature"]
                elif "reasoning_blob" in psf:
                    reasoning_token = psf["reasoning_blob"]
                else:
                    reasoning_token = None

            # Fallback: Check top level attributes
            if not reasoning_token and hasattr(response, "model_extra"):
                me = response.model_extra
                reasoning_token = me["thought_signature"] if "thought_signature" in me else None

            usage: dict[str, Any] = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "cached_tokens": 0,
                "reasoning_tokens": 0,
            }
            if hasattr(response, "usage") and response.usage:
                if hasattr(response.usage, "prompt_tokens") and response.usage.prompt_tokens is not None:
                    usage["prompt_tokens"] = response.usage.prompt_tokens
                if hasattr(response.usage, "completion_tokens") and response.usage.completion_tokens is not None:
                    usage["completion_tokens"] = response.usage.completion_tokens
                if hasattr(response.usage, "total_tokens") and response.usage.total_tokens is not None:
                    usage["total_tokens"] = response.usage.total_tokens

                if hasattr(response.usage, "prompt_tokens_details") and response.usage.prompt_tokens_details:
                    details = response.usage.prompt_tokens_details
                    if hasattr(details, "cached_tokens") and details.cached_tokens is not None:
                        usage["cached_tokens"] = details.cached_tokens

                if hasattr(response.usage, "completion_tokens_details") and response.usage.completion_tokens_details:
                    details = response.usage.completion_tokens_details
                    if hasattr(details, "reasoning_tokens") and details.reasoning_tokens is not None:
                        usage["reasoning_tokens"] = details.reasoning_tokens

            final_content = raw_content
            parsed_obj = None  # --- ADVANCED TELEMETRY & METADATA ---
            system_fingerprint = response.system_fingerprint if hasattr(response, "system_fingerprint") else None
            if finish_reason in ["stop", "eos"]:
                finish_reason = None

            provider_meta = response.model_dump() if hasattr(response, "model_dump") else {}

            # Rate limits
            if hasattr(response, "_hidden_params") and isinstance(response._hidden_params, dict):
                headers = response._hidden_params["headers"] if "headers" in response._hidden_params else {}
                if isinstance(headers, dict):
                    ratelimit_key = "x-ratelimit-remaining-requests"
                    rem_reqs = headers[ratelimit_key] if ratelimit_key in headers else None
                    if rem_reqs:
                        provider_meta["rate_limit_remaining"] = rem_reqs
                        if str(rem_reqs).isdigit() and int(rem_reqs) < 10:
                            logger.warning("[LiteLLMProvider] QUOTA WARNING: Only %s requests remaining.", rem_reqs)

            # Vertex AI Safety & Grounding Citations
            if hasattr(response, "model_extra") and isinstance(response.model_extra, dict):
                if "safety_ratings" in response.model_extra:
                    provider_meta["safety_ratings"] = response.model_extra["safety_ratings"]
                gm = response.model_extra["grounding_metadata"] if "grounding_metadata" in response.model_extra else {}
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
                # Calculate cost using LiteLLM, explicitly passing model name without provider prefix
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
                    t_org = kwargs["organization_id"] if "organization_id" in kwargs else None
                    target_org = t_org or self.organization_id
                    t_usr = kwargs["user_id"] if "user_id" in kwargs else None
                    target_user = t_usr or "system_agent"

                    # Track usage asynchronously (fire and forget for now, or await)
                    await self.usage_service.track_usage(
                        org_id=target_org,
                        user_id=target_user,
                        model=self.model_name,
                        input_tokens=int(usage["prompt_tokens"] if "prompt_tokens" in usage else 0),
                        output_tokens=int(usage["completion_tokens"] if "completion_tokens" in usage else 0),
                        cached_tokens=int(usage["cached_tokens"] if "cached_tokens" in usage else 0),
                        reasoning_tokens=int(usage["reasoning_tokens"] if "reasoning_tokens" in usage else 0),
                        latency_ms=latency_ms,
                        finish_reason=str(finish_reason) if finish_reason else None,
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
            extracted_tool_calls: list[dict[str, Any]] = []
            if hasattr(message, "tool_calls") and message.tool_calls:
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
            )

        except Exception as e:
            if isinstance(e, AppException):
                raise e

            # Jan 2026: Reduce Error Verbosity & Improve Classification
            error_msg = str(e)
            error_type = type(e).__name__

            # 0. DIRECT PASS-THROUGH (Network Errors for BaseAgent)
            if (
                isinstance(e, getattr(litellm, "APIConnectionError", type(None)))
                or "NameResolutionError" in error_type
                or "ConnectTimeout" in error_type
                or "gaierror" in error_type
            ):
                raise e

            # 1. RATE LIMITS & QUOTA (Critical Infra)
            # 429s are natively handled in the inner retry loop! If they bubble here, retries were exhausted.
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
                    details={"error_code": ErrorCodes.RATE_LIMIT_EXCEEDED, "original_error": error_msg},
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
                    details={"error_code": ErrorCodes.AGENT_RESPONSE_PARSING_FAILED, "original_error": error_msg},
                ) from e

            # 2. AUTHENTICATION ALERTS (Security/Config)
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
                        "error_code": ErrorCodes.CONFIGURATION_ERROR,
                        "original_error": "Invalid API Key or Credential",
                    },
                ) from e

            # 3. CONTEXT WINDOW (Data/Prompt Engineering)
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
                    detail=ErrorCodes.AGENT_EXECUTION_CRITICAL, original_error=e, agent_name=self.model_name
                ) from e
            elif hasattr(e, "status_code") and e.status_code == 400:
                logger.error("[LiteLLM] %s: BAD REQUEST (400): %s", ErrorCodes.AGENT_RESPONSE_MALFORMED.name, error_msg)
                raise AgentExecutionError(
                    detail=ErrorCodes.AGENT_RESPONSE_MALFORMED, original_error=e, agent_name=self.model_name
                ) from e

            # 4. SERVICE INSTABILITY (Infra)
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
                    details={"error_code": ErrorCodes.UPSTREAM_TIMEOUT},
                ) from e

            # 5. CONTENT POLICY (Safety)
            elif "ContentPolicyViolation" in error_type or "blocked" in error_msg.lower():
                logger.warning(
                    "[LiteLLM] %s: SAFETY FILTER TRIGGERED: %s", ErrorCodes.SECURITY_VIOLATION.name, error_msg
                )
                raise SecurityViolationError(
                    message="Content blocked by safety filters.",
                    details={"error_code": ErrorCodes.SECURITY_VIOLATION, "original_error": error_msg},
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
                    details={"error_code": ErrorCodes.UNKNOWN_ERROR, "original_error": error_msg},
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

        # STRICT CONFIGURATION (Jan 2026): Reject defaults in Mock too.
        if temperature is None:
            msg = "Strict Mode: 'temperature' must be explicitly provided from configuration. No default allowed."
            logger.error("[MockProvider] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
            raise ConfigurationError(message=msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR})

        if max_tokens is None:
            msg = "Strict Mode: 'max_tokens' must be explicitly provided from configuration. No default allowed."
            logger.error("[MockProvider] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
            raise ConfigurationError(message=msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR})

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
                logger.warning("Failed to schedule diagnostic dump: %s", e)

        # Simulate network delay for verification of async behavior
        await asyncio.sleep(0.5)

        mock = MockLLMService()  # MockLLMService on untyped legacy moduuli

        # Extract explicit identity if provided
        agent_identity = kwargs["mock_identity"] if "mock_identity" in kwargs else None

        prompt_str = prompt or ""
        if messages and not prompt_str:
            # Fallback to serializing messages if prompt is empty
            prompt_str = json.dumps(messages)

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
                details={"error_code": "CONFIGURATION_ERROR"},
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
                target_org = kwargs["organization_id"] if "organization_id" in kwargs else None or self.organization_id
                target_user = kwargs["user_id"] if "user_id" in kwargs else None or "system_agent"

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
                {"role": "user", "content": prompt},
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
                    details={"error_code": ErrorCodes.SERVICE_DISABLED},
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
            tools = kwargs["tools"] if "tools" in kwargs else []
            enable_grounding = kwargs["enable_grounding"] if "enable_grounding" in kwargs else False

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
                        details={"error_code": ErrorCodes.CAPABILITY_NOT_SUPPORTED},
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
        if settings.use_mock_llm:
            logger.warning(
                "[LLMFactory] Global USE_MOCK_LLM=True. Overriding request for '%s' -> MockProvider.", provider_type
            )
            return MockProvider(
                model_name=model_name or "mock",
                usage_service=usage_service,
                organization_id=organization_id,
            )

        # STRICT CONFIGURATION:
        # If not in global mock mode, we DO NOT allow 'mock' to be implicitly selected
        # unless explicitly requested. If 'vertex_ai' is requested, we get Vertex (or fail).
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
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
            )

        resolved_api_key = api_key
        if not resolved_api_key:
            if provider_type == "litellm":
                if "gemini" in model_name:
                    resolved_api_key = settings.google_api_key
                elif "gpt" in model_name or "o1" in model_name:
                    resolved_api_key = settings.openai_api_key
                elif "claude" in model_name:
                    resolved_api_key = settings.anthropic_api_key

        # Determine fallback if still empty and logic required
        if not resolved_api_key:
            match provider_type.lower():
                case "gemini" | "vertex_ai":
                    resolved_api_key = settings.google_api_key
                case "openai":
                    resolved_api_key = settings.openai_api_key
                    if not resolved_api_key:
                        resolved_api_key = os.getenv("OPENAI_API_KEY")

        return LiteLLMProvider(
            model_name=model_name,
            api_key=resolved_api_key,
            settings=settings,
            usage_service=usage_service,
            organization_id=organization_id,
            limits=limits,
            supports_grounding=config.supports_grounding if config else False,
        )
