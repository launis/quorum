import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
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
