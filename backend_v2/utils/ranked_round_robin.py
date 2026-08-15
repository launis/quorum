"""Ranked round-robin selection utility.

Single Source of Truth (SSOT) generic utility for fair, interleaved item selection
across multiple groups ranked by priority or informativeness.
"""

from collections.abc import Callable, Hashable, Sequence
from typing import Any


def ranked_round_robin_select[T](
    items: Sequence[T],
    group_key: Callable[[T], Hashable],
    rank_key: Callable[[T], Any],
    max_items: int,
    *,
    reverse_rank: bool = True,
) -> list[T]:
    """Select up to `max_items` by round-robin interleaving across groups ordered by rank.

    Algorithm:
    1. Returns empty list immediately if `max_items <= 0` or `not items`.
    2. Partitions items into buckets by `group_key`, preserving first-appearance order of groups.
    3. Sorts each group internally with `reverse=not reverse_rank`, positioning the highest-priority
       item at the tail (`-1` index) of each group list.
    4. Iteratively pops from the tail of each group in round-robin sequence in O(1) time.
    5. Deletes exhausted group entries via `del groups[k]`.
    6. Stops once `max_items` items are selected or all groups are exhausted.

    Complexity:
        O(N log N + K) where N is total items and K is min(len(items), max_items).
        Extraction per round is O(1) via native tail `.pop()`.

    Args:
        items: Sequence of items to select from.
        group_key: Callable returning a hashable group identifier for each item.
        rank_key: Callable returning a comparable sort key for each item.
        max_items: Maximum number of items to return in the interleaved output.
        reverse_rank: If True (default), highest rank key value is selected first.
            If False, lowest rank key value is selected first.

    Returns:
        List of up to `max_items` selected items.

    Raises:
        TypeError: If `group_key` produces unhashable keys or `rank_key` produces
            mutually incomparable keys within the same group.
    """
    # Phase 1, Step 2: Validate budget boundary
    if max_items <= 0 or not items:
        return []

    # Phase 1, Step 2: Group items preserving first appearance order
    groups: dict[Hashable, list[T]] = {}
    for item in items:
        g_key = group_key(item)
        groups.setdefault(g_key, []).append(item)

    # Phase 1, Step 2: Inverted sort so highest priority is at tail (-1 index) for O(1) pop
    sort_reverse = not reverse_rank
    for g_items in groups.values():
        g_items.sort(key=rank_key, reverse=sort_reverse)

    # Phase 1, Step 2: Round-robin selection popping from tail
    selected: list[T] = []
    while groups and len(selected) < max_items:
        # Freeze keys list to allow safe deletion during iteration
        for group_id in list(groups.keys()):
            group_items = groups[group_id]
            selected.append(group_items.pop())

            if not group_items:
                del groups[group_id]

            if len(selected) >= max_items:
                break

    return selected
