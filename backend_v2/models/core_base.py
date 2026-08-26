import logging
import re
from typing import Annotated

from fastapi import status
from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)


class V2CoreBase(BaseModel):
    """Base model enforcing Pydantic strict mode across all V2 schemas.

    This model serves as the foundational class for all V2 DTOs and models,
    guaranteeing strict validation, forbidding extra fields, and enforcing
    immutability.

    Attributes:
        model_config (ConfigDict): Pydantic configuration dictionary.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid", str_strip_whitespace=True)


class I18nText(V2CoreBase):
    """V2 Strict: Frontend no-string mandate requires all localized text to be structured.

    Attributes:
        translations: Dictionary mapping locale code to translated string.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    translations: Annotated[
        dict[str, str],
        Field(
            description=(
                "Dictionary mapping locale code to translated string, specifically: {'fi': 'Teksti', 'en': 'Text'}."
            )
        ),
    ]

    @field_validator("translations")
    @classmethod
    def validate_translations(cls, v: dict[str, str]) -> dict[str, str]:
        """Validates that English translation is always present as a baseline fallback.

        Sanitizes keys (strip and lowercase) and values, and ensures non-empty 'en'.

        Args:
            v: Raw translations dictionary.

        Returns:
            Sanitized translations dictionary with canonical keys.

        Raises:
            AppException: If 'en' key is missing or empty.
        """
        sanitized: dict[str, str] = {}
        for raw_key, raw_val in v.items():
            clean_key = raw_key.strip().lower()
            sanitized[clean_key] = raw_val

        en_trans = sanitized.get("en")
        if not en_trans or not en_trans.strip():
            msg = (
                f"I18nText must contain a valid English ('en') translation as a baseline fallback. Payload: {sanitized}"
            )
            logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        return sanitized

    def resolve(self, target_locale: str | None = None, fallback_locale: str = "en") -> str:
        """Strictly typed method to resolve the best localization, avoiding 'naked dict' fallback logic.

        Args:
            target_locale: The requested locale code (e.g. 'fi', 'fi-FI').
            fallback_locale: Fallback locale code if target_locale is unavailable (default: 'en').

        Returns:
            The resolved localized string.

        Raises:
            AppException: If no valid non-empty translation is resolved.
        """
        if target_locale:
            target_lang = re.split(r"[-_]", target_locale.strip())[0].lower()
            if target_lang in self.translations and self.translations[target_lang].strip():
                return self.translations[target_lang]

        clean_fallback = re.split(r"[-_]", fallback_locale.strip())[0].lower()
        if clean_fallback in self.translations and self.translations[clean_fallback].strip():
            return self.translations[clean_fallback]

        if "en" in self.translations and self.translations["en"].strip():
            return self.translations["en"]

        msg = (
            f"I18nText failed to resolve localization for target '{target_locale}' and fallback '{fallback_locale}'. "
            f"Available keys: {list(self.translations.keys())}"
        )
        logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    def get(self, lang_code: str, fallback: str = "en") -> str:
        """Extracts the localized string safely for templates (Jinja2) and programmatic access.

        Args:
            lang_code: Target locale code.
            fallback: Default fallback locale code if unable to resolve.

        Returns:
            The resolved string.
        """
        return self.resolve(target_locale=lang_code, fallback_locale=fallback)
