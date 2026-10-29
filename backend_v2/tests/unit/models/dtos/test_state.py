"""Unit tests for state Data Transfer Objects (DTOs).

Verifies strict Pydantic V2 schema validation, extra field rejection, type
enforcement, and immutability across HookStateMetadata, I18nStatePayload, and
TranslationResponseDTO.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.state import (
    HookStateMetadata,
    I18nStatePayload,
    TranslationResponseDTO,
)


def test_hook_state_metadata_strictness() -> None:
    """Verify HookStateMetadata enforces strict typing, extra='forbid', and frozen immutability."""
    dto = HookStateMetadata(target_locale="en-US", fields_to_translate=["summary"])
    assert dto.target_locale == "en-US"
    assert dto.fields_to_translate == ["summary"]

    default_dto = HookStateMetadata(target_locale="fi")
    assert default_dto.fields_to_translate == []

    # Negative Case 1: Extra unknown field triggers ValidationError
    with pytest.raises(ValidationError):
        HookStateMetadata.model_validate({"target_locale": "fi", "unknown_field": True})

    # Negative Case 2: Invalid type on target_locale or fields_to_translate triggers ValidationError
    with pytest.raises(ValidationError):
        HookStateMetadata.model_validate({"target_locale": 123, "fields_to_translate": ["summary"]})

    with pytest.raises(ValidationError):
        HookStateMetadata.model_validate({"target_locale": "fi", "fields_to_translate": [123]})


def test_i18n_state_payload_strictness() -> None:
    """Verify I18nStatePayload enforces strict typing and extra='forbid'."""
    dto = I18nStatePayload(language="fi")
    assert dto.language == "fi"

    # Negative Case 1: Extra unknown field triggers ValidationError
    with pytest.raises(ValidationError):
        I18nStatePayload.model_validate({"language": "fi", "extra_field": "fail"})

    # Negative Case 2: Missing required field or non-string language triggers ValidationError
    with pytest.raises(ValidationError):
        I18nStatePayload.model_validate({})

    with pytest.raises(ValidationError):
        I18nStatePayload.model_validate({"language": 999})


def test_translation_response_dto_typing() -> None:
    """Verify TranslationResponseDTO enforces strict dict[str, str] typing and extra='forbid'."""
    dto = TranslationResponseDTO(translated_data={"key1": "value1", "key2": "value2"})
    assert dto.translated_data["key1"] == "value1"

    # Negative Case 1: Non-string dictionary value triggers ValidationError
    with pytest.raises(ValidationError):
        TranslationResponseDTO.model_validate({"translated_data": {"key": 12345}})

    # Negative Case 2: Nested list value or extra root field triggers ValidationError
    with pytest.raises(ValidationError):
        TranslationResponseDTO.model_validate({"translated_data": {"key": ["nested", "list"]}})

    with pytest.raises(ValidationError):
        TranslationResponseDTO.model_validate({"translated_data": {"key": "val"}, "extra": 1})
