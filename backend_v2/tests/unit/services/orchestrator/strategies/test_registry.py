"""Unit tests for static NODE_STRATEGY_REGISTRY and NodeStrategyFactory."""

from unittest.mock import MagicMock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.enums import StepType
from backend_v2.services.orchestrator.engines.base import ExecutionEngine
from backend_v2.services.orchestrator.strategies.base import StrategyDependencies
from backend_v2.services.orchestrator.strategies.llm import LLMNodeStrategy
from backend_v2.services.orchestrator.strategies.logic import LogicNodeStrategy
from backend_v2.services.orchestrator.strategies.registry import (
    NODE_STRATEGY_REGISTRY,
    NodeStrategyFactory,
)


@pytest.fixture
def mock_deps() -> StrategyDependencies:
    """Provides a mocked StrategyDependencies container."""
    return StrategyDependencies(
        exec_repo=MagicMock(),
        workflow_repo=MagicMock(),
        comp_repo=MagicMock(),
        prompt_block_repo=MagicMock(),
        output_profile_repo=MagicMock(),
        identity_repo=MagicMock(),
        audit_repo=MagicMock(),
        system_repo=MagicMock(),
        prompt_compiler=MagicMock(),
    )


def test_node_strategy_registry_resolves_logic_strategy(mock_deps: StrategyDependencies) -> None:
    """Test factory creates LogicNodeStrategy for StepType.LOGIC."""
    strategy = NodeStrategyFactory.create_strategy(StepType.LOGIC, deps=mock_deps)
    assert isinstance(strategy, LogicNodeStrategy)
    assert strategy.deps is mock_deps


def test_node_strategy_registry_resolves_llm_strategy(mock_deps: StrategyDependencies) -> None:
    """Test factory creates LLMNodeStrategy for StepType.LLM with non-null ExecutionEngine."""
    mock_engine = MagicMock(spec=ExecutionEngine)
    strategy = NodeStrategyFactory.create_strategy(StepType.LLM, deps=mock_deps, engine=mock_engine)
    assert isinstance(strategy, LLMNodeStrategy)
    assert strategy.deps is mock_deps
    assert strategy._engine is mock_engine


def test_node_strategy_registry_llm_without_engine_raises_app_exception(mock_deps: StrategyDependencies) -> None:
    """Test factory raises AppException(CONFIGURATION_ERROR) when StepType.LLM has engine=None."""
    with pytest.raises(AppException) as exc_info:
        NodeStrategyFactory.create_strategy(StepType.LLM, deps=mock_deps, engine=None)

    assert exc_info.value.status_code == 500
    assert "ExecutionEngine" in exc_info.value.message


def test_node_strategy_registry_unregistered_type_raises_app_exception(mock_deps: StrategyDependencies) -> None:
    """Test factory raises AppException(CONFIGURATION_ERROR) for unregistered step type."""
    with pytest.raises(AppException) as exc_info:
        NodeStrategyFactory.create_strategy("unregistered_type", deps=mock_deps)  # type: ignore[arg-type]

    assert exc_info.value.status_code == 500
    assert "Unsupported step type" in exc_info.value.message


def test_node_strategy_registry_contains_canonical_step_types() -> None:
    """Test NODE_STRATEGY_REGISTRY contains exact StepType enum keys."""
    assert StepType.LOGIC in NODE_STRATEGY_REGISTRY
    assert StepType.LLM in NODE_STRATEGY_REGISTRY
