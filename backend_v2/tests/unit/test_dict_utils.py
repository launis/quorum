import pytest
from pydantic import BaseModel

from backend_v2.exceptions import ErrorCodes, MissingInputMappingError
from backend_v2.utils.dict_utils import deep_merge_dicts, resolve_dot_notation


def test_deep_merge_dicts() -> None:
    """Test safe merging without overwriting nested dictionaries."""
    from typing import Any

    base: dict[str, Any] = {"a": 1, "b": {"c": 2, "d": 3}}
    update = {"b": {"c": 99, "e": 4}, "f": 5}

    result = deep_merge_dicts(base, update)

    assert result["a"] == 1
    assert result["b"]["c"] == 99  # Overwritten
    assert result["b"]["d"] == 3  # Preserved
    assert result["b"]["e"] == 4  # Added
    assert result["f"] == 5  # Added

    # Original unmutated
    assert base["b"]["c"] == 2


class DummyObj(BaseModel):
    value: int
    nested: dict[str, str]


def test_resolve_dot_notation_success() -> None:
    """Test successful dot notation resolution."""
    state = {
        "user": {"profile": {"age": 30}, "tags": ["a", "b", "c"], "obj": DummyObj(value=42, nested={"key": "val"})}
    }

    assert resolve_dot_notation(state, "user.profile.age") == 30
    assert resolve_dot_notation(state, "user.tags.1") == "b"
    assert resolve_dot_notation(state, "user.obj.value") == 42
    assert resolve_dot_notation(state, "user.obj.nested.key") == "val"
    assert resolve_dot_notation(state, "") == state


def test_resolve_dot_notation_failure() -> None:
    """Test dot notation throws MissingInputMappingError correctly."""
    state = {"user": {"profile": {"age": 30}}}

    with pytest.raises(MissingInputMappingError) as exc_info:
        resolve_dot_notation(state, "user.invalid.age")

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.INPUT_RESOLUTION_FAILED.value
    assert exc_info.value.details["path"] == "user.invalid.age"
    assert "Failed at 'invalid'" in exc_info.value.message
