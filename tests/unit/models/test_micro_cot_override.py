import pytest
from pydantic import ValidationError
from backend_v2.models.v2_core import BaseTDAExtraction

def test_contextual_override_cross_validation():
    data_valid = {
        "step_1_evidence_scan": "scan",
        "step_2_mitigating_context": "context",
        "contextual_override": True,
        "exact_quote": None,
        "extracted_data": "some data"
    }
    model = BaseTDAExtraction.model_validate(data_valid)
    assert model.contextual_override is True
    assert model.exact_quote is None

    data_invalid = {
        "step_1_evidence_scan": "scan",
        "step_2_mitigating_context": "context",
        "contextual_override": True,
        "exact_quote": "Löytyi lainaus",
        "extracted_data": "some data"
    }
    with pytest.raises(ValidationError) as exc_info:
        BaseTDAExtraction.model_validate(data_invalid)
    
    assert "exact_quote MUST be null if contextual_override is True" in str(exc_info.value)
