import pytest
from pydantic import ValidationError

from backend_v2.models.domain.output_profile import OutputProfile


def test_output_profile_fails_fast_on_invalid_id() -> None:
    data = {
        "id": "INVALID",
        "slug": "test_slug",
        "workflow_id": "wf_1234abcd",
        "name": {"default_locale": "en", "translations": {"en": "Title", "fi": "Title"}},
        "layouts": [],
    }
    with pytest.raises(ValidationError) as exc_info:
        OutputProfile.model_validate(data)
    assert "String should match pattern" in str(exc_info.value)


def test_output_profile_fails_fast_on_empty_slug() -> None:
    data = {
        "id": "prf_1234abcd",
        "slug": "   ",
        "workflow_id": "wf_1234abcd",
        "name": {"default_locale": "en", "translations": {"en": "Title", "fi": "Title"}},
        "layouts": [],
    }
    with pytest.raises(ValidationError) as exc_info:
        OutputProfile.model_validate(data)
    assert "slug" in str(exc_info.value)
