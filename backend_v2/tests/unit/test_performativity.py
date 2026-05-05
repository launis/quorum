"""Unit tests for Performativity Domain Models."""

from collections.abc import Generator
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.performativity import (
    LinguisticsResult,
    PerformativePattern,
    PerformativityAnalysis,
    PerformativityDTO,
    PerformativityHeuristic,
    PerformativityInput,
    PerformativityOutput,
    PreMortemAnalysis,
)
from backend_v2.models.enums import AuthenticityLevel


def test_performativity_fails_fast_on_invalid_authenticity() -> None:
    data = {
        "performativity_heuristics": [{"heuristic_name": "Test", "flag_raised": False, "description": "Desc"}],
        "pre_mortem_analysis": {"performed": True, "weak_signals": ["signal1"]},
        "authenticity_assessment": "INVALID",
        "description": "Desc",
    }
    with pytest.raises(ValidationError) as exc_info:
        PerformativityAnalysis.model_validate(data)
    assert "Invalid AuthenticityLevel 'INVALID'" in str(exc_info.value)


def test_performativity_heuristic_empty_strings_fail() -> None:
    with pytest.raises(ValidationError):
        PerformativityHeuristic(heuristic_name="", flag_raised=False, description="Desc")


def test_pre_mortem_empty_signals_fail() -> None:
    with pytest.raises(ValidationError):
        PreMortemAnalysis(performed=True, weak_signals=[])


def test_performativity_analysis_valid() -> None:
    heur = PerformativityHeuristic(heuristic_name="H1", flag_raised=True, description="D1")
    pm = PreMortemAnalysis(performed=True, weak_signals=["S1"])
    data = PerformativityAnalysis(
        performativity_heuristics=[heur],
        pre_mortem_analysis=pm,
        authenticity_assessment=AuthenticityLevel.PERFORMATIVE,
        authenticity_score=2.0,
    )
    assert data.authenticity_score == 2.0
    assert data.description != ""


def test_performativity_analysis_empty_heuristics_fail() -> None:
    pm = PreMortemAnalysis(performed=True, weak_signals=["S1"])
    with pytest.raises(ValidationError):
        PerformativityAnalysis(
            performativity_heuristics=[],
            pre_mortem_analysis=pm,
            authenticity_assessment=AuthenticityLevel.PERFORMATIVE,
            authenticity_score=2.0,
        )


def test_performativity_input_valid() -> None:
    inp = PerformativityInput(chat_log="Hello")
    assert inp.chat_log == "Hello"


def test_performativity_input_empty_chat_log_fail() -> None:
    with pytest.raises(ValidationError):
        PerformativityInput(chat_log="")


def test_performativity_input_extra_forbid() -> None:
    with pytest.raises(ValidationError):
        PerformativityInput.model_validate({"chat_log": "Hello", "extra": "Forbidden"})


def test_performativity_dto_and_output() -> None:
    heur = PerformativityHeuristic(heuristic_name="H1", flag_raised=True, description="D1")
    pm = PreMortemAnalysis(performed=True, weak_signals=["S1"])
    data = PerformativityAnalysis(
        performativity_heuristics=[heur],
        pre_mortem_analysis=pm,
        authenticity_assessment=AuthenticityLevel.PERFORMATIVE,
        authenticity_score=2.0,
    )
    dto = PerformativityDTO(
        thought_process="Thinking",
        conclusion="Done",
        confidence_score=0.9,
        performativity_analysis=data,
    )
    assert dto.confidence_score == 0.9

    out = PerformativityOutput(
        thought_process="Thinking",
        conclusion="Done",
        confidence_score=0.9,
        performativity_analysis=data,
    )
    assert out.thought_process == "Thinking"


def test_performative_pattern_empty_strings_fail() -> None:
    with pytest.raises(ValidationError):
        PerformativePattern(pattern_id="", detected_phrase="Phrase", category="Cat")


def test_linguistics_result() -> None:
    pat = PerformativePattern(pattern_id="P1", detected_phrase="Phrase", category="Cat")
    res = LinguisticsResult(performative_patterns=[pat])
    assert len(res.performative_patterns) == 1
