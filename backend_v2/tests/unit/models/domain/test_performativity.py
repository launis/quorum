from unittest.mock import AsyncMock
import pytest
from pydantic import ValidationError

from backend_v2.models.domain.performativity import (
    PerformativityAnalysis,
    PerformativityInput,
    PerformativityOutput,
)
from backend_v2.models.enums import AuthenticityLevel


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
        "authenticity_score": 3.0,
    }
    analysis = PerformativityAnalysis.model_validate(data)
    assert analysis.authenticity_score == 3.0
    assert analysis.authenticity_assessment == AuthenticityLevel.ORGANIC

    # Fail fast if authenticity_score is omitted
    del data["authenticity_score"]
    with pytest.raises(ValidationError) as exc_info:
        PerformativityAnalysis.model_validate(data)
    assert "authenticity_score" in str(exc_info.value)


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
        "authenticity_assessment": "AUTH_ORGANIC",
        "authenticity_score": 3.0,
    }
    analysis = PerformativityAnalysis.model_validate(data)
    assert analysis.authenticity_score == 3.0
    assert analysis.authenticity_assessment == AuthenticityLevel.ORGANIC


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
        "authenticity_score": 3.0,
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
            "authenticity_assessment": "AUTH_PERFORMATIVE",
            "authenticity_score": 2.0,
        },
        "reasoning_trace": "Analysis complete.",
        "calculation_log": [],
        "rogue_field": "Should fail",
    }
    with pytest.raises(ValidationError):
        PerformativityOutput.model_validate(data)
