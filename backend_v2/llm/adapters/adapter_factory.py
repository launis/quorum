"""Adapter Factory for Lazy Loading LLM Providers Cache Adapters.

Provides a decoupled mechanism to fetch concrete LLM cache adapters without triggering
heavy upfront third-party imports at initialization.
"""

from __future__ import annotations

import logging
from typing import cast

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.adapters.base_adapter import BaseLLMAdapter
from backend_v2.models.enums import LLMProviderName

logger = logging.getLogger(__name__)


class LLMCacheAdapterFactory:
    """Factory class to load the appropriate caching and pricing adapter lazily.

    All concrete adapter imports are performed lazily within this method to ensure
    heavy third-party SDK dependencies (e.g. vertexai, anthropic) are not loaded
    into memory unless explicitly instantiated.
    """

    @staticmethod
    def get_adapter(
        provider_name: LLMProviderName | str,
        model_name: str | None = None,
    ) -> BaseLLMAdapter:
        """Return the appropriate adapter for the given provider_name and optional model_name.

        All concrete adapter imports are performed lazily within this method to ensure
        heavy third-party SDK dependencies (e.g. vertexai, anthropic) are not loaded
        into memory unless explicitly instantiated.

        Args:
            provider_name: The name of the LLM provider.
            model_name: Optional model name identifier used to disambiguate umbrella
                providers (such as 'google' with 'vertex_ai/' prefix vs 'gemini/' prefix).

        Returns:
            An instance of BaseLLMAdapter.

        Raises:
            AppException: Triggered with ErrorCodes.CAPABILITY_NOT_SUPPORTED if the SDK import fails
                or ErrorCodes.VALIDATION_FAILED if the provider is unrecognized.
        """
        match provider_name:
            case LLMProviderName.MOCK:
                from backend_v2.llm.adapters.mock_adapter import MockCacheAdapter

                return MockCacheAdapter()

            case LLMProviderName.AI_STUDIO | "ai_studio":
                try:
                    from backend_v2.llm.adapters.ai_studio_adapter import GoogleAIStudioCacheAdapter

                    return cast(BaseLLMAdapter, GoogleAIStudioCacheAdapter())
                except ImportError as e:
                    logger.error("Google AI Studio cache adapter import failed", exc_info=True)
                    raise AppException(
                        message=f"Adapter for provider '{provider_name}' is not implemented: {e}",
                        status_code=500,
                        details={"error_code": ErrorCodes.CAPABILITY_NOT_SUPPORTED},
                    ) from e

            case LLMProviderName.VERTEX_AI | "vertex_ai":
                try:
                    from backend_v2.llm.adapters.vertex_adapter import VertexCacheAdapter

                    return cast(BaseLLMAdapter, VertexCacheAdapter())
                except ImportError as e:
                    logger.error("Vertex AI cache adapter import failed", exc_info=True)
                    raise AppException(
                        message=f"Adapter for provider '{provider_name}' is not implemented: {e}",
                        status_code=500,
                        details={"error_code": ErrorCodes.CAPABILITY_NOT_SUPPORTED},
                    ) from e

            case LLMProviderName.GOOGLE | "google":
                # Disambiguate umbrella 'google' provider based on model_name
                is_vertex = model_name is not None and ("vertex_ai/" in model_name or "vertex_ai" in model_name)
                if is_vertex:
                    try:
                        from backend_v2.llm.adapters.vertex_adapter import VertexCacheAdapter

                        return cast(BaseLLMAdapter, VertexCacheAdapter())
                    except ImportError as e:
                        logger.error("Vertex AI cache adapter import failed", exc_info=True)
                        raise AppException(
                            message=f"Adapter for provider '{provider_name}' is not implemented: {e}",
                            status_code=500,
                            details={"error_code": ErrorCodes.CAPABILITY_NOT_SUPPORTED},
                        ) from e
                else:
                    try:
                        from backend_v2.llm.adapters.ai_studio_adapter import GoogleAIStudioCacheAdapter

                        return cast(BaseLLMAdapter, GoogleAIStudioCacheAdapter())
                    except ImportError as e:
                        logger.error("Google AI Studio cache adapter import failed", exc_info=True)
                        raise AppException(
                            message=f"Adapter for provider '{provider_name}' is not implemented: {e}",
                            status_code=500,
                            details={"error_code": ErrorCodes.CAPABILITY_NOT_SUPPORTED},
                        ) from e

            case LLMProviderName.ANTHROPIC:
                try:
                    from backend_v2.llm.adapters.anthropic_adapter import AnthropicCacheAdapter

                    return cast(BaseLLMAdapter, AnthropicCacheAdapter())
                except ImportError as e:
                    logger.error("Anthropic cache adapter import failed", exc_info=True)
                    raise AppException(
                        message=f"Adapter for provider '{provider_name}' is not implemented: {e}",
                        status_code=500,
                        details={"error_code": ErrorCodes.CAPABILITY_NOT_SUPPORTED},
                    ) from e

            case LLMProviderName.OPENAI:
                try:
                    from backend_v2.llm.adapters.openai_adapter import OpenAICacheAdapter

                    return cast(BaseLLMAdapter, OpenAICacheAdapter())
                except ImportError as e:
                    logger.error("OpenAI cache adapter import failed", exc_info=True)
                    raise AppException(
                        message=f"Adapter for provider '{provider_name}' is not implemented: {e}",
                        status_code=500,
                        details={"error_code": ErrorCodes.CAPABILITY_NOT_SUPPORTED},
                    ) from e

            case LLMProviderName.DEEPSEEK:
                try:
                    from backend_v2.llm.adapters.deepseek_adapter import DeepSeekCacheAdapter

                    return cast(BaseLLMAdapter, DeepSeekCacheAdapter())
                except ImportError as e:
                    logger.error("DeepSeek cache adapter import failed", exc_info=True)
                    raise AppException(
                        message=f"Adapter for provider '{provider_name}' is not implemented: {e}",
                        status_code=500,
                        details={"error_code": ErrorCodes.CAPABILITY_NOT_SUPPORTED},
                    ) from e

            case _:
                logger.error("Unsupported provider encountered in adapter factory: %s", provider_name)
                raise AppException(
                    message=f"Unsupported provider: '{provider_name}'",
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED},
                )
