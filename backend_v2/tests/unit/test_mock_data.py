import pytest

from backend_v2.llm.mock_data import get_fallback_data


def test_get_fallback_data_success() -> None:
    """Test that a valid key returns the expected mock data dict."""
    data = get_fallback_data("analyst_agent")
    assert isinstance(data, dict)
    assert "thought_process" in data


def test_get_fallback_data_atomize_mock() -> None:
    """Test the special atomize_mock key."""
    data = get_fallback_data("atomize_mock")
    assert isinstance(data, dict)
    assert "tda_assertions" in data
    assert len(data["tda_assertions"]) == 15


def test_get_fallback_data_fail_fast() -> None:
    """Test that an unknown key throws a ValueError (Fail-Fast)."""
    with pytest.raises(ValueError, match="Strict Mock Data Error: Mock data not found for key 'unknown_key'"):
        get_fallback_data("unknown_key")
