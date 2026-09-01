"""Average scoring engines for Phase 9 Cognitive Quorum.

Enables both linear unweighted average computation with outlier mitigation
and weighted sigmoid average scoring engines.
"""

import statistics
from typing import override

from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO, XAILogDto
from backend_v2.models.enums import StrictnessAnchor
from backend_v2.utils.math_utils import (
    calculate_linear_ratio_score,
    convert_strictness_to_forgiveness,
)
from backend_v2.utils.scoring.base_engine import ScoringEngineProtocol


class PureAverageScoringEngine(ScoringEngineProtocol):
    """Pure Average implementation (Linear, unweighted).

    Transforms the matrix statistics so that all scale levels have the same weight (1.0).
    Calculates the exact ratio of hits vs total criteria across the entire matrix.
    """

    @override
    def calculate(
        self,
        stats: dict[float, LevelStatsDTO],
        math_min: float,
        math_max: float,
        strictness_level: int = StrictnessAnchor.STANDARD.value,
    ) -> tuple[float, XAILogDto, dict[str, dict[str, int]]]:
        """Calculate pure linear average across score levels, applying outlier rejection.

        Args:
            stats: Dictionary mapping scale levels to hits, total, and optional dlqs count.
            math_min: The minimum score threshold representing scale_min.
            math_max: The maximum score limit representing scale_max.
            strictness_level: The user strictness input mapped on 0-100 range.

        Returns:
            A tuple containing:
                - The computed float final score.
                - An XAILogDto filled with diagnostic trace timelines.
                - A dictionary breakdown of the scores per level stringified.
        """
        log_lines: list[str] = ["Lineaarinen Keskiarvo Breakdown (Outlier Rejection):"]

        hit_rates: list[float] = []
        for v in stats.values():
            eff_total = v.total - v.dlqs
            if eff_total > 0:
                hit_rates.append(v.hits / eff_total)
            else:
                hit_rates.append(0.0)

        if len(hit_rates) > 1:
            median_hr = statistics.median(hit_rates)
            deviations = [abs(hr - median_hr) for hr in hit_rates]
            mad = statistics.median(deviations)
            if mad == 0.0:
                mad = 0.05
        else:
            median_hr = hit_rates[0] if hit_rates else 0.0
            mad = 0.05

        outlier_threshold = median_hr - 3.0 * mad

        flattened_hits = 0.0
        flattened_total = 0.0

        for level, v in stats.items():
            eff_total = v.total - v.dlqs
            hr = (v.hits / eff_total) if eff_total > 0 else 0.0

            if hr < outlier_threshold and hr < 0.30:
                log_lines.append(
                    f"Outlier Mitigated at Level {level}: Hit rate {hr:.2f} < "
                    f"{outlier_threshold:.2f} (Median {median_hr:.2f}, MAD {mad:.2f}). "
                    f"Weight reduced to 0.25x."
                )
                flattened_hits += v.hits * 0.25
                flattened_total += eff_total * 0.25
            else:
                flattened_hits += v.hits
                flattened_total += eff_total

        flattened_stats: dict[float, LevelStatsDTO] = {1.0: LevelStatsDTO(hits=flattened_hits, total=flattened_total)}

        base_forgiveness = convert_strictness_to_forgiveness(strictness_level)
        exponent = 1.0 + (1.0 - base_forgiveness)
        pure_score = calculate_linear_ratio_score(flattened_stats, math_min, math_max, exponent)

        total_hits = flattened_hits
        total_criteria = flattened_total

        hit_rate = (total_hits / total_criteria) if total_criteria > 0 else 0.0
        pct = int(hit_rate * 100)

        log_lines.append(f"Total Hit Ratio (Weighted): {total_hits:.2f}/{total_criteria:.2f} ({pct}%)")
        log_lines.append(
            f"Final Pure Average Score: {pure_score:.2f} (Mapped to scale {math_min}-{math_max} "
            f"with exponent {exponent:.2f} based on strictness {strictness_level})"
        )

        level_breakdown = {
            str(k): {"hits": int(v.hits), "total": int(v.total), "dlqs": int(v.dlqs)} for k, v in stats.items()
        }

        engine_debug_trace = {
            "engine": "pure_average",
            "stats": {k: v.model_dump() for k, v in stats.items()},
            "strictness_level": strictness_level,
            "outlier_threshold": outlier_threshold,
            "exponent": exponent,
            "log_trace": log_lines,
        }

        xai_log = XAILogDto(
            pedagogical_key="xai_pure_average_engine_breakdown",
            engine_debug_trace=engine_debug_trace,
        )

        return float(pure_score), xai_log, level_breakdown


class WeightedAverageScoringEngine(ScoringEngineProtocol):
    """Weighted Average implementation.

    Calculates the global weighted average of all matrix atoms,
    using the matrix scale levels natively as the mathematical weights.
    """

    @override
    def calculate(
        self,
        stats: dict[float, LevelStatsDTO],
        math_min: float,
        math_max: float,
        strictness_level: int = StrictnessAnchor.STANDARD.value,
    ) -> tuple[float, XAILogDto, dict[str, dict[str, int]]]:
        """Calculate weighted average scores using linear ratio based on configured strictness level.

        Args:
            stats: Dictionary mapping scale levels to hits, total, and optional dlqs count.
            math_min: The minimum score threshold representing scale_min.
            math_max: The maximum score limit representing scale_max.
            strictness_level: The user strictness input mapped on 0-100 range.

        Returns:
            A tuple containing:
                - The computed float final score.
                - An XAILogDto filled with diagnostic trace timelines.
                - A dictionary breakdown of the scores per level stringified.
        """
        base_forgiveness = convert_strictness_to_forgiveness(strictness_level)
        exponent = 1.0 + (1.0 - base_forgiveness)
        weighted_score = calculate_linear_ratio_score(stats, math_min, math_max, exponent)

        log_lines: list[str] = ["Weighted Average Breakdown:"]
        sorted_levels = sorted(stats.keys())

        achieved_weights = 0.0
        max_weights = 0.0

        for s_level in sorted_levels:
            level_data = stats[s_level]
            t_hits = level_data.hits
            eff_total = level_data.total - level_data.dlqs

            achieved_weights += t_hits * s_level
            max_weights += eff_total * s_level

            log_lines.append(f"Level {s_level} (Weight x{s_level}): {t_hits}/{eff_total} hits")

        ratio = (achieved_weights / max_weights) if max_weights > 0 else 0.0
        pct = int(ratio * 100)

        log_lines.append(f"Weighted Points Achieved: {achieved_weights:.1f} / {max_weights:.1f} ({pct}%)")
        log_lines.append(
            f"Final Weighted Score: {weighted_score:.2f} (Mapped to scale "
            f"{math_min}-{math_max} with exponent {exponent:.2f} based on strictness {strictness_level})"
        )

        level_breakdown = {
            str(k): {"hits": int(v.hits), "total": int(v.total), "dlqs": int(v.dlqs)} for k, v in stats.items()
        }

        engine_debug_trace = {
            "engine": "weighted_average",
            "stats": {k: v.model_dump() for k, v in stats.items()},
            "strictness_level": strictness_level,
            "exponent": exponent,
            "log_trace": log_lines,
        }

        xai_log = XAILogDto(
            pedagogical_key="xai_weighted_average_engine_breakdown",
            engine_debug_trace=engine_debug_trace,
        )

        return float(weighted_score), xai_log, level_breakdown
