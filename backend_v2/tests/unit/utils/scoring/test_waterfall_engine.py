import pytest
from backend_v2.utils.scoring.waterfall_engine import WaterfallScoringEngine


def test_waterfall_engine_calculate_lenient():
    engine = WaterfallScoringEngine()
    stats = {
        1.0: {"hits": 1, "total": 1},
        2.0: {"hits": 0, "total": 1},
        3.0: {"hits": 1, "total": 1},
    }
    # Strictness 15 -> Lenient, Forgiveness 0.60
    score, log, breakdown = engine.calculate(stats, math_min=1.0, math_max=3.0, strictness_level=15)
    
    assert score > 1.0
    assert "Soft Benefit of the Doubt" in log
    assert "Subsequent multiplier reduced to 0.60 due to strictness 15" in log


def test_waterfall_engine_calculate_strict():
    engine = WaterfallScoringEngine()
    stats = {
        1.0: {"hits": 1, "total": 1},
        2.0: {"hits": 0, "total": 1},
        3.0: {"hits": 1, "total": 1},
    }
    # Strictness 85 -> Strict, Forgiveness 0.10
    score, log, breakdown = engine.calculate(stats, math_min=1.0, math_max=3.0, strictness_level=85)
    
    assert score > 1.0
    assert "Subsequent multiplier reduced to 0.10 due to strictness 85" in log
    
def test_waterfall_engine_calculate_standard():
    engine = WaterfallScoringEngine()
    stats = {
        1.0: {"hits": 1, "total": 1},
        2.0: {"hits": 1, "total": 1},
        3.0: {"hits": 1, "total": 1},
    }
    # Strictness 50 -> Standard
    score, log, breakdown = engine.calculate(stats, math_min=1.0, math_max=3.0, strictness_level=50)
    
    assert score == 3.0
    assert "PASSED" in log
