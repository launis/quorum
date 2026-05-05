import pytest
from pydantic import ValidationError

from backend_v2.models.domain.causal import (
    CausalAnalysis,
    CausalAnalysisData,
    CausalInput,
    CounterfactualTest,
)
from backend_v2.models.enums import AbductiveConclusion, PlausibilityLevel


def test_causal_input_strict_validation() -> None:
    """Test that CausalInput follows V2CoreBase strict constraints."""
    item = CausalInput(chat_log="User said hello", last_reasoning_trace="Thinking...")
    assert item.chat_log == "User said hello"
    
    with pytest.raises(ValidationError):
        CausalInput(chat_log="Hello", extra_field="not allowed")


def test_causal_analysis_data_validation() -> None:
    """Test CausalAnalysisData constraints."""
    data = CausalAnalysisData(timeline_valid=True, observation="Looks good")
    assert data.timeline_valid is True
    
    with pytest.raises(ValidationError):
        CausalAnalysisData(timeline_valid=True, observation="Looks good", extra_field="bad")


def test_counterfactual_test_validation() -> None:
    """Test CounterfactualTest plausibility rules."""
    ct = CounterfactualTest(
        plausibility_score=PlausibilityLevel.PLAUSIBLE,
        plausibility_numeric=2.5,
        actual_scenario="Car stopped",
        simulation_result="Car kept going"
    )
    assert ct.plausibility_numeric == 2.5
    
    # Test min length / bounds
    with pytest.raises(ValidationError):
        CounterfactualTest(
            plausibility_score=PlausibilityLevel.PLAUSIBLE,
            plausibility_numeric=0.5, # Less than 1.0
            actual_scenario="Car stopped",
            simulation_result="Car kept going"
        )


def test_causal_analysis_validation() -> None:
    """Test CausalAnalysis constraints."""
    ct = CounterfactualTest(
        plausibility_score=PlausibilityLevel.PLAUSIBLE,
        plausibility_numeric=2.5,
        actual_scenario="A",
        simulation_result="B"
    )
    analysis = CausalAnalysis(
        abductive_conclusion=AbductiveConclusion.GENUINE,
        abductive_score=2.0,
        counterfactual_test=ct,
        observation="Obs",
        hypothesis="Hyp"
    )
    assert analysis.abductive_score == 2.0
    
    with pytest.raises(ValidationError):
        CausalAnalysis(
            abductive_conclusion=AbductiveConclusion.GENUINE,
            abductive_score=4.0, # Greater than 3.0
            counterfactual_test=ct,
            observation="Obs",
            hypothesis="Hyp"
        )
