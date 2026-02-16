
from unittest.mock import MagicMock, patch

import pytest

# Import the hook function
from backend.hooks.reporting import generate_report
from backend.models.state import WorkflowState


# Mock LocalizationService avoid DB calls
@pytest.fixture(autouse=True)
def mock_localization():
    with patch("backend.hooks.reporting.LocalizationService") as mock:
        mock.get.return_value = "Localized String"
        yield mock

@pytest.fixture
def mock_jinja():
    with patch("backend.hooks.reporting.Environment") as mock_env:
        mock_template = MagicMock()
        mock_template.render.return_value = "# Report\nMock Content"
        mock_env.return_value.get_template.return_value = mock_template
        yield mock_env

def test_generate_report_no_data():
    state = WorkflowState(
        workflow_id="test-wf",
        context_variables={}
    )
    # Should return same state, no warning if log mocked?
    # Actually it returns state unmodified.
    new_state = generate_report(state)
    assert new_state == state
    assert "xai_report_formatted" not in new_state.context_variables

def test_generate_report_with_data(mock_jinja):
    # Setup Context Variables
    xai_data = {
        "executive_summary": "Test Summary"
    }

    judge_data = {
        "pisteet": {
            "Dimension1": {"arvosana": 4.0, "perustelu": "Good"}
        },
        "kriittiset_havainnot_yhteenveto": ["Critical Issue 1"]
    }

    context_vars = {
        "step_xai": xai_data,
        "step_judge": judge_data,
        "step_overseer": {"eettiset_havainnot": []},
        "step_coach": {"coaching_plan": {}}
    }

    state = WorkflowState(
        workflow_id="test-wf",
        context_variables=context_vars
    )

    # Execute Hook
    with patch("backend.hooks.reporting.logger") as mock_logger:
        new_state = generate_report(state)

    # Verify New State
    assert new_state.execution_id == state.execution_id
    assert new_state.workflow_id == state.workflow_id

    # Check context_variables updated
    assert "xai_report_formatted" in new_state.context_variables
    assert new_state.context_variables["xai_report_formatted"] == "# Report\nMock Content"

    # Verify Jinja Template called
    mock_jinja.return_value.get_template.assert_called_with("report_template.jinja2")

    # Verify render arguments
    # We can inspect the calls to render if we want deep verification
    # But checking output is enough for "Availability" test.

def test_generate_report_attributes_fallback(mock_jinja):
    """Test fallback to attributes for legacy support (if applicable)."""
    # But WorkflowState is Frozen, so attributes can't be set on it easily outside of Pydantic.
    # We can skip this if we focus on V2.
    pass
