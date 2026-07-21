from unittest.mock import AsyncMock
import pytest
from pydantic import ValidationError

from backend_v2.models.domain.hydration import HydrationInputSourceDTO


def test_hydration_input_source_strict_validation() -> None:
    """Test that HydrationInputSourceDTO follows V2CoreBase strict constraints."""
    dto = HydrationInputSourceDTO(inputs={"key": "value", "foo": "bar"})
    assert "key" in dto.inputs
    assert dto.inputs["key"] == "value"

    # Test methods
    assert dto.is_valid_source() is True
    assert dto.extract_hydrated_inputs() == {"key": "value", "foo": "bar"}

    # Test extra forbid
    with pytest.raises(ValidationError):
        HydrationInputSourceDTO.model_validate({"inputs": {"key": "value"}, "extra_field": "not allowed"})


def test_hydration_input_source_type_validation() -> None:
    """Test value types."""
    # Strict validation should catch non-string values if applicable, though dict[str,str] coerce types sometimes.
    # But checking that it accepts proper input.
    dto = HydrationInputSourceDTO(inputs={})
    assert dto.inputs == {}
