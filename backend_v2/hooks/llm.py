"""LLM hooks for configuring model providers and context."""

import asyncio
import logging
import uuid
from typing import Any

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
        AppException: If configuration is invalid or missing.
    """
    logger.debug("[LLMHook] Running configure_llm_context_hook...")

    if not state:
        return HookResult(success=True, state_delta=HookDeltaDTO(delta={}))


    # 2. Get Strategy (SSOT)
    if not state.step_id:
        msg = "state.step_id is strictly required for LLM context configuration."
        logger.error("[LLMHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    step_id = state.step_id
    settings = get_settings()

    if not settings.default_model_strategy:
        msg = "settings.default_model_strategy is strictly required but missing."
        logger.error("[LLMHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})

    model_strategy = settings.default_model_strategy

    # 3. Resolve Provider & Model via SSOT Strategy Factory
    try:
        # Factory method is async. Pre-hooks run synchronously in the current engine,
        # so we must handle the event loop carefully. If configure_llm_context
        # remains synchronous, we use asyncio.run or retrieve settings synchronously.
        # Given it's a hook, let's adapt it safely:

        # In a perfect refactor, hooks would be async. However, since they might be sync:
        try:
            loop = asyncio.get_running_loop()
            is_running = loop.is_running()
        except RuntimeError:
            is_running = False

        if is_running:
            # Standard async runtime (e.g., FastAPI) - this hook should theoretically be async.
            # If the engine wraps this synchronously, this will fail. We'll use a direct fetch
            # avoiding the async API if we are inside a sync hook execution.

            # Since the hook is `def configure...` and NOT `async def configure...`,
            # we must execute the async factory cleanly.
            # Usually the engine awaits async hooks if they are defined as async,
            # but if it enforces sync execution, we might need a workaround.
            # Let's assume for this transition we extract the logic synchronously
            # or the engine permits async if we change the signature.
            # To be safe without breaking the BaseAgent hook runner, we will emulate
            # what the factory does here synchronously using the cached settings if possible,
            # but ideally we convert this hook to async in the future.

            # For now, we perform local resolution using identical Pydantic models.
            pass

        if not settings.model_registry:
            raise ConfigurationError("System config 'model_registry' is missing.")
        raw_registry = settings.model_registry

        registry = inflate(raw_registry, SystemConfigModelRegistry)
        if not registry or not registry.tier_definitions:
            raise ConfigurationError("ModelRegistry is corrupt.")

        # V2: Option A Sovereign Model Stack direct mapping tier -> ModelProfile
        try:
            tier_enum = (
                model_strategy
                if isinstance(model_strategy, CognitiveTier)
                else CognitiveTier(str(model_strategy).lower())
            )
        except ValueError:
            tier_enum = None

        if tier_enum is None or tier_enum not in registry.tier_definitions:
            raise ConfigurationError(
                message=f"Strategy '{model_strategy}' not found in registry.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )
        target_strategy = registry.tier_definitions[tier_enum]

        if target_strategy.tpm_limit is None or target_strategy.rpm_limit is None:
            raise ConfigurationError(
                message=(
                    f"Model Profile for strategy '{model_strategy}' must explicitly define "
                    "tpm_limit and rpm_limit. Use 0 for unlimited."
                ),
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        config_data: dict[str, Any] = {
            "id": f"llm_{uuid.uuid4().hex[:8]}",
            "provider": target_strategy.provider,
            "model_name": target_strategy.model_name,
            "api_key": target_strategy.api_key,
            "tpm_limit": target_strategy.tpm_limit,
            "rpm_limit": target_strategy.rpm_limit,
            "default_max_tokens": target_strategy.max_tokens,
            "supports_grounding": target_strategy.supports_grounding,
        }

        if target_strategy.temperature is not None:
            config_data["temperature"] = target_strategy.temperature

        llm_config = LLMProviderConfig.model_validate(config_data)

        # 4. Inject
        logger.info(
            "[LLMHook] Injected strictly parsed LLM Config for %s (Strategy: %s, Model: %s)",
            step_id,
            model_strategy,
            llm_config.model_name,
        )

        return HookResult(
            success=True, state_delta=HookDeltaDTO(delta={"llm_config": llm_config.model_dump(mode="json")})
        )

    except Exception as e:
        # Distinguish strictly raised ConfigErrors vs generic exceptions
        if isinstance(e, AppException):
            logger.error("[LLMHook] %s: %s", e.error_code, e)
            raise

        logger.error("[LLMHook] Failed to resolve LLM config: %s", e, exc_info=True)
        raise AppException(
            message=f"LLM Hook failed: {e}",
            status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value, "cause": str(e)},
        ) from e
