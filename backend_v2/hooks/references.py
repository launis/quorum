"""Reference management hooks for bibliography generation."""

from __future__ import annotations

import json
import logging
from typing import Any

from backend_v2.core.hook_registry import hook_registry
from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)


def generate_bibliography(text_dump: str, knowledge_base: dict[str, Any] | None) -> list[Any]:
    """Scan the provided text dump for references using the ReferenceManager.

    Supports "advanced scan" which detects both explicit citations (e.g. "Author 2020")
    and implicit conceptual links.

    Args:
        text_dump (str): The full text content to scan (e.g. serialized state).
        knowledge_base (Dict[str, Any]): The knowledge base structure containing references and concepts.

    Returns:
        List[BibliographyItem]: A list of unique reference domain objects found in the text.
    """
    try:
        # Stubbed implementation of ReferenceManager (Not ported to V2)
        refs: list[dict[str, Any]] = [
            {
                "source_id": "ref_mock_stub",
                "title": "Mock Reference for Workflow Engine Testing",
                "snippet": "Stubbed citation due to ReferenceManager not being migrated yet.",
                "url": None,
            }
        ]

        logger.debug(f"[ReferenceHook] Scan complete. Found {len(refs)} unique references.")
        return refs

    except AppException:
        raise
    except Exception as e:
        error_code = ErrorCodes.CITATION_PARSING_FAILED
        logger.error(f"[ReferenceHook] {error_code.name}: Bibliography generation failed: {e}", exc_info=True)
        raise AppException(
            message=f"Bibliography generation failed: {e}", status_code=500, details={"error_code": error_code}
        ) from e


@hook_registry.register(name="generate_bibliography")
async def generate_bibliography_hook(data: dict[str, Any], repository: Any = None) -> dict[str, Any]:
    """Wrap generate_bibliography and inject its results."""
    logger.debug("[ReferenceHook] Running generate_bibliography_hook...")

    if not data:
        return {}

    try:
        text_dump = ""

        inputs = data.get("inputs")

        if inputs:
            for val in inputs.values():
                text = str(val) if val else ""
                text_dump += text + "\n"

        step_coach = data.get("step_coach")
        if step_coach:
            if isinstance(step_coach, dict):
                text_dump += json.dumps(step_coach, ensure_ascii=False)
            elif hasattr(step_coach, "model_dump"):
                text_dump += json.dumps(step_coach.model_dump(mode="json"), ensure_ascii=False)

        if not text_dump.strip():
            logger.warning("[ReferenceHook] No text to scan.")
            return {}

        knowledge_base = data.get("knowledge_base")

        # 3. Generate References
        # This might raise REFERENCES_GENERATION_FAILED (AppException)
        generated_references: list[Any] = generate_bibliography(text_dump, knowledge_base)

        # 4. Map to Domain Models
        items = generated_references

        # We can just use a raw dict output instead of wrapping in Any
        result = {"references": items}

        logger.debug(f"[ReferenceHook] Generated {len(items)} references.")
        delta: dict[str, Any] = {"bibliography_result": result}

        if "knowledge_base" not in data:
            delta["knowledge_base"] = knowledge_base

        return delta

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
