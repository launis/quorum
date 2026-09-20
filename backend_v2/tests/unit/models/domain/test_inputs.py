"""Unit tests for workflow input models, closed unions, and validation invariants."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.inputs import (
    Base64Attachment,
    DomainInputValue,
    IngressInputValue,
    WorkflowInputs,
    WorkflowInputsIngress,
)
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.dtos.inputs import GuidedReflectionInputDTO, QuestionAnswerPair


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


def test_ingress_input_value_accepts_valid_types() -> None:
    """Test contract: IngressInputValue union accepts all allowed types without error."""
    attachment = Base64Attachment(filename="sample.txt", content_base64="aGVsbG8=")
    questionnaire = GuidedReflectionInputDTO(
        pairs=[QuestionAnswerPair(question="What is the goal?", answer="To test.")],
    )

    valid_payloads: dict[str, IngressInputValue] = {
        "text_key": "sample string",
        "int_key": 42,
        "float_key": 3.14,
        "bool_key": True,
        "list_key": ["alpha", "beta"],
        "attachment_key": attachment,
        "questionnaire_key": questionnaire,
    }

    ingress = WorkflowInputsIngress(dynamic_inputs=valid_payloads)
    assert ingress.dynamic_inputs["text_key"] == "sample string"
    assert ingress.dynamic_inputs["int_key"] == 42
    assert ingress.dynamic_inputs["attachment_key"] == attachment


def test_ingress_input_value_rejects_nested_dict() -> None:
    """Test contract: IngressInputValue rejects arbitrary untyped nested dictionaries."""
    with pytest.raises(ValidationError):
        WorkflowInputsIngress(
            dynamic_inputs={"nested": {"key": "val"}},  # type: ignore[arg-type]
        )


def test_domain_input_value_rejects_base64_attachment() -> None:
    """Test contract: DomainInputValue / WorkflowInputs mathematically rejects Base64Attachment."""
    attachment = Base64Attachment(filename="doc.pdf", content_base64="JVBERi...")
    with pytest.raises(ValidationError):
        WorkflowInputs(
            dynamic_inputs={"attachment": attachment},  # type: ignore[arg-type]
        )


def test_domain_input_value_rejects_raw_base64_dict() -> None:
    """Test contract: WorkflowInputs rejects raw dictionary payloads containing base64 data."""
    with pytest.raises(ValidationError):
        WorkflowInputs(
            dynamic_inputs={"file": {"content_base64": "binary_blob"}},  # type: ignore[arg-type]
        )


def test_workflow_inputs_valid_domain_types() -> None:
    """Test WorkflowInputs allows valid domain inputs excluding Base64Attachment."""
    questionnaire = GuidedReflectionInputDTO(
        pairs=[QuestionAnswerPair(question="Q", answer="A")],
    )
    valid_payloads: dict[str, DomainInputValue] = {
        "normal_field": "text_data",
        "int_field": 100,
        "list_field": ["str1", "str2"],
        "questionnaire": questionnaire,
    }
    inputs = WorkflowInputs(
        organization_id="org_123",
        dynamic_inputs=valid_payloads,
    )
    assert inputs.organization_id == "org_123"
    assert inputs.dynamic_inputs["normal_field"] == "text_data"
    assert inputs.dynamic_inputs["int_field"] == 100


def test_execution_inputs_rejects_raw_string_without_coercion() -> None:
    """Test contract: ExecutionInputsDTO rejects raw string inputs without silent coercion."""
    with pytest.raises(ValidationError):
        ExecutionInputsDTO(raw_inputs="hello")  # type: ignore[arg-type]
