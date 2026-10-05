import pytest
from pydantic import BaseModel

from backend_v2.llm.mock_data import MOCK_REGISTRY, get_fallback_data


def test_mock_registry_typed_contracts() -> None:
    """Test that MOCK_REGISTRY enforces type[BaseModel] keys and BaseModel values."""
    assert len(MOCK_REGISTRY) == 22
    for model_cls, model_instance in MOCK_REGISTRY.items():
        assert issubclass(model_cls, BaseModel)
        assert isinstance(model_instance, BaseModel)
        assert isinstance(model_instance, model_cls)


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
    assert type(data) is dict
    assert len(data) > 0


def test_get_fallback_data_atomize_mock() -> None:
    """Test the special atomize_mock key."""
    data = get_fallback_data("atomize_mock")
    assert type(data) is dict
    assert "tda_assertions" in data
    tda_list = data["tda_assertions"]
    assert isinstance(tda_list, list)
    assert len(tda_list) == 15


def test_get_fallback_data_fail_fast() -> None:
    """Test that an unknown key throws a ValueError (Fail-Fast)."""
    with pytest.raises(ValueError, match="Strict Mock Data Error: Mock data not found for key 'unknown_key'"):
        get_fallback_data("unknown_key")
