from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDeltaDTO,
    HookDependencies,
    HookState,
)
from backend_v2.hooks.references import generate_bibliography_hook
from backend_v2.models.execution_core import ExecutionMetadata


@pytest.mark.asyncio
async def test_generate_bibliography_hook_success() -> None:
    """Test that bibliography generation returns strictly typed Pydantic dicts."""
    state = HookState(
        execution_id="123",
        workflow_id="wf1",
        step_id="step1",
        inputs=ExecutionInputsDTO(raw_inputs={"text": "This is a dummy text for testing citations."}),
        global_context_vars=GlobalContextVarsDTO(vars={"knowledge_base": {"concepts": []}}),
        metadata=ExecutionMetadata(target_locale="fi"),
    )

    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )

    from collections.abc import Awaitable
    from typing import cast

    from backend_v2.core.hook_registry import HookResult

    result = await cast(Awaitable[HookResult], generate_bibliography_hook(state, deps))

    assert result.success is True
    assert isinstance(result.state_delta, HookDeltaDTO)
    assert "bibliography_result" in result.state_delta.delta
    refs = result.state_delta.delta["bibliography_result"]["references"]

    assert len(refs) == 1
    assert refs[0]["source_id"].startswith("ref_")
    assert "url" in refs[0]
