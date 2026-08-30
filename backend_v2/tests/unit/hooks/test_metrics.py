from unittest.mock import MagicMock, patch

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDeltaDTO,
    HookState,
)
from backend_v2.hooks.metrics import text_metrics
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
        metadata=ExecutionMetadata(target_locale="fi"),
    )

    deps = MagicMock()

    result = text_metrics(state, deps)

    assert result.success
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    metrics = delta["profiler_metrics"]

    # Word count should only count "Hello AI!" which is 2 words, not 500+
    assert metrics["word_count"] == 2
