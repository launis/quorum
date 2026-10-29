"""Unit tests for HydrationInputSourceDTO."""

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.hydration import HydrationInputSourceDTO


def test_hydration_input_source_strict_validation() -> None:
    """Test that HydrationInputSourceDTO follows V2CoreBase strict constraints."""
    dto = HydrationInputSourceDTO(inputs={"key": "value", "foo": "bar"})
    assert "key" in dto.inputs
    assert dto.inputs["key"] == "value"

    # Test methods and defensive copy behavior
    assert dto.is_valid_source() is True
    extracted = dto.extract_hydrated_inputs()
    assert extracted == {"key": "value", "foo": "bar"}
    extracted["mutated"] = "change"
    assert "mutated" not in dto.inputs

    # Negative case 1: Extra fields are strictly forbidden
    with pytest.raises(ValidationError):
        HydrationInputSourceDTO.model_validate({"inputs": {"key": "value"}, "extra_field": "not allowed"})


def test_hydration_input_source_type_validation() -> None:
    """Test value types and negative boundary cases under strict Pydantic V2."""
    dto = HydrationInputSourceDTO(inputs={})
    assert dto.inputs == {}

    # Negative case 2: Non-string dictionary values rejected in strict mode
    with pytest.raises(ValidationError):
        HydrationInputSourceDTO.model_validate({"inputs": {"key": 123}})

    # Negative case 3: Missing required inputs field rejected
    with pytest.raises(ValidationError):
        HydrationInputSourceDTO.model_validate({})

    # Negative case 4: Non-dict inputs payload rejected
    with pytest.raises(ValidationError):
        HydrationInputSourceDTO.model_validate({"inputs": ["not", "a", "dict"]})
