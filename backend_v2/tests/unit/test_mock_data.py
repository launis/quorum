"""Unit tests for backend_v2.llm.mock_data."""

import pytest
from pydantic import BaseModel

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.mock_data import MOCK_REGISTRY, get_fallback_data, get_mock_structured_response
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.enums import PromptBlockCategory


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


@pytest.mark.parametrize("max_scale_point", [2, 10])
def test_get_mock_structured_response_handles_minimum_and_maximum_scale_bounds(max_scale_point: int) -> None:
    """Boundary test: verify mock structured response respects computed_min and computed_max across 1..2 and 1..10 scales."""
    scales = [
        {
            "score": lvl,
            "ai_label": f"Level {lvl}",
            "claims": [
                {
                    "label": {"translations": {"en": f"Claim {lvl}"}},
                    "tda_assertions": [
                        {
                            "tda_id": f"tda_{lvl:032x}",
                            "concept_description": f"Assertion at level {lvl}",
                            "inverse_evidence": False,
                            "aggregation_mode": "EXISTS",
                        }
                    ],
                }
            ],
        }
        for lvl in range(1, max_scale_point + 1)
    ]
    block = MatrixPromptBlock.model_validate(
        {
            "id": "blk_0195f3a0000070008000000000000001",
            "slug": f"matrix_scale_{max_scale_point}",
            "label": {"translations": {"en": "Scale Matrix"}},
            "description": {"translations": {"en": "Dynamic scale test matrix"}},
            "type": "float",
            "category_id": PromptBlockCategory.MATRIX.value,
            "ai_description": "Evaluate dynamic matrix scale bounds.",
            "scales": scales,
        }
    )

    assert block.computed_min == 1.0
    assert block.computed_max == float(max_scale_point)

    mock_out = get_mock_structured_response(block)
    assert isinstance(mock_out, LightweightMatrixOutput)
    assert mock_out.raw_score is not None
    assert block.computed_min <= mock_out.raw_score <= block.computed_max
    assert mock_out.raw_score == float(max_scale_point)
    assert mock_out.level_breakdown is not None
    assert len(mock_out.level_breakdown) == max_scale_point
