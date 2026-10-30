"""Unit tests for backend_v2/models/core_base.py.

Verifies V2CoreBase immutability, extra-field forbidding, I18nText sanitization,
validation error fail-fast handling, localization resolution, and RFC 9562 PrefixedUUID7 utilities.
"""

from __future__ import annotations

import re
import uuid

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.core_base import (
    _UUID7_STATE,
    OPAQUE_STRIPE_ID_REGEX,
    I18nText,
    V2CoreBase,
    coerce_source_quotes_tuple,
    format_prefixed_uuid7,
    generate_opaque_id,
    generate_uuid7,
    generate_uuid7_opaque_id,
    parse_prefixed_uuid7,
)
from backend_v2.models.enums import EntityPrefix


def test_v2_core_base_immutability_and_strictness() -> None:
    """Verifies V2CoreBase enforces frozen immutability and forbids extra fields."""

    class ConcreteModel(V2CoreBase):
        name: str

    model = ConcreteModel(name="test")
    assert model.name == "test"

    # 1. Immutability check
    with pytest.raises(ValidationError):
        model.__setattr__("name", "mutated")

    # 2. Extra fields forbidden
    with pytest.raises(ValidationError):
        ConcreteModel.model_validate({"name": "test", "extra_field": "forbidden"})

    # 3. String whitespace stripping
    stripped_model = ConcreteModel(name="  trimmed  ")
    assert stripped_model.name == "trimmed"


def test_i18n_text_validation_negative_partitions() -> None:
    """Verifies I18nText rejection of invalid payloads per ISTQB partitions."""
    # 1. Missing 'en' key entirely
    with pytest.raises(AppException) as exc_info:
        I18nText.model_validate({"translations": {"fi": "Teksti"}})
    assert exc_info.value.status_code == 400

    # 2. Empty string 'en'
    with pytest.raises(AppException) as exc_info:
        I18nText.model_validate({"translations": {"en": ""}})
    assert exc_info.value.status_code == 400

    # 3. Whitespace-only 'en'
    with pytest.raises(AppException) as exc_info:
        I18nText.model_validate({"translations": {"en": "   ", "fi": "Teksti"}})
    assert exc_info.value.status_code == 400

    # 4. Missing translations dictionary altogether
    with pytest.raises(ValidationError):
        I18nText.model_validate({})

    # 5. Non-dict translations payload
    with pytest.raises(ValidationError):
        I18nText.model_validate({"translations": "not_a_dict"})


def test_i18n_text_key_sanitization_and_resolution() -> None:
    """Verifies I18nText canonicalizes language keys and resolves requested locales."""
    i18n = I18nText(translations={"  EN  ": "English Text", "  FI_fi  ": "Suomenkielinen teksti"})
    assert "en" in i18n.translations
    assert "fi_fi" in i18n.translations

    # Exact language code
    assert i18n.resolve("en") == "English Text"
    assert i18n.get("en") == "English Text"

    # Regional language code extraction ('fi-FI' -> 'fi')
    i18n_bilingual = I18nText(translations={"en": "Hello", "fi": "Moi", "de": "Hallo"})
    assert i18n_bilingual.resolve("fi-FI") == "Moi"
    assert i18n_bilingual.resolve("fi_FI") == "Moi"

    # Fallback to custom locale when target missing
    assert i18n_bilingual.resolve("fr", fallback_locale="de") == "Hallo"

    # Fallback to English baseline when target missing and default fallback used
    assert i18n_bilingual.resolve("fr") == "Hello"

    # Fallback to English baseline when custom fallback locale is missing from translations
    i18n_only_en = I18nText(translations={"en": "Only English"})
    assert i18n_only_en.resolve("fr", fallback_locale="de") == "Only English"


def test_i18n_text_resolve_unresolvable_raises_app_exception() -> None:
    """Verifies resolve raises AppException when no valid translation can be resolved."""
    # Constructed without en
    i18n = I18nText.model_construct(translations={"es": "Hola"})
    with pytest.raises(AppException) as exc_info:
        i18n.resolve("fr", fallback_locale="de")
    assert exc_info.value.status_code == 400

    # Constructed with whitespace translations only
    i18n_empty = I18nText.model_construct(translations={"en": "   ", "fi": "   "})
    with pytest.raises(AppException) as exc_info:
        i18n_empty.resolve("fi")
    assert exc_info.value.status_code == 400


