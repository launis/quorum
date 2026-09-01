"""Base scoring engine protocol definitions."""

from typing import Protocol, runtime_checkable

from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO, XAILogDto
from backend_v2.models.enums import StrictnessAnchor


@runtime_checkable
class ScoringEngineProtocol(Protocol):
    """Protocol defining the structural interface contract for all scoring strategy engines (Strategy Pattern).

    Each engine implements a specific mathematical model for calculating
    final matrix scores based on execution statistics.
    """

    def calculate(
        self,
        stats: dict[float, LevelStatsDTO],
        math_min: float,
        math_max: float,
        strictness_level: int = StrictnessAnchor.STANDARD.value,
    ) -> tuple[float, XAILogDto, dict[str, dict[str, int]]]:
        """Calculates the final score and generates XAI justification log.

        Args:
            stats: Dictionary mapping scale_level to hits and total.
            math_min: The minimum possible score in the calculation matrix.
            math_max: The maximum possible score in the calculation matrix.
            strictness_level: The user strictness input mapped on 0-100 range.

        Returns:
            Tuple containing the calculated raw mathematical score,
            the formatted XAI justification log DTO, and
            the level breakdown dictionary for the frontend.
        """
        ...
