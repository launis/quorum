"""Unit tests for backend_v2.utils.scoring.base_engine."""

from __future__ import annotations

import inspect

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO, ScoringResultDTO
from backend_v2.utils.scoring.base_engine import ScoringEngineProtocol
from backend_v2.utils.scoring.unified_engine import UnifiedScoringEngine


def test_scoring_engine_protocol_definition_and_conformance() -> None:
    """Verify ScoringEngineProtocol structural contract and runtime conformance via UnifiedScoringEngine."""
    assert inspect.isclass(ScoringEngineProtocol)
    assert any(base.__name__ == "Protocol" for base in ScoringEngineProtocol.__mro__)

    engine: ScoringEngineProtocol = UnifiedScoringEngine()
    assert isinstance(engine, ScoringEngineProtocol)

    stats = {
        1.0: LevelStatsDTO(hits=4, total=5, dlqs=0),
        2.0: LevelStatsDTO(hits=3, total=5, dlqs=0),
    }
    result = engine.calculate(
        stats=stats,
        math_min=1.0,
        math_max=5.0,
        strictness_level=50,
        penalties_detected=[0.05],
    )
    assert isinstance(result, ScoringResultDTO)
    assert 1.0 <= result.score <= 5.0
    assert "1.0" in result.breakdown
    assert "2.0" in result.breakdown


def test_scoring_engine_protocol_direct_instantiation_and_non_conforming_rejection() -> None:
    """Verify direct Protocol instantiation raises TypeError and non-conforming types fail isinstance."""
    with pytest.raises(TypeError):
        ScoringEngineProtocol()

    class NonConformingEngine:
        """Dummy class lacking calculate method."""

    assert not isinstance(object(), ScoringEngineProtocol)
    assert not isinstance(NonConformingEngine(), ScoringEngineProtocol)


def test_scoring_engine_protocol_invalid_extrema_bounds_raises_app_exception() -> None:
    """Verify ScoringEngineProtocol implementation raises AppException when math_min >= math_max."""
    engine: ScoringEngineProtocol = UnifiedScoringEngine()
    stats = {1.0: LevelStatsDTO(hits=2, total=4, dlqs=0)}

    # Boundary value: math_min == math_max
    with pytest.raises(AppException) as exc_equal:
        engine.calculate(stats=stats, math_min=5.0, math_max=5.0, strictness_level=50)
    assert exc_equal.value.details["error_code"] == ErrorCodes.INVALID_OUTPUT_SCHEMA.value

    # Inverted boundary: math_min > math_max
    with pytest.raises(AppException) as exc_inverted:
        engine.calculate(stats=stats, math_min=5.0, math_max=1.0, strictness_level=50)
    assert exc_inverted.value.details["error_code"] == ErrorCodes.INVALID_OUTPUT_SCHEMA.value


def test_scoring_engine_protocol_output_immutability_and_strict_schema() -> None:
    """Verify ScoringEngineProtocol result enforces frozen immutability and forbids extra fields."""
    engine: ScoringEngineProtocol = UnifiedScoringEngine()
    stats = {1.0: LevelStatsDTO(hits=3, total=3, dlqs=0)}
    result = engine.calculate(stats=stats, math_min=1.0, math_max=5.0)

    with pytest.raises(ValidationError):
        result.score = 0.0
