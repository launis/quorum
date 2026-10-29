"""Google AI Studio (Direct Gemini API) cache adapter with distributed Redis locks and thundering herd protection.

Uses the official Google GenAI SDK (google.genai) caches.create API without requiring GCP Vertex AI infrastructure.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import re
from typing import TYPE_CHECKING, Any, Final, override

from arq.connections import ArqRedis, RedisSettings, create_pool
from pydantic import BaseModel

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.adapters.base_adapter import BaseLLMAdapter
from backend_v2.models.domain.system_config import ModelProfile
from backend_v2.models.domain.usage import PricingConfig, TokenUsage
from backend_v2.models.enums import PromptCacheStatus
from backend_v2.models.llm import CachingPayloadResultDTO, LLMMessageDTO, LLMProviderConfig
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.settings import Settings, get_settings
from backend_v2.utils.redis_patcher import get_patched_fakeredis_pool

if TYPE_CHECKING:
    from fakeredis.aioredis import FakeRedis

logger = logging.getLogger(__name__)

__all__ = [
    "GoogleAIStudioCacheAdapter",
    "get_redis_client",
    "is_gemini_v3_or_higher",
]

_AI_STUDIO_CACHE_READ_RATE: Final[float] = 0.25
_AI_STUDIO_CACHE_SAVINGS_RATE: Final[float] = 0.75

_AI_STUDIO_SAFETY_SETTINGS: Final[list[dict[str, str]]] = [
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
]

_redis_pool: ArqRedis | FakeRedis | None = None
_redis_loop: asyncio.AbstractEventLoop | None = None


def _is_system_turn(m: LLMMessageDTO | dict[str, Any]) -> bool:
    """Check whether a message represents a system turn without using dict.get().

    Args:
        m: The message DTO or message dictionary.

    Returns:
        True if the message is a system role, False otherwise.
    """
    if isinstance(m, LLMMessageDTO):
        return m.role == "system"
    if not isinstance(m, (str, int, float, bool, list)) and m is not None and "role" in m:
        return str(m["role"]) == "system"
    return False


async def get_redis_client() -> ArqRedis | FakeRedis:
    """Return a shared Redis connection pool or in-memory FakeRedis during tests.

    Returns:
        The active Redis connection pool instance.

    Raises:
        AppException: STORAGE_ACCESS_FAILED if Redis connection pool initialization fails.
    """
    global _redis_pool, _redis_loop

    try:
        current_loop = asyncio.get_running_loop()
        if _redis_pool is None or _redis_loop != current_loop:
            if "PYTEST_CURRENT_TEST" in os.environ or os.getenv("USE_FAKEREDIS") == "true":
                _redis_pool = get_patched_fakeredis_pool()
                _redis_loop = current_loop
                return _redis_pool

            settings = get_settings()
            _redis_pool = await create_pool(
                RedisSettings(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    conn_timeout=int(settings.redis_connection_timeout_seconds),
                )
            )
            _redis_loop = current_loop
        return _redis_pool
    except (TimeoutError, ConnectionError, OSError, RuntimeError) as exc:
        logger.error(
            "[GoogleAIStudioCacheAdapter] %s: Failed to initialize Redis pool for AI Studio cache.",
            ErrorCodes.STORAGE_ACCESS_FAILED.name,
            extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "error_details": str(exc)},
            exc_info=True,
        )
        raise AppException(
            message=f"Redis initialization failed: {str(exc)}",
            status_code=500,
            details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
        ) from exc


def is_gemini_v3_or_higher(model_name: str) -> bool:
    """Evaluate whether the given model name refers to a Gemini major version 3 or greater.

    Args:
        model_name: The identifier or path of the model.

    Returns:
        True if the model is Gemini 3+, False otherwise.
    """
    match = re.search(r"gemini-(\d+)(?:\.(\d+))?", model_name.lower())
    if match:
        major = int(match.group(1))
        return major >= 3
    return False


class GoogleAIStudioCacheAdapter(BaseLLMAdapter):
    """Caching and pricing adapter for Google AI Studio (Direct Gemini API) models."""

    @staticmethod
    def _decode_redis_cache_id(raw_cache_id: bytes | str | None) -> str | None:
        """Normalize a raw Redis cache identifier into a UTF-8 string.

        Args:
            raw_cache_id: Raw bytes or string value returned from Redis.

        Returns:
            Decoded string identifier or None if empty.
        """
        if not raw_cache_id:
            return None
        if isinstance(raw_cache_id, bytes):
            return raw_cache_id.decode("utf-8")
        return str(raw_cache_id)

    @staticmethod
    def _resolve_existing_cache_entry(
        cache_id: str | None,
        compiled_prompt: CompiledPrompt,
        log_events: bool = True,
    ) -> CachingPayloadResultDTO | None:
        """Evaluate an existing Redis ledger cache entry and return a result if terminal.

        Args:
            cache_id: Decoded cache entry string from Redis, if any.
            compiled_prompt: The structured prompt payload.
            log_events: Whether to emit informational/warning log messages on hit/failure.

        Returns:
            CachingPayloadResultDTO if the entry represents a terminal hit or failure, else None.
        """
        if not cache_id:
            return None
        if cache_id == PromptCacheStatus.FAILED.value:
            if log_events:
                logger.warning(
                    "Google AI Studio cached content previously marked as FAILED. Falling back to standard completion."
                )
            return CachingPayloadResultDTO(messages=compiled_prompt.to_flat_messages(), kwargs={})
        if cache_id != PromptCacheStatus.CREATING.value:
            if log_events:
                logger.info("Google AI Studio Cache Hit in shared ledger: %s", cache_id)
            return CachingPayloadResultDTO(
                messages=compiled_prompt.to_dynamic_flat(),
                kwargs={"cached_content": cache_id},
            )
        return None

    @staticmethod
    def _build_ai_studio_cache_config(
        static_flat: list[LLMMessageDTO],
        ttl_seconds: int,
        types_module: Any,
    ) -> Any:
        """Build the Google GenAI CreateCachedContentConfig from static prompt messages.

        Args:
            static_flat: List of static LLMMessageDTO turns to cache.
            ttl_seconds: Cache time-to-live in seconds.
            types_module: Imported google.genai.types module.

        Returns:
            Constructed CreateCachedContentConfig instance.
        """
        ai_studio_contents: list[dict[str, Any]] = []
        system_text = ""
        for raw_msg in static_flat:
            msg = raw_msg if isinstance(raw_msg, LLMMessageDTO) else LLMMessageDTO.model_validate(raw_msg)
            role = msg.role
            content = msg.content

            if role == "system":
                if isinstance(content, str):
                    system_text += content + "\n"
                else:
                    system_text += json.dumps(content) + "\n"
                continue

            if role == "assistant":
                role = "model"

            if isinstance(content, str):
                ai_studio_contents.append({"role": role, "parts": [{"text": content}]})
            else:
                ai_studio_contents.append({"role": role, "parts": list(content)})

        config = types_module.CreateCachedContentConfig(
            contents=ai_studio_contents,
            ttl=f"{ttl_seconds}s",
        )
        if system_text.strip():
            config.system_instruction = system_text.strip()
        return config

    async def _create_cache_under_lock(
        self,
        redis_client: ArqRedis | FakeRedis,
        compiled_prompt: CompiledPrompt,
        clean_model_name: str,
        redis_key: str,
        lock_key: str,
    ) -> CachingPayloadResultDTO:
        """Execute Google AI Studio context cache creation while holding the distributed Redis lock.

        Args:
            redis_client: Active Redis client instance.
            compiled_prompt: The structured prompt payload.
            clean_model_name: Normalized model identifier without provider prefix.
            redis_key: Redis key storing the cache resource name or status.
            lock_key: Distributed Redis lock key protecting creation.

        Returns:
            A CachingPayloadResultDTO containing dynamic or flat messages and cache kwargs.
        """
        try:
            raw_cached = await redis_client.get(redis_key)
            existing = self._resolve_existing_cache_entry(
                self._decode_redis_cache_id(raw_cached),
                compiled_prompt,
                log_events=False,
            )
            if existing is not None:
                return existing

            settings = get_settings()
            await redis_client.set(
                redis_key,
                PromptCacheStatus.CREATING.value,
                ex=settings.context_cache_lock_ttl_seconds,
            )

            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                api_key = os.getenv("GOOGLE_API_KEY")
            static_flat = compiled_prompt.to_static_flat()

            try:
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=api_key)
                logger.info("Creating Google AI Studio Context Cache for model: %s", clean_model_name)

                ttl_seconds = int(settings.context_cache_passive_ttl_seconds)
                config = self._build_ai_studio_cache_config(static_flat, ttl_seconds, types)
                cache = client.caches.create(model=clean_model_name, config=config)
                cache_name = str(cache.name)

                await redis_client.set(redis_key, cache_name, ex=ttl_seconds)
                logger.info("Google AI Studio Context Cache successfully created: %s", cache_name)
                return CachingPayloadResultDTO(
                    messages=compiled_prompt.to_dynamic_flat(),
                    kwargs={"cached_content": cache_name},
                )
            except Exception as exc:
                if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                    raise
                logger.warning(
                    "Fail-Soft: Google AI Studio Context Cache creation bypassed/failed (%s). "
                    "Continuing with uncached completion.",
                    str(exc),
                )
                await redis_client.set(
                    redis_key,
                    PromptCacheStatus.FAILED.value,
                    ex=settings.context_cache_failed_ttl_seconds,
                )
                return CachingPayloadResultDTO(messages=compiled_prompt.to_flat_messages(), kwargs={})
        finally:
            await redis_client.delete(lock_key)

    async def _poll_for_active_cache_creation(
        self,
        redis_client: ArqRedis | FakeRedis,
        compiled_prompt: CompiledPrompt,
        redis_key: str,
    ) -> CachingPayloadResultDTO:
        """Poll Redis while another worker is actively creating the Google AI Studio context cache.

        Args:
            redis_client: Active Redis client instance.
            compiled_prompt: The structured prompt payload.
            redis_key: Redis key storing the cache resource name or status.

        Returns:
            A CachingPayloadResultDTO with either the newly created cache reference or flat fallback messages.
        """
        settings = get_settings()
        poll_interval_s = float(settings.context_cache_lock_poll_interval_ms / 1000.0)
        max_wait_s = float(settings.context_cache_lock_wait_limit_seconds)
        elapsed_s = 0.0

        while elapsed_s < max_wait_s:
            await asyncio.sleep(poll_interval_s)
            elapsed_s += poll_interval_s

            cache_id = self._decode_redis_cache_id(await redis_client.get(redis_key))
            if cache_id:
                if cache_id == PromptCacheStatus.FAILED.value:
                    logger.warning("Wait-and-Poll: Active creation failed on first worker. Falling back instantly.")
                    return CachingPayloadResultDTO(messages=compiled_prompt.to_flat_messages(), kwargs={})

                if cache_id != PromptCacheStatus.CREATING.value:
                    logger.info("Wait-and-Poll: Cache creation completed by first worker: %s", cache_id)
                    return CachingPayloadResultDTO(
                        messages=compiled_prompt.to_dynamic_flat(),
                        kwargs={"cached_content": cache_id},
                    )

        logger.warning(
            "Wait-and-Poll timeout reached after %s seconds. Falling back to uncached completion.",
            max_wait_s,
        )
        return CachingPayloadResultDTO(messages=compiled_prompt.to_flat_messages(), kwargs={})

    @override
    async def prepare_caching_payload(
        self, compiled_prompt: CompiledPrompt, model_name: str
    ) -> CachingPayloadResultDTO:
        """Prepare the Google AI Studio specific prompt payload by setting up cached content.

        Args:
            compiled_prompt: The structured prompt payload.
            model_name: The target model name.

        Returns:
            A CachingPayloadResultDTO containing messages and extra kwargs.

        Raises:
            AppException: VALIDATION_FAILED if model_name is empty or whitespace, or
                STORAGE_ACCESS_FAILED if Redis connection pool initialization fails.
        """
        if not model_name or not model_name.strip():
            logger.error(
                "[GoogleAIStudioCacheAdapter] %s: Target model_name cannot be empty.",
                ErrorCodes.VALIDATION_FAILED.name,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message="Target model_name cannot be empty for Google AI Studio cache payload preparation.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        static_content_token_count, has_non_system_static = self.estimate_static_tokens(
            compiled_prompt, exclude_system=True
        )
        settings = get_settings()
        min_threshold = settings.context_cache_min_tokens_ai_studio

        if settings.disable_vertex_cache or not has_non_system_static or static_content_token_count < min_threshold:
            logger.info(
                "Google AI Studio caching bypassed: Static conversational contents (%d tokens) below "
                "minimum threshold (%d tokens) or lacking non-system turns.",
                static_content_token_count,
                min_threshold,
            )
            return CachingPayloadResultDTO(messages=compiled_prompt.to_flat_messages(), kwargs={})

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
        existing = self._resolve_existing_cache_entry(
            self._decode_redis_cache_id(await redis_client.get(redis_key)),
            compiled_prompt,
            log_events=True,
        )
        if existing is not None:
            return existing

        lock_ttl_ms = int(settings.context_cache_lock_ttl_seconds * 1000)
        lock_acquired = await redis_client.set(lock_key, "worker_1", nx=True, px=lock_ttl_ms)
        if lock_acquired:
            return await self._create_cache_under_lock(
                redis_client=redis_client,
                compiled_prompt=compiled_prompt,
                clean_model_name=clean_model_name,
                redis_key=redis_key,
                lock_key=lock_key,
            )
        return await self._poll_for_active_cache_creation(
            redis_client=redis_client,
            compiled_prompt=compiled_prompt,
            redis_key=redis_key,
        )

    @override
    async def teardown_cache(self, workflow_run_id: str) -> None:
        """Validate workflow_run_id and execute passive TTL teardown for Google AI Studio.

        Args:
            workflow_run_id: The tracking context identifier.

        Raises:
            AppException: VALIDATION_FAILED if workflow_run_id is empty or whitespace.
        """
        if not workflow_run_id or not workflow_run_id.strip():
            logger.error(
                "[GoogleAIStudioCacheAdapter] %s: workflow_run_id cannot be empty during cache teardown.",
                ErrorCodes.VALIDATION_FAILED.name,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message="workflow_run_id cannot be empty for Google AI Studio cache teardown.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

    @override
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
        p_cached = (
            pricing_config.cached_input_token_price
            if pricing_config.cached_input_token_price is not None
            else p_in * _AI_STUDIO_CACHE_READ_RATE
        )

        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        cached_tokens = usage.cached_tokens

        regular_input = max(0, prompt_tokens - cached_tokens)

        cost_regular = regular_input * p_in
        cost_cached = cached_tokens * p_cached
        cost_output = completion_tokens * p_out

        total_cost = cost_regular + cost_cached + cost_output
        total_savings = (
            cached_tokens * max(0.0, p_in - p_cached)
            if pricing_config.cached_input_token_price is not None
            else cached_tokens * p_in * _AI_STUDIO_CACHE_SAVINGS_RATE
        )

        return TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=usage.total_tokens,
            cached_tokens=cached_tokens,
            reasoning_tokens=usage.reasoning_tokens,
            cache_creation_input_tokens=usage.cache_creation_input_tokens,
            cost_usd=total_cost,
            estimated_savings_usd=total_savings,
        )

    @override
    def prepare_provider_kwargs(self, model_name: str) -> dict[str, Any]:
        """Prepare Google AI Studio specific arguments for LiteLLM.

        Args:
            model_name: The target model name.

        Returns:
            Dictionary containing safety settings.

        Raises:
            AppException: VALIDATION_FAILED if model_name is empty or whitespace.
        """
        if not model_name or not model_name.strip():
            logger.error(
                "[GoogleAIStudioCacheAdapter] %s: Target model_name cannot be empty.",
                ErrorCodes.VALIDATION_FAILED.name,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message="Target model_name cannot be empty for Google AI Studio provider kwargs.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        return {"safety_settings": _AI_STUDIO_SAFETY_SETTINGS}

    @override
    def prepare_structured_output(self, response_model: type[BaseModel]) -> dict[str, Any] | type[BaseModel]:
        """Convert a Pydantic model into a Google AI Studio structured output schema format.

        Args:
            response_model: The Pydantic model defining the expected JSON structure.

        Returns:
            A dictionary matching LiteLLM's structured output format with stripped constraints.

        Raises:
            AppException: VALIDATION_FAILED if response_model is not a Pydantic BaseModel subclass.
        """
        if not isinstance(response_model, type) or not issubclass(response_model, BaseModel):
            logger.error(
                "[GoogleAIStudioCacheAdapter] %s: response_model must be a Pydantic BaseModel subclass.",
                ErrorCodes.VALIDATION_FAILED.name,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message="response_model must be a Pydantic BaseModel subclass for Google AI Studio structured output.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

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

    @staticmethod
    def _inject_thinking_budget(call_kwargs: dict[str, Any], thinking_budget: int) -> None:
        """Inject the Gemini thinkingBudget configuration into call_kwargs extra_body.

        Args:
            call_kwargs: Mutable dictionary of LiteLLM call arguments.
            thinking_budget: Target thinking token budget to inject.
        """
        if "extra_body" not in call_kwargs or call_kwargs["extra_body"] is None:
            call_kwargs["extra_body"] = {}
        if "generationConfig" not in call_kwargs["extra_body"]:
            call_kwargs["extra_body"]["generationConfig"] = {}
        if "thinkingConfig" not in call_kwargs["extra_body"]["generationConfig"]:
            call_kwargs["extra_body"]["generationConfig"]["thinkingConfig"] = {}
        call_kwargs["extra_body"]["generationConfig"]["thinkingConfig"]["thinkingBudget"] = thinking_budget

    @staticmethod
    def _apply_cached_content_mapping(call_kwargs: dict[str, Any]) -> None:
        """Map cached_content into camelCase extra_body.cachedContent and scrub stray system turns.

        Args:
            call_kwargs: Mutable dictionary of LiteLLM call arguments.
        """
        cache_id = call_kwargs["cached_content"]
        if "extra_body" not in call_kwargs or call_kwargs["extra_body"] is None:
            call_kwargs["extra_body"] = {}
        # Step 1: Preserving ONLY canonical camelCase cachedContent to avoid Google proto3 oneof collision
        call_kwargs["extra_body"]["cachedContent"] = cache_id

        if "messages" in call_kwargs:
            system_msgs = [m for m in call_kwargs["messages"] if _is_system_turn(m)]
            if system_msgs:
                logger.critical(
                    "ARCHITECTURE VIOLATION: %d system message(s) detected in cached payload. "
                    "Scrubbing defensively to prevent Google 400. "
                    "This indicates a CompiledPrompt construction defect.",
                    len(system_msgs),
                )
                call_kwargs["messages"] = [m for m in call_kwargs["messages"] if not _is_system_turn(m)]

    @override
    def prepare_kwargs(
        self,
        call_kwargs: dict[str, Any],
        config: LLMProviderConfig | ModelProfile | None = None,
        settings: Settings | None = None,
    ) -> dict[str, Any]:
        """Prepare AI Studio specific kwargs, handling caching mappings and parameters.

        Args:
            call_kwargs: The dictionary of arguments to pass to litellm.
            config: Optional config object for the provider.
            settings: Optional app settings.

        Returns:
            The potentially modified call_kwargs dictionary.
        """
        super().prepare_kwargs(call_kwargs, config=config, settings=settings)

        model_key = ""
        if "model" in call_kwargs and call_kwargs["model"]:
            model_key = str(call_kwargs["model"])
        elif isinstance(config, LLMProviderConfig | ModelProfile):
            model_key = config.model_name
        model_name = str(model_key).lower()
        is_gemini_v3 = is_gemini_v3_or_higher(model_name)

        thinking_budget: int | None = None
        if isinstance(config, ModelProfile) and config.thinking_budget_tokens is not None:
            thinking_budget = int(config.thinking_budget_tokens)

        if settings is not None and settings.environment == "development":
            if thinking_budget is not None:
                thinking_budget = min(thinking_budget, settings.dev_max_thinking_budget)
            else:
                thinking_budget = settings.dev_max_thinking_budget

        if thinking_budget is not None:
            self._inject_thinking_budget(call_kwargs, thinking_budget)

        if is_gemini_v3:
            scrubbed_keys: list[str] = []
            for deprecated_key in ("temperature", "top_p", "top_k", "frequency_penalty", "presence_penalty"):
                if deprecated_key in call_kwargs:
                    del call_kwargs[deprecated_key]
                    scrubbed_keys.append(deprecated_key)

            if scrubbed_keys:
                logger.debug(
                    "[GoogleAIStudioCacheAdapter] Scrubbed unsupported sampling "
                    "parameters %s for Gemini 3+ model '%s'.",
                    scrubbed_keys,
                    model_name,
                )

        if "cached_content" in call_kwargs:
            self._apply_cached_content_mapping(call_kwargs)

        return call_kwargs
