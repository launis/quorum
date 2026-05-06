import pytest
from backend_v2.utils.scoring.waterfall_engine import WaterfallScoringEngine
from backend_v2.models.enums import StrictnessAnchor

def test_waterfall_monotonicity():
    """Ensure Waterfall monotonic behavior (Koearvostelu)."""
    engine = WaterfallScoringEngine()
    
    stats = {
        1.0: {"hits": 0, "total": 10},
        2.0: {"hits": 0, "total": 10},
    }
    
    prev_score = -1.0
    for hit_rate in range(0, 101, 5): # 0.0 to 1.0
        stats[1.0]["hits"] = int(hit_rate / 100 * 10)
        stats[2.0]["hits"] = int(hit_rate / 100 * 10)
        score, log, bd = engine.calculate(stats, 1.0, 3.0, strictness_level=85)
        assert score >= prev_score
        prev_score = score

def test_waterfall_sliding_penalty_cascade():
    """Test sliding penalty cascades only to subsequent levels."""
    engine = WaterfallScoringEngine()
    
    stats = {
        1.0: {"hits": 5, "total": 10},  # Level 1: 50%
        2.0: {"hits": 10, "total": 10}, # Level 2: 100%
        3.0: {"hits": 10, "total": 10}, # Level 3: 100%
    }
    
    score, log, bd = engine.calculate(stats, 1.0, 4.0, strictness_level=85)
    
    # Threshold for strictness 85 is 0.70. base_forgiveness = 0.10.
    # Level 1: achieved = 1.0 + 1.0 * 0.5 * 1.0 = 1.5
    # shortfall = (0.7 - 0.5)/0.7 = 0.2857.
    # sliding_penalty = 1.0 - (0.2857 * 0.9) = 0.7428.
    # Level 2: hit_rate=1.0. points = 1.0 * 1.0 * 0.7428 = 0.7428.
    # Level 3: hit_rate=1.0. points = 1.0 * 1.0 * 0.7428 = 0.7428.
    # Total score = 1.5 + 0.7428 + 0.7428 = 2.9856...
    
    assert score > 2.98
    assert score < 2.99
    
def test_waterfall_all_zeros():
    engine = WaterfallScoringEngine()
    stats = {
        1.0: {"hits": 0, "total": 10},
        2.0: {"hits": 0, "total": 10},
    }
    score, _, _ = engine.calculate(stats, 1.0, 3.0, strictness_level=85)
    assert score == 1.0

def test_waterfall_all_perfect():
    engine = WaterfallScoringEngine()
    stats = {
        1.0: {"hits": 10, "total": 10},
        2.0: {"hits": 10, "total": 10},
    }
    score, _, _ = engine.calculate(stats, 1.0, 3.0, strictness_level=85)
    assert score == 3.0
