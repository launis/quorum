import pytest

from backend.exceptions import AppException, ErrorCodes
from backend.utils.math_utils import normalize_score_to_100


def test_normalize_score_standard_1_to_5():
    # 3.0 out of 1-5 scale -> 50%
    assert normalize_score_to_100(3.0, 1.0, 5.0) == 50.0

def test_normalize_score_standard_10_to_50():
    # 20 out of 10-50 scale -> 25% (because range is 40. 10 above min. 10/40 = 25%)
    assert normalize_score_to_100(20.0, 10.0, 50.0) == 25.0

def test_normalize_score_already_0_to_100():
    # 75 out of 0-100 scale -> 75%
    assert normalize_score_to_100(75.0, 0.0, 100.0) == 75.0

def test_normalize_score_out_of_bounds_clamping():
    # Strict validation happens upstream, but if a score slips through (e.g passivity penalty) to 0.5 below min 1:
    assert normalize_score_to_100(0.5, 1.0, 5.0) == 0.0
    # Or above max 5:
    assert normalize_score_to_100(6.0, 1.0, 5.0) == 100.0

def test_normalize_score_invalid_scale():
    # min >= max should raise AppException (Fail Fast)
    with pytest.raises(AppException) as exc:
        normalize_score_to_100(3.0, 5.0, 1.0)

    assert exc.value.status_code == 500
    assert exc.value.details["error_code"] == ErrorCodes.INVALID_OUTPUT_SCHEMA.value

    # min == max should also raise
    with pytest.raises(AppException) as exc2:
        normalize_score_to_100(3.0, 5.0, 5.0)

    assert exc2.value.details["error_code"] == ErrorCodes.INVALID_OUTPUT_SCHEMA.value
