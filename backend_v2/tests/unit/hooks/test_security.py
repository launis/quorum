"""Unit tests for security hook module."""

from typing import Any, cast
from unittest.mock import MagicMock

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookState,
)
from backend_v2.exceptions import AppException
from backend_v2.hooks.security import sanitize_text_hook
from backend_v2.models.domain.security import SanitizationResultDTO
from backend_v2.models.execution_core import ExecutionMetadata


class MockRepository:
    """Mock repository."""


def test_sanitize_text_hook_missing_state_raises() -> None:
    """Test that missing state raises VALIDATION_FAILED."""
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
        sanitize_text_hook(cast(Any, None), deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"


def test_sanitize_text_hook_success_no_pii() -> None:
    """Test standard execution with clean input."""
    state = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        step_id="step_1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"reflection_text": "Tämä on puhdas analyysi."}),
        global_context_vars=GlobalContextVarsDTO(language="fi"),
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

    result = sanitize_text_hook(state, deps)
    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, SanitizationResultDTO)
    assert result.state_delta.delta.threat_detected is False
    assert result.state_delta.delta.sanitized_inputs["reflection_text"] == "Tämä on puhdas analyysi."


def test_sanitize_text_hook_redacts_pii(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that detected PII is redacted and threat_detected is set to True."""
    mock_pii = MagicMock()
    mock_pii.mask_pii.return_value = "Matti [REDACTED]"
    monkeypatch.setattr("backend_v2.hooks.security.get_pii_service", lambda: mock_pii)

    state = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        step_id="step_1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"reflection_text": "Matti Meikäläinen 010190-123A"}),
        global_context_vars=GlobalContextVarsDTO(language="fi"),
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

    result = sanitize_text_hook(state, deps)
    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, SanitizationResultDTO)
    assert result.state_delta.delta.threat_detected is True
    assert result.state_delta.delta.sanitized_inputs["reflection_text"] == "Matti [REDACTED]"


def test_sanitize_text_hook_invalid_language_payload_raises() -> None:
    """Test that invalid language format raises VALIDATION_FAILED."""
    state = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        step_id="step_1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"reflection_text": "test"}),
        global_context_vars=GlobalContextVarsDTO.model_construct(language={"invalid": 123}),  # type: ignore[arg-type]
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
        sanitize_text_hook(state, deps)

    assert exc_info.value.error_code == "VALIDATION_FAILED"


def test_sanitize_text_hook_mask_pii_exception_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that exception during mask_pii raises SECURITY_SCAN_FAILED."""
    mock_pii = MagicMock()
    mock_pii.mask_pii.side_effect = RuntimeError("PII Scanner crash")
    monkeypatch.setattr("backend_v2.hooks.security.get_pii_service", lambda: mock_pii)

    state = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        step_id="step_1",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"reflection_text": "Tekstiä"}),
        global_context_vars=GlobalContextVarsDTO(language="fi"),
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
        sanitize_text_hook(state, deps)

    assert exc_info.value.error_code == "SECURITY_SCAN_FAILED"
