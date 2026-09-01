"""Pure state reduction utilities for orchestrator execution and dynamic inputs merging.

Provides non-destructive merging of nested dictionaries for hook states and dynamic inputs,
preventing shallow merge data loss on nested scoring, validation, or metadata structures.
"""

from __future__ import annotations

import copy
from typing import Any


def merge_dynamic_inputs(
    base: dict[str, Any] | None,
    delta: dict[str, Any] | None,
) -> dict[str, Any]:
    """Recursively merges a delta dictionary into a copy of the base dictionary.

    Guarantees:
    1. Base and delta are never mutated in-place (pure function).
    2. Nested dictionaries are recursively merged rather than overwritten.
    3. If a dictionary in delta contains `__replace__: True`, it completely replaces
       the base sub-dictionary instead of merging into it.
    4. Non-dictionary values in delta overwrite the corresponding base keys.
    5. Returns a new deep copy with all `__replace__` directives stripped.

    Args:
        base: The original base dictionary, or None.
        delta: The dictionary containing new updates, or None.

    Returns:
        A new deeply merged dictionary.
    """
    if base is None:
        base = {}
    if delta is None:
        return copy.deepcopy(base)

    merged: dict[str, Any] = copy.deepcopy(base)
    for key, value in delta.items():
        if (
            isinstance(value, dict)  # noqa: QGR012 [REASON: Pure state reduction merge utility operates on heterogeneous dynamic state dictionaries]
            and key in merged
            and isinstance(merged[key], dict)  # noqa: QGR012 [REASON: Pure state reduction merge utility operates on heterogeneous dynamic state dictionaries]
        ):
            if "__replace__" in value and value["__replace__"] is True:
                value_copy = copy.deepcopy(value)
                value_copy.pop("__replace__", None)
                merged[key] = value_copy
            else:
                merged[key] = merge_dynamic_inputs(merged[key], value)
        else:
            value_copy = copy.deepcopy(value)
            if isinstance(value_copy, dict):  # noqa: QGR012 [REASON: Pure state reduction merge utility operates on heterogeneous dynamic state dictionaries]
                value_copy.pop("__replace__", None)
            merged[key] = value_copy
    return merged
