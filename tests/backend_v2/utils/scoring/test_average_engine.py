import pytest
from backend_v2.utils.scoring.average_engine import PureAverageScoringEngine, WeightedAverageScoringEngine

def test_weighted_average_monotonicity():
    """Ensure Weighted Average (Sigmoid) monotonic behavior."""
    engine = WeightedAverageScoringEngine()
    
    stats = {
        1.0: {"hits": 0, "total": 10},
    }
    
    prev_score = -1.0
    for strictness in [20, 50, 80]:
        for hit_rate in range(0, 101, 1):
            stats[1.0]["hits"] = hit_rate / 100 * 10
            score, log, bd = engine.calculate(stats, 1.0, 5.0, strictness_level=strictness)
            assert score >= prev_score
            prev_score = score
        prev_score = -1.0

def test_pure_average_monotonicity():
    """Ensure Pure Average monotonic behavior."""
    engine = PureAverageScoringEngine()
    
    stats = {
        1.0: {"hits": 0, "total": 10},
    }
    
    prev_score = -1.0
    for strictness in [20, 50, 80]:
        for hit_rate in range(0, 101, 1):
            stats[1.0]["hits"] = hit_rate / 100 * 10
            score, log, bd = engine.calculate(stats, 1.0, 5.0, strictness_level=strictness)
            assert score >= prev_score
            prev_score = score
        prev_score = -1.0

def test_pure_average_outlier_rejection():
    """Ensure Outlier Mitigation Tests: Pass [1.0, 1.0, 0.0, 1.0]."""
    engine = PureAverageScoringEngine()
    
    stats = {
        1.0: {"hits": 10, "total": 10}, # 1.0
        2.0: {"hits": 10, "total": 10}, # 1.0
        3.0: {"hits": 0, "total": 10},  # 0.0 - OUTLIER
        4.0: {"hits": 10, "total": 10}, # 1.0
    }
    
    score, log, bd = engine.calculate(stats, 1.0, 5.0, strictness_level=50)
    
    # Without outlier rejection, mean is 0.75 hit rate.
    # 0.75 * 4 = 3.0 -> +1.0 = 4.0
    # With outlier rejection, 3.0 weight is reduced.
    # Let's just assert that score > 4.0 (closer to 5.0).
    assert score > 4.0
