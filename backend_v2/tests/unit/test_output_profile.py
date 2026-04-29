import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.output_profile import OutputProfileResponseDTO
from backend_v2.models.v2_core import I18nText


def test_output_profile_response_dto_exclude_organization_id() -> None:
    """Test that OutputProfileResponseDTO inherits from BaseResponseDTO and excludes organization_id."""
    dto = OutputProfileResponseDTO(
        id="test_id",
        slug="test_slug",
        workflow_id="workflow_123",
        organization_id="org_secret_123",
        name=I18nText(default_locale="en", translations={"en": "Test Profile"}),
        layouts=[],
    )

    # Verify the value is accessible in domain logic
    assert dto.organization_id == "org_secret_123"

    # Verify the value is stripped from API response payload (Data Leak Prevention Firewall)
    dumped_data = dto.model_dump()
    assert "organization_id" not in dumped_data


def test_output_profile_response_dto_extra_forbid() -> None:
    """Test that extra fields are forbidden (Zero-Duck-Typing Mandate)."""
    with pytest.raises(ValidationError) as exc_info:
        OutputProfileResponseDTO(  # type: ignore
            id="test_id",
            slug="test_slug",
            workflow_id="workflow_123",
            name=I18nText(default_locale="en", translations={"en": "Test Profile"}),
            layouts=[],
            malicious_leak="hack",
        )

    assert "Extra inputs are not permitted" in str(exc_info.value) or "extra_forbidden" in str(exc_info.value)
