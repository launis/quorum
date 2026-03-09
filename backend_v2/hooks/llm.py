"""LLM hooks for configuring model providers and context."""

import logging
from typing import Any

from backend_v2.core.hook_registry import hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)


@hook_registry.register(name="configure_llm_context")
def configure_llm_context_hook(data: dict[str, Any]) -> dict[str, Any]:
    """Workflow Data wrapper for configure_llm_context.

    Resolve the LLM provider configuration based on the 'model_strategy' in context.
    Ensure that the correct model (e.g. Gemini 2.0 Flash) is selected for the current step.

    Logic:
    1. Check 'model_strategy' availability.
    2. Delegate resolution to LLMClient Strategy Factory.
    3. Inject 'llm_config' into context for downstream usage (e.g. by BaseAgent).

    Args:
        data (dict): Current workflow data.

    Returns:
        dict: Updated data with 'llm_config'.

    Raises:
        AppException: If configuration is invalid or missing.
    """
    logger.debug("[LLMHook] Running configure_llm_context_hook...")

    if not data:
        return {}

    # 1. Retrieve Context Variables
    # If no context, nothing to configure, but unusual.
    ctx = data

    # 2. Get Strategy (SSOT)
    # We no longer rely on 'step.config' (which violated SSOT).
    # Instead, we look up the target strategy from the workflow's default_model_mapping,
    # or fallback to the system's global default.
    step_id = ctx.get("step_id", "unknown_agent")

    # Since hooks don't easily have 'repository' injected via parameters,
    # we can try to find workflow mapping in state or resolve using registry singleton in real time.
    # However, to avoid expensive DB calls in pre-hooks, we use the System Config's default strategy.

    settings = get_settings()

    # We resolve the strategy. If a workflow default_model_mapping was injected into ctx, we could use it.
    # But for strict SSOT, we just use the system default unless explicitly overridden in the execution context.
    model_strategy = settings.default_model_strategy or "fast"

    # Future SSOT enhancement: If we need step-specific overrides, the Engine should pass the
    # WorkflowDefinition's 'default_model_mapping' dictionary into 'state.context_variables'
    # so we can do: model_strategy = ctx.get("workflow_model_mapping", {}).get(step_id, model_strategy)

    if "workflow_model_mapping" in ctx:
        model_strategy = ctx["workflow_model_mapping"].get(step_id, model_strategy)

    # 3. Resolve Provider & Model via SSOT Strategy Factory
    try:
        import asyncio

        # Factory method is async. Pre-hooks run synchronously in the current engine,
        # so we must handle the event loop carefully. If configure_llm_context
        # remains synchronous, we use asyncio.run or retrieve settings synchronously.
        # Given it's a hook, let's adapt it safely:

        # In a perfect refactor, hooks would be async. However, since they might be sync:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Standard async runtime (e.g., FastAPI) - this hook should theoretically be async.
            # If the engine wraps this synchronously, this will fail. We'll use a direct fetch
            # avoiding the async API if we are inside a sync hook execution.
            from backend_v2.database.repository import UnifiedWorkflowRepository

            UnifiedWorkflowRepository()  # type: ignore

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

        from backend_v2.models.llm import LLMProviderConfig, ModelRegistryConfig

        from backend_v2.exceptions import ConfigurationError
        from backend_v2.utils.pydantic_utils import inflate

        raw_registry = getattr(settings, "model_registry", {})
        if not raw_registry:
            raise ConfigurationError("System config 'model_registry' is missing.")

        registry = inflate(raw_registry, ModelRegistryConfig)
        if not registry or not registry.models:
            raise ConfigurationError("ModelRegistry is corrupt.")

        # V1/Simple: We assume 'google' as primary provider
        provider = ctx.get("provider_id", "google")

        provider_models = registry.models.get(provider)
        if not provider_models:
            raise ConfigurationError(f"Provider '{provider}' not found in registry.")

        target_strategy = provider_models.get(model_strategy)

        if not target_strategy:
            raise ConfigurationError(
                message=f"Strategy '{model_strategy}' not found for provider '{provider}'.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
            )

        llm_config = LLMProviderConfig(
            id=f"{provider}/{model_strategy}",
            provider=provider,
            model_name=getattr(target_strategy, "model_name", ""),
            api_key=getattr(target_strategy, "api_key", ""),
            temperature=getattr(target_strategy, "temperature", 0.0),
            tpm_limit=getattr(target_strategy, "tpm_limit", 0),
            rpm_limit=getattr(target_strategy, "rpm_limit", 0),
            default_max_tokens=getattr(target_strategy, "max_tokens", 0),
            supports_grounding=getattr(target_strategy, "supports_grounding", False),
        )

        # 4. Inject
        logger.info(
            f"[LLMHook] Injected strictly parsed LLM Config for {step_id} "
            f"(Strategy: {model_strategy}, Model: {llm_config.model_name})"
        )

        return {"llm_config": llm_config}

    except Exception as e:
        error_code = ErrorCodes.CONFIGURATION_ERROR
        # Distinguish strictly raised ConfigErrors vs generic exceptions
        if isinstance(e, AppException):
            logger.error(f"[LLMHook] {e.error_code}: {e}")
            raise

        logger.error(f"[LLMHook] Failed to resolve LLM config: {e}", exc_info=True)
        # Fail Fast
        raise AppException(
            message=f"LLM Hook failed: {e}", status_code=500, details={"error_code": error_code, "cause": str(e)}
        ) from e
