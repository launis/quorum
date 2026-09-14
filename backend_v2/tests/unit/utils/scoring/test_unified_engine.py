"""Unit tests for UnifiedScoringEngine and continuous strictness calculation."""

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO, ScoringResultDTO
from backend_v2.utils.scoring.unified_engine import (
    UnifiedScoringEngine,
    calculate_strictness_exponent,
)


def test_calculate_strictness_exponent_anchor_points() -> None:
    """Verify exact anchor points for continuous strictness exponent."""
    assert calculate_strictness_exponent(-10) == 1.0
    assert calculate_strictness_exponent(0) == 1.0
    assert calculate_strictness_exponent(50) == 1.25
    assert calculate_strictness_exponent(85) == 1.70
    assert calculate_strictness_exponent(100) == 2.20
    assert calculate_strictness_exponent(110) == 2.20


def test_calculate_strictness_exponent_monotonicity() -> None:
    """Verify that the exponent increases monotonically across the full 0-100 range."""
    prev_exponent = calculate_strictness_exponent(0)
    for level in range(1, 101):
        curr_exponent = calculate_strictness_exponent(level)
        assert curr_exponent >= prev_exponent, f"Monotonicity violated at level {level}"
        prev_exponent = curr_exponent


def test_calculate_strictness_exponent_interpolation() -> None:
    """Verify continuous piecewise interpolation between anchor points."""
    # Midpoint of 0-50 (level 25): 1.0 + (25/50)*0.25 = 1.125
    assert abs(calculate_strictness_exponent(25) - 1.125) < 1e-6

    # Midpoint of 50-85 (level 67.5 -> let's test integer 67)
    exp_67 = calculate_strictness_exponent(67)
    expected_67 = 1.25 + ((67 - 50.0) / 35.0) * 0.45
    assert abs(exp_67 - expected_67) < 1e-6


def test_unified_scoring_engine_basic_calculation() -> None:
    """Verify basic calculation returns typed ScoringResultDTO."""
    engine = UnifiedScoringEngine()
    stats = {
        1.0: LevelStatsDTO(hits=5, total=10, dlqs=0),
        2.0: LevelStatsDTO(hits=8, total=10, dlqs=0),
    }

    result = engine.calculate(stats=stats, math_min=1.0, math_max=5.0, strictness_level=50)

    assert isinstance(result, ScoringResultDTO)
    assert 1.0 <= result.score <= 5.0
    assert result.xai_log.pedagogical_key == "xai_unified_engine_breakdown"
    assert result.xai_log.engine_debug_trace["engine"] == "unified"
    assert result.xai_log.engine_debug_trace["strictness_level"] == 50
    assert "1.0" in result.breakdown
    assert result.breakdown["1.0"]["hits"] == 5


def test_unified_scoring_engine_strictness_impact() -> None:
    """Verify higher strictness decreases score for partial performance."""
    engine = UnifiedScoringEngine()
    stats = {
        1.0: LevelStatsDTO(hits=5, total=10, dlqs=0),
        2.0: LevelStatsDTO(hits=3, total=10, dlqs=0),
    }

    res_0 = engine.calculate(stats=stats, math_min=1.0, math_max=5.0, strictness_level=0)
    res_50 = engine.calculate(stats=stats, math_min=1.0, math_max=5.0, strictness_level=50)
    res_85 = engine.calculate(stats=stats, math_min=1.0, math_max=5.0, strictness_level=85)
    res_100 = engine.calculate(stats=stats, math_min=1.0, math_max=5.0, strictness_level=100)

    assert res_0.score >= res_50.score >= res_85.score >= res_100.score


def test_unified_scoring_engine_perfect_score() -> None:
    """Verify 100% hits yields math_max regardless of strictness."""
    engine = UnifiedScoringEngine()
    stats = {
        1.0: LevelStatsDTO(hits=10, total=10, dlqs=0),
        2.0: LevelStatsDTO(hits=10, total=10, dlqs=0),
    }

    res_0 = engine.calculate(stats=stats, math_min=1.0, math_max=5.0, strictness_level=0)
    res_100 = engine.calculate(stats=stats, math_min=1.0, math_max=5.0, strictness_level=100)

    assert abs(res_0.score - 5.0) < 1e-6
    assert abs(res_100.score - 5.0) < 1e-6


def test_unified_scoring_engine_zero_score() -> None:
    """Verify 0% hits yields math_min regardless of strictness."""
    engine = UnifiedScoringEngine()
    stats = {
        1.0: LevelStatsDTO(hits=0, total=10, dlqs=0),
        2.0: LevelStatsDTO(hits=0, total=10, dlqs=0),
    }

    res_0 = engine.calculate(stats=stats, math_min=1.0, math_max=5.0, strictness_level=0)
    res_100 = engine.calculate(stats=stats, math_min=1.0, math_max=5.0, strictness_level=100)

    assert abs(res_0.score - 1.0) < 1e-6
    assert abs(res_100.score - 1.0) < 1e-6


def test_unified_scoring_engine_dlq_exclusion() -> None:
    """Verify dlqs are deducted from total in calculation."""
    engine = UnifiedScoringEngine()
    # 5 hits out of 5 effective total (10 total - 5 dlqs) = 100% effective hit rate
    stats = {
        1.0: LevelStatsDTO(hits=5, total=10, dlqs=5),
    }

    result = engine.calculate(stats=stats, math_min=1.0, math_max=5.0, strictness_level=50)
    assert abs(result.score - 5.0) < 1e-6


def test_unified_scoring_engine_invalid_scale_raises() -> None:
    """Verify math_min >= math_max raises AppException."""
    engine = UnifiedScoringEngine()
    stats = {1.0: LevelStatsDTO(hits=5, total=10, dlqs=0)}

    with pytest.raises(AppException):
        engine.calculate(stats=stats, math_min=5.0, math_max=1.0, strictness_level=50)


def test_unified_scoring_engine_dto_immutability() -> None:
    """Verify ScoringResultDTO is frozen and immutable."""
    engine = UnifiedScoringEngine()
    stats = {1.0: LevelStatsDTO(hits=5, total=10, dlqs=0)}
    result = engine.calculate(stats=stats, math_min=1.0, math_max=5.0, strictness_level=50)

    with pytest.raises(ValidationError):
        # Trying to mutate frozen Pydantic model raises error
        result.score = 99.0  # type: ignore[misc]
