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


def test_domain_input_value_accepts_none() -> None:
    """Test contract: DomainInputValue union accepts None for optional/unmapped inputs."""
    inputs = WorkflowInputs(
        organization_id="org_123",
        dynamic_inputs={"optional_key": None, "str_key": "val"},
    )
    assert inputs.dynamic_inputs["optional_key"] is None
    assert inputs.dynamic_inputs["str_key"] == "val"


def test_execution_inputs_handles_none_values() -> None:
    """Test contract: ExecutionInputsDTO cleanly accepts None values in raw_inputs and dynamic_inputs."""
    dto = ExecutionInputsDTO(
        raw_inputs={"id": None, "text": "sample"},
        dynamic_inputs={"id": None, "score": 4.5},
    )
    assert dto.raw_inputs["id"] is None
    assert dto.raw_inputs["text"] == "sample"
    assert dto.dynamic_inputs["id"] is None
    assert dto.dynamic_inputs["score"] == 4.5


def test_domain_input_value_accepts_flattened_atoms() -> None:
    """Test contract: DomainInputValue union accepts FlattenedAtom and list[FlattenedAtom]."""
    from backend_v2.models.dtos.flattened_atom import FlattenedAtom

    atom = FlattenedAtom(
        atom_id="tda_123",
        question="test question",
        extraction_rule="rule",
        anchor_target="target",
        is_inverse=False,
        acceptance_criteria=(),
        anti_patterns=(),
        syntactic_anchors=(),
    )
    dto = ExecutionInputsDTO(
        raw_inputs={"shuffled_atoms": [atom]},
        dynamic_inputs={"atom": atom},
    )
    assert len(dto.raw_inputs["shuffled_atoms"]) == 1  # type: ignore[arg-type]
    assert dto.dynamic_inputs["atom"].atom_id == "tda_123"  # type: ignore[union-attr]


def test_dlq_atom_schema_valid() -> None:
    """Test valid DLQAtomSchema creation and immutability."""
    from backend_v2.models.domain.inputs import DLQAtomSchema

    dlq = DLQAtomSchema(atom_id="atm_123", tda_id="tda_456", status="FAILED")
    assert dlq.atom_id == "atm_123"
    assert dlq.tda_id == "tda_456"
    assert dlq.status == "FAILED"


def test_validate_no_base64_validator_direct() -> None:
    """Test contract: validate_no_base64 directly raises ValueError on Base64Attachment."""
    attachment = Base64Attachment(filename="doc.pdf", content_base64="JVBERi...")
    with pytest.raises(ValueError, match="Base64Attachment is strictly forbidden in WorkflowInputs"):
        WorkflowInputs.validate_no_base64({"attachment": attachment})  # type: ignore[dict-item]


def test_domain_input_value_accepts_reduced_atoms() -> None:
    """Test contract: DomainInputValue union accepts ReducedAtomDTO and list[ReducedAtomDTO]."""
    from backend_v2.models.dtos.atom_evaluation import ReducedAtomDTO
    from backend_v2.models.enums import LaxExecutionStatus

    atom = ReducedAtomDTO(
        tda_id="tda_1234567890abcdef",
        status=LaxExecutionStatus.PASSED,
        reasoning="Compact reasoning.",
        source_quote="Quote text.",
    )
    atoms_list = [atom]

    inputs = WorkflowInputs(
        organization_id="org_123",
        dynamic_inputs={
            "single_reduced": atom,
            "list_reduced": atoms_list,
        },
    )
    assert inputs.dynamic_inputs["single_reduced"] == atom
    assert inputs.dynamic_inputs["list_reduced"] == atoms_list

