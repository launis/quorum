"""Localization and string formatting service for backend SDUI schemas."""

from __future__ import annotations

import json
import logging
from contextvars import ContextVar
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any

from fastapi import status
from pydantic import BaseModel, ConfigDict, Field

from backend_v2.exceptions import AppException, ErrorCodes

__all__ = [
    "LocaleTranslationsDTO",
    "LocalizationService",
    "get_language",
    "set_language",
]

logger = logging.getLogger(__name__)

# Context Variable for Request-Scope Language
_language_var: ContextVar[str] = ContextVar("language", default="en")


def set_language(lang: str) -> None:
    """Sets the language for the current context (request).

    Args:
        lang: The language code to set (e.g. 'en' or 'fi').
    """
    _language_var.set(lang)


def get_language() -> str:
    """Gets the language from the current context.

    Returns:
        The current language code.
    """
    return _language_var.get()


class LocaleTranslationsDTO(BaseModel):
    """Encapsulates translations for a specific locale.

    Attributes:
        translations: Mapping of translation keys to localized string values.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    translations: Annotated[
        dict[str, str],
        Field(default_factory=dict, description="Mapping of translation keys to localized string values"),
    ] = Field(default_factory=dict)

    def lookup(self, key: str) -> str | None:
        """Retrieve translation string by key if present.

        Args:
            key: The translation key.

        Returns:
            The translation string if present, None otherwise.
        """
        if key in self.translations:
            return self.translations[key]
        return None

    def __getitem__(self, key: str) -> str:
        """Subscript access for template rendering.

        Args:
            key: The translation key.

        Returns:
            The translation string for key.
        """
        return self.translations[key]

    def __getattr__(self, item: str) -> str:
        """Attribute access for template rendering.

        Args:
            item: Attribute name as translation key.

        Returns:
            The translation string for item.

        Raises:
            AttributeError: If key is not found in translations.
        """
        if item in self.translations:
            return self.translations[item]
        raise AttributeError(f"Translation key '{item}' not found in translations")

    def __contains__(self, key: str) -> bool:
        """Check if key exists in translations.

        Args:
            key: The translation key to verify.

        Returns:
            True if key exists, False otherwise.
        """
        return key in self.translations


class LocalizationService:
    """Service to handle server-side translation for SDUI schemas."""

    _translations: dict[str, LocaleTranslationsDTO] = {}
    _loaded: bool = False

    # Point to the backend l10n directory
    L10N_DIR: Path = Path(__file__).parent.parent / "l10n"

    @classmethod
    def load_if_needed(cls) -> None:
        """Loads translation files into memory on first access.

        Raises:
            AppException: If the L10N_DIR is missing, contains no files, or contains corrupt JSON (ErrorCodes.CONFIGURATION_ERROR).
        """
        if cls._loaded:
            return

        try:
            if not cls.L10N_DIR.exists():
                # Fail Fast: Missing localization directory is a critical deployment error.
                msg = f"Localization directory not found: {cls.L10N_DIR}"
                logger.error("[LocalizationService] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

            json_files = list(cls.L10N_DIR.glob("*.json"))
            if not json_files:
                # Fail Fast: No translation files found.
                msg = f"No translation files found in {cls.L10N_DIR}"
                logger.error("[LocalizationService] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

            for file_path in json_files:
                # filename is like en.json -> stem is 'en'
                lang_code = file_path.stem
                try:
                    with open(file_path, encoding="utf-8") as f:
                        data = json.load(f)
                        cls._translations[lang_code] = LocaleTranslationsDTO(translations=data)
                except (json.JSONDecodeError, OSError, ValueError) as e:
                    # Fail Fast: Corrupt translation file.
                    msg = f"Failed to load translation file {file_path}"
                    logger.error(
                        "[LocalizationService] %s: %s - %s",
                        ErrorCodes.CONFIGURATION_ERROR.name,
                        msg,
                        e,
                        exc_info=True,
                    )
                    raise AppException(
                        message=msg,
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value, "original_error": str(e)},
                    ) from e

            cls._loaded = True
            logger.info("Loaded translations for languages: %s", list(cls._translations.keys()))
        except AppException:
            raise
        except OSError as e:
            # Catch-all for unexpected filesystem errors
            msg = f"Critical error loading translations: {e}"
            logger.error("[LocalizationService] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value, "original_error": str(e)},
            ) from e

    @classmethod
    def translate(cls, key: str, lang: str | None = None, **kwargs: Any) -> str:
        """Translates a key into the target language with optional interpolation.

        Args:
            key: The translation key.
            lang: The target language code (e.g., 'fi'). If None, uses Context.
            **kwargs: Arguments for string interpolation (e.g., name="User").

        Returns:
            The translated and formatted string.

        Raises:
            AppException: If the translation key is completely missing or interpolation arguments are invalid (ErrorCodes.CONFIGURATION_ERROR).
        """
        cls.load_if_needed()

        # Resolve Language from Context if not provided
        if lang is None:
            lang = get_language()

        # Fallback logic: "fi-FI" -> "fi"
        lang_simple = lang.split("-")[0].lower()
        target_dto = cls.get_translations(lang_simple)
        val: str | None = None
        if target_dto is not None:
            val = target_dto.lookup(key)

        # 2. Try Fallback to English
        if val is None and lang_simple != "en":
            en_dto = cls.get_translations("en")
            if en_dto is not None:
                val = en_dto.lookup(key)
            if val is not None:
                logger.warning(
                    "BFF Translation Fallback: Key '%s' missing in '%s', falling back to English.", key, lang_simple
                )

        # 3. Strict Missing Key Exception
        if val is None:
            msg = f"Translation key '{key}' is missing from both '{lang_simple}' and 'en' dictionaries."
            logger.error("[LocalizationService] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        # 4. Interpolation
        if kwargs:
            try:
                return val.format(**kwargs)
            except KeyError as e:
                # Fail Fast: Missing interpolation argument is a developer error.
                msg = f"Localization missing argument '{e.args[0]}' for key '{key}' in lang '{lang}'"
                logger.error("[LocalizationService] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value, "missing_arg": str(e.args[0])},
                ) from e
            except (ValueError, TypeError) as e:
                # Fail Fast: Invalid format string
                msg = f"Localization format error for key '{key}': {e}"
                logger.error("[LocalizationService] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value, "original_error": str(e)},
                ) from e

        return val

    @classmethod
    def get_translations(cls, lang_simple: str) -> LocaleTranslationsDTO | None:
        """Retrieves translations for a specific language code.

        Args:
            lang_simple: Simple language code (e.g. 'en', 'fi').

        Returns:
            LocaleTranslationsDTO if loaded and found, None otherwise.
        """
        cls.load_if_needed()
        if lang_simple in cls._translations:
            return cls._translations[lang_simple]
        return None

    @classmethod
    def get(cls, key: str, lang: str | None = None, **kwargs: Any) -> str:
        """Class method alias for translate. (Hardcoded defaults purged).

        Args:
            key: The translation key.
            lang: The target language code (e.g., 'fi'). If None, uses Context.
            **kwargs: Arguments for string interpolation.

        Returns:
            The translated string.

        Raises:
            AppException: If the translation key is missing or formatting fails (ErrorCodes.CONFIGURATION_ERROR).
        """
        return cls.translate(key, lang, **kwargs)

    @classmethod
    def format_date(cls, dt: datetime, locale: str = "en") -> str:
        """Formats a datetime object according to locale conventions.

        Args:
            dt: The datetime to format.
            locale: Target locale code (e.g., 'fi' or 'en').

        Returns:
            Localized formatted date and time string.
        """
        lang_simple = locale.split("-")[0].lower()
        if lang_simple == "fi":
            return f"{dt.strftime('%d.%m.%Y')} klo {dt.strftime('%H:%M')}"
        return dt.strftime("%Y-%m-%d %H:%M")

    @classmethod
    def format_decimal(cls, value: float, locale: str = "en", decimals: int = 2) -> str:
        """Formats a floating-point number with localized decimal separator.

        Args:
            value: Number to format.
            locale: Target locale code (e.g., 'fi' or 'en').
            decimals: Number of decimal digits.

        Returns:
            Localized formatted decimal number string.
        """
        formatted = f"{value:.{decimals}f}"
        lang_simple = locale.split("-")[0].lower()
        if lang_simple == "fi":
            return formatted.replace(".", ",")
        return formatted

    @classmethod
    def format_score(cls, value: float, locale: str = "en") -> str:
        """Formats an evaluative or normalized score.

        Args:
            value: Score number to format.
            locale: Target locale code (e.g., 'fi' or 'en').

        Returns:
            Localized score string formatted to two decimals.
        """
        return cls.format_decimal(value, locale, decimals=2)

    @classmethod
    def format_percent(cls, ratio: float, locale: str = "en", decimals: int = 1) -> str:
        """Formats a percentage ratio with localized punctuation and spacing.

        Args:
            ratio: Percentage value (e.g., 85.2).
            locale: Target locale code (e.g., 'fi' or 'en').
            decimals: Number of decimal digits.

        Returns:
            Localized percentage string (e.g. '85,2 %' in fi, '85.2%' in en).
        """
        formatted = cls.format_decimal(ratio, locale, decimals=decimals)
        lang_simple = locale.split("-")[0].lower()
        if lang_simple == "fi":
            return f"{formatted} %"
        return f"{formatted}%"

    @classmethod
    def format_cost(cls, amount: float, locale: str = "en") -> str:
        """Formats a USD monetary amount with localized decimal and currency symbol positioning.

        Args:
            amount: Cost amount in USD.
            locale: Target locale code (e.g., 'fi' or 'en').

        Returns:
            Localized cost string (e.g. '12,50 $' or '0,04 $' in fi, '$12.50' or '$0.04' in en).
        """
        formatted = cls.format_decimal(amount, locale, decimals=2)
        lang_simple = locale.split("-")[0].lower()
        if lang_simple == "fi":
            return f"{formatted} $"
        return f"${formatted}"
