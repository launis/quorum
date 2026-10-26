"""Node strategy static registry and factory resolution."""

import logging
from typing import Protocol

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.enums import StepType
from backend_v2.services.orchestrator.engines.base import ExecutionEngine
from backend_v2.services.orchestrator.strategies.base import NodeStrategy, StrategyDependencies
from backend_v2.services.orchestrator.strategies.llm_strategy import LLMNodeStrategy
from backend_v2.services.orchestrator.strategies.logic import LogicNodeStrategy

logger = logging.getLogger(__name__)

__all__ = [
    "NODE_STRATEGY_REGISTRY",
    "NodeStrategyFactory",
    "StrategyBuilder",
]


class StrategyBuilder(Protocol):
    """Protocol for building node strategy instances."""

    def __call__(
        self,
        deps: StrategyDependencies,
        engine: ExecutionEngine | None = None,
    ) -> NodeStrategy:
        """Instantiate a NodeStrategy using injected dependencies and optional engine.

        Args:
            deps: Immutable dependency container holding repositories and services.
            engine: Optional ExecutionEngine required by LLM-backed node strategies.

        Returns:
            Instantiated NodeStrategy implementation.

        Raises:
            AppException: With CONFIGURATION_ERROR if required engine dependency is missing.
        """
        ...


def _build_logic_strategy(
    deps: StrategyDependencies,
    engine: ExecutionEngine | None = None,
) -> NodeStrategy:
    """Build a LogicNodeStrategy instance.

    Args:
        deps: Immutable dependency container holding repositories and services.
        engine: Unused optional ExecutionEngine maintained for StrategyBuilder signature parity.

    Returns:
        Instantiated LogicNodeStrategy bound to the provided dependencies.
    """
    return LogicNodeStrategy(deps=deps)


def _build_llm_strategy(
    deps: StrategyDependencies,
    engine: ExecutionEngine | None = None,
) -> NodeStrategy:
    """Build an LLMNodeStrategy instance enforcing non-null engine.

    Args:
        deps: Immutable dependency container holding repositories and services.
        engine: ExecutionEngine instance required to execute LLM tasks.

    Returns:
        Instantiated LLMNodeStrategy bound to dependencies and engine.

    Raises:
        AppException: With CONFIGURATION_ERROR if engine is None.
    """
    if engine is None:
        msg = "LLMNodeStrategy requires a non-null ExecutionEngine instance."
        logger.error(
            "[NodeStrategyFactory] %s: %s",
            ErrorCodes.CONFIGURATION_ERROR.name,
            msg,
            extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name},
            exc_info=True,
        )
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )
    return LLMNodeStrategy(deps=deps, engine=engine)


NODE_STRATEGY_REGISTRY: dict[StepType, StrategyBuilder] = {
    StepType.LOGIC: _build_logic_strategy,
    StepType.LLM: _build_llm_strategy,
    StepType.CAUSAL_DISCOVERY: _build_llm_strategy,
}


class NodeStrategyFactory:
    """Factory resolving node strategies via strict static registry mapping."""

    @staticmethod
    def create_strategy(
        step_type: StepType,
        deps: StrategyDependencies,
        engine: ExecutionEngine | None = None,
    ) -> NodeStrategy:
        """Resolve and instantiate a NodeStrategy for the given StepType.

        Args:
            step_type: Canonical StepType enum identifying the node execution strategy.
            deps: Immutable dependency container holding repositories and services.
            engine: Optional ExecutionEngine required for LLM and causal discovery strategies.

        Returns:
            Instantiated NodeStrategy corresponding to step_type.

        Raises:
            AppException: With CONFIGURATION_ERROR if step_type is unregistered or engine is missing.
        """
        if step_type not in NODE_STRATEGY_REGISTRY:
            msg = f"Unsupported step type '{step_type}'. Must be registered in NODE_STRATEGY_REGISTRY."
            logger.error(
                "[NodeStrategyFactory] %s: %s",
                ErrorCodes.CONFIGURATION_ERROR.name,
                msg,
                extra={
                    "error_code": ErrorCodes.CONFIGURATION_ERROR.name,
                    "step_type": str(step_type),
                },
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={
                    "error_code": ErrorCodes.CONFIGURATION_ERROR.value,
                    "step_type": str(step_type),
                },
            )
        builder = NODE_STRATEGY_REGISTRY[step_type]
        return builder(deps=deps, engine=engine)
