import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.output_profile import (
    OutputProfileCreateDTO,
    OutputProfileResponseDTO,
    OutputProfileUpdateDTO,
)
from backend_v2.models.enums import XaiExtensionType
from backend_v2.models.v2_core import I18nText, OutputLayoutBlock


@pytest.fixture
def base_i18n() -> I18nText:
    return I18nText(default_locale="en", translations={"en": "Test Profile"})


@pytest.fixture
def mock_layouts() -> list[OutputLayoutBlock]:
    return [
        OutputLayoutBlock(
            preset_view="1d_metrics",
            title=I18nText(default_locale="en", translations={"en": "Metrics"}),
        )
    ]


def test_output_profile_create_dto_validates_xai_coercion(base_i18n: I18nText, mock_layouts: list[OutputLayoutBlock]) -> None:
    # Test that list of strings coerces directly to Enum
    data = {
        "id": "prf_1234567890abcdef",
        "slug": "test_profile",
        "workflow_id": "wf_1",
        "name": base_i18n.model_dump(),
        "visible_extensions": ["falsification", "coaching"],
        "include_diagnostic_scorecard": True,
        "layouts": [l.model_dump() for l in mock_layouts],
    }

    dto = OutputProfileCreateDTO.model_validate(data)
    assert len(dto.visible_extensions) == 2
    assert dto.visible_extensions[0] == XaiExtensionType.FALSIFICATION
    assert dto.visible_extensions[1] == XaiExtensionType.COACHING
    assert dto.include_diagnostic_scorecard is True


def test_output_profile_response_dto_validates_xai_coercion(base_i18n: I18nText, mock_layouts: list[OutputLayoutBlock]) -> None:
    # Epic 24 and XAI coercion requirements for the database read DTO
    data = {
        "id": "prf_1234567890abcdef",
        "slug": "test_profile",
        "workflow_id": "wf_1",
        "name": base_i18n.model_dump(),
        "visible_extensions": ["emotional_sentiment", "risk_flag"],
        "include_diagnostic_scorecard": False,
        "layouts": [l.model_dump() for l in mock_layouts],
    }

    dto = OutputProfileResponseDTO.model_validate(data)
    assert dto.visible_extensions[0] == XaiExtensionType.EMOTIONAL_SENTIMENT
    assert dto.visible_extensions[1] == XaiExtensionType.RISK_FLAG
    assert dto.include_diagnostic_scorecard is False


def test_output_profile_dto_extra_forbid(base_i18n: I18nText, mock_layouts: list[OutputLayoutBlock]) -> None:
    # Ensure extra fields crash the DTO safely (RFC 7807 Fail-Fast)
    data = {
        "id": "prf_1234567890abcdef",
        "slug": "test_profile",
        "workflow_id": "wf_1",
        "name": base_i18n.model_dump(),
        "layouts": [l.model_dump() for l in mock_layouts],
        "v1_legacy_field": "should crash",
    }

    with pytest.raises(ValidationError) as exc:
        OutputProfileResponseDTO.model_validate(data)
    assert "Extra inputs are not permitted" in str(exc.value)


def test_output_profile_update_dto_validates_epic24() -> None:
    # Test update allows null or boolean for diagnostic scorecard
    dto = OutputProfileUpdateDTO.model_validate({"include_diagnostic_scorecard": True})
    assert dto.include_diagnostic_scorecard is True
    
    dto_none = OutputProfileUpdateDTO.model_validate({"include_diagnostic_scorecard": None})
    assert dto_none.include_diagnostic_scorecard is None
