from unittest.mock import AsyncMock

import pytest
from fastapi import status

from backend_v2.core.hook_registry import HookDependencies, HookState
from backend_v2.exceptions import AppException
from backend_v2.hooks.synthesis import text_consolidation_hook


@pytest.mark.asyncio
async def test_synthesis_hook_fail_fast_on_missing_step_results() -> None:
    """Fail-fast testing: The hook should crash if step_results is missing."""
    state = HookState.model_construct(
        execution_id="exec_123",
        workflow_id="wf_123",
        step_id="step_123",
        task_blueprint="bp_123",
        metadata={"target_locale": "en"},  # missing step_results
        inputs={"input_1": "some value"},
        global_context_vars={},
    )
    deps = HookDependencies(repository=AsyncMock())

    from collections.abc import Awaitable
    from typing import cast

    from backend_v2.core.hook_registry import HookResult

    with pytest.raises(AppException) as exc:
        await cast(Awaitable[HookResult], text_consolidation_hook(state, deps))

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "missing step_results" in exc.value.message


@pytest.mark.asyncio
async def test_synthesis_hook_fail_fast_on_empty_step_results() -> None:
    """Fail-fast testing: The hook should crash if step_results is explicitly empty."""
    state = HookState.model_construct(
        execution_id="exec_123",
        workflow_id="wf_123",
        step_id="step_123",
        task_blueprint="bp_123",
        metadata={"target_locale": "en", "step_results": {}},  # empty step_results
        inputs={"input_1": "some value"},
        global_context_vars={},
    )
    deps = HookDependencies(repository=AsyncMock())

    from collections.abc import Awaitable
    from typing import cast

    from backend_v2.core.hook_registry import HookResult

    with pytest.raises(AppException) as exc:
        await cast(Awaitable[HookResult], text_consolidation_hook(state, deps))

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "missing step_results" in exc.value.message
