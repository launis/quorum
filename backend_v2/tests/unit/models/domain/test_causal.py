"""Unit tests for Causal Agent Domain Models."""

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.causal import (
    CausalAnalysis,
    CausalAnalysisData,
    CausalDTO,
    CausalInput,
    CausalOutput,
    CounterfactualTest,
)
from backend_v2.models.enums import AbductiveConclusion, PlausibilityLevel


def test_causal_input_strict_validation() -> None:
    """Test that CausalInput follows V2CoreBase strict and frozen constraints."""
    item = CausalInput(chat_log="User said hello", last_reasoning_trace="Thinking...")
    assert item.chat_log == "User said hello"

    # Negative case 1: extra field forbidden
    with pytest.raises(ValidationError):
        CausalInput.model_validate({"chat_log": "Hello", "extra_field": "not allowed"})

    # Negative case 2: empty chat_log violates min_length=1
    with pytest.raises(ValidationError):
        CausalInput(chat_log="")


def test_causal_analysis_data_validation() -> None:
    """Test CausalAnalysisData constraints and negative cases."""
    data = CausalAnalysisData(timeline_valid=True, observation="Looks good")
    assert data.timeline_valid is True

    # Negative case 1: extra field forbidden
    with pytest.raises(ValidationError):
        CausalAnalysisData.model_validate({"timeline_valid": True, "observation": "Looks good", "extra_field": "bad"})

    # Negative case 2: empty observation violates min_length=1
    with pytest.raises(ValidationError):
        CausalAnalysisData(timeline_valid=True, observation="")


def test_counterfactual_test_validation() -> None:
    """Test CounterfactualTest plausibility rules including boundary values."""
    ct_min = CounterfactualTest(
        plausibility_score=PlausibilityLevel.PLAUSIBLE,
        plausibility_numeric=1.0,
        actual_scenario="Car stopped",
        simulation_result="Car kept going",
    )
    assert ct_min.plausibility_numeric == 1.0

    ct_max = CounterfactualTest(
        plausibility_score=PlausibilityLevel.PLAUSIBLE,
        plausibility_numeric=3.0,
        actual_scenario="Car stopped",
        simulation_result="Car kept going",
    )
    assert ct_max.plausibility_numeric == 3.0

    # Negative case 1: below lower bound (min - 0.1)
    with pytest.raises(AppException) as exc_low:
        CounterfactualTest(
            plausibility_score=PlausibilityLevel.PLAUSIBLE,
            plausibility_numeric=0.9,
            actual_scenario="Car stopped",
            simulation_result="Car kept going",
        )
    assert exc_low.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED}

    # Negative case 2: above upper bound (max + 0.1)
    with pytest.raises(AppException) as exc_high:
        CounterfactualTest(
            plausibility_score=PlausibilityLevel.PLAUSIBLE,
            plausibility_numeric=3.1,
            actual_scenario="Car stopped",
            simulation_result="Car kept going",
        )
    assert exc_high.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED}


def test_causal_analysis_validation() -> None:
    """Test CausalAnalysis constraints including boundary values."""
    ct = CounterfactualTest(
        plausibility_score=PlausibilityLevel.PLAUSIBLE,
        plausibility_numeric=2.5,
        actual_scenario="A",
        simulation_result="B",
    )
    analysis_min = CausalAnalysis(
        abductive_conclusion=AbductiveConclusion.GENUINE,
        abductive_score=1.0,
        counterfactual_test=ct,
        observation="Obs",
        hypothesis="Hyp",
    )
    assert analysis_min.abductive_score == 1.0

    analysis_max = CausalAnalysis(
        abductive_conclusion=AbductiveConclusion.GENUINE,
        abductive_score=3.0,
        counterfactual_test=ct,
        observation="Obs",
        hypothesis="Hyp",
    )
    assert analysis_max.abductive_score == 3.0

    # Negative case 1: below lower bound (min - 0.1)
    with pytest.raises(AppException) as exc_low:
        CausalAnalysis(
            abductive_conclusion=AbductiveConclusion.GENUINE,
            abductive_score=0.9,
            counterfactual_test=ct,
            observation="Obs",
            hypothesis="Hyp",
        )
    assert exc_low.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED}

    # Negative case 2: above upper bound (max + 0.1)
    with pytest.raises(AppException) as exc_high:
        CausalAnalysis(
            abductive_conclusion=AbductiveConclusion.GENUINE,
            abductive_score=3.1,
            counterfactual_test=ct,
            observation="Obs",
            hypothesis="Hyp",
        )
    assert exc_high.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED}


def test_causal_dto_and_output_validation() -> None:
    """Test CausalDTO and CausalOutput validation and negative cases."""
    ct = CounterfactualTest(
        plausibility_score=PlausibilityLevel.PLAUSIBLE,
        plausibility_numeric=2.0,
        actual_scenario="A",
        simulation_result="B",
    )
    analysis = CausalAnalysis(
        abductive_conclusion=AbductiveConclusion.GENUINE,
        abductive_score=2.0,
        counterfactual_test=ct,
        observation="Obs",
        hypothesis="Hyp",
    )
    dto = CausalDTO(
        thought_process="Step-by-step causal reasoning",
        conclusion="Valid causal chain",
        confidence_score=0.85,
        causal_analysis=analysis,
    )
    assert dto.causal_analysis.abductive_score == 2.0

    output = CausalOutput(
        thought_process="Step-by-step causal reasoning",
        conclusion="Valid causal chain",
        confidence_score=0.85,
        causal_analysis=analysis,
    )
    assert output.confidence_score == 0.85

    # Negative case 1: confidence_score out of bounds (> 1.0)
    with pytest.raises(AppException):
        CausalOutput(
            thought_process="Step-by-step causal reasoning",
            conclusion="Valid causal chain",
            confidence_score=1.5,
            causal_analysis=analysis,
        )

    # Negative case 2: hallucinated empty thought_process
    with pytest.raises(AppException):
        CausalDTO(
            thought_process="N/A",
            conclusion="Valid causal chain",
            confidence_score=0.85,
            causal_analysis=analysis,
        )
