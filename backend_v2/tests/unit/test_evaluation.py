from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.evaluation import (
    EvaluationCriterion,
    EvaluationMatrixConfig,
    EvaluationResult,
    ValidationResult,
)
from backend_v2.models.domain.judge import DimensionResultItem


def test_evaluation_criterion_success() -> None:
    """Test valid EvaluationCriterion."""
    crit = EvaluationCriterion(id="c1", label="Label 1", weight=2.0)
    assert crit.id == "c1"
    assert crit.weight == 2.0


def test_evaluation_criterion_validation() -> None:
    """Test min_length and ge validation on EvaluationCriterion."""
    with pytest.raises(ValidationError):
        EvaluationCriterion(id="", label="Label 1")
    with pytest.raises(ValidationError):
        EvaluationCriterion(id="c1", label="", weight=1.0)
    with pytest.raises(ValidationError):
        EvaluationCriterion(id="c1", label="L", weight=-1.0)


def test_evaluation_matrix_config_success() -> None:
    """Test valid EvaluationMatrixConfig."""
    crit = EvaluationCriterion(id="c1", label="Label 1", weight=1.0)
    config = EvaluationMatrixConfig(id="m1", name="Matrix 1", criteria=[crit])
    assert config.id == "m1"
    assert len(config.criteria) == 1


def test_evaluation_matrix_config_validation() -> None:
    """Test min_length validation on EvaluationMatrixConfig."""
    crit = EvaluationCriterion(id="c1", label="Label 1", weight=1.0)
    with pytest.raises(ValidationError):
        EvaluationMatrixConfig(id="", name="Matrix 1", criteria=[crit])
    with pytest.raises(ValidationError):
        EvaluationMatrixConfig(id="m1", name="", criteria=[crit])
    with pytest.raises(ValidationError):
        EvaluationMatrixConfig(id="m1", name="Matrix 1", criteria=[])


def test_evaluation_result_success() -> None:
    """Test valid EvaluationResult."""
    dim = DimensionResultItem(dimension_id="d1", dimension_label="L1", score=5.0, reasoning="R")
    res = EvaluationResult(
        matrix_id="m1",
        timestamp=datetime.now(tz=timezone.utc),
        total_score=5.0,
        final_verdict="Verdict",
        dimensions=[dim],
        scale_min=1.0,
        scale_max=10.0,
        thought_process="T",
        conclusion="C",
        confidence_score=0.9,
    )
    assert res.total_score == 5.0
    assert len(res.dimensions) == 1


def test_evaluation_result_validation() -> None:
    """Test min_length and cross-field logic validation on EvaluationResult."""
    dim = DimensionResultItem(dimension_id="d1", dimension_label="L1", score=5.0, reasoning="R")
    timestamp = datetime.now(tz=timezone.utc)

    # Empty string validation
    with pytest.raises(ValidationError):
        EvaluationResult(
            matrix_id="",
            timestamp=timestamp,
            total_score=5.0,
            final_verdict="Verdict",
            dimensions=[dim],
            scale_min=1.0,
            scale_max=10.0,
            thought_process="T",
            conclusion="C",
            confidence_score=0.9,
        )
    with pytest.raises(ValidationError):
        EvaluationResult(
            matrix_id="m1",
            timestamp=timestamp,
            total_score=5.0,
            final_verdict="",
            dimensions=[dim],
            scale_min=1.0,
            scale_max=10.0,
            thought_process="T",
            conclusion="C",
            confidence_score=0.9,
        )

    # Empty dimensions validation
    with pytest.raises(ValidationError):
        EvaluationResult(
            matrix_id="m1",
            timestamp=timestamp,
            total_score=5.0,
            final_verdict="V",
            dimensions=[],
            scale_min=1.0,
            scale_max=10.0,
            thought_process="T",
            conclusion="C",
            confidence_score=0.9,
        )

    # Scale range logic validation (raises AppException)
    with pytest.raises(ValidationError):
        EvaluationResult(
            matrix_id="m1",
            timestamp=timestamp,
            total_score=5.0,
            final_verdict="Verdict",
            dimensions=[dim],
            scale_min=10.0,
            scale_max=1.0,
            thought_process="T",
            conclusion="C",
            confidence_score=0.9,
        )

    with pytest.raises(ValidationError):
        EvaluationResult(
            matrix_id="m1",
            timestamp=timestamp,
            total_score=15.0,
            final_verdict="Verdict",
            dimensions=[dim],
            scale_min=1.0,
            scale_max=10.0,
            thought_process="T",
            conclusion="C",
            confidence_score=0.9,
        )


def test_validation_result_success() -> None:
    """Test valid ValidationResult."""
    res1 = ValidationResult(is_valid=True)
    assert res1.is_valid is True

    res2 = ValidationResult(is_valid=False, errors=["Error 1"])
    assert res2.is_valid is False
    assert len(res2.errors) == 1


def test_validation_result_logic_error() -> None:
    """Test cross-field logic validation on ValidationResult."""
    with pytest.raises(ValidationError):
        ValidationResult(is_valid=False, errors=[])
