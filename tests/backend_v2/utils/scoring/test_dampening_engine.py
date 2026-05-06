import pytest
from backend_v2.utils.scoring.dampening_engine import DampeningScoringEngine

def test_dampening_monotonicity():
    """Ensure Dampening monotonic behavior (Syväarvostelu)."""
    engine = DampeningScoringEngine()
    
    stats = {
        1.0: {"hits": 0, "total": 10},
        2.0: {"hits": 0, "total": 10},
    }
    
    prev_score = -1.0
    for strictness in [20, 50, 80]:
        for hit_rate in range(0, 101, 1): # 0.0 to 1.0 in 0.01 increments
            stats[1.0]["hits"] = hit_rate / 100 * 10
            stats[2.0]["hits"] = hit_rate / 100 * 10
            score, log, bd = engine.calculate(stats, 1.0, 3.0, strictness_level=strictness)
            assert score >= prev_score
            prev_score = score
        prev_score = -1.0

def test_dampening_boundary():
    """Ensure Dampening respects math bounds."""
    engine = DampeningScoringEngine()
    
    # 0.0 hits
    stats_zero = {
        1.0: {"hits": 0, "total": 10},
        2.0: {"hits": 0, "total": 10},
    }
    score_zero, _, _ = engine.calculate(stats_zero, 1.0, 3.0, strictness_level=50)
    assert score_zero == 1.0
    
    # 1.0 hits
    stats_perfect = {
        1.0: {"hits": 10, "total": 10},
        2.0: {"hits": 10, "total": 10},
    }
    score_perfect, _, _ = engine.calculate(stats_perfect, 1.0, 3.0, strictness_level=50)
    assert score_perfect == 3.0
