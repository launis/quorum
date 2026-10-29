"""Global Prompt Directives.

This module acts as the Single Source of Truth for all LLM prompt instructions
and system directives across the application.
"""

from typing import Final

__all__ = [
    "STUDIO_DISCOVER_SLOP_PHRASES",
    "STUDIO_TRANSLATE_SLOP_PHRASES",
]

STUDIO_DISCOVER_SLOP_PHRASES: Final[list[str]] = [
    "Return a list of heavily overused phrases (1-4 words max per phrase).",
    "Output must strictly be in the requested target language.",
]

STUDIO_TRANSLATE_SLOP_PHRASES: Final[list[str]] = [
    "Translate them intentionally literally as 'translation flowers' (calques in the requested target language).",
    "Do NOT return words that are already in the existing_words list.",
]
