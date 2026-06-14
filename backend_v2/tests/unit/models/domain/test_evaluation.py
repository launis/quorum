from datetime import datetime

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.domain.evaluation import (
    EvaluationCriterion,
    EvaluationResult,
    ValidationResult,
)
from backend_v2.models.domain.judge import DimensionResultItem


def test_evaluation_criterion_native_bounds() -> None:
    """Test that EvaluationCriterion.weight uses native ge=0.0."""
    # Valid
    crit = EvaluationCriterion(id="crit_1", label="Criterion 1", weight=1.5)
    assert crit.weight == 1.5

    # Invalid
    with pytest.raises(ValidationError) as exc:
        EvaluationCriterion(id="crit_1", label="Criterion 1", weight=-0.5)
    assert "Input should be greater than or equal to 0" in str(exc.value)


def test_evaluation_result_scale_validation() -> None:
    """Test that scale_min must be strictly less than scale_max."""
    with pytest.raises(AppException) as exc:
        EvaluationResult(
            thought_process="Valid",
            conclusion="Valid",
            confidence_score=0.9,
            matrix_id="mat_1",
            timestamp=datetime.fromisoformat("2026-05-04T12:00:00+00:00"),
            total_score=50.0,
            final_verdict="Valid",
            dimensions=[DimensionResultItem(dimension_id="dim_1", score=5.0, reasoning="OK")],
            scale_min=100.0,
            scale_max=0.0,  # Invalid, min > max
        )
    assert "scale_min must be strictly less than scale_max" in str(exc.value)


def test_evaluation_result_out_of_bounds_allowed() -> None:
    """Test that total_score can fall outside scale_min and scale_max (strict_math_display_isolation)."""
    # This should NOT raise an error because scale_min/max are just for UI mapping
    result = EvaluationResult(
        thought_process="Valid",
        conclusion="Valid",
        confidence_score=0.9,
        matrix_id="mat_1",
        timestamp=datetime.fromisoformat("2026-05-04T12:00:00+00:00"),
        total_score=150.0,  # Exceeds max
        final_verdict="Valid",
        dimensions=[DimensionResultItem(dimension_id="dim_1", score=5.0, reasoning="OK")],
        scale_min=0.0,
        scale_max=100.0,
    )
    assert result.total_score == 150.0


def test_validation_result_logic() -> None:
    """Test that ValidationResult requires errors if is_valid is False."""
    # Valid
    ValidationResult(is_valid=True)
    ValidationResult(is_valid=False, errors=["Error 1"])

    # Invalid
    with pytest.raises(AppException) as exc:
        ValidationResult(is_valid=False)
    assert "Invalid result must have errors" in str(exc.value)
