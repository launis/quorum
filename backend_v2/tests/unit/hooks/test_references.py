"""Unit tests for references hook module."""

from typing import Any, cast

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDeltaDTO,
    HookDependencies,
    HookState,
)
from backend_v2.exceptions import AppException
from backend_v2.hooks.references import generate_bibliography, generate_bibliography_hook
from backend_v2.models.execution_core import ExecutionMetadata


class MockRepository:
    """Mock repository."""


def test_generate_bibliography_success() -> None:
    """Test standard bibliography generation."""
    refs = generate_bibliography("Tämä on tekstiä", {"ref1": "doc1"})
    assert len(refs) == 1
    assert refs[0].source_id.startswith("ref_")


@pytest.mark.asyncio
async def test_generate_bibliography_hook_empty_state() -> None:
    """Test empty state returns empty result."""
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepository()),
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=cast(Any, MockRepository()),
        prompt_block_repo=cast(Any, MockRepository()),
        output_profile_repo=cast(Any, MockRepository()),
        identity_repo=cast(Any, MockRepository()),
        audit_repo=cast(Any, MockRepository()),
        system_repo=cast(Any, MockRepository()),
    )
    result = await generate_bibliography_hook(cast(Any, None), deps)
    assert result.success is True


@pytest.mark.asyncio
async def test_generate_bibliography_hook_success() -> None:
    """Test generate_bibliography_hook with valid inputs and context."""
    state = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        step_id="step_1",
        metadata=ExecutionMetadata(target_locale="fi"),
        inputs=ExecutionInputsDTO(raw_inputs={"text_payload": "Analysis content"}),
        global_context_vars=GlobalContextVarsDTO(vars={"knowledge_base": {"k1": "v1"}}),
    )
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepository()),
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=cast(Any, MockRepository()),
        prompt_block_repo=cast(Any, MockRepository()),
        output_profile_repo=cast(Any, MockRepository()),
        identity_repo=cast(Any, MockRepository()),
        audit_repo=cast(Any, MockRepository()),
        system_repo=cast(Any, MockRepository()),
    )
    result = await generate_bibliography_hook(state, deps)
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta is not None
    assert "bibliography_result" in delta
    assert len(delta["bibliography_result"]["references"]) == 1


@pytest.mark.asyncio
async def test_generate_bibliography_hook_missing_context_vars_raises() -> None:
    """Test that missing global_context_vars raises VALIDATION_FAILED."""
    state = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        step_id="step_1",
        metadata=ExecutionMetadata(target_locale="fi"),
        inputs=ExecutionInputsDTO(raw_inputs={"text_payload": "Analysis"}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    object.__setattr__(state, "global_context_vars", None)
    deps = HookDependencies(
        exec_repo=cast(Any, MockRepository()),
        workflow_repo=cast(Any, MockRepository()),
        comp_repo=cast(Any, MockRepository()),
        prompt_block_repo=cast(Any, MockRepository()),
        output_profile_repo=cast(Any, MockRepository()),
        identity_repo=cast(Any, MockRepository()),
        audit_repo=cast(Any, MockRepository()),
        system_repo=cast(Any, MockRepository()),
    )
    with pytest.raises(AppException) as exc_info:
        await generate_bibliography_hook(state, deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"
