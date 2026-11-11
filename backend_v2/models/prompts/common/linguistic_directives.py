"""Linguistic Directives Module (Common Layer).

Single Source of Truth for language mandates and dynamic parameter injection.
"""

from __future__ import annotations

import functools

__all__ = [
    "DESC_TRANSLATION_MANDATE",
    "STATIC_LINGUISTIC_PROTOCOL",
    "build_linguistic_parameters",
]

DESC_TRANSLATION_MANDATE: str = "Translated into the target locale."

STATIC_LINGUISTIC_PROTOCOL: str = (
    "<linguistic_mandate>\n"
    "- REASONING VS. OUTPUT LANGUAGE ISOLATION:\n"
    "  * The `<required_reasoning_language>` directive applies strictly to hidden internal thought traces (specifically `reasoning_trace`).\n"
    "  * ALL user-facing JSON string fields (specifically content blocks, xai_highlights, row_explanation, and atom evaluation `reasoning` / `semantic_reasoning` explanations) MUST be generated strictly in the language specified in `<required_output_language>`.\n"
    "  * Even when internal reasoning is conducted in English, NEVER emit English in user-facing fields unless `<required_output_language>` is 'en'.\n"
    "</linguistic_mandate>"
)


@functools.lru_cache(maxsize=32)
def build_linguistic_parameters(
    target_locale: str,
    source_language: str = "Unknown/Original",
) -> str:
    """Return strictly the lightweight dynamic XML parameter block.

    Args:
        target_locale: Target output locale code for user-facing fields.
        source_language: Detected or declared language of the source data.

    Returns:
        Formatted XML string containing the `<linguistic_parameters>` block.
    """
    return (
        "<linguistic_parameters>\n"
        f"  <source_data_language>{source_language.strip()}</source_data_language>\n"
        f"  <required_output_language>{target_locale.strip().lower()}</required_output_language>\n"
        "  <required_reasoning_language>English</required_reasoning_language>\n"
        "</linguistic_parameters>"
    )
