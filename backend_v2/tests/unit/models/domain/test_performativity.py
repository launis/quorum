import pytest
from pydantic import ValidationError

from backend_v2.models.enums import AuthenticityLevel
from backend_v2.models.domain.performativity import (
    PerformativityInput,
    PerformativityAnalysis,
    PerformativityOutput,
)


def test_performativity_input_requires_chatlog() -> None:
    """Test that PerformativityInput requires chat_log."""
    data = {"step_analyst": None}
    with pytest.raises(ValidationError):
        PerformativityInput.model_validate(data)


def test_performativity_analysis_authenticity_enum() -> None:
    """Test PerformativityAnalysis parsing AuthenticityLevel via Enum and score assignment."""
    data = {
        "performativity_heuristics": [
            {
                "heuristic_name": "Jargon Overload",
                "flag_raised": True,
                "description": "Uses too much jargon.",
            }
        ],
        "pre_mortem_analysis": {
            "performed": True,
            "weak_signals": ["Signal 1"],
        },
        "authenticity_assessment": AuthenticityLevel.ORGANIC,
    }
    analysis = PerformativityAnalysis.model_validate(data)
    assert getattr(analysis, "authenticity_score") == 3.0
    assert getattr(analysis, "authenticity_assessment") == AuthenticityLevel.ORGANIC


def test_performativity_analysis_authenticity_string() -> None:
    """Test PerformativityAnalysis parsing AuthenticityLevel via String."""
    data = {
        "performativity_heuristics": [
            {
                "heuristic_name": "Jargon Overload",
                "flag_raised": True,
                "description": "Uses too much jargon.",
            }
        ],
        "pre_mortem_analysis": {
            "performed": True,
            "weak_signals": ["Signal 1"],
        },
        "authenticity_assessment": "LEVEL_ORGANIC",
    }
    analysis = PerformativityAnalysis.model_validate(data)
    assert getattr(analysis, "authenticity_score") == 3.0
    assert getattr(analysis, "authenticity_assessment") == AuthenticityLevel.ORGANIC


def test_performativity_analysis_invalid_authenticity() -> None:
    """Test that PerformativityAnalysis raises ValidationError on invalid AuthenticityLevel."""
    data = {
        "performativity_heuristics": [
            {
                "heuristic_name": "Jargon",
                "flag_raised": False,
                "description": "Clear.",
            }
        ],
        "pre_mortem_analysis": {
            "performed": True,
            "weak_signals": ["Signal 1"],
        },
        "authenticity_assessment": "INVALID_LEVEL",
    }
    with pytest.raises(ValidationError):
        PerformativityAnalysis.model_validate(data)


def test_performativity_output_frozen_and_strict() -> None:
    """Test that PerformativityOutput rejects unknown fields and is frozen."""
    data = {
        "performativity_analysis": {
            "performativity_heuristics": [
                {
                    "heuristic_name": "Test",
                    "flag_raised": False,
                    "description": "Test",
                }
            ],
            "pre_mortem_analysis": {
                "performed": True,
                "weak_signals": ["Signal"],
            },
            "authenticity_assessment": "LEVEL_PERFORMATIVE",
        },
        "reasoning_trace": "Analysis complete.",
        "calculation_log": [],
        "rogue_field": "Should fail",
    }
    with pytest.raises(ValidationError):
        PerformativityOutput.model_validate(data)
