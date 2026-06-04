import pytest

from backend_v2.exceptions import MissingInputMappingError
from backend_v2.utils.dict_utils import compress_anchors, deep_merge_dicts, resolve_dot_notation


def test_deep_merge_dicts():
    base = {"a": 1, "b": {"c": 2}}
    update = {"b": {"d": 3}, "e": 4}
    merged = deep_merge_dicts(base, update)
    assert merged == {"a": 1, "b": {"c": 2, "d": 3}, "e": 4}
    assert base == {"a": 1, "b": {"c": 2}}  # Original remains unmutated


def test_resolve_dot_notation_dict():
    state = {"user": {"profile": {"age": 30}}}
    assert resolve_dot_notation(state, "user.profile.age") == 30


def test_resolve_dot_notation_object():
    class Profile:
        age = 30

    class User:
        profile = Profile()

    class State:
        user = User()

    state = State()
    assert resolve_dot_notation(state, "user.profile.age") == 30


def test_resolve_dot_notation_list():
    state = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
    assert resolve_dot_notation(state, "users.1.name") == "Bob"


def test_resolve_dot_notation_missing_dict_key():
    state = {"user": {}}
    with pytest.raises(MissingInputMappingError) as exc_info:
        resolve_dot_notation(state, "user.profile.age")
    assert "Failed at 'profile': KeyError" in exc_info.value.details["reason"]
    assert exc_info.value.status_code == 400


def test_resolve_dot_notation_missing_attribute():
    class User:
        pass

    state = {"user": User()}
    with pytest.raises(MissingInputMappingError) as exc_info:
        resolve_dot_notation(state, "user.profile.age")
    assert "Failed at 'profile': AttributeError" in exc_info.value.details["reason"]


def test_resolve_dot_notation_missing_index():
    state = {"users": []}
    with pytest.raises(MissingInputMappingError) as exc_info:
        resolve_dot_notation(state, "users.0")
    assert "Failed at '0': IndexError" in exc_info.value.details["reason"]


def test_resolve_dot_notation_invalid_list_index():
    state = {"users": []}
    with pytest.raises(MissingInputMappingError) as exc_info:
        resolve_dot_notation(state, "users.not_an_int")
    assert "Failed at 'not_an_int': ValueError" in exc_info.value.details["reason"]


def test_resolve_dot_notation_empty_path():
    state = {"a": 1}
    assert resolve_dot_notation(state, "") == state


def test_compress_anchors_preserves_short_list() -> None:
    """Verify that anchor lists with ≤2 items pass through unchanged."""
    assert compress_anchors(["anchor_one"]) == ["anchor_one"]
    assert compress_anchors(["a", "b"]) == ["a", "b"]
    assert compress_anchors([]) == []


def test_compress_anchors_compresses_long_list() -> None:
    """Verify that anchor lists with >2 items are compressed to hybrid signal."""
    anchors = [
        "short",
        "medium length anchor",
        "this is the longest anchor string in the list by far",
        "another",
        "yet another",
        "sixth one",
        "seventh",
    ]
    result = compress_anchors(anchors)

    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(item, str) for item in result)
    assert "this is the longest anchor string" in result[0]
    assert result[1] == "[+6 additional anchors found]"


def test_compress_anchors_truncates_long_anchor() -> None:
    """Verify that the best anchor is truncated to 100 chars with ellipsis."""
    long_anchor = "A" * 150
    result = compress_anchors([long_anchor, "short", "also short"])

    assert len(result) == 2
    assert result[0] == "A" * 100 + "..."
    assert len(result[0]) == 103
    assert result[1] == "[+2 additional anchors found]"
