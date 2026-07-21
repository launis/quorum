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
