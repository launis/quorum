from unittest.mock import MagicMock, patch

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDeltaDTO,
    HookState,
)
from backend_v2.exceptions import AppException
from backend_v2.hooks.metrics import (
    analyze_text,
    calculate_behavioral_metrics,
    calculate_control_ratio,
    calculate_control_ratio_hook,
    text_metrics,
)
from backend_v2.models.execution_core import ExecutionMetadata


@patch("backend_v2.hooks.metrics.get_settings")
def test_text_metrics_uses_user_only_data(mock_settings: MagicMock) -> None:
    mock_settings.return_value.metrics_short_response_word_count = 5
    mock_settings.return_value.metrics_automation_bias_ratio = 0.5
    mock_settings.return_value.metrics_mechanical_ratio = 0.2

    state = HookState(
        workflow_id="test",
        execution_id="test",
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "chat_log": "**user**: Hello AI!\n\n**ai**: " + " ".join(["word"] * 500),
                "chat_log_user_only": "Hello AI!",
                "chat_log_ai_only": " ".join(["word"] * 500),
            }
        ),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )

    deps = MagicMock()

    result = text_metrics(state, deps)

    assert result.success
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    metrics = delta["profiler_metrics"]

    # Word count should only count "Hello AI!" which is 2 words, not 500+
    assert metrics["word_count"] == 2


def test_analyze_text_empty_and_valid() -> None:
    empty_res = analyze_text("")
    assert empty_res.word_count == 0
    assert empty_res.sentence_count == 0

    valid_res = analyze_text("Hello World! This is a test. How are you?")
    assert valid_res.word_count == 9
    assert valid_res.sentence_count == 3
    assert valid_res.avg_sentence_length == 3.0


def test_calculate_control_ratio_speakers() -> None:
    assert calculate_control_ratio("") == 0.0
    text = "user: Hello there\nai: Hi user\nkäyttäjä: How are you?\ntekoäly: I am fine"
    ratio = calculate_control_ratio(text)
    assert 0.0 < ratio < 1.0


def test_calculate_behavioral_metrics() -> None:
    settings = MagicMock()
    settings.metrics_short_response_word_count = 3
    settings.metrics_automation_bias_ratio = 0.3
    settings.metrics_mechanical_ratio = 0.1

    empty_metrics = calculate_behavioral_metrics("", settings)
    assert empty_metrics.automation_bias == 0.0

    text = "user: ok\nuser: kyllä\nuser: tilaa\nuser: vahvista"
    metrics = calculate_behavioral_metrics(text, settings)
    assert metrics.automation_bias == 1.0
    assert metrics.say_do_gap == 1.0


def test_calculate_control_ratio_hook() -> None:
    state = HookState(
        workflow_id="test",
        execution_id="test",
        inputs=ExecutionInputsDTO(raw_inputs={"input_text": "user: Hello\nai: Bye"}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    deps = MagicMock()
    res = calculate_control_ratio_hook(state, deps)
    assert res.success is True
    assert "input_control_ratio" in res.state_delta.delta


def test_calculate_control_ratio_hook_invalid_payload() -> None:
    inputs = ExecutionInputsDTO(raw_inputs={})
    object.__setattr__(inputs, "raw_inputs", 12345)
    state = HookState(
        workflow_id="test",
        execution_id="test",
        inputs=inputs,
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    deps = MagicMock()
    with pytest.raises(AppException) as exc:
        calculate_control_ratio_hook(state, deps)
    assert exc.value.status_code == 400


def test_text_metrics_empty_input_raises() -> None:
    state = HookState(
        workflow_id="test",
        execution_id="test",
        inputs=ExecutionInputsDTO(raw_inputs={"chat_log": "   "}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    deps = MagicMock()
    with pytest.raises(AppException) as exc:
        text_metrics(state, deps)
    assert exc.value.status_code == 400


def test_text_metrics_invalid_payload_raises() -> None:
    inputs = ExecutionInputsDTO(raw_inputs={})
    object.__setattr__(inputs, "raw_inputs", 12345)
    state = HookState(
        workflow_id="test",
        execution_id="test",
        inputs=inputs,
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    deps = MagicMock()
    with pytest.raises(AppException) as exc:
        text_metrics(state, deps)
    assert exc.value.status_code == 400
