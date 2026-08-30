from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.core.hook_registry import HookState
from backend_v2.exceptions import AppException
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.v2_core import Step as V2Step
from backend_v2.services.orchestrator.strategies.base import NodeStrategy, StrategyDependencies


class DummyStrategy(NodeStrategy):
    async def execute(self, *args: Any, **kwargs: Any) -> list[Any]:
        return []


@pytest.fixture
def dummy_strategy() -> DummyStrategy:
    deps = StrategyDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
        prompt_compiler=AsyncMock(),
        arq_pool=MagicMock(),
    )
    return DummyStrategy(deps=deps)


def test_strategy_properties(dummy_strategy: DummyStrategy) -> None:
    """Verify all convenience property accessors on NodeStrategy."""
    assert dummy_strategy.exec_repo is dummy_strategy.deps.exec_repo
    assert dummy_strategy.workflow_repo is dummy_strategy.deps.workflow_repo
    assert dummy_strategy.comp_repo is dummy_strategy.deps.comp_repo
    assert dummy_strategy.prompt_block_repo is dummy_strategy.deps.prompt_block_repo
    assert dummy_strategy.output_profile_repo is dummy_strategy.deps.output_profile_repo
    assert dummy_strategy.identity_repo is dummy_strategy.deps.identity_repo
    assert dummy_strategy.audit_repo is dummy_strategy.deps.audit_repo
    assert dummy_strategy.system_repo is dummy_strategy.deps.system_repo
    assert dummy_strategy.compiler is dummy_strategy.deps.prompt_compiler
    assert dummy_strategy.arq_pool is dummy_strategy.deps.arq_pool


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
    step_obj = V2Step.model_construct(id="stp_1", slug="s1", name="s1", pre_hooks=[])  # type: ignore[arg-type]
    hook_state = HookState(
        execution_id="e1",
        workflow_id="w1",
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars={},
        inputs={},
    )
    res_state, res_events = await dummy_strategy.run_pre_hooks(step_obj, MagicMock(), hook_state, MagicMock())
    assert res_state == hook_state
    assert res_events == []


@pytest.mark.asyncio
async def test_run_pre_hooks_success(dummy_strategy: DummyStrategy, monkeypatch: pytest.MonkeyPatch) -> None:
    from backend_v2.core.hook_registry import HookResult, hook_registry

    mock_result = HookResult(
        success=True,
        state_delta={
            "metadata": {"profile_id": "prof_updated"},
            "global_context_vars": {"ext_var": "val1"},
            "extra_input": "data1",
        },
    )
    monkeypatch.setattr(hook_registry, "execute", AsyncMock(return_value=mock_result))

    step_obj = V2Step.model_construct(id="stp_1", slug="s1", name="s1", pre_hooks=["hook_test"])  # type: ignore[arg-type]
    step_rule = MagicMock(id="node_1")
    hook_state = HookState(
        execution_id="e1",
        workflow_id="w1",
        metadata=ExecutionMetadata(target_locale="en", profile_id="prof_orig"),
        global_context_vars={"g_init": "1"},
        inputs={"in": "1"},
    )

    res_state, res_events = await dummy_strategy.run_pre_hooks(step_obj, step_rule, hook_state, MagicMock())
    assert res_state.metadata.profile_id == "prof_updated"
    assert res_state.metadata.target_locale == "en"
    assert res_state.global_context_vars == {"g_init": "1", "ext_var": "val1"}
    assert res_state.inputs == {"in": "1", "extra_input": "data1"}
    assert len(res_events) == 1
    assert res_events[0].step_name == "node_1"
    assert res_events[0].content == {"ext_var": "val1"}


@pytest.mark.asyncio
async def test_run_pre_hooks_failure(dummy_strategy: DummyStrategy, monkeypatch: pytest.MonkeyPatch) -> None:
    from backend_v2.core.hook_registry import HookResult, hook_registry

    mock_result = HookResult(success=False, state_delta={})
    monkeypatch.setattr(hook_registry, "execute", AsyncMock(return_value=mock_result))

    step_obj = V2Step.model_construct(id="stp_1", slug="s1", name="s1", pre_hooks=["hook_fail"])  # type: ignore[arg-type]
    step_rule = MagicMock(id="node_1")
    hook_state = HookState(
        execution_id="e1",
        workflow_id="w1",
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars={},
        inputs={},
    )

    res_state, res_events = await dummy_strategy.run_pre_hooks(step_obj, step_rule, hook_state, MagicMock())
    assert res_state == hook_state
    assert res_events == []


@pytest.mark.asyncio
async def test_run_post_hooks_empty(dummy_strategy: DummyStrategy) -> None:
    step_obj = V2Step.model_construct(id="stp_1", slug="s1", name="s1", post_hooks=[])  # type: ignore[arg-type]
    hook_state = HookState(
        execution_id="e1",
        workflow_id="w1",
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars={},
        inputs={},
    )
    res_state, res_events = await dummy_strategy.run_post_hooks(step_obj, MagicMock(), hook_state, MagicMock())
    assert res_state == hook_state
    assert res_events == []


@pytest.mark.asyncio
async def test_run_post_hooks_success(dummy_strategy: DummyStrategy, monkeypatch: pytest.MonkeyPatch) -> None:
    from backend_v2.core.hook_registry import HookResult, hook_registry

    mock_result = HookResult(
        success=True,
        state_delta={
            "metadata": {"profile_id": "prof_post_updated"},
            "global_context_vars": {"post_var": "val2"},
            "post_input": "data2",
        },
    )
    monkeypatch.setattr(hook_registry, "execute", AsyncMock(return_value=mock_result))

    step_obj = V2Step.model_construct(id="stp_1", slug="s1", name="s1", post_hooks=["hook_post"])  # type: ignore[arg-type]
    step_rule = MagicMock(id="node_1")
    hook_state = HookState(
        execution_id="e1",
        workflow_id="w1",
        metadata=ExecutionMetadata(target_locale="en", profile_id="prof_orig"),
        global_context_vars={"g_init": "1"},
        inputs={"in": "1"},
    )

    res_state, res_events = await dummy_strategy.run_post_hooks(step_obj, step_rule, hook_state, MagicMock())
    assert res_state.metadata.profile_id == "prof_post_updated"
    assert res_state.metadata.target_locale == "en"
    assert res_state.global_context_vars == {"g_init": "1", "post_var": "val2"}
    assert res_state.inputs == {"in": "1", "post_input": "data2"}
    assert len(res_events) == 1
    assert res_events[0].step_name == "node_1"
    assert res_events[0].content == {"post_var": "val2"}


@pytest.mark.asyncio
async def test_run_post_hooks_failure(dummy_strategy: DummyStrategy, monkeypatch: pytest.MonkeyPatch) -> None:
    from backend_v2.core.hook_registry import HookResult, hook_registry

    mock_result = HookResult(success=False, state_delta={})
    monkeypatch.setattr(hook_registry, "execute", AsyncMock(return_value=mock_result))

    step_obj = V2Step.model_construct(id="stp_1", slug="s1", name="s1", post_hooks=["hook_fail"])  # type: ignore[arg-type]
    step_rule = MagicMock(id="node_1")
    hook_state = HookState(
        execution_id="e1",
        workflow_id="w1",
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars={},
        inputs={},
    )

    res_state, res_events = await dummy_strategy.run_post_hooks(step_obj, step_rule, hook_state, MagicMock())
    assert res_state == hook_state
    assert res_events == []
