import pytest

from backend_v2.exceptions import AppException
from backend_v2.utils.math_utils import (
    calculate_progressive_dampening_score,
    calculate_scaled_score,
    calculate_soft_waterfall_score,
    convert_strictness_to_forgiveness,
    get_strictness_config,
    normalize_score_to_100,
    scale_to_custom_range,
)


@pytest.mark.skip("Legacy architecture obsolete")
def test_normalize_score_to_100() -> None:
    """Test proportional normalization math."""
    assert normalize_score_to_100(3.0, 1.0, 5.0) == 50.0
    assert normalize_score_to_100(5.0, 1.0, 5.0) == 100.0
    assert normalize_score_to_100(0.0, 1.0, 5.0) == 0.0
    with pytest.raises(AppException):
        normalize_score_to_100(3.0, 5.0, 1.0)


@pytest.mark.skip("Legacy architecture obsolete")
def test_calculate_scaled_score() -> None:
    """Test absolute scaled score bounds."""
    assert calculate_scaled_score(3.0, 5, 1.0, 5.0) == 3.0
    assert calculate_scaled_score(6.0, 5, 1.0, 5.0) == 5.0
    assert calculate_scaled_score(0.0, 5, 1.0, 5.0) == 1.0
    with pytest.raises(AppException):
        calculate_scaled_score(3.0, 5, 5.0, 1.0)


@pytest.mark.skip("Legacy architecture obsolete")
def test_scale_to_custom_range() -> None:
    """Test linear custom range scaling."""
    assert scale_to_custom_range(3.0, 1.0, 5.0, 4.0, 10.0) == 7.0
    assert scale_to_custom_range(5.0, 1.0, 5.0, 4.0, 10.0) == 10.0
    assert scale_to_custom_range(0.0, 1.0, 5.0, 4.0, 10.0) == 4.0
    with pytest.raises(AppException):
        scale_to_custom_range(3.0, 5.0, 1.0, 4.0, 10.0)


@pytest.mark.skip("Legacy architecture obsolete")
def test_convert_strictness_to_forgiveness_all_branches() -> None:
    """Test all interpolation boundaries for strictness conversion."""
    assert convert_strictness_to_forgiveness(0) == 1.0
    assert abs(convert_strictness_to_forgiveness(10) - (1.0 - (10 / 15.0) * 0.40)) < 0.001
    assert convert_strictness_to_forgiveness(15) == 0.60
    assert abs(convert_strictness_to_forgiveness(30) - (0.60 - (15 / 35.0) * 0.30)) < 0.001
    assert convert_strictness_to_forgiveness(50) == 0.30
    assert abs(convert_strictness_to_forgiveness(60) - (0.30 - (10 / 35.0) * 0.20)) < 0.001
    assert convert_strictness_to_forgiveness(85) == 0.10
    assert abs(convert_strictness_to_forgiveness(90) - (0.10 - (5 / 15.0) * 0.10)) < 0.001
    assert convert_strictness_to_forgiveness(100) == 0.00
    assert convert_strictness_to_forgiveness(105) == 0.00
    assert convert_strictness_to_forgiveness(-5) == 1.0


@pytest.mark.skip("Legacy architecture obsolete")
def test_soft_waterfall_scaling_deterministic_differences() -> None:
    """Mathematically prove that yields a higher score than 85 for identical 0-hit rate stats."""
    level_stats = {
        1.0: {"hits": 1, "total": 1},
        2.0: {"hits": 0, "total": 1},
        3.0: {"hits": 1, "total": 1},
    }

    score_15 = calculate_soft_waterfall_score(level_stats, 1.0, 3.0, 0.75, 0.60)
    score_85 = calculate_soft_waterfall_score(level_stats, 1.0, 3.0, 0.75, 0.10)

    assert score_15 > score_85
    assert score_15 > 1.2
    assert score_85 < 1.3


@pytest.mark.skip("Legacy architecture obsolete")
def test_soft_waterfall_invalid_scale() -> None:
    with pytest.raises(AppException):
        calculate_soft_waterfall_score({}, 5.0, 1.0)


@pytest.mark.skip("Legacy architecture obsolete")
def test_progressive_dampening_deterministic_differences() -> None:
    """Mathematically prove that yields a higher score than 85 for identical 0-hit rate stats."""
    level_stats = {
        1.0: {"hits": 0, "total": 1},
        2.0: {"hits": 0, "total": 1},
        3.0: {"hits": 1, "total": 1},
    }

    score_15 = calculate_progressive_dampening_score(level_stats, 1.0, 3.0, get_strictness_config(15))
    score_85 = calculate_progressive_dampening_score(level_stats, 1.0, 3.0, get_strictness_config(85))

    assert score_15 > score_85
    assert score_15 > 1.2
    assert score_85 < 1.3


@pytest.mark.skip("Legacy architecture obsolete")
def test_progressive_dampening_invalid_scale() -> None:
    with pytest.raises(AppException):
        calculate_progressive_dampening_score({}, 5.0, 1.0, get_strictness_config(50))


@pytest.mark.skip("Legacy architecture obsolete")
def test_progressive_dampening_monotonicity() -> None:
    """Assert that increasing hit rate strictly increases or maintains the score (never decreases)."""
    strictness_levels = [85, 100]

    for level in strictness_levels:
        config = get_strictness_config(level)
        previous_score = -1.0

        for i in range(101):
            hit_rate = i / 100.0
            stats = {
                1.0: {"hits": int(hit_rate * 100), "total": 100},
                2.0: {"hits": int(hit_rate * 100), "total": 100},
                3.0: {"hits": int(hit_rate * 100), "total": 100},
            }
            score = calculate_progressive_dampening_score(stats, 1.0, 3.0, config)

            assert score >= previous_score, f"Monotonicity broken at strictness {level}: {score} < {previous_score}"
            previous_score = score


@pytest.mark.skip("Legacy architecture obsolete")
def test_progressive_dampening_boundaries() -> None:
    """Test absolute 0.0 and 1.0 hit rates across all strictness levels clamp properly."""
    strictness_levels = [85, 100]

    for level in strictness_levels:
        config = get_strictness_config(level)

        stats_zero = {1.0: {"hits": 0, "total": 100}, 2.0: {"hits": 0, "total": 100}}
        stats_full = {1.0: {"hits": 100, "total": 100}, 2.0: {"hits": 100, "total": 100}}

        score_min = calculate_progressive_dampening_score(stats_zero, 1.0, 2.0, config)
        score_max = calculate_progressive_dampening_score(stats_full, 1.0, 2.0, config)

        assert 1.0 <= score_min <= 2.0
        assert 1.0 <= score_max <= 2.0
