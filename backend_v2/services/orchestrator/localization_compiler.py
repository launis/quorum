"""Localization Compiler for resolving I18n text and compiling LLM prompt instructions.

Centralizes translation resolution, static rubric compilation, and dynamic runtime
instruction compilation logic for the prompt orchestration pipeline.
"""

from __future__ import annotations

import datetime
import logging
from typing import Any

from pydantic import ValidationError

from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PersonaPromptBlock,
    PromptBlock,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.enums import PromptBlockCategory

logger = logging.getLogger(__name__)

__all__ = ["LANGUAGE_NAMES", "LocalizationCompiler"]

# Standard language names for dynamic TARGET_LANGUAGE substitution
LANGUAGE_NAMES = {"fi": "Finnish", "en": "English", "sv": "Swedish", "de": "German", "fr": "French", "es": "Spanish"}


class LocalizationCompiler:
    """Handles I18n text resolution and instruction compilation for LLM prompts.

    Centralizes all localization-sensitive prompt compilation logic for static
    cached prefixes and dynamic user message tails.
    """

    def __init__(self) -> None:
        """Initialize LocalizationCompiler."""
        pass

    def _resolve_target_language_name(self, target_locale: str) -> str:
        """Resolve a target locale code to its full English language name.

        Args:
            target_locale: The requested language code (e.g., 'fi' or 'en').

        Returns:
            The canonical English name of the target language.

        Raises:
            AppException: If target_locale is unsupported (ErrorCodes.VALIDATION_FAILED).
        """
        base_locale = target_locale.split("-")[0].lower()
        if base_locale not in LANGUAGE_NAMES:
            msg = f"Unsupported target locale '{target_locale}'"
            logger.error(
                "[LocalizationCompiler] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "target_locale": target_locale},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        return LANGUAGE_NAMES[base_locale]

    def _resolve_execution_time(self, execution_time: datetime.datetime | str | None) -> datetime.datetime:
        """Resolve optional execution_time input into a timezone-aware UTC datetime.

        Args:
            execution_time: Optional static timestamp or ISO-8601 string.

        Returns:
            Resolved datetime object.

        Raises:
            AppException: If execution_time string cannot be parsed as ISO-8601 or has invalid type
                (ErrorCodes.VALIDATION_FAILED).
        """
        if execution_time is None:
            return datetime.datetime.now(datetime.UTC)
        if isinstance(execution_time, datetime.datetime):
            return execution_time
        if isinstance(execution_time, str):
            try:
                clean_str = execution_time.replace("Z", "+00:00")
                return datetime.datetime.fromisoformat(clean_str)
            except ValueError as e:
                msg = f"Failed to parse execution_time string '{execution_time}' into a valid ISO-8601 datetime."
                logger.error(
                    "[LocalizationCompiler] %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    msg,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
                    exc_info=True,
                )
                raise AppException(
                    message=msg,
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e

        msg = f"Invalid execution_time type '{type(execution_time).__name__}'. Must be datetime, str, or None."
        logger.error(
            "[LocalizationCompiler] %s: %s",
            ErrorCodes.VALIDATION_FAILED.name,
            msg,
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
            exc_info=True,
        )
        raise AppException(
            message=msg,
            status_code=400,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    def resolve_i18n(self, text_obj: Any, target_locale: str) -> str:
        """Resolve an I18n object to a localized string with strict fail-fast validation.

        Args:
            text_obj: The I18nText model, raw I18n dictionary, or None.
            target_locale: The requested language code (e.g., 'fi' or 'en').

        Returns:
            Resolved text string, or empty string if None.

        Raises:
            ConfigurationError: If the text object cannot be hydrated as I18nText
                or if the required locale translation is missing (ErrorCodes.VALIDATION_FAILED).
        """
        if not text_obj:
            return ""

        if not isinstance(text_obj, I18nText):
            try:
                text_obj = I18nText.model_validate(text_obj)
            except (ValidationError, ValueError, TypeError) as e:
                msg = (
                    f"Legacy string fallback detected or invalid type: '{type(text_obj).__name__}'. "
                    "All text MUST be valid I18nText dictionaries."
                )
                logger.error(
                    "[LocalizationCompiler] %s",
                    msg,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
                    exc_info=True,
                )
                raise ConfigurationError(msg, details={"error_code": ErrorCodes.VALIDATION_FAILED}) from e

        # V2 MANDATE: NO FALLBACKS. If a translation is requested, it MUST exist.
        target_lang = target_locale.split("-")[0].lower()
        if target_lang not in text_obj.translations or not text_obj.translations[target_lang]:
            msg = f"Translation missing for required locale '{target_locale}'. Fallbacks are strictly forbidden."
            logger.error(
                "Translation missing for required locale.",
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "target_locale": target_locale},
                exc_info=True,
            )
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})

        return str(text_obj.resolve(target_locale))

    def compile_static_instructions(self, blocks: list[PromptBlock], target_locale: str) -> str:
        """Compile static instruction-type V2 PromptBlocks for the Cached System Prompt.

        Extracts blocks where not MatrixPromptBlock AND category_id != RUNTIME_VARIABLES.

        Args:
            blocks: List of PromptBlock definitions.
            target_locale: The requested language code.

        Returns:
            A formatted string of all static instruction directives.

        Raises:
            AppException: If target_locale is unsupported (ErrorCodes.VALIDATION_FAILED).
            ConfigurationError: If a PromptBlock is missing mandatory instruction text
                (ErrorCodes.VALIDATION_FAILED).
        """
        compiled_lines: list[str] = []
        target_lang_name = self._resolve_target_language_name(target_locale)

        for block in blocks:
            if not isinstance(block, MatrixPromptBlock) and block.category_id != PromptBlockCategory.RUNTIME_VARIABLES:
                label = self.resolve_i18n(block.label, "en")
                desc = ""
                match block:
                    case SystemRulePromptBlock(instruction_text=text) if text:
                        desc = text
                    case PersonaPromptBlock(role_enforcement=text) if text:
                        desc = text
                    case ProtocolPromptBlock(protocol_instructions=text) if text:
                        desc = text

                if not desc:
                    block_id = block.id
                    msg = f"PromptBlock '{block_id}' is missing mandatory instruction text."
                    logger.error(
                        "PromptBlock is missing mandatory instruction text.",
                        extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "block_id": block_id},
                        exc_info=True,
                    )
                    raise ConfigurationError(msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})

                desc = desc.replace("{TARGET_LANGUAGE}", target_lang_name)

                if label or desc:
                    compiled_lines.append(f'<STATIC_INSTRUCTION label="{label}">\n{desc}\n</STATIC_INSTRUCTION>')
        return "\n\n".join(compiled_lines)

    def compile_dynamic_instructions(
        self,
        blocks: list[PromptBlock],
        target_locale: str,
        execution_time: datetime.datetime | str | None = None,
    ) -> str:
        """Compile dynamic instruction-type V2 PromptBlocks for the Uncached User Tail.

        Extracts blocks where category_id == RUNTIME_VARIABLES,
        and performs real-time variable substitutions (e.g. {CURRENT_DATE}).

        Args:
            blocks: List of PromptBlock definitions.
            target_locale: The requested language code.
            execution_time: Optional static timestamp of the execution or inputs to ensure 100% determinism.

        Returns:
            A formatted string of all dynamic runtime instruction directives.

        Raises:
            AppException: If target_locale is unsupported or execution_time string cannot be parsed as ISO-8601
                (ErrorCodes.VALIDATION_FAILED).
            ConfigurationError: If a runtime_variables block is missing mandatory instruction text
                (ErrorCodes.VALIDATION_FAILED).
        """
        now_utc = self._resolve_execution_time(execution_time)
        current_date_str = now_utc.strftime("%Y-%m-%d")
        dynamic_time_str = now_utc.strftime("%H:%M:%S UTC")
        target_lang_name = self._resolve_target_language_name(target_locale)

        compiled_lines: list[str] = []
        for block in blocks:
            if block.category_id == PromptBlockCategory.RUNTIME_VARIABLES:
                label = self.resolve_i18n(block.label, "en")
                desc = ""
                match block:
                    case SystemRulePromptBlock(instruction_text=text) if text:
                        desc = text

                if not desc:
                    block_id = block.id
                    msg = f"PromptBlock '{block_id}' is missing mandatory 'instruction_text'."
                    logger.error(
                        "PromptBlock is missing mandatory instruction text.",
                        extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "block_id": block_id},
                        exc_info=True,
                    )
                    raise ConfigurationError(msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})

                # Perform Runtime Variable Substitutions
                desc = desc.replace("{CURRENT_DATE}", current_date_str)
                desc = desc.replace("{DYNAMIC_TIME}", dynamic_time_str)
                desc = desc.replace("{TARGET_LANGUAGE}", target_lang_name)

                if label or desc:
                    compiled_lines.append(f'<DYNAMIC_INSTRUCTION label="{label}">\n{desc}\n</DYNAMIC_INSTRUCTION>')
        return "\n\n".join(compiled_lines)
