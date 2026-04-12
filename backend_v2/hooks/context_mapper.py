"""Universal Context Mapper for Dynamic Target Data Dictionaries.

Translates rigid numerical and UUID-based system keys into LLM-understandable
ordinal dictionaries to completely eradicate UUID blindness and Sycophancy
across all output profiles, holistic evaluations, and matrices.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ContextMapper:
    """Builder for translating Target Data IDs into Universal Ordinal Mapping limits."""

    @staticmethod
    def build_ordinal_mapping(target_blocks: list[str], all_blocks: list[Any] | None = None) -> str:
        """Builds a section-level ordinal dictionary for evaluating specific targets."""
        if not target_blocks or "*" in target_blocks:
            return ""

        instruction = "=== TARGET DATA MAPPING & ANTI-SYCOPHANCY MANDATE ===\n"
        instruction += (
            "The raw JSON context uses non-semantic unique IDs. "
            "Below is their ordinal mapping (1, 2, 3...) and ABSOLUTE mathematical bounds:\n"
        )

        all_blocks = all_blocks or []

        for b_idx, block_id in enumerate(target_blocks):
            extrema_str = ""
            for b in all_blocks:
                from backend_v2.models.v2_core import PromptBlock

                if not isinstance(b, PromptBlock):
                    from backend_v2.exceptions import AppException

                    msg = (
                        "Fail-Fast violation: ContextMapper MUST receive strictly typed "
                        "PromptBlock models, not raw dictionaries."
                    )
                    logger.error("[ContextMapper] DATA_CORRUPTION: %s", msg, exc_info=True)
                    raise AppException(message="Internal compilation error.", status_code=500, details={})

                if str(b.id) == str(block_id):
                    if b.computed_min is not None and b.computed_max is not None:
                        extrema_str = f" (Absolute Scale Limits: {b.computed_min} to {b.computed_max})"
                    break

            instruction += f"  {b_idx + 1}. Target Data Element -> ID: {block_id}{extrema_str}\n"

        instruction += (
            "\nCRITICAL RULE: You MUST read the exact numeric score (e.g., 'step_4_final_score') "
            "from the JSON data\nfor EACH mapped ID listed above. DO NOT HALLUCINATE positive outcomes "
            "based primarily on the blueprint's tone.\nIf the numeric score for an element is mathematically "
            "low (e.g., 1.x or 2.x out of 5), you MUST be ruthless,\ncritical, and objective in explaining "
            "its severe real-world implication.\n"
            "NEVER mention internal system IDs (e.g. blk_...) or logic node names in your output.\n"
            "=====================================================\n"
        )
        return instruction

    @staticmethod
    def build_global_mapping(
        workflow_data: dict[str, Any], selected_layouts: list[dict[str, Any]] | None = None
    ) -> str:
        """Builds a global mapping cheatsheet across the entire workflow if needed.
        Scans all step IDs to ensure the LLM knows how step variable contexts map.
        """
        # MVP: currently step-level IDs are injected at JSON assembly in synthesis.py
        # This will be extended when global cross-matrix blocks are added.
        return ""
