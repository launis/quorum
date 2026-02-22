"""LLM hooks for configuring model providers and context."""

import logging

from backend.exceptions import AppException, ConfigurationError, ErrorCodes
from backend.models.llm import LLMProviderConfig
from backend.models.state import WorkflowState
from backend.settings import get_settings

logger = logging.getLogger(__name__)


def configure_llm_context(state: WorkflowState) -> WorkflowState:
    """HOOK: configure_llm_context.

    Resolves the LLM provider configuration based on the 'model_strategy' in context.
    Ensures that the correct model (e.g. Gemini 2.0 Flash) is selected for the current step.

    Logic:
    1. Check 'model_strategy' availability.
    2. Validate strategy against allowed configurations.
    3. Inject 'llm_config' into context for downstream usage (e.g. by BaseAgent).

    Args:
        state (WorkflowState): Current workflow state.

    Returns:
        WorkflowState: Updated state with 'llm_config'.

    Raises:
        AppException: If configuration is invalid or missing.
    """
    logger.debug("[LLMHook] Running configure_llm_context...")

    # Strict Enforce: State must be WorkflowState object
    if isinstance(state, dict):
        raise AppException(
            message="LLM Hook received dict state. Strict Pydantic Enforcement Violation.",
            status_code=500,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA},
        )

    # 1. Retrieve Context Variables
    ctx = state.context_variables
    if not ctx:
        # If no context, nothing to configure, but unusual.
        logger.warning("[LLMHook] Empty context variables.")
        return state

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

    # 3. Resolve Provider & Model for Strategy
    try:
        # Example: settings.model_registry is a dict.
        # We assume settings has this attribute as per architecture.
        # If not, we fail fast.
        registry = getattr(settings, "model_registry", {})

        if not isinstance(registry, dict):
            # Should be caught by settings validation, but double check here.
            raise ConfigurationError(f"Settings.model_registry is not a dict: {type(registry)}")

        # For V1/Simple: We assume 'google' as primary provider
        # Future: Could come from context["provider_id"]
        provider = ctx.get("provider_id", "google")

        provider_config = registry.get(provider)

        # Strict Dict Access (Fail Fast if provider not configured)
        if not provider_config:
            raise ConfigurationError(f"Provider '{provider}' not found in registry.")

        if not isinstance(provider_config, dict):
            raise ConfigurationError(f"Invalid provider config type for '{provider}': {type(provider_config)}")

        strategy_config = provider_config.get(model_strategy)

        if not strategy_config:
            # FAIL FAST: Required strategy must exist.
            raise ConfigurationError(
                message=f"Strategy '{model_strategy}' not found for provider '{provider}'.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
            )

        # 4. Construct LLMProviderConfig
        # Validate critical fields
        if "model_name" not in strategy_config:
            raise ConfigurationError(f"Missing 'model_name' in strategy '{model_strategy}'")

        llm_config = LLMProviderConfig(
            id=f"{provider}/{model_strategy}",
            provider=provider,
            model_name=strategy_config.get("model_name"),
            api_key=strategy_config.get("api_key"),  # might be env var resolve
            base_url=strategy_config.get("base_url"),
            temperature=strategy_config.get("temperature", 0.7),
            tpm_limit=strategy_config.get("tpm_limit", 0),
            rpm_limit=strategy_config.get("rpm_limit", 0),
            default_max_tokens=strategy_config.get("max_tokens"),
            vertex_location=strategy_config.get("vertex_location"),
            supports_grounding=strategy_config.get("supports_grounding", False),
            is_active=strategy_config.get("is_active", True),
            additional_params=strategy_config.get("additional_params", {}),
        )

        # 5. Inject
        new_ctx = ctx.copy()
        new_ctx["llm_config"] = llm_config

        logger.info(
            f"[LLMHook] Injected LLM Config for {step_id} (Strategy: {model_strategy}, Model: {llm_config.model_name})"
        )

        return state.model_copy(update={"context_variables": new_ctx})

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
