"""Vertex AI cache adapter with distributed Redis locks, thundering herd protection, and option B passive teardown."""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
from typing import Any

from pydantic import Field, field_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.adapters.base_adapter import BaseLLMAdapter
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.enums import PromptCacheStatus, SystemConcurrency
from backend_v2.models.prompt import CompiledPrompt

logger = logging.getLogger(__name__)

_redis_pool: Any = None
_redis_loop: Any = None


async def get_redis_client() -> Any:
    """Return a shared Redis connection pool or in-memory FakeRedis during tests.

    Adheres strictly to the testing firewalls.

    Returns:
        The active Redis connection pool instance.
    """
    global _redis_pool, _redis_loop
    try:
        current_loop = asyncio.get_running_loop()
    except RuntimeError:
        current_loop = None

    if _redis_pool is not None:
        if "PYTEST_CURRENT_TEST" in os.environ and _redis_loop is not current_loop:
            _redis_pool = None
        else:
            return _redis_pool

    if "PYTEST_CURRENT_TEST" in os.environ:
        from backend_v2.utils.redis_patcher import get_patched_fakeredis_pool

        _redis_pool = get_patched_fakeredis_pool()
        _redis_loop = current_loop
    else:
        from arq.connections import RedisSettings, create_pool

        from backend_v2.models.enums import SystemConcurrency
        from backend_v2.settings import get_settings

        settings = get_settings()
        _redis_pool = await create_pool(
            RedisSettings(
                host=settings.redis_host,
                port=settings.redis_port,
                conn_timeout=int(SystemConcurrency.REDIS_CONNECTION_TIMEOUT_SECONDS.value),
            )
        )
        _redis_loop = current_loop
    return _redis_pool


class VertexTokenUsage(TokenUsage):
    """Subclass of TokenUsage supporting Vertex-specific caching telemetry and savings.

    Attributes:
        estimated_savings_usd: FinOps ROI estimated savings in USD.
    """

    estimated_savings_usd: float = Field(default=0.0, description="FinOps ROI estimated savings in USD.")

    @field_validator("estimated_savings_usd")
    @classmethod
    def validate_estimated_savings_usd(cls, v: float) -> float:
        """Validate that the estimated savings are non-negative.

        Args:
            v: The computed savings in USD.

        Returns:
            The validated float value.

        Raises:
            ValueError: If the savings value is negative.
        """
        if v < 0.0:
            raise ValueError("estimated_savings_usd must be greater than or equal to 0.0")
        return v


