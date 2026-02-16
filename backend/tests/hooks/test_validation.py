
import pytest
from backend.hooks.validation import verify_structure
from backend.models.state import WorkflowState
from backend.models.domain import ValidationResult
from backend.exceptions import AppException, ErrorCodes

@pytest.fixture
def mock_state():
    return WorkflowState(
        workflow_id="test_wf",
        context_variables={"inputs": {
            "history_text": "History " * 20, # > 100 chars
            "product_text": "Product " * 20,
            "reflection_text": "Reflection " * 20
        }}
    )

def test_verify_structure_success(mock_state):
    """Verify checks pass with valid input."""
    new_state = verify_structure(mock_state)
    result = new_state.context_variables.get("validation_result")
    
    assert isinstance(result, ValidationResult)
    assert result.is_valid is True
    assert len(result.errors) == 0

def test_verify_structure_short_input(mock_state):
    """Verify validation fails for short input."""
    mock_state = mock_state.model_copy(update={
        "context_variables": {
            "inputs": {
                "history_text": "Too short",
                "product_text": "Valid " * 20,
                "reflection_text": "Valid " * 20
            }
        }
    })
    
    with pytest.raises(AppException) as exc:
        verify_structure(mock_state)
    
    assert exc.value.error_code == ErrorCodes.VALIDATION_FAILED
    assert "too short" in str(exc.value.details["warnings"])
    
    # We can't check state update because exception raised, 
    # but in a real workflow the engine catches this.

def test_verify_structure_missing_context(mock_state):
    """Fail Fast: Missing context raises EMPTY_INPUT."""
    mock_state = mock_state.model_copy(update={"context_variables": {}})
    
    with pytest.raises(AppException) as exc:
        verify_structure(mock_state)
        
    assert exc.value.error_code == ErrorCodes.EMPTY_INPUT

def test_verify_structure_invalid_inputs_type(mock_state):
    """Should handle invalid inputs type gracefully (default to empty and fail validation)."""
    mock_state = mock_state.model_copy(update={
        "context_variables": {"inputs": "Invalid String"}
    })
    
    with pytest.raises(AppException) as exc:
        verify_structure(mock_state)
    
    assert exc.value.error_code == ErrorCodes.VALIDATION_FAILED
    # All fields missing/short
    assert len(exc.value.details["warnings"]) == 3
