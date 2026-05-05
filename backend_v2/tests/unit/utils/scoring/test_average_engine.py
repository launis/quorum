import pytest
from backend_v2.utils.scoring.average_engine import PureAverageScoringEngine, WeightedAverageScoringEngine


def test_pure_average_engine_calculate():
    engine = PureAverageScoringEngine()
    stats = {
        1.0: {"hits": 1, "total": 1},
        2.0: {"hits": 0, "total": 1},
    }
    # Strictness 50 -> Forgiveness 0.30 -> Exponent 1.70
    score, log, breakdown = engine.calculate(stats, math_min=1.0, math_max=3.0, strictness_level=50)
    
    assert score >= 1.0 and score <= 3.0
    assert "Mapped to scale 1.0-3.0 with exponent 1.70 based on strictness 50" in log


def test_weighted_average_engine_calculate():
    engine = WeightedAverageScoringEngine()
    stats = {
        1.0: {"hits": 1, "total": 1},
        2.0: {"hits": 0, "total": 1},
    }
    # Strictness 85 -> Forgiveness 0.10 -> Exponent 1.90
    score, log, breakdown = engine.calculate(stats, math_min=1.0, math_max=3.0, strictness_level=85)
    
    assert score >= 1.0 and score <= 3.0
    assert "with exponent 1.90" in log
    assert "Weighted Points Achieved" in log
