from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookState,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.hooks.metrics import calculate_control_ratio_hook, text_metrics
from backend_v2.models.domain.metrics import ProfilerMetricsDTO
from backend_v2.models.dtos.hook_delta import InputControlRatioResultDTO
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@pytest.fixture
def mock_deps() -> HookDependencies:
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
        search_client=AsyncMock(),
    )


def test_text_metrics_hook_valid_payload(mock_deps: HookDependencies) -> None:
    """Test that text metrics are correctly calculated for valid text inputs."""
    state = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        step_id="step_1",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "history_text": "User: Can you summarize this?\nAI: Yes, I can.",
                "product_text": "This is a product. It has three sentences. Awesome!",
            }
        ),
    )

    result = text_metrics(state, mock_deps)
    assert result.success is True
    assert result.state_delta is not None
    metrics = result.state_delta.delta
    assert isinstance(metrics, ProfilerMetricsDTO)
    assert metrics.word_count > 0
    assert metrics.sentence_count > 0
    assert metrics.control_ratio > 0.0


def test_text_metrics_hook_with_user_only_key(mock_deps: HookDependencies) -> None:
    """Test text metrics when a _user_only input key is provided."""
    state = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        step_id="step_1",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "chat_user_only": "User: This is a direct multiline statement.\nContinuing on next line.\nThird line.",
                "chat": "User: Hello\nAI: Hi there!\nUser: tilaa ja vahvista",
            }
        ),
    )
    result = text_metrics(state, mock_deps)
    assert result.success is True
    assert result.state_delta is not None
    metrics = result.state_delta.delta
    assert isinstance(metrics, ProfilerMetricsDTO)
    assert metrics.automation_bias >= 0.0


def test_control_ratio_multiline_and_empty(mock_deps: HookDependencies) -> None:
    """Test multi-line speaker continuing text and zero total chars in control ratio."""
    state = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        step_id="step_1",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "chat": "User: Start user line\nSecond user line\nAI: Start ai line\nSecond ai line",
            }
        ),
    )
    res = calculate_control_ratio_hook(state, mock_deps)
    assert res.success is True
    assert res.state_delta is not None
    delta1 = res.state_delta.delta
    assert isinstance(delta1, InputControlRatioResultDTO)
    assert delta1.input_control_ratio > 0.0

    state_no_prefix = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        step_id="step_1",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "plain": "AI: Just pure AI text without any user statements",
            }
        ),
    )
    res2 = calculate_control_ratio_hook(state_no_prefix, mock_deps)
    assert res2.success is True
    assert res2.state_delta is not None
    delta2 = res2.state_delta.delta
    assert isinstance(delta2, InputControlRatioResultDTO)
    assert delta2.input_control_ratio == 0.0


@patch("backend_v2.hooks.metrics.analyze_text", side_effect=RuntimeError("Unexpected text processing failure"))
def test_text_metrics_hook_internal_error(mock_analyze: MagicMock, mock_deps: HookDependencies) -> None:
    """Test unexpected internal errors re-raising as 500 AppException."""
    state = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        step_id="step_1",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(raw_inputs={"text": "Some valid content"}),
    )
    with pytest.raises(AppException) as exc:
        text_metrics(state, mock_deps)
    assert exc.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_text_metrics_hook_empty_text_fails(mock_deps: HookDependencies) -> None:
    """Test that empty string inputs trigger a Fail-Fast AppException."""
    state = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        step_id="step_1",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(raw_inputs={"empty_key": "", "none_key": None}),
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
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(raw_inputs={"chat": "User: Hello\nAI: Hi there!"}),
    )

    result = calculate_control_ratio_hook(state, mock_deps)
    assert result.success is True
    assert result.state_delta is not None
    delta = result.state_delta.delta
    assert isinstance(delta, InputControlRatioResultDTO)
    assert delta.input_control_ratio > 0.0


@patch("backend_v2.hooks.metrics.MetricsPayloadDTO.model_validate")
def test_control_ratio_hook_invalid_schema(mock_validate: AsyncMock, mock_deps: HookDependencies) -> None:
    """Mock the DTO validation to force a ValidationError and check Fail-Fast behavior."""
    from pydantic import BaseModel, ValidationError

    class Dummy(BaseModel):
        x: int

    try:
        Dummy.model_validate({"x": "not an int"})
    except ValidationError as e:
        val_error = e

    mock_validate.side_effect = val_error

    state = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        step_id="step_1",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(raw_inputs={"valid": "but mocked to fail"}),
    )

    with pytest.raises(AppException) as exc_info:
        calculate_control_ratio_hook(state, mock_deps)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.details["error_code"] == ErrorCodes.INVALID_JSON_PAYLOAD.value


@patch("backend_v2.hooks.metrics.MetricsPayloadDTO.model_validate")
def test_text_metrics_hook_invalid_schema(mock_validate: AsyncMock, mock_deps: HookDependencies) -> None:
    """Mock the DTO validation to force a ValidationError and check Fail-Fast behavior."""
    from pydantic import BaseModel, ValidationError

    class Dummy(BaseModel):
        x: int

    try:
        Dummy.model_validate({"x": "not an int"})
    except ValidationError as e:
        val_error = e

    mock_validate.side_effect = val_error

    state = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        step_id="step_1",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(raw_inputs={"valid": "but mocked to fail"}),
    )

    with pytest.raises(AppException) as exc_info:
        text_metrics(state, mock_deps)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.details["error_code"] == ErrorCodes.INVALID_JSON_PAYLOAD.value
