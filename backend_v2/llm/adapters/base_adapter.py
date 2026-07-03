"""Abstract base class for provider-agnostic caching and pricing adapters.

All implementations must enforce high-fidelity adapters supporting performance metrics,
strict pricing policies, and distributed rate pacing control patterns.
"""

import asyncio
import logging
import os
from abc import ABC, abstractmethod
from typing import Any

from arq.connections import RedisSettings, create_pool
from pydantic import BaseModel

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.enums import LLMProviderName
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

_redis_pool: Any | None = None
_redis_loop: Any | None = None


async def get_redis_client_for_pacing() -> Any:
    """Resolve or initialize the Redis client pool used for distributed rate pacing.

    Returns:
        The active Redis pool instance.

    Raises:
        AppException: STORAGE_ACCESS_FAILED if Redis connection pool creation fails.
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

    try:
        if "PYTEST_CURRENT_TEST" in os.environ:
            from backend_v2.utils.redis_patcher import get_patched_fakeredis_pool

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
    except Exception as e:
        logger.error("Failed to initialize Redis pool for pacing.", exc_info=True)
        raise AppException(
            message=f"Redis initialization failed: {str(e)}",
            status_code=500,
            details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
        ) from e

    return _redis_pool


async def apply_provider_pacing(
    provider_name: str, strategy_id: str | None = None, rpm_limit: int | None = None
) -> None:
    """Enforce provider-scoped RPM pacing using Redis distributed lock.

    Prevents Thundering Herd exhaustion of rate limits by spacing API calls.

    Args:
        provider_name: The target LLM provider identifier string.
        strategy_id: Optional strategy identifier to scope the lock (e.g. 'fast', 'strict').
        rpm_limit: Optional database-driven RPM limit. If > 0, dynamic pacing is used.

    Raises:
        AppException: NETWORK_UNAVAILABLE if Redis execution fails during pacing operations.
    """
    if rpm_limit is not None and rpm_limit > 0:
        delay = 60.0 / float(rpm_limit)
    else:
        match provider_name:
            case LLMProviderName.VERTEX_AI.value | LLMProviderName.GOOGLE.value:
                delay = get_settings().pacing_delay_vertex_seconds
            case LLMProviderName.OPENAI.value:
                delay = get_settings().pacing_delay_openai_seconds
            case LLMProviderName.MOCK.value:
                delay = get_settings().pacing_delay_mock_seconds
            case _:
                delay = 0

    if delay <= 0:
        return

    lock_target = f"{provider_name}:{strategy_id}" if strategy_id else provider_name
    logger.info("Applying provider pacing of %s seconds for '%s'.", delay, lock_target)

    try:
        redis_client = await get_redis_client_for_pacing()
        lock_key = f"lock:pacer:{lock_target}"
        lock_ttl_ms = int(delay * 1000)
        poll_interval_s = 0.5

        while True:
            # SETNX with expiration enforces the provider rate spacing
            lock_acquired = await redis_client.set(lock_key, "locked", nx=True, px=lock_ttl_ms)
            if lock_acquired:
                # Lock acquired! Do NOT release it; it protects the entire delay window.
                break

            logger.info(f"Wait-and-Poll: Pacing lock active for {lock_target}. Waiting...")
            await asyncio.sleep(poll_interval_s)
    except Exception as e:
        logger.error(f"Provider pacing operation failed for {provider_name}.", exc_info=True)
        raise AppException(
            message=f"Pacing failed: {str(e)}",
            status_code=500,
            details={"error_code": ErrorCodes.NETWORK_UNAVAILABLE.value},
        ) from e


class BaseLLMAdapter(ABC):
    """Abstract base class defining the strict interface for caching and pricing adapters."""

    @abstractmethod
    async def prepare_caching_payload(
        self, compiled_prompt: CompiledPrompt, model_name: str
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Prepare the payload for the API request by configuring caching structures.

        Args:
            compiled_prompt: The prompt after execution compilation stages.
            model_name: The physical target deployment model.

        Returns:
            A tuple containing:
                - The list of formatted messages (potentially with provider-specific cache blocks).
                - A dictionary of extra keyword arguments (kwargs) to merge into the request body.
        """
        pass

    @abstractmethod
    async def teardown_cache(self, workflow_run_id: str) -> None:
        """Teardown any resources or session states associated with caching.

        Args:
            workflow_run_id: Identifies the active pipeline execution sequence.
        """
        pass

    @abstractmethod
    def calculate_cost(self, usage: TokenUsage, pricing_config: dict[str, Any]) -> TokenUsage:
        """Calculate the precise financial usage cost and ROI utilizing provider-specific pricing coefficients.

        Args:
            usage: Token count footprint statistics.
            pricing_config: Provider rate tables mapping models to pricing metrics.

        Returns:
            TokenUsage structure updated with monetary and evaluation values.
        """
        pass

    @abstractmethod
    def prepare_provider_kwargs(self, model_name: str) -> dict[str, Any]:
        """Prepare LLM provider specific static configuration arguments.

        Called unconditionally for every LLM request to inject required provider-specific
        flags (e.g. safety_settings, custom formats) that bypass the LiteLLM translation layer.

        Args:
            model_name: The actual deployment model identifier.

        Returns:
            A dictionary containing provider-specific keyword arguments.
        """
        pass

    def sanitize_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Sanitize message array to prevent provider-specific API crashes.

        Defaults to returning the messages unmodified. Can be overridden by
        specific adapters to handle provider quirks (like orphaned tool messages).

        Args:
            messages: A list of message dictionaries.

        Returns:
            A sanitized list of message dictionaries.
        """
        return messages

    def prepare_kwargs(
        self, call_kwargs: dict[str, Any], config: Any | None = None, settings: Any | None = None
    ) -> dict[str, Any]:
        """Optional: Modifies parameters passed to LiteLLM (e.g. provider specific mappings).

        Args:
            call_kwargs: The dictionary of arguments to pass to litellm.
            config: Optional config object for the provider.
            settings: Optional app settings.

        Returns:
            The potentially modified call_kwargs dictionary.
        """
        return call_kwargs

    def build_http_client(self, timeout: float) -> Any | None:
        """Optional: Build a provider-specific HTTP client wrapper.

        Args:
            timeout: The requested timeout in seconds.

        Returns:
            A custom HTTP client or None to use default.
        """
        return None

    @abstractmethod
    def prepare_structured_output(self, response_model: type[BaseModel]) -> dict[str, Any] | type[BaseModel]:
        """Convert a Pydantic model into a provider-specific structured output schema format.

        Args:
            response_model: The Pydantic model defining the expected JSON structure.

        Returns:
            A dictionary matching the provider's native schema format, or the Pydantic type itself.
        """
        pass

    def _strip_unsupported_constraints(self, schema_dict: Any) -> None:
        """Strip unsupported JSON schema constraints (e.g. minLength, maxLength) for strict mode.

        Args:
            schema_dict: The JSON schema dictionary to mutate in place.
        """
        if isinstance(schema_dict, dict):
            schema_dict.pop("maxLength", None)
            schema_dict.pop("minLength", None)

            if "const" in schema_dict:
                schema_dict["enum"] = [schema_dict.pop("const")]

            # Remove contextual constraints not supported by standard strict schemas
            if "properties" in schema_dict:
                schema_dict["properties"].pop("contextual_override", None)
                schema_dict["properties"].pop("override_reason", None)
            if "required" in schema_dict and isinstance(schema_dict["required"], list):
                if "contextual_override" in schema_dict["required"]:
                    schema_dict["required"].remove("contextual_override")
                if "override_reason" in schema_dict["required"]:
                    schema_dict["required"].remove("override_reason")

            for v in list(schema_dict.values()):
                self._strip_unsupported_constraints(v)
        elif isinstance(schema_dict, list):
            for item in schema_dict:
                self._strip_unsupported_constraints(item)
