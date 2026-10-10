"""Stateless formatting functions for tabular export evidence, citations, and AI reasoning.

Provides pure utility functions for formatting text observations, citation bracket
cleaning, and qualitative reasoning sanitization for Excel and CSV export pipelines.
"""

from __future__ import annotations

import re

__all__ = [
    "clean_citation_brackets",
    "format_ai_reasoning",
    "format_text_observations",
]


def clean_citation_brackets(text: str) -> str:
    """Cleans citation strings by stripping surrounding brackets and quotes.

    Args:
        text: Raw citation or source reference string.

    Returns:
        Cleaned citation string with surrounding brackets/quotes removed and whitespace trimmed.
    """
    if not text or not text.strip():
        return ""

    cleaned = text.strip()

    # Strip surrounding square brackets if matched pair
    if cleaned.startswith("[") and cleaned.endswith("]") and len(cleaned) >= 2:
        cleaned = cleaned[1:-1].strip()

    # Strip surrounding double or single quotation marks
    if (cleaned.startswith('"') and cleaned.endswith('"')) or (cleaned.startswith("'") and cleaned.endswith("'")):
        if len(cleaned) >= 2:
            cleaned = cleaned[1:-1].strip()

    # Collapse internal multiple whitespace
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    return cleaned


def format_text_observations(quotes: list[str] | str | None) -> str:
    r"""Formats forensic text observation citations for tabular spreadsheet and CSV cells.

    For single quotes, strips whitespace and surrounding quotation noise.
    For multi-quote collections, strips each item and returns a clean, newline-delimited
    numbered enumeration list (e.g. '[1] ...\\n[2] ...').

    Args:
        quotes: Single quote string, list of quote strings, or None.

    Returns:
        Cleaned, formatted multi-line observation string or empty string.
    """
    if quotes is None:
        return ""

    if isinstance(quotes, str):
        cleaned = quotes.strip()
        return cleaned

    # Process list of quote strings
    cleaned_items: list[str] = []
    for item in quotes:
        if item and item.strip():
            c = item.strip()
            cleaned_items.append(c)

    if not cleaned_items:
        return ""

    if len(cleaned_items) == 1:
        return cleaned_items[0]

    # Multiple quotes: format with numbered brackets on separate lines
    formatted_lines = [f"[{idx}] {q}" for idx, q in enumerate(cleaned_items, start=1)]
    return "\n".join(formatted_lines)


def format_ai_reasoning(reasoning: str | None) -> str:
    """Sanitizes and formats AI qualitative evaluation rationale for export surfaces.

    Normalizes Windows CRLF to LF, collapses consecutive empty lines, and ensures
    clean leading and trailing whitespace boundaries.

    Args:
        reasoning: Raw qualitative rationale string or None.

    Returns:
        Sanitized rationale string or empty string if None or whitespace-only.
    """
    if reasoning is None or not reasoning.strip():
        return ""

    # Normalize CRLF to LF
    text = reasoning.replace("\r\n", "\n").replace("\r", "\n").strip()

    # Collapse 3+ newlines to 2 newlines (preserve paragraphs without excessive blank space)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text
