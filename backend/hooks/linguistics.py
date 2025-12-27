
import logging
import json
from typing import List
from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)

def detect_performative_patterns(state: WorkflowState) -> WorkflowState:
    """
    HOOK: detect_performative_patterns
    Scans input texts (history, product) for performative/filler language patterns.
    Injects a JSON list of matches into 'aux_data.performative_patterns_detected'.
    Used to flag potentially generic or low-quality input text.

    Args:
        state (WorkflowState): Current workflow state.

    Returns:
        WorkflowState: Updated state with detected pattern metadata.
    """
    logger.info("[LinguisticsHook] Running detect_performative_patterns...")
    
    suspect_patterns = [
        "delve into", "tapestry", "comprehensive overview", "rich history",
        "testament to", "underscore the importance", "pivotal role",
        "landscape of", "realm of", "foster a sense of"
    ]
    
    detected = []
    # Scan history and product text
    text_to_scan = (state.inputs.history_text or "") + (state.inputs.product_text or "")
    text_lower = text_to_scan.lower()
    
    for pattern in suspect_patterns:
        if pattern in text_lower:
            detected.append(pattern)
            
    if detected:
        logger.info(f"   [LinguisticsHook] Detected patterns: {detected}")
        state.aux_data['performative_patterns_detected'] = json.dumps(detected)
    else:
        state.aux_data['performative_patterns_detected'] = "[]"
        
    return state
