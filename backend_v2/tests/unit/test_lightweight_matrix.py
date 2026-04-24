import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.enums import XaiExtensionType


def test_lightweight_matrix_preserves_raw_score_and_source_id() -> None:
    data = {
        "raw_score": 4.5,
        "normalized_score": 0.875,
        "level_breakdown": "level 4",
        "justification": "Good enough",
        "evaluated_atoms": {"atom1": True},
        "extensions": {XaiExtensionType.SOURCE_ID: "doc_123"},
    }

    output = LightweightMatrixOutput.model_validate(data)

    assert output.raw_score == 4.5
    assert output.normalized_score == 0.875
    assert output.extensions[XaiExtensionType.SOURCE_ID] == "doc_123"


def test_lightweight_matrix_fail_fast_missing_raw_score() -> None:
    data = {
        "normalized_score": 0.875,
        "level_breakdown": "level 4",
        "justification": "Good enough",
        "evaluated_atoms": {"atom1": True},
        "extensions": {},
    }

    with pytest.raises(ValidationError) as exc_info:
        LightweightMatrixOutput.model_validate(data)

    assert "Field required" in str(exc_info.value)
    assert "raw_score" in str(exc_info.value)
