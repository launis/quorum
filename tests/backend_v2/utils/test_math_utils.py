import pytest
from backend_v2.utils.math_utils import calculate_progressive_dampening_score
from backend_v2.exceptions import AppException

def test_dampening_all_zeros():
    stats = {
        1.0: {"hits": 0, "total": 15},
        2.0: {"hits": 0, "total": 15},
        3.0: {"hits": 0, "total": 15},
    }
    score = calculate_progressive_dampening_score(stats, 1.0, 5.0)
    assert score == 1.0

def test_dampening_no_foundation_high_ceiling():
    """Fail Fast requirement: Attempting to get higher score without Level 1 must be mathematically impossible."""
    stats = {
        1.0: {"hits": 0, "total": 15}, # 0% modifier
        2.0: {"hits": 15, "total": 15},
        3.0: {"hits": 15, "total": 15},
        4.0: {"hits": 15, "total": 15},
        5.0: {"hits": 15, "total": 15},
    }
    score = calculate_progressive_dampening_score(stats, 1.0, 5.0)
    # The modifier will be 0.0, so no value can be added beyond scale_min
    assert score == 1.0

def test_dampening_weak_foundation_high_ceiling():
    """Validation for Epic: Level 5 100% must provide only a microscopic addition if Level 1 is weak (10%)."""
    stats = {
        1.0: {"hits": 1, "total": 10},  # 10%
        2.0: {"hits": 5, "total": 10},  # 50%
        3.0: {"hits": 5, "total": 10},  # 50%
        4.0: {"hits": 5, "total": 10},  # 50%
        5.0: {"hits": 10, "total": 10}, # 100%
    }
    score = calculate_progressive_dampening_score(stats, 1.0, 5.0)
    assert pytest.approx(score, 0.001) == 1.1

def test_dampening_perfect_score():
    stats = {
        1.0: {"hits": 10, "total": 10},
        2.0: {"hits": 10, "total": 10},
        3.0: {"hits": 10, "total": 10},
        4.0: {"hits": 10, "total": 10},
        5.0: {"hits": 10, "total": 10},
    }
    score = calculate_progressive_dampening_score(stats, 1.0, 5.0)
    assert score == 5.0

def test_dampening_out_of_bounds():
    stats = {1.0: {"hits": 10, "total": 10}}
    with pytest.raises(AppException) as excinfo:
        calculate_progressive_dampening_score(stats, 5.0, 1.0)
    assert "Invalid scale definition" in str(excinfo.value)
