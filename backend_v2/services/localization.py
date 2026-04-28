import json
import logging
from contextvars import ContextVar
from pathlib import Path
from typing import Any

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

# Context Variable for Request-Scope Language
_language_var: ContextVar[str] = ContextVar("language", default="en")


def set_language(lang: str) -> None:
    """Sets the language for the current context (request)."""
    _language_var.set(lang)


def get_language() -> str:
    """Gets the language from the current context."""
    return _language_var.get()


class LocalizationService:
    """Service to handle server-side translation for SDUI schemas."""

    _translations: dict[str, dict[str, str]] = {}
    _loaded: bool = False

    # Path relative to backend root, assuming standard structure
    L10N_DIR: Path = Path(__file__).parent.parent / "l10n"

    @classmethod
    def load_if_needed(cls) -> None:
        """Loads translation files into memory on first access."""
        if cls._loaded:
            return

        try:
            if not cls.L10N_DIR.exists():
                # Fail Fast: Missing localization directory is a critical deployment error.
                msg = f"Localization directory not found: {cls.L10N_DIR}"
                logger.error("[LocalizationService] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
                )

            json_files = list(cls.L10N_DIR.glob("*.json"))
            if not json_files:
                # Fail Fast: No translation files found.
                msg = f"No translation files found in {cls.L10N_DIR}"
                logger.error("[LocalizationService] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
                )

            for file_path in json_files:
                lang_code = file_path.stem  # e.g., 'en', 'fi'
                try:
                    with open(file_path, encoding="utf-8") as f:
                        data = json.load(f)
                        cls._translations[lang_code] = data
                except Exception as e:
                    # Fail Fast: Corrupt translation file.
                    msg = f"Failed to load translation file {file_path}"
                    logger.error("[LocalizationService] %s: %s - %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, e)
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.CONFIGURATION_ERROR, "original_error": str(e)},
                    ) from e

            cls._loaded = True
            logger.info("Loaded translations for languages: %s", list(cls._translations.keys()))
        except AppException:
            raise
        except Exception as e:
            # Catch-all for unexpected filesystem errors
            msg = f"Critical error loading translations: {e}"
            logger.error("[LocalizationService] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR, "original_error": str(e)},
            ) from e

    @classmethod
    def translate(cls, key: str, lang: str | None = None, **kwargs: Any) -> str:
        """Translates a key into the target language with optional interpolation.

        Args:
            key (str): The translation key.
            lang (str): The target language code (e.g., 'fi'). If None, uses Context.
            **kwargs: Arguments for string interpolation (e.g., name="User").

        Returns:
            str: The translated and formatted string.
        """
        cls.load_if_needed()

        # Resolve Language from Context if not provided
        if lang is None:
            lang = get_language()

        # Fallback logic: "fi-FI" -> "fi"
        lang_simple = lang.split("-")[0].lower()
        target_dict = cls._translations.get(lang_simple, {})

        # 1. Try exact match in target language
        val = target_dict.get(key)

        # 2. Try Fallback to English
        if val is None and lang_simple != "en":
            val = cls._translations.get("en", {}).get(key)
            if val is not None:
                logger.warning(
                    "BFF Translation Fallback: Key '%s' missing in '%s', falling back to English.", key, lang_simple
                )

        # 3. Strict Missing Key Exception
        if val is None:
            msg = f"Translation key '{key}' is missing from both '{lang_simple}' and 'en' dictionaries."
            logger.error("[LocalizationService] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
            )

        # 4. Interpolation
        if kwargs:
            try:
                return val.format(**kwargs)
            except KeyError as e:
                # Fail Fast: Missing interpolation argument is a developer error.
                msg = f"Localization missing argument '{e.args[0]}' for key '{key}' in lang '{lang}'"
                logger.error("[LocalizationService] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR, "missing_arg": str(e.args[0])},
                ) from e
            except Exception as e:
                # Fail Fast: Invalid format string
                msg = f"Localization format error for key '{key}': {e}"
                logger.error("[LocalizationService] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR, "original_error": str(e)},
                ) from e

        return val

    @classmethod
    def get(cls, key: str, lang: str | None = None, **kwargs: Any) -> str:
        """Class method alias for translate. (Hardcoded defaults purged)."""
        return cls.translate(key, lang, **kwargs)