def test_i18n_text_with_copy_suffix() -> None:
    """Verifies with_copy_suffix appends copy suffix to all translations."""
    original = I18nText(translations={"en": "Executive Report", "fi": "Johdon raportti"})
    copied = original.with_copy_suffix()
    assert copied.translations["en"] == "Executive Report (Copy)"
    assert copied.translations["fi"] == "Johdon raportti (Copy)"

    custom_copied = original.with_copy_suffix(" - Cloned")
    assert custom_copied.translations["en"] == "Executive Report - Cloned"
    assert custom_copied.translations["fi"] == "Johdon raportti - Cloned"


def test_generate_opaque_id_success() -> None:
    """Verifies generate_opaque_id produces valid 32-hex RFC 9562 UUIDv7 Opaque Stripe IDs matching regex."""
    for prefix in EntityPrefix:
        generated = generate_opaque_id(prefix)
        assert generated.startswith(f"{prefix.value}_")
        assert re.match(OPAQUE_STRIPE_ID_REGEX, generated)
        assert parse_prefixed_uuid7(generated, prefix).version == 7

    # String prefix with canonical length=32
    custom_id = generate_opaque_id("prf", length=32)
    assert custom_id.startswith("prf_")
    assert len(custom_id) == 4 + 32
    assert re.match(OPAQUE_STRIPE_ID_REGEX, custom_id)


def test_generate_opaque_id_negative_invalid_prefix() -> None:
    """Verifies generate_opaque_id fails fast when prefix or length is invalid."""
    with pytest.raises(AppException) as exc_info:
        generate_opaque_id("toolongprefix")
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"

    with pytest.raises(AppException) as exc_info2:
        generate_opaque_id("x")
    assert exc_info2.value.status_code == 400

    with pytest.raises(AppException) as exc_len:
        generate_opaque_id(EntityPrefix.WORKFLOW, length=16)
    assert exc_len.value.status_code == 400
    assert exc_len.value.details["error_code"] == "VALIDATION_FAILED"

    with pytest.raises(AppException) as exc_len_24:
        generate_opaque_id("prf", length=24)
    assert exc_len_24.value.status_code == 400


def test_coerce_source_quotes_tuple_none_and_empty() -> None:
    """Verifies coerce_source_quotes_tuple returns None for None or blank inputs."""
    assert coerce_source_quotes_tuple(None) is None
    assert coerce_source_quotes_tuple("") is None
    assert coerce_source_quotes_tuple("   ") is None
    assert coerce_source_quotes_tuple([]) is None
    assert coerce_source_quotes_tuple(["", "   "]) is None


def test_coerce_source_quotes_tuple_single_string() -> None:
    """Verifies coerce_source_quotes_tuple packs single string into a 1-tuple."""
    assert coerce_source_quotes_tuple("Direct quote") == ("Direct quote",)
    assert coerce_source_quotes_tuple("  Whitespace quote  ") == ("Whitespace quote",)


def test_coerce_source_quotes_tuple_sequences() -> None:
    """Verifies coerce_source_quotes_tuple cleans sequences into immutable tuples."""
    assert coerce_source_quotes_tuple(["quote 1", "quote 2"]) == ("quote 1", "quote 2")
    assert coerce_source_quotes_tuple(("quote 1", "  quote 2  ", "")) == ("quote 1", "quote 2")
    assert coerce_source_quotes_tuple({"single_item"}) == ("single_item",)


def test_coerce_source_quotes_tuple_unsupported_types() -> None:
    """Verifies coerce_source_quotes_tuple returns None for unsupported input types."""
    assert coerce_source_quotes_tuple(12345) is None
    assert coerce_source_quotes_tuple({"key": "val"}) is None
    assert coerce_source_quotes_tuple([1, 2, 3]) is None


