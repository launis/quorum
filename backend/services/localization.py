import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

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
    def translate(cls, key: str, lang: str = "en") -> str:
        """Translates a key into the target language.
        
        Args:
            key (str): The translation key (usually the English text).
            lang (str): The target language code (e.g., 'fi').
            
        Returns:
            str: The translated string, or the key itself if no translation found.
        """
        cls.load_if_needed()

        # Fallback logic: "fi-FI" -> "fi"
        lang_simple = lang.split("-")[0].lower()

        # 1. Try exact match in target language
        target_dict = cls._translations.get(lang_simple, {})
        if key in target_dict:
            return target_dict[key]

        # 2. Try Fallback to English (if requested something else)
        if lang_simple != "en":
             en_dict = cls._translations.get("en", {})
             if key in en_dict:
                 return en_dict[key]

        # 3. Return Key
        return key

    def get(self, key: str, lang: str = "en", default: str = None) -> str:
        """Instance method alias for translate with custom default fallback."""
        val = self.translate(key, lang)
        if val == key and default:
            return default
        return val


def localize_schema(schema: dict[str, Any], lang: str) -> dict[str, Any]:
    """Recursively traverses a JSON Schema and translates SDUI hints."""
    if isinstance(schema, dict):
        # 1. Translate UI Hints in current node
        if "x-ui-label" in schema and isinstance(schema["x-ui-label"], str):
            schema["x-ui-label"] = LocalizationService.translate(schema["x-ui-label"], lang)

        if "x-ui-group" in schema and isinstance(schema["x-ui-group"], str):
            schema["x-ui-group"] = LocalizationService.translate(schema["x-ui-group"], lang)

        # 2. Recurse into children
        for key, value in schema.items():
            schema[key] = localize_schema(value, lang)

    elif isinstance(schema, list):
         for i, item in enumerate(schema):
             schema[i] = localize_schema(item, lang)

    return schema
