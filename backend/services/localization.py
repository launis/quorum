import json
import logging
from contextvars import ContextVar
from pathlib import Path
from typing import Any

from backend.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

# Context Variable for Request-Scope Language
_language_var: ContextVar[str] = ContextVar("language", default="en")


def set_language(lang: str):
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
    def load_if_needed(cls):
        """Loads translation files into memory on first access."""
        if cls._loaded:
            return

        try:
            if not cls.L10N_DIR.exists():
                 # Fail Fast: Missing localization directory is a critical deployment error.
                raise AppException(
                    message=f"Localization directory not found: {cls.L10N_DIR}",
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR}
                )

            json_files = list(cls.L10N_DIR.glob("*.json"))
            if not json_files:
                 # Fail Fast: No translation files found.
                 raise AppException(
                    message=f"No translation files found in {cls.L10N_DIR}",
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR}
                )

            for file_path in json_files:
                lang_code = file_path.stem  # e.g., 'en', 'fi'
                try:
                    with open(file_path, encoding="utf-8") as f:
                        data = json.load(f)
                        cls._translations[lang_code] = data
                except Exception as e:
                     # Fail Fast: Corrupt translation file.
                    raise AppException(
                        message=f"Failed to load translation file {file_path}",
                        status_code=500,
                        details={"error_code": ErrorCodes.CONFIGURATION_ERROR, "original_error": str(e)}
                    ) from e

            cls._loaded = True
            logger.info(f"Loaded translations for languages: {list(cls._translations.keys())}")
        except AppException:
            raise
        except Exception as e:
            # Catch-all for unexpected filesystem errors
            raise AppException(
                message=f"Critical error loading translations: {e}",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR, "original_error": str(e)}
            ) from e

    @classmethod
    def translate(cls, key: str, lang: str | None = None, **kwargs) -> str:
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

        # 3. Fallback to Key
        if val is None:
            val = key

        # 4. Interpolation
        if kwargs:
            try:
                return val.format(**kwargs)
            except KeyError as e:
                # Fail Fast: Missing interpolation argument is a developer error.
                raise AppException(
                    message=f"Localization missing argument '{e.args[0]}' for key '{key}' in lang '{lang}'",
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR, "missing_arg": str(e.args[0])}
                ) from e
            except Exception as e:
                # Fail Fast: Invalid format string
                raise AppException(
                    message=f"Localization format error for key '{key}': {e}",
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR, "original_error": str(e)}
                ) from e

        return val

    @classmethod
    def get(cls, key: str, lang: str | None = None, default: str | None = None, **kwargs) -> str:
        """Class method alias for translate with custom default fallback."""
        val = cls.translate(key, lang, **kwargs)
        if val == key and default:
            return default
        return val


def localize_schema(schema: dict[str, Any], lang: str | None = None) -> dict[str, Any]:
    """Recursively traverses a JSON Schema and translates SDUI hints."""
    # If lang is provided explicitly (legacy), use it. Otherwise translate() picks up Context.

    if isinstance(schema, dict):
        # 1. Translate UI Hints (Pydantic / JSON Schema proper)
        if "x-ui-label" in schema and isinstance(schema["x-ui-label"], str):
            schema["x-ui-label"] = LocalizationService.translate(schema["x-ui-label"], lang)

        if "x-ui-group" in schema and isinstance(schema["x-ui-group"], str):
            schema["x-ui-group"] = LocalizationService.translate(schema["x-ui-group"], lang)

        # 2. Translate Generic UI Schema (Workflow Config)
        # Seed data uses "label" for input fields
        if "label" in schema and isinstance(schema["label"], str):
             # heuristic: only translate if it looks like a key (uppercase start?)
             # or just always try. If key missing, it falls back to value.
             # But if value is long English text "1. Chat History...", we don't want to use that as key.
             # We rely on seed_data being updated to simple keys first.
            schema["label"] = LocalizationService.translate(schema["label"], lang)

        # 3. Recurse into children
        for key, value in schema.items():
            schema[key] = localize_schema(value, lang)

    elif isinstance(schema, list):
         for i, item in enumerate(schema):
             schema[i] = localize_schema(item, lang)

    return schema
