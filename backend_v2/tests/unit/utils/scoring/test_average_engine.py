import pytest

from backend_v2.utils.scoring.average_engine import PureAverageScoringEngine, WeightedAverageScoringEngine
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO


def test_pure_average_engine_calculate() -> None:
    engine = PureAverageScoringEngine()
    stats = {
        1.0: LevelStatsDTO(hits=1, total=1),
        2.0: LevelStatsDTO(hits=0, total=1),
    }
    # Strictness 50 -> Forgiveness 0.30 -> Exponent 1.70
    score, log, breakdown = engine.calculate(
        stats,
        math_min=1.0,
        math_max=3.0,
    )

    assert score >= 1.0 and score <= 3.0
    log_str = "\n".join(log.engine_debug_trace["log_trace"])
    assert "Mapped to scale 1.0-3.0 with exponent 1.70 based on strictness 50" in log_str


def test_weighted_average_engine_calculate() -> None:
    engine = WeightedAverageScoringEngine()
    stats = {
        1.0: LevelStatsDTO(hits=1, total=1),
        2.0: LevelStatsDTO(hits=0, total=1),
    }
    # Strictness 85 -> Forgiveness 0.10 -> Exponent 1.90
    score, log, breakdown = engine.calculate(
        stats,
        math_min=1.0,
        math_max=3.0,
    )

    assert score >= 1.0 and score <= 3.0
    log_str = "\n".join(log.engine_debug_trace["log_trace"])
    assert "Mapped to scale" in log_str
    assert "Weighted Points Achieved" in log_str


def test_pure_average_engine_outlier_rejection() -> None:
    engine = PureAverageScoringEngine()
    # [1.0, 1.0, 0.0, 1.0] hit rates
    stats = {
        1.0: LevelStatsDTO(hits=1, total=1),
        2.0: LevelStatsDTO(hits=1, total=1),
        3.0: LevelStatsDTO(hits=0, total=1),  # This is the outlier (hit rate 0.0)
        4.0: LevelStatsDTO(hits=1, total=1),
    }

    score, log, _ = engine.calculate(stats, 1.0, 5.0, 50)

    # Assert outlier was mitigated
    log_str = "\n".join(log.engine_debug_trace["log_trace"])
    assert "Outlier Mitigated at Level 3.0" in log_str

    # Standard mean ratio would be 3/4 = 0.75.
    # Mitigated hits: 3 * 1 + 0 * 0.25 = 3
    # Mitigated total: 3 * 1 + 1 * 0.25 = 3.25
    # Ratio = 3 / 3.25 = 0.923 (much higher because the 0.0 was reduced)
    # The score should reflect this higher ratio.
    # With exponent 1.70, score is mapped from 1 to 5.

    # Just verify that the mitigated ratio is computed
    assert "0.25x" in log_str


def test_weighted_average_engine_linear_monotonicity() -> None:
    engine = WeightedAverageScoringEngine()

    previous_score = -1.0
    for i in range(101):
        hit_rate = i / 100.0
        stats = {
            1.0: LevelStatsDTO(hits=int(hit_rate * 100), total=100),
            2.0: LevelStatsDTO(hits=int(hit_rate * 100), total=100),
        }
        score, log, _ = engine.calculate(
            stats,
            1.0,
            5.0,
        )

        assert score >= previous_score
        previous_score = score

        if hit_rate == 0.0:
            assert abs(score - 1.0) < 0.001
        elif hit_rate == 1.0:
            assert abs(score - 5.0) < 0.001
