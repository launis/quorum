from abc import ABC, abstractmethod


class ScoringEngineBase(ABC):
    """Abstract base class for all scoring strategy engines (Strategy Pattern).

    Each engine implements a specific mathematical model for calculating
    final matrix scores based on execution statistics.
    """

    @abstractmethod
    def calculate(
        self, stats: dict[float, dict[str, int]], math_min: float, math_max: float
    ) -> tuple[float, str, dict[str, dict[str, int]]]:
        """Calculates the final score and generates XAI justification log.

        Args:
            stats: Dictionary mapping scale_level -> {"hits": X, "total": Y}
            math_min: The minimum possible score in the calculation matrix.
            math_max: The maximum possible score in the calculation matrix.

        Returns:
            tuple[float, str, dict]:
                - The calculated raw mathematical score
                - The formatted XAI justification log string
                - The level breakdown dictionary for the frontend
        """
        pass
