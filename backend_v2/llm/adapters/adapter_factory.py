"""Adapter Factory for Lazy Loading LLM Providers Cache Adapters.

Provides a decoupled mechanism to fetch concrete LLM cache adapters without triggering
heavy upfront third-party imports at initialization.
"""

from __future__ import annotations

import logging

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.adapters.base_adapter import BaseLLMAdapter
from backend_v2.models.enums import LLMProviderName

logger = logging.getLogger(__name__)

__all__ = ["LLMCacheAdapterFactory"]


class LLMCacheAdapterFactory:
    """Factory class to load the appropriate caching and pricing adapter lazily.

    All concrete adapter imports are performed lazily within this method to ensure
    heavy third-party SDK dependencies (specifically vertexai and anthropic) are not loaded
    into memory unless explicitly instantiated.
    """

    @staticmethod
    def get_adapter(
        provider_name: LLMProviderName | str,
        model_name: str | None = None,
    ) -> BaseLLMAdapter:
        """Return the appropriate adapter for the given provider_name and optional model_name.

        All concrete adapter imports are performed lazily within this method to ensure
        heavy third-party SDK dependencies (specifically vertexai and anthropic) are not loaded
        into memory unless explicitly instantiated.

        Args:
            provider_name: The name of the LLM provider.
            model_name: Optional model name identifier preserved for interface parity.

        Returns:
            An instance of BaseLLMAdapter.

        Raises:
            AppException: Triggered with ErrorCodes.CAPABILITY_NOT_SUPPORTED if the SDK import fails
                or ErrorCodes.VALIDATION_FAILED if the provider is unrecognized.
        """
        _ = model_name
        try:
            match provider_name:
                case LLMProviderName.MOCK:
                    from backend_v2.llm.adapters.mock_adapter import MockCacheAdapter

                    return MockCacheAdapter()

                case LLMProviderName.AI_STUDIO | "ai_studio":
                    from backend_v2.llm.adapters.ai_studio_adapter import GoogleAIStudioCacheAdapter

                    return GoogleAIStudioCacheAdapter()

                case LLMProviderName.VERTEX_AI | "vertex_ai":
                    from backend_v2.llm.adapters.vertex_adapter import VertexCacheAdapter

                    return VertexCacheAdapter()

                case LLMProviderName.ANTHROPIC:
                    from backend_v2.llm.adapters.anthropic_adapter import AnthropicCacheAdapter

                    return AnthropicCacheAdapter()

                case LLMProviderName.OPENAI:
                    from backend_v2.llm.adapters.openai_adapter import OpenAICacheAdapter

                    return OpenAICacheAdapter()

                case LLMProviderName.DEEPSEEK:
                    from backend_v2.llm.adapters.deepseek_adapter import DeepSeekCacheAdapter

                    return DeepSeekCacheAdapter()

                case _:
                    logger.error(
                        "Unsupported provider encountered in adapter factory: %s",
                        provider_name,
                        extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
                        exc_info=True,
                    )
                    raise AppException(
                        message=f"Unsupported provider: '{provider_name}'",
                        status_code=400,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )
        except ImportError as e:
            logger.error(
                "Cache adapter import failed for provider '%s'",
                provider_name,
                extra={"error_code": ErrorCodes.CAPABILITY_NOT_SUPPORTED.name},
                exc_info=True,
            )
            raise AppException(
                message=f"Adapter for provider '{provider_name}' is not implemented: {e}",
                status_code=500,
                details={"error_code": ErrorCodes.CAPABILITY_NOT_SUPPORTED.value},
            ) from e
