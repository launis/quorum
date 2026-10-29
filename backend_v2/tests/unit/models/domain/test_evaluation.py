"""Unit tests for evaluation and validation domain models."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.domain.evaluation import (
    EvaluationCriterion,
    EvaluationMatrixConfig,
    EvaluationResult,
    ValidationResult,
)
from backend_v2.models.domain.judge import DimensionResultItem


def test_evaluation_criterion_weight_bounds() -> None:
    """Test that EvaluationCriterion.weight enforces >= 0.0 and rejects empty IDs."""
    # Positive: valid weight and zero boundary
    crit = EvaluationCriterion(id="crit_1", label="Criterion 1", weight=1.5)
    assert crit.weight == 1.5
    zero_crit = EvaluationCriterion(id="crit_0", label="Criterion 0", weight=0.0)
    assert zero_crit.weight == 0.0

    # Negative 1: boundary min - epsilon (< 0.0) raises AppException
    with pytest.raises(AppException) as exc:
        EvaluationCriterion(id="crit_1", label="Criterion 1", weight=-0.01)
    assert "weight must be >= 0.0" in str(exc.value)

    # Negative 2: empty id violates min_length=1
    with pytest.raises(ValidationError):
        EvaluationCriterion(id="", label="Criterion 1", weight=1.0)


def test_evaluation_matrix_config_validation() -> None:
    """Test EvaluationMatrixConfig positive and negative boundary cases."""
    crit = EvaluationCriterion(id="crit_1", label="Criterion 1")
    config = EvaluationMatrixConfig(id="mat_1", name="Matrix 1", criteria=[crit])
    assert config.id == "mat_1"
    assert len(config.criteria) == 1

    # Negative 1: empty criteria list violates min_length=1
    with pytest.raises(ValidationError):
        EvaluationMatrixConfig(id="mat_1", name="Matrix 1", criteria=[])

    # Negative 2: empty name violates min_length=1
    with pytest.raises(ValidationError):
        EvaluationMatrixConfig(id="mat_1", name="", criteria=[crit])


def test_evaluation_result_scale_validation() -> None:
    """Test that scale_min must be strictly less than scale_max (equality and inversion rejected)."""
    # Negative 1: scale_min > scale_max
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
            scale_max=0.0,
        )
    assert "scale_min must be strictly less than scale_max" in str(exc.value)

    # Negative 2: boundary scale_min == scale_max
    with pytest.raises(AppException) as exc_eq:
        EvaluationResult(
            thought_process="Valid",
            conclusion="Valid",
            confidence_score=0.9,
            matrix_id="mat_1",
            timestamp=datetime.fromisoformat("2026-05-04T12:00:00+00:00"),
            total_score=50.0,
            final_verdict="Valid",
            dimensions=[DimensionResultItem(dimension_id="dim_1", score=5.0, reasoning="OK")],
            scale_min=50.0,
            scale_max=50.0,
        )
    assert "scale_min must be strictly less than scale_max" in str(exc_eq.value)


def test_evaluation_result_out_of_bounds_allowed_and_iso_timestamp() -> None:
    """Test that total_score can fall outside scale_min/scale_max and ISO string timestamps parse cleanly."""
    result = EvaluationResult.model_validate(
        {
            "thought_process": "Valid",
            "conclusion": "Valid",
            "confidence_score": 0.9,
            "matrix_id": "mat_1",
            "timestamp": "2026-05-04T12:00:00Z",
            "total_score": 150.0,
            "final_verdict": "Valid",
            "dimensions": [DimensionResultItem(dimension_id="dim_1", score=5.0, reasoning="OK")],
            "scale_min": 0.0,
            "scale_max": 100.0,
        }
    )
    assert result.total_score == 150.0
    assert result.timestamp == datetime(2026, 5, 4, 12, 0, 0, tzinfo=UTC)


def test_validation_result_logic() -> None:
    """Test that ValidationResult requires errors if is_valid is False and rejects invalid types."""
    # Positive
    valid_res = ValidationResult(is_valid=True)
    assert valid_res.is_valid is True
    invalid_res = ValidationResult(is_valid=False, errors=["Error 1"])
    assert invalid_res.errors == ["Error 1"]

    # Negative 1: is_valid=False with empty errors raises AppException
    with pytest.raises(AppException) as exc:
        ValidationResult(is_valid=False)
    assert "Invalid result must have errors" in str(exc.value)

    # Negative 2: strict mode rejects non-bool is_valid
    with pytest.raises(ValidationError):
        ValidationResult.model_validate({"is_valid": "false", "errors": ["Error 1"]})
