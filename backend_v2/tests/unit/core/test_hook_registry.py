import pytest
from pydantic import ValidationError

from backend_v2.core.hook_registry import HookResult, HookState


def test_hook_state_strictness() -> None:
    state = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        metadata={"key": "val"},
        global_context_vars={"g": "v"},
        inputs={"in": "1"},
    )
    assert state.execution_id == "exec_1"
    assert state.metadata == {"key": "val"}

    with pytest.raises(ValidationError):
        HookState(execution_id="exec_1", workflow_id="wf_1", extra="fail")  # type: ignore


def test_hook_result_strictness() -> None:
    res = HookResult(success=True, state_delta={"test": 123})
    assert res.success is True

    with pytest.raises(ValidationError):
        HookResult(success=True, state_delta={"test": 123}, extra="fail")  # type: ignore


@pytest.mark.asyncio
async def test_hook_registry_register_and_execute_sync_and_async() -> None:
    """Test registering and executing both sync and async hooks."""
    from unittest.mock import MagicMock

    from backend_v2.core.hook_registry import HookDependencies, HookRegistry

    registry = HookRegistry()
    registry.clear()

    # Sync hook
    @registry.register("sync_test_hook")
    def sync_hook(state: HookState, deps: HookDependencies) -> HookResult:
        return HookResult(success=True, state_delta={"sync": "ok"})

    # Async hook
    @registry.register("async_test_hook")
    async def async_hook(state: HookState, deps: HookDependencies) -> HookResult:
        return HookResult(success=True, state_delta={"async": "ok"})

    state = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        step_id="stp_1",
        metadata={"k": "v"},
        global_context_vars={},
        inputs={"param": 1},
    )
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        prompt_block_repo=MagicMock(),
        output_profile_repo=MagicMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )

    res_sync = await registry.execute("sync_test_hook", state, deps)
    assert res_sync.success is True
    assert res_sync.state_delta == {"sync": "ok"}

    res_async = await registry.execute("async_test_hook", state, deps)
    assert res_async.success is True
    assert res_async.state_delta == {"async": "ok"}

    assert set(registry.get_all_hooks()) == {"sync_test_hook", "async_test_hook"}


@pytest.mark.asyncio
async def test_hook_registry_fail_fast_conditions() -> None:
    """Test duplicate registration, missing hook, invalid return type, and error wrapping."""
    from unittest.mock import MagicMock

    from backend_v2.core.hook_registry import HookDependencies, HookRegistry
    from backend_v2.exceptions import AppException

    registry = HookRegistry()
    registry.clear()

    # 1. Duplicate registration raises AppException(CONFIGURATION_ERROR)
    @registry.register("dup_hook")
    def hook1(state: HookState, deps: HookDependencies) -> HookResult:
        return HookResult(success=True, state_delta=None)

    with pytest.raises(AppException) as exc_dup:
        registry.register("dup_hook")(hook1)
    assert exc_dup.value.status_code == 500

    # 2. Missing hook raises AppException(RESOURCE_NOT_FOUND)
    state = HookState(
        execution_id="e",
        workflow_id="w",
        metadata={},
        global_context_vars={},
        inputs={},
    )
    deps = HookDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        prompt_block_repo=MagicMock(),
        output_profile_repo=MagicMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
    )
    with pytest.raises(AppException) as exc_missing:
        registry.get_hook("non_existent")
    assert exc_missing.value.status_code == 404

    # 3. Invalid return type raises AppException
    @registry.register("invalid_return_hook")
    def bad_hook(state: HookState, deps: HookDependencies) -> Any:
        return {"not": "a HookResult"}

    with pytest.raises(AppException) as exc_type:
        await registry.execute("invalid_return_hook", state, deps)
    assert "Must return HookResult" in exc_type.value.message

    # 4. Unhandled runtime exception wrapped in AppException
    @registry.register("exploding_hook")
    def explode_hook(state: HookState, deps: HookDependencies) -> HookResult:
        raise ValueError("Boom!")

    with pytest.raises(AppException) as exc_err:
        await registry.execute("exploding_hook", state, deps)
    assert "execution failed" in exc_err.value.message
