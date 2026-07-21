from unittest.mock import AsyncMock
import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO
from backend_v2.utils.math_utils import (
    calculate_scaled_score,
    calculate_soft_waterfall_score,
    convert_strictness_to_forgiveness,
    normalize_score_to_100,
    scale_to_custom_range,
)


def test_normalize_score_to_100() -> None:
    """Test proportional normalization math."""
    assert normalize_score_to_100(3.0, 1.0, 5.0) == 50.0
    assert normalize_score_to_100(5.0, 1.0, 5.0) == 100.0
    assert normalize_score_to_100(0.0, 1.0, 5.0) == 0.0
    with pytest.raises(AppException):
        normalize_score_to_100(3.0, 5.0, 1.0)


def test_calculate_scaled_score() -> None:
    """Test absolute scaled score bounds."""
    assert calculate_scaled_score(3.0, 5, 1.0, 5.0) == 3.0
    assert calculate_scaled_score(6.0, 5, 1.0, 5.0) == 5.0
    assert calculate_scaled_score(0.0, 5, 1.0, 5.0) == 1.0
    with pytest.raises(AppException):
        calculate_scaled_score(3.0, 5, 5.0, 1.0)


def test_scale_to_custom_range() -> None:
    """Test linear custom range scaling."""
    assert scale_to_custom_range(3.0, 1.0, 5.0, 4.0, 10.0) == 7.0
    assert scale_to_custom_range(5.0, 1.0, 5.0, 4.0, 10.0) == 10.0
    assert scale_to_custom_range(0.0, 1.0, 5.0, 4.0, 10.0) == 4.0
    with pytest.raises(AppException):
        scale_to_custom_range(3.0, 5.0, 1.0, 4.0, 10.0)


def test_convert_strictness_to_forgiveness_all_branches() -> None:
    """Test all interpolation boundaries for strictness conversion."""
    assert convert_strictness_to_forgiveness(85) == 0.10
    assert abs(convert_strictness_to_forgiveness(90) - (0.10 - (5 / 15.0) * 0.10)) < 0.001
    assert convert_strictness_to_forgiveness(100) == 0.00
    assert convert_strictness_to_forgiveness(105) == 0.00
    assert convert_strictness_to_forgiveness(50) == 0.30
    assert convert_strictness_to_forgiveness(0) == 0.50
    assert convert_strictness_to_forgiveness(-10) == 0.50


def test_soft_waterfall_scaling_deterministic_differences() -> None:
    """Mathematically prove that yields a higher score than 85 for identical 0-hit rate stats."""
    level_stats = {
        1.0: LevelStatsDTO(hits=1, total=1),
        2.0: LevelStatsDTO(hits=0, total=1),
        3.0: LevelStatsDTO(hits=1, total=1),
    }

    score_85 = calculate_soft_waterfall_score(level_stats, 1.0, 3.0, 0.75, 0.10)
    score_100 = calculate_soft_waterfall_score(level_stats, 1.0, 3.0, 0.75, 0.0)

    assert score_85 > score_100
    assert score_85 < 1.3


def test_soft_waterfall_invalid_scale() -> None:
    with pytest.raises(AppException):
        calculate_soft_waterfall_score({}, 5.0, 1.0)


def test_clamp_score_invalid_scale() -> None:
    from backend_v2.utils.math_utils import clamp_score

    with pytest.raises(AppException):
        clamp_score(3.0, 5.0, 1.0)


def test_calculate_linear_ratio_score() -> None:
    from backend_v2.utils.math_utils import calculate_linear_ratio_score

    stats = {
        1.0: LevelStatsDTO(hits=100, total=100),
        2.0: LevelStatsDTO(hits=50, total=100),
    }
    score = calculate_linear_ratio_score(stats, 1.0, 5.0)
    assert score > 1.0

    with pytest.raises(AppException):
        calculate_linear_ratio_score(stats, 5.0, 1.0)

    # 0 max weights
    stats_empty = {
        1.0: LevelStatsDTO(hits=0, total=0),
    }
    assert calculate_linear_ratio_score(stats_empty, 1.0, 5.0) == 1.0


def test_soft_waterfall_threshold_zero() -> None:
    stats = {1.0: LevelStatsDTO(hits=0, total=100)}
    # threshold = 0.0 -> fallback branch
    score = calculate_soft_waterfall_score(stats, 1.0, 5.0, 0.0, 0.5)
    assert score == 1.0
