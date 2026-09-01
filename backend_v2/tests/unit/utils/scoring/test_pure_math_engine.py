"""Unit tests for pure_math_engine.py."""

from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO
from backend_v2.utils.scoring.pure_math_engine import PureMathScoringEngine


def test_pure_math_scoring_engine_calculation() -> None:
    engine = PureMathScoringEngine()
    stats = {
        1.0: LevelStatsDTO(hits=2, total=2),
        2.0: LevelStatsDTO(hits=1, total=2),
        3.0: LevelStatsDTO(hits=0, total=2),
    }

    score, xai_log, breakdown = engine.calculate(stats, math_min=1.0, math_max=5.0)

    # Max weights = 2*1 + 2*2 + 2*3 = 2 + 4 + 6 = 12
    # Achieved = 2*1 + 1*2 + 0*3 = 4
    # Ratio = 4/12 = 1/3
    # Score = 1.0 + (1/3)*(4.0) = 1.0 + 1.333 = 2.333
    assert abs(score - 2.333) < 0.01
    assert xai_log.pedagogical_key == "xai_pure_math_engine_breakdown"
    assert "1.0" in breakdown


def test_pure_math_scoring_engine_empty_stats() -> None:
    engine = PureMathScoringEngine()
    score, xai_log, breakdown = engine.calculate({}, math_min=1.0, math_max=5.0)
    assert score == 1.0
    assert breakdown == {}
