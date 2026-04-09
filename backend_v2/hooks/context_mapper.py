"""Universal Context Mapper for Dynamic Target Data Dictionaries.

Translates rigid numerical and UUID-based system keys into LLM-understandable
ordinal dictionaries to completely eradicate UUID blindness and Sycophancy
across all output profiles, holistic evaluations, and matrices.
"""



class ContextMapper:
    """Builder for translating Target Data IDs into Universal Ordinal Mapping limits."""

    @staticmethod
    def build_ordinal_mapping(target_blocks: list[str]) -> str:
        """Builds a section-level ordinal dictionary for evaluating specific targets."""
        if not target_blocks or "*" in target_blocks:
            return ""

        instruction = "=== TARGET DATA MAPPING & ANTI-SYCOPHANCY MANDATE ===\n"
        instruction += (
            "The raw JSON context uses non-semantic unique IDs. Below is their ordinal mapping (1, 2, 3...):\n"
        )

        for b_idx, block_id in enumerate(target_blocks):
            instruction += f"  {b_idx + 1}. Target Data Element -> ID: {block_id}\n"

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
    def build_global_mapping(workflow_data: dict, selected_layouts: list[dict] = None) -> str:
        """Builds a global mapping cheatsheet across the entire workflow if needed.
        Scans all step IDs to ensure the LLM knows how step variable contexts map.
        """
        # MVP: currently step-level IDs are injected at JSON assembly in synthesis.py
        # This will be extended when global cross-matrix blocks are added.
        return ""

