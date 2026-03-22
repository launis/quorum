"""Unit tests for the Deep Merge utility.

Verifies that parallel properties are preserved inside nested states and
that base dictionaries are not mutated.
"""


from backend_v2.utils.dict_utils import deep_merge_dicts


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
