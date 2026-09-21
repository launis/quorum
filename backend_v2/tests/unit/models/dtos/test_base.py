"""Unit tests for base DTOs and response schemas."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.base import (
    BaseDTO,
    BaseResponseDTO,
    DataStarvationEvent,
    GenericStatusResponseDTO,
)


class MockDTO(BaseDTO):
    name: str
    age: int


class MockResponseDTO(BaseResponseDTO):
    name: str


def test_base_dto_is_frozen_and_strict() -> None:
    """Test that BaseDTO inherits V2CoreBase strictness and immutability."""
    dto = MockDTO(name="test", age=30)
    assert dto.name == "test"

    # Should be frozen
    with pytest.raises(ValidationError, match="Instance is frozen"):
        dto.name = "new"  # type: ignore[misc]

    # Should forbid extra
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        MockDTO.model_validate({"name": "test", "age": 30, "extra": "invalid"})


def test_base_response_dto_excludes_organization_id() -> None:
    """Test that BaseResponseDTO strictly excludes organization_id in JSON dumps."""
    dto = MockResponseDTO(name="test", organization_id="org_123")

    # organization_id is accessible in Python
    assert dto.organization_id == "org_123"

    # but excluded from serialization (preventing cross-tenant leaks)
    dumped = dto.model_dump()
    assert "name" in dumped
    assert "organization_id" not in dumped

    dumped_json = dto.model_dump_json()
    assert "org_123" not in dumped_json


def test_generic_status_response_dto() -> None:
    """Verify GenericStatusResponseDTO default status and attributes."""
    dto = GenericStatusResponseDTO(message="Operation successful")
    assert dto.status == "ok"
    assert dto.message == "Operation successful"

    custom_dto = GenericStatusResponseDTO(status="created", message="Resource created")
    assert custom_dto.status == "created"
    assert custom_dto.message == "Resource created"

    with pytest.raises(ValidationError):
        GenericStatusResponseDTO(message="missing", extra_prop=123)  # type: ignore[call-arg]


def test_data_starvation_event() -> None:
    """Verify DataStarvationEvent defaults, validation, and immutability."""
    event = DataStarvationEvent(total_atoms=0)
    assert event.event_type == "starvation"
    assert event.total_atoms == 0
    assert event.reason == "Data starvation: insufficient atoms"

    custom_event = DataStarvationEvent(
        total_atoms=2,
        reason="Custom starvation threshold not met",
    )
    assert custom_event.total_atoms == 2
    assert custom_event.reason == "Custom starvation threshold not met"

    # Negative total atoms fails validation
    with pytest.raises(ValidationError):
        DataStarvationEvent(total_atoms=-1)

    # Invalid event_type discriminator fails validation
    with pytest.raises(ValidationError):
        DataStarvationEvent(total_atoms=0, event_type="other")  # type: ignore[arg-type]

    # Frozen immutability check
    with pytest.raises(ValidationError, match="Instance is frozen"):
        event.total_atoms = 5  # type: ignore[misc]

