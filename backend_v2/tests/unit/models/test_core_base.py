"""Unit tests for backend_v2/models/core_base.py.

Verifies V2CoreBase immutability, extra-field forbidding, I18nText sanitization,
validation error fail-fast handling, and localization resolution.
"""

from __future__ import annotations

import re

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.core_base import (
    OPAQUE_STRIPE_ID_REGEX,
    I18nText,
    V2CoreBase,
    generate_opaque_id,
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
        model.name = "mutated"  # type: ignore[misc]

    # 2. Extra fields forbidden
    with pytest.raises(ValidationError):
        ConcreteModel(name="test", extra_field="forbidden")  # type: ignore[call-arg]

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
    assert i18n_bilingual.get("fi-FI") == "Moi"

    # Fallback to custom locale when target missing
    assert i18n_bilingual.resolve("fr", fallback_locale="de") == "Hallo"
    assert i18n_bilingual.get("fr", fallback="de") == "Hallo"

    # Fallback to English baseline when target missing and default fallback used
    assert i18n_bilingual.resolve("fr") == "Hello"
    assert i18n_bilingual.get("fr") == "Hello"

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
    """Verifies generate_opaque_id produces valid Opaque Stripe IDs matching regex."""
    for prefix in EntityPrefix:
        generated = generate_opaque_id(prefix)
        assert generated.startswith(f"{prefix.value}_")
        assert re.match(OPAQUE_STRIPE_ID_REGEX, generated)

    # String prefix and custom length
    custom_id = generate_opaque_id("prf", length=24)
    assert custom_id.startswith("prf_")
    assert len(custom_id) == 4 + 24
    assert re.match(OPAQUE_STRIPE_ID_REGEX, custom_id)

    # Bounded length (min 16, max 32)
    min_bounded = generate_opaque_id("wf", length=5)
    assert len(min_bounded) == 3 + 16


def test_generate_opaque_id_negative_invalid_prefix() -> None:
    """Verifies generate_opaque_id fails fast when prefix is invalid."""
    with pytest.raises(AppException) as exc_info:
        generate_opaque_id("toolongprefix")
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"

    with pytest.raises(AppException) as exc_info2:
        generate_opaque_id("x")
    assert exc_info2.value.status_code == 400

