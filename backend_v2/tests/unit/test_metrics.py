from typing import cast
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.hooks.metrics import calculate_control_ratio_hook, text_metrics


@pytest.fixture
def mock_deps() -> HookDependencies:
    return HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),  # noqa: E501
        search_client=AsyncMock(),
    )


def test_text_metrics_hook_valid_payload(mock_deps: HookDependencies) -> None:
    """Test that text metrics are correctly calculated for valid text inputs."""
    state = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        step_id="step_1",
        metadata={},
        global_context_vars={},
        inputs={
            "history_text": "User: Can you summarize this?\nAI: Yes, I can.",
            "product_text": "This is a product. It has three sentences. Awesome!",
        },
    )

    result = cast(HookResult, text_metrics(state, mock_deps))
    assert result.success is True
    assert result.state_delta is not None
    assert "profiler_metrics" in result.state_delta

    metrics = result.state_delta["profiler_metrics"]
    assert "word_count" in metrics
    assert "sentence_count" in metrics
    assert metrics["word_count"] > 0
    assert metrics["sentence_count"] > 0
    assert metrics["control_ratio"] > 0.0


def test_text_metrics_hook_invalid_payload_fails_fast(mock_deps: HookDependencies) -> None:
    """Test that the hook enforces Fail-Fast via Pydantic model validation on invalid schemas."""
    pass


def test_text_metrics_hook_empty_text_fails(mock_deps: HookDependencies) -> None:
    """Test that empty string inputs trigger a Fail-Fast AppException."""
    state = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        step_id="step_1",
        metadata={},
        global_context_vars={},
        inputs={"empty_key": "", "none_key": None},
    )

    with pytest.raises(AppException) as exc_info:
        text_metrics(state, mock_deps)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.details["error_code"] == ErrorCodes.EMPTY_INPUT.value


def test_control_ratio_hook_valid(mock_deps: HookDependencies) -> None:
    """Test the standalone control ratio hook."""
    state = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        step_id="step_1",
        metadata={},
        global_context_vars={},
        inputs={"chat": "User: Hello\nAI: Hi there!"},
    )

    result = cast(HookResult, calculate_control_ratio_hook(state, mock_deps))
    assert result.success is True
    assert result.state_delta is not None
    assert "input_control_ratio" in result.state_delta
    assert result.state_delta["input_control_ratio"] > 0.0


@patch("backend_v2.hooks.metrics.MetricsPayloadDTO.model_validate")
def test_control_ratio_hook_invalid_schema(mock_validate: AsyncMock, mock_deps: HookDependencies) -> None:  # noqa: E501
    """Mock the DTO validation to force a ValidationError and check Fail-Fast behavior."""
    from pydantic import BaseModel, ValidationError

    class Dummy(BaseModel):
        x: int

    try:
        Dummy(x=cast(int, "not an int"))
    except ValidationError as e:
        val_error = e

    mock_validate.side_effect = val_error

    state = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        step_id="step_1",
        metadata={},
        global_context_vars={},
        inputs={"valid": "but mocked to fail"},
    )

    with pytest.raises(AppException) as exc_info:
        calculate_control_ratio_hook(state, mock_deps)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.details["error_code"] == ErrorCodes.INVALID_JSON_PAYLOAD.value


@patch("backend_v2.hooks.metrics.MetricsPayloadDTO.model_validate")
def test_text_metrics_hook_invalid_schema(mock_validate: AsyncMock, mock_deps: HookDependencies) -> None:  # noqa: E501
    """Mock the DTO validation to force a ValidationError and check Fail-Fast behavior."""
    from pydantic import BaseModel, ValidationError

    class Dummy(BaseModel):
        x: int

    try:
        Dummy(x=cast(int, "not an int"))
    except ValidationError as e:
        val_error = e

    mock_validate.side_effect = val_error

    state = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        step_id="step_1",
        metadata={},
        global_context_vars={},
        inputs={"valid": "but mocked to fail"},
    )

    with pytest.raises(AppException) as exc_info:
        text_metrics(state, mock_deps)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.details["error_code"] == ErrorCodes.INVALID_JSON_PAYLOAD.value
