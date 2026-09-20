"""Pure state reduction utilities for orchestrator execution and dynamic inputs merging."""

from __future__ import annotations

import copy

from backend_v2.models.dtos.hook_state import ExecutionInputsDTO

__all__ = ["merge_execution_inputs"]


def merge_execution_inputs(
    base: ExecutionInputsDTO | None,
    delta: ExecutionInputsDTO | None,
) -> ExecutionInputsDTO:
    """Pure immutable merging of ExecutionInputsDTO instances.

    Guarantees:
    1. Base and delta are never mutated in-place (pure function).
    2. raw_inputs and dynamic_inputs dictionaries are non-destructively merged.
    3. delta fields take precedence over base fields.
    4. Returns a newly instantiated, immutable ExecutionInputsDTO.

    Args:
        base: The original base inputs container, or None.
        delta: The inputs container containing updates, or None.

    Returns:
        A new ExecutionInputsDTO representing the merged state.
    """
    if base is None and delta is None:
        return ExecutionInputsDTO()
    if base is None:
        assert delta is not None
        return delta.model_copy()
    if delta is None:
        return base.model_copy()

    merged_raw = copy.deepcopy(dict(base.raw_inputs))
    merged_raw.update(copy.deepcopy(dict(delta.raw_inputs)))

    merged_dynamic = copy.deepcopy(dict(base.dynamic_inputs))
    merged_dynamic.update(copy.deepcopy(dict(delta.dynamic_inputs)))

    target_locale = delta.target_locale if delta.target_locale is not None else base.target_locale
    user_role = delta.user_role if delta.user_role is not None else base.user_role

    return base.model_copy(
        update={
            "raw_inputs": merged_raw,
            "dynamic_inputs": merged_dynamic,
            "target_locale": target_locale,
            "user_role": user_role,
        }
    )
