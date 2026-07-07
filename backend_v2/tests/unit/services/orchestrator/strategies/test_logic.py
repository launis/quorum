import asyncio
from unittest.mock import AsyncMock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.state import StateProjector
from backend_v2.models.v2_core import StepRule
from backend_v2.services.orchestrator.strategies.base import StrategyContext
from backend_v2.services.orchestrator.strategies.logic import LogicNodeStrategy


@pytest.fixture
def logic_strategy() -> LogicNodeStrategy:
    return LogicNodeStrategy(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
        prompt_compiler=AsyncMock(),
    )


@pytest.mark.asyncio
async def test_execute_no_blueprint(logic_strategy: LogicNodeStrategy) -> None:
    # Explicitly using an empty string as task_blueprint to simulate missing configuration
    # while passing strict string type requirements in Pydantic models.
    step = StepRule.model_construct(id="step_1", task_blueprint="")
    projector = StateProjector()
    context = StrategyContext.model_construct(execution_id="e1", workflow_id="w1", metadata={})
    semaphore = asyncio.Semaphore(1)

    with pytest.raises(AppException) as exc:
        await logic_strategy.execute(step, projector, context, None, None, semaphore)

    assert "has no task_blueprint" in str(exc.value)
    assert exc.value.status_code == 500


@pytest.mark.asyncio
async def test_execute_blueprint_not_found(logic_strategy: LogicNodeStrategy) -> None:
    step = StepRule.model_construct(id="step_1", task_blueprint="bp_123")
    projector = StateProjector()
    context = StrategyContext.model_construct(execution_id="e1", workflow_id="w1", metadata={})
    semaphore = asyncio.Semaphore(1)

    from typing import cast

    mock_repo = cast(AsyncMock, logic_strategy.workflow_repo)
    if hasattr(mock_repo, "get_step_by_id"):
        mock_repo.get_step_by_id.return_value = None

    with pytest.raises(AppException) as exc:
        await logic_strategy.execute(step, projector, context, None, None, semaphore)

    assert "not found" in str(exc.value)
    assert exc.value.status_code == 500


@pytest.mark.asyncio
async def test_execute_passes_global_context_vars(logic_strategy: LogicNodeStrategy) -> None:
    step = StepRule.model_construct(id="step_1", task_blueprint="bp_123")
    projector = StateProjector()
    context = StrategyContext.model_construct(
        execution_id="e1", workflow_id="w1", metadata={}, global_context_vars={"language": "fi"}
    )
    semaphore = asyncio.Semaphore(1)

    step_def = {
        "id": "stp_1234567890abcdef",
        "slug": "test_slug",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "hook": "test_hook",
        "description": {"default_locale": "en", "translations": {"en": "Test Desc"}},
        "type": "logic",
    }
    from typing import cast

    mock_repo = cast(AsyncMock, logic_strategy.workflow_repo)
    mock_repo.get_step_by_id.return_value = step_def

    from unittest.mock import patch

    from backend_v2.core.hook_registry import HookResult

    with patch("backend_v2.services.orchestrator.strategies.logic.hook_registry.execute") as mock_execute:
        mock_execute.return_value = HookResult(success=True, state_delta={})

        await logic_strategy.execute(step, projector, context, None, None, semaphore)

        # Assert the hook was called with the global_context_vars
        mock_execute.assert_called_once()
        hook_name, hook_state, hook_deps = mock_execute.call_args.args
        assert hook_name == "test_hook"
        assert hook_state.global_context_vars == {"language": "fi"}
