from unittest.mock import AsyncMock

import pytest

from backend_v2.core.hook_registry import HookDependencies, HookState
from backend_v2.hooks.hydration import hydrate_global_inputs_hook
from backend_v2.models.domain.hydration import HydrationInputSourceDTO


@pytest.fixture
def mock_deps() -> HookDependencies:
    return HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),  # noqa: E501
        search_client=AsyncMock(),
    )


def test_hydration_payload_dto_filtering() -> None:
    """Test that the HydrationInputSourceDTO correctly filters and extracts only strings."""
    # Test top-level string extraction
    dto1 = HydrationInputSourceDTO.model_validate(
        {
            "agent_type": "InputProcessorAgent",
            "valid_string": "extracted",
            "invalid_int": 123,
            "invalid_dict": {"foo": "bar"},
        }
    )
    assert dto1.is_valid_source() is True
    updates1 = dto1.extract_hydrated_inputs()
    assert "valid_string" in updates1
    assert "invalid_int" not in updates1
    assert "invalid_dict" not in updates1

    # Test strict inputs dictionary extraction
    dto2 = HydrationInputSourceDTO.model_validate(
        {
            "agent_type": "InputProcessorAgent",
            "inputs": {"key1": "value1", "key2": "value2"},
            "ignored_top_level": "will_be_ignored",
        }
    )
    assert dto2.is_valid_source() is True
    updates2 = dto2.extract_hydrated_inputs()
    assert "key1" in updates2
    assert "key2" in updates2
    assert "ignored_top_level" not in updates2


def test_hydrate_global_inputs_hook_with_inputs_dict(mock_deps: HookDependencies) -> None:
    """Test hook successfully hydrates from an explicit inputs dictionary."""
    state = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        step_id="step_1",
        metadata={},
        inputs={"existing_key": "existing_value"},
        global_context_vars={
            "step_input": {"agent_type": "InputProcessorAgent", "inputs": {"new_key": "new_value"}},
            "unrelated_step": {"some": "data"},
        },
    )

    from typing import cast

    from backend_v2.core.hook_registry import HookResult

    result = cast(HookResult, hydrate_global_inputs_hook(state, mock_deps))

    assert result.success is True
    assert result.state_delta is not None
    assert "inputs" in result.state_delta

    hydrated_inputs = result.state_delta["inputs"]
    assert "existing_key" in hydrated_inputs
    assert "new_key" in hydrated_inputs
    assert hydrated_inputs["new_key"] == "new_value"


def test_hydrate_global_inputs_hook_with_top_level_strings(mock_deps: HookDependencies) -> None:
    """Test hook successfully hydrates from top-level strings."""
    state = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        step_id="step_1",
        metadata={},
        inputs={},
        global_context_vars={
            "step_input": {
                "agent_type": "InputProcessorAgent",
                "q1": "Answer 1",
                "q2": "Answer 2",
                "score": 5,  # Should be filtered out
            }
        },
    )

    from typing import cast

    from backend_v2.core.hook_registry import HookResult

    result = cast(HookResult, hydrate_global_inputs_hook(state, mock_deps))

    assert result.success is True
    assert result.state_delta is not None
    assert "inputs" in result.state_delta

    hydrated_inputs = result.state_delta["inputs"]
    assert "q1" in hydrated_inputs
    assert "q2" in hydrated_inputs
    assert "score" not in hydrated_inputs


def test_hydrate_global_inputs_hook_no_source(mock_deps: HookDependencies) -> None:
    """Test hook returns empty state delta when no valid source is found."""
    state = HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        step_id="step_1",
        metadata={},
        inputs={"existing_key": "existing_value"},
        global_context_vars={"unrelated_step": {"some": "data"}},
    )

    from typing import cast

    from backend_v2.core.hook_registry import HookResult

    result = cast(HookResult, hydrate_global_inputs_hook(state, mock_deps))

    assert result.success is True
    assert result.state_delta == {}
