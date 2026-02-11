"""Validation hooks for structural integrity checks."""

import logging

from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)


def verify_structure(state: WorkflowState) -> WorkflowState:
    """HOOK: verify_structure.

    Pre-execution validation check to ensure inputs ('history_text', 'product_text', 'reflection_text')
    have sufficient content length for meaningful analysis.
    Adds warnings to 'aux_data.structural_warnings' if checks fail.

    Min Length: 100 chars.

    Args:
        state (WorkflowState): Current state.

    Returns:
        WorkflowState: Updated state with warnings if applicable.

    """
    logger.debug("[ValidationHook] Running structural inputs check...")

    # Minimum char limits
    MIN_CHARS = 100

    warnings = []

    inputs = state.context_variables.get("inputs", {})
    if not isinstance(inputs, dict):
        inputs = {}

    for key in ["history_text", "product_text", "reflection_text"]:
        text = inputs.get(key, "")
        if not text or len(text) < MIN_CHARS:
            warnings.append(
                f"Input '{key}' is too short ({len(text) if text else 0} chars). Analysis quality may suffer."
            )

    
    try:
        from backend.models.domain import ValidationResult
        result = ValidationResult(
            is_valid=len(warnings) == 0,
            errors=warnings
        )
    except ImportError:
        logger.error("[ValidationHook] Could not import ValidationResult")
        return state

    new_context = state.context_variables.copy()
    new_context["validation_result"] = result
    
    # Legacy support
    if warnings:
        msg = f"[ValidationHook] Structural Checks Failed: {warnings}"
        logger.error(msg)
        # Note: Validation failures used to raise ValueError.
        # Strict Mode often prefers returning error state over crashing if possible,
        # but for pre-validation, stopping execution is correct.
        # We will still raise ValueError if invalid, BUT we store the result first.
        # However, if we raise, we can't return state. 
        # Strategy: Store result, THEN raise. 
        # But raising stops flow, so state isn't saved unless engine handles it.
        # The engine generally catches exceptions.
        # Let's attach the result to the exception details if possible, or just raise.
        
        # To persist the validation failure in state for history, we'd need to NOT raise
        # and let the engine/next step handle "is_valid=False".
        # But 'verify_structure' is a Pre-Hook. If it fails, step shouldn't run.
        # So raising is correct for control flow.
        raise ValueError(msg)
    else:
        logger.debug("[ValidationHook] checks passed.")

    return state.model_copy(update={"context_variables": new_context})
