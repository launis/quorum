import json

import pytest
from pydantic import ValidationError

from backend.models.domain import (
    CausalAnalysis,
    CognitiveLevel,
    CounterfactualTest,
    PerformativityAnalysis,
    ReasoningFidelity,
    SecurityCheck,
)
from backend.models.enums import (
    AbductiveConclusion,
    AuthenticityLevel,
    BloomLevel,
    FidelityLevel,
    PlausibilityLevel,
    RiskLevel,
    SimulationType,
    StrategicDepth,
)

# --- 1. SecurityCheck Tests ---


def test_security_check_enum_input():
    """Test SecurityCheck with strict Enum input."""
    data = {
        "threat_detected": True,
        "risk_level": RiskLevel.HIGH,  # Direct Enum
        "simulation_result": SimulationType.MALICIOUS,  # Direct Enum
        "anonymized": True,
        "safe_data": "SAFE",
        "original_text": "text",
    }
    # risk_score/simulation_score should be calculated automatically
    obj = SecurityCheck.model_validate(data)
    assert obj.risk_score == 3.0
    assert obj.simulation_score == 3.0
    assert obj.risk_level == RiskLevel.HIGH


def test_security_check_string_input():
    """Test SecurityCheck with string input (LLM compatibility)."""
    data = {
        "threat_detected": False,
        "risk_level": "RISK_LOW",  # String matching Enum value
        "simulation_result": "SIM_PASSIVE",
        "anonymized": True,
        "safe_data": "SAFE",
        "original_text": "text",
    }
    obj = SecurityCheck.model_validate(data)
    assert obj.risk_score == 1.0
    assert obj.simulation_score == 1.0
    assert obj.risk_level == RiskLevel.LOW  # Should be auto-converted


def test_security_check_invalid_input():
    """Test SecurityCheck fails fast with invalid input."""
    data = {
        "threat_detected": False,
        "risk_level": "INVALID_RISK",
        "simulation_result": "SIM_PASSIVE",
        "anonymized": True,
        "safe_data": "SAFE",
        "original_text": "text",
    }
    with pytest.raises(ValidationError):
        SecurityCheck.model_validate(data)


# --- 2. CognitiveLevel Tests ---


def test_cognitive_level_calculation():
    """Test CognitiveLevel score calculation."""
    data = {
        "bloom_level": BloomLevel.CREATING,
        "strategic_depth": StrategicDepth.VISIONARY,
        # scores missing, should be calc'd
    }
    obj = CognitiveLevel.model_validate(data)
    assert obj.bloom_score == 6.0
    assert obj.strategic_score == 4.0


def test_cognitive_level_string_casting():
    """Test robust string casting for CognitiveLevel."""
    data = {"bloom_level": "BLOOM_ANALYZING", "strategic_depth": "STRAT_MEDIUM"}
    obj = CognitiveLevel.model_validate(data)
    assert obj.bloom_score == 4.0
    assert obj.strategic_score == 2.0
    assert obj.bloom_level == BloomLevel.ANALYZING


# --- 3. Panel Agent Tests ---


def test_reasoning_fidelity():
    data = {"fidelity_score": "FIDELITY_HIGH", "justification": "Test", "quote": "Quote"}
    obj = ReasoningFidelity.model_validate(data)
    assert obj.fidelity_numeric == 3.0
    assert obj.fidelity_score == FidelityLevel.HIGH


def test_counterfactual_test():
    data = {"plausibility_score": PlausibilityLevel.IMPOSSIBLE, "actual_scenario": "A", "simulation_result": "B"}
    obj = CounterfactualTest.model_validate(data)
    assert obj.plausibility_numeric == 1.0


def test_causal_analysis():
    data = {
        "abductive_conclusion": AbductiveConclusion.GENUINE,
        "observation": "Obs",
        "hypothesis": "Hyp",
        "counterfactual_test": {
            "plausibility_score": PlausibilityLevel.IMPOSSIBLE,
            "actual_scenario": "A",
            "simulation_result": "B",
        },
    }
    obj = CausalAnalysis.model_validate(data)
    assert obj.abductive_score == 3.0


def test_performativity_analysis():
    data = {
        "authenticity_assessment": "AUTH_ORGANIC",
        "pre_mortem_analysis": {"performed": False, "weak_signals": []},
        "performativity_heuristics": [{"heuristic_name": "Test", "flag_raised": False, "description": "Desc"}],
    }
    obj = PerformativityAnalysis.model_validate(data)
    assert obj.authenticity_score == 3.0
    assert obj.authenticity_assessment == AuthenticityLevel.ORGANIC


# --- 4. Localization Integrity ---


def test_l10n_keys_exist():
    """Verify all Enum values exist in en.json."""
    from pathlib import Path
    l10n_path = Path(__file__).parent.parent / "l10n" / "en.json"
    with open(l10n_path, encoding="utf-8") as f:
        en_data = json.load(f)

    from enum import Enum
    enums_to_check: list[type[Enum]] = [
        RiskLevel,
        SimulationType,
        BloomLevel,
        StrategicDepth,
        FidelityLevel,
        PlausibilityLevel,
        AbductiveConclusion,
        AuthenticityLevel,
    ]

    missing_keys = []
    for enum_cls in enums_to_check:
        for member in enum_cls:
            if member.value not in en_data:
                missing_keys.append(member.value)

    assert not missing_keys, f"Missing L10n keys: {missing_keys}"
