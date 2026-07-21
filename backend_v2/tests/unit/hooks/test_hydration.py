from unittest.mock import AsyncMock
"""Tests for the global inputs hydration hook."""

from typing import cast
from unittest.mock import MagicMock

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
from backend_v2.hooks.hydration import hydrate_global_inputs_hook


def test_hydrate_global_inputs_no_source() -> None:
    """Test hydration hook when no valid input source is present."""
    state = HookState(
        execution_id="exe_123",
        workflow_id="wor_456",
        metadata={},
        inputs={"existing": "data"},
        global_context_vars={"random_var": {"not_a": "source"}},
    )
    deps = MagicMock(spec=HookDependencies)

    result = cast(HookResult, hydrate_global_inputs_hook(state, deps))

    assert result.success is True
    assert result.state_delta == {}


def test_hydrate_global_inputs_empty_updates() -> None:
    """Test hydration hook when input source yields no updates."""
    state = HookState(
        execution_id="exe_123",
        workflow_id="wor_456",
        metadata={},
        inputs={"existing": "data"},
        global_context_vars={"valid_var": {"inputs": {}}},
    )
    deps = MagicMock(spec=HookDependencies)

    result = cast(HookResult, hydrate_global_inputs_hook(state, deps))

    assert result.success is True
    assert result.state_delta == {}


def test_hydrate_global_inputs_success() -> None:
    """Test successful hydration of global inputs."""
    state = HookState(
        execution_id="exe_123",
        workflow_id="wor_456",
        metadata={},
        inputs={"existing": "data"},
        global_context_vars={"valid_var": {"inputs": {"new": "data", "existing": "overridden"}}},
    )
    deps = MagicMock(spec=HookDependencies)

    result = cast(HookResult, hydrate_global_inputs_hook(state, deps))

    assert result.success is True
    assert result.state_delta == {"inputs": {"existing": "overridden", "new": "data"}}


def test_hydrate_global_inputs_ignores_non_dict() -> None:
    """Test hydration hook ignores non-dict items in global_context_vars."""
    state = HookState(
        execution_id="exe_123",
        workflow_id="wor_456",
        metadata={},
        inputs={"existing": "data"},
        global_context_vars={"string_var": "I am not a dict"},
    )
    deps = MagicMock(spec=HookDependencies)

    result = cast(HookResult, hydrate_global_inputs_hook(state, deps))

    assert result.success is True
    assert result.state_delta == {}
