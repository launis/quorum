"""Tests for the global inputs hydration hook."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookState,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.hooks.hydration import hydrate_global_inputs_hook
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.domain.hydration import HydrationInputSourceDTO
from backend_v2.models.enums import EntityPrefix
from backend_v2.models.execution_core import ExecutionMetadata


def test_hydrate_global_inputs_no_source() -> None:
    """Test hydration hook when no valid input source is present."""
    state = HookState(
        execution_id=generate_opaque_id(EntityPrefix.EXECUTION),
        workflow_id=generate_opaque_id(EntityPrefix.WORKFLOW),
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"existing": "data"}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = MagicMock(spec=HookDependencies)

    result = hydrate_global_inputs_hook(state, deps)

    assert result.success is True
    assert result.state_delta is not None
    assert not result.state_delta.delta


def test_hydrate_global_inputs_empty_updates() -> None:
    """Test hydration hook when input source yields no updates."""
    state = HookState(
        execution_id=generate_opaque_id(EntityPrefix.EXECUTION),
        workflow_id=generate_opaque_id(EntityPrefix.WORKFLOW),
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"existing": "data"}),
        global_context_vars=GlobalContextVarsDTO(hydration_results=HydrationInputSourceDTO(inputs={})),
    )
    deps = MagicMock(spec=HookDependencies)

    result = hydrate_global_inputs_hook(state, deps)

    assert result.success is True
    assert result.state_delta is not None
    assert not result.state_delta.delta


def test_hydrate_global_inputs_success() -> None:
    """Test successful hydration of global inputs preserving existing ExecutionInputsDTO fields."""
    state = HookState(
        execution_id=generate_opaque_id(EntityPrefix.EXECUTION),
        workflow_id=generate_opaque_id(EntityPrefix.WORKFLOW),
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={"existing": "data"},
            user_role="analyst",
            target_locale="en",
        ),
        global_context_vars=GlobalContextVarsDTO(
            hydration_results=HydrationInputSourceDTO(inputs={"new": "data", "existing": "overridden"})
        ),
    )
    deps = MagicMock(spec=HookDependencies)

    result = hydrate_global_inputs_hook(state, deps)

    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.delta == ExecutionInputsDTO(
        raw_inputs={"existing": "overridden", "new": "data"},
        user_role="analyst",
        target_locale="en",
    )


def test_hydrate_global_inputs_none_source() -> None:
    """Test hydration hook handles none hydration_results gracefully."""
    state = HookState(
        execution_id=generate_opaque_id(EntityPrefix.EXECUTION),
        workflow_id=generate_opaque_id(EntityPrefix.WORKFLOW),
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"existing": "data"}),
        global_context_vars=GlobalContextVarsDTO(hydration_results=None),
    )
    deps = MagicMock(spec=HookDependencies)

    result = hydrate_global_inputs_hook(state, deps)

    assert result.success is True
    assert result.state_delta is not None
    assert not result.state_delta.delta


@pytest.mark.parametrize(
    ("execution_id", "workflow_id"),
    [
        ("", generate_opaque_id(EntityPrefix.WORKFLOW)),
        ("   ", generate_opaque_id(EntityPrefix.WORKFLOW)),
        (generate_opaque_id(EntityPrefix.EXECUTION), ""),
        (generate_opaque_id(EntityPrefix.EXECUTION), "   "),
    ],
)
def test_hydrate_global_inputs_missing_identifiers_raises_app_exception(
    execution_id: str,
    workflow_id: str,
) -> None:
    """ISTQB Boundary Value Analysis: Empty or whitespace execution_id/workflow_id raises AppException."""
    state = HookState(
        execution_id=execution_id,
        workflow_id=workflow_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"existing": "data"}),
        global_context_vars=GlobalContextVarsDTO(
            hydration_results=HydrationInputSourceDTO(inputs={"new": "data"}),
        ),
    )
    deps = MagicMock(spec=HookDependencies)

    with pytest.raises(AppException) as exc_info:
        hydrate_global_inputs_hook(state, deps)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.parametrize("invalid_key", ["", "   "])
def test_hydrate_global_inputs_empty_key_raises_app_exception(invalid_key: str) -> None:
    """ISTQB Boundary Value Analysis: Empty or whitespace hydrated input key raises AppException."""
    state = HookState(
        execution_id=generate_opaque_id(EntityPrefix.EXECUTION),
        workflow_id=generate_opaque_id(EntityPrefix.WORKFLOW),
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"existing": "data"}),
        global_context_vars=GlobalContextVarsDTO(
            hydration_results=HydrationInputSourceDTO(inputs={invalid_key: "data"}),
        ),
    )
    deps = MagicMock(spec=HookDependencies)

    with pytest.raises(AppException) as exc_info:
        hydrate_global_inputs_hook(state, deps)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
