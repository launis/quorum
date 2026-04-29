from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import status

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
from backend_v2.exceptions import AppException
from backend_v2.hooks.security import sanitize_text_hook


@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock()


def test_sanitize_text_hook_fails_fast_on_invalid_inputs(mock_repository: AsyncMock) -> None:
    """Test that missing or non-dict inputs trigger AppException due to strict Pydantic parsing."""
    state = HookState.model_construct(
        execution_id="exe_123",
        workflow_id="wf_123",
        inputs=None,  # type: ignore[arg-type]
        metadata={},
        global_context_vars={},
    )
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )

    with pytest.raises(AppException) as exc_info:
        sanitize_text_hook(state, deps)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Strict Fail-Fast Enforced" in exc_info.value.message


def test_sanitize_text_hook_fails_fast_on_list_inputs(mock_repository: AsyncMock) -> None:
    """Test that list inputs trigger AppException (extra='forbid' via RootModel[dict])."""
    state = HookState.model_construct(
        execution_id="exe_123",
        workflow_id="wf_123",
        inputs=["invalid", "list"],  # type: ignore[arg-type]
        metadata={},
        global_context_vars={},
    )
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )

    with pytest.raises(AppException) as exc_info:
        sanitize_text_hook(state, deps)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Strict Fail-Fast Enforced" in exc_info.value.message


def test_sanitize_text_hook_success(mock_repository: AsyncMock) -> None:
    """Test that valid string inputs are sanitized correctly."""
    state = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        inputs={"test_field": "This is a safe string."},
        metadata={},
        global_context_vars={},
    )
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )

    result = cast(HookResult, sanitize_text_hook(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    assert "sanitization_result" in result.state_delta
    assert result.state_delta["sanitization_result"]["security_status"] == "DATA_CHECKED_AND_SECURED"
    assert "test_field" in result.state_delta["sanitization_result"]["sanitized_inputs"]
