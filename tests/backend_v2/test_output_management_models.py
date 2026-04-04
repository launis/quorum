import pytest
from pydantic import ValidationError

from backend_v2.models.domain.output_profile import OutputProfile, SynthesisConfigDTO
from backend_v2.models.v2_core import I18nText

def test_synthesis_config_dto_valid():
    config = SynthesisConfigDTO(
        length_constraint=500,
        preamble_text=I18nText(default_locale="en", translations={"en": "Hello"}),
        include_historical_summary=True,
        enable_pii_masking=True,
        allowed_exports=["pdf", "raw_json"],
        omit_empty_sections=True
    )
    assert config.length_constraint == 500
    assert config.enable_pii_masking is True

def test_synthesis_config_dto_extra_forbid():
    with pytest.raises(ValidationError) as exc_info:
        SynthesisConfigDTO(
            length_constraint=500,
            invalid_extra_field="Should fail fast"
        )
    assert "Extra inputs are not permitted" in str(exc_info.value)

def test_output_profile_valid_with_synthesis():
    profile = OutputProfile(
        id="prf_1111222233334444",
        slug="test-profile",
        workflow_id="wf_1234567890abcdef",
        name=I18nText(default_locale="en", translations={"en": "Test Profile"}),
        display_scale="original",
        synthesis=SynthesisConfigDTO(
            length_constraint=1000,
            enable_pii_masking=False
        ),
        layouts=[]
    )
    assert profile.synthesis is not None
    assert profile.synthesis.length_constraint == 1000

def test_output_profile_extra_forbid():
    with pytest.raises(ValidationError) as exc_info:
        OutputProfile(
            id="prf_1111222233334444",
            slug="test-profile",
            workflow_id="wf_1234567890abcdef",
            name=I18nText(default_locale="en", translations={"en": "Test Profile"}),
            display_scale="original",
            synthesis=None,
            layouts=[],
            unknown_invalid_key="fail"
        )
    assert "Extra inputs are not permitted" in str(exc_info.value)
