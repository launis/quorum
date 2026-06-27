"""Centralized Linguistic Directive Module.

Provides the Single Source of Truth for all LLM language context injection.
Every LLM call site producing user-facing content MUST use these utilities
to ensure consistent bilingual output: English reasoning + target language output.

Architecture Reference:
    - Rule `native_english_generation_mandate` (05_llm_architecture.md L118-L122)
    - Synthesis Hook pattern (synthesis.py L658)
"""

from typing import Any

# ---------------------------------------------------------------------------
# CONSTANTS — The canonical language mandate injected into system prompts.
# ---------------------------------------------------------------------------

LANGUAGE_MANDATE: str = (
    "<rule>CRITICAL LANGUAGE MANDATE: You must generate ALL user-facing text fields "
    "(justification, coaching, falsification, remediation_steps, emotional_sentiment, "
    "theory_link, evaluation_notes, missing_context, semantic_reasoning, content_blocks, "
    "xai_highlights) exclusively in the language specified in <required_output_language>. "
    "Internal fields (reasoning_trace) may remain in English for maximum analytical depth.</rule>"
)
"""The canonical language mandate rule.

Injected into system prompts to enforce bilingual output:
- Internal reasoning in English (preserves LLM cognitive capacity)
- User-facing content in target language (respects localization)
"""


def build_linguistic_context(
    *,
    target_locale: str,
    source_language: str = "Unknown/Original",
) -> str:
    """Build the full XML linguistic context block for LLM system prompts.

    Encapsulates the three-part linguistic directive:
    1. Source data language (what the input is written in)
    2. Required output language (what the user sees)
    3. Required reasoning language (English, for maximum LLM cognitive depth)

    Args:
        target_locale: ISO language code for user-facing output (e.g. 'fi', 'en', 'sv').
        source_language: Language of the input data being evaluated.

    Returns:
        XML string ready for injection into system prompts.
    """
    return (
        "<linguistic_context>\n"
        f"  <source_data_language>{source_language}</source_data_language>\n"
        f"  <required_output_language>{target_locale}</required_output_language>\n"
        "  <required_reasoning_language>English</required_reasoning_language>\n"
        "</linguistic_context>"
    )


async def translate_text(
    text: str,
    target_lang: str,
    llm_client: Any,
    source_language: str = "English/Original",
) -> str:
    """Translates the given text to the target language using LLM.

    Args:
        text: The raw text to translate.
        target_lang: Target language code (e.g. 'fi', 'sv').
        llm_client: Bound LLMClient instance.
        source_language: The assumed language of the source text.

    Returns:
        The translated text, or the original text if translation fails, is not needed,
        or if an exception is caught (graceful fallback).

    Raises:
        None: All internal exceptions (including LLM execution failures) are caught
            and logged as warnings, returning the original text to enforce Graceful
            Degradation (§6.3).
    """
    if not text or not text.strip() or not target_lang or target_lang.lower() == "en" or not llm_client:
        return text

    try:
        from backend_v2.llm.prompt_builder import build_system_directive
        from backend_v2.services.llm_task_executor import LLMTaskExecutor
        from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

        linguistic_context = build_linguistic_context(
            target_locale=target_lang,
            source_language=source_language,
        )
        translation_system_prompt = build_system_directive(
            objective="Translate the provided text directly into the target language.",
            linguistic_context=linguistic_context,
            rules=[
                "Maintain the original meaning, tone, and facts.",
                "Output ONLY the translated text without any explanations, tags, prefix, suffix, or extra commentary.",
            ],
        )
        translation_messages = [
            {"role": "system", "content": translation_system_prompt},
            {"role": "user", "content": text},
        ]

        temp_executor = LLMTaskExecutor(PromptCompiler())
        translated_res = await temp_executor.execute_chat_task(
            client=llm_client,
            messages=translation_messages,
        )

        if isinstance(translated_res, tuple):
            translated_res = translated_res[0]
        if isinstance(translated_res, dict):
            translated_res = translated_res.get("content", "")

        translated_str = translated_res.strip() if isinstance(translated_res, str) else ""
        return translated_str if translated_str else text
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to translate text to '{target_lang}': {e}", exc_info=True)
        return text
