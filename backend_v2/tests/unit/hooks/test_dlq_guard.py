import pytest

from backend_v2.core.hook_registry import HookDependencies, HookState
from backend_v2.exceptions import AppException
from backend_v2.hooks.dlq_guard import dlq_strict_mode_guard_hook


class DummyRepository:
    pass


@pytest.fixture
def dummy_deps() -> HookDependencies:
    repo = DummyRepository()
    return HookDependencies(
        exec_repo=repo,  # type: ignore
        workflow_repo=repo,  # type: ignore
        comp_repo=repo,  # type: ignore
        identity_repo=repo,  # type: ignore
        audit_repo=repo,  # type: ignore
        system_repo=repo,  # type: ignore
    )


def test_dlq_guard_success_no_dlqs(dummy_deps: HookDependencies) -> None:
    """Verify that dlq_strict_mode_guard passes when there are no DLQs."""
    state = HookState(
        execution_id="exec_123",
        workflow_id="wor_123",
        inputs={
            "evaluations": [
                {"atom_id": "atom_1", "status": "PASS"},
                {"atom_id": "atom_2", "status": "FAIL"},
                {"atom_id": "atom_3", "status": "PASS"},
            ]
        },
        metadata={},
        global_context_vars={},
    )

    result = dlq_strict_mode_guard_hook(state, dummy_deps)
    from backend_v2.core.hook_registry import HookResult

    assert isinstance(result, HookResult)
    assert result.success is True
    assert result.state_delta == {}


def test_dlq_guard_success_under_threshold(dummy_deps: HookDependencies) -> None:
    """Verify that dlq_strict_mode_guard passes when DLQ ratio is exactly at or under 10%."""
    # 1 DLQ out of 10 atoms = 10% (should pass)
    state = HookState(
        execution_id="exec_123",
        workflow_id="wor_123",
        inputs={
            "evaluations": [
                {"atom_id": "atom_1", "status": "DLQ"},
            ]
            + [{"atom_id": f"atom_{i}", "status": "PASS"} for i in range(2, 11)]
        },
        metadata={},
        global_context_vars={},
    )

    result = dlq_strict_mode_guard_hook(state, dummy_deps)
    from backend_v2.core.hook_registry import HookResult

    assert isinstance(result, HookResult)
    assert result.success is True
    assert result.state_delta == {}


def test_dlq_guard_fails_over_threshold(dummy_deps: HookDependencies) -> None:
    """Verify that dlq_strict_mode_guard raises AppException when DLQ ratio > 10%."""
    # 2 DLQs out of 10 atoms = 20% > 10% (should fail fast)
    state = HookState(
        execution_id="exec_123",
        workflow_id="wor_123",
        inputs={
            "evaluations": [
                {"atom_id": "atom_1", "status": "DLQ"},
                {"atom_id": "atom_2", "status": "DLQ"},
            ]
            + [{"atom_id": f"atom_{i}", "status": "PASS"} for i in range(3, 11)]
        },
        metadata={},
        global_context_vars={},
    )

    with pytest.raises(AppException) as exc_info:
        dlq_strict_mode_guard_hook(state, dummy_deps)

    assert exc_info.value.status_code == 500
    assert "Strict Fail-Fast: DLQ ratio" in exc_info.value.message
    assert "exceeded the 10.00% absolute limit." in exc_info.value.message
