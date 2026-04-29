from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import status

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
from backend_v2.exceptions import AppException
from backend_v2.hooks.validation import verify_output_language, verify_structure


@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock()


def test_verify_structure_empty_state(mock_repository: AsyncMock) -> None:
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )
    with pytest.raises(AppException) as exc:
        verify_structure(None, deps)  # type: ignore[arg-type]
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


def test_verify_structure_success(mock_repository: AsyncMock) -> None:
    state = HookState(
        execution_id="sub-123",
        workflow_id="wf-123",
        step_id="step-123",
        task_blueprint="bp-123",
        metadata={},
        global_context_vars={},
        inputs={"data": "This is a sufficiently long string for the validation to pass."},
    )
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )
    res = cast(HookResult, verify_structure(state, deps))
    assert res.success is True


def test_verify_structure_invalid_input(mock_repository: AsyncMock) -> None:
    state = HookState(
        execution_id="sub-123",
        workflow_id="wf-123",
        step_id="step-123",
        task_blueprint="bp-123",
        metadata={},
        global_context_vars={},
        inputs={"data": "short"},  # < 10 chars
    )
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )
    with pytest.raises(AppException) as exc:
        verify_structure(state, deps)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "warnings" in exc.value.details


def test_verify_structure_empty_dict(mock_repository: AsyncMock) -> None:
    state = HookState(
        execution_id="sub-123",
        workflow_id="wf-123",
        step_id="step-123",
        task_blueprint="bp-123",
        metadata={},
        global_context_vars={},
        inputs={},
    )
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )
    with pytest.raises(AppException) as exc:
        verify_structure(state, deps)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "No valid analysis content" in exc.value.message or "No Content Detected" in str(exc.value.details)


def test_verify_output_language_skips_en(mock_repository: AsyncMock) -> None:
    state = HookState(
        execution_id="sub-123",
        workflow_id="wf-123",
        step_id="step-123",
        task_blueprint="bp-123",
        metadata={"target_locale": "en"},
        global_context_vars={},
        inputs={"language": "en", "data": "value"},
    )
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )
    res = cast(HookResult, verify_output_language(state, deps))
    assert res.success is True


def test_verify_output_language_crashes_missing_metadata(mock_repository: AsyncMock) -> None:
    state = HookState(
        execution_id="sub-123",
        workflow_id="wf-123",
        metadata={},
        global_context_vars={},
        inputs={"language": "en", "data": "value"},
    )
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )
    with pytest.raises(AppException) as exc:
        verify_output_language(state, deps)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "target_locale" in exc.value.message


def test_verify_output_language_leaks_english(mock_repository: AsyncMock) -> None:
    state = HookState(
        execution_id="sub-123",
        workflow_id="wf-123",
        step_id="step-123",
        task_blueprint="bp-123",
        metadata={"target_locale": "fi"},
        global_context_vars={},
        inputs={"language": "fi", "evaluation_notes": "This is an english sentence with the and was and from."},
    )
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )
    res = cast(HookResult, verify_output_language(state, deps))
    assert res.success is True
    assert res.state_delta is not None
    assert "_system_warnings" in res.state_delta
    assert len(res.state_delta["_system_warnings"]) == 1
