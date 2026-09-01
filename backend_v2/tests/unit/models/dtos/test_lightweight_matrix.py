import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO, LightweightMatrixOutput
from backend_v2.models.enums import ExecutionStatus


def test_lightweight_matrix_output_coerces_failed_string() -> None:
    """Test that LightweightMatrixOutput correctly coerces 'FAILED' string to ExecutionStatus.FAILED."""
    payload = {"evaluated_atoms": {"a0": "FAILED", "a1": "PASSED"}}
    dto = LightweightMatrixOutput.model_validate(payload)
    assert dto.evaluated_atoms["a0"] == ExecutionStatus.FAILED
    assert dto.evaluated_atoms["a1"] == ExecutionStatus.PASSED


def test_lightweight_matrix_output_rejects_raw_bool() -> None:
    """Test that LightweightMatrixOutput explicitly rejects raw bool values (True/False)."""
    payload = {"evaluated_atoms": {"a0": False}}
    with pytest.raises(ValidationError) as exc:
        LightweightMatrixOutput.model_validate(payload)
    assert "Input should be" in str(exc.value)

    payload_true = {"evaluated_atoms": {"a0": True}}
    with pytest.raises(ValidationError) as exc_true:
        LightweightMatrixOutput.model_validate(payload_true)
    assert "Input should be" in str(exc_true.value)


def test_level_stats_dto_defaults_and_fields() -> None:
    """Test LevelStatsDTO defaults dlqs to 0 and accepts explicit values."""
    dto_default = LevelStatsDTO(hits=3, total=5)
    assert dto_default.hits == 3
    assert dto_default.total == 5
    assert dto_default.dlqs == 0

    dto_explicit = LevelStatsDTO(hits=2.5, total=10.0, dlqs=2)
    assert dto_explicit.hits == 2.5
    assert dto_explicit.total == 10.0
    assert dto_explicit.dlqs == 2


def test_lightweight_matrix_output_normalized_score_validation() -> None:
    """Test LightweightMatrixOutput normalized_score bounds validation."""
    valid_dto = LightweightMatrixOutput(normalized_score=85.5)
    assert valid_dto.normalized_score == 85.5

    with pytest.raises(ValidationError):
        LightweightMatrixOutput(normalized_score=150.0)

    with pytest.raises(ValidationError):
        LightweightMatrixOutput(normalized_score=-5.0)
