"""Scoring engine factory and strategy implementations."""

import logging

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.enums import ScoringStrategy
from backend_v2.utils.scoring.average_engine import PureAverageScoringEngine, WeightedAverageScoringEngine
from backend_v2.utils.scoring.base_engine import ScoringEngineBase
from backend_v2.utils.scoring.pure_math_engine import PureMathScoringEngine
from backend_v2.utils.scoring.waterfall_engine import WaterfallScoringEngine


def get_scoring_engine(strategy: ScoringStrategy | str) -> ScoringEngineBase:
    """Strategy Pattern Factory. Returns the correct mathematical engine based on the execution strategy.

    Args:
        strategy: The scoring strategy to use, either as an enum or string.

    Returns:
        The instantiated scoring engine.

    Raises:
        AppException: If the provided strategy is invalid (VALIDATION_FAILED).
    """
    # Normalize to enum
    if isinstance(strategy, str):
        try:
            strategy = ScoringStrategy(strategy)
        except ValueError as e:
            logger = logging.getLogger(__name__)
            msg = f"Invalid scoring strategy string: {strategy}"
            logger.error("[ScoringEngine] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

    match strategy:
        case ScoringStrategy.WATERFALL:
            return WaterfallScoringEngine()
        case ScoringStrategy.AVERAGE:
            return PureAverageScoringEngine()
        case ScoringStrategy.WEIGHTED_AVERAGE:
            return WeightedAverageScoringEngine()
        case ScoringStrategy.PURE_MATH:
            return PureMathScoringEngine()
        case _:
            # Absolute fallback
            return WaterfallScoringEngine()
