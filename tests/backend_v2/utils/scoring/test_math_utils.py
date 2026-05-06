import pytest
from backend_v2.utils.math_utils import clamp_score, get_strictness_config

def test_clamp_score():
    assert clamp_score(-1.0, 1.0, 5.0) == 1.0
    assert clamp_score(6.0, 1.0, 5.0) == 5.0
    assert clamp_score(3.0, 1.0, 5.0) == 3.0
    assert clamp_score(1.0, 1.0, 5.0) == 1.0
    assert clamp_score(5.0, 1.0, 5.0) == 5.0

def test_get_strictness_config():
    config_50 = get_strictness_config(50)
    assert config_50.base_forgiveness > 0.0
    assert config_50.dynamic_exponent > 0.0
    
    config_100 = get_strictness_config(100)
    assert config_100.base_forgiveness < config_50.base_forgiveness
    assert config_100.dynamic_exponent > config_50.dynamic_exponent
