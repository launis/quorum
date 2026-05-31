"""Abstract base class for provider-agnostic caching and pricing adapters."""

import asyncio
import logging
import os
from abc import ABC, abstractmethod
from typing import Any

from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.enums import LLMProviderName, SystemConcurrency
from backend_v2.models.prompt import CompiledPrompt

logger = logging.getLogger(__name__)

_redis_pool: Any = None
_redis_loop: Any = None


async def get_redis_client_for_pacing() -> Any:
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

        from backend_v2.settings import get_settings

        settings = get_settings()
        _redis_pool = await create_pool(RedisSettings(host=settings.redis_host, port=settings.redis_port))
        _redis_loop = current_loop
    return _redis_pool


async def apply_provider_pacing(provider_name: str) -> None:
    """Enforce provider-scoped RPM pacing using Redis distributed lock.

    Prevents Thundering Herd exhaustion of rate limits by spacing API calls.
    """
    delay = 0
    if provider_name == LLMProviderName.VERTEX_AI.value:
        delay = SystemConcurrency.PACING_DELAY_VERTEX_SECONDS.value
    elif provider_name == LLMProviderName.OPENAI.value:
        delay = SystemConcurrency.PACING_DELAY_OPENAI_SECONDS.value
    elif provider_name == LLMProviderName.MOCK.value:
        delay = SystemConcurrency.PACING_DELAY_MOCK_SECONDS.value

    if delay <= 0:
        return

    redis_client = await get_redis_client_for_pacing()
    lock_key = f"lock:pacer:{provider_name}"
    lock_ttl_ms = int(delay * 1000)

    poll_interval_s = 0.5

    while True:
        # SETNX with expiration enforces the provider rate spacing
        lock_acquired = await redis_client.set(lock_key, "locked", nx=True, px=lock_ttl_ms)
        if lock_acquired:
            # Lock acquired! Do NOT release it; it protects the entire delay window.
            break

        logger.info(f"Wait-and-Poll: Pacing lock active for {provider_name}. Waiting...")
        await asyncio.sleep(poll_interval_s)


class BaseLLMAdapter(ABC):
    """Abstract base class defining the strict interface for caching and pricing adapters."""

    @abstractmethod
    async def prepare_caching_payload(
        self, compiled_prompt: CompiledPrompt, model_name: str
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Prepare the payload for the API request by configuring caching structures.

        Returns:
            A tuple containing:
                - The list of formatted messages (potentially with provider-specific cache blocks).
                - A dictionary of extra keyword arguments (kwargs) to merge into the request body.
        """
        pass

    @abstractmethod
    async def teardown_cache(self, workflow_run_id: str) -> None:
        """Teardown any resources or session states associated with caching.

        Option B: Vertex AI context cache deletion or No-Op for Anthropic/OpenAI.
        """
        pass

    @abstractmethod
    def calculate_cost(self, usage: TokenUsage, pricing_config: dict[str, Any]) -> TokenUsage:
        """Calculate the precise financial usage cost and ROI utilizing provider-specific pricing coefficients."""
        pass
