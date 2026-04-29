from unittest.mock import MagicMock

import pytest

from backend_v2.core.hook_registry import HookDependencies, HookState
from backend_v2.hooks.references import generate_bibliography_hook


@pytest.mark.asyncio
async def test_generate_bibliography_hook_success() -> None:
    """Test that bibliography generation returns strictly typed Pydantic dicts."""
    state = HookState(
        execution_id="123",
        workflow_id="wf1",
        step_id="step1",
        inputs={"text": "This is a dummy text for testing citations."},
        global_context_vars={"knowledge_base": {"concepts": []}},
        metadata={},
    )

    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )

    from collections.abc import Awaitable
    from typing import cast

    from backend_v2.core.hook_registry import HookResult

    result = await cast(Awaitable[HookResult], generate_bibliography_hook(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    assert "bibliography_result" in result.state_delta
    refs = result.state_delta["bibliography_result"]["references"]

    assert len(refs) == 1
    assert refs[0]["source_id"].startswith("ref_")
    assert "url" in refs[0]
