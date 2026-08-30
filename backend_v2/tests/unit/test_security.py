from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
from backend_v2.exceptions import AppException
from backend_v2.hooks.security import sanitize_text_hook
from backend_v2.models.execution_core import ExecutionMetadata


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
        global_context_vars={"language": "fi"},
    )
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
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
        global_context_vars={"language": "fi"},
    )
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )

    with pytest.raises(AppException) as exc_info:
        sanitize_text_hook(state, deps)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Strict Fail-Fast Enforced" in exc_info.value.message


@patch("backend_v2.hooks.security.get_pii_service")
def test_sanitize_text_hook_success(mock_get_pii_service: MagicMock, mock_repository: AsyncMock) -> None:
    """Test that valid string inputs are sanitized correctly."""
    mock_service = MagicMock()
    mock_service.mask_pii.return_value = "This is a safe string."
    mock_get_pii_service.return_value = mock_service

    state = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        inputs={"test_field": "This is a safe string."},
        metadata=ExecutionMetadata(target_locale="fi"),
        global_context_vars={"language": "fi"},
    )
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
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


@patch("backend_v2.hooks.security.get_pii_service")
def test_sanitize_text_hook_skips_non_strings(mock_get_pii_service: MagicMock, mock_repository: AsyncMock) -> None:
    """Test that non-string values like dicts or lists in inputs are ignored."""
    mock_service = MagicMock()
    mock_service.mask_pii.return_value = "This is a safe string."
    mock_get_pii_service.return_value = mock_service

    state = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        inputs={
            "string_field": "This is a safe string.",
            "dict_field": {"some": "data"},
            "list_field": ["some", "data"],
        },
        metadata=ExecutionMetadata(target_locale="fi"),
        global_context_vars={"language": "fi"},
    )
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )

    result = cast(HookResult, sanitize_text_hook(state, deps))

    assert result.success is True
    # mask_pii should only be called once, for the string field.
    assert mock_service.mask_pii.call_count == 1
    assert "string_field" in result.state_delta["sanitization_result"]["sanitized_inputs"]
    assert "dict_field" not in result.state_delta["sanitization_result"]["sanitized_inputs"]
    assert "list_field" not in result.state_delta["sanitization_result"]["sanitized_inputs"]


@patch("backend_v2.hooks.security.get_pii_service")
def test_sanitize_text_hook_resolves_language_from_execution_metadata(
    mock_get_pii_service: MagicMock, mock_repository: AsyncMock
) -> None:
    """Regression test: sanitize_text_hook must resolve language from metadata.target_locale when global_context_vars is empty."""
    mock_service = MagicMock()
    mock_service.mask_pii.return_value = "Puhdistettu teksti."
    mock_get_pii_service.return_value = mock_service

    state = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        inputs={"text": "Sensitiivinen teksti."},
        metadata=ExecutionMetadata(target_locale="fi"),
        global_context_vars={},
    )
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )

    result = cast(HookResult, sanitize_text_hook(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    assert "sanitization_result" in result.state_delta


def test_sanitize_text_hook_fails_fast_on_missing_state() -> None:
    """Test that None state raises AppException(500)."""
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )
    with pytest.raises(AppException) as exc_info:
        sanitize_text_hook(cast(HookState, None), deps)
    assert exc_info.value.status_code == 500


def test_sanitize_text_hook_fails_fast_on_invalid_language() -> None:
    """Test that invalid language payload raises AppException(400)."""
    state = HookState.model_construct(
        execution_id="exe_123",
        workflow_id="wf_123",
        inputs={"text": "Hello"},
        metadata=None,
        global_context_vars={},
    )
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )
    with pytest.raises(AppException) as exc_info:
        sanitize_text_hook(state, deps)
    assert exc_info.value.status_code == 400


@patch("backend_v2.hooks.security.get_pii_service")
def test_sanitize_text_hook_detects_threats(mock_get_pii_service: MagicMock) -> None:
    """Test that PII redaction adds threats to summary and flags threat_detected."""
    mock_service = MagicMock()
    mock_service.mask_pii.return_value = "[REDACTED]"
    mock_get_pii_service.return_value = mock_service

    state = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        inputs={"name": "John Doe"},
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars={},
    )
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )

    result = cast(HookResult, sanitize_text_hook(state, deps))
    assert result.success is True
    assert result.state_delta is not None
    res = result.state_delta["sanitization_result"]
    assert res["threat_detected"] is True
    assert res["sanitized_inputs"]["name"] == "[REDACTED]"


@patch("backend_v2.hooks.security.get_pii_service")
def test_sanitize_text_hook_mask_pii_failure(mock_get_pii_service: MagicMock) -> None:
    """Test that failure in mask_pii raises AppException(500, SECURITY_SCAN_FAILED)."""
    mock_service = MagicMock()
    mock_service.mask_pii.side_effect = RuntimeError("PII service crashed")
    mock_get_pii_service.return_value = mock_service

    state = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        inputs={"text": "Sensitive data"},
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars={},
    )
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )

    with pytest.raises(AppException) as exc_info:
        sanitize_text_hook(state, deps)
    assert exc_info.value.status_code == 500


@patch("backend_v2.hooks.security.SanitizationResultDTO")
@patch("backend_v2.hooks.security.get_pii_service")
def test_sanitize_text_hook_dto_creation_failure(mock_get_pii_service: MagicMock, mock_dto_cls: MagicMock) -> None:
    """Test that failure in SanitizationResultDTO raises AppException(500, SECURITY_CONFIG_ERROR)."""
    mock_service = MagicMock()
    mock_service.mask_pii.return_value = "safe"
    mock_get_pii_service.return_value = mock_service
    mock_dto_cls.side_effect = RuntimeError("DTO validation explosion")

    state = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        inputs={"text": "safe"},
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars={},
    )
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )

    with pytest.raises(AppException) as exc_info:
        sanitize_text_hook(state, deps)
    assert exc_info.value.status_code == 500
