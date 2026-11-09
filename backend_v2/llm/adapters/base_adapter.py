"""Abstract base class for provider-agnostic caching and pricing adapters.

All implementations must enforce high-fidelity adapters supporting performance metrics,
strict pricing policies, and distributed rate pacing control patterns.
"""

from __future__ import annotations

import asyncio
import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Final

import opentelemetry.trace as otel_trace
from arq.connections import ArqRedis, RedisSettings, create_pool
from pydantic import BaseModel

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import ResolvedCredentialDTO
from backend_v2.models.domain.system_config import ModelProfile
from backend_v2.models.domain.usage import PricingConfig, TokenUsage
from backend_v2.models.enums import LLMProviderName
from backend_v2.models.llm import CachingPayloadResultDTO, LLMProviderConfig
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.settings import Settings, get_settings

logger = logging.getLogger(__name__)

__all__ = [
    "BaseLLMAdapter",
    "apply_provider_pacing",
    "get_redis_client_for_pacing",
]

_DEFAULT_PACING_POLL_INTERVAL_SECONDS: Final[float] = 0.5


class _InMemoryPacingClient:
    """Network-free in-memory pacing client used during isolated pytest executions."""

    async def set(
        self,
        key: str,
        value: str,
        *,
        nx: bool = False,
        px: int | None = None,
    ) -> bool:
        """Immediately grant pacing lock in hermetic test environments.

        Args:
            key: Distributed lock key.
            value: Lock value string.
            nx: Set only if key does not exist.
            px: Expiration time in milliseconds.

        Returns:
            Always True to avoid artificial network/timer blocking in unit tests.
        """
        _ = (key, value, nx, px)
        return True


_redis_pool: ArqRedis | _InMemoryPacingClient | None = None


