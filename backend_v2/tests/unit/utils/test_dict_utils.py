from unittest.mock import AsyncMock
import pytest

from backend_v2.exceptions import MissingInputMappingError
from backend_v2.utils.dict_utils import deep_merge_dicts, resolve_dot_notation


def test_deep_merge_dicts() -> None:
    base = {"a": 1, "b": {"c": 2}}
    update = {"b": {"d": 3}, "e": 4}
    merged = deep_merge_dicts(base, update)
    assert merged == {"a": 1, "b": {"c": 2, "d": 3}, "e": 4}
    assert base == {"a": 1, "b": {"c": 2}}  # Original remains unmutated


def test_resolve_dot_notation_dict() -> None:
    state = {"user": {"profile": {"age": 30}}}
    assert resolve_dot_notation(state, "user.profile.age") == 30


def test_resolve_dot_notation_object() -> None:
    class Profile:
        age = 30

    class User:
        profile = Profile()

    class State:
        user = User()

    state = State()
    assert resolve_dot_notation(state, "user.profile.age") == 30


def test_resolve_dot_notation_list() -> None:
    state = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
    assert resolve_dot_notation(state, "users.1.name") == "Bob"


def test_resolve_dot_notation_missing_dict_key() -> None:
    state: dict[str, object] = {"user": {}}
    with pytest.raises(MissingInputMappingError) as exc_info:
        resolve_dot_notation(state, "user.profile.age")
    assert "Failed at 'profile': KeyError" in exc_info.value.details["reason"]
    assert exc_info.value.status_code == 400


def test_resolve_dot_notation_missing_attribute() -> None:
    class User:
        pass

    state = {"user": User()}
    with pytest.raises(MissingInputMappingError) as exc_info:
        resolve_dot_notation(state, "user.profile.age")
    assert "Failed at 'profile': AttributeError" in exc_info.value.details["reason"]


def test_resolve_dot_notation_missing_index() -> None:
    state: dict[str, list[object]] = {"users": []}
    with pytest.raises(MissingInputMappingError) as exc_info:
        resolve_dot_notation(state, "users.0")
    assert "Failed at '0': IndexError" in exc_info.value.details["reason"]


def test_resolve_dot_notation_invalid_list_index() -> None:
    state: dict[str, list[object]] = {"users": []}
    with pytest.raises(MissingInputMappingError) as exc_info:
        resolve_dot_notation(state, "users.not_an_int")
    assert "Failed at 'not_an_int': ValueError" in exc_info.value.details["reason"]


def test_resolve_dot_notation_empty_path() -> None:
    state = {"a": 1}
    assert resolve_dot_notation(state, "") == state
