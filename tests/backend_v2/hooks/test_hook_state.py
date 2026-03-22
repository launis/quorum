import pytest
from pydantic import ValidationError

from backend_v2.core.hook_registry import HookState, HookDependencies


def test_hook_state_immutability():
    """Ensure HookState cannot be mutated directly (FrozenInstanceError or ValidationError)."""
    state_dict = {
        "execution_id": "test_exec",
        "workflow_id": "test_flow",
        "step_id": "test_step",
        "inputs": {"key": "value"},
    }
    state = HookState(**state_dict)

    # Validate that we can access the data
    assert state.execution_id == "test_exec"
    assert state.inputs == {"key": "value"}

    # Attempt mutation -> should raise an error due to frozen=True
    with pytest.raises(ValidationError):
        state.inputs = {"another": "value"}  # type: ignore

    with pytest.raises(ValidationError):
        state.execution_id = "new_exec"  # type: ignore

def test_hook_state_forbids_extra_fields():
    """Ensure HookState rejects unknown initialization variables (extra='forbid')."""
    with pytest.raises(ValidationError):
        HookState(
            execution_id="test",
            workflow_id="test",
            step_id="test",
            unknown_magic_field="should fail"
        )

def test_hook_dependencies_creation():
    """Ensure HookDependencies works correctly and takes repository."""
    # We can pass None for testing
    deps = HookDependencies(repository=None)
    assert deps.repository is None
