from backend_v2.models.dtos.output_profile import OutputProfileResponseDTO


def test_reproduce_tier4_profile_bug() -> None:
    # If the bug exists, this will PASS when it should FAIL (Validation Error for 50)
    profile_data = {
        "id": "prf_test12345678",
        "slug": "test_profile",
        "workflow_id": "wf_123",
        "name": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
        "strictness_level": 50,
        "layouts": [],
    }

    import pytest
    from pydantic import ValidationError

    # If the bug exists, this will FAIL because NO ValidationError is raised.
    # We WANT it to raise a ValidationError because 50 is an illegal strictness level.
    with pytest.raises(ValidationError):
        OutputProfileResponseDTO.model_validate(profile_data)
