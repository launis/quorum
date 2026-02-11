import json
import logging
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Optional

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
                logger.warning(f"Localization directory not found: {cls.L10N_DIR}")
                return

            for file_path in cls.L10N_DIR.glob("*.json"):
                lang_code = file_path.stem  # e.g., 'en', 'fi'
                try:
                    with open(file_path, encoding="utf-8") as f:
                        data = json.load(f)
                        cls._translations[lang_code] = data
                except Exception as e:
                    logger.error(f"Failed to load translation file {file_path}: {e}")

            cls._loaded = True
            logger.info(f"Loaded translations for languages: {list(cls._translations.keys())}")
        except Exception as e:
            logger.error(f"Critical error loading translations: {e}", exc_info=True)

    @classmethod
    def translate(cls, key: str, lang: Optional[str] = None, **kwargs) -> str:
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
                logger.warning(f"Localization missing argument '{e.args[0]}' for key '{key}' in lang '{lang}'")
                return val # Return unformatted string rather than crashing
            except Exception as e:
                logger.error(f"Localization format error for key '{key}': {e}")
                return val
        
        return val

    def get(self, key: str, lang: Optional[str] = None, default: str = None, **kwargs) -> str:
        """Instance method alias for translate with custom default fallback."""
        val = self.translate(key, lang, **kwargs)
        if val == key and default:
            return default
        return val


def localize_schema(schema: dict[str, Any], lang: Optional[str] = None) -> dict[str, Any]:
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
