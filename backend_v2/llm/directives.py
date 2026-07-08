"""Global Prompt Directives.

This module acts as the Single Source of Truth for all LLM prompt instructions
and system directives across the application.
"""

STUDIO_DISCOVER_SLOP_PHRASES = [
    "Return a list of heavily overused phrases (1-4 words max per phrase).",
    "Output must strictly be in the requested target language.",
]

STUDIO_TRANSLATE_SLOP_PHRASES = [
    "Translate them intentionally literally as 'translation flowers' (käännöskukkasia).",
    "Do NOT return words that are already in the existing_words list.",
]
