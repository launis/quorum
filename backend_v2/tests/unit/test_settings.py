import os
from unittest.mock import patch

from backend_v2.settings import Settings, get_settings


def test_settings_initialization() -> None:
    """Test that settings can be instantiated with default or provided values."""
    settings = Settings(google_api_key="sk-google-test", use_mock_db=True, use_mock_llm=True)
    assert settings.google_api_key == "sk-google-test"
    assert settings.use_mock_db is True
    assert settings.use_mock_llm is True
    assert settings.use_mock_llm is True


def test_get_settings_lru_cache() -> None:
    """Test that get_settings is properly cached and returns a singleton instance."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2


def test_settings_model_post_init_mock_llm() -> None:
    """Test the Google AI post_init validation bypasses key check when mock LLM is enabled."""
    with patch.dict(os.environ, clear=True):
        settings = Settings(use_mock_llm=True)
        # Should not raise any validation error because mock LLM is true.
        assert settings.use_mock_llm is True
