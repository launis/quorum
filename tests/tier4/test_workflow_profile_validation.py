from pydantic import ValidationError

from backend_v2.models.v2_core import EmbeddedOutputProfile, I18nText


def test_embedded_output_profile_accepts_user_role_label():
    """Prove that EmbeddedOutputProfile accepts user_role_label like OutputProfile does."""
    data = {
        "name": {"default_locale": "en", "translations": {"en": "Test Profile"}},
        "user_role_label": {"default_locale": "en", "translations": {"en": "Target audience"}},
        "visible_metadata": ["date"],
        "display_scale": "original",
        "layouts": [],
    }
    
    profile = EmbeddedOutputProfile.model_validate(data)
    assert profile.user_role_label.default_locale == "en"
