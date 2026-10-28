"""Provider-agnostic caching facade implementing the Zero If-Statement Principle."""

import logging
import re
from typing import Final

import opentelemetry.trace as trace

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.adapters.adapter_factory import LLMCacheAdapterFactory
from backend_v2.models.llm import CachingPayloadResultDTO, LLMMessageDTO
from backend_v2.models.prompt import CompiledPrompt

__all__ = ["LLMCachingService"]

logger = logging.getLogger(__name__)

_UUID_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)
# Matches ISO 8601 timestamps (specifically YYYY-MM-DDTHH:MM:SS)
_TIMESTAMP_PATTERN: Final[re.Pattern[str]] = re.compile(r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")


class LLMCachingService:
    """Provider-agnostic Facade for Large Language Model context caching.

    Enforces the Zero If-Statement Principle by delegating all operations
    dynamically and blindly to the corresponding provider-specific adapter.
    """

    @staticmethod
    def record_cache_hit(is_hit: bool) -> None:
        """Record the context cache hit status on the active OpenTelemetry span.

        Args:
            is_hit: Whether a prompt cache hit occurred.
        """
        current_span = trace.get_current_span()
        if current_span.is_recording():
            current_span.set_attribute("gen_ai.cache.hit", is_hit)

    @classmethod
    async def prepare_caching_payload(
        cls,
        provider_name: str,
        compiled_prompt: CompiledPrompt,
        model_name: str,
    ) -> CachingPayloadResultDTO:
        """Prepare the cache payload by delegating to the appropriate adapter.

        Args:
            provider_name: The target LLM provider (e.g., 'vertex_ai', 'anthropic').
            compiled_prompt: The structured CompiledPrompt containing static and dynamic message segments.
            model_name: The actual target model identifier.

        Returns:
            Prepared messages and extra provider-specific caching keyword arguments.

        Raises:
            AppException: Triggered with ErrorCodes.VALIDATION_FAILED if dynamic traces
                pollute the static system prompt or if the provider is unrecognized, or
                ErrorCodes.CAPABILITY_NOT_SUPPORTED if adapter initialization fails.
        """
        await cls._run_purity_scanner(compiled_prompt.to_flat_messages())

        adapter = LLMCacheAdapterFactory.get_adapter(provider_name, model_name=model_name)
        return await adapter.prepare_caching_payload(compiled_prompt, model_name)

    @classmethod
    async def pre_cache_document(
        cls,
        provider_name: str,
        compiled_prompt: CompiledPrompt,
        model_name: str,
    ) -> None:
        """Pre-cache a document upfront (Cache Pre-Warming).

        Explicitly triggers the adapter to create and lock the provider-specific context cache,
        preventing thundering herds during parallel TaskGroup execution.

        Args:
            provider_name: The target LLM provider (e.g., 'vertex_ai').
            compiled_prompt: The structured CompiledPrompt containing static content.
            model_name: The target model identifier.

        Raises:
            AppException: Triggered with ErrorCodes.VALIDATION_FAILED if dynamic traces
                pollute the static system prompt or if the provider is unrecognized, or
                ErrorCodes.CAPABILITY_NOT_SUPPORTED if adapter initialization fails.
        """
        await cls.prepare_caching_payload(provider_name, compiled_prompt, model_name)

    @classmethod
    async def _run_purity_scanner(cls, messages: list[LLMMessageDTO]) -> None:
        """Scan system messages to detect context caching purity violations.

        Scans messages for dynamic traces such as UUIDs and ISO-8601 timestamps that
        prevent downstream caches from achieving optimal hit rates.

        Args:
            messages: Message DTOs consisting of standard roles and content.

        Raises:
            AppException: Triggered with ErrorCodes.VALIDATION_FAILED if a dynamic UUID
                or timestamp pattern is detected in a system message.
        """
        for msg in messages:
            if msg.role == "system":
                content = str(msg.content)
                if _UUID_PATTERN.search(content) or _TIMESTAMP_PATTERN.search(content):
                    msg_text = (
                        "PROMPT_CACHING_PURITY_VIOLATION: Dynamic trace/timestamp pattern "
                        "detected in static system instruction block. Cache hit rate will drop to 0%!"
                    )
                    logger.error(
                        "[LLMCachingService] %s: %s",
                        ErrorCodes.VALIDATION_FAILED.name,
                        msg_text,
                        exc_info=True,
                        extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )
                    raise AppException(
                        message=msg_text,
                        status_code=400,
                        details={
                            "error_code": ErrorCodes.VALIDATION_FAILED.value,
                            "reason": "Dynamic UUID or timestamp detected in static system prompt prefix",
                            "violating_role": msg.role,
                        },
                    )

    @staticmethod
    async def teardown_workflow_caches(provider_name: str, workflow_run_id: str) -> None:
        """Perform asynchronous cache teardown for active session states.

        Args:
            provider_name: The target LLM provider.
            workflow_run_id: The active workflow run reference ID.

        Raises:
            AppException: Triggered with ErrorCodes.INTERNAL_SERVER_ERROR if cache
                teardown fails.
        """
        try:
            adapter = LLMCacheAdapterFactory.get_adapter(provider_name)
            await adapter.teardown_cache(workflow_run_id)
        except Exception as e:
            logger.error(
                "Asynchronous cache teardown failed for provider '%s': %s",
                provider_name,
                str(e),
                exc_info=True,
                extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
            )
            status_code = 500
            raise AppException(
                message=f"Asynchronous cache teardown failed for provider '{provider_name}': {str(e)}",
                status_code=status_code,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR},
            ) from e
