from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

from backend_v2.exceptions import AppException, format_validation_error


class DummyModel(BaseModel):
    name: str
    age: int

def test_format_validation_error_valid_pydantic() -> None:
    """Test that a valid Pydantic error is properly formatted."""
    try:
        # Ignore mypy argument warning since we deliberately want to trigger ValidationError
        DummyModel(name="test")  # type: ignore[call-arg]
    except ValidationError as e:
        result = format_validation_error(e)
        assert "DummyModel validation failed. Missing required fields: age" in result

def test_format_validation_error_internal_error(monkeypatch: Any) -> None:
    """Test the fail-fast behavior when Pydantic internal structure crashes the formatter."""
    import pydantic

    class FakeError(Exception):
        pass

    monkeypatch.setattr(pydantic, "ValidationError", FakeError)

    with pytest.raises(AppException) as exc_info:
        format_validation_error(FakeError("Fake error here"))

    assert exc_info.value.status_code == 500
    assert exc_info.value.error_code == "INTERNAL_SERVER_ERROR"
    assert "Internal error during error formatting" in str(exc_info.value)
