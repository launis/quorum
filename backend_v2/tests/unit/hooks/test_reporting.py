from typing import Any, cast
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import status

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
from backend_v2.exceptions import AppException
from backend_v2.hooks.reporting import generate_report_hook


@patch("backend_v2.hooks.reporting.Path.exists", return_value=True)
def test_reporting_hook_fail_fast_on_invalid_inputs(mock_exists: Any) -> None:
    """Fail-fast testing: The hook should crash if state.inputs is missing or invalid."""
    state = HookState.model_construct(
        execution_id=uuid4().hex,
        workflow_id="wf_123",
        step_id="step_123",
        task_blueprint="bp_123",
        metadata={},
        inputs=None,  # Missing
        global_context_vars={},
    )
    deps = HookDependencies(repository=AsyncMock())

    with pytest.raises(AppException) as exc:
        generate_report_hook(state, deps)

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Missing or invalid 'inputs'" in exc.value.message


@patch("backend_v2.hooks.reporting.Path.exists", return_value=True)
def test_reporting_hook_fail_fast_on_invalid_pydantic_schema(mock_exists: Any) -> None:
    """Fail-fast testing: The hook should crash if Pydantic parsing fails."""
    # We pass malformed data that violates the strict schemas defined in GlobalContextVarsDTO
    state = HookState(
        execution_id=uuid4().hex,
        workflow_id="wf_123",
        step_id="step_123",
        task_blueprint="bp_123",
        metadata={},
        inputs={"valid": "input"},
        global_context_vars={
            "step_xai": {
                # Invalid schema: expecting 'executive_summary' as string, but passing a list
                "executive_summary": ["this", "should", "be", "a", "string"]
            }
        },
    )
    deps = HookDependencies(repository=AsyncMock())

    with pytest.raises(AppException) as exc:
        generate_report_hook(state, deps)

    assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Report Context Validation Failed." in exc.value.message


@patch("backend_v2.hooks.reporting.Path.exists", return_value=True)
def test_reporting_hook_success_with_valid_schema(mock_exists: Any) -> None:
    """Test successful validation and parsing using the strict DTO."""
    state = HookState(
        execution_id=uuid4().hex,
        workflow_id="wf_123",
        step_id="step_123",
        task_blueprint="bp_123",
        metadata={},
        inputs={
            "dataset_name": "Test dataset",
            "dim1": {
                "raw_score": 4.5,
                "normalized_score": 4.5,
                "level_breakdown": "",
                "justification": "Very logical.",
                "evaluated_atoms": {},
                "extensions": {}
            }
        },
        global_context_vars={
            "step_xai": {
                "executive_summary": "All looks great."
            },
            "step_judge": {"critical_findings": ["Finding A", "Finding B"]},
        },
    )
    deps = HookDependencies(repository=AsyncMock())

    with patch("backend_v2.hooks.reporting.Path.exists", return_value=True):
        result = cast(HookResult, generate_report_hook(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    assert "report_context" in result.state_delta
    ctx = result.state_delta["report_context"]
    assert ctx["summary"] == "All looks great."
    assert ctx["critical_findings"] == ["Finding A", "Finding B"]
    assert "dim1" in ctx["scores"]
    assert ctx["scores"]["dim1"]["score"] == 4.5
