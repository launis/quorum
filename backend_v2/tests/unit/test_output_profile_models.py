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


def test_output_profile_fails_fast_on_extra_keys() -> None:
    data = {
        "id": "prf_1234abcd",
        "slug": "test_slug",
        "workflow_id": "wf_1234abcd",
        "name": {"default_locale": "en", "translations": {"en": "Title", "fi": "Title"}},
        "layouts": [],
        "include_diagnostic_scorecard": True,
    }
    with pytest.raises(ValidationError) as exc_info:
        OutputProfile.model_validate(data)
    assert "Extra inputs are not permitted" in str(exc_info.value)


def test_output_profile_fails_fast_on_unmapped_target_block_type() -> None:
    data = {
        "id": "prf_1234abcd",
        "slug": "test_slug",
        "workflow_id": "wf_1234abcd",
        "name": {"default_locale": "en", "translations": {"en": "Title", "fi": "Title"}},
        "layouts": [],
        "target_block_order": ["unmapped_block_type_xyz"],
    }
    with pytest.raises(ValidationError) as exc_info:
        OutputProfile.model_validate(data)
    assert "Input should be" in str(exc_info.value)
