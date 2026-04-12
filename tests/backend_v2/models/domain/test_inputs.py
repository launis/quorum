import pytest
from pydantic import ValidationError

from backend_v2.exceptions import ConfigurationError, ErrorCodes
from backend_v2.models.domain.inputs import WorkflowInputs

def test_workflow_inputs_accepts_valid_data() -> None:
    """Test that valid inputs are accepted."""
    data = {"history_text": "Good text", "count": 5}
    inputs = WorkflowInputs.model_validate(data)
    assert getattr(inputs, "history_text") == "Good text"
    assert getattr(inputs, "count") == 5

def test_workflow_inputs_rejects_content_base64_direct() -> None:
    """Test that a direct base64 dict is rejected by the strict mandate."""
    data = {
        "chat_log": {
            "filename": "test.pdf",
            "content_base64": "SGVsbG8gV29ybGQ=",
        }
    }
    with pytest.raises(ConfigurationError) as exc_info:
        WorkflowInputs.model_validate(data)
    
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED
    assert "Binary 'content_base64' payload detected" in exc_info.value.message

def test_workflow_inputs_rejects_content_base64_deep() -> None:
    """Test that base64 is rejected even if sent under a random dynamic key."""
    data = {
        "random_file_input": {
            "filename": "test.pdf",
            "content_base64": "abc",
        }
    }
    with pytest.raises(ConfigurationError) as exc_info:
        WorkflowInputs.model_validate(data)
    
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED

