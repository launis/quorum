"""Reference management hooks for bibliography generation."""

import logging
from typing import Any

from backend.services.reference_manager import ReferenceManager

logger = logging.getLogger(__name__)


def generate_bibliography(text_dump: str, knowledge_base: dict[str, Any]) -> list[str]:
    """HOOK: generate_bibliography.

    Scans the provided text dump for references using the ReferenceManager.
    Supports "advanced scan" which detects both explicit citations (e.g. "Author 2020")
    and implicit conceptual links.

    Args:
        text_dump (str): The full text content to scan (e.g. serialized state).
        knowledge_base (Dict[str, Any]): The knowledge base structure containing references and concepts.

    Returns:
        List[str]: A sorted list of unique, full bibliographic reference strings found in the text.

    """
    if not knowledge_base:
        return []

    try:
        # Initialize ReferenceManager with the provided KB
        # Note: ReferenceManager expects {"references": [...], "concepts": {...}}
        # CoachAgent.knowledge_base follows this structure.
        rm = ReferenceManager(knowledge_base)

        # Use advanced scan to find both direct citations and concept-linked citations
        references_map = rm.advanced_scan(text_dump)

        # We return just the keys (Full References) sorted
        formatted_list = sorted(list(references_map.keys()))

        logger.info(f"[ReferenceHook] Scan complete. Found {len(formatted_list)} unique references.")
        return formatted_list

    except Exception as e:
        logger.error(f"[ReferenceHook] Bibliography generation failed: {e}")
        return []


# --- WORKFLOW STATE WRAPPERS (for HOOK_MAPPING compatibility) ---

def generate_bibliography_hook(state) -> "WorkflowState":
    """WorkflowState wrapper for generate_bibliography.
    
    Extracts text from state, generates bibliography, and stores in aux_data.
    """
    logger.info("[ReferenceHook] Running generate_bibliography_hook...")
    
    # Try to get text content from various sources
    text_dump = ""
    
    if hasattr(state, "inputs") and state.inputs:
        for field in ["history_text", "product_text", "reflection_text"]:
            text = getattr(state.inputs, field, "") or ""
            text_dump += text + "\n"
    
    # Also include coach findings if available
    if hasattr(state, "step_coach") and state.step_coach:
        if hasattr(state.step_coach, "model_dump"):
            import json
            text_dump += json.dumps(state.step_coach.model_dump(), ensure_ascii=False)
    
    if not text_dump.strip():
        logger.warning("[ReferenceHook] No text to scan for references.")
        return state
    
    # Default knowledge base structure
    knowledge_base = state.aux_data.get("knowledge_base", {
        "references": [],
        "concepts": {}
    })
    
    references = generate_bibliography(text_dump, knowledge_base)
    state.aux_data["bibliography"] = references
    
    logger.info(f"[ReferenceHook] Generated {len(references)} references.")
    
    return state
