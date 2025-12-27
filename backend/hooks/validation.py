
import logging
from typing import List, Dict, Any
from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)

def verify_structure(state: WorkflowState) -> WorkflowState:
    """
    HOOK: verify_structure
    Validates that inputs have sufficient content for analysis.
    Used by AnalystAgent.
    """
    logger.info("[ValidationHook] Running structural inputs check...")
    
    # Minimum char limits
    MIN_CHARS = 100 
    
    warnings = []
    
    for key in ["history_text", "product_text", "reflection_text"]:
        text = getattr(state.inputs, key, "")
        if not text or len(text) < MIN_CHARS:
            warnings.append(f"Input '{key}' is too short ({len(text) if text else 0} chars). Analysis quality may suffer.")
            
    if warnings:
        logger.warning(f"[ValidationHook] Structural Warnings: {warnings}")
        state.aux_data['structural_warnings'] = warnings
    else:
        logger.info("[ValidationHook] checks passed.")
        
    return state
