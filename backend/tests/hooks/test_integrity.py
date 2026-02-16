
import pytest
from backend.hooks.integrity import verify_citation_integrity, enforce_hypothesis_linking
from backend.models.state import WorkflowState
from backend.exceptions import AppException

# Mock Data Classes
class MockHypothesis:
    def __init__(self, id, quotes=None):
        self.id = id
        self.quotes = quotes or []

class MockAnalyst:
    def __init__(self, hypotheses):
        self.hypotheses = hypotheses

# TESTS

def test_enforce_hypothesis_linking_success():
    state = WorkflowState(workflow_id="wf-1")
    state.context_variables["step_analyst"] = MockAnalyst([
        MockHypothesis("HYP-1"),
        MockHypothesis("HYP-2"),
        MockHypothesis("HYP-3")
    ])
    
    new_state = enforce_hypothesis_linking(state)
    assert new_state == state # Should return same state if verified

def test_enforce_hypothesis_linking_bad_format():
    state = WorkflowState(workflow_id="wf-1")
    state.context_variables["step_analyst"] = MockAnalyst([
        MockHypothesis("HYP-1"),
        MockHypothesis("INVALID-2")
    ])
    
    with pytest.raises(AppException) as exc:
        enforce_hypothesis_linking(state)
    
    assert "INVALID_HYPOTHESIS_ID" in str(exc.value.details)

def test_enforce_hypothesis_linking_sequence_gap():
    state = WorkflowState(workflow_id="wf-1")
    state.context_variables["step_analyst"] = MockAnalyst([
        MockHypothesis("HYP-1"),
        MockHypothesis("HYP-3") # Skipped 2
    ])
    
    with pytest.raises(AppException) as exc:
        enforce_hypothesis_linking(state)
        
    assert "HYPOTHESIS_SEQUENCE_ERROR" in str(exc.value.details)

def test_verify_citation_integrity_success():
    state = WorkflowState(workflow_id="wf-1")
    state.context_variables["inputs"] = {
        "history_text": "The quick brown fox jumps over the lazy dog.",
        "product_text": ""
    }
    state.context_variables["step_analyst"] = MockAnalyst([
        MockHypothesis("HYP-1", quotes=["quick brown fox", "lazy dog"])
    ])
    
    new_state = verify_citation_integrity(state)
    audit = new_state.context_variables["integrity_audit"]
    assert audit.valid_citations == 2
    assert audit.integrity_score == 1.0

def test_verify_citation_integrity_fail_fast():
    state = WorkflowState(workflow_id="wf-1")
    state.context_variables["inputs"] = {
        "history_text": "The quick brown fox jumps over the lazy dog.",
        "product_text": ""
    }
    # 2 invalid vs 1 valid -> 0.33 score -> Fail
    state.context_variables["step_analyst"] = MockAnalyst([
        MockHypothesis("HYP-1", quotes=["quick brown fox", "unicorn", "leprechaun"])
    ])
    
    with pytest.raises(AppException) as exc:
        verify_citation_integrity(state)
        
    assert "CITATION_INTEGRITY_FAILURE" in str(exc.value.details)
    assert exc.value.status_code == 422
