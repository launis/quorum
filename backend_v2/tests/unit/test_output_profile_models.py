import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.domain.output_profile import OutputProfile


def test_output_profile_fails_fast_on_invalid_id() -> None:
    data = {
        "id": "INVALID",
        "slug": "test_slug",
        "workflow_id": "wf_1234abcd",
        "name": {"default_locale": "en", "translations": {"en": "Title"}},
        "layouts": []
    }
    with pytest.raises(AppException) as exc_info:
        OutputProfile.model_validate(data)
    assert "Opaque Stripe Pattern" in exc_info.value.message
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"


def test_output_profile_fails_fast_on_empty_slug() -> None:
    data = {
        "id": "prf_1234abcd",
        "slug": "   ",
        "workflow_id": "wf_1234abcd",
        "name": {"default_locale": "en", "translations": {"en": "Title"}},
        "layouts": []
    }
    with pytest.raises(AppException) as exc_info:
        OutputProfile.model_validate(data)
    assert "cannot be empty" in exc_info.value.message
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
