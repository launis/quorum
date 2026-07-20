"""Dictionary utilities for deep merging states.

Enforces safe, non-destructive merging of nested dictionaries, resolving
the issue of shallow merges destroying existing nested keys in Hook Execution states.
"""

import copy
from typing import Any

from backend_v2.exceptions import MissingInputMappingError


def deep_merge_dicts(base: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    """Recursively merges the 'update' dictionary into a copy of the 'base' dictionary.

    Ensures that existing nested dictionary keys are maintained alongside new ones,
    instead of being fully overwritten.

    Args:
        base: The original dictionary (remains unmutated).
        update: The dictionary delta containing updates.

    Returns:
        A new deeply merged dictionary.
    """
    merged = copy.deepcopy(base)
    for key, value in update.items():
        if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
            if "__replace__" in value and value["__replace__"] is True:
                value_copy = copy.deepcopy(value)
                value_copy.pop("__replace__", None)
                merged[key] = value_copy
            else:
                merged[key] = deep_merge_dicts(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def resolve_dot_notation(state: Any, path: str) -> Any:
    """Safely resolves a dot-notation path against a state dictionary or object.

    Uses strictly iterative lookup. Never uses eval, exec, dict.get, or hasattr.
    Raises MissingInputMappingError on any resolution failure.

    Args:
        state: The object or dictionary to traverse.
        path: Dot-separated string path (e.g. 'user.profile.age').

    Returns:
        The resolved value.

    Raises:
        MissingInputMappingError: If the path cannot be resolved.
    """
    if not path:
        return state

    parts = path.split(".")
    curr = state

    for _i, part in enumerate(parts):
        try:
            if isinstance(curr, dict):
                curr = curr[part]
            elif isinstance(curr, list):
                curr = curr[int(part)]
            else:
                curr = getattr(curr, part)
        except (KeyError, AttributeError, IndexError, ValueError) as e:
            raise MissingInputMappingError(
                path=path, state_type=type(curr).__name__, reason=f"Failed at '{part}': {type(e).__name__}"
            ) from e

    return curr
