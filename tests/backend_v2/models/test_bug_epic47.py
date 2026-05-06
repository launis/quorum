import pytest
from pydantic import ValidationError
from backend_v2.models.dtos.report import TraceMatrixPayloadDTO

def test_trace_matrix_payload_dto_accepts_xai_log():
    payload = {
        "raw_score": 3.5,
        "normalized_score": 75.0,
        "justification": "Test justification",
        "xai_log": {"pedagogical_key": "some_value"}
    }
    
    # This should pass without raising ValidationError: Extra inputs are not permitted
    dto = TraceMatrixPayloadDTO.model_validate(payload, strict=False)
    assert dto.raw_score == 3.5
