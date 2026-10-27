"""LiteLLM response parsing, telemetry recording, cost calculation, and RFC 7807 error stage."""

import asyncio
import logging
import sys
import time
import uuid
from typing import Any

import opentelemetry.trace as otel_trace
from pydantic import BaseModel

from backend_v2.exceptions import (
    AgentExecutionError,
    AppException,
    ConfigurationError,
    ErrorCodes,
    SecurityViolationError,
    ServiceUnavailableError,
)
from backend_v2.llm.caching_service import LLMCachingService
from backend_v2.llm.provider.env_and_schema_utils import _safe_static_getattr
from backend_v2.models.domain.mcp import OpenAIFunctionCallDTO, OpenAIToolCallDTO
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.llm import LLMMessageDTO, LLMResponse, ProviderMetadataDTO
from backend_v2.services.usage_service import UsageService

__all__ = ["_truncate_for_debug", "classify_and_raise_litellm_error", "extract_litellm_content_and_usage"]

logger = logging.getLogger(__name__)
_ORIG_OTEL_TRACE = otel_trace


def _resolve_otel_trace() -> Any:
    """Resolve opentelemetry.trace module honoring monkeypatches on provider facade.

    Returns:
        Active opentelemetry.trace module reference.
    """
    if otel_trace is not _ORIG_OTEL_TRACE:
        return otel_trace
    if "backend_v2.llm.provider" in sys.modules:
        provider_mod: Any = sys.modules["backend_v2.llm.provider"]
        if "otel_trace" in dir(provider_mod):
            return provider_mod.otel_trace
    return otel_trace


# Phase 3, Step 1: Hoist _truncate_for_debug from LiteLLMProvider.generate
def _truncate_for_debug(text: str, label: str) -> None:
    """Log redacted prompt/message character length without leaking raw content.

    Args:
        text: Prompt or serialized message string to measure.
        label: Log label identifying the payload segment.
    """
    if not text:
        logger.info("[LiteLLM] [%s]: <empty>", label)
        return
    logger.info("[LiteLLM] [%s]: Length=%d chars | Content=[REDACTED_FOR_SECURITY]", label, len(text))


