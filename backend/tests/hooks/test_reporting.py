
import pytest
from unittest.mock import patch
from backend.hooks.reporting import generate_report
from backend.models.state import WorkflowState
from backend.exceptions import AppException

def test_generate_report_success():
    state = WorkflowState(workflow_id="wf-1")
    state.context_variables["inputs"] = {"history_text": "History"}
    state.context_variables["step_xai"] = {
        "executive_summary": "Summary",
        "analysis_strengths": "Strengths",
        "analysis_weaknesses": "Weaknesses",
        "analysis_opportunities": "Opportunities",
        "analysis_recommendations": "Recommendations",
        "final_verdict": "Verdict",
        "confidence_score": 0.9,
        "thought_process": "Thinking",
        "conclusion": "Done"
    }
    
    # Mock File existence
    with patch("pathlib.Path.exists", return_value=True):
        new_state = generate_report(state)
        
        result = new_state.context_variables.get("report_context")
        assert result is not None
        assert isinstance(result, dict)
        assert result.get("summary") == "Summary"

def test_generate_report_fail_fast_missing_template_dir():
    state = WorkflowState(workflow_id="wf-1")
    
    # Mock File non-existence
    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(AppException) as exc:
            generate_report(state)
        
        assert "CONFIGURATION_ERROR" in str(exc.value.details)
