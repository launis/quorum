"""Dictionary utilities for deep merging states.

Enforces safe, non-destructive merging of nested dictionaries, resolving
the issue of shallow merges destroying existing nested keys in Hook Execution states.
"""

import copy
from typing import Any


def deep_merge_dicts(base: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    """Recursively merges the 'update' dictionary into a copy of the 'base' dictionary.

    Ensures that existing nested dictionary keys are maintained alongside new ones,
    instead of being fully overwritten.

    Args:
        base (dict[str, Any]): The original dictionary (remains unmutated).
        update (dict[str, Any]): The dictionary delta containing updates.

    Returns:
        dict[str, Any]: A new deeply merged dictionary.
    """
    merged = copy.deepcopy(base)
    for key, value in update.items():
        if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
            merged[key] = deep_merge_dicts(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged
