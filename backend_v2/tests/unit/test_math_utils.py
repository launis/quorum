import pytest
from backend_v2.utils.math_utils import (
    convert_strictness_to_forgiveness,
    calculate_soft_waterfall_score,
    calculate_progressive_dampening_score,
    get_strictness_config,
)
from backend_v2.models.enums import WaterfallThreshold


def test_convert_strictness_to_forgiveness():
    """Test the strictness conversion mapping."""
    assert convert_strictness_to_forgiveness(0) == 1.0
    assert convert_strictness_to_forgiveness(15) == 0.60
    assert convert_strictness_to_forgiveness(50) == 0.30
    assert convert_strictness_to_forgiveness(85) == 0.10
    assert convert_strictness_to_forgiveness(100) == 0.00
    
    # Check interpolation bounds
    assert convert_strictness_to_forgiveness(7) > 0.60
    assert convert_strictness_to_forgiveness(7) < 1.0
    assert convert_strictness_to_forgiveness(105) == 0.00
    assert convert_strictness_to_forgiveness(-5) == 1.0


def test_soft_waterfall_scaling_deterministic_differences():
    """Mathematically prove that strictness_level=15 yields a higher score than 85 for identical 0-hit rate stats."""
    # Scale 1-5, failing on level 2.
    level_stats = {
        1.0: {"hits": 1, "total": 1},  # hit_rate 1.0
        2.0: {"hits": 0, "total": 1},  # hit_rate 0.0
        3.0: {"hits": 0, "total": 1},
        4.0: {"hits": 0, "total": 1},
        5.0: {"hits": 0, "total": 1},
    }
    
    forgiveness_15 = convert_strictness_to_forgiveness(15)  # 0.60
    forgiveness_85 = convert_strictness_to_forgiveness(85)  # 0.10
    
    score_15 = calculate_soft_waterfall_score(
        level_stats, 
        scale_min=1.0, 
        scale_max=5.0, 
        threshold=0.75, 
        base_forgiveness=forgiveness_15
    )
    
    score_85 = calculate_soft_waterfall_score(
        level_stats, 
        scale_min=1.0, 
        scale_max=5.0, 
        threshold=0.75, 
        base_forgiveness=forgiveness_85
    )
    
    # Both fail at level 2. Since score 15 has higher forgiveness, it retains more points from higher levels.
    # Level 1 gives 1.0 points (total so far 2.0). Level 2 gives 0 points. Multiplier drops.
    # Actually wait: hit_rate is 0, so it gives 0 points.
    assert score_15 > score_85, f"Expected {score_15} > {score_85}"


def test_progressive_dampening_deterministic_differences():
    """Mathematically prove that strictness_level=15 yields a higher score than 85 for identical 0-hit rate stats."""
    level_stats = {
        1.0: {"hits": 0, "total": 1},
        2.0: {"hits": 0, "total": 1},
        3.0: {"hits": 0, "total": 1},
    }
    
    forgiveness_15 = convert_strictness_to_forgiveness(15)
    forgiveness_85 = convert_strictness_to_forgiveness(85)
    
    score_15 = calculate_progressive_dampening_score(
        level_stats, scale_min=1.0, scale_max=3.0, strictness_config=get_strictness_config(15)
    )
    
    score_85 = calculate_progressive_dampening_score(
        level_stats, scale_min=1.0, scale_max=3.0, strictness_config=get_strictness_config(85)
    )
    
    assert score_15 > score_85, f"Expected {score_15} > {score_85}"
