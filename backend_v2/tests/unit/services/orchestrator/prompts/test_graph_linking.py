from unittest.mock import AsyncMock
from backend_v2.services.orchestrator.prompts.graph_linking import LINKER_SYSTEM_PROMPT, LINKER_USER_PROMPT


def test_prompts_exist() -> None:
    assert isinstance(LINKER_SYSTEM_PROMPT, str)
    assert isinstance(LINKER_USER_PROMPT, str)
    assert len(LINKER_SYSTEM_PROMPT) > 0
    assert len(LINKER_USER_PROMPT) > 0
