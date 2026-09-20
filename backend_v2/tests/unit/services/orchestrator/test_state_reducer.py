"""Unit tests for state_reducer.py following ISTQB Equivalence Partitions."""

from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.services.orchestrator.state_reducer import merge_execution_inputs


def test_merge_execution_inputs_with_none_inputs() -> None:
    """ISTQB Partition 1: None inputs handling."""
    assert merge_execution_inputs(None, None) == ExecutionInputsDTO()

    base = ExecutionInputsDTO(raw_inputs={"a": "1"})
    assert merge_execution_inputs(base, None) == base

    delta = ExecutionInputsDTO(raw_inputs={"b": "2"})
    assert merge_execution_inputs(None, delta) == delta


def test_merge_execution_inputs_pure_immutability() -> None:
    """ISTQB Partition 2: Verifies base and delta are never mutated in-place."""
    base = ExecutionInputsDTO(
        raw_inputs={"text": "orig", "count": 1},
        dynamic_inputs={"score": 10.0},
        target_locale="en",
    )
    delta = ExecutionInputsDTO(
        raw_inputs={"extra": "new"},
        dynamic_inputs={"score": 20.0, "step1": "done"},
        target_locale="fi",
    )

    merged = merge_execution_inputs(base, delta)

    # Merged has combined state
    assert merged.raw_inputs == {"text": "orig", "count": 1, "extra": "new"}
    assert merged.dynamic_inputs == {"score": 20.0, "step1": "done"}
    assert merged.target_locale == "fi"

    # Base is unchanged
    assert base.raw_inputs == {"text": "orig", "count": 1}
    assert base.dynamic_inputs == {"score": 10.0}
    assert base.target_locale == "en"

    # Delta is unchanged
    assert delta.raw_inputs == {"extra": "new"}
    assert delta.dynamic_inputs == {"score": 20.0, "step1": "done"}
    assert delta.target_locale == "fi"


def test_merge_execution_inputs_overwrites_and_locale() -> None:
    """ISTQB Partition 3: Delta takes precedence over base fields."""
    base = ExecutionInputsDTO(
        raw_inputs={"doc": "base_doc"},
        dynamic_inputs={"val": "base_val"},
        user_role="analyst",
        target_locale="en",
    )
    delta = ExecutionInputsDTO(
        raw_inputs={"doc": "delta_doc"},
        dynamic_inputs={"val": "delta_val"},
        user_role="admin",
        target_locale=None,
    )

    merged = merge_execution_inputs(base, delta)

    assert merged.raw_inputs["doc"] == "delta_doc"
    assert merged.dynamic_inputs["val"] == "delta_val"
    assert merged.user_role == "admin"
    # When delta target_locale is None, base target_locale is preserved
    assert merged.target_locale == "en"
