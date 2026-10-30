"""Core Base Models for Quorum V2 Architecture.

Provides foundational Pydantic V2 base models (V2CoreBase) and structured
multilingual text representations (I18nText) enforcing strict mode, fail-fast
validation, and cross-domain localization parity.
"""

from __future__ import annotations

import logging
import re
import secrets
import threading
import time
import uuid
from dataclasses import dataclass
from typing import Annotated

from fastapi import status
from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.enums import EntityPrefix

__all__ = [
    "I18nText",
    "OPAQUE_STRIPE_ID_REGEX",
    "V2CoreBase",
    "coerce_source_quotes_tuple",
    "format_prefixed_uuid7",
    "generate_opaque_id",
    "generate_uuid7",
    "generate_uuid7_opaque_id",
    "parse_prefixed_uuid7",
]

logger = logging.getLogger(__name__)

# Phase 1, Step 1: Lock universal 32-hex RFC 9562 UUIDv7 Opaque Stripe ID regex
OPAQUE_STRIPE_ID_REGEX: str = r"^([a-z]{2,5})_[a-fA-F0-9]{32}$"


@dataclass
class _MonotonicUuid7State:
    """Thread-safe RFC 9562 Section 6.2 monotonic sub-millisecond counter state.

    Attributes:
        last_timestamp_ms: Last observed 48-bit Unix epoch millisecond tick.
        rand_a_counter: 12-bit monotonic counter within the same millisecond tick.
    """

    last_timestamp_ms: int = 0
    rand_a_counter: int = 0


_UUID7_LOCK = threading.Lock()
_UUID7_STATE = _MonotonicUuid7State()


