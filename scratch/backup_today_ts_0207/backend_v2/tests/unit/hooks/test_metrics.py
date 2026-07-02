from unittest.mock import MagicMock, patch

from backend_v2.core.hook_registry import HookState
from backend_v2.hooks.metrics import text_metrics


@patch("backend_v2.hooks.metrics.get_settings")
def test_text_metrics_uses_user_only_data(mock_settings):
    mock_settings.return_value.metrics_short_response_word_count = 5
    mock_settings.return_value.metrics_automation_bias_ratio = 0.5
    mock_settings.return_value.metrics_mechanical_ratio = 0.2

    state = HookState(
        workflow_id="test",
        execution_id="test",
        inputs={
            "chat_log": "**user**: Hello AI!\n\n**ai**: " + " ".join(["word"] * 500),
            "chat_log_user_only": "Hello AI!",
            "chat_log_ai_only": " ".join(["word"] * 500),
        },
        global_context_vars={},
        metadata={},
    )

    deps = MagicMock()

    result = text_metrics(state, deps)

    assert result.success
    metrics = result.state_delta["profiler_metrics"]

    # Word count should only count "Hello AI!" which is 2 words, not 500+
    assert metrics["word_count"] == 2
