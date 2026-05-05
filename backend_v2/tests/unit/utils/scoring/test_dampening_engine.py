import pytest
from backend_v2.utils.scoring.dampening_engine import DampeningScoringEngine


def test_dampening_engine_calculate():
    engine = DampeningScoringEngine()
    stats = {
        1.0: {"hits": 1, "total": 1},
        2.0: {"hits": 0, "total": 1},
    }
    score, log, breakdown = engine.calculate(stats, math_min=1.0, math_max=3.0, strictness_level=50)
    
    # Mathematical bounds test
    assert score >= 1.0 and score <= 3.0
    
    # String breakdown test for UI
    assert "Tasolta 2.0 saatiin 0 osumaa. Käytetään Strictness 50:n mukaista joustokerrointa (0.30), joten pisteitä vaimennettiin pehmeästi." in log
    
    # Standard log checks
    assert "Progressively dampened" in log
    assert breakdown["1.0"]["hits"] == 1
    
def test_dampening_engine_optimal_flow():
    engine = DampeningScoringEngine()
    stats = {
        1.0: {"hits": 1, "total": 1},
        2.0: {"hits": 1, "total": 1},
    }
    score, log, breakdown = engine.calculate(stats, math_min=1.0, math_max=3.0, strictness_level=0)
    assert "OPTIMAL" in log
