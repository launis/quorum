"""Unit tests for metadata hook module."""

from __future__ import annotations

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
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@pytest.fixture
def mock_deps() -> HookDependencies:
    """Fixture providing typed HookDependencies with unified in-memory repository."""
    repo = InMemoryUnifiedWorkflowRepository()
    return HookDependencies(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
    )


def test_inject_step_metadata_empty_state(mock_deps: HookDependencies) -> None:
    """Test that empty state returns empty result."""
    result = inject_step_metadata(None, mock_deps)
    assert result.success is True


def test_inject_step_metadata_success(mock_deps: HookDependencies) -> None:
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
    result = inject_step_metadata(state, mock_deps)
    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, MetadataHookResultDTO)
    step_meta = result.state_delta.delta.step_metadata
    assert step_meta.execution_id == "exec_123"
    assert step_meta.step_id == "step_789"
    assert step_meta.initiator_id == "user_admin"
    assert result.state_delta.delta.audit_signature.startswith("step_789:exec_123:")


def test_inject_step_metadata_missing_execution_id_raises(mock_deps: HookDependencies) -> None:
    """Test that missing execution_id raises VALIDATION_FAILED."""
    state = HookState(
        execution_id="",
        workflow_id="wf_1",
        step_id="step_1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(),
        global_context_vars=GlobalContextVarsDTO(),
    )
    with pytest.raises(AppException) as exc_info:
        inject_step_metadata(state, mock_deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"


@pytest.mark.parametrize("invalid_step_id", [None, "", "   "])
def test_inject_step_metadata_missing_or_blank_step_id_raises(
    mock_deps: HookDependencies, invalid_step_id: str | None
) -> None:
    """Test that missing, empty, or whitespace step_id raises VALIDATION_FAILED."""
    state = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        step_id=invalid_step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(),
        global_context_vars=GlobalContextVarsDTO(),
    )
    with pytest.raises(AppException) as exc_info:
        inject_step_metadata(state, mock_deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"


@pytest.mark.parametrize("invalid_workflow_id", ["", "   "])
def test_inject_step_metadata_missing_or_blank_workflow_id_raises(
    mock_deps: HookDependencies, invalid_workflow_id: str
) -> None:
    """Test that empty or whitespace workflow_id raises VALIDATION_FAILED."""
    state = HookState(
        execution_id="exec_1",
        workflow_id=invalid_workflow_id,
        step_id="step_1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(),
        global_context_vars=GlobalContextVarsDTO(),
    )
    with pytest.raises(AppException) as exc_info:
        inject_step_metadata(state, mock_deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"


def test_inject_step_metadata_default_system_initiator(mock_deps: HookDependencies) -> None:
    """Test that omitted initiator_id defaults to 'system'."""
    state = HookState(
        execution_id="exec_123",
        workflow_id="wf_456",
        step_id="step_789",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(),
        global_context_vars=GlobalContextVarsDTO(initiator_id=None),
    )
    result = inject_step_metadata(state, mock_deps)
    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, MetadataHookResultDTO)
    assert result.state_delta.delta.step_metadata.initiator_id == "system"
