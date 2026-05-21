import pytest
from pydantic import ValidationError

from backend_v2.models.domain.causal import CounterfactualTest, CausalAnalysis
from backend_v2.models.domain.performativity import PerformativityAnalysis
from backend_v2.models.enums import PlausibilityLevel, AbductiveConclusion, AuthenticityLevel

def test_counterfactual_test_bounds_validation():
    # 1. Verify that validation STILL works and raises ValidationError for out-of-bounds values
    with pytest.raises(ValidationError):
        CounterfactualTest(
            plausibility_score=PlausibilityLevel.PLAUSIBLE,
            plausibility_numeric=0.9,  # Under minimum 1.0
            actual_scenario="Actual scenario string",
            simulation_result="Simulation result string"
        )
        
    with pytest.raises(ValidationError):
        CounterfactualTest(
            plausibility_score=PlausibilityLevel.PLAUSIBLE,
            plausibility_numeric=3.1,  # Over maximum 3.0
            actual_scenario="Actual scenario string",
            simulation_result="Simulation result string"
        )

    # 2. Verify that the JSON schema does NOT contain minimum/maximum constraints on float fields
    schema = CounterfactualTest.model_json_schema()
    properties = schema.get("properties", {})
    plausibility_numeric_field = properties.get("plausibility_numeric", {})
    
    assert "minimum" not in plausibility_numeric_field, "JSON Schema must not contain minimum bound to prevent Vertex AI state explosion"
    assert "maximum" not in plausibility_numeric_field, "JSON Schema must not contain maximum bound to prevent Vertex AI state explosion"


def test_causal_analysis_bounds_validation():
    # 1. Verify that validation STILL works and raises ValidationError for out-of-bounds values
    with pytest.raises(ValidationError):
        CausalAnalysis(
            abductive_conclusion=AbductiveConclusion.GENUINE,
            abductive_score=0.9,  # Under minimum 1.0
            counterfactual_test=CounterfactualTest(
                plausibility_score=PlausibilityLevel.PLAUSIBLE,
                plausibility_numeric=2.0,
                actual_scenario="Actual",
                simulation_result="Simulated"
            ),
            observation="Observation string",
            hypothesis="Hypothesis string"
        )

    with pytest.raises(ValidationError):
        CausalAnalysis(
            abductive_conclusion=AbductiveConclusion.GENUINE,
            abductive_score=3.1,  # Over maximum 3.0
            counterfactual_test=CounterfactualTest(
                plausibility_score=PlausibilityLevel.PLAUSIBLE,
                plausibility_numeric=2.0,
                actual_scenario="Actual",
                simulation_result="Simulated"
            ),
            observation="Observation string",
            hypothesis="Hypothesis string"
        )

    # 2. Verify that the JSON schema does NOT contain minimum/maximum constraints on float fields
    schema = CausalAnalysis.model_json_schema()
    properties = schema.get("properties", {})
    abductive_score_field = properties.get("abductive_score", {})
    
    assert "minimum" not in abductive_score_field, "JSON Schema must not contain minimum bound to prevent Vertex AI state explosion"
    assert "maximum" not in abductive_score_field, "JSON Schema must not contain maximum bound to prevent Vertex AI state explosion"


def test_performativity_analysis_bounds_validation():
    # 1. Verify that validation STILL works and raises ValidationError for out-of-bounds values
    with pytest.raises(ValidationError):
        PerformativityAnalysis(
            performativity_heuristics=[],
            pre_mortem_analysis={"performed": False, "weak_signals": []},
            authenticity_assessment=AuthenticityLevel.ORGANIC,
            authenticity_score=0.9,  # Under minimum 1.0
            description="Description text"
        )

    with pytest.raises(ValidationError):
        PerformativityAnalysis(
            performativity_heuristics=[],
            pre_mortem_analysis={"performed": False, "weak_signals": []},
            authenticity_assessment=AuthenticityLevel.ORGANIC,
            authenticity_score=3.1,  # Over maximum 3.0
            description="Description text"
        )

    # 2. Verify that the JSON schema does NOT contain minimum/maximum constraints on float fields
    schema = PerformativityAnalysis.model_json_schema()
    properties = schema.get("properties", {})
    authenticity_score_field = properties.get("authenticity_score", {})
    
    assert "minimum" not in authenticity_score_field, "JSON Schema must not contain minimum bound to prevent Vertex AI state explosion"
    assert "maximum" not in authenticity_score_field, "JSON Schema must not contain maximum bound to prevent Vertex AI state explosion"

