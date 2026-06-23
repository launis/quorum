from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.core.hook_registry import HookState
from backend_v2.hooks.linguistics import detect_performative_patterns


@pytest.mark.asyncio
async def test_detect_performative_patterns_prioritizes_user_only():
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
    deps.system_repo = AsyncMock()
    deps.system_repo.get_system_config.return_value = {
        "id": "sys_e0b2a3c4d5e6f7a8",
        "slug": "lexicon",
        "type": "performative_lexicons",
        "lexicon_configs": {
            "en": {
                "language_code": "en",
                "language_name": "English",
                "fuzz_threshold": 90.0,
                "words": ["delve into", "myriad of", "cutting edge", "tapestry"],
            }
        },
    }
    result = await detect_performative_patterns(state, deps)

    assert result.success
    res_dict = result.state_delta["global_context_vars"]["step_linguistics"]
    patterns = res_dict.get("performative_patterns", [])

    # Because user_only is just "normal text.", no performative patterns should be detected
    # even though ai said "delve into", "myriad of", "cutting edge", "tapestry".
    assert len(patterns) == 0