# Phase 3, Step 1: Extract response parsing, TokenUsage, cost, and OpenTelemetry span stage
async def extract_litellm_content_and_usage(
    response: Any,
    model_name: str,
    start_time: float,
    final_messages: list[LLMMessageDTO | dict[str, Any]],
    response_schema: type[BaseModel] | dict[str, Any] | None = None,
    usage_service: UsageService | None = None,
    organization_id: str = "UNKNOWN_ORG",
    kwargs: dict[str, Any] | None = None,
) -> LLMResponse:
    """Extract content, tool calls, token usage, cost, and telemetry from a LiteLLM response.

    Args:
        response: Raw completion response object returned by LiteLLM Router.
        model_name: Configured model identifier.
        start_time: Monotonic perf_counter timestamp when the completion call started.
        final_messages: Sanitized message list dispatched to the provider.
        response_schema: Optional structured output Pydantic schema or JSON schema dict.
        usage_service: Optional usage tracking service.
        organization_id: Organization identifier for FinOps attribution.
        kwargs: Additional execution keyword arguments (organization_id, user_id).

    Returns:
        Constructed LLMResponse containing content, token_usage, tool_calls, and metadata.

    Raises:
        ServiceUnavailableError: If the response object is None.
        AgentExecutionError: If LiteLLM cost calculation fails.
        AppException: If usage tracking persistence fails.
    """
    import litellm

    if response is None:
        raise ServiceUnavailableError("Failed to get a response from the model provider.")

    call_extra: dict[str, Any] = {} if kwargs is None else kwargs
    actual_model = response.model if "model" in dir(response) else model_name
    clean_req = model_name.removeprefix("openai/").removeprefix("vertex_ai/").removeprefix("gemini/").lower()
    clean_act = str(actual_model).removeprefix("openai/").removeprefix("vertex_ai/").removeprefix("gemini/").lower()
    is_same_family = clean_req in clean_act or clean_act in clean_req
    if isinstance(actual_model, str) and actual_model and not is_same_family:
        logger.info(
            "[LiteLLMProvider] LLM Fallback utilized: Primary model '%s' failed, "
            "successfully routed to fallback model '%s'.",
            model_name,
            actual_model,
        )

    latency_ms = int((time.perf_counter() - start_time) * 1000)
    choice = response.choices[0]
    message = choice.message
    raw_content = "" if not message.content else message.content

    if not raw_content and "tool_calls" in dir(message) and message.tool_calls:
        tc = message.tool_calls[0]
        if "function" in dir(tc) and "arguments" in dir(tc.function):
            raw_content = "" if not tc.function.arguments else tc.function.arguments
        elif type(tc) is dict and "function" in tc and type(tc["function"]) is dict and "arguments" in tc["function"]:
            raw_content = "" if not tc["function"]["arguments"] else tc["function"]["arguments"]

    finish_reason = None if "finish_reason" not in dir(choice) else choice.finish_reason
    if not raw_content:
        dump_str = response.model_dump_json() if "model_dump_json" in dir(response) else str(response)
        logger.critical("[DIAGNOSTIC] LLM Output was completely empty! Raw response object dump: %s", dump_str)

    reasoning_token = None
    psf = _safe_static_getattr(message, "provider_specific_fields")
    if isinstance(psf, dict) and ("thought_signature" in psf or "reasoning_blob" in psf):
        reasoning_token = psf["thought_signature"] if "thought_signature" in psf else psf["reasoning_blob"]

    me = _safe_static_getattr(response, "model_extra")
    if not reasoning_token and isinstance(me, dict) and "thought_signature" in me:
        reasoning_token = me["thought_signature"]

    usage: dict[str, Any] = {}
    resp_usage = _safe_static_getattr(response, "usage")
    if resp_usage:
        for tok_key in ("prompt_tokens", "completion_tokens", "total_tokens"):
            if (tok_val := _safe_static_getattr(resp_usage, tok_key)) is not None:
                usage[tok_key] = tok_val
        if "total_tokens" not in usage and ("prompt_tokens" in usage or "completion_tokens" in usage):
            p_val = 0 if "prompt_tokens" not in usage else usage["prompt_tokens"]
            c_val = 0 if "completion_tokens" not in usage else usage["completion_tokens"]
            usage["total_tokens"] = p_val + c_val

        p_details = _safe_static_getattr(resp_usage, "prompt_tokens_details")
        if p_details and (cached_tok := _safe_static_getattr(p_details, "cached_tokens")) is not None:
            usage["cached_tokens"] = cached_tok

        c_details = _safe_static_getattr(resp_usage, "completion_tokens_details")
        if c_details and (reasoning_tok := _safe_static_getattr(c_details, "reasoning_tokens")) is not None:
            usage["reasoning_tokens"] = reasoning_tok

    final_content = raw_content
    parsed_obj = None
    cached_tokens_val = 0 if "cached_tokens" not in usage or usage["cached_tokens"] is None else usage["cached_tokens"]
    LLMCachingService.record_cache_hit(bool(cached_tokens_val and cached_tokens_val > 0))

    active_span = _resolve_otel_trace().get_current_span()
    if active_span.is_recording():
        if resp_model := _safe_static_getattr(response, "model"):
            active_span.set_attribute("gen_ai.response.model", str(resp_model))
        if "prompt_tokens" in usage and usage["prompt_tokens"] is not None:
            active_span.set_attribute("gen_ai.usage.input_tokens", int(usage["prompt_tokens"]))
        if "completion_tokens" in usage and usage["completion_tokens"] is not None:
            active_span.set_attribute("gen_ai.usage.output_tokens", int(usage["completion_tokens"]))

    system_fingerprint = _safe_static_getattr(response, "system_fingerprint")
    if finish_reason in ["stop", "eos"]:
        finish_reason = None

    dump_fn = _safe_static_getattr(response, "model_dump")
    provider_meta: dict[str, Any] = {} if not callable(dump_fn) else dump_fn()
    hidden_params = _safe_static_getattr(response, "_hidden_params")
    headers: Any = (
        {} if not (isinstance(hidden_params, dict) and "headers" in hidden_params) else hidden_params["headers"]
    )
    if isinstance(headers, dict) and "x-ratelimit-remaining-requests" in headers:
        if rem_reqs := headers["x-ratelimit-remaining-requests"]:
            provider_meta["rate_limit_remaining"] = rem_reqs
            if str(rem_reqs).isdigit() and int(rem_reqs) < 10:
                logger.warning("[LiteLLMProvider] QUOTA WARNING: Only %s requests remaining.", rem_reqs)

    model_extra = _safe_static_getattr(response, "model_extra")
    if isinstance(model_extra, dict):
        if "safety_ratings" in model_extra:
            provider_meta["safety_ratings"] = model_extra["safety_ratings"]
        gm = None if "grounding_metadata" not in model_extra else model_extra["grounding_metadata"]
        if isinstance(gm, dict) and "grounding_chunks" in gm:
            urls = [
                c["web"]["uri"]
                for c in gm["grounding_chunks"]
                if isinstance(c, dict) and "web" in c and "uri" in c["web"]
            ]
            if urls:
                provider_meta["grounding_urls"] = urls
                if not response_schema:
                    final_content += "\n\n**Lähteet (Google Search Grounding):**\n"
                    final_content += "\n".join([f"- [{url}]({url})" for url in urls])

    try:
        base_model_name = model_name.split("/")[-1] if "/" in model_name else model_name
        cost = litellm.completion_cost(completion_response=response, model=base_model_name)
    except Exception as e:
        logger.error("[LiteLLMProvider] Cost Calculation Failed: %s", e)
        raise AgentExecutionError(detail=ErrorCodes.UNKNOWN_ERROR, original_error=e, agent_name=model_name) from e

    if usage_service:
        try:
            target_org = (
                call_extra["organization_id"]
                if "organization_id" in call_extra and call_extra["organization_id"]
                else organization_id
            )
            target_user = (
                "system_agent" if not ("user_id" in call_extra and call_extra["user_id"]) else call_extra["user_id"]
            )
            await usage_service.track_usage(
                org_id=target_org,
                user_id=target_user,
                model=model_name,
                input_tokens=0 if "prompt_tokens" not in usage else int(usage["prompt_tokens"]),
                output_tokens=0 if "completion_tokens" not in usage else int(usage["completion_tokens"]),
                cached_tokens=0 if "cached_tokens" not in usage else int(usage["cached_tokens"]),
                reasoning_tokens=0 if "reasoning_tokens" not in usage else int(usage["reasoning_tokens"]),
                latency_ms=latency_ms,
                finish_reason=None if not finish_reason else str(finish_reason),
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

    usage["cost_usd"] = cost

    extracted_tool_calls: list[OpenAIToolCallDTO] = []
    raw_tool_calls = None if "tool_calls" not in dir(message) else message.tool_calls
    if raw_tool_calls:
        for tc in raw_tool_calls:
            if isinstance(tc, OpenAIToolCallDTO):
                extracted_tool_calls.append(tc)
            elif "model_dump" in dir(tc):
                extracted_tool_calls.append(OpenAIToolCallDTO.model_validate(tc.model_dump()))
            elif type(tc) is dict:
                extracted_tool_calls.append(OpenAIToolCallDTO.model_validate(tc))
            else:
                fn = None if "function" not in dir(tc) else tc.function
                fn_name = "unknown" if not (fn and "name" in dir(fn)) else fn.name
                fn_args = "{}" if not (fn and "arguments" in dir(fn)) else fn.arguments
                fn_dto = OpenAIFunctionCallDTO(name=fn_name, arguments=fn_args)
                tc_id = str(tc.id) if "id" in dir(tc) else f"call_{uuid.uuid4().hex[:8]}"
                extracted_tool_calls.append(OpenAIToolCallDTO(id=tc_id, function=fn_dto))

    meta_dto = ProviderMetadataDTO(
        finish_reason=None if not finish_reason else str(finish_reason),
        raw_extra=None if not provider_meta else provider_meta,
    )
    typed_messages: list[LLMMessageDTO] = [
        m if isinstance(m, LLMMessageDTO) else LLMMessageDTO.model_validate(m) for m in final_messages
    ]

    return LLMResponse(
        content=final_content,
        parsed_content=None if not response_schema else parsed_obj,
        reasoning_token=reasoning_token,
        token_usage=TokenUsage.model_validate(usage),
        provider_metadata=meta_dto,
        system_fingerprint=system_fingerprint,
        tool_calls=None if not extracted_tool_calls else extracted_tool_calls,
        messages=typed_messages,
        override_reason=None,
    )


# Phase 3, Step 1: Extract post-retry RFC 7807 exception classification stage
def classify_and_raise_litellm_error(e: Exception, model_name: str) -> Any:
    """Record exception on active OpenTelemetry span and raise mapped RFC 7807 AppException.

    Args:
        e: Exception raised during LiteLLM completion or post-processing.
        model_name: Configured model identifier for error attribution.

    Raises:
        AgentExecutionError: On context window overflow or HTTP 400 bad request.
        AppException: On Instructor/structured output parsing failure or pre-wrapped AppException.
        ConfigurationError: On HTTP 401/403 or invalid API key authentication failure.
        SecurityViolationError: On content policy or safety filter violation.
        ServiceUnavailableError: On rate limit exhaustion, upstream timeout, or unknown upstream error.
    """
    active_otel = _resolve_otel_trace()
    err_span = active_otel.get_current_span()
    if err_span.is_recording():
        err_span.record_exception(e)
        err_span.set_status(active_otel.StatusCode.ERROR, str(e))

    if isinstance(e, AppException):
        raise e

    import litellm.exceptions as litellm_exc

    error_msg = str(e)
    error_type = type(e).__name__
    status_code = _safe_static_getattr(e, "status_code")

    if isinstance(e, litellm_exc.APIConnectionError) or any(
        m in error_type for m in ("NameResolutionError", "ConnectTimeout", "gaierror")
    ):
        raise e

    if isinstance(e, litellm_exc.RateLimitError) or status_code == 429 or "Resource exhausted" in error_msg:
        rl_code = ErrorCodes.RATE_LIMIT_EXCEEDED
        logger.error("[LiteLLM] %s: RESOURCE EXHAUSTED (Retries depleted): %s", rl_code.name, error_msg)
        raise ServiceUnavailableError(
            message="Model provider rate limit exceeded and all automatic retries failed.",
            details={"error_code": rl_code.value, "original_error": error_msg},
        ) from e

    if "InstructorRetryException" in error_type or "ResponseParsingError" in error_type:
        parse_code = ErrorCodes.AGENT_RESPONSE_PARSING_FAILED
        logger.error("[LiteLLM] %s: INSTRUCTOR / MODEL FAILURE: %s", parse_code.name, error_msg)
        raise AppException(
            message="Model failed to generate structured output (empty response or looping).",
            status_code=500,
            details={"error_code": ErrorCodes.AGENT_RESPONSE_PARSING_FAILED.value, "original_error": error_msg},
        ) from e

    if isinstance(e, litellm_exc.AuthenticationError) or status_code in (401, 403) or "invalid_api_key" in error_msg:
        cfg_code = ErrorCodes.CONFIGURATION_ERROR
        logger.critical("[LiteLLM] %s: AUTH FAILED (Check API Keys): %s", cfg_code.name, error_msg)
        raise ConfigurationError(
            message="LLM Provider authentication failed.",
            details={"error_code": cfg_code.value, "original_error": "Invalid API Key or Credential"},
        ) from e

    if isinstance(e, litellm_exc.ContextWindowExceededError) or (
        status_code == 400 and ("context" in error_msg.lower() or "token" in error_msg.lower())
    ):
        err_code = ErrorCodes.AGENT_EXECUTION_CRITICAL
        logger.error("[LiteLLM] %s: CONTEXT EXCEEDED (Prompt too long): %s", err_code.name, error_msg)
        raise AgentExecutionError(detail=err_code, original_error=e, agent_name=model_name) from e

    if status_code == 400:
        err_code = ErrorCodes.AGENT_RESPONSE_MALFORMED
        logger.error("[LiteLLM] %s: BAD REQUEST (400): %s", err_code.name, error_msg)
        raise AgentExecutionError(detail=err_code, original_error=e, agent_name=model_name) from e

    if isinstance(e, (litellm_exc.ServiceUnavailableError, litellm_exc.Timeout, asyncio.TimeoutError)) or (
        isinstance(status_code, int) and status_code in (408, 500, 502, 503, 504)
    ):
        to_code = ErrorCodes.UPSTREAM_TIMEOUT
        logger.error("[LiteLLM] %s: SERVICE UNAVAILABLE (Upstream/Timeout): %s", to_code.name, error_msg)
        raise ServiceUnavailableError(
            message="Upstream LLM service timed out or is unavailable.",
            details={"error_code": to_code.value, "original_error": error_msg},
        ) from e

    if "ContentPolicyViolation" in error_type or "blocked" in error_msg.lower():
        logger.warning("[LiteLLM] %s: SAFETY FILTER TRIGGERED: %s", ErrorCodes.SECURITY_VIOLATION.name, error_msg)
        raise SecurityViolationError(
            message="Content blocked by safety filters.",
            details={"error_code": ErrorCodes.SECURITY_VIOLATION.value, "original_error": error_msg},
        ) from e

    if len(error_msg) > 500:
        error_msg = error_msg[:500] + "... [TRUNCATED]"
    unk_code = ErrorCodes.UNKNOWN_ERROR
    logger.error("[LiteLLM] %s: Execution Failed (%s): %s", unk_code.name, error_type, error_msg, exc_info=True)
    raise ServiceUnavailableError(
        message=f"Unknown upstream LLM error: {error_type}",
        details={"error_code": unk_code.value, "original_error": error_msg},
    ) from e
