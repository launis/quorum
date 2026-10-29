"""Unit tests for references hook module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookState,
)
from backend_v2.exceptions import AppException, ErrorCodes
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
    refs = generate_bibliography("Sample analytical text", {"ref1": "doc1"})
    assert len(refs) == 1
    assert refs[0].source_id.startswith("ref_")


def test_generate_bibliography_reraises_app_exception() -> None:
    """Test that generate_bibliography re-raises AppException directly without wrapping."""
    expected_exc = AppException(
        message="Upstream failure",
        status_code=422,
        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
    )
    with (
        patch("backend_v2.hooks.references.uuid.uuid4", side_effect=expected_exc),
        pytest.raises(AppException) as exc_info,
    ):
        generate_bibliography("Sample text", None)

    assert exc_info.value is expected_exc


def test_generate_bibliography_generic_error_raises_citation_parsing_failed() -> None:
    """Test that unexpected errors in generate_bibliography raise CITATION_PARSING_FAILED."""
    with (
        patch("backend_v2.hooks.references.uuid.uuid4", side_effect=RuntimeError("UUID generation failure")),
        pytest.raises(AppException) as exc_info,
    ):
        generate_bibliography("Sample text", None)

    assert exc_info.value.status_code == 500
    assert exc_info.value.error_code == ErrorCodes.CITATION_PARSING_FAILED.value


@pytest.mark.asyncio
async def test_generate_bibliography_hook_empty_state(mock_deps: HookDependencies) -> None:
    """Test empty state returns empty result."""
    result = await generate_bibliography_hook(None, mock_deps)
    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.delta is None


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
async def test_generate_bibliography_hook_with_step_coach_only(mock_deps: HookDependencies) -> None:
    """Test generate_bibliography_hook when text_dump is populated from step_coach."""
    state = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        step_id="step_1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(step_coach={"coach_note": "Actionable insight"}),
    )
    result = await generate_bibliography_hook(state, mock_deps)
    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, BibliographyResultDTO)
    assert len(result.state_delta.delta.references) == 1


@pytest.mark.asyncio
async def test_generate_bibliography_hook_empty_text_short_circuits(mock_deps: HookDependencies) -> None:
    """Test boundary condition where empty/whitespace text_dump short-circuits cleanly."""
    state = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        step_id="step_1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"text_payload": "   ", "empty_val": ""}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    result = await generate_bibliography_hook(state, mock_deps)
    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.delta is None


@pytest.mark.asyncio
async def test_generate_bibliography_hook_invalid_inputs_raises(mock_deps: HookDependencies) -> None:
    """Test negative partition where invalid raw_inputs schema raises INVALID_JSON_PAYLOAD."""
    mock_inputs = MagicMock()
    mock_inputs.raw_inputs = 12345
    state = HookState.model_construct(
        execution_id="exec_1",
        workflow_id="wf_1",
        step_id="step_1",
        metadata=ExecutionMetadata(),
        inputs=mock_inputs,
        global_context_vars=GlobalContextVarsDTO(),
    )
    with pytest.raises(AppException) as exc_info:
        await generate_bibliography_hook(state, mock_deps)

    assert exc_info.value.status_code == 400
    assert exc_info.value.error_code == ErrorCodes.INVALID_JSON_PAYLOAD.value


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

    assert exc_info.value.status_code == 500
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_generate_bibliography_hook_unexpected_error_raises(mock_deps: HookDependencies) -> None:
    """Test that unexpected non-AppException errors in hook wrapper raise HOOK_EXECUTION_FAILED."""
    state = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        step_id="step_1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"text_payload": "Analysis"}),
        global_context_vars=GlobalContextVarsDTO(),
    )
    with (
        patch("backend_v2.hooks.references.generate_bibliography", side_effect=RuntimeError("Unexpected crash")),
        pytest.raises(AppException) as exc_info,
    ):
        await generate_bibliography_hook(state, mock_deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.error_code == ErrorCodes.HOOK_EXECUTION_FAILED.value
