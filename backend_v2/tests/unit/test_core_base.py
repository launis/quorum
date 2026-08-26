import pytest
from pydantic import ValidationError

from backend_v2.models.core_base import V2CoreBase


def test_v2_core_base_extra_forbid() -> None:
    """Test that V2CoreBase enforces extra='forbid'."""

    class DummyModel(V2CoreBase):
        field: str

    # Should succeed with exact fields
    obj = DummyModel(field="value")
    assert obj.field == "value"

    # Should fail if extra fields are provided
    with pytest.raises(ValidationError) as exc_info:
        DummyModel(**{"field": "value", "extra_field": "not allowed"})

    assert "Extra inputs are not permitted" in str(exc_info.value) or "extra_forbidden" in str(exc_info.value)


def test_v2_core_base_strict_mode() -> None:
    """Test that V2CoreBase enforces strict mode."""

    class DummyModel(V2CoreBase):
        field: int

    # Should fail if given a string that can be cast to int, because strict=True
    with pytest.raises(ValidationError) as exc_info:
        DummyModel(field="123")  # type: ignore[arg-type]

    assert "Input should be a valid integer" in str(exc_info.value) or "int_type" in str(exc_info.value)


def test_i18n_text_validation_and_resolve() -> None:
    """Test I18nText validation and resolution logic in core_base."""
    from backend_v2.exceptions import AppException
    from backend_v2.models.core_base import I18nText

    # 1. Missing or whitespace English translation raises AppException
    with pytest.raises(AppException):
        I18nText.model_validate({"translations": {"fi": "Moi", "en": "   "}})

    # 2. Missing translations dictionary altogether raises ValidationError
    with pytest.raises(ValidationError):
        I18nText.model_validate({})

    # 3. Extra fields forbidden (e.g. default_locale)
    with pytest.raises(ValidationError):
        I18nText.model_validate({"default_locale": "en", "translations": {"en": "Hello"}})

    # 4. Key sanitization (whitespace and uppercase)
    i18n_sanitized = I18nText(translations={"  EN  ": "Hello", "  FI  ": "Moi"})
    assert i18n_sanitized.translations == {"en": "Hello", "fi": "Moi"}

    # 5. Resolve and get logic
    i18n = I18nText(translations={"fi": "Moi", "en": "Hello", "sv": "Hej"})
    assert i18n.resolve("sv-SE") == "Hej"
    assert i18n.resolve("de", fallback_locale="fi") == "Moi"  # fallback to specified fallback_locale
    assert i18n.resolve("de") == "Hello"  # default fallback to en
    assert i18n.get("sv") == "Hej"
    assert i18n.get("de", fallback="fi") == "Moi"
    assert i18n.get("de") == "Hello"

    # 6. Resolve with unresolvable locale and missing fallback raises AppException
    i18n_de = I18nText.model_construct(translations={"de": "Hallo"})
    with pytest.raises(AppException):
        i18n_de.resolve("fr", fallback_locale="es")

    # 7. Resolve with whitespace-only translation raises AppException
    i18n_whitespace = I18nText.model_construct(translations={"fi": "   ", "en": "   "})
    with pytest.raises(AppException):
        i18n_whitespace.resolve("fi")
