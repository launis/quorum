
import pytest
from unittest.mock import MagicMock, patch
from backend.hooks.reporting import generate_report
from backend.models.state import WorkflowState
from backend.models.domain import ReportResult, ReportContext
from backend.exceptions import AppException

def test_generate_report_success():
    state = WorkflowState(workflow_id="wf-1")
    # Mock XAI step data
    state.context_variables["step_xai"] = {
        "executive_summary": "Summary",
        "final_verdict": "Verdict",
        "confidence_score": 0.9,
    }
    state.context_variables["inputs"] = {"history_text": "History"}
    
    # Mock Template Rendering to avoid file system dependencies in unit test
    with patch("backend.hooks.reporting.Environment") as MockEnv:
        mock_template = MagicMock()
        mock_template.render.return_value = "# Report"
        MockEnv.return_value.get_template.return_value = mock_template
        
        # Mock File existence
        with patch("os.path.exists", return_value=True):
            new_state = generate_report(state)
            
            result = new_state.context_variables.get("report_result")
            assert isinstance(result, ReportResult)
            assert result.report_content == "# Report"
            assert isinstance(result.data, ReportContext)
            assert result.data.summary == "Summary"

def test_generate_report_fail_fast_missing_template_dir():
    state = WorkflowState(workflow_id="wf-1")
    
    # Mock File non-existence
    with patch("os.path.exists", return_value=False):
        with pytest.raises(AppException) as exc:
            generate_report(state)
        
        # Just check for message or error code, the structure detail might be in details
        assert "REPORT_TEMPLATE_DIR_MISSING" in str(exc.value.details)

def test_generate_report_context_validation_failure():
    state = WorkflowState(workflow_id="wf-1")
    # Provide partial data to pass "if not xai_data" check, but fail ReportContext validation (missing summary)
    state.context_variables["step_xai"] = {"some_field": "some_value"} 
    
    with patch("os.path.exists", return_value=True):
        with patch("backend.hooks.reporting.Environment"):
             with pytest.raises(AppException) as exc:
                 generate_report(state)
                 
             assert "REPORT_CONTEXT_VALIDATION_FAILED" in str(exc.value.details)
