"""Unit tests for WorkflowSchemaResponseDTO."""

import pytest
from pydantic import ValidationError

from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.step import ExpectedInput
from backend_v2.models.dtos.workflow_schema import WorkflowSchemaResponseDTO


def test_workflow_schema_response_dto_default() -> None:
    """Verify default initialization produces an empty expected_inputs list."""
    dto = WorkflowSchemaResponseDTO()
    assert dto.expected_inputs == []


def test_workflow_schema_response_dto_with_inputs() -> None:
    """Verify initialization with ExpectedInput instances."""
    input_item = ExpectedInput(
        input_key="product_brief",
        label=I18nText(translations={"en": "Product Brief", "fi": "Tuotetiivistelmä"}),
        description=I18nText(translations={"en": "Brief description"}),
        required=True,
        input_modes=["file", "text"],
    )
    dto = WorkflowSchemaResponseDTO(expected_inputs=[input_item])
    assert len(dto.expected_inputs) == 1
    assert dto.expected_inputs[0].input_key == "product_brief"
    assert dto.expected_inputs[0].required is True


def test_workflow_schema_response_dto_extra_forbidden() -> None:
    """Verify extra='forbid' raises ValidationError when unknown fields are passed."""
    with pytest.raises(ValidationError):
        WorkflowSchemaResponseDTO.model_validate({"expected_inputs": [], "unknown_field": "disallowed"})


def test_workflow_schema_response_dto_strict_type_enforcement() -> None:
    """Verify strict type enforcement on expected_inputs."""
    with pytest.raises(ValidationError):
        WorkflowSchemaResponseDTO.model_validate({"expected_inputs": "not_a_list"})


def test_workflow_schema_response_dto_serialization_roundtrip() -> None:
    """Verify model_dump and model_validate roundtrip preservation."""
    input_item = ExpectedInput(
        input_key="assignment_brief",
        label=I18nText(translations={"en": "Assignment", "fi": "Tehtävänanto"}),
        description=I18nText(translations={"en": "Assignment description"}),
        required=False,
        input_modes=["assignment"],
    )
    dto = WorkflowSchemaResponseDTO(expected_inputs=[input_item])
    dumped = dto.model_dump(mode="json")
    assert "expected_inputs" in dumped
    assert dumped["expected_inputs"][0]["input_key"] == "assignment_brief"

    reconstituted = WorkflowSchemaResponseDTO.model_validate(dumped)
    assert len(reconstituted.expected_inputs) == 1
    assert reconstituted.expected_inputs[0].input_key == "assignment_brief"

