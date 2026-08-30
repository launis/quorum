from typing import cast
from unittest.mock import MagicMock, patch

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookResult,
    HookState,
)
from backend_v2.exceptions import AppException
from backend_v2.hooks.llm import configure_llm_context_hook
from backend_v2.models.execution_core import ExecutionMetadata


def test_configure_llm_context_hook_no_state() -> None:
    result = cast(HookResult, configure_llm_context_hook(None, MagicMock(spec=HookDependencies)))  # type: ignore[arg-type]
    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.delta == {}


def test_configure_llm_context_hook_no_step_id() -> None:
    state = HookState(
        execution_id="exe1",
        workflow_id="wf1",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = MagicMock(spec=HookDependencies)

    with pytest.raises(AppException) as exc:
        configure_llm_context_hook(state, deps)

    assert exc.value.status_code == 500
    assert exc.value.details["error_code"] == "VALIDATION_FAILED"


@patch("backend_v2.hooks.llm.get_settings")
def test_configure_llm_context_hook_no_default_strategy(mock_get_settings: MagicMock) -> None:
    mock_settings = MagicMock()
    mock_settings.default_model_strategy = None
    mock_get_settings.return_value = mock_settings

    state = HookState(
        execution_id="exe1",
        workflow_id="wf1",
        step_id="step_1",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = MagicMock(spec=HookDependencies)

    with pytest.raises(AppException) as exc:
        configure_llm_context_hook(state, deps)

    assert exc.value.status_code == 500
    assert exc.value.details["error_code"] == "CONFIGURATION_ERROR"


@pytest.mark.asyncio
@patch("backend_v2.hooks.llm.get_settings")
async def test_configure_llm_context_hook_valid(mock_get_settings: MagicMock) -> None:
    mock_settings = MagicMock()
    mock_settings.default_model_strategy = "fast"
    mock_settings.model_registry = {
        "id": "sys_abcdef0123456789abcdef0123456789",
        "slug": "sys_reg",
        "type": "model_registry",
        "models": {
            "fast": {
                "provider": "openai",
                "model_name": "gpt-4o-mini",
                "api_key": "test",
                "tpm_limit": 0,
                "rpm_limit": 0,
                "max_tokens": 1000,
                "supports_grounding": False,
                "temperature": 0.7,
            }
        },
    }
    mock_get_settings.return_value = mock_settings

    state = HookState(
        execution_id="exe1",
        workflow_id="wf1",
        step_id="step_1",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = MagicMock(spec=HookDependencies)

    result = cast(HookResult, configure_llm_context_hook(state, deps))
    assert result.success is True
    assert result.state_delta is not None
    assert "llm_config" in result.state_delta.delta
