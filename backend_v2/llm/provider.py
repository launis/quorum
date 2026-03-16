"""LLM Provider implementations (LiteLLM, Mock, Unconfigured)."""

import asyncio
import json
import logging
import os
import time
from abc import ABC, abstractmethod
from typing import Any

import instructor
import litellm
from litellm import Router  # type: ignore
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from backend_v2.exceptions import (
    AgentExecutionError,
    AppException,
    ConfigurationError,
    ErrorCodes,
    SecurityViolationError,
    ServiceUnavailableError,
)
from backend_v2.models.llm import LLMProviderConfig, LLMResponse
from backend_v2.services.usage_service import UsageService
from backend_v2.settings import get_settings

# Configure logging
logger = logging.getLogger(__name__)

# Define retry strategy
_settings = get_settings()

retry_strategy = retry(
    stop=stop_after_attempt(_settings.llm_max_retries),
    wait=wait_exponential(multiplier=_settings.llm_retry_delay, min=1, max=60),
    reraise=True,
    before_sleep=lambda retry_state: logger.warning(
        f"Retrying LLM call... (Attempt {retry_state.attempt_number}/{_settings.llm_max_retries})"
    ),
)


class LLMProvider(ABC):
    """Abstract base class for LLM providers.

    Defines the contract for text generation and structured data extraction.
    """

    @abstractmethod
    async def generate(  # type: ignore
        self,
        prompt: str,
        system_instruction: str | None = None,
        response_schema: type[BaseModel] | dict[str, Any] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        pass_reasoning_token: str | None = None,
        **kwargs,
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
    _instructor_cache: dict[str, Any] = {}

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
            logger.error(f"[LiteLLMProvider] {msg}")
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR})

        tpm = limits.get("tpm")
        rpm = limits.get("rpm")

        if tpm is None or rpm is None:
            msg = "Strict Mode: Both TPM and RPM must be defined in limits config."
            logger.error(f"[LiteLLMProvider] {msg}")
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR})

        # 4. Determine Parsing Mode
        parse_mode = instructor.Mode.MD_JSON
        if self.settings and getattr(self.settings, "parsing_mode", None):
            mode_str = self.settings.parsing_mode.upper()
            if hasattr(instructor.Mode, mode_str):
                parse_mode = getattr(instructor.Mode, mode_str)
            else:
                logger.warning(
                    f"[LiteLLMProvider] Invalid parsing_mode '{mode_str}' in config, falling back to MD_JSON"
                )

        # Use Class Cache for Router and Instructor Client to avoid MAX_CALLBACKS leak
        cache_key = f"{model_name}_{tpm}_{rpm}_{parse_mode}"

        if cache_key in self.__class__._router_cache:
            self.router = self.__class__._router_cache[cache_key]
            self.client = self.__class__._instructor_cache[cache_key]
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
            self.router = Router(
                model_list=[model_config],
                set_verbose=False,
            )

            self.client = instructor.from_litellm(self.router.acompletion, mode=parse_mode)

            # Save to class cache
            self.__class__._router_cache[cache_key] = self.router
            self.__class__._instructor_cache[cache_key] = self.client

    @retry_strategy
    async def generate(  # type: ignore
        self,
        prompt: str,
        system_instruction: str | None = None,
        response_schema: type[BaseModel] | dict[str, Any] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        pass_reasoning_token: str | None = None,
        **kwargs,
    ) -> LLMResponse:
        """Generates content using LiteLLM.

        Returns unified LLMResponse with content and reasoning state.
        """
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})

        # STRICT CONFIGURATION (Jan 2026): Reject defaults.
        if temperature is None:
            msg = (
                "Strict Mode: 'temperature' must be explicitly provided "
                "from configuration (Database/Registry). No default allowed."
            )
            logger.error(f"[LiteLLMProvider] {msg}")
            raise ConfigurationError(msg)

        if max_tokens is None:
            msg = (
                "Strict Mode: 'max_tokens' must be explicitly provided "
                "from configuration (Database/Registry). No default allowed."
            )
            logger.error(f"[LiteLLMProvider] {msg}")
            raise ConfigurationError(msg)

        # Context Continuity (Stateless Reasoning Blob)
        if pass_reasoning_token:
            # Abstraction: We pass it as a developer hint for now.
            # Real implementation would use provider-specific params in `litellm.acompletion`
            messages.append(
                {
                    "role": "system",
                    "content": f"[SYSTEM: RESUME_THOUGHT_PROCESS] PREVIOUS_STATE_BLOB: {pass_reasoning_token}",
                }
            )

        messages.append({"role": "user", "content": prompt})

        response_format = None
        if response_schema:
            try:
                schema_name = "dict"
                if isinstance(response_schema, type):
                    schema_name = getattr(response_schema, "__name__", "dict")

                logger.info(f"[LiteLLM] Enabling Structured Output for schema: {schema_name}")
                response_format = response_schema
            except Exception as schema_err:
                logger.debug(f"[LiteLLM] Could not resolve schema name: {schema_err}")

        try:
            # --- LOGGING ---
            def _truncate_for_debug(text: str, label: str) -> None:
                if not text:
                    logger.info(f"[LiteLLM] [{label}]: <empty>")
                    return

                # Format for log
                # User Mandate (Jan 2026): Single-line compact debug log
                content_preview = text[:50].replace("\n", "\\n")
                suffix = text[-50:].replace("\n", "\\n") if len(text) > 50 else ""
                logger.info(f"[LiteLLM] [{label}]: Length={len(text)} chars | Content='{content_preview}...{suffix}'")

            if system_instruction:
                _truncate_for_debug(system_instruction, "SYSTEM INSTRUCTION")
            _truncate_for_debug(prompt, "USER PROMPT")

            logger.info(f"[LiteLLM] Calling {self.model_name}...")

            # Prepare arguments
            call_kwargs = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "response_format": response_format,
                "api_key": self.api_key,
                "drop_params": True,
                # STRICT NETWORK TIMEOUT: Fail fast (300s) instead of hanging forever.
                "timeout": 300,
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

            # Ensure env is loaded from project root
            from pathlib import Path

            from dotenv import load_dotenv

            # provider.py is at backend/llm/provider.py
            # Go up 3 levels to reach project root
            root_dir = Path(__file__).resolve().parent.parent.parent
            env_path = root_dir / ".env"

            load_dotenv(dotenv_path=env_path)

            v_loc = None
            if self.settings and hasattr(self.settings, "vertex_location"):
                v_loc = self.settings.vertex_location

            if not v_loc:
                v_loc = os.getenv("VERTEX_LOCATION")

            # STRICT MODE: No defaults. Fail if missing.
            if not v_loc:
                logger.error(f"[LiteLLMProvider] Env load failed. Tried path: {env_path}, Exists: {env_path.exists()}")
                raise ValueError(
                    f"[LiteLLMProvider] Critical Error: VERTEX_LOCATION not found in settings or .env ({env_path}). "
                    "Cannot proceed."
                )

            logger.info(f"[LiteLLMProvider] Using Vertex Location: {v_loc}")
            call_kwargs["vertex_location"] = v_loc

            # --- DYNAMIC GROUNDING (Google Search) ---
            # Driven by the settings (UI Model Registry config)
            if getattr(self, "supports_grounding", False):
                # Ensure it's a Vertex AI compatible model
                if self.model_name.startswith("vertex_ai/"):
                    logger.info(f"[LiteLLMProvider] Google Search Grounding ENABLED for {self.model_name}")

                    # Check if tools are already passed to kwargs
                    existing_tools = call_kwargs.get("tools", [])
                    # Append Google Search Tool schema required by Vertex AI
                    search_tool: dict[str, Any] = {"googleSearch": {}}

                    if search_tool not in existing_tools:
                        existing_tools.append(search_tool)
                        call_kwargs["tools"] = existing_tools

            # --- DIAGNOSTIC DUMP ---
            dump_file = os.getenv("DUMP_PROMPTS_FILE")
            if dump_file:
                try:
                    with open(dump_file, "a", encoding="utf-8") as f:
                        f.write(f"\n\n--- [LiteLLM] {self.model_name} ---\n")
                        f.write(json.dumps(messages, indent=2, ensure_ascii=False))
                except Exception as e:
                    logger.warning(f"Failed to dump prompt: {e}")

            start_time = time.perf_counter()

            # --- INSTRUCTOR CALL (Structured) ---
            if response_schema:
                # Use Instructor for Pydantic validation
                # we use 'create' because we wrapped self.router.acompletion in __init__
                # Note: instructor.from_litellm expects the *function* or client.
                # Since we wrapped it, we call client.chat.completions.create

                # Instructor might return the Model instance directly, or a tuple/Stream.
                # We expect the Model instance.

                # Adjust kwargs for Instructor
                call_kwargs["response_model"] = response_schema
                # Remove fields not needed or handled by Instructor/LiteLLM mixed
                call_kwargs.pop("response_format", None)

                # We need to map 'max_tokens' -> 'max_tokens' (standard)

                # EXECUTE
                # Note: usage/cost tracking with Instructor + Router + LiteLLM is tricky.
                # We might need to inspect the raw response if available, or rely on LiteLLM callbacks.
                # For now, let's assume Instructor returns the Pydantic object.
                # BUT we lose the 'reasoning_token' and 'usage' stats if we just get the object.
                # Instructor allows `checks` and returning `(model, completion)`?
                # Let's try to get the raw completion to extract usage/reasoning.
                # from instructor import Response

                # Actually, standard Instructor usage:
                # result = await self.client.chat.completions.create(...) # -> returns the Pydantic model.

                # To get usage, we might need to rely on LiteLLM's success callbacks or
                # use `response_model=[response_schema]` iterable trick (deprecated?)
                # OR use `instructor.patch()` on a client that returns raw response?

                # Let's stick to the simplest path first: Get the object.
                # We might lose Usage stats temporarily (or get them from callback logic in future).
                # For reasoning token, checks provider_specific_fields... strictly, Pydantic model
                # doesn't have it unless we add it to the model.

                # CRITICAL: We need 'reasoning_token' for chain-of-thought continuity.
                # If we lose it, we break CoT.

                # Strategy:
                # 1. We assume 'response_schema' is the content model.
                # 2. We can ask Instructor to return `(instance, raw_completion)` if configured?
                #    No, `with_response=True` (in newer versions).

                # Let's try basic implementation and see.
                # I will wrap the Pydantic result into our LLMResponse.

                logger.info(f"[Instructor] Calling {self.model_name} with schema {schema_name}")

                # HYBRID APPROACH (Feb 2026):
                # `create_with_completion` extracts Grounding Citations but crashes on Gemini-Flash with 100k+ tokens.
                # Standard `.create()` is rock solid for big context but swallows the raw headers.
                # We only use the fragile `create_with_completion` if Grounding is explicitly required.

                try:
                    if self.settings and getattr(self.settings, "supports_grounding", False):
                        logger.info("[Instructor] Grounding enabled. Using create_with_completion.")
                        structured_response, raw_completion = await self.client.chat.completions.create_with_completion(
                            **call_kwargs
                        )
                        parsed_obj = structured_response
                    else:
                        logger.info("[Instructor] Standard extraction. Using .create().")
                        parsed_obj = await self.client.chat.completions.create(**call_kwargs)
                        # For metrics, attempt to extract the underlying object if available
                        raw_completion = getattr(parsed_obj, "_raw_response", None)
                except Exception as e:
                    # Fail Fast: Catch Instructor empty choices or parsing failures cleanly
                    error_str = str(e)
                    if "ResponseParsingError" in type(e).__name__ or "No completion choices found" in error_str:
                        logger.error(f"[LiteLLMProvider] Instructor JSON Parsing Failure: {error_str}")

                        # Extract safety trigger context if possible
                        safety_hint = ""
                        if "safety_ratings" in error_str or "finish_reason: safety" in error_str.lower():
                            safety_hint = " Additionally, Vertex AI Safety Filters may have blocked the response."

                        raise AppException(
                            message=(
                                f"LLM returned an empty or malformed structured response. "
                                f"This is often caused by a prompt that is too large (Search Data) "
                                f"or a JSON format configuration error.{safety_hint}"
                            ),
                            status_code=500,
                            details={"error_code": ErrorCodes.AGENT_RESPONSE_PARSING_FAILED, "raw_error": error_str},
                        ) from e
                    raise e

                final_content = parsed_obj.model_dump_json()

                latency_ms = int((time.perf_counter() - start_time) * 1000)

                # Extract Usage from raw_completion if available
                usage: dict[str, Any] = {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "cached_tokens": 0,
                    "reasoning_tokens": 0,
                }
                if hasattr(raw_completion, "usage") and raw_completion.usage:
                    usage["prompt_tokens"] = getattr(raw_completion.usage, "prompt_tokens", 0) or 0
                    usage["completion_tokens"] = getattr(raw_completion.usage, "completion_tokens", 0) or 0
                    usage["total_tokens"] = getattr(raw_completion.usage, "total_tokens", 0) or 0

                    if (
                        hasattr(raw_completion.usage, "prompt_tokens_details")
                        and raw_completion.usage.prompt_tokens_details
                    ):
                        usage["cached_tokens"] = (
                            getattr(raw_completion.usage.prompt_tokens_details, "cached_tokens", 0) or 0
                        )

                    if (
                        hasattr(raw_completion.usage, "completion_tokens_details")
                        and raw_completion.usage.completion_tokens_details
                    ):
                        usage["reasoning_tokens"] = (
                            getattr(raw_completion.usage.completion_tokens_details, "reasoning_tokens", 0) or 0
                        )

                finish_reason = None
                if hasattr(raw_completion, "choices") and raw_completion.choices:
                    finish_reason = getattr(raw_completion.choices[0], "finish_reason", None)

                # Extract reasoning token if possible (from provider_specific_fields or model_extra)
                # Note: raw_completion is a generic Completion object (or ChatCompletion)
                reasoning_token = None

                # Try locating thought signature in extras
                if hasattr(raw_completion, "model_extra") and raw_completion.model_extra:
                    reasoning_token = raw_completion.model_extra.get("thought_signature")

                # If missing, check message provider specific fields (if accessible)
                # Usually located in choices[0].message
                if not reasoning_token and hasattr(raw_completion, "choices") and raw_completion.choices:
                    msg = raw_completion.choices[0].message
                    if hasattr(msg, "provider_specific_fields") and msg.provider_specific_fields:
                        reasoning_token = msg.provider_specific_fields.get("thought_signature")

                # --- ADVANCED TELEMETRY & METADATA ---
                system_fingerprint = getattr(raw_completion, "system_fingerprint", None)
                if finish_reason in ["stop", "eos"]:
                    finish_reason = None

                provider_meta = raw_completion.model_dump() if hasattr(raw_completion, "model_dump") else {}

                # Rate limits
                if hasattr(raw_completion, "_hidden_params") and isinstance(raw_completion._hidden_params, dict):
                    headers = raw_completion._hidden_params.get("headers", {})
                    if hasattr(headers, "get"):
                        rem_reqs = headers.get("x-ratelimit-remaining-requests")
                        if rem_reqs:
                            provider_meta["rate_limit_remaining"] = rem_reqs
                            if str(rem_reqs).isdigit() and int(rem_reqs) < 10:
                                logger.warning(f"[LiteLLMProvider] QUOTA WARNING: Only {rem_reqs} requests remaining.")

                # Vertex AI Safety & Grounding
                if hasattr(raw_completion, "model_extra") and isinstance(raw_completion.model_extra, dict):
                    if "safety_ratings" in raw_completion.model_extra:
                        provider_meta["safety_ratings"] = raw_completion.model_extra["safety_ratings"]
                    gm = raw_completion.model_extra.get("grounding_metadata", {})
                    if isinstance(gm, dict) and "grounding_chunks" in gm:
                        urls = [
                            chunk["web"]["uri"]
                            for chunk in gm["grounding_chunks"]
                            if isinstance(chunk, dict) and "web" in chunk and "uri" in chunk["web"]
                        ]
                        if urls:
                            provider_meta["grounding_urls"] = urls

                # --- COST TRACKING ---
                cost = 0.0
                if self.usage_service:
                    try:
                        # Calculate cost using LiteLLM raw_completion, explicitly passing
                        # model name without provider prefix
                        base_model_name = (
                            self.model_name.split("/")[-1] if "/" in self.model_name else self.model_name
                        )
                        cost = litellm.completion_cost(
                            completion_response=raw_completion, model=base_model_name
                        )

                        # Resolve IDs from kwargs (execution config) or provider instance
                        target_org = kwargs.get("organization_id") or self.organization_id
                        target_user = kwargs.get("user_id") or "system_agent"

                        await self.usage_service.track_usage(
                            org_id=target_org,
                            user_id=target_user,
                            model=self.model_name,
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
                        logger.warning(f"[LiteLLMProvider] Usage Tracking Failed: {e}")

                # Inject cost into usage dict so BaseAgent can pick it up
                usage["cost_usd"] = cost

                return LLMResponse(
                    content=final_content,
                    parsed_content=parsed_obj.model_dump(),
                    reasoning_token=reasoning_token,
                    token_usage=usage,
                    provider_metadata=provider_meta,
                    system_fingerprint=system_fingerprint,
                    tool_calls=[],
                    messages=messages,
                )

            # --- STANDARD CALL (Unstructured) ---
            # Fallback to self.router.acompletion directly if no schema
            # Remove keys that shouldn't be passed directly
            call_kwargs["model"] = self.model_name

            response = await self.router.acompletion(**call_kwargs)
            latency_ms = int((time.perf_counter() - start_time) * 1000)

            # Extract basic content
            choice = response.choices[0]
            message = choice.message
            raw_content = message.content or ""
            finish_reason = getattr(choice, "finish_reason", None)

            # Extract Reasoning Token (Gemini 3 / GPT-5.1)
            reasoning_token = None

            # Check standard LiteLLM extra fields
            if hasattr(message, "provider_specific_fields") and message.provider_specific_fields:
                reasoning_token = message.provider_specific_fields.get(
                    "thought_signature"
                ) or message.provider_specific_fields.get("reasoning_blob")

            # Fallback: Check top level attributes
            if not reasoning_token and hasattr(response, "model_extra"):
                reasoning_token = response.model_extra.get("thought_signature")

            # Extract Usage
            usage = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "cached_tokens": 0,
                "reasoning_tokens": 0,
            }
            if hasattr(response, "usage") and response.usage:
                usage["prompt_tokens"] = getattr(response.usage, "prompt_tokens", 0) or 0
                usage["completion_tokens"] = getattr(response.usage, "completion_tokens", 0) or 0
                usage["total_tokens"] = getattr(response.usage, "total_tokens", 0) or 0

                if hasattr(response.usage, "prompt_tokens_details") and response.usage.prompt_tokens_details:
                    usage["cached_tokens"] = getattr(response.usage.prompt_tokens_details, "cached_tokens", 0) or 0

                if hasattr(response.usage, "completion_tokens_details") and response.usage.completion_tokens_details:
                    usage["reasoning_tokens"] = (
                        getattr(response.usage.completion_tokens_details, "reasoning_tokens", 0) or 0
                    )

            # Handle Schema Parsing (Validation) - This block is now only for non-Instructor structured output
            # If schema was requested, we return the JSON string in 'content'
            # OR we populate 'tool_calls' if that mechanism was used.
            # For simplicity in this unified response, we ensure 'content' is the stringent result.

            final_content = raw_content
            parsed_obj = None  # Initialize parsed_obj for unstructured path
            # The original `if response_schema:` block for regex parsing is removed
            # as Instructor handles structured output.
            # If response_schema was passed, the `if response_schema:` block above would have handled it.
            # This means if we reach here, response_schema was None, and we just return raw_content.

            # --- ADVANCED TELEMETRY & METADATA ---
            system_fingerprint = getattr(response, "system_fingerprint", None)
            if finish_reason in ["stop", "eos"]:
                finish_reason = None

            provider_meta = response.model_dump() if hasattr(response, "model_dump") else {}

            # Rate limits
            if hasattr(response, "_hidden_params") and isinstance(response._hidden_params, dict):
                headers = response._hidden_params.get("headers", {})
                if hasattr(headers, "get"):
                    rem_reqs = headers.get("x-ratelimit-remaining-requests")
                    if rem_reqs:
                        provider_meta["rate_limit_remaining"] = rem_reqs
                        if str(rem_reqs).isdigit() and int(rem_reqs) < 10:
                            logger.warning(f"[LiteLLMProvider] QUOTA WARNING: Only {rem_reqs} requests remaining.")

            # Vertex AI Safety & Grounding Citations
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
                        # Inject Grounding Citations directly into the markdown response!
                        final_content += "\n\n**Lähteet (Google Search Grounding):**\n"
                        final_content += "\n".join([f"- [{url}]({url})" for url in urls])

            # --- COST TRACKING ---
            cost = 0.0
            if self.usage_service:
                try:
                    # Calculate cost using LiteLLM, explicitly passing model name without provider prefix
                    base_model_name = self.model_name.split("/")[-1] if "/" in self.model_name else self.model_name
                    cost = litellm.completion_cost(completion_response=response, model=base_model_name)

                    # Resolve IDs from kwargs (execution config) or provider instance
                    target_org = kwargs.get("organization_id") or self.organization_id
                    target_user = kwargs.get("user_id") or "system_agent"

                    # Track usage asynchronously (fire and forget for now, or await)
                    await self.usage_service.track_usage(
                        org_id=target_org,
                        user_id=target_user,
                        model=self.model_name,
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
                    logger.warning(f"[LiteLLMProvider] Usage Tracking Failed: {e}")

            # Inject cost into usage dict so BaseAgent can pick it up
            usage["cost_usd"] = cost

            from typing import cast

            return LLMResponse(
                content=final_content,
                parsed_content=parsed_obj if response_schema else None,
                reasoning_token=reasoning_token,
                token_usage=cast(dict[str, float | int], usage),
                provider_metadata=provider_meta,
                system_fingerprint=system_fingerprint,
                tool_calls=[],
                messages=messages,
            )

        except Exception as e:
            if isinstance(e, AppException) or hasattr(e, "status_code"):
                raise e

            # Jan 2026: Reduce Error Verbosity & Improve Classification
            error_msg = str(e)
            error_type = type(e).__name__

            # 0. DIRECT PASS-THROUGH (Network Errors for BaseAgent)
            if (
                "APIConnectionError" in error_type
                or "NameResolutionError" in error_type
                or "ConnectTimeout" in error_type
                or "gaierror" in error_type
            ):
                raise e

            # 1. RATE LIMITS & QUOTA (Critical Infra)
            if "RateLimitError" in error_type or "429" in error_msg or "Resource exhausted" in error_msg:
                logger.error(f"[LiteLLM] {ErrorCodes.RATE_LIMIT_EXCEEDED.name}: RESOURCE EXHAUSTED (Rate Limit): {error_msg}")
                raise ServiceUnavailableError(
                    message="Model provider rate limit exceeded.",
                    details={"error_code": ErrorCodes.RATE_LIMIT_EXCEEDED, "original_error": error_msg},
                ) from e

            # 1.1 OUTPUT LIMIT (Model Looping/Max Tokens/Empty Response)
            elif "InstructorRetryException" in error_type or "ResponseParsingError" in error_type:
                logger.error(f"[LiteLLM] {ErrorCodes.AGENT_RESPONSE_PARSING_FAILED.name}: INSTRUCTOR / MODEL FAILURE (Empty choices or schema mismatch): {error_msg}")
                raise AppException(
                    message="Model failed to generate structured output (empty response or looping).",
                    status_code=500,
                    details={"error_code": ErrorCodes.AGENT_RESPONSE_PARSING_FAILED, "original_error": error_msg},
                ) from e

            # 2. AUTHENTICATION ALERTS (Security/Config)
            elif "AuthenticationError" in error_type or "401" in error_msg or "invalid_api_key" in error_msg:
                logger.critical(f"[LiteLLM] {ErrorCodes.CONFIGURATION_ERROR.name}: AUTH FAILED (Check API Keys): {error_msg}")
                raise ConfigurationError(
                    message="LLM Provider authentication failed.",
                    details={
                        "error_code": ErrorCodes.CONFIGURATION_ERROR,
                        "original_error": "Invalid API Key or Credential",
                    },
                ) from e

            # 3. CONTEXT WINDOW (Data/Prompt Engineering)
            elif (
                "ContextWindowExceededError" in error_type
                or "context_length_exceeded" in error_msg
                or "400" in error_msg
            ):
                # Often 400 is generic, but combined with length/context keywords matches this.
                if "context" in error_msg.lower() or "token" in error_msg.lower():
                    logger.error(f"[LiteLLM] {ErrorCodes.AGENT_EXECUTION_CRITICAL.name}: CONTEXT EXCEEDED (Prompt too long): {error_msg}")
                    raise AgentExecutionError(
                        detail=ErrorCodes.AGENT_EXECUTION_CRITICAL, original_error=e, agent_name=self.model_name
                    ) from e
                else:
                    logger.error(f"[LiteLLM] {ErrorCodes.AGENT_RESPONSE_MALFORMED.name}: BAD REQUEST (400): {error_msg}")
                    raise AgentExecutionError(
                        detail=ErrorCodes.AGENT_RESPONSE_MALFORMED, original_error=e, agent_name=self.model_name
                    ) from e

            # 4. SERVICE INSTABILITY (Infra)
            elif (
                "ServiceUnavailableError" in error_type
                or "503" in error_msg
                or "500" in error_msg
                or "Timeout" in error_type
            ):
                logger.error(f"[LiteLLM] {ErrorCodes.UPSTREAM_TIMEOUT.name}: SERVICE UNAVAILABLE (Upstream/Timeout): {error_msg}")
                raise AppException(
                    message="Upstream LLM service timed out or is unavailable.",
                    status_code=503,
                    details={"error_code": ErrorCodes.UPSTREAM_TIMEOUT},
                ) from e

            # 5. CONTENT POLICY (Safety)
            elif "ContentPolicyViolation" in error_type or "blocked" in error_msg.lower():
                logger.warning(f"[LiteLLM] {ErrorCodes.SECURITY_VIOLATION.name}: SAFETY FILTER TRIGGERED: {error_msg}")
                raise SecurityViolationError(
                    message="Content blocked by safety filters.",
                    details={"error_code": ErrorCodes.SECURITY_VIOLATION, "original_error": error_msg},
                ) from e

            # 6. GENERIC FALLBACK (Fail Fast)
            else:
                if len(error_msg) > 500:
                    error_msg = error_msg[:500] + "... [TRUNCATED]"
                logger.error(f"[LiteLLM] {ErrorCodes.UNKNOWN_ERROR.name}: Execution Failed ({error_type}): {error_msg}", exc_info=True)

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

    async def generate(  # type: ignore
        self,
        prompt: str,
        system_instruction: str | None = None,
        response_schema: type[BaseModel] | dict[str, Any] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        pass_reasoning_token: str | None = None,
        **kwargs,
    ) -> LLMResponse:
        """Simulates generation by invoking the MockLLMService."""
        from backend_v2.llm.mock import MockLLMService

        logger.info(f"[MockProvider] Calling Mock Service (Simulating Async)... {kwargs}")

        # STRICT CONFIGURATION (Jan 2026): Reject defaults in Mock too.
        if temperature is None:
            msg = "Strict Mode: 'temperature' must be explicitly provided from configuration. No default allowed."
            logger.error(f"[MockProvider] {ErrorCodes.CONFIGURATION_ERROR.name}: {msg}")
            raise ConfigurationError(
                message=msg,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR}
            )

        if max_tokens is None:
            msg = "Strict Mode: 'max_tokens' must be explicitly provided from configuration. No default allowed."
            logger.error(f"[MockProvider] {ErrorCodes.CONFIGURATION_ERROR.name}: {msg}")
            raise ConfigurationError(
                message=msg,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR}
            )

        # --- DIAGNOSTIC DUMP ---
        dump_file = os.getenv("DUMP_PROMPTS_FILE")
        if dump_file:
            try:
                with open(dump_file, "a", encoding="utf-8") as f:
                    f.write(f"\n\n--- [MockProvider] {self.model_name} ---\n")
                    f.write(f"PROMPT:\n{prompt}\n")
                    if system_instruction:
                        f.write(f"SYSTEM:\n{system_instruction}\n")
            except Exception as e:
                logger.warning(f"Failed to dump prompt: {e}")

        # Simulate network delay for verification of async behavior
        await asyncio.sleep(0.5)

        mock = MockLLMService()  # type: ignore

        # Extract explicit identity if provided
        agent_identity = kwargs.get("mock_identity")

        result = mock.generate_content(
            prompt,
            system_instruction,
            agent_identity=agent_identity,
            response_schema=response_schema,
        )

        # Determine content string and parsed object
        content_str = ""
        parsed_result = None

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
            except Exception:
                # If it's not JSON, it's just text
                parsed_result = None

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
                target_org = kwargs.get("organization_id") or self.organization_id
                target_user = kwargs.get("user_id") or "system_agent"

                await self.usage_service.track_usage(
                    org_id=target_org,
                    user_id=target_user,
                    model=self.model_name,
                    input_tokens=int(usage_data["prompt_tokens"]),
                    output_tokens=int(usage_data["completion_tokens"]),
                    cost_usd=usage_data["total_cost"],
                )
            except Exception as e:
                logger.warning(f"[MockProvider] Usage Tracking Failed: {e}")

        return LLMResponse(
            content=content_str,
            parsed_content=parsed_result,
            reasoning_token="mock_thought_signature_123456",
            token_usage=usage_data,
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
    def create_provider(  # type: ignore
        provider_type: str,
        model_name: str,
        context: dict[str, Any] | Any | None = None,
        organization_id: str | None = None,
        usage_service: UsageService | None = None,
        limits: dict[str, int] | None = None,
        api_key: str | None = None,
        config: LLMProviderConfig | None = None,
        **kwargs,
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
                logger.error(f"[LLMFactory] {ErrorCodes.SERVICE_DISABLED.name}: Provider '{model_name}' is disabled in configuration.")
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
            tools = kwargs.get("tools", [])
            enable_grounding = kwargs.get("enable_grounding", False)

            # Check for Google Search tool or explicit flag
            has_search_intent = enable_grounding or (tools and any("google_search" in str(t) for t in tools))

            if has_search_intent:
                if not config.supports_grounding:
                    msg = (
                        f"Grounding/Search requested for '{model_name}' "
                        "but provider config 'supports_grounding' is False."
                    )
                    logger.error(f"[LLMFactory] {ErrorCodes.CAPABILITY_NOT_SUPPORTED.name}: {msg}")
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
                f"[LLMFactory] Global USE_MOCK_LLM=True. Overriding request for '{provider_type}' -> MockProvider."
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
            logger.error(f"[LLMFactory] {ErrorCodes.CONFIGURATION_ERROR.name}: Model name is required for LLMProvider creation.")
            raise ConfigurationError(
                message="Model name is required for LLMProvider creation.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR}
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
                        import os

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
