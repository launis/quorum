from typing import cast
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import status

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
from backend_v2.exceptions import AppException
from backend_v2.hooks.reporting import generate_report_hook

valid_execution_data = {
    "id": "exe_123",
    "workflow_id": "wf_123",
    "organization_id": "org_1",
    "status": "running",
    "output_profile_id": "prof_123",
}

valid_workflow_data = {
    "id": "wf_123",
    "slug": "test_workflow",
    "name": {"default_locale": "en", "translations": {"en": "Test"}},
    "description": {"default_locale": "en", "translations": {"en": "Desc"}},
    "status": "draft",
    "version": 1,
    "default_profile_id": "prof_123",
    "expected_inputs": [],
    "steps": [],
}


def test_reporting_hook_fail_fast_on_invalid_inputs() -> None:
    """Fail-fast testing: The hook should crash if state.inputs is missing or invalid."""
    state = HookState.model_construct(
        execution_id=uuid4().hex,
        workflow_id="wf_123",
        step_id="step_123",
        task_blueprint="bp_123",
        metadata={},
        inputs=None,  # type: ignore[arg-type] # Missing
        global_context_vars={},
    )
    mock_exec_repo = AsyncMock()
    mock_workflow_repo = AsyncMock()
    mock_exec_repo.get_execution.return_value = valid_execution_data
    mock_workflow_repo.get_workflow_by_id.return_value = valid_workflow_data
    mock_workflow_repo.get_output_profile_by_id.return_value = {
        "id": "prof_123",
        "slug": "test_profile",
        "workflow_id": "wf_123",
        "name": {"default_locale": "en", "translations": {"en": "Test Profile"}},
        "layouts": [],
        "display_scale": "original",
    }  # noqa: E501
    deps = HookDependencies(
        exec_repo=mock_exec_repo,
        workflow_repo=mock_workflow_repo,
        comp_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )
    # AsyncMock())

    with pytest.raises(AppException) as exc:
        generate_report_hook(state, deps)

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Missing or empty 'inputs' in data." in exc.value.message


def test_reporting_hook_fail_fast_on_invalid_pydantic_schema() -> None:
    """Fail-fast testing: The hook should crash if Pydantic parsing fails."""
    # We pass malformed data that violates the strict schemas defined in GlobalContextVarsDTO
    state = HookState(
        execution_id=uuid4().hex,
        workflow_id="wf_123",
        step_id="step_123",
        task_blueprint="bp_123",
        metadata={},
        inputs={"true_atoms_count": 5},
        global_context_vars={
            "step_xai": {
                # Invalid schema: expecting 'executive_summary' as string, but passing a list
                "executive_summary": ["this", "should", "be", "a", "string"]
            }
        },
    )
    mock_exec_repo = AsyncMock()
    mock_workflow_repo = AsyncMock()
    mock_exec_repo.get_execution.return_value = valid_execution_data
    mock_workflow_repo.get_workflow_by_id.return_value = valid_workflow_data
    mock_workflow_repo.get_output_profile_by_id.return_value = {
        "id": "prof_123",
        "slug": "test_profile",
        "workflow_id": "wf_123",
        "name": {"default_locale": "en", "translations": {"en": "Test Profile"}},
        "layouts": [],
        "display_scale": "original",
    }  # noqa: E501
    deps = HookDependencies(
        exec_repo=mock_exec_repo,
        workflow_repo=mock_workflow_repo,
        comp_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )
    # AsyncMock())

    with pytest.raises(AppException) as exc:
        generate_report_hook(state, deps)

    assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Report Context Validation Failed." in exc.value.message


def test_reporting_hook_success_with_valid_schema() -> None:
    """Test successful validation and parsing using the strict DTO."""
    state = HookState(
        execution_id=uuid4().hex,
        workflow_id="wf_123",
        step_id="step_123",
        task_blueprint="bp_123",
        metadata={},
        inputs={
            "true_atoms_count": 0,
            "false_atoms_count": 0,
            "matrices": {
                "dim1": {
                    "normalized_score": 4.5,
                    "justification": "Very logical.",
                }
            },
        },
        global_context_vars={
            "step_xai": {"executive_summary": "All looks great."},
            "step_judge": {"critical_findings": ["Finding A", "Finding B"]},
        },
    )
    mock_exec_repo = AsyncMock()
    mock_workflow_repo = AsyncMock()
    mock_exec_repo.get_execution.return_value = valid_execution_data
    mock_workflow_repo.get_workflow_by_id.return_value = valid_workflow_data
    mock_workflow_repo.get_output_profile_by_id.return_value = {
        "id": "prof_123",
        "slug": "test_profile",
        "workflow_id": "wf_123",
        "name": {"default_locale": "en", "translations": {"en": "Test Profile"}},
        "layouts": [],
        "display_scale": "original",
    }  # noqa: E501
    deps = HookDependencies(
        exec_repo=mock_exec_repo,
        workflow_repo=mock_workflow_repo,
        comp_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )
    # AsyncMock())

    result = cast(HookResult, generate_report_hook(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    assert "report_context" in result.state_delta
    ctx = result.state_delta["report_context"]
    assert ctx.summary == "All looks great."
    assert ctx.critical_findings == ["Finding A", "Finding B"]
    assert "dim1" in ctx.scores
    assert ctx.scores["dim1"].score == 4.5
