from typing import Any

import pytest
from pydantic import ValidationError

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDeltaDTO,
    HookDependencies,
    HookRegistry,
    HookResult,
    HookState,
    hook_registry,
)
from backend_v2.exceptions import AppException
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


def _create_hook_deps(repo: InMemoryUnifiedWorkflowRepository | None = None) -> HookDependencies:
    r = repo or InMemoryUnifiedWorkflowRepository()
    return HookDependencies(
        exec_repo=r,
        workflow_repo=r,
        comp_repo=r,
        prompt_block_repo=r,
        output_profile_repo=r,
        identity_repo=r,
        audit_repo=r,
        system_repo=r,
    )


def test_hook_state_instantiation() -> None:
    """Test HookState instantiation and attribute access."""
    state = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        step_id="stp_1",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(language="fi"),
        inputs=ExecutionInputsDTO(raw_inputs={"in": "1"}),
    )
    assert state.execution_id == "exec_1"
    assert state.metadata.workflow_version == 1
    assert state.inputs.raw_inputs == {"in": "1"}
    assert state.global_context_vars.language == "fi"


def test_hook_state_rejects_invalid_inputs() -> None:
    """Test that HookState rejects invalid non-mapping inputs."""
    with pytest.raises(ValidationError):
        HookState.model_validate(
            {
                "execution_id": "exec_1",
                "workflow_id": "wf_1",
                "metadata": ExecutionMetadata(),
                "global_context_vars": GlobalContextVarsDTO(),
                "inputs": 12345,
            }
        )


def test_hook_state_strictness() -> None:
    """Test extra fields rejection on HookState."""
    with pytest.raises(ValidationError):
        HookState.model_validate(
            {
                "execution_id": "exec_1",
                "workflow_id": "wf_1",
                "metadata": ExecutionMetadata(),
                "global_context_vars": GlobalContextVarsDTO(),
                "inputs": ExecutionInputsDTO(),
                "extra": "fail",
            }
        )


def test_hook_result_strictness() -> None:
    """Test HookResult strictness and state_delta typing."""
    payload = GlobalContextVarsDTO(language="fi")
    res = HookResult(success=True, state_delta=HookDeltaDTO(delta=payload))
    assert res.success is True
    assert res.state_delta is not None
    assert res.state_delta.delta == payload

    with pytest.raises(ValidationError):
        HookResult.model_validate(
            {
                "success": True,
                "state_delta": HookDeltaDTO(delta=payload),
                "extra": "fail",
            }
        )


@pytest.mark.asyncio
async def test_hook_registry_register_and_execute_sync_and_async() -> None:
    """Test registering and executing both sync and async hooks."""
    saved_hooks = dict(hook_registry._hooks)
    try:
        hook_registry.clear()

        sync_payload = GlobalContextVarsDTO(language="fi")
        async_payload = GlobalContextVarsDTO(language="en")

        # Sync hook
        @hook_registry.register("sync_test_hook")
        def sync_hook(state: HookState, deps: HookDependencies) -> HookResult:
            return HookResult(success=True, state_delta=HookDeltaDTO(delta=sync_payload))

        # Async hook
        @hook_registry.register("async_test_hook")
        async def async_hook(state: HookState, deps: HookDependencies) -> HookResult:
            return HookResult(success=True, state_delta=HookDeltaDTO(delta=async_payload))

        state = HookState(
            execution_id="exec_1",
            workflow_id="wf_1",
            step_id="stp_1",
            metadata=ExecutionMetadata(),
            global_context_vars=GlobalContextVarsDTO(),
            inputs=ExecutionInputsDTO(raw_inputs={"param": 1}),
        )
        deps = _create_hook_deps()

        res_sync = await hook_registry.execute("sync_test_hook", state, deps)
        assert res_sync.success is True
        assert res_sync.state_delta is not None
        assert res_sync.state_delta.delta == sync_payload

        res_async = await hook_registry.execute("async_test_hook", state, deps)
        assert res_async.success is True
        assert res_async.state_delta is not None
        assert res_async.state_delta.delta == async_payload

        assert set(hook_registry.get_all_hooks()) == {"sync_test_hook", "async_test_hook"}
    finally:
        hook_registry._hooks = saved_hooks


@pytest.mark.asyncio
async def test_hook_registry_fail_fast_conditions() -> None:
    """Test duplicate registration, missing hook, invalid return type, and error wrapping."""
    saved_hooks = dict(hook_registry._hooks)
    try:
        hook_registry.clear()

        # 1. Duplicate registration raises AppException(CONFIGURATION_ERROR)
        @hook_registry.register("dup_hook")
        def hook1(state: HookState, deps: HookDependencies) -> HookResult:
            return HookResult(success=True, state_delta=None)

        with pytest.raises(AppException) as exc_dup:
            hook_registry.register("dup_hook")(hook1)
        assert exc_dup.value.status_code == 500

        # 2. Missing hook raises AppException(RESOURCE_NOT_FOUND)
        state = HookState(
            execution_id="e",
            workflow_id="w",
            metadata=ExecutionMetadata(),
            global_context_vars=GlobalContextVarsDTO(),
            inputs=ExecutionInputsDTO(),
        )
        deps = _create_hook_deps()
        with pytest.raises(AppException) as exc_missing:
            hook_registry.get_hook("non_existent")
        assert exc_missing.value.status_code == 404

        # 3. Invalid return type raises AppException
        @hook_registry.register("invalid_return_hook")
        def bad_hook(state: HookState, deps: HookDependencies) -> Any:
            return {"not": "a HookResult"}

        with pytest.raises(AppException) as exc_type:
            await hook_registry.execute("invalid_return_hook", state, deps)
        assert "Must return HookResult" in exc_type.value.message

        # 4. Unhandled runtime exception wrapped in AppException
        @hook_registry.register("exploding_hook")
        def explode_hook(state: HookState, deps: HookDependencies) -> HookResult:
            raise ValueError("Boom!")

        with pytest.raises(AppException) as exc_err:
            await hook_registry.execute("exploding_hook", state, deps)
        assert "execution failed" in exc_err.value.message
    finally:
        hook_registry._hooks = saved_hooks


def test_hook_registry_singleton_integrity() -> None:
    """Test that HookRegistry enforces singleton instance identity."""
    reg1 = HookRegistry()
    reg2 = HookRegistry()
    assert reg1 is reg2
    assert reg1 is hook_registry
