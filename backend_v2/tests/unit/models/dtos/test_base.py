from unittest.mock import AsyncMock
import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.base import BaseDTO, BaseResponseDTO


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
    with pytest.raises(ValidationError, match="Extra inputs are not permitted|Extra inputs are not permitted"):
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
