from unittest.mock import AsyncMock
from backend_v2.services.orchestrator.prompts.atom_extraction import PHASE_0_SYSTEM_PROMPT, PHASE_1_SYSTEM_PROMPT


def test_prompts_exist() -> None:
    assert isinstance(PHASE_0_SYSTEM_PROMPT, str)
    assert isinstance(PHASE_1_SYSTEM_PROMPT, str)
    assert len(PHASE_0_SYSTEM_PROMPT) > 0
    assert len(PHASE_1_SYSTEM_PROMPT) > 0
