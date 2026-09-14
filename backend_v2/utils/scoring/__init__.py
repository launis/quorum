"""Scoring engine factory and strategy implementations."""

from typing import Any

from backend_v2.models.dtos.lightweight_matrix import ScoringResultDTO
from backend_v2.utils.scoring.base_engine import ScoringEngineProtocol
from backend_v2.utils.scoring.unified_engine import UnifiedScoringEngine

__all__ = [
    "ScoringEngineProtocol",
    "ScoringResultDTO",
    "UnifiedScoringEngine",
    "get_scoring_engine",
]


def get_scoring_engine(_strategy: Any = None) -> ScoringEngineProtocol:
    """Returns the unified continuous scoring engine.

    Args:
        _strategy: Unused legacy strategy parameter preserved for backward-compatible call sites.

    Returns:
        The instantiated UnifiedScoringEngine.
    """
    return UnifiedScoringEngine()
