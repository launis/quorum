"""Translation Service Module.

Provides utilities for translating text using LLM calls.
"""

from __future__ import annotations

import logging

from backend_v2.core.template_processor import TemplateProcessor
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.llm.prompt_builder import build_system_directive
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.prompts.common import (
    STATIC_LINGUISTIC_PROTOCOL,
    build_linguistic_parameters,
)
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

__all__ = ["translate_text"]

logger = logging.getLogger(__name__)

_SYSTEM_INSTRUCTION = build_system_directive(
    objective="Translate the provided text directly into the target language.",
    linguistic_context=STATIC_LINGUISTIC_PROTOCOL,
    rules=[
        "Maintain the original meaning, tone, and facts.",
        "Output ONLY the translated text without any explanations, tags, prefix, suffix, or extra commentary.",
    ],
)


def _dlq_record_translation_failure(text: str, target_lang: str, exc: Exception) -> None:
    """Record translation failure for telemetry and dead-letter tracing.

    Args:
        text: The source text that failed translation.
        target_lang: The target ISO language code.
        exc: The caught exception that triggered the fallback.
    """
    logger.error(
        "Failed to translate text to '%s': %s",
        target_lang,
        exc,
        exc_info=True,
        extra={
            "error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.name,
            "target_lang": target_lang,
            "payload_length": len(text),
        },
    )


async def translate_text(
    text: str,
    target_lang: str,
    llm_client: LLMClient | None,
    source_language: str = "English/Original",
) -> str:
    """Translate the given text to the target language using an LLM.

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
        linguistic_params = build_linguistic_parameters(
            target_locale=target_lang,
            source_language=source_language,
        )
        user_content = TemplateProcessor.render_prompt(
            t"{linguistic_params:raw}\n<user_payload>\n{text}\n</user_payload>"
        )
        translation_messages = [
            LLMMessageDTO(role="system", content=_SYSTEM_INSTRUCTION),
            LLMMessageDTO(role="user", content=user_content),
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
        _dlq_record_translation_failure(text, target_lang, e)
        return text
