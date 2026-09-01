"""Unit tests for state_reducer.py following ISTQB Equivalence Partitions."""

from backend_v2.services.orchestrator.state_reducer import merge_dynamic_inputs


def test_merge_dynamic_inputs_with_none_inputs() -> None:
    """ISTQB Partition 1: None inputs handling."""
    assert merge_dynamic_inputs(None, None) == {}
    assert merge_dynamic_inputs({"a": 1}, None) == {"a": 1}
    assert merge_dynamic_inputs(None, {"b": 2}) == {"b": 2}


def test_merge_dynamic_inputs_pure_immutability() -> None:
    """ISTQB Partition 2: Verifies base and delta are never mutated in-place."""
    base = {"nested": {"score": 10, "meta": {"author": "alice"}}, "count": 1}
    delta = {"nested": {"score": 20, "extra": "new"}, "count": 2}

    merged = merge_dynamic_inputs(base, delta)

    # Merged has combined state
    assert merged == {
        "nested": {"score": 20, "meta": {"author": "alice"}, "extra": "new"},
        "count": 2,
    }
    # Base is unchanged
    assert base == {"nested": {"score": 10, "meta": {"author": "alice"}}, "count": 1}
    # Delta is unchanged
    assert delta == {"nested": {"score": 20, "extra": "new"}, "count": 2}


def test_merge_dynamic_inputs_nested_recursive_merging() -> None:
    """ISTQB Partition 3: Deep nested merging across multiple levels."""
    base = {
        "scoring_result": {
            "matrix_a": {"score": 4.5, "claims": ["c1", "c2"]},
            "matrix_b": {"score": 3.0},
        },
        "step_name": "initial",
    }
    delta = {
        "scoring_result": {
            "matrix_a": {"score": 5.0, "confidence": 0.95},
            "matrix_c": {"score": 4.0},
        },
        "step_name": "updated",
    }

    result = merge_dynamic_inputs(base, delta)

    assert result == {
        "scoring_result": {
            "matrix_a": {"score": 5.0, "claims": ["c1", "c2"], "confidence": 0.95},
            "matrix_b": {"score": 3.0},
            "matrix_c": {"score": 4.0},
        },
        "step_name": "updated",
    }


def test_merge_dynamic_inputs_with_replace_flag() -> None:
    """ISTQB Partition 4: __replace__: True directive replaces sub-dict and strips flag."""
    base = {
        "scoring_result": {
            "matrix_a": {"score": 4.5, "claims": ["c1", "c2"], "stale": True},
            "matrix_b": {"score": 3.0},
        }
    }
    delta = {
        "scoring_result": {
            "matrix_a": {"score": 5.0, "claims": ["c3"], "__replace__": True},
        }
    }

    result = merge_dynamic_inputs(base, delta)

    assert result == {
        "scoring_result": {
            "matrix_a": {"score": 5.0, "claims": ["c3"]},
            "matrix_b": {"score": 3.0},
        }
    }
    assert "__replace__" not in result["scoring_result"]["matrix_a"]


def test_merge_dynamic_inputs_scalar_and_list_overwrites() -> None:
    """ISTQB Boundary: Scalar and list value replacements."""
    base = {
        "numbers": [1, 2, 3],
        "flag": True,
        "label": "old",
    }
    delta = {
        "numbers": [4, 5],
        "flag": False,
        "label": "new",
    }

    result = merge_dynamic_inputs(base, delta)

    assert result == {
        "numbers": [4, 5],
        "flag": False,
        "label": "new",
    }