async def get_redis_client_for_pacing() -> ArqRedis | _InMemoryPacingClient:
    """Resolve or initialize the Redis client pool used for distributed rate pacing.

    Returns:
        The active Redis pool or in-memory pacing client instance.

    Raises:
        AppException: STORAGE_ACCESS_FAILED if Redis connection pool creation fails.
    """
    global _redis_pool

    try:
        if "PYTEST_CURRENT_TEST" in os.environ:
            return _InMemoryPacingClient()

        if _redis_pool is not None:
            return _redis_pool

        settings = get_settings()
        pool = await create_pool(
            RedisSettings(
                host=settings.redis_host,
                port=settings.redis_port,
                conn_timeout=int(settings.redis_connection_timeout_seconds),
            )
        )
        _redis_pool = pool
        return pool
    except (TimeoutError, ConnectionError, OSError, RuntimeError) as e:
        logger.error(
            "Failed to initialize Redis pool for pacing.",
            extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.name, "error_details": str(e)},
            exc_info=True,
        )
        raise AppException(
            message=f"Redis initialization failed: {str(e)}",
            status_code=500,
            details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
        ) from e


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
        AppException: VALIDATION_FAILED if provider_name is empty or rpm_limit is negative, or
            NETWORK_UNAVAILABLE if Redis execution fails during pacing operations.
    """
    if not provider_name or not provider_name.strip():
        logger.error(
            "Provider name cannot be empty for rate pacing.",
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
            exc_info=True,
        )
        raise AppException(
            message="Provider name cannot be empty for rate pacing.",
            status_code=400,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    if rpm_limit is not None and rpm_limit < 0:
        logger.error(
            "RPM limit (%d) cannot be negative for rate pacing.",
            rpm_limit,
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
            exc_info=True,
        )
        raise AppException(
            message=f"RPM limit ({rpm_limit}) cannot be negative for rate pacing.",
            status_code=400,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    settings = get_settings()
    if rpm_limit is not None and rpm_limit > 0:
        delay = 60.0 / float(rpm_limit)
    else:
        match provider_name:
            case LLMProviderName.VERTEX_AI.value:
                delay = float(settings.pacing_delay_vertex_seconds)
            case LLMProviderName.AI_STUDIO.value:
                delay = float(settings.pacing_delay_ai_studio_seconds)
            case LLMProviderName.OPENAI.value:
                delay = float(settings.pacing_delay_openai_seconds)
            case LLMProviderName.MOCK.value:
                delay = float(settings.pacing_delay_mock_seconds)
            case _:
                delay = 0.0

    if delay <= 0:
        return

    lock_target = f"{provider_name}:{strategy_id}" if strategy_id else provider_name
    logger.info("Applying provider pacing of %s seconds for '%s'.", delay, lock_target)

    raw_poll_ms = settings.context_cache_lock_poll_interval_ms
    poll_interval_s = (
        float(raw_poll_ms) / 1000.0
        if isinstance(raw_poll_ms, int | float) and raw_poll_ms > 0
        else _DEFAULT_PACING_POLL_INTERVAL_SECONDS
    )

    try:
        redis_client = await get_redis_client_for_pacing()
        lock_key = f"lock:pacer:{lock_target}"
        lock_ttl_ms = int(delay * 1000)

        while True:
            # SETNX with expiration enforces the provider rate spacing
            lock_acquired = await redis_client.set(lock_key, "locked", nx=True, px=lock_ttl_ms)
            if lock_acquired:
                # Lock acquired! Do NOT release it; it protects the entire delay window.
                break

            logger.info("Wait-and-Poll: Pacing lock active for %s. Waiting...", lock_target)
            await asyncio.sleep(poll_interval_s)
    except (TimeoutError, ConnectionError, OSError, RuntimeError) as e:
        logger.error(
            "Provider pacing operation failed for %s.",
            provider_name,
            extra={"error_code": ErrorCodes.NETWORK_UNAVAILABLE.name, "error_details": str(e)},
            exc_info=True,
        )
        raise AppException(
            message=f"Pacing failed: {str(e)}",
            status_code=500,
            details={"error_code": ErrorCodes.NETWORK_UNAVAILABLE.value},
        ) from e


class BaseLLMAdapter(ABC):
    """Abstract base class defining the strict interface for caching and pricing adapters."""

    @abstractmethod
    async def prepare_caching_payload(
        self,
        compiled_prompt: CompiledPrompt,
        model_name: str,
        config: LLMProviderConfig | ModelProfile | None = None,
        resolved_credential: ResolvedCredentialDTO | None = None,
    ) -> CachingPayloadResultDTO:
        """Prepare the payload for the API request by configuring caching structures.

        Args:
            compiled_prompt: The prompt after execution compilation stages.
            model_name: The physical target deployment model.
            config: Optional provider or model profile configuration.
            resolved_credential: Optional resolved tenant or platform credential DTO.

        Returns:
            A CachingPayloadResultDTO containing structured messages and extra kwargs.
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
    def calculate_cost(self, usage: TokenUsage, pricing_config: PricingConfig) -> TokenUsage:
        """Calculate the precise financial usage cost and ROI utilizing provider-specific pricing coefficients.

        Args:
            usage: Token count footprint statistics.
            pricing_config: Provider rate tables mapping models to pricing metrics.

        Returns:
            TokenUsage structure updated with monetary and evaluation values.
        """
        pass

    def estimate_static_tokens(self, compiled_prompt: CompiledPrompt, exclude_system: bool = False) -> tuple[int, bool]:
        """Estimate the token count for static prompt content and verify if valid turns exist.

        Calculates token estimate using standard character ratio (total_chars // 4).

        Args:
            compiled_prompt: The structured prompt payload containing static and dynamic turns.
            exclude_system: If True, system role messages are excluded from the character count.

        Returns:
            A tuple containing:
                - Estimated token count (int) derived from static message characters.
                - Boolean flag indicating whether non-system static turns are present.
        """
        total_chars = 0
        has_non_system_static = False

        for msg in compiled_prompt.static_messages:
            role = msg.role
            raw_content = msg.content

            if role == "system":
                if exclude_system:
                    continue
            else:
                has_non_system_static = True

            if isinstance(raw_content, str):
                total_chars += len(raw_content)
            else:
                total_chars += len(str(raw_content))

        estimated_tokens = total_chars // 4
        return estimated_tokens, has_non_system_static

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

    def sanitize_messages(self, messages: list[Any]) -> list[Any]:
        """Sanitize message array to prevent provider-specific API crashes.

        Defaults to returning the messages unmodified. Can be overridden by
        specific adapters to handle provider quirks (like orphaned tool messages).

        Args:
            messages: A list of message objects or dictionaries.

        Returns:
            A sanitized list of message objects or dictionaries.
        """
        return messages

    def prepare_kwargs(
        self,
        call_kwargs: dict[str, Any],
        config: LLMProviderConfig | ModelProfile | None = None,
        settings: Settings | None = None,
        resolved_credential: ResolvedCredentialDTO | None = None,
    ) -> dict[str, Any]:
        """Optional: Modifies parameters passed to LiteLLM (e.g. provider specific mappings).

        Args:
            call_kwargs: The dictionary of arguments to pass to litellm.
            config: Optional config object for the provider.
            settings: Optional app settings.
            resolved_credential: Optional resolved tenant or platform credential DTO.

        Returns:
            The potentially modified call_kwargs dictionary.
        """
        _ = (settings, resolved_credential)
        current_span = otel_trace.get_current_span()
        if current_span.is_recording():
            if "model" in call_kwargs and call_kwargs["model"] is not None:
                current_span.set_attribute("gen_ai.request.model", str(call_kwargs["model"]))
            if isinstance(config, LLMProviderConfig | ModelProfile) and config.provider is not None:
                current_span.set_attribute("gen_ai.system", str(config.provider))
        return call_kwargs

    def build_http_client(self, timeout: float) -> Any | None:
        """Optional: Build a provider-specific HTTP client wrapper.

        Args:
            timeout: The requested timeout in seconds.

        Returns:
            A custom HTTP client or None to use default.

        Raises:
            AppException: VALIDATION_FAILED if timeout is less than or equal to zero.
        """
        if timeout <= 0:
            logger.error(
                "HTTP client timeout (%s) must be greater than zero.",
                timeout,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
                exc_info=True,
            )
            raise AppException(
                message=f"HTTP client timeout ({timeout}) must be greater than zero.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
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

    def _strip_unsupported_constraints(
        self,
        schema_dict: Any,
        known_discriminators: set[str] | None = None,
    ) -> None:
        """Strip unsupported JSON schema constraints (e.g. minLength, maxLength) for strict mode.

        Also ensures that any discriminator property (e.g., 'block_type', 'extension_type',
        'runtimeType') present in an object schema's 'properties' is explicitly added to its
        'required' array so LLMs are constrained to output discriminator tags.

        Args:
            schema_dict: The JSON schema dictionary to mutate in place.
            known_discriminators: Set of property names that act as discriminators in the schema.
        """
        if known_discriminators is None:
            known_discriminators = {"block_type", "extension_type", "runtimeType"}
            # Extract any explicit discriminator property names declared in the schema
            self._collect_discriminator_names(schema_dict, known_discriminators)

        if isinstance(schema_dict, dict):
            # [2026-07-03] Targeted Schema Stripping:
            # We MUST strip mechanical constraints that cause Vertex's Guided Decoding state machine
            # to explode ("too many states for serving"). These include lengths, regexes, and bounds.
            # We MUST NOT strip semantic fields ("title", "description", "enum") because the LLM
            # relies on them to prevent hallucinations.
            keys_to_strip: list[str] = [
                "maxLength",
                "minLength",
                "pattern",
                "format",
                "maximum",
                "minimum",
                "exclusiveMaximum",
                "exclusiveMinimum",
                "multipleOf",
            ]
            for k in keys_to_strip:
                if k in schema_dict:
                    del schema_dict[k]

            if "const" in schema_dict:
                schema_dict["enum"] = [schema_dict["const"]]
                del schema_dict["const"]

            # Remove contextual constraints not supported by standard strict schemas
            if "properties" in schema_dict:
                properties = schema_dict["properties"]
                if isinstance(properties, dict):
                    if "contextual_override" in properties:
                        del properties["contextual_override"]
                    if "override_reason" in properties:
                        del properties["override_reason"]

                # Ensure any discriminator property present in properties is marked required
                properties = schema_dict["properties"]
                if isinstance(properties, dict):
                    if "required" not in schema_dict or not isinstance(schema_dict["required"], list):
                        schema_dict["required"] = []
                    for disc in known_discriminators:
                        if disc in properties and disc not in schema_dict["required"]:
                            schema_dict["required"].append(disc)

            if "required" in schema_dict and isinstance(schema_dict["required"], list):
                if "contextual_override" in schema_dict["required"]:
                    schema_dict["required"].remove("contextual_override")
                if "override_reason" in schema_dict["required"]:
                    schema_dict["required"].remove("override_reason")

            for v in list(schema_dict.values()):
                self._strip_unsupported_constraints(v, known_discriminators=known_discriminators)
        elif isinstance(schema_dict, list):
            for item in schema_dict:
                self._strip_unsupported_constraints(item, known_discriminators=known_discriminators)

    def _collect_discriminator_names(self, node: Any, result: set[str]) -> None:
        """Recursively scan schema for discriminator propertyName declarations.

        Args:
            node: The schema node to inspect.
            result: The accumulator set of discriminator names.
        """
        if isinstance(node, dict):
            if "discriminator" in node and isinstance(node["discriminator"], dict):
                prop_name = None
                if "propertyName" in node["discriminator"]:
                    prop_name = node["discriminator"]["propertyName"]
                if isinstance(prop_name, str) and prop_name:
                    result.add(prop_name)
            for v in node.values():
                self._collect_discriminator_names(v, result)
        elif isinstance(node, list):
            for item in node:
                self._collect_discriminator_names(item, result)
