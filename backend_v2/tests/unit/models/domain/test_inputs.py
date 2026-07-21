import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.domain.inputs import Base64Attachment, WorkflowInputs, WorkflowInputsIngress


def test_base64_attachment_valid() -> None:
    """Test valid Base64Attachment creation."""
    attachment = Base64Attachment(
        filename="test.pdf",
        content_base64="JVBERi...",
        content_type="application/pdf",
    )
    assert attachment.filename == "test.pdf"
    assert attachment.content_base64 == "JVBERi..."
    assert attachment.content_type == "application/pdf"


def test_workflow_inputs_ingress_valid() -> None:
    """Test valid WorkflowInputsIngress creation."""
    inputs = WorkflowInputsIngress(
        organization_id="org_123",
        user_id="usr_456",
        simulation_mode=True,
        language="fi",
        dynamic_inputs={"foo": "bar"},
    )
    assert inputs.organization_id == "org_123"
    assert inputs.user_id == "usr_456"
    assert inputs.simulation_mode is True
    assert inputs.language == "fi"
    assert inputs.dynamic_inputs == {"foo": "bar"}


def test_workflow_inputs_prevent_base64_pollution() -> None:
    """Test that WorkflowInputs bans content_base64 in payload to protect DB."""
    # Should raise error if content_base64 is at root level payload
    with pytest.raises(AppException) as exc_info:
        WorkflowInputs(
            dynamic_inputs={"file": {"content_base64": "binary_blob_here"}},
        )
    assert "content_base64" in str(exc_info.value)

    # Should also raise error if content_base64 is passed directly in extra kwargs
    with pytest.raises(AppException) as exc_info:
        WorkflowInputs.model_validate({"malicious_attachment": {"content_base64": "binary_blob_here"}})
    assert "content_base64" in str(exc_info.value)


def test_workflow_inputs_valid() -> None:
    """Test WorkflowInputs allows normal dicts without content_base64."""
    inputs = WorkflowInputs(
        organization_id="org_123",
        dynamic_inputs={"normal_field": "text_data", "nested": {"key": "value"}},
    )
    assert inputs.organization_id == "org_123"
    assert inputs.dynamic_inputs["normal_field"] == "text_data"