class V2CoreBase(BaseModel):
    """Base model enforcing Pydantic strict mode across all V2 schemas.

    This model serves as the foundational class for all V2 DTOs and models,
    guaranteeing strict validation, forbidding extra fields, and enforcing
    immutability.

    Attributes:
        model_config: Pydantic configuration dictionary enforcing strictness,
            frozen immutability, and forbidding extra fields.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid", str_strip_whitespace=True)


class I18nText(V2CoreBase):
    """V2 Strict: Frontend no-string mandate requires all localized text to be structured.

    Attributes:
        translations: Dictionary mapping locale code to translated string.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

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

        if "en" not in sanitized or not sanitized["en"].strip():
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
        logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
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

        Raises:
            AppException: If no valid non-empty translation is resolved.
        """
        return self.resolve(target_locale=lang_code, fallback_locale=fallback)

    def with_copy_suffix(self, suffix: str = " (Copy)") -> I18nText:
        """Creates a new I18nText with a copy suffix appended to all translations.

        Args:
            suffix: Suffix string to append to each translation value (default: ' (Copy)').

        Returns:
            New I18nText instance with updated translation values.
        """
        new_translations = {k: f"{v}{suffix}" for k, v in self.translations.items()}
        return I18nText(translations=new_translations)


# Phase 1, Step 1: Universal 32-hex RFC 9562 UUIDv7 delegation across all EntityPrefix members
def generate_opaque_id(prefix: EntityPrefix | str, length: int = 32) -> str:
    """Generates a canonical 32-hex RFC 9562 UUIDv7 Opaque Stripe ID.

    Args:
        prefix: Entity prefix (EntityPrefix member or string matching a canonical EntityPrefix).
        length: Required hex payload length (must be 32 under universal UUIDv7 cutover).

    Returns:
        Canonical Opaque Stripe ID string formatted as '{prefix}_{32_hex}'.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if prefix is not a valid EntityPrefix
            or length is not 32.
    """
    if length != 32:
        msg = f"Universal PrefixedUUID7 requires a 32-character hex payload, got length={length}."
        logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )
    if isinstance(prefix, EntityPrefix):
        resolved_prefix = prefix
    else:
        prefix_str = str(prefix).strip().lower()
        try:
            resolved_prefix = EntityPrefix(prefix_str)
        except ValueError as exc:
            msg = f"Prefix '{prefix}' is not a registered EntityPrefix."
            logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from exc
    return generate_uuid7_opaque_id(resolved_prefix)


def parse_prefixed_uuid7(
    value: str | uuid.UUID,
    expected_prefix: EntityPrefix,
    enforce_v7: bool = True,
) -> uuid.UUID:
    """Parse a prefixed Opaque Stripe ID or UUID into a validated 16-byte UUID object.

    Args:
        value: Prefixed string identifier (specifically '{prefix}_{32_hex}') or uuid.UUID instance.
        expected_prefix: Canonical EntityPrefix expected on string inputs.
        enforce_v7: Whether to require RFC 9562 version 7 on the parsed UUID.

    Returns:
        Validated 16-byte uuid.UUID instance.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if prefix, regex, or version is invalid.
    """
    if isinstance(value, uuid.UUID):
        parsed = value
    else:
        cleaned = value.strip()
        if not re.match(OPAQUE_STRIPE_ID_REGEX, cleaned):
            msg = f"Identifier '{value}' does not match OPAQUE_STRIPE_ID_REGEX."
            logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        prefix_part, hex_part = cleaned.split("_", 1)
        if prefix_part != expected_prefix.value:
            msg = f"Identifier '{value}' has prefix '{prefix_part}', expected '{expected_prefix.value}'."
            logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        parsed = uuid.UUID(hex=hex_part)

    if enforce_v7 and parsed.version != 7:
        msg = f"UUID '{parsed}' has version {parsed.version}, expected RFC 9562 version 7."
        logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )
    return parsed


def format_prefixed_uuid7(
    raw_uuid: uuid.UUID | str,
    prefix: EntityPrefix,
    enforce_v7: bool = True,
) -> str:
    """Format a 16-byte UUID or UUID string into a canonical prefixed Opaque Stripe ID.

    Args:
        raw_uuid: uuid.UUID instance, raw UUID string, or already-prefixed Opaque Stripe ID.
        prefix: Canonical EntityPrefix to prepend.
        enforce_v7: Whether to require RFC 9562 version 7 on the UUID.

    Returns:
        Canonical Opaque Stripe ID string formatted as '{prefix.value}_{uuid.hex}'.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if raw_uuid is malformed or fails version check.
    """
    if isinstance(raw_uuid, uuid.UUID):
        uuid_obj = raw_uuid
    else:
        cleaned = raw_uuid.strip()
        if "_" in cleaned:
            uuid_obj = parse_prefixed_uuid7(cleaned, prefix, enforce_v7=enforce_v7)
            return f"{prefix.value}_{uuid_obj.hex}"
        try:
            uuid_obj = uuid.UUID(cleaned)
        except ValueError as exc:
            msg = f"Invalid UUID string '{raw_uuid}' passed to format_prefixed_uuid7."
            logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from exc

    if enforce_v7 and uuid_obj.version != 7:
        msg = f"UUID '{uuid_obj}' has version {uuid_obj.version}, expected RFC 9562 version 7."
        logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )
    return f"{prefix.value}_{uuid_obj.hex}"


# Phase 2, Step 2: Extract standalone RFC 9562 UUIDv7 primitive
def generate_uuid7(timestamp_ms: int | None = None) -> uuid.UUID:
    """Generate a monotonic 16-byte RFC 9562 UUIDv7 instance.

    Combines a 48-bit Unix epoch millisecond timestamp, a thread-safe 12-bit monotonic
    sub-millisecond counter (rand_a), the 2-bit RFC 9562 variant (0b10), and 62 bits of
    cryptographic randomness (rand_b).

    Args:
        timestamp_ms: Optional explicit Unix epoch millisecond timestamp for deterministic tests.

    Returns:
        Monotonic 16-byte uuid.UUID instance with RFC 9562 version 7.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if timestamp_ms is negative or exceeds 48 bits.
    """
    resolved_ms = int(time.time() * 1000) if timestamp_ms is None else timestamp_ms
    if resolved_ms < 0 or resolved_ms > 0xFFFFFFFFFFFF:
        msg = f"UUIDv7 timestamp_ms={resolved_ms} is outside valid 48-bit unsigned range."
        logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    with _UUID7_LOCK:
        if timestamp_ms is None and resolved_ms < _UUID7_STATE.last_timestamp_ms:
            resolved_ms = _UUID7_STATE.last_timestamp_ms

        if resolved_ms == _UUID7_STATE.last_timestamp_ms:
            _UUID7_STATE.rand_a_counter = (_UUID7_STATE.rand_a_counter + 1) & 0xFFF
            if _UUID7_STATE.rand_a_counter == 0:
                resolved_ms += 1
                _UUID7_STATE.last_timestamp_ms = resolved_ms
        else:
            _UUID7_STATE.last_timestamp_ms = resolved_ms
            _UUID7_STATE.rand_a_counter = secrets.randbits(10)

        rand_a = _UUID7_STATE.rand_a_counter

    rand_b = secrets.randbits(62)
    uuid_int = (
        ((resolved_ms & 0xFFFFFFFFFFFF) << 80)
        | (0x7 << 76)
        | ((rand_a & 0xFFF) << 64)
        | (0b10 << 62)
        | (rand_b & 0x3FFFFFFFFFFFFFFF)
    )
    return uuid.UUID(int=uuid_int)


def generate_uuid7_opaque_id(
    prefix: EntityPrefix,
    timestamp_ms: int | None = None,
) -> str:
    """Generate a monotonic RFC 9562 UUIDv7 formatted as a canonical Opaque Stripe ID.

    Combines a 48-bit Unix epoch millisecond timestamp, a thread-safe 12-bit monotonic
    sub-millisecond counter (rand_a), the 2-bit RFC 9562 variant (0b10), and 62 bits of
    cryptographic randomness (rand_b).

    Args:
        prefix: Canonical EntityPrefix to prepend to the 32-hex UUIDv7 payload.
        timestamp_ms: Optional explicit Unix epoch millisecond timestamp for deterministic tests.

    Returns:
        Canonical 32-hex Opaque Stripe ID string ('{prefix.value}_{uuid7_hex}').

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if timestamp_ms is negative or exceeds 48 bits.
    """
    return format_prefixed_uuid7(generate_uuid7(timestamp_ms=timestamp_ms), prefix, enforce_v7=True)


def coerce_source_quotes_tuple(v: object) -> tuple[str, ...] | None:
    """Coerces various quote representations into an immutable tuple of non-empty strings.

    Prevents string shattering (e.g. converting a string directly to a tuple of characters)
    by explicitly checking for `str`. Strips whitespace and filters out empty strings.
    Returns None if the result is empty or if input is None.

    Args:
        v: Raw quote object (string, sequence of strings, or None).

    Returns:
        Immutable tuple of non-empty stripped quote strings, or None if empty.
    """
    if v is None:
        return None
    if isinstance(v, str):
        stripped = v.strip()
        if stripped:
            return (stripped,)
        return None
    if isinstance(v, (list, tuple, set)):
        cleaned = tuple(item.strip() for item in v if isinstance(item, str) and item.strip())
        if cleaned:
            return cleaned
        return None
    return None
