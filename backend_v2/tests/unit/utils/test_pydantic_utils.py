"""Unit tests for Pydantic model inflation utility."""

from typing import Annotated

import pytest
from pydantic import BaseModel, ConfigDict, Field

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.utils.pydantic_utils import inflate


class MockModel(BaseModel):
    """Strict test model for verifying Pydantic inflation behavior.

    Attributes:
        name: Label string for the mock entity.
        age: Non-negative integer age attribute.
    """

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    name: Annotated[str, Field(description="Label string for the mock entity.")]
    age: Annotated[int, Field(ge=0, description="Non-negative integer age attribute.")]


def test_inflate_none() -> None:
    """Verify that None input returns None."""
    assert inflate(None, MockModel) is None


def test_inflate_empty_dict() -> None:
    """Verify that an empty mapping returns None."""
    assert inflate({}, MockModel) is None


def test_inflate_dict() -> None:
    """Verify that a valid dictionary is inflated into MockModel."""
    data = {"name": "Test", "age": 0}
    model = inflate(data, MockModel)
    assert model is not None
    assert model.name == "Test"
    assert model.age == 0


def test_inflate_invalid_dict() -> None:
    """Verify that boundary violation (age = -1, min - 1) raises AppException."""
    data = {"name": "Test", "age": -1}
    with pytest.raises(AppException) as exc_info:
        inflate(data, MockModel)
    assert exc_info.value.details == {"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value}


def test_inflate_extra_field_forbidden() -> None:
    """Verify that undeclared extra fields trigger AppException under extra='forbid'."""
    data = {"name": "Test", "age": 25, "extra_field": "unexpected"}
    with pytest.raises(AppException) as exc_info:
        inflate(data, MockModel)
    assert exc_info.value.details == {"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value}


def test_inflate_model_instance() -> None:
    """Verify that an existing valid model instance inflates cleanly."""
    model = MockModel(name="Test", age=25)
    inflated = inflate(model, MockModel)
    assert inflated == model


def test_inflate_unrecognized() -> None:
    """Verify that non-mapping primitive input raises AppException."""
    with pytest.raises(AppException) as exc_info:
        inflate("not a dict or model", MockModel)
    assert exc_info.value.details == {"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value}
