"""Universal Context Mapper for Dynamic Target Data Dictionaries.

Translates rigid numerical and UUID-based system keys into LLM-understandable
ordinal dictionaries to completely eradicate UUID blindness and Sycophancy
across all output profiles, holistic evaluations, and matrices.
"""

import logging

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, PromptBlockBase
from backend_v2.models.v2_core import MatrixSynthesisGroup, Workflow

logger = logging.getLogger(__name__)


class ContextMapper:
    """Builder for translating Target Data IDs into Universal Ordinal Mapping limits."""

    @staticmethod
    def build_ordinal_mapping(target_blocks: list[str], all_blocks: list[PromptBlockBase] | None = None) -> str:
        """Builds a section-level ordinal dictionary for evaluating specific targets.

        Translates raw non-semantic unique IDs to numbered ordinals with explicit
        extrema scales to avoid LLM sycophancy.

        Args:
            target_blocks: List of string identifiers for the target data blocks.
            all_blocks: Optional full list of PromptBlock objects to cross-reference bounds.

        Returns:
            str: The compiled string instructions for the LLM.

        Raises:
            AppException: If blocks provided are not strict PromptBlock Pydantic models.
        """
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
                if not isinstance(b, PromptBlockBase):
                    msg = (
                        "Fail-Fast violation: ContextMapper MUST receive strictly typed "
                        "PromptBlock models, not raw dictionaries."
                    )
                    logger.error("[ContextMapper] %s: %s", ErrorCodes.DATA_CORRUPTION.name, msg, exc_info=True)
                    raise AppException(
                        message="Internal compilation error.",
                        status_code=500,
                        details={"error_code": ErrorCodes.DATA_CORRUPTION.value},
                    )

                if str(b.id) == str(block_id):
                    if isinstance(b, MatrixPromptBlock) and b.computed_min is not None and b.computed_max is not None:
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
        workflow_data: Workflow | None = None,
        selected_groups: list[MatrixSynthesisGroup] | None = None,
        execution_id: str | None = None,
    ) -> str:
        """Builds a global mapping cheatsheet across the entire workflow if needed.

        Scans all step IDs to ensure the LLM knows how step variable contexts map.

        Args:
            workflow_data: The full workflow graph definition.
            selected_groups: Target output synthesis groups for the report.
            execution_id: Identifier of the current execution.

        Returns:
            str: The compiled global mapping instructions string.
        """
        # MVP: currently step-level IDs are injected at JSON assembly in synthesis.py
        # This will be extended when global cross-matrix blocks are added.
        if execution_id:
            return f"=== GLOBAL CONTEXT ===\nExecution ID: {execution_id}\n======================\n"
        return ""
