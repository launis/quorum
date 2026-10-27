"""LLMFactory for instantiating configured LLMProvider implementations."""

import logging
import sys
from collections.abc import Sequence
from typing import Any

from backend_v2.exceptions import (
    ConfigurationError,
    ErrorCodes,
    ServiceUnavailableError,
)
from backend_v2.llm.provider.base_and_mock_provider import LLMProvider, MockProvider
from backend_v2.llm.provider.env_and_schema_utils import _safe_static_getattr
from backend_v2.models.enums import LLMProviderName
from backend_v2.models.llm import LLMProviderConfig
from backend_v2.services.usage_service import UsageService
from backend_v2.settings import Settings, get_settings

__all__ = [
    "LLMFactory",
]

logger = logging.getLogger(__name__)

_ORIG_GET_SETTINGS = get_settings
_ORIG_MOCK_PROVIDER = MockProvider


class LLMFactory:
    """Factory class to instantiate the appropriate LLMProvider based on configuration."""

    @staticmethod
    def _validate_config_and_grounding(
        config: LLMProviderConfig,
        tools: Sequence[Any] | None,
        enable_grounding: bool,
    ) -> None:
        """Validate provider activation status and grounding capability support.

        Args:
            config: Strict database-driven provider configuration object.
            tools: Optional sequence of tool definitions requested by the caller.
            enable_grounding: Explicit flag indicating whether grounding is requested.

        Raises:
            ServiceUnavailableError: If the provider is disabled (ErrorCodes.SERVICE_DISABLED).
            ConfigurationError: If grounding is requested when unsupported (ErrorCodes.CAPABILITY_NOT_SUPPORTED).
        """
        if not config.is_active:
            logger.error(
                "[LLMFactory] %s: Provider '%s' is disabled in configuration.",
                ErrorCodes.SERVICE_DISABLED.name,
                config.model_name,
                exc_info=True,
            )
            raise ServiceUnavailableError(
                message=f"Provider '{config.model_name}' is disabled in configuration.",
                details={"error_code": ErrorCodes.SERVICE_DISABLED.value},
            )

        has_search_intent = enable_grounding
        if not has_search_intent and tools:
            has_search_intent = any("google_search" in str(t) for t in tools)

        if has_search_intent and not config.supports_grounding:
            msg = (
                f"Grounding/Search requested for '{config.model_name}' "
                "but provider config 'supports_grounding' is False."
            )
            logger.error(
                "[LLMFactory] %s: %s",
                ErrorCodes.CAPABILITY_NOT_SUPPORTED.name,
                msg,
                exc_info=True,
            )
            raise ConfigurationError(
                message=msg,
                details={"error_code": ErrorCodes.CAPABILITY_NOT_SUPPORTED.value},
            )

    @staticmethod
    def _resolve_config_limits(
        config: LLMProviderConfig,
        limits: dict[str, int] | None,
    ) -> dict[str, int]:
        """Resolve effective TPM and RPM rate limits from provider configuration.

        Args:
            config: Strict database-driven provider configuration object.
            limits: Optional initial rate limits mapping.

        Returns:
            Resolved dictionary of rate limits combining caller limits with config overrides.
        """
        resolved_limits: dict[str, int]
        if limits is None:
            resolved_limits = {}
        else:
            resolved_limits = dict(limits)
        if config.tpm_limit > 0:
            resolved_limits = {**resolved_limits, "tpm": config.tpm_limit}
        if config.rpm_limit > 0:
            resolved_limits = {**resolved_limits, "rpm": config.rpm_limit}
        return resolved_limits

    @staticmethod
    def _resolve_provider_api_key(
        provider_type: str,
        model_name: str,
        api_key: str | None,
        settings: Settings,
    ) -> str | None:
        """Resolve and validate the provider API key from explicit overrides or environment settings.

        Args:
            provider_type: Provider identifier string.
            model_name: Target model identifier string.
            api_key: Optional explicit API key override.
            settings: Active application settings instance.

        Returns:
            Resolved API key string or None for keyless providers (such as Vertex AI ADC).

        Raises:
            ConfigurationError: If a required provider API key is missing (ErrorCodes.CONFIGURATION_ERROR).
        """
        resolved_api_key = api_key
        match provider_type.lower():
            case LLMProviderName.VERTEX_AI.value | "vertex_ai":
                # Vertex AI authenticates via GCP Application Default Credentials backed by service-account.json
                return None
            case LLMProviderName.AI_STUDIO.value | "ai_studio":
                if not resolved_api_key:
                    resolved_api_key = settings.google_api_key
                if not resolved_api_key:
                    logger.error(
                        "Fail-Fast: GEMINI_API_KEY / GOOGLE_API_KEY is not configured in settings or environment.",
                        extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "model_name": model_name},
                        exc_info=True,
                    )
                    raise ConfigurationError(
                        message=(
                            "Fail-Fast: GEMINI_API_KEY / GOOGLE_API_KEY is not configured in settings or environment."
                        ),
                        details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                    )
            case LLMProviderName.OPENAI.value | "openai":
                if not resolved_api_key:
                    resolved_api_key = settings.openai_api_key
                if not resolved_api_key:
                    logger.error(
                        "Fail-Fast: OPENAI_API_KEY is not configured in settings or environment.",
                        extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "model_name": model_name},
                        exc_info=True,
                    )
                    raise ConfigurationError(
                        message="Fail-Fast: OPENAI_API_KEY is not configured in settings or environment.",
                        details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                    )
            case LLMProviderName.ANTHROPIC.value | "anthropic":
                if not resolved_api_key:
                    resolved_api_key = settings.anthropic_api_key
                if not resolved_api_key:
                    logger.error(
                        "Fail-Fast: ANTHROPIC_API_KEY is not configured in settings or environment.",
                        extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "model_name": model_name},
                        exc_info=True,
                    )
                    raise ConfigurationError(
                        message="Fail-Fast: ANTHROPIC_API_KEY is not configured in settings or environment.",
                        details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                    )
            case "litellm" | _:
                pass
        return resolved_api_key

    @staticmethod
    def create_provider(
        provider_type: str,
        model_name: str,
        context: Any = None,
        organization_id: str | None = None,
        usage_service: UsageService | None = None,
        limits: dict[str, int] | None = None,
        api_key: str | None = None,
        config: LLMProviderConfig | None = None,
        tools: Sequence[Any] | None = None,
        enable_grounding: bool = False,
    ) -> LLMProvider:
        """Create a configured LLMProvider instance from explicit parameters or LLMProviderConfig.

        Args:
            provider_type: Provider type key (specifically 'vertex_ai', 'ai_studio', 'openai', 'anthropic', 'litellm', 'mock').
            model_name: Model identifier.
            context: Optional execution context object.
            organization_id: Organization ID for usage tracking.
            usage_service: Usage service instance for telemetry.
            limits: Explicit usage limits mapping (tpm, rpm).
            api_key: Explicit API key override for ad-hoc testing.
            config: Strict database-driven provider configuration object.
            tools: Optional sequence of tool definitions to validate grounding capabilities.
            enable_grounding: Explicit flag indicating whether grounding is requested.

        Returns:
            Configured LLMProvider instance.

        Raises:
            ConfigurationError: If configuration is invalid, credentials are missing, or grounding is unsupported (ErrorCodes.CONFIGURATION_ERROR, ErrorCodes.CAPABILITY_NOT_SUPPORTED).
            ServiceUnavailableError: If the provider is disabled in configuration (ErrorCodes.SERVICE_DISABLED).
        """
        provider_mod: Any = None
        active_get_settings = get_settings
        active_mock_provider: type[MockProvider] = MockProvider
        if "backend_v2.llm.provider" in sys.modules:
            provider_mod = sys.modules["backend_v2.llm.provider"]
            if get_settings is _ORIG_GET_SETTINGS and "get_settings" in dir(provider_mod):
                active_get_settings = provider_mod.get_settings
            if MockProvider is _ORIG_MOCK_PROVIDER:
                active_mock_provider = _safe_static_getattr(provider_mod, "MockProvider", MockProvider)

        settings = active_get_settings()

        if config is not None:
            LLMFactory._validate_config_and_grounding(
                config=config,
                tools=tools,
                enable_grounding=enable_grounding,
            )
            provider_type = config.provider
            model_name = config.model_name
            limits = LLMFactory._resolve_config_limits(config=config, limits=limits)
            if config.api_key:
                api_key = config.api_key

        mock_model_name = "mock"
        if model_name:
            mock_model_name = model_name

        if settings.use_mock_llm:
            logger.warning(
                "[LLMFactory] Global USE_MOCK_LLM=True. Overriding request for '%s' -> MockProvider.", provider_type
            )
            return active_mock_provider(
                model_name=mock_model_name,
                usage_service=usage_service,
                organization_id=organization_id,
            )

        if provider_type in ("mock", "mock_llm_99"):
            return active_mock_provider(
                model_name=mock_model_name,
                usage_service=usage_service,
                organization_id=organization_id,
            )

        if not model_name:
            logger.error(
                "[LLMFactory] %s: Model name is required for LLMProvider creation.",
                ErrorCodes.CONFIGURATION_ERROR.name,
                exc_info=True,
            )
            raise ConfigurationError(
                message="Model name is required for LLMProvider creation.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        resolved_api_key = LLMFactory._resolve_provider_api_key(
            provider_type=provider_type,
            model_name=model_name,
            api_key=api_key,
            settings=settings,
        )

        active_litellm_provider_cls = _safe_static_getattr(provider_mod, "LiteLLMProvider", None)
        if active_litellm_provider_cls is None:
            logger.error(
                "[LLMFactory] %s: LiteLLMProvider class is not registered in provider module.",
                ErrorCodes.CONFIGURATION_ERROR.name,
                exc_info=True,
            )
            raise ConfigurationError(
                message="LiteLLMProvider class is not registered in provider module.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        supports_grounding = False
        if config is not None:
            supports_grounding = config.supports_grounding

        res: LLMProvider = active_litellm_provider_cls(
            model_name=model_name,
            api_key=resolved_api_key,
            settings=settings,
            usage_service=usage_service,
            organization_id=organization_id,
            limits=limits,
            supports_grounding=supports_grounding,
            config=config,
        )
        return res