class VertexCacheAdapter(BaseLLMAdapter):
    """Caching and pricing adapter for Google Vertex AI Gemini models."""

    async def prepare_caching_payload(
        self, compiled_prompt: CompiledPrompt, model_name: str
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Prepare the Vertex AI specific prompt payload by setting up cached content.

        Args:
            compiled_prompt: The structured CompiledPrompt instance.
            model_name: The target model name.

        Returns:
            A tuple containing:
                - The list of flattened messages.
                - A dictionary of extra keyword arguments containing the cache reference name.
        """
        estimated_token_count = compiled_prompt.metadata.get("estimated_token_count", 0)

        if estimated_token_count == 0:
            total_static_chars = 0
            for msg in compiled_prompt.static_messages:
                content = msg.get("content")
                if isinstance(content, str):
                    total_static_chars += len(content)
                elif isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            total_static_chars += len(block.get("text", ""))
                elif content is not None:
                    total_static_chars += len(str(content))
            estimated_token_count = total_static_chars // 4

        if estimated_token_count < SystemConcurrency.CONTEXT_CACHE_MINIMUM_TOKEN_LIMIT.value:
            logger.info(
                "Vertex AI caching bypassed: Token Proxy Score %d is below threshold %d",
                estimated_token_count,
                SystemConcurrency.CONTEXT_CACHE_MINIMUM_TOKEN_LIMIT.value,
            )
            return compiled_prompt.to_flat_messages(), {}

        static_hash = hashlib.sha256(json.dumps(compiled_prompt.static_messages, sort_keys=True).encode()).hexdigest()
        redis_key = f"vertex_cache:{model_name}:{static_hash}"
        lock_key = f"lock:vertex_cache:{model_name}:{static_hash}"

        redis_client = await get_redis_client()

        cache_id = await redis_client.get(redis_key)
        if cache_id:
            if isinstance(cache_id, bytes):
                cache_id = cache_id.decode("utf-8")

            if cache_id == PromptCacheStatus.FAILED.value:
                logger.warning(
                    "Vertex cached content previously marked as FAILED. Falling back to standard completion."
                )
                return compiled_prompt.to_flat_messages(), {}

            if cache_id != PromptCacheStatus.CREATING.value:
                logger.info(
                    "Vertex AI Cache Hit in shared ledger: %s",
                    cache_id,
                )
                return compiled_prompt.to_dynamic_flat(), {"cached_content": cache_id}

        lock_ttl_ms = int(SystemConcurrency.CONTEXT_CACHE_LOCK_TTL_SECONDS.value * 1000)
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
                        return compiled_prompt.to_dynamic_flat(), {"cached_content": cache_id}

                await redis_client.set(
                    redis_key,
                    PromptCacheStatus.CREATING.value,
                    ex=SystemConcurrency.CONTEXT_CACHE_LOCK_TTL_SECONDS.value,
                )

                import datetime

                from backend_v2.settings import get_settings

                settings = get_settings()
                project = os.getenv("VERTEX_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
                location = settings.vertex_location or "europe-north1"
                clean_model_name = model_name.split("/")[-1]
                # V3 Cache Fix: Upload ONLY static content to cache
                static_flat = compiled_prompt.to_static_flat()

                try:
                    import importlib

                    import vertexai

                    vertexai.init(project=project, location=location)

                    try:
                        caching = importlib.import_module("vertexai.preview.caching")
                        cached_content_cls = caching.CachedContent
                    except (ImportError, AttributeError):
                        generative_models = importlib.import_module("vertexai.preview.generative_models")
                        cached_content_cls = generative_models.cached_contents.CachedContent

                    logger.info(
                        "Creating Vertex AI Context Cache in GCP for model: %s",
                        clean_model_name,
                    )
                    # Convert to native Vertex AI GAPIC format: role/parts instead of role/content
                    vertex_contents = []
                    system_text = ""
                    for msg in static_flat:
                        role = msg.get("role", "user")
                        content = msg.get("content", "")

                        if role == "system":
                            system_text += content + "\n"
                            continue

                        if role == "assistant":
                            role = "model"

                        vertex_contents.append({"role": role, "parts": [{"text": content}]})

                    create_kwargs = {
                        "model_name": clean_model_name,
                        "contents": vertex_contents,
                        "ttl": datetime.timedelta(seconds=SystemConcurrency.CONTEXT_CACHE_PASSIVE_TTL_SECONDS.value),
                    }

                    if system_text:
                        create_kwargs["system_instruction"] = system_text.strip()

                    cached_content = cached_content_cls.create(**create_kwargs)
                    cache_resource_id = str(cached_content.name)

                    if not cache_resource_id.startswith("projects/"):
                        cache_resource_id = (
                            f"projects/{project}/locations/{location}/cachedContents/{cache_resource_id}"
                        )

                    await redis_client.set(
                        redis_key,
                        cache_resource_id,
                        ex=SystemConcurrency.CONTEXT_CACHE_PASSIVE_TTL_SECONDS.value,
                    )
                    logger.info(
                        "Vertex AI Context Cache successfully created: %s",
                        cache_resource_id,
                    )
                    # V3 Cache Fix: Return dynamic-only messages alongside cache reference
                    return compiled_prompt.to_dynamic_flat(), {"cached_content": cache_resource_id}

                except Exception:
                    logger.error(
                        "Fail-Soft: Google GCP API Context Cache creation failed. Falling back to uncached completion.",
                        exc_info=True,
                    )
                    await redis_client.set(redis_key, PromptCacheStatus.FAILED.value, ex=300)
                    return compiled_prompt.to_flat_messages(), {}

            finally:
                await redis_client.delete(lock_key)

        else:
            poll_interval_s = float(SystemConcurrency.CONTEXT_CACHE_LOCK_POLL_INTERVAL_MS.value / 1000.0)
            max_wait_s = float(SystemConcurrency.CONTEXT_CACHE_LOCK_WAIT_LIMIT_SECONDS.value)
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
                        return compiled_prompt.to_dynamic_flat(), {"cached_content": cache_id}

            logger.warning(
                "Wait-and-Poll timeout reached after %s seconds. Falling back to uncached completion.",
                max_wait_s,
            )
            return compiled_prompt.to_flat_messages(), {}

    async def teardown_cache(self, workflow_run_id: str) -> None:
        """No-Op teardown for Vertex AI (Option B - Pure Passive TTL Caching).

        Args:
            workflow_run_id: The tracking context identifier.
        """
        pass

    def calculate_cost(self, usage: TokenUsage, pricing_config: dict[str, Any]) -> VertexTokenUsage:
        """Calculate the precise Vertex AI cost and savings.

        Gemini Context Caching has a 75% read discount (meaning cached input tokens cost 25% of standard input).

        Args:
            usage: The source TokenUsage object.
            pricing_config: Provider pricing parameters.

        Returns:
            An instance of VertexTokenUsage with calculated values.

        Raises:
            AppException: If essential pricing parameters are missing from pricing_config.
        """
        if "input_token_price" not in pricing_config or "output_token_price" not in pricing_config:
            logger.error(
                "Invalid pricing configuration detected: missing input_token_price or output_token_price", exc_info=True
            )
            raise AppException(
                message="Invalid pricing configuration: missing input_token_price or output_token_price",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        p_in = float(pricing_config["input_token_price"])
        p_out = float(pricing_config["output_token_price"])

        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        cached_tokens = usage.cached_tokens

        regular_input = max(0, prompt_tokens - cached_tokens)

        cost_regular = regular_input * p_in
        cost_cached = cached_tokens * p_in * 0.25
        cost_output = completion_tokens * p_out

        total_cost = cost_regular + cost_cached + cost_output
        total_savings = cached_tokens * p_in * 0.75

        return VertexTokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=usage.total_tokens,
            cached_tokens=cached_tokens,
            reasoning_tokens=usage.reasoning_tokens,
            cost_usd=total_cost,
            estimated_savings_usd=total_savings,
        )
