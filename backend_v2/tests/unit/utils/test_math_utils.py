import pytest
from backend_v2.utils.math_utils import (
    convert_strictness_to_forgiveness,
    calculate_soft_waterfall_score,
    calculate_progressive_dampening_score,
    normalize_score_to_100,
    calculate_scaled_score,
    scale_to_custom_range,
    calculate_weighted_score,
)
from backend_v2.exceptions import AppException


def test_normalize_score_to_100():
    """Test proportional normalization math."""
    assert normalize_score_to_100(3.0, 1.0, 5.0) == 50.0
    assert normalize_score_to_100(5.0, 1.0, 5.0) == 100.0
    assert normalize_score_to_100(0.0, 1.0, 5.0) == 0.0
    with pytest.raises(AppException):
        normalize_score_to_100(3.0, 5.0, 1.0)


def test_calculate_scaled_score():
    """Test absolute scaled score bounds."""
    assert calculate_scaled_score(3.0, 5, 1.0, 5.0) == 3.0
    assert calculate_scaled_score(6.0, 5, 1.0, 5.0) == 5.0
    assert calculate_scaled_score(0.0, 5, 1.0, 5.0) == 1.0
    with pytest.raises(AppException):
        calculate_scaled_score(3.0, 5, 5.0, 1.0)


def test_scale_to_custom_range():
    """Test linear custom range scaling."""
    assert scale_to_custom_range(3.0, 1.0, 5.0, 4.0, 10.0) == 7.0
    assert scale_to_custom_range(5.0, 1.0, 5.0, 4.0, 10.0) == 10.0
    assert scale_to_custom_range(0.0, 1.0, 5.0, 4.0, 10.0) == 4.0
    with pytest.raises(AppException):
        scale_to_custom_range(3.0, 5.0, 1.0, 4.0, 10.0)


def test_calculate_weighted_score():
    """Test weighted score accumulation math."""
    level_stats = {
        1.0: {"hits": 1, "total": 1},
        5.0: {"hits": 1, "total": 1},
    }
    assert calculate_weighted_score(level_stats, 1.0, 5.0) == 5.0
    
    level_stats_empty = {
        1.0: {"hits": 0, "total": 0},
    }
    assert calculate_weighted_score(level_stats_empty, 1.0, 5.0) == 1.0
    
    with pytest.raises(AppException):
        calculate_weighted_score({}, 5.0, 1.0)


def test_convert_strictness_to_forgiveness_all_branches():
    """Test all interpolation boundaries for strictness conversion."""
    assert convert_strictness_to_forgiveness(0) == 1.0
    assert abs(convert_strictness_to_forgiveness(10) - (1.0 - (10/15.0)*0.40)) < 0.001
    assert convert_strictness_to_forgiveness(15) == 0.60
    assert abs(convert_strictness_to_forgiveness(30) - (0.60 - (15/35.0)*0.30)) < 0.001
    assert convert_strictness_to_forgiveness(50) == 0.30
    assert abs(convert_strictness_to_forgiveness(60) - (0.30 - (10/35.0)*0.20)) < 0.001
    assert convert_strictness_to_forgiveness(85) == 0.10
    assert abs(convert_strictness_to_forgiveness(90) - (0.10 - (5/15.0)*0.10)) < 0.001
    assert convert_strictness_to_forgiveness(100) == 0.00
    assert convert_strictness_to_forgiveness(105) == 0.00
    assert convert_strictness_to_forgiveness(-5) == 1.0


def test_soft_waterfall_scaling_deterministic_differences():
    """Mathematically prove that strictness_level=15 yields a higher score than 85 for identical 0-hit rate stats."""
    level_stats = {
        1.0: {"hits": 1, "total": 1},
        2.0: {"hits": 0, "total": 1},
        3.0: {"hits": 1, "total": 1},
    }
    
    score_15 = calculate_soft_waterfall_score(level_stats, 1.0, 3.0, 0.75, 0.60)
    score_85 = calculate_soft_waterfall_score(level_stats, 1.0, 3.0, 0.75, 0.10)
    
    assert abs(score_15 - 1.60) < 0.001
    assert abs(score_85 - 1.10) < 0.001
    assert score_15 > score_85


def test_soft_waterfall_invalid_scale():
    with pytest.raises(AppException):
        calculate_soft_waterfall_score({}, 5.0, 1.0)


def test_progressive_dampening_deterministic_differences():
    """Mathematically prove that strictness_level=15 yields a higher score than 85 for identical 0-hit rate stats."""
    level_stats = {
        1.0: {"hits": 0, "total": 1},
        2.0: {"hits": 0, "total": 1},
        3.0: {"hits": 1, "total": 1},
    }
    
    score_15 = calculate_progressive_dampening_score(level_stats, 1.0, 3.0, 0.60)
    score_85 = calculate_progressive_dampening_score(level_stats, 1.0, 3.0, 0.10)
    
    assert abs(score_15 - 1.60) < 0.001
    assert abs(score_85 - 1.10) < 0.001
    assert score_15 > score_85


def test_progressive_dampening_invalid_scale():
    with pytest.raises(AppException):
        calculate_progressive_dampening_score({}, 5.0, 1.0)
