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
from backend_v2.models.llm import LLMProviderConfig


def test_configure_llm_context_hook_no_state() -> None:
    result = cast(HookResult, configure_llm_context_hook(None, MagicMock(spec=HookDependencies)))  # type: ignore[arg-type]
    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.delta is None


def test_configure_llm_context_hook_no_step_id() -> None:
    state = HookState(
        execution_id="exe1",
        workflow_id="wf1",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        metadata=ExecutionMetadata(),
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
        metadata=ExecutionMetadata(),
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
        "tier_definitions": {
            tier: {
                "provider": "openai",
                "model_name": "gpt-4o-mini",
                "api_key": "test",
                "tpm_limit": 0,
                "rpm_limit": 0,
                "max_tokens": 1000,
                "supports_grounding": False,
                "temperature": 0.7,
            }
            for tier in ("fast", "balanced", "deep", "reasoning")
        },
    }
    mock_get_settings.return_value = mock_settings

    state = HookState(
        execution_id="exe1",
        workflow_id="wf1",
        step_id="step_1",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = MagicMock(spec=HookDependencies)

    result = cast(HookResult, configure_llm_context_hook(state, deps))
    assert result.success is True
    assert isinstance(result.state_delta.delta, LLMProviderConfig)
    assert result.state_delta.delta.model_name == "gpt-4o-mini"


@pytest.mark.asyncio
@patch("backend_v2.hooks.llm.get_settings")
async def test_configure_llm_context_hook_workflow_model_mapping(mock_get_settings: MagicMock) -> None:
    mock_settings = MagicMock()
    mock_settings.default_model_strategy = "fast"
    tier_defs = {
        tier: {
            "provider": "openai",
            "model_name": "gpt-4o-mini",
            "api_key": "test",
            "tpm_limit": 0,
            "rpm_limit": 0,
            "max_tokens": 1000,
            "supports_grounding": False,
        }
        for tier in ("fast", "balanced", "deep", "reasoning")
    }
    tier_defs["deep"] = {
        "provider": "gemini",
        "model_name": "gemini-2.0-flash",
        "api_key": "test2",
        "tpm_limit": 0,
        "rpm_limit": 0,
        "max_tokens": 2000,
        "supports_grounding": True,
        "temperature": 0.5,
    }
    mock_settings.default_model_strategy = "deep"
    mock_settings.model_registry = {
        "id": "sys_abcdef0123456789abcdef0123456789",
        "slug": "sys_reg",
        "type": "model_registry",
        "tier_definitions": tier_defs,
    }
    mock_get_settings.return_value = mock_settings

    state = HookState(
        execution_id="exe1",
        workflow_id="wf1",
        step_id="step_1",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = MagicMock(spec=HookDependencies)

    result = cast(HookResult, configure_llm_context_hook(state, deps))
    assert result.success is True
    assert isinstance(result.state_delta.delta, LLMProviderConfig)
    assert result.state_delta.delta.model_name == "gemini-2.0-flash"


@patch("backend_v2.hooks.llm.get_settings")
def test_configure_llm_context_hook_missing_registry(mock_get_settings: MagicMock) -> None:
    mock_settings = MagicMock()
    mock_settings.default_model_strategy = "fast"
    mock_settings.model_registry = None
    mock_get_settings.return_value = mock_settings

    state = HookState(
        execution_id="exe1",
        workflow_id="wf1",
        step_id="step_1",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = MagicMock(spec=HookDependencies)

    with pytest.raises(AppException) as exc:
        configure_llm_context_hook(state, deps)
    assert exc.value.status_code == 500


@patch("backend_v2.hooks.llm.get_settings")
def test_configure_llm_context_hook_strategy_not_found(mock_get_settings: MagicMock) -> None:
    mock_settings = MagicMock()
    mock_settings.default_model_strategy = "unknown_strategy"
    mock_settings.model_registry = {
        "id": "sys_abcdef0123456789abcdef0123456789",
        "slug": "sys_reg",
        "type": "model_registry",
        "tier_definitions": {
            tier: {
                "provider": "openai",
                "model_name": "gpt-4o-mini",
                "api_key": "test",
                "tpm_limit": 0,
                "rpm_limit": 0,
                "max_tokens": 1000,
                "supports_grounding": False,
            }
            for tier in ("fast", "balanced", "deep", "reasoning")
        },
    }
    mock_get_settings.return_value = mock_settings

    state = HookState(
        execution_id="exe1",
        workflow_id="wf1",
        step_id="step_1",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = MagicMock(spec=HookDependencies)

    with pytest.raises(AppException) as exc:
        configure_llm_context_hook(state, deps)
    assert exc.value.status_code == 500
    assert exc.value.details["error_code"] == "CONFIGURATION_ERROR"
    assert "Strategy 'unknown_strategy' not found in registry" in exc.value.message


@patch("backend_v2.hooks.llm.inflate")
@patch("backend_v2.hooks.llm.get_settings")
def test_configure_llm_context_hook_corrupt_registry(mock_get_settings: MagicMock, mock_inflate: MagicMock) -> None:
    mock_settings = MagicMock()
    mock_settings.default_model_strategy = "fast"
    mock_settings.model_registry = {
        "id": "sys_abcdef0123456789abcdef0123456789",
        "slug": "sys_reg",
        "type": "model_registry",
    }
    mock_get_settings.return_value = mock_settings
    mock_reg = MagicMock()
    mock_reg.tier_definitions = {}
    mock_inflate.return_value = mock_reg

    state = HookState(
        execution_id="exe1",
        workflow_id="wf1",
        step_id="step_1",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = MagicMock(spec=HookDependencies)

    with pytest.raises(AppException) as exc:
        configure_llm_context_hook(state, deps)
    assert exc.value.status_code == 500
    assert "ModelRegistry is corrupt" in exc.value.message


@patch("backend_v2.hooks.llm.inflate")
@patch("backend_v2.hooks.llm.get_settings")
def test_configure_llm_context_hook_tier_not_in_definitions(
    mock_get_settings: MagicMock, mock_inflate: MagicMock
) -> None:
    mock_settings = MagicMock()
    mock_settings.default_model_strategy = "deep"
    mock_settings.model_registry = {
        "id": "sys_abcdef0123456789abcdef0123456789",
        "slug": "sys_reg",
        "type": "model_registry",
    }
    mock_get_settings.return_value = mock_settings
    mock_reg = MagicMock()
    mock_reg.tier_definitions = {"fast": MagicMock()}
    mock_inflate.return_value = mock_reg

    state = HookState(
        execution_id="exe1",
        workflow_id="wf1",
        step_id="step_1",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = MagicMock(spec=HookDependencies)

    with pytest.raises(AppException) as exc:
        configure_llm_context_hook(state, deps)
    assert exc.value.status_code == 500
    assert "Strategy 'deep' not found in registry" in exc.value.message


@patch("backend_v2.hooks.llm.get_settings")
def test_configure_llm_context_hook_missing_limits(mock_get_settings: MagicMock) -> None:
    mock_settings = MagicMock()
    mock_settings.default_model_strategy = "fast"
    mock_settings.model_registry = {
        "id": "sys_abcdef0123456789abcdef0123456789",
        "slug": "sys_reg",
        "type": "model_registry",
        "tier_definitions": {
            tier: {
                "provider": "openai",
                "model_name": "gpt-4o-mini",
                "api_key": "test",
                "tpm_limit": None if tier == "fast" else 0,
                "rpm_limit": None if tier == "fast" else 0,
                "max_tokens": 1000,
                "supports_grounding": False,
            }
            for tier in ("fast", "balanced", "deep", "reasoning")
        },
    }
    mock_get_settings.return_value = mock_settings

    state = HookState(
        execution_id="exe1",
        workflow_id="wf1",
        step_id="step_1",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = MagicMock(spec=HookDependencies)

    with pytest.raises(AppException) as exc:
        configure_llm_context_hook(state, deps)
    assert exc.value.status_code == 500
    assert "must explicitly define tpm_limit and rpm_limit" in exc.value.message


@patch("backend_v2.hooks.llm.inflate")
@patch("backend_v2.hooks.llm.get_settings")
def test_configure_llm_context_hook_unexpected_exception(mock_get_settings: MagicMock, mock_inflate: MagicMock) -> None:
    mock_settings = MagicMock()
    mock_settings.default_model_strategy = "fast"
    mock_settings.model_registry = {"valid": "dict"}
    mock_get_settings.return_value = mock_settings
    mock_inflate.side_effect = RuntimeError("Catastrophic deserialization breakdown")

    state = HookState(
        execution_id="exe1",
        workflow_id="wf1",
        step_id="step_1",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )
    deps = MagicMock(spec=HookDependencies)

    with pytest.raises(AppException) as exc:
        configure_llm_context_hook(state, deps)
    assert exc.value.status_code == 500
    assert "LLM Hook failed" in exc.value.message
