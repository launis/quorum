"""Reference management hooks for bibliography generation."""

import json
import logging
from typing import TYPE_CHECKING, Any, Dict, List

from backend.exceptions import AppException
from backend.models.domain import BibliographyItem, BibliographyResult
from backend.services.reference_manager import ReferenceManager

# TYPE_CHECKING block for circular dependencies if needed
if TYPE_CHECKING:
    from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)


def generate_bibliography(text_dump: str, knowledge_base: Dict[str, Any]) -> List[Dict[str, Any]]:
    """HOOK: generate_bibliography.

    Scans the provided text dump for references using the ReferenceManager.
    Supports "advanced scan" which detects both explicit citations (e.g. "Author 2020")
    and implicit conceptual links.

    Args:
        text_dump (str): The full text content to scan (e.g. serialized state).
        knowledge_base (Dict[str, Any]): The knowledge base structure containing references and concepts.

    Returns:
        List[Dict[str, Any]]: A list of unique reference data objects found in the text.
    """
    if not knowledge_base:
        return []

    try:
        # Initialize ReferenceManager with the provided KB
        rm = ReferenceManager(knowledge_base)

        # Use advanced scan to find both direct citations and concept-linked citations
        # keys=citations, values=reference_data
        references_map = rm.advanced_scan(text_dump)

        # Return the reference data objects (values), sorted by title for consistency
        # We assume reference data has a 'title' field, or we use the key
        unique_refs = list(references_map.values())
        
        # Sort by title if available, else by source_id
        unique_refs.sort(key=lambda x: str(x.get("title", "") or x.get("source_id", "")))

        logger.debug(f"[ReferenceHook] Scan complete. Found {len(unique_refs)} unique references.")
        return unique_refs

    except Exception as e:
        error_code = "REFERENCES_GENERATION_FAILED"
        logger.error(f"[ReferenceHook] {error_code}: {e}", exc_info=True)
        raise AppException(
            message=f"Bibliography generation failed: {e}",
            status_code=500,
            details={"error_code": error_code}
        ) from e


def generate_bibliography_hook(state) -> "WorkflowState":
    """WorkflowState wrapper for generate_bibliography."""
    logger.debug("[ReferenceHook] Running generate_bibliography_hook...")
    
    try:
        # 1. Extract Text
        text_dump = ""
        inputs = state.context_variables.get("inputs", {})
        if isinstance(inputs, dict):
            for field in ["history_text", "product_text", "reflection_text"]:
                text = inputs.get(field, "") or ""
                text_dump += str(text) + "\n"

        step_coach = getattr(state, "step_coach", None)
        if step_coach and hasattr(step_coach, "model_dump"):
            text_dump += json.dumps(step_coach.model_dump(), ensure_ascii=False)

        if not text_dump.strip():
            logger.warning("[ReferenceHook] No text to scan.")
            return state

        # 2. Get Knowledge Base
        knowledge_base = state.context_variables.get("knowledge_base")
        if knowledge_base is None:
            knowledge_base = {"references": [], "concepts": {}}

        # 3. Generate References
        # This might raise REFERENCES_GENERATION_FAILED (AppException)
        references = generate_bibliography(text_dump, knowledge_base)

        # 4. Map to Domain Models
        from backend.models.domain import BibliographyItem, BibliographyResult
        
        items: List[BibliographyItem] = []
        for ref in references:
            # We enforce strict typing here. 'ref' is a dict from generate_bibliography
            if isinstance(ref, dict):
                items.append(BibliographyItem(
                    source_id=str(ref.get("source_id", "unknown")),
                    title=str(ref.get("title", "Untitled")),
                    url=ref.get("url"),
                    snippet=ref.get("snippet")
                ))

        result = BibliographyResult(references=items)

        # 5. Update State
        new_context = state.context_variables.copy()
        new_context["bibliography_result"] = result
        new_context["bibliography"] = [r.get("title", "Unknown") for r in references] # Legacy list of strings

        logger.debug(f"[ReferenceHook] Generated {len(items)} references.")
        return state.model_copy(update={"context_variables": new_context})

    except AppException:
        # Re-raise AppExceptions directly (Fail Fast)
        raise
    except Exception as e:
        # Catch unexpected errors in the hook wrapper
        error_code = "REFERENCES_HOOK_FAILED"
        logger.error(f"[ReferenceHook] {error_code}: {e}", exc_info=True)
        raise AppException(
            message=f"Bibliography hook failed: {e}",
            status_code=500,
            details={"error_code": error_code}
        ) from e
