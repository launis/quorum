"""Scoring engine factory and strategy implementations."""

from backend_v2.models.enums import ScoringStrategy
from backend_v2.utils.scoring.average_engine import PureAverageScoringEngine, WeightedAverageScoringEngine
from backend_v2.utils.scoring.base_engine import ScoringEngineBase
from backend_v2.utils.scoring.dampening_engine import DampeningScoringEngine
from backend_v2.utils.scoring.waterfall_engine import WaterfallScoringEngine


def get_scoring_engine(strategy: ScoringStrategy | str) -> ScoringEngineBase:
    """Strategy Pattern Factory. Returns the correct mathematical engine based on the execution strategy."""
    # Normalize to enum
    if isinstance(strategy, str):
        try:
            strategy = ScoringStrategy(strategy)
        except ValueError:
            # Fallback to standard if corrupted, though Fail-Fast at API level should prevent this
            strategy = ScoringStrategy.WATERFALL_FLOOR

    if strategy == ScoringStrategy.WATERFALL_FLOOR:
        return WaterfallScoringEngine()
    elif strategy == ScoringStrategy.PROGRESSIVE_DAMPENING:
        return DampeningScoringEngine()
    elif strategy == ScoringStrategy.PURE_AVERAGE:
        return PureAverageScoringEngine()
    elif strategy == ScoringStrategy.WEIGHTED_AVERAGE:
        return WeightedAverageScoringEngine()

    # Absolute fallback
    return WaterfallScoringEngine()
