"""Translation Service Module.

Provides utilities for translating text using LLM calls.
"""

import logging
from typing import Any

from backend_v2.exceptions import AppException
from backend_v2.llm.prompt_builder import build_system_directive
from backend_v2.models.prompts.linguistic_directives import build_linguistic_context
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

logger = logging.getLogger(__name__)


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
    """
    if not text or not text.strip() or not target_lang or target_lang.lower() == "en" or not llm_client:
        return text

    try:
        linguistic_context = build_linguistic_context(
            target_locale=target_lang,
            source_language=source_language,
            include_mandate=True,
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

        translated_str = ""
        match translated_res:
            case (str() as content, _):
                translated_str = content.strip()
            case str() as content:
                translated_str = content.strip()
            case _:
                translated_str = str(translated_res).strip()

        return translated_str if translated_str else text
    except (AppException, AttributeError, OSError, ValueError, KeyError, RuntimeError, TypeError) as e:
        logger.error("Failed to translate text to '%s': %s", target_lang, e, exc_info=True)
        return text
