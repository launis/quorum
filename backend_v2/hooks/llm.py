"""LLM hooks for configuring model providers and context."""

import logging
import uuid

from backend_v2.core.hook_registry import (
    HookDeltaDTO,
    HookDependencies,
    HookResult,
    HookState,
    hook_registry,
)
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.domain.system_config import SystemConfigModelRegistry
from backend_v2.models.enums import CognitiveTier
from backend_v2.models.llm import LLMProviderConfig
from backend_v2.settings import get_settings
from backend_v2.utils.pydantic_utils import inflate

logger = logging.getLogger(__name__)

__all__ = ["configure_llm_context_hook"]


@hook_registry.register(name="configure_llm_context")
def configure_llm_context_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Workflow Data wrapper for configure_llm_context.

    Resolve the LLM provider configuration based on the 'model_strategy' in context.
    Ensure that the correct model (e.g. Gemini 2.0 Flash) is selected for the current step.

    Logic:
    1. Check 'model_strategy' availability.
    2. Delegate resolution to LLMClient Strategy Factory.
    3. Inject 'llm_config' into context for downstream usage (e.g. by BaseAgent).

    Args:
        state: The current execution state of the hook.
        deps: Dependencies required for execution.

    Returns:
        A HookResult containing the 'llm_config' in the state_delta.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if state.step_id is missing, or
            ErrorCodes.CONFIGURATION_ERROR if configuration or strategy resolution fails.
        ConfigurationError: If model_registry is missing, corrupt, or strategy is unmapped.
    """
    logger.debug("[LLMHook] Running configure_llm_context_hook...")

    if not state:
        return HookResult(success=True, state_delta=HookDeltaDTO())

    # 2. Get Strategy (SSOT)
    if not state.step_id:
        msg = "state.step_id is strictly required for LLM context configuration."
        logger.error("[LLMHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    step_id = state.step_id
    settings = get_settings()

    if not settings.default_model_strategy:
        msg = "settings.default_model_strategy is strictly required but missing."
        logger.error("[LLMHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})

    model_strategy = settings.default_model_strategy

    # 3. Resolve Provider & Model via SSOT Strategy Factory
    try:
        # Factory method is async. Pre-hooks run synchronously in the current engine,
        # so we must handle the event loop carefully. If configure_llm_context
        # remains synchronous, we use asyncio.run or retrieve settings synchronously.
        # Given it's a hook, let's adapt it safely:

        if not settings.model_registry:
            msg = "System config 'model_registry' is missing."
            logger.error("[LLMHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
            raise ConfigurationError(msg)
        raw_registry = settings.model_registry

        registry = inflate(raw_registry, SystemConfigModelRegistry)
        if not registry or not registry.tier_definitions:
            msg = "ModelRegistry is corrupt."
            logger.error("[LLMHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
            raise ConfigurationError(msg)

        # V2: Option A Sovereign Model Stack direct mapping tier -> ModelProfile
        try:
            tier_enum = (
                model_strategy
                if isinstance(model_strategy, CognitiveTier)
                else CognitiveTier(str(model_strategy).lower())
            )
        except ValueError as e:
            msg = f"Strategy '{model_strategy}' not found in registry."
            logger.error("[LLMHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
            raise ConfigurationError(
                message=msg,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            ) from e

        if tier_enum not in registry.tier_definitions:
            msg = f"Strategy '{model_strategy}' not found in registry."
            logger.error("[LLMHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
            raise ConfigurationError(
                message=msg,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )
        target_strategy = registry.tier_definitions[tier_enum]

        if target_strategy.tpm_limit is None or target_strategy.rpm_limit is None:
            msg = (
                f"Model Profile for strategy '{model_strategy}' must explicitly define "
                "tpm_limit and rpm_limit. Use 0 for unlimited."
            )
            logger.error("[LLMHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
            raise ConfigurationError(
                message=msg,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        llm_config = LLMProviderConfig(
            id=f"llm_{uuid.uuid4().hex[:8]}",
            provider=target_strategy.provider,
            model_name=target_strategy.model_name,
            api_key=target_strategy.api_key,
            tpm_limit=target_strategy.tpm_limit,
            rpm_limit=target_strategy.rpm_limit,
            default_max_tokens=target_strategy.max_tokens,
            supports_grounding=target_strategy.supports_grounding,
            additional_params=target_strategy.additional_params,
        )
        if target_strategy.temperature is not None:
            llm_config = llm_config.model_copy(update={"temperature": target_strategy.temperature})

        # 4. Inject
        logger.info(
            "[LLMHook] Injected strictly parsed LLM Config for %s (Strategy: %s, Model: %s)",
            step_id,
            model_strategy,
            llm_config.model_name,
        )

        return HookResult(success=True, state_delta=HookDeltaDTO(delta=llm_config))

    except Exception as e:
        # Distinguish strictly raised ConfigErrors vs generic exceptions
        if isinstance(e, AppException):
            logger.error("[LLMHook] %s: %s", e.error_code, e, exc_info=True)
            raise

        logger.error("[LLMHook] Failed to resolve LLM config: %s", e, exc_info=True)
        raise AppException(
            message=f"LLM Hook failed: {e}",
            status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value, "cause": str(e)},
        ) from e
