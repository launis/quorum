"""Unit tests for bibliography reference generation hooks."""

from __future__ import annotations

from collections.abc import Awaitable
from typing import cast
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDeltaDTO,
    HookDependencies,
    HookResult,
    HookState,
)
from backend_v2.exceptions import AppException
from backend_v2.hooks.references import generate_bibliography, generate_bibliography_hook
from backend_v2.models.domain.references import BibliographyResultDTO
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@pytest.mark.asyncio
async def test_generate_bibliography_hook_success() -> None:
    """Test that bibliography generation returns strictly typed BibliographyResultDTO."""
    state = HookState(
        execution_id="123",
        workflow_id="wf1",
        step_id="step1",
        inputs=ExecutionInputsDTO(
            raw_inputs={"text": "This is a dummy text for testing citations."},
            dynamic_inputs={},
        ),
        global_context_vars=GlobalContextVarsDTO(knowledge_base={"concepts": []}),
        metadata=ExecutionMetadata(),
    )

    repo = InMemoryUnifiedWorkflowRepository()
    deps = HookDependencies(
        exec_repo=repo,
        workflow_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
    )

    result = await cast(Awaitable[HookResult], generate_bibliography_hook(state, deps))

    assert result.success is True
    assert isinstance(result.state_delta, HookDeltaDTO)
    assert isinstance(result.state_delta.delta, BibliographyResultDTO)
    refs = result.state_delta.delta.references

    assert len(refs) == 1
    assert refs[0].source_id.startswith("ref_")
    assert refs[0].url is not None


@pytest.mark.asyncio
async def test_generate_bibliography_hook_none_state() -> None:
    """Verify generate_bibliography_hook returns empty delta when state is None."""
    deps = MagicMock(spec=HookDependencies)
    result = await cast(Awaitable[HookResult], generate_bibliography_hook(None, deps))
    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.delta is None


@pytest.mark.asyncio
async def test_generate_bibliography_hook_invalid_inputs_raises() -> None:
    """Verify generate_bibliography_hook raises 400 AppException when raw_inputs is not a mapping."""
    mock_inputs = MagicMock()
    mock_inputs.raw_inputs = 12345
    state = HookState(
        execution_id="123",
        workflow_id="wf1",
        inputs=ExecutionInputsDTO(raw_inputs={}, dynamic_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    ).model_copy(update={"inputs": mock_inputs})
    deps = MagicMock(spec=HookDependencies)

    with pytest.raises(AppException) as exc:
        await cast(Awaitable[HookResult], generate_bibliography_hook(state, deps))
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_generate_bibliography_hook_none_gvars_raises() -> None:
    """Verify generate_bibliography_hook raises 500 AppException when global_context_vars is None."""
    state = HookState(
        execution_id="123",
        workflow_id="wf1",
        inputs=ExecutionInputsDTO(raw_inputs={"text": "Hello"}, dynamic_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    ).model_copy(update={"global_context_vars": None})
    deps = MagicMock(spec=HookDependencies)

    with pytest.raises(AppException) as exc:
        await cast(Awaitable[HookResult], generate_bibliography_hook(state, deps))
    assert exc.value.status_code == 500


@pytest.mark.asyncio
async def test_generate_bibliography_hook_invalid_context_raises() -> None:
    """Verify invalid knowledge_base payload raises ValidationError or AppException."""
    deps = MagicMock(spec=HookDependencies)
    with pytest.raises((AppException, ValidationError)):
        state = HookState(
            execution_id="123",
            workflow_id="wf1",
            inputs=ExecutionInputsDTO(raw_inputs={"text": "Hello"}, dynamic_inputs={}),
            global_context_vars=GlobalContextVarsDTO.model_validate({"knowledge_base": "not_a_dict"}),
            metadata=ExecutionMetadata(),
        )
        await cast(Awaitable[HookResult], generate_bibliography_hook(state, deps))


@pytest.mark.asyncio
async def test_generate_bibliography_hook_empty_text_short_circuit() -> None:
    """Verify empty text input short-circuits without generating references."""
    state = HookState(
        execution_id="123",
        workflow_id="wf1",
        inputs=ExecutionInputsDTO(raw_inputs={"text": ""}, dynamic_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    deps = MagicMock(spec=HookDependencies)

    result = await cast(Awaitable[HookResult], generate_bibliography_hook(state, deps))
    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.delta is None


@pytest.mark.asyncio
async def test_generate_bibliography_hook_with_step_coach_and_no_kb_in_gvars() -> None:
    """Verify bibliography generation extracts text from step_coach context when raw_inputs is empty."""
    state = HookState(
        execution_id="123",
        workflow_id="wf1",
        inputs=ExecutionInputsDTO(raw_inputs={}, dynamic_inputs={}),
        global_context_vars=GlobalContextVarsDTO(step_coach={"coach_note": "Great"}),
        metadata=ExecutionMetadata(),
    )
    deps = MagicMock(spec=HookDependencies)

    result = await cast(Awaitable[HookResult], generate_bibliography_hook(state, deps))
    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, BibliographyResultDTO)
    assert len(result.state_delta.delta.references) > 0


def test_generate_bibliography_generic_error_raises() -> None:
    """Verify unexpected error inside generate_bibliography translates to 500 AppException."""
    with (
        patch("backend_v2.hooks.references.generate_uuid7", side_effect=RuntimeError("UUID generation failure")),
        pytest.raises(AppException) as exc,
    ):
        generate_bibliography("sample text", None)
    assert exc.value.status_code == 500


@pytest.mark.asyncio
async def test_generate_bibliography_hook_unexpected_error_raises() -> None:
    """Verify unexpected error inside generate_bibliography_hook translates to 500 AppException."""
    state = HookState(
        execution_id="123",
        workflow_id="wf1",
        inputs=ExecutionInputsDTO(raw_inputs={"text": "Valid text"}, dynamic_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    deps = MagicMock(spec=HookDependencies)

    with (
        patch("backend_v2.hooks.references.generate_bibliography", side_effect=RuntimeError("Unexpected error")),
        pytest.raises(AppException) as exc,
    ):
        await cast(Awaitable[HookResult], generate_bibliography_hook(state, deps))
    assert exc.value.status_code == 500
