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
    logger.info("[ValidationHook] Running structural inputs check...")

    # Minimum char limits
    MIN_CHARS = 100

    warnings = []

    for key in ["history_text", "product_text", "reflection_text"]:
        text = getattr(state.inputs, key, "")
        if not text or len(text) < MIN_CHARS:
            warnings.append(
                f"Input '{key}' is too short ({len(text) if text else 0} chars). Analysis quality may suffer."
            )

    if warnings:
        logger.warning(f"[ValidationHook] Structural Warnings: {warnings}")
        state.aux_data["structural_warnings"] = warnings
    else:
        logger.info("[ValidationHook] checks passed.")

    return state
