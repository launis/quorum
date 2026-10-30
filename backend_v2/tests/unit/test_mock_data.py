"""Unit tests for backend_v2.llm.mock_data."""

import pytest
from pydantic import BaseModel

from backend_v2.exceptions import AppException, ErrorCodes
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


def test_get_fallback_data_unknown_key_raises_app_exception() -> None:
    """Negative test: verify unknown key raises AppException (VALIDATION_FAILED)."""
    with pytest.raises(
        AppException, match="Strict Mock Data Error: Mock data not found for key 'unknown_key'"
    ) as exc_info:
        get_fallback_data("unknown_key")
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.parametrize("invalid_key", ["", "   "])
def test_get_fallback_data_empty_or_whitespace_key_raises_app_exception(invalid_key: str) -> None:
    """Negative boundary test: verify empty or whitespace-only key raises AppException."""
    with pytest.raises(AppException, match="Strict Mock Data Error: Mock data key cannot be empty") as exc_info:
        get_fallback_data(invalid_key)
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
