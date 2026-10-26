"""Unit tests for backend_v2.services.orchestrator.strategies.__init__."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

import backend_v2.services.orchestrator.strategies as strategies_pkg
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.enums import StepType
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.services.orchestrator.strategies import (
    NODE_STRATEGY_REGISTRY,
    LLMNodeStrategy,
    LogicNodeStrategy,
    NodeStrategy,
    NodeStrategyFactory,
    StrategyContext,
    StrategyDependencies,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


def _build_deps() -> StrategyDependencies:
    """Create StrategyDependencies backed by InMemoryUnifiedWorkflowRepository."""
    repo = InMemoryUnifiedWorkflowRepository()
    return StrategyDependencies(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
        prompt_compiler=MagicMock(spec=PromptCompiler),
    )


def test_strategies_init_public_interface_and_resolution() -> None:
    """Verify strategies.__init__ exports and factory resolution for LogicNodeStrategy."""
    expected = [
        "LLMNodeStrategy",
        "LogicNodeStrategy",
        "NODE_STRATEGY_REGISTRY",
        "NodeStrategy",
        "NodeStrategyFactory",
        "StrategyBuilder",
        "StrategyContext",
        "StrategyDependencies",
    ]
    assert sorted(strategies_pkg.__all__) == expected
    assert issubclass(LogicNodeStrategy, NodeStrategy)
    assert issubclass(LLMNodeStrategy, NodeStrategy)
    assert StepType.LOGIC in NODE_STRATEGY_REGISTRY

    deps = _build_deps()
    strategy = NodeStrategyFactory.create_strategy(StepType.LOGIC, deps=deps)
    assert isinstance(strategy, LogicNodeStrategy)


def test_negative_strategies_init_missing_llm_engine_fails_fast() -> None:
    """Negative test (ISTQB): LLM strategy creation without engine raises AppException."""
    deps = _build_deps()
    with pytest.raises(AppException) as exc_info:
        NodeStrategyFactory.create_strategy(StepType.LLM, deps=deps, engine=None)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value


def test_negative_strategies_init_strategy_context_rejects_extra_fields() -> None:
    """Negative test (ISTQB): StrategyContext enforces extra='forbid' and strict=True."""
    with pytest.raises(ValidationError):
        StrategyContext.model_validate(
            {
                "execution_id": "exe_1",
                "workflow_id": "wf_1",
                "metadata": ExecutionMetadata(),
                "extra_key": "rejected",
            }
        )
