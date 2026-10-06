"""Unit tests for references hook module."""

from __future__ import annotations

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookState,
)
from backend_v2.exceptions import AppException
from backend_v2.hooks.references import generate_bibliography, generate_bibliography_hook
from backend_v2.models.domain.references import BibliographyResultDTO
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@pytest.fixture
def mock_deps() -> HookDependencies:
    """Fixture providing typed HookDependencies backed by in-memory repository."""
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


def test_generate_bibliography_success() -> None:
    """Test standard bibliography generation."""
    refs = generate_bibliography("Tämä on tekstiä", {"ref1": "doc1"})
    assert len(refs) == 1
    assert refs[0].source_id.startswith("ref_")


@pytest.mark.asyncio
async def test_generate_bibliography_hook_empty_state(mock_deps: HookDependencies) -> None:
    """Test empty state returns empty result."""
    result = await generate_bibliography_hook(None, mock_deps)
    assert result.success is True


@pytest.mark.asyncio
async def test_generate_bibliography_hook_success(mock_deps: HookDependencies) -> None:
    """Test generate_bibliography_hook with valid inputs and context."""
    state = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        step_id="step_1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"text_payload": "Analysis content"}),
        global_context_vars=GlobalContextVarsDTO(knowledge_base={"k1": "v1"}),
    )
    result = await generate_bibliography_hook(state, mock_deps)
    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, BibliographyResultDTO)
    assert len(result.state_delta.delta.references) == 1


@pytest.mark.asyncio
async def test_generate_bibliography_hook_missing_context_vars_raises(mock_deps: HookDependencies) -> None:
    """Test that missing global_context_vars raises VALIDATION_FAILED."""
    state = HookState.model_construct(
        execution_id="exec_1",
        workflow_id="wf_1",
        step_id="step_1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"text_payload": "Analysis"}),
        global_context_vars=None,
    )
    with pytest.raises(AppException) as exc_info:
        await generate_bibliography_hook(state, mock_deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"
