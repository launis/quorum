"""Reference management hooks for bibliography generation."""

import logging
from typing import TYPE_CHECKING, Any

from backend.services.reference_manager import ReferenceManager

if TYPE_CHECKING:
    from backend.models.state import WorkflowState

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

        logger.debug(f"[ReferenceHook] Scan complete. Found {len(formatted_list)} unique references.")
        return formatted_list

    except Exception as e:
        logger.error(f"[ReferenceHook] Bibliography generation failed: {e}")
        return []


# --- WORKFLOW STATE WRAPPERS (for HOOK_MAPPING compatibility) ---


def generate_bibliography_hook(state) -> WorkflowState:
    """WorkflowState wrapper for generate_bibliography.

    Extracts text from state, generates bibliography, and stores in aux_data.
    """
    logger.debug("[ReferenceHook] Running generate_bibliography_hook...")

    # Try to get text content from various sources
    text_dump = ""

    inputs = state.context_variables.get("inputs", {})
    if isinstance(inputs, dict):
        for field in ["history_text", "product_text", "reflection_text"]:
            text = inputs.get(field, "") or ""
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
    # Use config from context if available, else default
    # Note: aux_data is gone, so we check context_variables or default
    knowledge_base = state.context_variables.get("knowledge_base", {"references": [], "concepts": {}})

    references = generate_bibliography(text_dump, knowledge_base)
    
    # Create strictly typed result
    try:
        from backend.models.domain import BibliographyResult, BibliographyItem
        
        items = []
        if references:
            for ref in references:
                if isinstance(ref, dict):
                     items.append(BibliographyItem(
                        source_id=str(ref.get("source_id", "unknown")),
                        title=str(ref.get("title", "Untitled")),
                        url=ref.get("url"),
                        snippet=ref.get("snippet")
                    ))
        
        result = BibliographyResult(references=items)
    except ImportError:
        logger.error("[ReferenceHook] Could not import BibliographyResult")
        return state

    # IMMUTABILITY FIX
    new_context = state.context_variables.copy()
    new_context["bibliography_result"] = result
    
    # Legacy support
    new_context["bibliography"] = references

    logger.debug(f"[ReferenceHook] Generated {len(references)} references.")

    return state.model_copy(update={"context_variables": new_context})
