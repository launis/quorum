"""Unit tests for metadata hook module."""

from typing import Any, cast

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookState,
)
from backend_v2.exceptions import AppException
from backend_v2.hooks.metadata import inject_step_metadata
from backend_v2.models.domain.metadata import MetadataHookResultDTO
from backend_v2.models.execution_core import ExecutionMetadata


class MockRepository:
    """Mock repository."""


def test_inject_step_metadata_empty_state() -> None:
    """Test that empty state returns empty result."""
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
    result = inject_step_metadata(cast(Any, None), deps)
    assert result.success is True


def test_inject_step_metadata_success() -> None:
    """Test successful metadata injection."""
    state = HookState(
        execution_id="exec_123",
        workflow_id="wf_456",
        step_id="step_789",
        task_blueprint="bp_step",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(),
        global_context_vars=GlobalContextVarsDTO(initiator_id="user_admin"),
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
    result = inject_step_metadata(state, deps)
    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, MetadataHookResultDTO)
    step_meta = result.state_delta.delta.step_metadata
    assert step_meta.execution_id == "exec_123"
    assert step_meta.step_id == "step_789"
    assert step_meta.initiator_id == "user_admin"
    assert result.state_delta.delta.audit_signature.startswith("step_789:exec_123:")


def test_inject_step_metadata_missing_execution_id_raises() -> None:
    """Test that missing execution_id raises VALIDATION_FAILED."""
    state = HookState(
        execution_id="",
        workflow_id="wf_1",
        step_id="step_1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(),
        global_context_vars=GlobalContextVarsDTO(),
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
    with pytest.raises(AppException) as exc_info:
        inject_step_metadata(state, deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"
