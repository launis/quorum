"""Regression test for OutputProfile schema mismatch (Epic 122/123 Parity)."""

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.output_profile import OutputProfileResponseDTO
from backend_v2.models.v2_core import EmbeddedOutputProfile


def test_output_profile_response_dto_schema_parity() -> None:
    """Proof of success: OutputProfileResponseDTO should accept extension_labels and user_role_mappings."""
    payload = {
        "id": "prf_1234567890123456",
        "slug": "test-profile",
        "workflow_id": "wf_9d68c573802341db",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "layouts": [],
        "user_role_mappings": {"ROLE_ARCHITECT": {"default_locale": "en", "translations": {"en": "Navigator"}}},
        "extension_labels": {"citation": {"default_locale": "en", "translations": {"en": "Citation"}}},
    }

    # This should now pass without raising extra_forbidden
    OutputProfileResponseDTO.model_validate(payload)


def test_embedded_output_profile_schema_parity() -> None:
    """Proof of success: EmbeddedOutputProfile should accept extension_labels and user_role_mappings."""
    payload = {
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "layouts": [],
        "user_role_mappings": {"ROLE_ARCHITECT": {"default_locale": "en", "translations": {"en": "Navigator"}}},
        "extension_labels": {"citation": {"default_locale": "en", "translations": {"en": "Citation"}}},
    }

    # This should now pass without raising extra_forbidden
    EmbeddedOutputProfile.model_validate(payload)


def test_output_profile_response_dto_negative_extra_keys() -> None:
    """Proof of failure: extra='forbid' should still work."""
    payload = {
        "id": "prf_1234567890123456",
        "slug": "test-profile",
        "workflow_id": "wf_9d68c573802341db",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "layouts": [],
        "invalid_extra_key": "should fail",
    }
    with pytest.raises(ValidationError) as exc_info:
        OutputProfileResponseDTO.model_validate(payload)
    assert "Extra inputs are not permitted" in str(exc_info.value)


def test_embedded_output_profile_negative_wrong_type() -> None:
    """Proof of failure: user_role_mappings must be dict, not list."""
    payload = {
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "layouts": [],
        "user_role_mappings": [{"ROLE_ARCHITECT": {"default_locale": "en", "translations": {"en": "Navigator"}}}],
    }
    with pytest.raises(ValidationError) as exc_info:
        EmbeddedOutputProfile.model_validate(payload)
    assert "Input should be a valid dictionary" in str(exc_info.value)
