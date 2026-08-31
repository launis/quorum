"""Google AI Studio (Direct Gemini API) cache adapter with distributed Redis locks and thundering herd protection.

Uses the official Google GenAI SDK (google.genai) caches.create API without requiring GCP Vertex AI infrastructure.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
from typing import Any

from arq.connections import RedisSettings, create_pool
from pydantic import BaseModel

from backend_v2.llm.adapters.base_adapter import BaseLLMAdapter
from backend_v2.models.domain.usage import PricingConfig, TokenUsage
from backend_v2.models.enums import PromptCacheStatus
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.models.v2_core import ChatMessageDTO, ModelProfile
from backend_v2.settings import get_settings
from backend_v2.utils.redis_patcher import get_patched_fakeredis_pool

logger = logging.getLogger(__name__)

_AI_STUDIO_SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
]

_redis_pool: Any = None
_redis_loop: Any = None


async def get_redis_client() -> Any:
    """Return a shared Redis connection pool or in-memory FakeRedis during tests.

    Returns:
        The active Redis connection pool instance.
    """
    global _redis_pool, _redis_loop

    current_loop = asyncio.get_running_loop()
    if _redis_pool is None or _redis_loop != current_loop:
        if "PYTEST_CURRENT_TEST" in os.environ or os.environ.get("USE_FAKEREDIS") == "true":
            _redis_pool = get_patched_fakeredis_pool()
            _redis_loop = current_loop
            return _redis_pool

        settings = get_settings()
        _redis_pool = await create_pool(
            RedisSettings(
                host=settings.redis_host,
                port=settings.redis_port,
                conn_timeout=int(get_settings().redis_connection_timeout_seconds),
            )
        )
        _redis_loop = current_loop
    return _redis_pool


class GoogleAIStudioCacheAdapter(BaseLLMAdapter):
    """Caching and pricing adapter for Google AI Studio (Direct Gemini API) models."""

    async def prepare_caching_payload(
        self, compiled_prompt: CompiledPrompt, model_name: str
    ) -> tuple[list[LLMMessageDTO] | list[dict[str, Any]], dict[str, Any]]:
        """Prepare the Google AI Studio specific prompt payload by setting up cached content.

        Args:
            compiled_prompt: The structured prompt payload.
            model_name: The target model name.

        Returns:
            A pair containing:
                - The list of flattened messages.
                - A dictionary of extra keyword arguments containing the cache reference name.
        """
        # Google AI Studio minimum token limit for context caching (typically 32,768 tokens for Gemini 1.5/2.0/3.7)
        static_content_token_count, has_non_system_static = self.estimate_static_tokens(
            compiled_prompt, exclude_system=True
        )

        min_threshold = get_settings().context_cache_min_tokens_ai_studio

        if (
            get_settings().disable_vertex_cache
            or not has_non_system_static
            or static_content_token_count < min_threshold
        ):
            logger.info(
                "Google AI Studio caching bypassed: Static conversational contents (%d tokens) below "
                "minimum threshold (%d tokens) or lacking non-system turns.",
                static_content_token_count,
                min_threshold,
            )
            return compiled_prompt.to_flat_messages(), {}

        clean_model_name = model_name.split("/")[-1]
        static_hash = hashlib.sha256(
            json.dumps(
                [m.model_dump(mode="json", exclude_none=True) for m in compiled_prompt.static_messages],
                sort_keys=True,
            ).encode()
        ).hexdigest()
        redis_key = f"ai_studio_cache:{clean_model_name}:{static_hash}"
        lock_key = f"lock:ai_studio_cache:{clean_model_name}:{static_hash}"

        redis_client = await get_redis_client()

        cache_id = await redis_client.get(redis_key)
        if cache_id:
            if isinstance(cache_id, bytes):
                cache_id = cache_id.decode("utf-8")

            if cache_id == PromptCacheStatus.FAILED.value:
                logger.warning(
                    "Google AI Studio cached content previously marked as FAILED. Falling back to standard completion."
                )
                return compiled_prompt.to_flat_messages(), {}

            if cache_id != PromptCacheStatus.CREATING.value:
                logger.info("Google AI Studio Cache Hit in shared ledger: %s", cache_id)
                return compiled_prompt.to_dynamic_flat(), {
                    "cached_content": cache_id,
                }

        lock_ttl_ms = int(get_settings().context_cache_lock_ttl_seconds * 1000)
        lock_acquired = await redis_client.set(lock_key, "worker_1", nx=True, px=lock_ttl_ms)

        if lock_acquired:
            try:
                cache_id = await redis_client.get(redis_key)
                if cache_id:
                    if isinstance(cache_id, bytes):
                        cache_id = cache_id.decode("utf-8")
                    if cache_id == PromptCacheStatus.FAILED.value:
                        return compiled_prompt.to_flat_messages(), {}
                    if cache_id != PromptCacheStatus.CREATING.value:
                        return compiled_prompt.to_dynamic_flat(), {
                            "cached_content": cache_id,
                        }

                await redis_client.set(
                    redis_key,
                    PromptCacheStatus.CREATING.value,
                    ex=get_settings().context_cache_lock_ttl_seconds,
                )

                api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
                static_flat = compiled_prompt.to_static_flat()

                try:
                    # Lazy loading SDK inside method
                    from google import genai
                    from google.genai import types

                    client = genai.Client(api_key=api_key)

                    logger.info(
                        "Creating Google AI Studio Context Cache for model: %s",
                        clean_model_name,
                    )

                    ai_studio_contents = []
                    system_text = ""
                    for raw_msg in static_flat:
                        msg = raw_msg if isinstance(raw_msg, ChatMessageDTO) else ChatMessageDTO.model_validate(raw_msg)
                        role = msg.role
                        content = msg.content

                        if role == "system":
                            system_text += content + "\n"
                            continue

                        if role == "assistant":
                            role = "model"

                        ai_studio_contents.append({"role": role, "parts": [{"text": content}]})

                    ttl_seconds = int(get_settings().context_cache_passive_ttl_seconds)
                    config = types.CreateCachedContentConfig(
                        contents=ai_studio_contents,
                        ttl=f"{ttl_seconds}s",
                    )
                    if system_text.strip():
                        config.system_instruction = system_text.strip()

                    cache = client.caches.create(
                        model=clean_model_name,
                        config=config,
                    )
                    cache_name = str(cache.name)

                    await redis_client.set(
                        redis_key,
                        cache_name,
                        ex=ttl_seconds,
                    )
                    logger.info(
                        "Google AI Studio Context Cache successfully created: %s",
                        cache_name,
                    )
                    return compiled_prompt.to_dynamic_flat(), {
                        "cached_content": cache_name,
                    }

                except Exception as exc:  # noqa: QGR003 [REASON: Fail-Soft graceful degradation to uncached completion on cloud SDK failure]
                    logger.warning(
                        "Fail-Soft: Google AI Studio Context Cache creation bypassed/failed (%s). "
                        "Continuing with uncached completion.",
                        str(exc),
                    )
                    await redis_client.set(
                        redis_key,
                        PromptCacheStatus.FAILED.value,
                        ex=get_settings().context_cache_failed_ttl_seconds,
                    )
                    return compiled_prompt.to_flat_messages(), {}

            finally:
                await redis_client.delete(lock_key)

        else:
            poll_interval_s = float(get_settings().context_cache_lock_poll_interval_ms / 1000.0)
            max_wait_s = float(get_settings().context_cache_lock_wait_limit_seconds)
            elapsed_s = 0.0

            while elapsed_s < max_wait_s:
                await asyncio.sleep(poll_interval_s)
                elapsed_s += poll_interval_s

                cache_id = await redis_client.get(redis_key)
                if cache_id:
                    if isinstance(cache_id, bytes):
                        cache_id = cache_id.decode("utf-8")

                    if cache_id == PromptCacheStatus.FAILED.value:
                        logger.warning("Wait-and-Poll: Active creation failed on first worker. Falling back instantly.")
                        return compiled_prompt.to_flat_messages(), {}

                    if cache_id != PromptCacheStatus.CREATING.value:
                        logger.info(
                            "Wait-and-Poll: Cache creation completed by first worker: %s",
                            cache_id,
                        )
                        return compiled_prompt.to_dynamic_flat(), {
                            "cached_content": cache_id,
                        }

            logger.warning(
                "Wait-and-Poll timeout reached after %s seconds. Falling back to uncached completion.",
                max_wait_s,
            )
            return compiled_prompt.to_flat_messages(), {}

    async def teardown_cache(self, workflow_run_id: str) -> None:
        """No-Op teardown for Google AI Studio (Pure Passive TTL Caching).

        Args:
            workflow_run_id: The tracking context identifier.
        """
        pass

    def calculate_cost(self, usage: TokenUsage, pricing_config: PricingConfig) -> TokenUsage:
        """Calculate the precise Google AI Studio cost and savings.

        Gemini Context Caching in AI Studio provides 75% read discount on cached input tokens.

        Args:
            usage: The source token usage data.
            pricing_config: Provider pricing parameters.

        Returns:
            The calculated usage metrics including savings.
        """
        p_in = pricing_config.input_token_price
        p_out = pricing_config.output_token_price

        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        cached_tokens = usage.cached_tokens

        regular_input = max(0, prompt_tokens - cached_tokens)

        cost_regular = regular_input * p_in
        cost_cached = cached_tokens * p_in * 0.25
        cost_output = completion_tokens * p_out

        total_cost = cost_regular + cost_cached + cost_output
        total_savings = cached_tokens * p_in * 0.75

        return TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=usage.total_tokens,
            cached_tokens=cached_tokens,
            reasoning_tokens=usage.reasoning_tokens,
            cost_usd=total_cost,
            estimated_savings_usd=total_savings,
        )

    def prepare_provider_kwargs(self, model_name: str) -> dict[str, Any]:
        """Prepare Google AI Studio specific arguments for LiteLLM.

        Args:
            model_name: The target model name.

        Returns:
            Dictionary containing safety settings.
        """
        return {"safety_settings": _AI_STUDIO_SAFETY_SETTINGS}

    def prepare_structured_output(self, response_model: type[BaseModel]) -> dict[str, Any] | type[BaseModel]:
        """Convert a Pydantic model into a Google AI Studio structured output schema format.

        Args:
            response_model: The Pydantic model defining the expected JSON structure.

        Returns:
            A dictionary matching LiteLLM's structured output format with stripped constraints.
        """
        json_schema = response_model.model_json_schema()
        self._strip_unsupported_constraints(json_schema)

        return {
            "type": "json_schema",
            "json_schema": {
                "name": response_model.__name__,
                "schema": json_schema,
                "strict": True,
            },
        }

    def prepare_kwargs(
        self, call_kwargs: dict[str, Any], config: Any | None = None, settings: Any | None = None
    ) -> dict[str, Any]:
        """Prepare AI Studio specific kwargs, handling caching mappings and parameters.

        Args:
            call_kwargs: The dictionary of arguments to pass to litellm.
            config: Optional config object for the provider.
            settings: Optional app settings.

        Returns:
            The potentially modified call_kwargs dictionary.
        """
        model_name = str(
            call_kwargs.get("model") or (config.model_name if isinstance(config, ModelProfile) else "")
        ).lower()
        is_gemini_3 = "gemini-3" in model_name or "gemini-3." in model_name

        thinking_budget: int | None = None
        if isinstance(config, ModelProfile):
            if config.thinking_budget_tokens is not None:
                thinking_budget = int(config.thinking_budget_tokens)
            elif config.additional_params and "thinking_budget_tokens" in config.additional_params:
                thinking_budget = int(config.additional_params["thinking_budget_tokens"])

        if thinking_budget is not None:
            if "extra_body" not in call_kwargs or call_kwargs["extra_body"] is None:
                call_kwargs["extra_body"] = {}
            if "generationConfig" not in call_kwargs["extra_body"]:
                call_kwargs["extra_body"]["generationConfig"] = {}
            if "thinkingConfig" not in call_kwargs["extra_body"]["generationConfig"]:
                call_kwargs["extra_body"]["generationConfig"]["thinkingConfig"] = {}
            call_kwargs["extra_body"]["generationConfig"]["thinkingConfig"]["thinkingBudget"] = thinking_budget

        if is_gemini_3:
            # Enforce temperature = 1.0 to prevent infinite thought loops / degradation
            passed_temp = call_kwargs.get("temperature")
            if passed_temp is not None and passed_temp < 1.0:
                logger.warning(
                    "[GoogleAIStudioCacheAdapter] Modern reasoning model (%s) requested temperature %s < 1.0. "
                    "Enforcing temperature=1.0 per Google recommendation.",
                    model_name,
                    passed_temp,
                )
                call_kwargs["temperature"] = 1.0

            # Strip unsupported/deprecated sampling parameters for reasoning models
            for deprecated_key in ("top_k", "frequency_penalty", "presence_penalty"):
                call_kwargs.pop(deprecated_key, None)

        if "cached_content" in call_kwargs:
            cache_id = call_kwargs["cached_content"]
            if "extra_body" not in call_kwargs or call_kwargs["extra_body"] is None:
                call_kwargs["extra_body"] = {}
            call_kwargs["extra_body"]["cachedContent"] = cache_id
            call_kwargs["extra_body"]["cached_content"] = cache_id

            if "messages" in call_kwargs:
                system_msgs = [m for m in call_kwargs["messages"] if m.get("role") == "system"]
                if system_msgs:
                    logger.critical(
                        "ARCHITECTURE VIOLATION: %d system message(s) detected in cached payload. "
                        "Scrubbing defensively to prevent Google 400. "
                        "This indicates a CompiledPrompt construction defect.",
                        len(system_msgs),
                    )
                    call_kwargs["messages"] = [m for m in call_kwargs["messages"] if m.get("role") != "system"]

        return call_kwargs