def test_uuid7_prefixed_bridge_and_monotonic_generation() -> None:
    """Verify generate_uuid7, generate_uuid7_opaque_id, parse_prefixed_uuid7, and format_prefixed_uuid7 roundtrips."""
    raw_u7 = generate_uuid7()
    assert isinstance(raw_u7, uuid.UUID)
    assert raw_u7.version == 7

    fixed_ts = 1_760_000_000_000
    generated_ids = [generate_uuid7_opaque_id(EntityPrefix.NODE, timestamp_ms=fixed_ts) for _ in range(10)]
    assert generated_ids == sorted(generated_ids)
    assert len(set(generated_ids)) == 10

    first_id = generated_ids[0]
    assert first_id.startswith("nod_")
    assert re.match(OPAQUE_STRIPE_ID_REGEX, first_id)

    parsed_uuid = parse_prefixed_uuid7(first_id, EntityPrefix.NODE)
    assert parsed_uuid.version == 7
    assert parse_prefixed_uuid7(parsed_uuid, EntityPrefix.NODE) == parsed_uuid
    assert format_prefixed_uuid7(parsed_uuid, EntityPrefix.NODE) == first_id
    assert format_prefixed_uuid7(str(parsed_uuid), EntityPrefix.NODE) == first_id
    assert format_prefixed_uuid7(first_id, EntityPrefix.NODE) == first_id

    # Historical timestamp branch
    older_id = generate_uuid7_opaque_id(EntityPrefix.EDGE, timestamp_ms=1_000)
    assert older_id.startswith("edg_")
    assert parse_prefixed_uuid7(older_id, EntityPrefix.EDGE).version == 7

    # Sub-millisecond 12-bit counter rollover (0xFFF -> 0 advances timestamp by 1ms)
    _UUID7_STATE.last_timestamp_ms = fixed_ts
    _UUID7_STATE.rand_a_counter = 0xFFF
    rollover_id = generate_uuid7_opaque_id(EntityPrefix.NODE, timestamp_ms=fixed_ts)
    assert parse_prefixed_uuid7(rollover_id, EntityPrefix.NODE).version == 7
    assert _UUID7_STATE.last_timestamp_ms == fixed_ts + 1
    assert _UUID7_STATE.rand_a_counter == 0

    # Clock-drift protection when wall clock is behind last_timestamp_ms
    future_ts = 9_999_999_999_999
    _UUID7_STATE.last_timestamp_ms = future_ts
    _UUID7_STATE.rand_a_counter = 10
    try:
        drift_id = generate_uuid7_opaque_id(EntityPrefix.NODE, timestamp_ms=None)
        assert parse_prefixed_uuid7(drift_id, EntityPrefix.NODE).version == 7
        assert _UUID7_STATE.last_timestamp_ms == future_ts
        assert _UUID7_STATE.rand_a_counter == 11
    finally:
        _UUID7_STATE.last_timestamp_ms = 0
        _UUID7_STATE.rand_a_counter = 0


def test_uuid7_prefixed_bridge_negative_boundaries() -> None:
    """Verify ISTQB negative boundaries on parse_prefixed_uuid7, format_prefixed_uuid7, and generate_uuid7_opaque_id."""
    v4_uuid = uuid.uuid4()
    v4_prefixed = f"nod_{v4_uuid.hex}"

    # Wrong prefix
    with pytest.raises(AppException) as exc_prefix:
        parse_prefixed_uuid7(generate_uuid7_opaque_id(EntityPrefix.NODE), EntityPrefix.EDGE)
    assert exc_prefix.value.details["error_code"] == "VALIDATION_FAILED"

    with pytest.raises(AppException) as exc_fmt_prefix:
        format_prefixed_uuid7(generate_uuid7_opaque_id(EntityPrefix.EDGE), EntityPrefix.NODE)
    assert exc_fmt_prefix.value.details["error_code"] == "VALIDATION_FAILED"

    # Non-v7 UUID rejected when enforce_v7=True
    with pytest.raises(AppException):
        parse_prefixed_uuid7(v4_prefixed, EntityPrefix.NODE, enforce_v7=True)

    with pytest.raises(AppException):
        format_prefixed_uuid7(v4_uuid, EntityPrefix.NODE, enforce_v7=True)

    # Short 16-hex ID rejected by parse_prefixed_uuid7
    with pytest.raises(AppException):
        parse_prefixed_uuid7("nod_0123456789abcdef", EntityPrefix.NODE)

    # Regex mismatch and invalid UUID strings
    with pytest.raises(AppException):
        parse_prefixed_uuid7("not-an-opaque-id", EntityPrefix.NODE)

    with pytest.raises(AppException):
        format_prefixed_uuid7("not-a-uuid-string", EntityPrefix.NODE)

    # Timestamp boundary violations (< 0 and > 48-bit max)
    with pytest.raises(AppException):
        generate_uuid7(timestamp_ms=-1)

    with pytest.raises(AppException):
        generate_uuid7_opaque_id(EntityPrefix.NODE, timestamp_ms=-1)

    with pytest.raises(AppException):
        generate_uuid7_opaque_id(EntityPrefix.NODE, timestamp_ms=0x1000000000000)
