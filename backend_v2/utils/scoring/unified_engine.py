"""Unified matrix calculation engine for Quorum V2 architecture.

Replaces legacy engine branching (Waterfall, PureAverage, WeightedAverage, PureMath)
with a single continuous piecewise power-curve weighted ratio scoring engine.
"""

from typing import override

from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO, ScoringResultDTO, XAILogDto
from backend_v2.utils.math_utils import calculate_linear_ratio_score
from backend_v2.utils.scoring.base_engine import ScoringEngineProtocol


def calculate_strictness_exponent(strictness_level: int) -> float:
    """Calculates the power-curve exponent for a 0-100 continuous strictness level.

    Enforces continuous piecewise linear interpolation between calibrated anchor points:
        - level <= 0: 1.00 (pure linear ratio, no dampening)
        - 0 < level <= 50: 1.00 + (level / 50.0) * (1.25 - 1.00)
        - 50 < level <= 85: 1.25 + ((level - 50.0) / 35.0) * (1.70 - 1.25)
        - 85 < level <= 100: 1.70 + ((level - 85.0) / 15.0) * (2.20 - 1.70)
        - level > 100: 2.20 (absolute strictness cap)

    Args:
        strictness_level: Integer strictness level on 0-100 scale.

    Returns:
        Monotonically increasing float exponent >= 1.0.
    """
    if strictness_level <= 0:
        return 1.0
    if strictness_level <= 50:
        return 1.0 + (strictness_level / 50.0) * 0.25
    if strictness_level <= 85:
        return 1.25 + ((strictness_level - 50.0) / 35.0) * 0.45
    if strictness_level <= 100:
        return 1.70 + ((strictness_level - 85.0) / 15.0) * 0.50
    return 2.20


class UnifiedScoringEngine(ScoringEngineProtocol):
    """Unified matrix calculation engine replacing all legacy scoring strategies.

    Executes continuous power-curve weighted ratio calculations mapped between math_min and math_max.
    """

    @override
    def calculate(
        self,
        stats: dict[float, LevelStatsDTO],
        math_min: float,
        math_max: float,
        strictness_level: int = 50,
    ) -> ScoringResultDTO:
        """Calculates the final matrix score using the unified weighted ratio engine.

        Args:
            stats: Dictionary mapping scale levels to LevelStatsDTO (hits, total, dlqs).
            math_min: The minimum score threshold of the scale.
            math_max: The maximum score limit of the scale.
            strictness_level: The user strictness input on a continuous 0-100 scale (defaults to 50).

        Returns:
            Strictly typed, immutable ScoringResultDTO containing the final score, XAI log, and breakdown.
        """
        exponent = calculate_strictness_exponent(strictness_level)
        score = calculate_linear_ratio_score(
            level_stats=stats,
            math_min=math_min,
            math_max=math_max,
            exponent=exponent,
        )

        sorted_levels = sorted(stats.keys())
        log_lines: list[str] = [f"Unified Scoring Engine (Strictness: {strictness_level}%, Exponent: {exponent:.4f}):"]

        achieved_weights = 0.0
        max_weights = 0.0
        for s_level in sorted_levels:
            level_data = stats[s_level]
            t_hits = level_data.hits
            eff_total = level_data.total - level_data.dlqs
            achieved_weights += t_hits * s_level
            max_weights += eff_total * s_level
            log_lines.append(f"Level {s_level} (Weight x{s_level}): {t_hits}/{eff_total} hits")

        if max_weights > 0:
            ratio = achieved_weights / max_weights
        else:
            ratio = 0.0
        curved_ratio = ratio**exponent
        pct = int(ratio * 100)
        curved_pct = int(curved_ratio * 100)

        log_lines.append(
            f"Weighted Points: {achieved_weights:.1f} / {max_weights:.1f} (Linear: {pct}%, Curved: {curved_pct}%)"
        )
        log_lines.append(f"Final Score: {score:.2f} (Mapped to scale {math_min}-{math_max})")

        level_breakdown = {str(k): LevelStatsDTO(hits=v.hits, total=v.total, dlqs=v.dlqs) for k, v in stats.items()}

        engine_debug_trace = {
            "engine": "unified",
            "strictness_level": strictness_level,
            "exponent": exponent,
            "linear_ratio": ratio,
            "curved_ratio": curved_ratio,
            "stats": {k: v.model_dump() for k, v in stats.items()},
            "log_trace": log_lines,
        }

        xai_log = XAILogDto(
            pedagogical_key="xai_unified_engine_breakdown",
            engine_debug_trace=engine_debug_trace,
        )

        return ScoringResultDTO(
            score=float(score),
            xai_log=xai_log,
            breakdown=level_breakdown,
        )
