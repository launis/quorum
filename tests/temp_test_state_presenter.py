import pytest
import datetime
from unittest.mock import MagicMock, patch

from backend.services.state_presenter import StatePresenter
from backend.models.dtos.state_presentation import StatePresentation, SystemStatus
from backend.models.state import WorkflowState
from backend.exceptions import AppException, ErrorCodes

# Mock Settings
@pytest.fixture
def mock_settings():
    # Patch the source since it is imported inside the function
    with patch("backend.settings.get_settings") as mock:
        mock.return_value.active_backend.value = "MOCK"
        mock.return_value.environment = "LOCAL"
        yield mock

class TestStatePresenter:
    
    def test_flatten_state_success(self, mock_settings):
        """Test happy path flattening to strict DTO."""
        # Setup valid state
        state = MagicMock(spec=WorkflowState)
        state.execution_id = "exec-123"
        state.workflow_id = "wf-456"
        state.workflow_name = "Test Workflow"
        state.start_time = datetime.datetime(2023, 10, 27, 10, 0, 0)
        state.reasoning_context = {} # Truthy
        state.organization_id = "org-1"
        state.user_id = "user-1"
        
        # Mock sub-steps (simplified)
        state.step_guard = MagicMock()
        state.step_guard.security_check.uhka_havaittu = False
        state.step_guard.security_check.riski_taso = "LOW"
        # IMPORTANT: Pydantic model_dump returns dicts, so mock that
        state.step_guard.security_check.model_dump.return_value = {"uhka_havaittu": False, "riski_taso": "LOW"}
        
        state.step_falsifier = None # Optional
        state.step_profiler = None
        state.step_interaction = None
        state.step_xai = None
        state.audit_results = {}
        state.step_judge = None
        state.step_judge_cognitive = None
        state.step_analyst = None
        state.step_logician = None
        state.step_causal = None
        state.step_detector = None
        state.step_overseer = None
        state.step_archivist = None
        state.step_coach = None
        state.step_panel = None

        # Execute
        result = StatePresenter.flatten_state(state)

        # Verify
        assert isinstance(result, StatePresentation)
        assert isinstance(result.System_Status, SystemStatus)
        assert result.System_Status.execution_id == "exec-123"
        assert result.System_Status.database_source == "MOCK"
        assert result.System_Status.environment == "LOCAL"
        # Check strict typing of boolean
        assert result.System_Status.uhka_havaittu is False
        print("\n[TEST] Flatten State: Success (Strict DTO returned)")

    def test_flatten_state_fail_fast_integrity(self, mock_settings):
        """Test fail fast when critical ID is missing."""
        # Setup invalid state
        state = MagicMock(spec=WorkflowState)
        state.execution_id = None # MISSING
        state.workflow_id = "wf-456"

        # Execute & Verify
        try:
            StatePresenter.flatten_state(state)
            assert False, "Should have raised AppException"
        except AppException as e:
            assert e.details["error_code"] == ErrorCodes.STATE_INTEGRITY_ERROR
            assert e.status_code == 500
            print("\n[TEST] State Integrity Failure: Caught (Fail Fast)")

if __name__ == "__main__":
    # Minimal runner
    t = TestStatePresenter()
    
    # Mock settings patching for manual run
    with patch("backend.settings.get_settings") as mock:
        mock.return_value.active_backend.value = "MOCK"
        mock.return_value.environment = "LOCAL"
        
        # Instantiate test class
        t = TestStatePresenter()
        
        print("\n--- Running Manual Tests ---")
        t.test_flatten_state_success(mock)
        t.test_flatten_state_fail_fast_integrity(mock)
        print("\n--- All Manual Tests Passed ---")
