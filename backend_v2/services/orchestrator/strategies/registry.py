import logging
from typing import Protocol

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.enums import StepType
from backend_v2.services.orchestrator.engines.base import ExecutionEngine
from backend_v2.services.orchestrator.strategies.base import NodeStrategy, StrategyDependencies
from backend_v2.services.orchestrator.strategies.llm import LLMNodeStrategy
from backend_v2.services.orchestrator.strategies.logic import LogicNodeStrategy

logger = logging.getLogger(__name__)


class StrategyBuilder(Protocol):
    """Protocol for building node strategy instances."""

    def __call__(
        self,
        deps: StrategyDependencies,
        engine: ExecutionEngine | None = None,
    ) -> NodeStrategy: ...


def _build_logic_strategy(
    deps: StrategyDependencies,
    engine: ExecutionEngine | None = None,
) -> NodeStrategy:
    """Build a LogicNodeStrategy instance."""
    return LogicNodeStrategy(deps=deps)


def _build_llm_strategy(
    deps: StrategyDependencies,
    engine: ExecutionEngine | None = None,
) -> NodeStrategy:
    """Build an LLMNodeStrategy instance enforcing non-null engine."""
    if engine is None:
        msg = "LLMNodeStrategy requires a non-null ExecutionEngine instance."
        logger.error(
            "[NodeStrategyFactory] %s: %s",
            ErrorCodes.CONFIGURATION_ERROR.name,
            msg,
            extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name},
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
}


class NodeStrategyFactory:
    """Factory resolving node strategies via strict static registry mapping."""

    @staticmethod
    def create_strategy(
        step_type: StepType,
        deps: StrategyDependencies,
        engine: ExecutionEngine | None = None,
    ) -> NodeStrategy:
        """Resolve and instantiate a NodeStrategy for the given StepType."""
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
