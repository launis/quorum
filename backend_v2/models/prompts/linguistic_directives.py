"""Linguistic Directives Module.

Provides the XML builders for linguistic context injection.
This module acts as the Single Source of Truth for language mandates.
"""

from backend_v2.models.prompts.global_mandates import LANGUAGE_MANDATE


def build_linguistic_context(
    *,
    target_locale: str,
    source_language: str = "Unknown/Original",
    include_mandate: bool = False,
) -> str:
    """Build the full XML linguistic context block for LLM system prompts.

    Encapsulates the three-part linguistic directive:
    1. Source data language (what the input is written in)
    2. Required output language (what the user sees)
    3. Required reasoning language (English, for maximum LLM cognitive depth)

    Args:
        target_locale: ISO language code for user-facing output (e.g. 'fi', 'en', 'sv').
        source_language: Language of the input data being evaluated.
        include_mandate: If True, appends LANGUAGE_MANDATE to the end of the block.

    Returns:
        XML string ready for injection into system prompts.
    """
    ctx = (
        "<linguistic_context>\n"
        f"  <source_data_language>{source_language}</source_data_language>\n"
        f"  <required_output_language>{target_locale}</required_output_language>\n"
        "  <required_reasoning_language>English</required_reasoning_language>\n"
        "  <critical_warning>Even if the system prompt and internal thoughts are in English, ALL user-facing JSON string fields (e.g., content blocks, xai_highlights content, row_explanation) MUST be translated to the Required Output Language. NEVER output English to the user unless they explicitly requested English.</critical_warning>\n"
        "</linguistic_context>"
    )
    if include_mandate:
        ctx += f"\n{LANGUAGE_MANDATE}"
    return ctx
