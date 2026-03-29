from typing import Any
import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.domain.output_profile import OutputProfileLayout


def test_output_profile_layout_fails_fast_on_invalid_layout_type() -> None:
    data = {
        "layout_type": "INVALID_LAYOUT",
        "title": {"default_locale": "en", "translations": {"en": "Title"}},
        "components": ["blk_123"],
        "show_text": True,
    }
    with pytest.raises(AppException) as exc_info:
        OutputProfileLayout.model_validate(data)
    assert "Invalid LayoutType 'INVALID_LAYOUT'" in exc_info.value.message
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"


def test_output_profile_layout_fails_fast_on_empty_components() -> None:
    data = {
        "layout_type": "text_only",
        "title": {"default_locale": "en", "translations": {"en": "Title"}},
        "components": [],
        "show_text": True,
    }
    with pytest.raises(AppException) as exc_info:
        OutputProfileLayout.model_validate(data)
    assert "at least one component" in exc_info.value.message
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
