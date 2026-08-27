"""Vertex AI cache adapter with distributed Redis locks, thundering herd protection, and option B passive teardown."""

from __future__ import annotations

import asyncio
import datetime
import hashlib
import json
import logging
import os
from typing import Any

from arq.connections import RedisSettings, create_pool
from pydantic import BaseModel, Field, field_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.adapters.base_adapter import BaseLLMAdapter
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.enums import GCPVertexLocation, PromptCacheStatus
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.settings import get_settings
from backend_v2.utils.redis_patcher import get_patched_fakeredis_pool

logger = logging.getLogger(__name__)

_VERTEX_SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
]

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
        _redis_pool = get_patched_fakeredis_pool()
        _redis_loop = current_loop
    else:
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
            The validated savings value.

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
            compiled_prompt: The structured prompt payload.
            model_name: The target model name.

        Returns:
            A pair containing:
                - The list of flattened messages.
                - A dictionary of extra keyword arguments containing the cache reference name.
        """
        # Vertex AI context caching requires caching conversational turns in `contents`.
        # System instructions alone (`system_instruction`) cannot form an explicit cached resource in GCP without accompanying conversational content.
        # Calculate the token estimate strictly from static non-system messages to prevent GCP 1-token / empty contents InvalidArgument errors.
        total_content_chars = 0
        has_non_system_static = False
        for msg in compiled_prompt.static_messages:
            role = msg.get("role", "user")
            if role == "system":
                continue
            has_non_system_static = True
            content = msg.get("content")
            if isinstance(content, str):
                total_content_chars += len(content)
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        total_content_chars += len(block.get("text", ""))
            elif content is not None:
                total_content_chars += len(str(content))
        static_content_token_count = total_content_chars // 4

        min_threshold = max(get_settings().context_cache_minimum_token_limit, 1024)

        if (
            get_settings().disable_vertex_cache
            or not has_non_system_static
            or static_content_token_count < min_threshold
        ):
            logger.info(
                "Vertex AI caching bypassed: Static conversational content token count %d is below minimum threshold %d (or static messages lack non-system turns or globally disabled).",
                static_content_token_count,
                min_threshold,
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

                settings = get_settings()
                project = os.getenv("VERTEX_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
                location = settings.vertex_location or GCPVertexLocation.EUROPE_NORTH1.value
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
                    except ImportError, AttributeError:
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
                        "ttl": datetime.timedelta(seconds=get_settings().context_cache_passive_ttl_seconds),
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
                        ex=get_settings().context_cache_passive_ttl_seconds,
                    )
                    logger.info(
                        "Vertex AI Context Cache successfully created: %s",
                        cache_resource_id,
                    )
                    # V3 Cache Fix: Return dynamic-only messages alongside cache reference
                    return compiled_prompt.to_dynamic_flat(), {
                        "cached_content": cache_resource_id,
                    }

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
        """No-Op teardown for Vertex AI (Option B - Pure Passive TTL Caching).

        Args:
            workflow_run_id: The tracking context identifier.
        """
        pass

    def calculate_cost(self, usage: TokenUsage, pricing_config: dict[str, Any]) -> VertexTokenUsage:
        """Calculate the precise Vertex AI cost and savings.

        Gemini Context Caching has a 75% read discount (meaning cached input tokens cost 25% of standard input).

        Args:
            usage: The source token usage data.
            pricing_config: Provider pricing parameters.

        Returns:
            The calculated usage metrics including savings.

        Raises:
            AppException (ErrorCodes.CONFIGURATION_ERROR): If essential pricing parameters are missing from pricing_config.
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

    def prepare_provider_kwargs(self, model_name: str) -> dict[str, Any]:
        """Prepare Vertex AI specific arguments for LiteLLM.

        Args:
            model_name: The target model name.

        Returns:
            Dictionary containing safety settings.
        """
        return {"safety_settings": _VERTEX_SAFETY_SETTINGS}

    def sanitize_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Sanitize message array to prevent LiteLLM Vertex transformation crashes.

        Vertex AI transformation in LiteLLM requires every `role: tool` message to be
        preceded by a `role: assistant` message containing matching `tool_calls`.
        If an orphaned `role: tool` message exists (e.g., due to self-healing retries
        stripping the original context), LiteLLM throws APIConnectionError.

        This function removes any `role: tool` message that lacks a valid pairing.

        Args:
            messages: A list of message dictionaries.

        Returns:
            A sanitized list of message dictionaries.
        """
        valid_tool_call_ids = set()
        sanitized = []

        for msg in messages:
            if msg.get("role") == "assistant" and "tool_calls" in msg:
                # Collect all valid tool_call_ids from assistant message
                for tc in msg["tool_calls"]:
                    if "id" in tc:
                        valid_tool_call_ids.add(tc["id"])
                sanitized.append(msg)
            elif msg.get("role") == "tool":
                tool_call_id = msg.get("tool_call_id")
                if tool_call_id in valid_tool_call_ids:
                    sanitized.append(msg)
                else:
                    logger.warning(
                        "[VertexAdapter] Stripping orphaned tool message (id: %s) to prevent Vertex crash.",
                        tool_call_id,
                    )
            else:
                sanitized.append(msg)

        return sanitized

    def prepare_kwargs(
        self, call_kwargs: dict[str, Any], config: Any | None = None, settings: Any | None = None
    ) -> dict[str, Any]:
        """Prepare Vertex specific kwargs, handling caching mappings and location resolution.

        Args:
            call_kwargs: The dictionary of arguments to pass to litellm.
            config: Optional config object for the provider.
            settings: Optional app settings.

        Returns:
            The potentially modified call_kwargs dictionary.
        """
        # 1. Resolve Vertex Location
        config_location = getattr(config, "vertex_location", None) if config else None

        # 1.5 Reasoning Parameter Extraction
        if config and getattr(config, "additional_params", None):
            thinking_budget = config.additional_params.get("thinking_budget_tokens")
            if thinking_budget:
                if "extra_body" not in call_kwargs or call_kwargs["extra_body"] is None:
                    call_kwargs["extra_body"] = {}
                if "generationConfig" not in call_kwargs["extra_body"]:
                    call_kwargs["extra_body"]["generationConfig"] = {}
                if "thinkingConfig" not in call_kwargs["extra_body"]["generationConfig"]:
                    call_kwargs["extra_body"]["generationConfig"]["thinkingConfig"] = {}
                call_kwargs["extra_body"]["generationConfig"]["thinkingConfig"]["thinkingBudget"] = int(thinking_budget)
        settings_location = getattr(settings, "vertex_location", None) if settings else None
        env_location = os.getenv("HARDENING_VERTEX_LOCATION")
        active_location = (
            call_kwargs.get("vertex_location")
            or config_location
            or settings_location
            or env_location
            or GCPVertexLocation.EUROPE_NORTH1.value
        )
        os.environ["VERTEX_LOCATION"] = active_location

        os.environ["VERTEXAI_LOCATION"] = active_location
        call_kwargs["vertex_location"] = active_location

        # 2. Caching parameter mapping
        if "cached_content" in call_kwargs:
            # Vertex API rejects (400 Bad Request) dynamic tools when using static cached_content.
            # If tools are detected, we gracefully bypass caching for this single request.
            if call_kwargs.get("tools"):
                logger.warning(
                    "[VertexAdapter] Dynamic tool payload detected alongside Vertex Caching. "
                    "Bypassing caching dynamically to prevent 400 Bad Request."
                )
                call_kwargs.pop("cached_content", None)
            else:
                cache_id = call_kwargs["cached_content"]
                if "extra_headers" not in call_kwargs or call_kwargs["extra_headers"] is None:
                    call_kwargs["extra_headers"] = {}
                call_kwargs["extra_headers"]["cached_content"] = cache_id

                if "extra_body" not in call_kwargs or call_kwargs["extra_body"] is None:
                    call_kwargs["extra_body"] = {}
                call_kwargs["extra_body"]["cachedContent"] = cache_id
                call_kwargs["extra_body"]["cached_content"] = cache_id

                # V3 Cache Fix: Diagnostic guard replacing blind system scrubber
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

    def build_http_client(self, timeout: float) -> Any | None:
        """Build a persistent HTTPX client with specific constraints for Vertex AI.

        Vertex AI Load Balancers drop connections after 600s. We enforce HTTP/1.1
        with massive keep-alive limits to reduce socket exhaustion on >100k token runs.
        Also, wraps the client in AsyncHTTPHandler because LiteLLM drops custom
        clients for Vertex if they are not wrapped.

        Args:
            timeout: The requested timeout in seconds.

        Returns:
            The wrapped httpx.AsyncClient or None.
        """
        import httpx
        from litellm.llms.custom_httpx.http_handler import AsyncHTTPHandler

        _raw_httpx = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout, connect=60.0),
            http2=False,
            limits=httpx.Limits(max_keepalive_connections=200, max_connections=400),
            transport=httpx.AsyncHTTPTransport(retries=3),
        )

        _handler = AsyncHTTPHandler(timeout=timeout)
        _handler.client = _raw_httpx
        return _handler

    def prepare_structured_output(self, response_model: type[BaseModel]) -> dict[str, Any] | type[BaseModel]:
        """Convert a Pydantic model into a Vertex AI specific structured output schema format.

        Vertex natively supports Strict JSON Schema but fails on constraints like minLength/maxLength.

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
