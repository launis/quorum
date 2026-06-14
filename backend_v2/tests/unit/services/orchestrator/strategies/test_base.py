from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.core.hook_registry import HookState
from backend_v2.exceptions import AppException
from backend_v2.models.v2_core import Step as V2Step
from backend_v2.services.orchestrator.strategies.base import NodeStrategy


class DummyStrategy(NodeStrategy):
    async def execute(self, *args: Any, **kwargs: Any) -> list[Any]:
        return []


@pytest.fixture
def dummy_strategy() -> DummyStrategy:
    return DummyStrategy(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
        prompt_compiler=AsyncMock(),
    )


@pytest.mark.asyncio
async def test_assert_quota_no_org(dummy_strategy: DummyStrategy) -> None:
    # Should return immediately
    await dummy_strategy.assert_quota(None)


@pytest.mark.asyncio
async def test_assert_quota_safe(dummy_strategy: DummyStrategy, monkeypatch: pytest.MonkeyPatch) -> None:
    mock_usage = AsyncMock()
    mock_usage.check_quota.return_value = True
    monkeypatch.setattr("backend_v2.services.orchestrator.strategies.base.UsageService", lambda *args: mock_usage)

    await dummy_strategy.assert_quota("org_123")
    mock_usage.check_quota.assert_called_once_with("org_123")


@pytest.mark.asyncio
async def test_assert_quota_exceeded(dummy_strategy: DummyStrategy, monkeypatch: pytest.MonkeyPatch) -> None:
    mock_usage = AsyncMock()
    mock_usage.check_quota.return_value = False
    monkeypatch.setattr("backend_v2.services.orchestrator.strategies.base.UsageService", lambda *args: mock_usage)

    with pytest.raises(AppException) as exc:
        await dummy_strategy.assert_quota("org_123")
    assert exc.value.status_code == 402


@pytest.mark.asyncio
async def test_run_pre_hooks_empty(dummy_strategy: DummyStrategy) -> None:
    step_obj = V2Step.model_construct(id="s1", slug="s1", name="s1", pre_hooks=[])  # type: ignore[arg-type]
    hook_state = HookState.model_construct(
        execution_id="e1", workflow_id="w1", metadata={}, global_context_vars={}, inputs={}
    )
    res = await dummy_strategy.run_pre_hooks(step_obj, MagicMock(), hook_state, MagicMock())
    assert res == hook_state


@pytest.mark.asyncio
async def test_run_post_hooks_empty(dummy_strategy: DummyStrategy) -> None:
    step_obj = V2Step.model_construct(id="s1", slug="s1", name="s1", post_hooks=[])  # type: ignore[arg-type]
    hook_state = HookState.model_construct(
        execution_id="e1", workflow_id="w1", metadata={}, global_context_vars={}, inputs={}
    )
    res = await dummy_strategy.run_post_hooks(step_obj, MagicMock(), hook_state, MagicMock())
    assert res == hook_state
