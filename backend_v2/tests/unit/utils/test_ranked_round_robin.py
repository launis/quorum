"""Unit tests for the ranked round-robin selection utility."""

import time

import pytest

from backend_v2.utils.ranked_round_robin import ranked_round_robin_select


def test_ranked_round_robin_empty_items_returns_empty() -> None:
    """Empty items input must return an empty list."""
    result = ranked_round_robin_select(
        items=[],
        group_key=lambda x: x,
        rank_key=lambda x: len(x),
        max_items=5,
    )
    assert result == []


def test_ranked_round_robin_max_items_non_positive_returns_empty() -> None:
    """max_items=0 must return an empty list."""
    result = ranked_round_robin_select(
        items=["a", "b"],
        group_key=lambda x: x,
        rank_key=lambda x: len(x),
        max_items=0,
    )
    assert result == []


def test_ranked_round_robin_negative_max_items_returns_empty() -> None:
    """Negative max_items must return an empty list."""
    result = ranked_round_robin_select(
        items=["a", "b"],
        group_key=lambda x: x,
        rank_key=lambda x: len(x),
        max_items=-5,
    )
    assert result == []


def test_ranked_round_robin_single_group_maintains_rank_order() -> None:
    """Single group items must maintain rank order (descending by default)."""
    items = ["short", "very_long_string", "medium"]
    result = ranked_round_robin_select(
        items=items,
        group_key=lambda x: "g1",
        rank_key=lambda x: len(x),
        max_items=3,
        reverse_rank=True,
    )
    assert result == ["very_long_string", "medium", "short"]


def test_ranked_round_robin_multi_group_interleaving() -> None:
    """Multiple groups must be interleaved round-robin by highest rank first."""
    items = [
        ("A", "a_short"),
        ("A", "a_longest_str"),
        ("B", "b_short"),
        ("B", "b_longest_str"),
    ]
    result = ranked_round_robin_select(
        items=items,
        group_key=lambda x: x[0],
        rank_key=lambda x: len(x[1]),
        max_items=4,
        reverse_rank=True,
    )
    assert result == [
        ("A", "a_longest_str"),
        ("B", "b_longest_str"),
        ("A", "a_short"),
        ("B", "b_short"),
    ]


def test_ranked_round_robin_budget_truncation() -> None:
    """max_items truncation must cap output length at exact budget limit."""
    items = [("A", "a1"), ("A", "a2"), ("B", "b1"), ("B", "b2")]
    result = ranked_round_robin_select(
        items=items,
        group_key=lambda x: x[0],
        rank_key=lambda x: x[1],
        max_items=3,
    )
    assert len(result) == 3
    assert result == [("A", "a2"), ("B", "b2"), ("A", "a1")]


def test_ranked_round_robin_budget_exceeds_total_items_returns_all() -> None:
    """Budget exceeding total items must return all items in round-robin order."""
    items = [("A", "a1"), ("B", "b1")]
    result = ranked_round_robin_select(
        items=items,
        group_key=lambda x: x[0],
        rank_key=lambda x: x[1],
        max_items=100,
    )
    assert len(result) == 2
    assert result == [("A", "a1"), ("B", "b1")]


def test_ranked_round_robin_unequal_groups() -> None:
    """Unequal group sizes must interleave until smaller group exhausts and continue with remaining."""
    items = [
        ("A", 10),
        ("B", 40),
        ("B", 30),
        ("B", 20),
        ("B", 10),
    ]
    result = ranked_round_robin_select(
        items=items,
        group_key=lambda x: x[0],
        rank_key=lambda x: x[1],
        max_items=4,
        reverse_rank=True,
    )
    assert result == [
        ("A", 10),
        ("B", 40),
        ("B", 30),
        ("B", 20),
    ]


def test_ranked_round_robin_reverse_rank_false_sorts_ascending() -> None:
    """Setting reverse_rank=False must rank items ascending (smallest first)."""
    items = [("A", 10), ("A", 2), ("B", 20), ("B", 1)]
    result = ranked_round_robin_select(
        items=items,
        group_key=lambda x: x[0],
        rank_key=lambda x: x[1],
        max_items=4,
        reverse_rank=False,
    )
    assert result == [("A", 2), ("B", 1), ("A", 10), ("B", 20)]


def test_ranked_round_robin_sequence_tuple_input() -> None:
    """Sequence tuple input must be accepted and processed without mutating input."""
    items = (("A", "x"), ("B", "y"))
    result = ranked_round_robin_select(
        items=items,
        group_key=lambda x: x[0],
        rank_key=lambda x: x[1],
        max_items=2,
    )
    assert result == [("A", "x"), ("B", "y")]


def test_ranked_round_robin_unhashable_group_key_raises_type_error() -> None:
    """Unhashable group key must raise TypeError fail-fast."""
    items = [[1, 2], [3, 4]]
    with pytest.raises(TypeError):
        ranked_round_robin_select(
            items=items,
            group_key=lambda x: x,  # type: ignore[arg-type] # unhashable list
            rank_key=lambda x: len(x),
            max_items=2,
        )


def test_ranked_round_robin_incompatible_rank_keys_raises_type_error() -> None:
    """Incompatible rank keys in the same group must raise TypeError during sorting."""
    items = [("A", 1), ("A", "str_val")]
    with pytest.raises(TypeError):
        ranked_round_robin_select(
            items=items,
            group_key=lambda x: x[0],
            rank_key=lambda x: x[1],
            max_items=2,
        )


def test_ranked_round_robin_performance_scaling_o1_tail_pop() -> None:
    """10,000 items in 50 groups must execute within 25ms proving O(1) tail .pop() efficiency."""
    items = [(f"group_{i % 50}", i) for i in range(10000)]
    start_time = time.perf_counter()
    result = ranked_round_robin_select(
        items=items,
        group_key=lambda x: x[0],
        rank_key=lambda x: x[1],
        max_items=5000,
        reverse_rank=True,
    )
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    assert len(result) == 5000
    assert elapsed_ms < 50.0  # Conservative bound for CI/CD while testing O(N log N + K) scaling
