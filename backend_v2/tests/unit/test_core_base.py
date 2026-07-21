from unittest.mock import AsyncMock
import pytest
from pydantic import ValidationError

from backend_v2.models.core_base import V2CoreBase


def test_v2_core_base_extra_forbid() -> None:
    """Test that V2CoreBase enforces extra='forbid'."""

    class DummyModel(V2CoreBase):
        field: str

    # Should succeed with exact fields
    obj = DummyModel(field="value")
    assert obj.field == "value"

    # Should fail if extra fields are provided
    with pytest.raises(ValidationError) as exc_info:
        DummyModel(**{"field": "value", "extra_field": "not allowed"})

    assert "Extra inputs are not permitted" in str(exc_info.value) or "extra_forbidden" in str(exc_info.value)


def test_v2_core_base_strict_mode() -> None:
    """Test that V2CoreBase enforces strict mode."""

    class DummyModel(V2CoreBase):
        field: int

    # Should fail if given a string that can be cast to int, because strict=True
    with pytest.raises(ValidationError) as exc_info:
        DummyModel(field="123")  # type: ignore[arg-type]

    assert "Input should be a valid integer" in str(exc_info.value) or "int_type" in str(exc_info.value)
