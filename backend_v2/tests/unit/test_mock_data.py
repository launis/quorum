import pytest

from backend_v2.llm.mock_data import get_fallback_data


@pytest.mark.parametrize(
    "key",
    [
        "guard_agent",
        "analyst_agent",
        "interaction_agent",
        "logician_agent",
        "falsifier_agent",
        "causal_agent",
        "performativity_agent",
        "fact_checker_agent",
        "profiler_agent",
        "archivist_agent",
        "judge_agent",
        "xai_agent",
        "text_consolidation_hook",
        "row_explainer",
        "variance_explainer",
        "ExecutiveSummaryTask",
        "MatrixSectionTask_m0",
        "XaiHighlightsTask",
    ],
)
def test_get_fallback_data_success(key: str) -> None:
    """Test that valid keys return expected mock data dictionaries."""
    data = get_fallback_data(key)
    assert isinstance(data, dict)
    assert len(data) > 0


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
