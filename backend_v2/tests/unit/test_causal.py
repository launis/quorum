import pytest
from pydantic import ValidationError

from backend_v2.models.domain.causal import (
    CausalAnalysis,
    CausalAnalysisData,
    CausalDTO,
    CausalInput,
    CausalOutput,
    CounterfactualTest,
)
from backend_v2.models.enums import AbductiveConclusion, PlausibilityLevel


def test_causal_input_success() -> None:
    """Test valid CausalInput."""
    data = CausalInput(chat_log="test log")
    assert data.chat_log == "test log"
    assert data.step_analyst is None
    assert data.last_reasoning_trace is None


def test_causal_input_empty_chat_log() -> None:
    """Test empty chat_log fails min_length validation."""
    with pytest.raises(ValidationError):
        CausalInput(chat_log="")


def test_causal_analysis_data_success() -> None:
    """Test valid CausalAnalysisData."""
    data = CausalAnalysisData(timeline_valid=True, observation="Valid timeline observation")
    assert data.timeline_valid is True
    assert data.observation == "Valid timeline observation"


def test_causal_analysis_data_empty_observation() -> None:
    """Test empty observation fails min_length validation."""
    with pytest.raises(ValidationError):
        CausalAnalysisData(timeline_valid=True, observation="")


def test_counterfactual_test_success() -> None:
    """Test valid CounterfactualTest."""
    data = CounterfactualTest(
        plausibility_score=PlausibilityLevel.HIGH,
        plausibility_numeric=3.0,
        actual_scenario="Actual scenario happened",
        simulation_result="Simulated scenario happened",
    )
    assert data.plausibility_score == PlausibilityLevel.HIGH
    assert data.plausibility_numeric == 3.0
    assert data.actual_scenario == "Actual scenario happened"
    assert data.simulation_result == "Simulated scenario happened"


def test_counterfactual_test_empty_fields() -> None:
    """Test min_length validation on CounterfactualTest string fields."""
    with pytest.raises(ValidationError):
        CounterfactualTest(
            plausibility_score=PlausibilityLevel.HIGH,
            plausibility_numeric=3.0,
            actual_scenario="",
            simulation_result="Simulated scenario happened",
        )
    with pytest.raises(ValidationError):
        CounterfactualTest(
            plausibility_score=PlausibilityLevel.HIGH,
            plausibility_numeric=3.0,
            actual_scenario="Actual",
            simulation_result="",
        )


def test_causal_analysis_success() -> None:
    """Test valid CausalAnalysis."""
    cf = CounterfactualTest(
        plausibility_score=PlausibilityLevel.HIGH,
        plausibility_numeric=3.0,
        actual_scenario="Actual",
        simulation_result="Sim",
    )
    data = CausalAnalysis(
        abductive_conclusion=AbductiveConclusion.GENUINE,
        abductive_score=3.0,
        counterfactual_test=cf,
        observation="Obs",
        hypothesis="Hyp",
    )
    assert data.abductive_score == 3.0
    assert data.observation == "Obs"
    assert data.hypothesis == "Hyp"


def test_causal_analysis_empty_fields() -> None:
    """Test min_length validation on CausalAnalysis string fields."""
    cf = CounterfactualTest(
        plausibility_score=PlausibilityLevel.HIGH,
        plausibility_numeric=3.0,
        actual_scenario="Actual",
        simulation_result="Sim",
    )
    with pytest.raises(ValidationError):
        CausalAnalysis(
            abductive_conclusion=AbductiveConclusion.GENUINE,
            abductive_score=3.0,
            counterfactual_test=cf,
            observation="",
            hypothesis="Hyp",
        )
    with pytest.raises(ValidationError):
        CausalAnalysis(
            abductive_conclusion=AbductiveConclusion.GENUINE,
            abductive_score=3.0,
            counterfactual_test=cf,
            observation="Obs",
            hypothesis="",
        )


def test_causal_dto_and_output() -> None:
    """Test wrapper DTOs."""
    cf = CounterfactualTest(
        plausibility_score=PlausibilityLevel.HIGH,
        plausibility_numeric=3.0,
        actual_scenario="Actual",
        simulation_result="Sim",
    )
    analysis = CausalAnalysis(
        abductive_conclusion=AbductiveConclusion.GENUINE,
        abductive_score=3.0,
        counterfactual_test=cf,
        observation="Obs",
        hypothesis="Hyp",
    )

    dto = CausalDTO(
        causal_analysis=analysis,
        thought_process="Thinking...",
        conclusion="Done",
        confidence_score=0.99,
    )
    assert dto.causal_analysis.observation == "Obs"

    out = CausalOutput(
        causal_analysis=analysis,
        thought_process="Thinking...",
        conclusion="Done",
        confidence_score=0.99,
        reasoning_token="Trace",
    )
    assert out.reasoning_token == "Trace"
    assert out.causal_analysis.hypothesis == "Hyp"
