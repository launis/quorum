"""Tests for the global inputs hydration hook."""

from typing import cast
from unittest.mock import MagicMock

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookResult,
    HookState,
)
from backend_v2.hooks.hydration import hydrate_global_inputs_hook
from backend_v2.models.domain.hydration import HydrationInputSourceDTO
from backend_v2.models.execution_core import ExecutionMetadata


def test_hydrate_global_inputs_no_source() -> None:
    """Test hydration hook when no valid input source is present."""
    state = HookState(
        execution_id="exe_123",
        workflow_id="wor_456",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"existing": "data"}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = MagicMock(spec=HookDependencies)

    result = cast(HookResult, hydrate_global_inputs_hook(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    assert not result.state_delta.delta


def test_hydrate_global_inputs_empty_updates() -> None:
    """Test hydration hook when input source yields no updates."""
    state = HookState(
        execution_id="exe_123",
        workflow_id="wor_456",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"existing": "data"}),
        global_context_vars=GlobalContextVarsDTO(
            hydration_results=HydrationInputSourceDTO(inputs={})
        ),
    )
    deps = MagicMock(spec=HookDependencies)

    result = cast(HookResult, hydrate_global_inputs_hook(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    assert not result.state_delta.delta


def test_hydrate_global_inputs_success() -> None:
    """Test successful hydration of global inputs."""
    state = HookState(
        execution_id="exe_123",
        workflow_id="wor_456",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"existing": "data"}),
        global_context_vars=GlobalContextVarsDTO(
            hydration_results=HydrationInputSourceDTO(inputs={"new": "data", "existing": "overridden"})
        ),
    )
    deps = MagicMock(spec=HookDependencies)

    result = cast(HookResult, hydrate_global_inputs_hook(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.delta == {"inputs": {"existing": "overridden", "new": "data"}}


def test_hydrate_global_inputs_none_source() -> None:
    """Test hydration hook handles none hydration_results gracefully."""
    state = HookState(
        execution_id="exe_123",
        workflow_id="wor_456",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"existing": "data"}),
        global_context_vars=GlobalContextVarsDTO(hydration_results=None),
    )
    deps = MagicMock(spec=HookDependencies)

    result = cast(HookResult, hydrate_global_inputs_hook(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    assert not result.state_delta.delta
