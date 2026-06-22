from unittest.mock import MagicMock

from backend_v2.core.hook_registry import HookState
from backend_v2.hooks.linguistics import detect_performative_patterns


def test_detect_performative_patterns_prioritizes_user_only():
    state = HookState(
        workflow_id="w1",
        execution_id="e1",
        inputs={
            "chat_log": "**user**: normal text.\n\n**ai**: we must delve into the myriad of cutting edge tapestry.",
            "chat_log_user_only": "normal text.",
        },
        global_context_vars={"language": "en"},
        metadata={},
    )

    deps = MagicMock()
    result = detect_performative_patterns(state, deps)

    assert result.success
    res_dict = result.state_delta["linguistics_result"]
    patterns = res_dict.get("performative_patterns", [])

    # Because user_only is just "normal text.", no performative patterns should be detected
    # even though ai said "delve into", "myriad of", "cutting edge", "tapestry".
    assert len(patterns) == 0
