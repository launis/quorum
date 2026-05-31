from typing import cast

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.adapters.base_adapter import BaseLLMAdapter
from backend_v2.models.enums import LLMProviderName


class LLMCacheAdapterFactory:
    """Factory class to load the appropriate caching and pricing adapter lazily."""

    @staticmethod
    def get_adapter(provider_name: str) -> BaseLLMAdapter:
        """Return the appropriate adapter for the given provider_name.

        All concrete adapter imports are performed lazily within this method to ensure
        heavy third-party SDK dependencies (e.g. vertexai, anthropic) are not loaded
        into memory unless explicitly instantiated.

        Args:
            provider_name: The name of the LLM provider (e.g., 'vertex_ai', 'anthropic').

        Returns:
            An instance of BaseLLMAdapter.

        Raises:
            AppException: If the provider name is unrecognized or the adapter is not implemented.
        """
        match provider_name:
            case LLMProviderName.MOCK:
                from backend_v2.llm.adapters.mock_adapter import MockCacheAdapter

                return MockCacheAdapter()

            case LLMProviderName.VERTEX_AI | LLMProviderName.GOOGLE:
                try:
                    from backend_v2.llm.adapters.vertex_adapter import VertexCacheAdapter

                    return cast(BaseLLMAdapter, VertexCacheAdapter())
                except ImportError as e:
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
                    raise AppException(
                        message=f"Adapter for provider '{provider_name}' is not implemented: {e}",
                        status_code=500,
                        details={"error_code": ErrorCodes.CAPABILITY_NOT_SUPPORTED},
                    ) from e

            case _:
                raise AppException(
                    message=f"Unsupported provider: '{provider_name}'",
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED},
                )
