"""Linguistic Directives Module.

Provides the Markdown builders for linguistic context injection.
This module acts as the Single Source of Truth for language mandates.
"""

from backend_v2.models.prompts.global_mandates import LANGUAGE_MANDATE


def build_linguistic_context(
    *,
    target_locale: str,
    source_language: str = "Unknown/Original",
    include_mandate: bool = False,
) -> str:
    """Build the full Markdown linguistic context block for LLM system prompts.

    Encapsulates the three-part linguistic directive:
    1. Source data language (what the input is written in)
    2. Required output language (what the user sees)
    3. Required reasoning language (English, for maximum LLM cognitive depth)

    Args:
        target_locale: ISO language code for user-facing output (e.g. 'fi', 'en', 'sv').
        source_language: Language of the input data being evaluated.
        include_mandate: If True, appends LANGUAGE_MANDATE to the end of the block.

    Returns:
        Markdown string ready for injection into system prompts.
    """
    ctx = (
        "## LINGUISTIC CONTEXT\n"
        f"- Source Data Language: {source_language}\n"
        f"- Required Output Language: {target_locale}\n"
        "- Internal Thought Language: English\n"
        "> [!CRITICAL_WARNING]\n"
        "> Even if the system prompt and internal thoughts are in English, ALL user-facing JSON fields (e.g. semantic_reasoning, row_explanation) MUST be generated in the Required Output Language.\n"
    )
    if include_mandate:
        ctx += f"\n{LANGUAGE_MANDATE}"
    return ctx
