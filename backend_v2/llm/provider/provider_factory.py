"""LLMFactory for instantiating configured LLMProvider implementations."""

import logging
import sys
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
from backend_v2.settings import get_settings

__all__ = [
    "LLMFactory",
]

logger = logging.getLogger(__name__)

_ORIG_GET_SETTINGS = get_settings
_ORIG_MOCK_PROVIDER = MockProvider


# Phase 2, Step 1: Relocate LLMFactory and resolve provider dependencies dynamically
class LLMFactory:
    """Factory class to instantiate the appropriate LLMProvider based on configuration."""

    @staticmethod
    def create_provider(
        provider_type: str,
        model_name: str,
        context: dict[str, Any] | Any | None = None,
        organization_id: str | None = None,
        usage_service: UsageService | None = None,
        limits: dict[str, int] | None = None,
        api_key: str | None = None,
        config: LLMProviderConfig | None = None,
        **kwargs: Any,
    ) -> LLMProvider:
        """Factory method to create an LLM Provider instance.

        Args:
            provider_type: Type key (e.g. 'litellm', 'mock').
            model_name: Model identifier.
            context: Additional context or settings.
            organization_id: Organization ID for tracking.
            usage_service: Usage service instance.
            limits: Usage limits (tpm, rpm).
            api_key: Explicit API Key override (e.g. for ad-hoc testing).
            config: Strict configuration object (Database-Driven).
            **kwargs: Additional arguments.

        Returns:
            Configured provider instance.

        Raises:
            ConfigurationError: If provider configuration is invalid or grounding is requested but not supported.
            ServiceUnavailableError: If the provider is disabled.
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

        # Resolve Configuration Source
        # If 'config' is passed, it is the Authority.
        if config:
            provider_type = config.provider
            model_name = config.model_name
            # If Config says "is_active=False", we should have caught this upstream,
            # but we can enforce it here too as a fail-safe.
            if not config.is_active:
                logger.error(
                    "[LLMFactory] %s: Provider '%s' is disabled in configuration.",
                    ErrorCodes.SERVICE_DISABLED.name,
                    model_name,
                )
                raise ServiceUnavailableError(
                    message=f"Provider '{model_name}' is disabled in configuration.",
                    details={"error_code": ErrorCodes.SERVICE_DISABLED.value},
                )

            # Resolve Limits from Config
            if not limits:
                limits = {}
            if config.tpm_limit > 0:
                limits["tpm"] = config.tpm_limit
            if config.rpm_limit > 0:
                limits["rpm"] = config.rpm_limit

            # Resolve API Key
            if config.api_key:
                api_key = config.api_key

            # Check Grounding Capability (Strict Mode: Fail Fast)
            # If caller requests grounding, but config says NO, we RAISE ERROR.
            # We do NOT fallback to non-grounded generation.
            tools = []
            if "tools" in kwargs:
                tools = kwargs["tools"]
            enable_grounding = False
            if "enable_grounding" in kwargs:
                enable_grounding = kwargs["enable_grounding"]

            # Check for Google Search tool or explicit flag
            has_search_intent = enable_grounding or (tools and any("google_search" in str(t) for t in tools))

            if has_search_intent:
                if not config.supports_grounding:
                    msg = (
                        f"Grounding/Search requested for '{model_name}' "
                        "but provider config 'supports_grounding' is False."
                    )
                    logger.error("[LLMFactory] %s: %s", ErrorCodes.CAPABILITY_NOT_SUPPORTED.name, msg)
                raise ConfigurationError(
                    message=msg,
                    details={"error_code": ErrorCodes.CAPABILITY_NOT_SUPPORTED.value},
                )

        # STRICT EXECUTION AUTHORITY (Jan 19 Update):
        # GLOBAL SAFETY: If 'settings.use_mock_llm' is True, we FORCE the MockProvider.
        # This guarantees that 'run_mock.bat' implies 100% offline mode, regardless of
        # what provider specific agents request (e.g. 'vertex_ai').
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

        # STRICT CONFIGURATION:
        # If not in global mock mode, we DO NOT allow 'mock' to be implicitly selected
        # unless explicitly requested. If 'vertex_ai' is requested, we get Vertex (or fail).
        if provider_type in ("mock", "mock_llm_99"):
            return active_mock_provider(
                model_name=mock_model_name,
                usage_service=usage_service,
                organization_id=organization_id,
            )

        if not model_name:
            logger.error(
                "[LLMFactory] %s: Model name is required for LLMProvider creation.", ErrorCodes.CONFIGURATION_ERROR.name
            )
            raise ConfigurationError(
                message="Model name is required for LLMProvider creation.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        resolved_api_key = api_key
        match provider_type.lower():
            case LLMProviderName.VERTEX_AI.value | "vertex_ai":
                # Vertex AI authenticates via GCP Application Default Credentials backed by service-account.json
                resolved_api_key = None
            case LLMProviderName.AI_STUDIO.value | "ai_studio":
                resolved_api_key = resolved_api_key or settings.google_api_key
                if not resolved_api_key:
                    logger.error(
                        "Fail-Fast: GEMINI_API_KEY / GOOGLE_API_KEY is not configured in settings or environment.",
                        extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "model_name": model_name},
                    )
                    raise ConfigurationError(
                        message=(
                            "Fail-Fast: GEMINI_API_KEY / GOOGLE_API_KEY is not configured in settings or environment."
                        ),
                        details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                    )
            case LLMProviderName.OPENAI.value | "openai":
                resolved_api_key = resolved_api_key or settings.openai_api_key
                if not resolved_api_key:
                    logger.error(
                        "Fail-Fast: OPENAI_API_KEY is not configured in settings or environment.",
                        extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "model_name": model_name},
                    )
                    raise ConfigurationError(
                        message="Fail-Fast: OPENAI_API_KEY is not configured in settings or environment.",
                        details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                    )
            case LLMProviderName.ANTHROPIC.value | "anthropic":
                resolved_api_key = resolved_api_key or settings.anthropic_api_key
                if not resolved_api_key:
                    logger.error(
                        "Fail-Fast: ANTHROPIC_API_KEY is not configured in settings or environment.",
                        extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "model_name": model_name},
                    )
                    raise ConfigurationError(
                        message="Fail-Fast: ANTHROPIC_API_KEY is not configured in settings or environment.",
                        details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                    )
            case "litellm":
                pass
            case _:
                pass

        active_litellm_provider_cls = _safe_static_getattr(provider_mod, "LiteLLMProvider", None)
        if active_litellm_provider_cls is None:
            logger.error(
                "[LLMFactory] %s: LiteLLMProvider class is not registered in provider module.",
                ErrorCodes.CONFIGURATION_ERROR.name,
            )
            raise ConfigurationError(
                message="LiteLLMProvider class is not registered in provider module.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        res: LLMProvider = active_litellm_provider_cls(
            model_name=model_name,
            api_key=resolved_api_key,
            settings=settings,
            usage_service=usage_service,
            organization_id=organization_id,
            limits=limits,
            supports_grounding=config.supports_grounding if config else False,
            config=config,
        )
        return res
