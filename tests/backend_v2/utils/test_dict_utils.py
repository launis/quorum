"""Unit tests for the Deep Merge utility.

Verifies that parallel properties are preserved inside nested states and
that base dictionaries are not mutated.
"""


from backend_v2.exceptions import MissingInputMappingError
import pytest
from backend_v2.utils.dict_utils import deep_merge_dicts, resolve_dot_notation


def test_deep_merge_dicts_nested_preservation() -> None:
    """Test that nested dictionaries retain non-overlapping parallel keys."""
    base = {
        "matrix_A": {
            "justification": "hyvä",
            "metadata": {"source": "test"}
        },
        "other_key": 1
    }
    update = {
        "matrix_A": {
            "score": 100.0,
            "metadata": {"processed": True}
        }
    }

    result = deep_merge_dicts(base, update)

    # Asserting parallel keys are preserved
    assert result["matrix_A"]["justification"] == "hyvä"
    assert result["matrix_A"]["score"] == 100.0
    assert result["matrix_A"]["metadata"]["source"] == "test"
    assert result["matrix_A"]["metadata"]["processed"] is True
    assert result["other_key"] == 1


def test_deep_merge_dicts_overwrite_atomic() -> None:
    """Test that primitive values are safely overwritten."""
    base = {"status": "pending", "count": 1}
    update = {"status": "completed", "count": 2, "new_key": "exists"}

    result = deep_merge_dicts(base, update)

    assert result["status"] == "completed"
    assert result["count"] == 2
    assert result["new_key"] == "exists"


def test_deep_merge_dicts_preserves_original_immutability() -> None:
    """Ensure that the original base dictionary is strictly not mutated."""
    base = {"nested": {"a": 1}}
    update = {"nested": {"b": 2}}

    deep_merge_dicts(base, update)

    assert "b" not in base["nested"]

def test_deep_merge_dicts_overwrite_dict_with_atomic() -> None:
    """Ensure that a dict can be overwritten by atomic values if specified."""
    base = {"nested": {"a": 1}}
    update = {"nested": "destroyed"}

    result = deep_merge_dicts(base, update)

    assert result["nested"] == "destroyed"


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
    state = {"user": {}}
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
    state = {"users": []}
    with pytest.raises(MissingInputMappingError) as exc_info:
        resolve_dot_notation(state, "users.0")
    assert "Failed at '0': IndexError" in exc_info.value.details["reason"]


def test_resolve_dot_notation_invalid_list_index() -> None:
    state = {"users": []}
    with pytest.raises(MissingInputMappingError) as exc_info:
        resolve_dot_notation(state, "users.not_an_int")
    assert "Failed at 'not_an_int': ValueError" in exc_info.value.details["reason"]


def test_resolve_dot_notation_empty_path() -> None:
    state = {"a": 1}
    assert resolve_dot_notation(state, "") == state
