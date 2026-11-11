"""Unit tests for the scoring package facade and factory."""

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO
from backend_v2.utils.scoring import (
    ScoringEngineProtocol,
    ScoringResultDTO,
    UnifiedScoringEngine,
    get_scoring_engine,
)


def test_get_scoring_engine() -> None:
    """Verify get_scoring_engine returns a valid UnifiedScoringEngine implementing ScoringEngineProtocol."""
    engine = get_scoring_engine()
    assert isinstance(engine, ScoringEngineProtocol)
    assert isinstance(engine, UnifiedScoringEngine)
    result = engine.calculate(
        stats={1.0: LevelStatsDTO(hits=5, total=10, dlqs=0)},
        math_min=1.0,
        math_max=5.0,
        strictness_level=50,
    )
    assert isinstance(result, ScoringResultDTO)


def test_get_scoring_engine_legacy_arg() -> None:
    """Verify get_scoring_engine ignores optional strategy argument and returns UnifiedScoringEngine."""
    engine = get_scoring_engine("WATERFALL")
    assert isinstance(engine, ScoringEngineProtocol)
    assert isinstance(engine, UnifiedScoringEngine)


def test_get_scoring_engine_invalid_inverted_scale_bounds() -> None:
    """Verify engine returned by get_scoring_engine raises AppException when math_min > math_max."""
    engine = get_scoring_engine()
    stats = {1.0: LevelStatsDTO(hits=1, total=2, dlqs=0)}
    with pytest.raises(AppException):
        engine.calculate(stats=stats, math_min=5.0, math_max=1.0, strictness_level=50)


def test_get_scoring_engine_error_degenerate_equal_scale_bounds() -> None:
    """Verify engine returned by get_scoring_engine raises AppException when math_min == math_max."""
    engine = get_scoring_engine()
    stats = {1.0: LevelStatsDTO(hits=1, total=2, dlqs=0)}
    with pytest.raises(AppException):
        engine.calculate(stats=stats, math_min=3.0, math_max=3.0, strictness_level=50)
