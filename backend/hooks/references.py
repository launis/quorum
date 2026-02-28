"""Reference management hooks for bibliography generation."""

from __future__ import annotations

import json
import logging
from typing import Any

from backend.exceptions import AppException, ErrorCodes
from backend.models.domain import BibliographyItem, BibliographyResult
from backend.models.domain.inputs import WorkflowInputs
from backend.models.state import WorkflowState
from backend.services.reference_manager import ReferenceManager
from backend.utils.pydantic_utils import inflate

logger = logging.getLogger(__name__)


def generate_bibliography(text_dump: str, knowledge_base: dict[str, Any]) -> list[BibliographyItem]:
    """Scan the provided text dump for references using the ReferenceManager.

    Supports "advanced scan" which detects both explicit citations (e.g. "Author 2020")
    and implicit conceptual links.

    Args:
        text_dump (str): The full text content to scan (e.g. serialized state).
        knowledge_base (Dict[str, Any]): The knowledge base structure containing references and concepts.

    Returns:
        List[BibliographyItem]: A list of unique reference domain objects found in the text.
    """
    if not knowledge_base:
        error_code = ErrorCodes.SERVICE_DEPENDENCY_MISSING
        logger.error(f"[ReferenceHook] {error_code.name}: generate_bibliography called with an empty knowledge_base.", exc_info=True)
        raise AppException(
            message="generate_bibliography called with an empty knowledge_base payload.",
            status_code=500,
            details={"error_code": error_code}
        )

    try:
        # Initialize ReferenceManager with the provided KB
        rm = ReferenceManager(knowledge_base)

        # Use advanced scan to find both direct citations and concept-linked citations
        # keys=citations, values=reference_data
        report = rm.advanced_scan(text_dump)

        # CitationReport contains a relevance_map: { "Full Reference String": ["Reason 1", "Reason 2"] }
        # We need to convert this back to a list of BibliographyItems for the hook contract.
        unique_refs: list[BibliographyItem] = []
        for full_text, reasons in report.relevance_map.items():
            unique_refs.append(
                BibliographyItem(
                    # Generate a stable ID based on content since ReferenceManager doesn't persist IDs
                    source_id=f"ref_{abs(hash(full_text)):x}",
                    title=full_text,
                    snippet="; ".join(reasons),
                    url=None,
                )
            )

        # Sort by title
        unique_refs.sort(key=lambda x: x.title or "")

        logger.debug(f"[ReferenceHook] Scan complete. Found {len(unique_refs)} unique references.")
        return unique_refs

    except AppException:
        raise
    except Exception as e:
        error_code = ErrorCodes.CITATION_PARSING_FAILED
        logger.error(f"[ReferenceHook] {error_code.name}: Bibliography generation failed: {e}", exc_info=True)
        raise AppException(
            message=f"Bibliography generation failed: {e}", status_code=500, details={"error_code": error_code}
        ) from e


async def generate_bibliography_hook(state, repository: Any = None) -> WorkflowState:
    """Wrap generate_bibliography and inject its results into WorkflowState."""
    logger.debug("[ReferenceHook] Running generate_bibliography_hook...")

    try:
        text_dump = ""
        input_data = state.context_variables.get("inputs")
        inputs = inflate(input_data, WorkflowInputs)

        if inputs:
            for field in ["history_text", "product_text", "reflection_text"]:
                text = getattr(inputs, field) or ""
                text_dump += str(text) + "\n"

        step_coach = state.context_variables.get("step_coach")
        if step_coach and hasattr(step_coach, "model_dump"):
            text_dump += json.dumps(step_coach.model_dump(mode="json"), ensure_ascii=False)

        if not text_dump.strip():
            logger.warning("[ReferenceHook] No text to scan.")
            return state

        knowledge_base = state.context_variables.get("knowledge_base")

        if knowledge_base is None:
            # FAIL FAST: Knowledge Base is a critical dependency for citation generation.
            error_code = ErrorCodes.SERVICE_DEPENDENCY_MISSING
            logger.error(
                f"[ReferenceHook] {error_code.name}: Knowledge Base missing in context.",
                exc_info=True,
            )
            raise AppException(
                message="Knowledge Base missing in ReferenceHook context.",
                status_code=500,
                details={"error_code": error_code},
            )

        # 3. Generate References
        # This might raise REFERENCES_GENERATION_FAILED (AppException)
        generated_references: list[BibliographyItem] = generate_bibliography(text_dump, knowledge_base)

        # 4. Map to Domain Models
        # STRICT TYPING: references is already List[BibliographyItem]
        items = generated_references
        result = BibliographyResult(references=items)

        # 5. Update State
        new_context = state.context_variables.copy()
        new_context["bibliography_result"] = result

        # OPTIONAL: Inject KB back into context to save future lookups?
        if "knowledge_base" not in new_context:
            new_context["knowledge_base"] = knowledge_base

        logger.debug(f"[ReferenceHook] Generated {len(items)} references.")
        return state.model_copy(update={"context_variables": new_context})

    except AppException:
        # Re-raise AppExceptions directly (Fail Fast)
        raise
    except Exception as e:
        # Catch unexpected errors in the hook wrapper
        error_code = ErrorCodes.HOOK_EXECUTION_FAILED
        logger.error(f"[ReferenceHook] {error_code.name}: Hook execution failed: {e}", exc_info=True)
        raise AppException(
            message=f"Bibliography hook failed: {e}", status_code=500, details={"error_code": error_code}
        ) from e
